# -*- coding: utf-8 -*-
r"""Стенд одной ленты для пробы ремней 0.4 (27.11.2026, владелец: «напечатать шестерни и один стенд — как ходит тележка, как идёт зацеп»).
Как в блоке v13: концевые ролики на ±22, ведущий ролик на роторе GB1806 в центре петли (x = +13, как мотор в шахматке).
Детали (PLA/PETG, сопло 0.4):
  stend_osnova      — нижняя плита: мотор GB1806 со стаканом стоит на ней, крепится длинными М2 через стакан (6 отверстий на Ø18 — 4 совпадут)
  stend_paluba      — палуба 2 мм на 4 ножках (шипы в основу): оси концевых роликов — кусочки филамента 1.75 (отверстия на натяг), окно под ведущий
  ved_rolik_Nmm     — ведущий ролик (тот же профиль, что rolik04 из стола 126) + проставка до палубы + 4 штыря Ø1.6 (было 1.9 — не лезли; 27.11 на пробе стола 128 из 1.4–1.8 идеально сел 1.6) в отверстия М2 ротора
  relsa_Nmm         — рельс, по нему едет площадка тележки (вставляется шипами в палубу)
  telezhka_stend_Nmm — тележка стенда: площадка 8.5 × 7, зуб 1.5 × 2.6 высотой ширина ремня + 1.2; зуб снаружи юбок роликов (пробные тележки стола 126 цепляют юбку ведущего)
Концевые ролики — rolik04_Nmm из стола 126 (3-0/remni/remen_04), ремни — стол 125. Мотор можно не подключать: ротор GB1806 крутится рукой.
Запуск: ..\..\..\2-0\.venv-b123d\Scripts\python stend_remen.py"""
import math, os
from build123d import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "stl"); os.makedirs(OUT, exist_ok=True)
for _f in os.listdir(OUT):
    if _f.endswith(".stl"): os.remove(os.path.join(OUT, _f))

# --- профиль ремня и ролика — как в remen_04.py (копия, чтобы импорт не трогал его папку) ---
X_C, R_END = 22.0, 2.5
LOOP = 2 * (2 * X_C) + 2 * math.pi * R_END
N, NP = 39, 6
RP = NP * LOOP / N / (2 * math.pi)
H, WT, TB = 0.7, 0.9, 0.9
CLR, BORE, T_FL = 0.10, 1.1, 0.6                    # 28.11: отверстие роликов Ø2.2 под болт М2 (крутится свободно)
CLR_DNO = 0.02                                      # 28.11: дно паза (как в remen_04.py)
T_W, G_T, LL, HP = 1.5, 0.10, 3.0, 1.5


def BB(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))


def CZ(r, z0, z1, x=0.0, y=0.0):
    return Pos(x, y, z0) * Cylinder(r, z1 - z0, align=(Align.CENTER, Align.CENTER, Align.MIN))


def ring_teeth(r, n, pts, height, z0=0.0):
    out = []
    for k in range(n):
        a = 2 * math.pi * k / n; c, s = math.cos(a), math.sin(a)
        q = [((r - nn) * c - t * s, (r - nn) * s + t * c) for t, nn in pts]
        out.append(Pos(0, 0, z0) * extrude(make_face(Polyline(*(q + [q[0]]))), height))
    return out


def pulley(w, bore=True):
    hub = w + 0.4
    p = Cylinder(RP, hub, align=(Align.CENTER, Align.CENTER, Align.MIN))
    g, d = WT / 2 + CLR, H + CLR_DNO
    p -= Part() + ring_teeth(RP, NP, [(-g, -0.3), (-g, d), (g, d), (g, -0.3)], hub + 2, -1)
    rf = RP + TB + 0.3
    p += Pos(0, 0, -T_FL) * Cylinder(rf, T_FL, align=(Align.CENTER, Align.CENTER, Align.MIN))
    p += Pos(0, 0, hub) * Cylinder(rf, T_FL, align=(Align.CENTER, Align.CENTER, Align.MIN))
    if bore: p -= Cylinder(BORE, 100)
    return Pos(0, 0, T_FL) * p                      # низ нижней юбки на z = 0


R_FL = RP + TB + 0.3                                # радиус юбок 3.74
Y_BACK = RP + TB                                    # спинка ремня снаружи от оси ленты (3.44)

