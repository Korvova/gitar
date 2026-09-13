# -*- coding: utf-8 -*-
"""ГИТАРА: ДЕКА v2 (2 секции по 160, y 480..800) — моторный отсек под настоящие
моторы тележек: круглый шаговик Ø36 (чертёж владельца 13.09.2026).

Что поменялось против v1 (NEMA17) и почему — проверка по STL 13.09.2026:
в v1 валы моторов не были в проверке сборки, и вал Ø5 проходил сквозь палец
кривошипа, вилку хвоста и ленты верхних этажей. В v2:
  * мотор снизу дна, вал вверх, но ОСЬ МОТОРА на X = 0 — сбоку от жёлоба лент
    (жёлоб X 6..14): ни вал, ни ступица кривошипа не проходят сквозь ленты;
  * кривошип = ступица на шестерне вала + диск над лентой своего этажа +
    палец ВНИЗ на радиусе R_PIN = 7.6 в открытую вилку хвоста;
  * вилка — открытая на запад: палец входит в неё сверху, при качании ±38°
    центр пальца ходит по X 6.0..7.6 и всегда держится зубьями вилки;
  * зубья вилки не шире щели гребёнки: хвост протаскивается сквозь гребёнки;
  * вал 6 мм не доходит до лент этажей 1–3 (они выше Z 8.4);
  * уши фланца повёрнуты на 56°: винты М3 ложатся между жёлобом и стенкой.
В проверке сборки: модель мотора (корпус, пилот, фланец с ушами, шестерня с
допуском вала +0.5) и КАЧАНИЕ всех кривошипов с лентами по сектору — зазоры
считаются на каждом шаге.

Запуск: .venv-b123d\\Scripts\\python gitara_deka.py
"""
import math
import sys
from build123d import *

OUT = r"C:\App\gitar\2-0\Print\Print"
L = 160
Z_FLOOR = [3, 8.4, 13.8, 19.2]
JX = (-21, -9, 5, 21)
LANE = 10                              # центр жёлоба лент
DK1_Y0, DK2_Y0 = 480, 640

# ---------------- мотор (чертёж владельца) ----------------
MOT_X = 0.0                            # ось мотора сбоку от жёлоба
MY = [515, 565, 615, 678]              # мотор этажа k (ближний к грифу — этаж 0)
MOT_R = 36.5 / 2                       # корпус Ø36.5
MOT_H = 22.0                           # глубина корпуса
PILOT_R, PILOT_H = 16.0 / 2, 1.5       # пилот Ø16 (−0.052) × 1.5
EAR_SPAN = 43.85                       # 2 × М3 на 43.85
EAR_R = EAR_SPAN / 2
EAR_ANG = 56.0                         # поворот ушей от оси Y (винты между жёлобом и стенкой)
SHAFT_OUT = 6.0 + 0.5                  # вал от фланца 6 ± 0.5 — берём худший
GEAR_L = 4.0
GEAR_D = 6.0                           # ⚠️ наружный Ø шестерни — ЗАМЕРИТЬ (в чертеже не указан)
GEAR_Z0 = SHAFT_OUT - 0.5 - GEAR_L     # начало шестерни при номинале (≈2.0)

# ---------------- кривошип ----------------
R_PIN = 7.6                            # радиус пальца
PIN_R = 2.5                            # палец Ø5
SWING = 38.0                           # рабочий сектор ±38° -> ход ленты ±4.68
SWING_MAX = 40.0                       # предел: центр пальца не западнее FORK_X+0.3 (cos = 5.8/7.6)
BORE_D = GEAR_D - 0.2                  # посадка ступицы на шестерню (купон 66)
HUB_R = GEAR_D / 2 + 1.2
HUB_Z0 = 2.2
DISK_R = R_PIN + PIN_R + 1.0
DISK_DZ, DISK_T = 1.8, 1.8             # диск: низ на полу+1.8, толщина 1.8 (верх этажа 3 = 22.8 < 23)
FORK_X = 5.5                           # западный край зубьев вилки (мир): не шире щели гребёнки 5.4,
                                       # чтобы хвост протаскивался сквозь гребёнки вилкой вперёд


def BB(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(
        abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))


def ear_holes(my, sign):
    """Два уха фланца мотора: (x, y) мир. sign выбирает диагональ."""
    a = math.radians(EAR_ANG)
    dx, dy = EAR_R * math.sin(a), EAR_R * math.cos(a)
    return [(MOT_X + sign * dx, my + dy), (MOT_X - sign * dx, my - dy)]


