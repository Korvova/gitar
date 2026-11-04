# Параметрическая модель кассеты тактильного грифа (телескоп, модуль 0.5)
# Оси: X поперёк грифа, Y вдоль грифа (ширина кассеты), Z вверх. Единицы: мм.
import math, os, sys
import cadquery as cq
from cadquery import exporters

# ---------- параметры, которые стоит сверить с реальным мотором ----------
MOTOR_D = 22.0        # диаметр корпуса
MOTOR_BODY_H = 14.0   # корпус (13 + 1) по таблице продавца
MOTOR_TOTAL_H = 17.5  # от опорной плоскости до торца выступа Ø9.5
BOSS_PCD = 6.0        # 4-M2 на торце выступа
BASE_PCD = 18.0       # M2 на основании мотора
# ---------- зубья ----------
M = 0.5
P = math.pi * M
ALPHA = math.radians(20)
BACKLASH = 0.04       # уменьшение толщины зуба на сторону контакта
RACK_ADD = 0.38       # высота головки зуба рейки (меньше 0.5, чтобы Z12 не подрезался)
RACK_DED = 0.625
# ---------- компоновка ----------
W, L = 24.0, 50.0     # ширина кассеты (вдоль грифа), длина (поперёк грифа)
T_BASE = 1.2
Z_GEAR0 = T_BASE + MOTOR_TOTAL_H + 0.1   # низ слоя шестерён
H_GEAR = 3.4
Z_RACK_TOP = Z_GEAR0 + H_GEAR + 0.05
Z_PLATE0 = Z_RACK_TOP + 0.05
T_PLATE = 1.2
Z_PLATE1 = Z_PLATE0 + T_PLATE
Z_CART0 = Z_PLATE1 + 0.1
T_CART = 3.0
Z_CART1 = Z_CART0 + T_CART
Y_FLOAT, Y_PIN = 6.0, 16.5
SP_FLOAT = 5 * P      # 7.854
TRAVEL = 48.0
SLIDER_LEN = 26.0
RACK_C_LEN = 12 * P   # 18.85
TONGUE = 18.0         # длина выступа ползуна в пазу стенки


def involute_pts(z, thin=BACKLASH, n=7):
    """Контур шестерни с эвольвентным профилем, зуб на +Y."""
    r = z * M / 2
    rb = r * math.cos(ALPHA)
    ra = r + M
    rf = r - 1.25 * M
    inv = lambda a: math.tan(a) - a
    half = (P / 2 - thin) / (2 * r) + inv(ALPHA)  # полуугол толщины на базовой окружности
    step = 2 * math.pi / z
    pts = []
    for i in range(z):
        c = math.pi / 2 + i * step
        rs = [max(rb, rf) + (ra - max(rb, rf)) * k / (n - 1) for k in range(n)]
        left, right = [], []
        for rr in rs:
            a = math.acos(min(1, rb / rr))
            t = half - inv(a)
            left.append((rr, c + t))
            right.append((rr, c - t))
        # от впадины по правой стороне к вершине и обратно по левой
        prof = [(rf, right[0][1])] + right + left[::-1] + [(rf, left[0][1])]
        pts += [(q * math.cos(th), q * math.sin(th)) for q, th in prof]
    # убрать совпавшие точки
    out = []
    for p in pts:
        if not out or math.dist(p, out[-1]) > 1e-4:
            out.append(p)
    return out


def gear(z, h, bore=0.0):
    w = cq.Workplane("XY").polyline(involute_pts(z)).close().extrude(h)
    if bore:
        w = w.faces(">Z").workplane().hole(bore)
    return w


def rack_pts(x1, x2, y_back, y_pitch, sign, phase):
    """sign=+1: зубья смотрят в +Y. Зубья с центрами в phase + k*P."""
    tip = y_pitch + sign * RACK_ADD
    root = y_pitch - sign * RACK_DED
    hp = P / 4 - BACKLASH / 2
    tn = math.tan(ALPHA)
    pts = [(x1, y_back), (x1, root)]
    k = math.ceil((x1 + RACK_DED - phase) / P)
    while phase + k * P + RACK_DED < x2:
        c = phase + k * P
        pts += [(c - hp - RACK_DED * tn, root), (c - hp + RACK_ADD * tn, tip),
                (c + hp - RACK_ADD * tn, tip), (c + hp + RACK_DED * tn, root)]
        k += 1
    pts += [(x2, root), (x2, y_back)]
    return pts


