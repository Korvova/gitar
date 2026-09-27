# -*- coding: utf-8 -*-
"""ГИТАРА: ДЕКА v3 (2 секции по 160, y 480..800) — моторный отсек под моторы
тележек Ø36 с шестерёнкой z10 (чертёж и замер владельца 13.09.2026).

v3 — ПОЛНЫЙ ОБОРОТ кривошипа (идея владельца), механизм «кулиса»:
  * мотор снизу дна, вал вверх, ось мотора X = 0 сбоку от жёлоба лент (X 6..14);
  * кривошип = ступица на шестерне + диск ПОД лентой своего этажа + палец Ø5
    ВВЕРХ на радиусе R = 4.8 в поперечную прорезь ленты. Ступица и шестерня
    не доходят до ленты, поэтому кривошип крутится на 360°, лента ходит
    вперёд-назад на ±R (синусом). Сила на ленте в 1.6 раза больше, чем в v2;
  * этажу 0 под лентой места нет: мотор 0 опущен на проставке 4 мм, диск 0
    крутится в окне дна хребта;
  * гребёнки открыты на восток (форма «Е»): ленты кладутся сверху, гребёнки
    задвигаются сбоку после всех лент — через закрытую щель широкий хвост
    с прорезью не пролез бы;
  * уши фланца повёрнуты на 56°: винты М3 ложатся между жёлобом и стенкой.
Проверка сборки: модель мотора по чертежу (вал с допуском +0.5) и полный оборот
всех кривошипов (вместе и со сдвигом 90°), зазоры на каждом шаге 30°.

Запуск: .venv-b123d\\Scripts\\python gitara_deka.py
"""
import gc
import math
import os
import sys
from build123d import *

# рядом со скриптом: работает и на Windows, и на сервере Linux
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Print", "Print")
os.makedirs(OUT, exist_ok=True)
SWEEP = os.environ.get("DEKA_SWEEP", "1") != "0"   # DEKA_SWEEP=0 — только детали и статика
L = 160
Z_FLOOR = [3, 8.4, 13.8, 19.2]
JX = (-21, -9, 5, 21)
LANE = 10                              # центр жёлоба лент
DK1_Y0, DK2_Y0 = 480, 640

# ---------------- мотор (чертёж владельца) ----------------
MOT_X = 0.0
MY = [515, 565, 615, 678]              # мотор этажа k (ближний к грифу — этаж 0)
MOT_R, MOT_H = 36.5 / 2, 22.0
PILOT_R, PILOT_H = 16.0 / 2, 1.5
EAR_R = 43.85 / 2
EAR_ANG = 56.0
SHAFT_OUT = 6.0 + 0.5                  # вал от фланца 6 ± 0.5 — худший случай
GEAR_L = 4.0
GEAR_D = 6.0                           # замер владельца 13.09.2026
SPACER = 4.0                           # проставка мотора 0
FLANGE_Z = [-SPACER, 0.0, 0.0, 0.0]    # высота фланца мотора k

# ---------------- кривошип (кулиса) ----------------
R_CR = 4.8                             # радиус пальца = ход ленты ±4.8
PIN_R = 2.5
BORE_D = GEAR_D - 0.2                  # посадка на шестерню (купон 66, риска 2)
HUB_R = GEAR_D / 2 + 1.2
DISK_R = R_CR + PIN_R + 1.0
DISK_T = 1.8
SLOT_C = 0.15                          # зазор пальца в прорези по Y
SLOT_HALF = R_CR + PIN_R + 0.3         # полудлина прорези по X


def disk_top(k):
    return Z_FLOOR[k] - 0.35           # диск под лентой этажа k


def BB(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(
        abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))


def ear_holes(my, sign):
    a = math.radians(EAR_ANG)
    dx, dy = EAR_R * math.sin(a), EAR_R * math.cos(a)
    return [(MOT_X + sign * dx, my + dy), (MOT_X - sign * dx, my - dy)]


TUMBA1 = [(-18, 60), (-18, 110)]       # тумбы корпуса (лок секции)
TUMBA2 = [(-18, 65), (18, 65), (-18, 135), (18, 135)]
COMB_Y = (540, 590, 634)               # гребёнки между моторами (мир)
COMB_X0, COMB_X1 = -6.0, 10.2          # гребёнка «Е»: спинка на западе, зубья до 10.2 —
                                       # держат ленту (X 6..14) за западную половину