# тумбы корпуса (лок секции): винты сверху сквозь дно
# v2: столбики 16×16 не должны задевать корпуса моторов Ø36.5 и уши фланцев —
# в Д1 место есть только у западной стенки между моторами (расчёт 13.09.2026)
TUMBA1 = [(-18, 60), (-18, 110)]
TUMBA2 = [(-18, 65), (18, 65), (-18, 135), (18, 135)]
COMB_Y = (540, 590, 634)               # гребёнки между моторами (мир)


def pick_ear_sign(my, sec_y0, tumba):
    """Диагональ ушей, дальняя от стыковых дырок, тумб и ямок гребёнок."""
    others = [(hx, sec_y0 + 9) for hx in JX] + [(hx, sec_y0 + L + 9) for hx in JX]
    others += [(tx, sec_y0 + ty) for tx, ty in tumba]
    others += [(gx, yg) for yg in COMB_Y for gx in (-4, 18)]
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
    """Дно секции деки v2: колодцы моторов Ø36, стыки, стенки, ямки гребёнок."""
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
    holes_used = []
    for k, my in enumerate(MY):
        if not (sec_y0 <= my < sec_y0 + L):
            continue
        yl = my - sec_y0
        b -= Pos(MOT_X, yl, PILOT_H / 2 + 0.05) * Cylinder(PILOT_R + 0.05, PILOT_H + 0.2)  # пилот
        b -= Pos(MOT_X, yl, 1.5) * Cylinder(HUB_R + 0.5, 3.2)                            # ступица
        for ex, ey in ear_holes(my, EAR_SIGN[k]):
            b -= Pos(ex, ey - sec_y0, 1.5) * Cylinder(1.7, 3.2)                          # М3
            holes_used.append((ex, ey - sec_y0))
        holes_used.append((MOT_X, yl))
    for yg in COMB_Y:                                  # ямки гребёнок
        yl = yg - sec_y0
        if 4 < yl < L - 4:
            for gx in (-4, 18):
                b -= Pos(gx, yl, 1.5) * Cylinder(3.0, 3.2)
    for tx, ty in tumba_xy:                            # тумбы корпуса
        b -= Pos(tx, ty, 1.5) * Cylinder(1.7, 3.2)
        holes_used.append((tx, ty))
    for ex in (-19, -11):                              # сетка стоек электроники
        for ey in range(25, L - 15, 35):
            if all(math.hypot(ex - hx, ey - hy) > 8 for hx, hy in holes_used):
                b -= Pos(ex, ey, 1.5) * Cylinder(1.3, 3.2)
    for ty in lid_y:                                   # крышка корпуса
        for sx in (-24, 24):
            b -= Pos(sx, ty, 18.2) * Cylinder(1.3, 10)
    if neck_mount:
        for x0, x1 in ((-26.1, -21.9), (21.9, 26.1)):
            b -= BB(x0, x1, -0.1, 30.5, 20, 23.1)
        for sx in (-24, 24):
            b -= Pos(sx, 10, 16.1) * Cylinder(1.3, 8.2)
    return b


# ---------------- модель мотора (для проверки и сцены, не печатается) ------
def motor_model(sign):
    m = Pos(0, 0, -MOT_H / 2) * Cylinder(MOT_R, MOT_H)
    m += Pos(0, 0, PILOT_H / 2) * Cylinder(PILOT_R, PILOT_H)
    a = math.radians(EAR_ANG)
    for s in (1, -1):                                  # фланец: лепесток к каждому уху
        ex, ey = s * sign * EAR_R * math.sin(a), s * EAR_R * math.cos(a)
        m += Pos(ex, ey, -0.5) * Cylinder(3.5, 1.0)
        mid = Pos(ex / 2, ey / 2, -0.5) * Rot(0, 0, -math.degrees(math.atan2(ex, ey))) * Box(7.0, EAR_R, 1.0)
        m += mid
        m -= Pos(ex, ey, -0.5) * Cylinder(1.6, 1.2)
    m += Pos(0, 0, PILOT_H + (SHAFT_OUT - PILOT_H) / 2) * Cylinder(1.25, SHAFT_OUT - PILOT_H)
    m += Pos(0, 0, SHAFT_OUT - GEAR_L / 2) * Cylinder(GEAR_D / 2, GEAR_L)
    return m


# ---------------- кривошип: ступица на шестерне, диск над лентой, палец вниз --
def crank_part(k):
    zf = Z_FLOOR[k]
    d0 = zf + DISK_DZ
    c = Pos(0, 0, d0 + DISK_T / 2) * Cylinder(DISK_R, DISK_T)
    c += Pos(0, 0, (HUB_Z0 + d0) / 2) * Cylinder(HUB_R, d0 - HUB_Z0)
    bore_top = SHAFT_OUT + 0.2
    c -= Pos(0, 0, (HUB_Z0 - 0.1 + bore_top) / 2) * Cylinder(BORE_D / 2, bore_top - HUB_Z0 + 0.1)
    c += Pos(R_PIN, 0, (zf + 0.3 + d0) / 2) * Cylinder(PIN_R, d0 - zf - 0.3)   # палец: низ на полу+0.3
    return c