def rack(x1, x2, y_back, y_pitch, sign, phase, z0, z1):
    return cq.Workplane("XY").workplane(offset=z0).polyline(
        rack_pts(x1, x2, y_back, y_pitch, sign, phase)).close().extrude(z1 - z0)


def bx(x1, x2, y1, y2, z1, z2):
    return cq.Workplane("XY").box(x2 - x1, y2 - y1, z2 - z1, centered=False).translate((x1, y1, z1))


def make_base():
    b = bx(-L / 2, L / 2, 0, W, 0, T_BASE)
    # левая стенка (Y 0..1.5) и правая стенка с пазом (Y 22.5..24)
    zw = T_BASE + MOTOR_BODY_H + 0.3
    b = b.union(bx(-L / 2, L / 2, 0, 1.5, zw, Z_CART0 + 0.2))
    b = b.union(bx(-L / 2, L / 2, 22.5, W, zw, Z_PLATE0 - 0.05))
    b = b.union(bx(-L / 2, L / 2, 22.5, W, Z_PLATE1 + 0.05, Z_PLATE1 + 0.85))
    # стойки стенок на концах
    for x1, x2 in ((-L / 2, -L / 2 + 3), (L / 2 - 3, L / 2)):
        for y1, y2 in ((0, 1.5), (22.5, W)):
            b = b.union(bx(x1, x2, y1, y2, T_BASE, zw + 0.5))
    # закрытый конец паза на +X: упор для выступа ползуна
    b = b.union(bx(TONGUE / 2 + 12.05, L / 2, 22.5, W, Z_PLATE0 - 0.1, Z_PLATE1 + 0.1))
    # неподвижная рейка на двух стойках
    b = b.union(rack(-16, 16, 11, 9, -1, 0, Z_GEAR0, Z_RACK_TOP))
    for x1, x2 in ((-16, -11), (11, 16)):
        b = b.union(bx(x1, x2, 5, 11, T_BASE, Z_GEAR0 + 0.01))
    # отверстия мотора: 4 из 6 M2 на Ø18 (остальные попадают на соседнюю кассету)
    for a in (150, 210, 270, 330):
        x = BASE_PCD / 2 * math.cos(math.radians(a))
        y = Y_PIN + BASE_PCD / 2 * math.sin(math.radians(a))
        b = b.cut(cq.Workplane("XY").center(x, y).circle(1.1).extrude(T_BASE + 0.1))
    # окно под подшипник и контакты мотора
    b = b.cut(cq.Workplane("XY").center(0, Y_PIN).circle(4.5).extrude(T_BASE + 0.1))
    # крепление кассеты к профилю
    for x in (-23.5, 23.5):
        for y in (6, 18):
            b = b.cut(cq.Workplane("XY").center(x, y).circle(1.1).extrude(T_BASE + 0.1))
    return b


def make_slider():
    s = bx(-SLIDER_LEN / 2, SLIDER_LEN / 2, 3.5, 22.4, Z_PLATE0, Z_PLATE1)
    s = s.union(bx(-TONGUE / 2, TONGUE / 2, 22.39, 23.2, Z_PLATE0, Z_PLATE1))  # выступ в паз стенки
    # рейка ползуна: шестерня мотора зубом на +Y при центре, значит центры зубьев рейки на P/2
    s = s.union(rack(-SLIDER_LEN / 2, SLIDER_LEN / 2, 22.4, Y_PIN + 4.5, -1, P / 2, Z_GEAR0, Z_PLATE0 + 0.01))
    # ласточкин хвост
    rib = (cq.Workplane("YZ").polyline([(9.5, Z_PLATE1 - 0.01), (14.5, Z_PLATE1 - 0.01), (15.2, Z_PLATE1 + 1.2), (8.8, Z_PLATE1 + 1.2)]).close()
           .extrude(SLIDER_LEN / 2, both=True))
    s = s.union(rib)
    # штифты Ø1.5: отверстия под посадку
    for x in (-SP_FLOAT / 2, SP_FLOAT / 2):
        s = s.cut(cq.Workplane("XY").workplane(offset=Z_PLATE0 - 0.1).center(x, Y_FLOAT).circle(0.72).extrude(T_PLATE + 0.2))
    return s