TENON = (-6.0, 5.4)                    # шип гребёнки в паз дна (по X)
COMB_SLIDE = 4.5                       # гребёнка ставится западнее на 4.5 и задвигается на ленты
KEY_X = (TENON[0] - COMB_SLIDE - 0.2, TENON[0] - 0.2)   # фиксатор в паз за шипом


def pick_ear_sign(my, sec_y0, tumba):
    others = [(hx, sec_y0 + 9) for hx in JX] + [(hx, sec_y0 + L + 9) for hx in JX]
    others += [(tx, sec_y0 + ty) for tx, ty in tumba]
    others += [(gx, yg) for yg in COMB_Y for gx in (-6, -0.3, 5.4)]
    best = None
    for s in (1, -1):
        d = min(math.hypot(ex - ox, ey - oy)
                for ex, ey in ear_holes(my, s) for ox, oy in others)
        if best is None or d > best[0]:
            best = (d, s)
    return best


EAR_SIGN = []
for k, my in enumerate(MY):
    sec = DK1_Y0 if my < DK2_Y0 else DK2_Y0
    d, s = pick_ear_sign(my, sec, TUMBA1 if sec == DK1_Y0 else TUMBA2)
    EAR_SIGN.append(s)
    if d < 6.0:
        print(f"FAIL мотор {k}: ухо в {d:.1f} мм от чужой дырки (нужно >= 6)")
        sys.exit(1)


def deka_base(sec_y0, south_shelf, tumba_xy, lid_y, neck_mount=False):
    b = BB(-26, 26, 0, L, 0, 3)
    b += BB(-26, -22, 0, L, 3, 23)
    b += BB(22, 26, 0, L, 3, 23)
    b -= BB(-26.1, 26.1, -0.1, 18, -0.1, 1.5)          # стык СЕВЕР
    for hx in JX:
        b -= Pos(hx, 9, 2.25) * Cylinder(1.3, 1.7)
    if south_shelf:
        b += BB(-26, 26, L, L + 18, 0, 1.5)
        for hx in JX:
            b -= Pos(hx, L + 9, 0.75) * Cylinder(1.6, 1.7)
    else:
        b += BB(-26, 26, L - 2, L, 3, 23)
    used = []
    for k, my in enumerate(MY):
        if not (sec_y0 <= my < sec_y0 + L):
            continue
        yl = my - sec_y0
        if k == 0:                                     # окно диска 0 насквозь
            b -= Pos(MOT_X, yl, 1.5) * Cylinder(DISK_R + 0.5, 3.2)
        else:
            b -= Pos(MOT_X, yl, PILOT_H / 2 + 0.05) * Cylinder(PILOT_R + 0.05, PILOT_H + 0.2)
            b -= Pos(MOT_X, yl, 1.5) * Cylinder(HUB_R + 0.5, 3.2)
        for ex, ey in ear_holes(my, EAR_SIGN[k]):
            b -= Pos(ex, ey - sec_y0, 1.5) * Cylinder(1.7, 3.2)
            used.append((ex, ey - sec_y0))
        used.append((MOT_X, yl))
    for yg in COMB_Y:                                  # пазы шипов гребёнок
        yl = yg - sec_y0
        if 4 < yl < L - 4:                             # длинный паз: шип едет 4.5 мм
            b -= BB(TENON[0] - COMB_SLIDE - 0.2, TENON[1] + 0.2, yl - 2.2, yl + 2.2, 0.5, 3.1)
            used += [(-0.3, yl), (TENON[0] - COMB_SLIDE, yl)]
    for tx, ty in tumba_xy:
        b -= Pos(tx, ty, 1.5) * Cylinder(1.7, 3.2)
        used.append((tx, ty))
    for ex in (-19, -11):                              # сетка стоек электроники
        for ey in range(25, L - 15, 35):
            if all(math.hypot(ex - hx, ey - hy) > 9 for hx, hy in used):
                b -= Pos(ex, ey, 1.5) * Cylinder(1.3, 3.2)
    for ty in lid_y:
        for sx in (-24, 24):
            b -= Pos(sx, ty, 18.2) * Cylinder(1.3, 10)
    if neck_mount:
        for x0, x1 in ((-26.1, -21.9), (21.9, 26.1)):
            b -= BB(x0, x1, -0.1, 30.5, 20, 23.1)
        for sx in (-24, 24):
            b -= Pos(sx, 10, 16.1) * Cylinder(1.3, 8.2)
    return b


