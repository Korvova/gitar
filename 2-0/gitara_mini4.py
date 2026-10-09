# -*- coding: utf-8 -*-
r"""СТЕНД ОДНОГО ПАЛЬЦА: ПРИБЛУДА + ШАТУН (09.10.2026, идея владельца).
Как стол 90 (gitara_mini3.py), но вместо ленты с пальцем в ПРЯМОУГОЛЬНОЙ прорези плеча — шатун с КРУГЛЫМИ
дырками: палец седла катушки (Ø5 вниз) → задняя дырка шатуна; стад шатуна (Ø5 вверх) → круглая дырка
на коротком плече (18). Дугу конца плеча берёт на себя наклон длинного шатуна (~110) — прорезей и люфта
прорези нет, мёртвых точек нет (катушка едет прямо). Плечо 36 : 18 — катушка ±10 → ложе ±20 (сила ÷2).
Свои детали: mini4_base (дно без рельсов ленты, проход шире под наклон шатуна), mini4_arm (круглая дырка),
mini4_shatun. С других столов: середина, палуба (стол 91: mini1_mid / mini1_deck), ложе v3, седло и палец
(стол 90: mini3_sedlo, mini3_palec), стержень и гильза (стол 89).
Запуск: .venv-b123d\Scripts\python gitara_mini4.py
"""
import math
import os
from build123d import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "Print", "Print")

W, L = 52, 110                  # стенд, как mini1
CART_Y, LB, XS = 16, 36.0, 15.0
RS = 18.0                       # короткое плечо: круглая дырка под стад шатуна
AX = CART_Y + LB                # ось плеча: 52
FIT_D = 5.1
LANE_X = 10
Z_FL, Z_RIB = 3.0, 3.15
Z_ARM = Z_RIB + 1.6 + 0.2
Z_CEIL = 6.8
Z_DECK, DECK_T, RUN = 21.0, 3.0, 2.9
TIE = [(23.5, 6), (-23.5, 6), (23.5, 32), (-23.5, 45), (23.5, L - 8), (-23.5, L - 8)]

# приблуда — размеры как в magnit/gitara_sterzhen_15.py
SQ, PLUG, ROD_L = 17.0, 6.0, 80.2
ROD_T = ROD_L + 2 * PLUG        # 92.2
XP = ROD_L / 2
BOB_L, OUTER = 33.2, 26.0
TRAVEL = 10.0                   # ход катушки = ход ленты (вариант А)
Z_AX = 26.0                     # ось стержня над столом (10.10: 22 → 26 — медь намотана толще щёчек, до Ø34)
CU_D = 34.0                     # наружный диаметр меди с запасом (выпирает за щёчки 26)
ST_N0 = L + 2.0                 # северная стойка начинается за стенкой стенда
Y_D = ST_N0 + XP + PLUG + 4.0   # центр стержня: 162.1
Y_END = Y_D + XP + PLUG + 4.0 + 2.0
SED_T = 2.0
Z_SED = Z_AX - CU_D / 2 - 0.5 - SED_T    # 6.5 — низ седла: под медью 0.5 мм
PIN_BOT = Z_FL + 0.3


def BB(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))


def walls(z0, z1):
    w = BB(-26, -24, 0, L, z0, z1) + BB(24, 26, 0, L, z0, z1)
    w += BB(-24, 24, 0, 2, z0, z1) + BB(-24, 24, L - 2, L, z0, z1)
    for x, y in TIE:
        s = 1 if x > 0 else -1
        w += BB(s * 21, s * 26, y - 4, y + 4, z0, z1)
    return w


def ties(part, z0, z1, r):
    for x, y in TIE:
        part -= Pos(x, y, (z0 + z1) / 2) * Cylinder(r, z1 - z0 + 0.2)
    return part


# ---------------- дно: стенд (как mini1, без мотора) + площадка приблуды ----------------
base = BB(-26, 26, 0, L, 0, Z_FL) + walls(Z_FL, Z_CEIL)
base += Pos(0, AX, (Z_FL + Z_ARM - 0.05) / 2) * Cylinder(4.0, Z_ARM - 0.05 - Z_FL)
base += Pos(0, AX, (Z_FL + Z_CEIL - 0.2) / 2) * Cylinder(2.5, Z_CEIL - 0.2 - Z_FL)
base += BB(LANE_X - 20, LANE_X + 20, L - 2, Y_END, 0, Z_FL)                     # площадка приблуды
for s in (1, -1):                                                                # стойки стержня
    yo = Y_D + s * (XP + PLUG + 4.0)
    yi = Y_D + s * (XP + 1.0)
    base += BB(LANE_X - SQ / 2 - 3, LANE_X + SQ / 2 + 3, min(yo, yi), max(yo, yi), Z_FL, Z_AX + SQ / 2 + 2.5)
    g0, g1 = sorted((Y_D + s * (XP + 0.9), Y_D + s * (XP + PLUG + 0.1)))
    base -= BB(LANE_X - SQ / 2 - 0.2, LANE_X + SQ / 2 + 0.2, g0, g1, Z_AX - SQ / 2 - 0.2, Z_AX + SQ / 2 + 10)