def make_cart():
    c = bx(-10, 10, 1.6, 22, Z_CART0, Z_CART1)
    # паз ласточкин хвост с зазором 0.1
    g = (cq.Workplane("YZ").polyline([(9.4, Z_CART0 - 0.2), (14.6, Z_CART0 - 0.2), (15.45, Z_CART0 + 1.3), (8.55, Z_CART0 + 1.3)]).close()
         .extrude(11, both=True))
    c = c.cut(g)
    # рейка на юбке: центры зубьев k*P
    c = c.union(rack(-RACK_C_LEN / 2, RACK_C_LEN / 2, 1.6, 3.0, 1, 0, Z_GEAR0, Z_CART0 + 0.01))
    # два отверстия под крепление пальца или вибромотора
    for x in (-5, 5):
        c = c.cut(cq.Workplane("XY").workplane(offset=Z_CART0 + 1.6).center(x, 18.5).circle(0.8).extrude(2))
    return c


def make_pinion():
    g = gear(18, H_GEAR)
    # 4 глухих отверстия под шпильки M2 на Ø6 (клей), снизу
    for a in (0, 90, 180, 270):
        x = BOSS_PCD / 2 * math.cos(math.radians(a))
        y = BOSS_PCD / 2 * math.sin(math.radians(a))
        g = g.cut(cq.Workplane("XY").center(x, y).circle(1.05).extrude(H_GEAR - 0.8))
    return g


def make_float():
    return gear(12, H_GEAR - 0.2, bore=1.6)


def make_stop():
    return bx(0, 2.5, 0, 0.75, 0, 1.15)


def parts():
    return {
        "01_osnovanie": make_base(),
        "02_shesternya_motora_Z18": make_pinion(),
        "03_shesternya_plav_Z12": make_float(),
        "04_polzun": make_slider(),
        "05_telezhka": make_cart(),
        "06_upor_paza": make_stop(),
    }


def placed(p, d=0.0):
    """Детали в сборке. d: смещение тележки от центра, мм."""
    s = d / 2
    a_f = -math.degrees(s / 3.0)   # катится по рейке
    a_p = math.degrees(s / 4.5)
    out = {"base": p["01_osnovanie"]}
    out["pinion"] = p["02_shesternya_motora_Z18"].rotate((0, 0, 0), (0, 0, 1), -a_p).translate((0, Y_PIN, Z_GEAR0))
    for i, x in enumerate((-SP_FLOAT / 2, SP_FLOAT / 2)):
        out[f"float{i}"] = p["03_shesternya_plav_Z12"].rotate((0, 0, 0), (0, 0, 1), -a_f).translate((x + s, Y_FLOAT, Z_GEAR0 + 0.1))
    out["slider"] = p["04_polzun"].translate((s, 0, 0))
    out["cart"] = p["05_telezhka"].translate((d, 0, 0))
    return out


if __name__ == "__main__":
    outdir = sys.argv[1] if len(sys.argv) > 1 else "out"
    os.makedirs(outdir, exist_ok=True)
    p = parts()
    for n, w in p.items():
        exporters.export(w, f"{outdir}/{n}.stl", tolerance=0.01, angularTolerance=0.1)
        exporters.export(w, f"{outdir}/{n}.step")
        s = w.val()
        print(n, "valid", s.isValid(), "vol", round(s.Volume(), 1), "bbox", [round(v, 2) for v in (s.BoundingBox().xlen, s.BoundingBox().ylen, s.BoundingBox().zlen)])
    print("Z:", dict(gear0=Z_GEAR0, rack_top=Z_RACK_TOP, plate0=Z_PLATE0, plate1=Z_PLATE1, cart0=Z_CART0, cart1=Z_CART1))
    a = cq.Assembly(name="kasseta")
    for n, w in placed(p).items():
        a.add(w, name=n)
    a.save(f"{outdir}/sborka_kasseta.step")