def ear_plate(sign, z0, z1, r_lobe):
    """Фланцевая пластина: лепестки к ушам + перемычки (для модели и проставки)."""
    a = math.radians(EAR_ANG)
    p = None
    for s in (1, -1):
        ex, ey = s * sign * EAR_R * math.sin(a), s * EAR_R * math.cos(a)
        lobe = Pos(ex, ey, (z0 + z1) / 2) * Cylinder(r_lobe, z1 - z0)
        bar = Pos(ex / 2, ey / 2, (z0 + z1) / 2) * Rot(0, 0, -math.degrees(math.atan2(ex, ey))) * \
            Box(2 * r_lobe, EAR_R, z1 - z0)
        p = lobe + bar if p is None else p + lobe + bar
    return p


def motor_model(sign):
    """Мотор в своей системе: фланец z=0, вал вверх (для проверки и сцены)."""
    m = Pos(0, 0, -MOT_H / 2) * Cylinder(MOT_R, MOT_H)
    m += Pos(0, 0, PILOT_H / 2) * Cylinder(PILOT_R, PILOT_H)
    m += ear_plate(sign, -1.0, 0.0, 3.5)
    a = math.radians(EAR_ANG)
    for s in (1, -1):
        m -= Pos(s * sign * EAR_R * math.sin(a), s * EAR_R * math.cos(a), -0.5) * Cylinder(1.6, 1.2)
    m += Pos(0, 0, PILOT_H + (SHAFT_OUT - PILOT_H) / 2) * Cylinder(1.25, SHAFT_OUT - PILOT_H)
    m += Pos(0, 0, SHAFT_OUT - GEAR_L / 2) * Cylinder(GEAR_D / 2, GEAR_L)
    return m


def spacer_part(sign):
    """Проставка мотора 0 (мир z −4..0): пилот снизу, ступица насквозь, уши."""
    s = Pos(0, 0, -SPACER / 2) * Cylinder(11.0, SPACER)
    s += ear_plate(sign, -SPACER, 0.0, 4.2)
    s -= Pos(0, 0, -SPACER + (PILOT_H + 0.1) / 2 - 0.05) * Cylinder(PILOT_R + 0.05, PILOT_H + 0.2)
    s -= Pos(0, 0, -SPACER / 2) * Cylinder(HUB_R + 0.5, SPACER + 0.2)
    a = math.radians(EAR_ANG)
    for q in (1, -1):
        s -= Pos(q * sign * EAR_R * math.sin(a), q * EAR_R * math.cos(a), -SPACER / 2) * \
            Cylinder(1.7, SPACER + 0.2)
    return s


def crank_part(k):
    """Кривошип в системе оси мотора (мир z): ступица на шестерне, диск под
    лентой, палец вверх в прорезь ленты."""
    fz = FLANGE_Z[k]
    hub_z0 = fz + 2.2
    dt = disk_top(k)
    d0 = dt - DISK_T
    c = Pos(0, 0, d0 + DISK_T / 2) * Cylinder(DISK_R, DISK_T)
    if d0 > hub_z0:
        c += Pos(0, 0, (hub_z0 + d0) / 2) * Cylinder(HUB_R, d0 - hub_z0)
    bore_top = fz + SHAFT_OUT + 0.2                    # у этажа 0 выходит сквозь диск — это не мешает
    c -= Pos(0, 0, (hub_z0 - 0.1 + bore_top) / 2) * Cylinder(BORE_D / 2, bore_top - hub_z0 + 0.1)
    pin_top = Z_FLOOR[k] + 1.45
    c += Pos(R_CR, 0, (dt + pin_top) / 2) * Cylinder(PIN_R, pin_top - dt)
    return c