cranks = [crank_part(k) for k in range(4)]

# ---------------- гребёнка (как в v1: не зависит от мотора) ----------------
comb = BB(-6, 21.9, -2, 2, 3, 22.5)
for zf in Z_FLOOR:
    comb -= BB(5.4, 14.6, -2.1, 2.1, zf - 0.15, zf + 1.95)
comb += Pos(-4, 0, 1.6) * Cylinder(2.85, 2.8)
comb += Pos(18, 0, 1.6) * Cylinder(2.85, 2.8)


# ---------------- ленты: защёлки-нахлёсты (как в v1) ----------------------
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

# хвост v2: лента до мотора своего этажа, на конце — зубья вилки с западным
# выступом до FORK_X и открытый на запад паз под палец (лок: X от центра жёлоба)
tails = []
for k in range(4):
    yc = MY[k] - 480                                   # центр паза (лок)
    ln = yc + 5.0
    t = lap_top(BB(-4, 4, 0, ln, 0, 1.6), 0)
    t += BB(FORK_X - LANE, -4, yc - 4.65, ln, 0, 1.6)  # западный выступ зубьев
    t -= BB(FORK_X - LANE - 0.1, (R_PIN + PIN_R + 0.3) - LANE,
            yc - (PIN_R + 0.15), yc + (PIN_R + 0.15), -0.1, 1.7)
    tails.append(t)

# ---------------- купон 66: посадка ступицы на шестерню ----------------------
# четыре трубки как ступица: отверстия GEAR_D −0.4 / −0.2 / 0 / +0.2, риски 1..4
kupon = BB(-2, 50, -6, 6, 0, 2)
for i, dd in enumerate((-0.4, -0.2, 0.0, 0.2)):
    x = 6 + i * 12
    kupon += Pos(x, 0, 4) * Cylinder(HUB_R, 4)
    kupon -= Pos(x, 0, 3.5) * Cylinder((GEAR_D + dd) / 2, 5.2)
    for j in range(i + 1):
        kupon -= BB(x - 3 + j * 1.6, x - 2.2 + j * 1.6, -6.1, -5.2, 1.4, 2.1)

parts = [("gdk1_base_v2", deka_base(DK1_Y0, True, TUMBA1, (40, 100, 135), neck_mount=True)),
         ("gdk2_base_v2", deka_base(DK2_Y0, False, TUMBA2, (75, 120))),
         ("gdk_comb", comb), ("gdk_ext", ext), ("gdk_kupon_shesternya", kupon)]
parts += [(f"gdk_crank{k}_v2", cranks[k]) for k in range(4)]
parts += [(f"gdk_tail{k}_v2", tails[k]) for k in range(4)]
parts += [(f"gdk_motor{k}_model", motor_model(EAR_SIGN[k])) for k in range(4)]
for name, part in parts:
    p = part if isinstance(part, Part) else Part() + part
    export_stl(p, rf"{OUT}\{name}.stl")
    print(f"{name}: volume={p.volume:.0f} mm3, solids={len(p.solids())}")
print("export done")

# ================= ПРОВЕРКИ =================
from clearance import Assembly


def base_asm():
    asm = Assembly()
    asm.add("dk1", rf"{OUT}\gdk1_base_v2.stl", loc=(0, DK1_Y0, 0))
    asm.add("dk2", rf"{OUT}\gdk2_base_v2.stl", loc=(0, DK2_Y0, 0))
    for k in range(4):
        asm.add(f"mot{k}", rf"{OUT}\gdk_motor{k}_model.stl", loc=(MOT_X, MY[k], 0))
    for i, yg in enumerate(COMB_Y):
        asm.add(f"comb{i}", rf"{OUT}\gdk_comb.stl", loc=(0, yg, 0))
    return asm


bad = []


def need(asm, a, b, gap, where):
    d, depth = asm._dist(a, b)
    if depth > 0.05 or d < gap - 1e-6:
        bad.append(f"{where}: {a} <-> {b} зазор {d:.2f} (нужно {gap}), вход {depth:.2f}")
    return d


# статика: моторы садятся в колодцы, гребёнки в ямки
asm = base_asm()
for k in range(4):
    dk = "dk1" if MY[k] < DK2_Y0 else "dk2"
    need(asm, f"mot{k}", dk, 0.0, "мотор в колодце")
    for i in range(3):
        need(asm, f"mot{k}", f"comb{i}", 0.1, "мотор/гребёнка")   # ухо под дном, штырь в ямке — по высоте 0.2