base -= BB(LANE_X - 5.0, LANE_X + 10.0, L - 3, Y_D - XP + 1, Z_FL - 0.01, Z_FL + 2.5)   # проход в стене и туннель под стойкой (шатун наклонный)
base = ties(base, 0.8, Z_CEIL, 1.3)

# ---------------- шатун: задняя дырка (0, 0) — на палец седла, стад (0, LC) — в круглую дырку плеча ----------------
HOLE_D = 5.4                                             # на пальцы Ø5 — свободно (стенд 82: 5.1 туго)
LC = round(math.hypot(RS - LANE_X, Y_D - AX), 2)        # в середине хода короткое плечо поперёк, шатун почти вдоль
rib = Pos(0, 0, 0.8) * Cylinder(4.4, 1.6) + Pos(0, LC, 0.8) * Cylinder(4.4, 1.6) + BB(-3, 3, 0, LC, 0, 1.6)
rib -= Pos(0, 0, 0.8) * Cylinder(HOLE_D / 2, 1.8)
rib += Pos(0, LC, 1.6 + (Z_ARM - Z_RIB) / 2) * Cylinder(2.5, Z_ARM - Z_RIB)          # стад до верха плеча

# ---------------- плечо: как mini1, но на коротком плече КРУГЛАЯ дырка (вместо прорези) ----------------
PIN_TOP = Z_DECK + DECK_T + 1.8
arm = Pos(0, 0, 0.8) * Cylinder(5, 1.6)
arm += BB(-2.5, 2.5, -LB, 0, 0, 1.6) + Pos(0, -LB, 0.8) * Cylinder(3.5, 1.6)
arm += BB(0, RS, -2.8, 2.8, 0, 1.6) + Pos(RS, 0, 0.8) * Cylinder(4.4, 1.6)
arm -= Pos(RS, 0, 0.8) * Cylinder(HOLE_D / 2, 1.8)
arm -= Pos(0, 0, 0.8) * Cylinder(FIT_D / 2, 1.8)                                      # на стад оси — плотно
pin_h = PIN_TOP - (Z_ARM + 1.6)
arm += Pos(0, -LB, 1.6 + pin_h / 2) * Cylinder(2.5, pin_h)

# ---------------- седло (10.10): пластина под медью + две торцевые вилки, бортиков по бокам нет ----------------
# вилки обнимают крайние щёчки гильзы снаружи (по оси) и стержень с боков — до оси и выше, держат катушку вдоль хода
FORK_T, FORK_W = 2.5, 4.5                                   # толщина вилки вдоль оси, ширина зубца
SY = BOB_L / 2 + 0.15                                       # внутренняя грань вилки — щёчка + зазор
PL_X = OUTER / 2                                            # пластина ±13 поперёк
sed = BB(-PL_X, PL_X, -SY - FORK_T, SY + FORK_T, 0, SED_T)
z_top = (Z_AX + 6) - Z_SED                                  # вилки до оси + 6
for sy in (1, -1):
    y0, y1 = sorted((sy * SY, sy * (SY + FORK_T)))
    for sx in (1, -1):
        x0, x1 = sorted((sx * (SQ / 2 + 0.6), sx * (SQ / 2 + 0.6 + FORK_W)))
        sed += BB(x0, x1, y0, y1, 0, z_top)                    # зубцы по бокам стержня
    sed += BB(-SQ / 2 - 0.6 - FORK_W, SQ / 2 + 0.6 + FORK_W, y0, y1, 0, Z_AX - SQ / 2 - 0.6 - Z_SED)   # перемычка под стержнем
for sx in (1, -1):                                          # пазы под стяжку вдоль оси (стяжка вокруг гильзы)
    sed -= BB(sx * (PL_X - 3.5) - 0.8, sx * (PL_X - 3.5) + 0.8, -3, 3, -0.1, SED_T + 0.1)
# 09.10 (владелец: «седло плохо печатается»): палец — отдельной деталью, седло печатается ПЛАСТИНОЙ НА СТОЛ,
# вилки растут вверх — ни мостов, ни поддержек. Палец mini3_palec: шляпка Ø8 × 1 в зенковку сверху пластины
# (заподлицо, под медью 0.5 мм) + стержень Ø5 вниз сквозь дырку Ø5.3 в ленту; вклеить.
pin_h = Z_SED - PIN_BOT
sed -= Pos(0, 0, SED_T / 2) * Cylinder(2.65, SED_T + 0.2)
sed -= Pos(0, 0, SED_T - 0.5 + 0.005) * Cylinder(4.2, 1.01)
PAL_L = SED_T - 1.0 + pin_h                                  # стержень пальца ниже шляпки
pal = Pos(0, 0, 0.5) * Cylinder(4.0, 1.0) + Pos(0, 0, 1.0 + PAL_L / 2) * Cylinder(2.5, PAL_L)