# ---------------- гребёнка «Е»: открыта на восток ----------------
comb = BB(COMB_X0, COMB_X1, -2, 2, 3, 22.5)
for zf in Z_FLOOR:
    comb -= BB(5.4, COMB_X1 + 0.1, -2.1, 2.1, zf - 0.15, zf + 1.95)
comb += BB(TENON[0], TENON[1], -2, 2, 0.6, 3.0)       # шип в паз дна
# фиксатор: брусок в паз за шипом, чтобы гребёнка не уехала назад на запад
comb_key = BB(KEY_X[0] + 0.1, KEY_X[1] - 0.1, -2.0, 2.0, 0.6, 4.5)


# ---------------- ленты: защёлки-нахлёсты ----------------
def lap_top(seg, y0):
    seg -= BB(-4.1, 4.1, y0 - 0.1, y0 + 18, -0.1, 0.8)
    seg -= Pos(0, y0 + 6.5, 1.2) * Cylinder(1.75, 1.0)
    seg += Pos(0, y0 + 11.5, 0.4) * Cylinder(1.5, 0.8)
    return seg


def lap_bot(seg, y1):
    seg -= BB(-4.1, 4.1, y1 - 18, y1 + 0.1, 0.8, 1.7)
    seg += Pos(0, y1 - 11.5, 2.0) * Cylinder(1.5, 2.4)
    seg -= Pos(0, y1 - 6.5, 0.4) * Cylinder(1.75, 1.0)
    return seg


ext = lap_bot(lap_top(BB(-4, 4, 0, 178, 0, 1.6), 0), 178)

# хвост v3: лента до мотора, на конце — площадка с ПОПЕРЕЧНОЙ прорезью (кулиса)
YOKE_HALF_Y = PIN_R + SLOT_C + 1.5
tails = []
for k in range(4):
    yc = MY[k] - 480
    ln = yc + YOKE_HALF_Y
    t = lap_top(BB(-4, 4, 0, ln, 0, 1.6), 0)
    x_w = MOT_X - SLOT_HALF - 1.2 - LANE               # западный край площадки (лок)
    t += BB(x_w, -4, yc - YOKE_HALF_Y, ln, 0, 1.6)
    t -= BB(MOT_X - SLOT_HALF - LANE, MOT_X + SLOT_HALF - LANE,
            yc - (PIN_R + SLOT_C), yc + (PIN_R + SLOT_C), -0.1, 1.7)
    tails.append(t)

# ---------------- купон 66: посадка на шестерню ----------------
GEAR_Z = 10
GEAR_M = GEAR_D / (GEAR_Z + 2)
R_TIP, R_ROOT = GEAR_D / 2, GEAR_D / 2 - 2.25 * GEAR_M
TOOTH_TIP_HALF, TOOTH_ROOT_HALF = 3.8, 15.0


def star_hole(c, h, z0):
    pts = []
    pitch = 360.0 / GEAR_Z
    for i in range(GEAR_Z):
        a = i * pitch
        ra, rt = R_ROOT + c, R_TIP + c
        dr, dtt = math.degrees(c / ra), math.degrees(c / rt)
        # полуугол впадины не больше полушага минус 1° — иначе соседние зубцы
        # перехлёстываются, контур сам себя пересекает и ядро CAD раздувает память
        hr = min(TOOTH_ROOT_HALF + dr, pitch / 2 - 1.0)
        ht = min(TOOTH_TIP_HALF + dtt, hr - 1.0)
        for ang, r in ((a - hr, ra), (a - ht, rt), (a + ht, rt), (a + hr, ra)):
            pts.append((r * math.cos(math.radians(ang)), r * math.sin(math.radians(ang))))
    pts.append(pts[0])
    return Pos(0, 0, z0) * extrude(make_face(Polyline(*pts)), h)


kupon = BB(-2, 74, -6, 6, 0, 2)
for i, (kind, val) in enumerate((("o", -0.4), ("o", -0.2), ("o", 0.0), ("o", 0.2),
                                 ("z", 0.1), ("z", 0.2))):
    x = 6 + i * 12
    kupon += Pos(x, 0, 4) * Cylinder(HUB_R, 4)
    if kind == "o":
        kupon -= Pos(x, 0, 3.5) * Cylinder((GEAR_D + val) / 2, 5.2)
    else:
        kupon -= Pos(x, 0, 0) * star_hole(val, 6.2, 0.9)
    for j in range(i + 1):
        w = 1.2 if i < 4 else 1.0
        kupon -= BB(x - 4 + j * w, x - 4 + j * w + 0.6, -6.1, -5.2, 1.4, 2.1)