for i in range(3):
    d, depth = asm._dist(f"comb{i}", "dk1" if COMB_Y[i] < DK2_Y0 else "dk2")
    if depth > 0.1:
        bad.append(f"гребёнка {i} не садится в ямки: вход {depth:.2f}")

# качание: все кривошипы вместе и вразнобой, от −SWING_MAX до +SWING_MAX
angles = [-SWING_MAX, -SWING, -20, 0, 20, SWING, SWING_MAX]
modes = {"вместе": [1, 1, 1, 1], "вразнобой": [1, -1, 1, -1]}
worst = {}
for mode, sgn in modes.items():
    for th in angles:
        asm = base_asm()
        for k in range(4):
            a = th * sgn[k]
            asm.add(f"cr{k}", rf"{OUT}\gdk_crank{k}_v2.stl", loc=(MOT_X, MY[k], 0), rz=a)
            dy = R_PIN * math.sin(math.radians(a))
            asm.add(f"tl{k}", rf"{OUT}\gdk_tail{k}_v2.stl",
                    loc=(LANE, 480 + dy, Z_FLOOR[k] + 0.05))
        where = f"{mode} {th:+.0f}°"
        for k in range(4):
            dk = "dk1" if MY[k] < DK2_Y0 else "dk2"
            for key, a, b, g in (
                    ("кривошип/дно", f"cr{k}", dk, 0.3),
                    ("палец в вилке", f"cr{k}", f"tl{k}", 0.1),
                    ("лента/мотор", f"tl{k}", f"mot{k}", 0.5)):
                d = need(asm, a, b, g, where)
                worst[key] = min(worst.get(key, 99), d)
            for j in range(4):
                if j != k:
                    d = need(asm, f"tl{k}", f"cr{j}", 0.5, where)
                    worst["лента/чужой кривошип"] = min(worst.get("лента/чужой кривошип", 99), d)
                    d = need(asm, f"tl{k}", f"mot{j}", 0.5, where)
                    worst["лента/чужой мотор"] = min(worst.get("лента/чужой мотор", 99), d)
            for i, yg in enumerate(COMB_Y):
                d = need(asm, f"cr{k}", f"comb{i}", 0.5, where)
                worst["кривошип/гребёнка"] = min(worst.get("кривошип/гребёнка", 99), d)
                if MY[k] - 12 > yg:
                    d = need(asm, f"tl{k}", f"comb{i}", 0.1, where)
                    worst["лента/гребёнка"] = min(worst.get("лента/гребёнка", 99), d)
        # палец обязан быть В зубьях вилки: центр пальца по X не западнее FORK_X
        px = MOT_X + R_PIN * math.cos(math.radians(abs(th)))
        if px < FORK_X + 0.3:
            bad.append(f"{where}: палец выходит из вилки (центр X {px:.2f})")
        top = max(asm.meshes[f"cr{k}"].bounds[1][2] for k in range(4))
        if top > 22.9:
            bad.append(f"{where}: кривошип выше стенок ({top:.2f})")

# стык-3: защёлка ленты-продолжения на хвост этажа 0
asm = base_asm()
asm.add("tl0", rf"{OUT}\gdk_tail0_v2.stl", loc=(LANE, 480, Z_FLOOR[0] + 0.05))
asm.add("ex0", rf"{OUT}\gdk_ext.stl", loc=(LANE, 320, Z_FLOOR[0] + 0.05))
d, depth = asm._dist("tl0", "ex0")
if depth > 0.1:
    bad.append(f"защёлка хвоста 0: вход {depth:.2f}")

# сборка: хвост протаскивается сквозь щели гребёнок вилкой вперёд
if FORK_X < 5.4 + 0.05:
    bad.append(f"зубья вилки (X {FORK_X}) шире щели гребёнки (X 5.4) — хвост не протащить")

print("минимальные зазоры по качанию (мм):")
for key in sorted(worst):
    print(f"  {key:22s} {worst[key]:.2f}")
print(f"ход ленты при ±{SWING:.0f}°: ±{R_PIN * math.sin(math.radians(SWING)):.2f} мм; "
      f"предел ±{SWING_MAX:.0f}°: ±{R_PIN * math.sin(math.radians(SWING_MAX)):.2f} мм")
print("уши моторов (диагональ):", EAR_SIGN)
if bad:
    print("!! НАРУШЕНИЯ:")
    for s in bad[:40]:
        print("  FAIL", s)
    sys.exit(1)
print("дека v2: каркас, моторы и качание чистые")