# --- стенд ---
XM = 13.0                                           # мотор / ведущий ролик (как в шахматке блока)
R_M, H_MOT = 11.0, 20.5                             # GB1806 со стаканом
T_B, T_D = 2.5, 2.0                                 # основа, палуба
Z_RF = T_B + H_MOT                                  # торец ротора 23.0
Z_D0 = Z_RF + 0.2; Z_D1 = Z_D0 + T_D                # палуба 23.2..25.2
X0, X1, Y0, Y1 = -30.0, 30.0, -14.0, 14.0
LEGS = [(sx * 27.0, sy * 11.0) for sx in (-1, 1) for sy in (-1, 1)]
R_FIL = 0.85                                        # 28.11 (владелец): отверстие Ø1.7 — оси концевых роликов болты М2, вкручиваются в палубу как саморез
M2_LEN = {2: 5, 3: 6, 4: 7, 5: 8}                   # длина болта М2 по ширине ремня: в палубе 1.4 резьбы, под палубу не выходит (под правым роликом ротор мотора)
Y_TOOTH = R_FL + 0.1                                # зуб тележки снаружи юбок роликов (иначе цепляет юбку ведущего посреди хода)
RAIL_Y0, RAIL_Y1 = Y_TOOTH + 2.6 + 0.4, Y_TOOTH + 2.6 + 0.4 + 3.6
RAIL_PEGS = [(-18.0, (RAIL_Y0 + RAIL_Y1) / 2), (18.0, (RAIL_Y0 + RAIL_Y1) / 2)]


def osnova():
    b = BB(X0, X1, Y0, Y1, 0, T_B)
    for a in range(0, 360, 60):                     # 6 × М2 на Ø18 (у мотора 6, стакан на 4 из них) + потай под головку снизу
        x, y = XM + 9 * math.cos(math.radians(a + 30)), 9 * math.sin(math.radians(a + 30))
        b -= CZ(1.1, -1, T_B + 1, x, y) + CZ(2.0, -1, 1.2, x, y)
    b -= CZ(3.0, -1, T_B + 1, XM, 0)                # центр — продуть/посмотреть
    for x, y in LEGS:                               # гнёзда под шипы ножек палубы
        b -= CZ(1.35, 0.8, T_B + 1, x, y)
    return b


def paluba():
    d = BB(X0, X1, Y0, Y1, Z_D0, Z_D1)
    d -= CZ(4.4, Z_D0 - 1, Z_D1 + 1, XM, 0)         # окно под проставку ведущего
    for sx in (-1, 1):
        d -= CZ(R_FIL, Z_D0 - 1, Z_D1 + 1, sx * X_C, 0)   # оси концевых роликов — болты М2 (Ø1.7 под саморез)
    for x, y in RAIL_PEGS:
        d -= CZ(1.1, Z_D0 - 1, Z_D1 + 1, x, y)       # гнёзда шипов рельса
    for x, y in LEGS:
        d += BB(x - 2, x + 2, y - 2, y + 2, T_B, Z_D0 + 0.01)        # ножка 4 × 4
        d += CZ(1.25, 0.8 + 0.1, T_B + 0.01, x, y)                    # шип в основу
    return d


PINS = (1.4, 1.5, 1.6, 1.7, 1.8)                    # пробные диаметры штырей; метка = столько же насечек на проставке (1.4 → 1 … 1.8 → 5)


def ved_rolik(w, pin=1.6, marks=0):              # 1.6 — подобрано на пробе 27.11 (стол 128, 3 насечки)
    p = Pos(XM, 0, Z_D1 + 0.1) * pulley(w, bore=False)
    p += CZ(4.05, Z_RF, Z_D1 + 0.11, XM, 0)         # проставка сквозь окно палубы (зазор 0.35; при 3.9 штырь 1.8 касался края)
    for k in range(marks):                          # насечки-метки диаметра штырей на боку проставки (между штырями)
        a = math.radians(30 + 20 * k)
        p -= Pos(XM + 4.05 * math.cos(a), 4.05 * math.sin(a), Z_RF + 0.3 + 0.85) * Rot(0, 0, math.degrees(a)) * Box(0.9, 0.5, 1.7)   # только по проставке, штыри и юбку не задевает
    for a in (0, 90, 180, 270):                     # 4 штыря в резьбовые М2 ротора (Ø6), капля клея
        p += CZ(pin / 2, Z_RF - 1.5, Z_RF + 0.01, XM + 3 * math.cos(math.radians(a)), 3 * math.sin(math.radians(a)))
    return p


def os_rolika(w, x=0.0):
    """Ось концевого ролика со шляпкой (вместо кусочка филамента): снизу Ø1.75 на натяг в палубу (как филамент),
    по ролику Ø1.6 (отверстие ролика Ø1.8 — крутится свободно), сверху шляпка Ø4.5 × 0.8 с зазором 0.2 — ролик не соскочит."""
    top = Z_D1 + T_FL + w + 0.4 + T_FL                  # верх верхней юбки ролика
    o = CZ(0.875, Z_D0 + 0.2, Z_D1, x)                  # в палубе (до низа не доходит 0.2)
    o += CZ(0.8, Z_D1 - 0.01, top + 0.2, x)            # по ролику
    o += CZ(2.25, top + 0.2, top + 1.0, x)              # шляпка
    return o