# медь для проверки: цилиндр Ø CU_D между крайними щёчками
cu = Rot(90, 0, 0) * Cylinder(CU_D / 2, BOB_L - 2 * 0.8)
cu -= Rot(90, 0, 0) * Cylinder(SQ / 2 + 2.5, BOB_L)

pal_asm = Rot(180, 0, 0) * Pos(0, 0, -SED_T) * pal                 # в сборке: шляпка вверху пластины, стержень вниз
parts = [("mini4_base", base), ("mini4_shatun", rib), ("mini4_arm", arm)]
for n, p in parts:
    p = Part() + p
    bb = p.bounding_box()
    print("%s: %.1f x %.1f x %.1f, solids %d" % (n, bb.size.X, bb.size.Y, bb.size.Z, len(p.solids())))
    export_stl(p, os.path.join(OUT, n + ".stl"))

# ================= ПРОВЕРКА: катушка ±10 шагом 2.5 =================
from clearance import Assembly


def S(n):
    return os.path.join(OUT, n + ".stl")


def solve_phi(u):
    """угол плеча при сдвиге катушки u: |стад плеча − палец седла| = LC"""
    lo, hi = -1.2, 1.2
    def f(p):
        sx, sy = RS * math.cos(p), AX + RS * math.sin(p)
        return math.hypot(sx - LANE_X, sy - (Y_D + u)) - LC
    for _ in range(80):
        m = (lo + hi) / 2
        if f(lo) * f(m) <= 0:
            hi = m
        else:
            lo = m
    return (lo + hi) / 2


asm = Assembly()
asm.add("base", S("mini4_base"))
asm.add("mid", S("mini1_mid"), loc=(0, 0, Z_CEIL))
asm.add("deck", S("mini1_deck"), loc=(0, 0, Z_DECK))
asm.add("rod", S("s15_sterzhen_proverka"), loc=(LANE_X, Y_D, Z_AX), rz=90)
clear, touch = [("rod", "mid", 1.0)], [("mid", "deck"), ("rod", "base")]
worst, mu_min = 0, 180
for i, u in enumerate([-9.8, -7.5, -5, -2.5, 0, 2.5, 5, 7.5, 10.1]):   # ложе ±20: катушка −9.8 … +10.2 (шатун наклонный)
    p = solve_phi(u)
    phi = math.degrees(p)
    worst = max(worst, abs(LB * math.sin(p)))
    sx, sy = RS * math.cos(p), AX + RS * math.sin(p)
    px, py = LANE_X, Y_D + u
    alpha = math.degrees(math.atan2(-(sx - px), sy - py))
    v1 = (sx - px, sy - py)                                              # шатун
    mu = math.degrees(math.acos(abs(v1[0] * math.cos(p) + v1[1] * math.sin(p)) / LC))   # угол передачи: шатун к плечу
    mu_min = min(mu_min, mu)
    k, s_, r, a, z = "kat%d" % i, "sed%d" % i, "sh%d" % i, "arm%d" % i, "lz%d" % i
    asm.add(k, S("s15_gilza_sobrannaya"), loc=(LANE_X, Y_D + u, Z_AX), rz=90)
    asm.add(s_, S("mini3_sedlo"), loc=(LANE_X, Y_D + u, Z_SED))
    asm.add("pal%d" % i, S("mini3_palec_sborka"), loc=(LANE_X, Y_D + u, Z_SED))
    asm.add("cu%d" % i, S("mini3_med_proverka"), loc=(LANE_X, Y_D + u, Z_AX))
    asm.add(r, S("mini4_shatun"), loc=(px, py, Z_RIB), rz=alpha)
    asm.add(a, S("mini4_arm"), loc=(0, AX, Z_ARM), rz=phi)
    asm.add(z, S("gs1_lozhe_v3"), loc=(LB * math.sin(p), CART_Y, Z_DECK + DECK_T - RUN))
    clear += [(k, "rod", 0.3), (k, "base", 0.5), (s_, "base", 0.3), (s_, "rod", 0.5), (s_, "cu%d" % i, 0.3), ("cu%d" % i, "base", 0.5),
              (r, "base", 0.1), (r, "mid", 0.15), (s_, r, 0.3),
              (a, "base", 0.01), (a, "mid", 0.15), (a, "deck", 0.15), (a, z, 0.0)]
    touch += [(a, r), (z, "deck"), ("pal%d" % i, r)]
asm.check(clearances=clear, touching=touch, verbose=False)
print("приблуда −9.8…+10.1 -> шатун %.1f -> плечо 36:18 -> ложе ±%.1f; худший угол передачи (шатун к дуге стада) %.0f°" % (LC, worst, mu_min))