parts = [("gdk1_base_v3", deka_base(DK1_Y0, True, TUMBA1, (40, 100, 135), neck_mount=True)),
         ("gdk2_base_v3", deka_base(DK2_Y0, False, TUMBA2, (75, 120))),
         ("gdk_comb_v3", comb), ("gdk_ext", ext), ("gdk_kupon_shesternya", kupon),
         ("gdk_spacer0_v3", spacer_part(EAR_SIGN[0])), ("gdk_comb_key_v3", comb_key)]
parts += [(f"gdk_crank{k}_v3", crank_part(k)) for k in range(4)]
parts += [(f"gdk_tail{k}_v3", tails[k]) for k in range(4)]
parts += [(f"gdk_motor{k}_model", motor_model(EAR_SIGN[k])) for k in range(4)]
for name, part in parts:
    p = part if isinstance(part, Part) else Part() + part
    export_stl(p, os.path.join(OUT, name + ".stl"))
    print(f"{name}: volume={p.volume:.0f} mm3, solids={len(p.solids())}")
print("export done")

# ================= ПРОВЕРКИ =================
# Память: каждая деталь грузится ОДИН раз; на шагах оборота подвижные детали
# только переставляются копией (раньше сборка перегружалась на каждом шаге —
# за 24 шага съедалась вся оперативка).
import trimesh
from clearance import Assembly


def stl(name):
    return os.path.join(OUT, name + ".stl")


asm = Assembly()
asm.add("dk1", stl("gdk1_base_v3"), loc=(0, DK1_Y0, 0))
asm.add("dk2", stl("gdk2_base_v3"), loc=(0, DK2_Y0, 0))
asm.add("sp0", stl("gdk_spacer0_v3"), loc=(MOT_X, MY[0], 0))
for k in range(4):
    asm.add(f"mot{k}", stl(f"gdk_motor{k}_model"), loc=(MOT_X, MY[k], FLANGE_Z[k]))
for i, yg in enumerate(COMB_Y):
    asm.add(f"comb{i}", stl("gdk_comb_v3"), loc=(0, yg, 0))
RAW_CR = [trimesh.load(stl(f"gdk_crank{k}_v3"), force="mesh") for k in range(4)]
RAW_TL = [trimesh.load(stl(f"gdk_tail{k}_v3"), force="mesh") for k in range(4)]

bad = []
worst = {}


def need(a, b, gap, where, key=None):
    d, depth = asm._dist(a, b)
    if depth > 0.05 or d < gap - 1e-6:
        bad.append(f"{where}: {a} <-> {b} зазор {d:.2f} (нужно {gap}), вход {depth:.2f}")
    if key:
        worst[key] = min(worst.get(key, 99), d if depth <= 0.05 else -depth)
    return d


def dk_of(y):
    return "dk1" if y < DK2_Y0 else "dk2"


def place(k, angle):
    """Кривошип k повернуть на angle, ленту k сдвинуть на R·sin — без перезагрузки."""
    T = trimesh.transformations.rotation_matrix(math.radians(angle), [0, 0, 1])
    T[:3, 3] = (MOT_X, MY[k], 0)
    c = RAW_CR[k].copy()
    c.apply_transform(T)
    asm.meshes[f"cr{k}"] = c
    t = RAW_TL[k].copy()
    t.apply_translation((LANE, 480 + R_CR * math.sin(math.radians(angle)), Z_FLOOR[k] + 0.05))
    asm.meshes[f"tl{k}"] = t


# статика
for k in range(4):
    d, depth = asm._dist(f"mot{k}", "sp0" if k == 0 else dk_of(MY[k]))
    if depth > 0.1:
        bad.append(f"мотор {k} не садится: вход {depth:.2f}")
d, depth = asm._dist("sp0", "dk1")
if depth > 0.1 or d > 0.05:
    bad.append(f"проставка 0 не прилегает к дну: зазор {d:.2f}, вход {depth:.2f}")