def relsa(w):
    top = Z_D1 + T_FL + w + 1.2                      # площадка тележки на 0.2 выше верхних юбок роликов
    r = BB(-27.0, 27.0, RAIL_Y0, RAIL_Y1, Z_D1, top)
    for x, y in RAIL_PEGS:
        r += CZ(0.95, Z_D1 - 1.6, Z_D1 + 0.01, x, y)
    return r


def telezhka(w, xc=0.0):
    top = Z_D1 + T_FL + w + 1.2
    plate = BB(xc - 4.25, xc + 4.25, Y_BACK + 0.1, Y_BACK + 0.1 + 7.0, top, top + 1.2)
    tooth = BB(xc - T_W / 2, xc + T_W / 2, Y_TOOTH, Y_TOOTH + 2.6, Z_D1 + T_FL, top + 0.01)   # с ушками перекрывается на 1.1 мм
    return plate + tooth


if __name__ == "__main__":
    import trimesh
    parts = {"stend_osnova": (osnova(), (0, 0, 0)), "stend_paluba": (paluba(), (180, 0, 0))}
    for w in (2, 3, 4, 5):
        parts["ved_rolik_%dmm" % w] = (ved_rolik(w), (180, 0, 0))          # верхней юбкой на стол, штыри вверх
        for i, d in enumerate(PINS):                                        # стол 128: подбор штырей
            parts["ved_rolik_%dmm_pin%d" % (w, round(d * 10))] = (ved_rolik(w, d, i + 1), (180, 0, 0))
        parts["relsa_%dmm" % w] = (relsa(w), (180, 0, 0))
        parts["os_rolika_%dmm" % w] = (os_rolika(w), (180, 0, 0))           # шляпкой на стол
        parts["telezhka_stend_%dmm" % w] = (telezhka(w), (180, 0, 0))   # площадкой на стол, зуб вверх
    # --- проверка на ширине 3: детали не врезаются; ход тележки — пока зуб не упрётся в юбку концевого ролика ---
    w = 3
    mot = CZ(R_M, T_B, Z_RF, XM, 0)
    rol = [Pos(sx * X_C, 0, Z_D1) * pulley(w) for sx in (-1, 1)]
    stat = {"основа": parts["stend_osnova"][0], "палуба": parts["stend_paluba"][0], "рельс": relsa(w), "мотор": mot}
    mov = {"ведущий": ved_rolik(w), "ролик-": rol[0], "ролик+": rol[1]}
    for sx in (-1, 1):
        top = Z_D1 + T_FL + w + 0.4 + T_FL                                     # болт М2: головка на верхней юбке, резьба в палубе
        stat["ось%+d" % sx] = CZ(1.0, top - M2_LEN[w], top, sx * X_C)
        if top - M2_LEN[w] < Z_D0: bad_m2 = True; print("  болт М2 выходит под палубу!")
    bad = 0
    for a, pa in list(stat.items()) + list(mov.items()):
        for b, pb in list(stat.items()) + list(mov.items()):
            if a < b:
                try:
                    v = (pa & pb).volume
                except Exception:
                    v = 0
                if v > 0.02 and {a, b} not in ({"основа", "палуба"}, {"мотор", "ведущий"}, {"основа", "мотор"}, {"ось-1", "палуба"}, {"ось+1", "палуба"}):
                    bad += 1; print("  %s × %s: %.3f" % (a, b, v))
    xmax = 0.0
    for xc in [k * 0.5 for k in range(0, 51)]:
        t = telezhka(w, xc)
        hit = sum(((t & q).volume if (t & q) is not None else 0) for q in list(stat.values()) + list(mov.values()) if q is not mot)
        if hit > 0.02: break
        xmax = xc
    print("СТЕНД: %s | торец ротора %.1f, палуба %.1f..%.1f, ход тележки ±%.1f (дальше зуб упирается в юбку концевого ролика)" % (
        "ЧИСТО" if not bad else "%d проблем" % bad, Z_RF, Z_D0, Z_D1, xmax))
    for n, (p, rot) in parts.items():
        q = Rot(*rot) * p; bb = q.bounding_box(); q = Pos(-(bb.min.X + bb.max.X) / 2, -(bb.min.Y + bb.max.Y) / 2, -bb.min.Z) * q
        f = os.path.join(OUT, n + ".stl"); export_stl(q, f, tolerance=0.004, angular_tolerance=0.05)
        m = trimesh.load(f); print("  %-22s %5.1f × %5.1f × %4.1f герм %s" % (n, *m.extents, m.is_watertight))
    # сборка для Blender (ширина 3)
    A = os.path.join(HERE, "asm"); os.makedirs(A, exist_ok=True)
    for n, p in (("osnova", osnova()), ("paluba", paluba()), ("motor", mot), ("ved", ved_rolik(w)), ("rol_l", rol[0]), ("rol_r", rol[1]), ("relsa", relsa(w)), ("tel", telezhka(w))):
        export_stl(p, os.path.join(A, n + ".stl"), tolerance=0.01, angular_tolerance=0.1)