asm.add("key0", stl("gdk_comb_key_v3"), loc=(0, COMB_Y[0], 0))
d, depth = asm._dist("key0", dk_of(COMB_Y[0]))
if depth > 0.1:
    bad.append(f"фиксатор гребёнки не садится в паз: вход {depth:.2f}")
d, depth = asm._dist("key0", "comb0")
if depth > 0.1:
    bad.append(f"фиксатор врезается в гребёнку: вход {depth:.2f}")
del asm.meshes["key0"]
for i, yg in enumerate(COMB_Y):
    d, depth = asm._dist(f"comb{i}", dk_of(yg))
    if depth > 0.1:
        bad.append(f"гребёнка {i} не садится в паз: вход {depth:.2f}")
    for k in range(4):
        need(f"comb{i}", f"mot{k}", 0.1, "статика", "гребёнка/мотор")

# защёлка ленты-продолжения на хвост этажа 0
place(0, 0)
asm.add("ex0", stl("gdk_ext"), loc=(LANE, 320, Z_FLOOR[0] + 0.05))
d, depth = asm._dist("tl0", "ex0")
if depth > 0.1:
    bad.append(f"защёлка хвоста 0: вход {depth:.2f}")
del asm.meshes["ex0"]

# сборка: гребёнка ставится западнее на COMB_SLIDE, ленты уже лежат — не задевает
for k in range(4):
    place(k, 0)
for i, yg in enumerate(COMB_Y):
    asm.add(f"combw{i}", stl("gdk_comb_v3"), loc=(-COMB_SLIDE, yg, 0))
    for k in range(4):
        if MY[k] - 12 > yg:
            need(f"combw{i}", f"tl{k}", 0.2, "установка гребёнки", "гребёнка до задвигания/лента")
    need(f"combw{i}", dk_of(yg), 0.0, "установка гребёнки")
    del asm.meshes[f"combw{i}"]

# полный оборот: все вместе и со сдвигом 90° по этажам
if SWEEP:
    modes = {"вместе": [0, 0, 0, 0], "сдвиг 90°": [0, 90, 180, 270]}
    for mode, ph in modes.items():
        for th0 in range(0, 360, 30):
            for k in range(4):
                place(k, th0 + ph[k])
            where = f"{mode} {th0}°"
            for k in range(4):
                need(f"cr{k}", dk_of(MY[k]), 0.3, where, "кривошип/дно")
                need(f"cr{k}", f"tl{k}", 0.1, where, "палец в прорези, диск под лентой")
                if k == 0:
                    need("cr0", "sp0", 0.3, where, "кривошип 0/проставка")
                for j in range(4):
                    need(f"tl{k}", f"mot{j}", 0.5, where, "лента/мотор")
                    if j != k:
                        need(f"cr{k}", f"tl{j}", 0.5, where, "кривошип/чужая лента")
                        need(f"cr{k}", f"mot{j}", 0.5, where, "кривошип/чужой мотор")
                for i, yg in enumerate(COMB_Y):
                    need(f"cr{k}", f"comb{i}", 0.5, where, "кривошип/гребёнка")
                    if MY[k] - 12 > yg:
                        need(f"tl{k}", f"comb{i}", 0.1, where, "лента/гребёнка")
                if asm.meshes[f"cr{k}"].bounds[1][2] > Z_FLOOR[k] + 1.65:
                    bad.append(f"{where}: кривошип {k} выше ленты своего этажа")
            gc.collect()
            print(f"  шаг {where}: ок, нарушений всего {len(bad)}", flush=True)
else:
    print("оборот пропущен (DEKA_SWEEP=0)")

print("минимальные зазоры (мм):")
for key in sorted(worst):
    print(f"  {key:34s} {worst[key]:.2f}")
print(f"ход ленты ±{R_CR} мм за оборот; уши моторов: {EAR_SIGN}")
if bad:
    print("!! НАРУШЕНИЯ:")
    for line in bad[:40]:
        print("  FAIL", line)
    sys.exit(1)
print("дека v3: каркас, моторы" + (" и полный оборот" if SWEEP else "") + " чистые")
