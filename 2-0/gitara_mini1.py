# -*- coding: utf-8 -*-
"""СТЕНД ОДНОГО ПАЛЬЦА (указательный, 27.09.2026) — проверить рычаг ×2 на минимуме печати.

Кусок грифа 52 x 110, высота до верха палубы 24 (владелец: 23–25). Механика как в гриф ×2 для
этажа 0, только без секций 2–3: мотор стоит сразу за плечом, спица с хвостом — одна короткая лента.
  * мотор 0 снизу дна на проставке-кольце (gdk_spacer0_x2), кривошип R10 цилиндром в окне дна
    (gdk_crank0_x2) — полный оборот = струны 1..6..1, кулиса ленты открыта в обе стороны;
  * ВСЕ ДЕТАЛИ ПЕЧАТАЮТСЯ БЕЗ ПОДДЕРЖЕК (владелец 27.09): лента — плоская со стадом ВВЕРХ, плечо —
    плоское с прорезью вдоль короткого плеча (стад в ней скользит по радиусу 15..18); плечо лежит
    на ступеньке стада оси НАД лентой. Раньше было наоборот: голова ленты с прорезью висела над плечом.
    Передаточное: ложе x = 36·sin(atan(u / 15)) — ×2.4 в середине хода, ×2 у краёв; лента ±10 → ложе ±20;
  * по X ленту у кулисы держат рейки на дне, сверху всё прижимает потолок середины;
  * стопка: дно (стенки до потолка) + середина (потолок + стенки до палубы) + палуба; 6 винтов М3
    сквозь палубу и середину в бобышки дна (самонарез Ø2.6).
Мотор висит под дном на 26 мм — стенд ставить на край стола или на подставку.
Запуск: .venv-b123d\\Scripts\\python gitara_mini1.py
"""
import math
import os
from build123d import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "Print", "Print")

W, L = 52, 110
CART_Y = 16                     # ложе
LB = 36.0                       # длинное плечо
XS = 15.0                       # стад ленты: x (ложе ±20 при ленте ±10: 36·sin(atan(10/15)) = 20)
AX = CART_Y + LB                # ось плеча: 52
MY = 80.0                       # мотор
R_CR, PIN_R, SLOT_C = 10.0, 2.5, 0.15
DISK_R = R_CR + PIN_R + 1.0     # как gdk_crank0_x2
FIT_D = 5.1
LANE_X = 10
Z_FL = 3.0                      # пол этажа 0 (верх дна)
Z_RIB = Z_FL + 0.15             # лента
Z_ARM = Z_RIB + 1.6 + 0.2       # плечо над лентой: 4.95
Z_CEIL = 6.8                    # потолок (низ середины)
CEIL_T = 1.6
Z_DECK, DECK_T = 21.0, 3.0      # палуба: верх 24
RUN = 2.9                       # полозья ложа
EAR_R, EAR_ANG, EAR_SIGN = 43.85 / 2, 56.0, 1                    # мотор 0 — как в gitara_deka.py
TIE = [(23.5, 6), (-23.5, 6), (23.5, 32), (-23.5, 45), (23.5, L - 8), (-23.5, L - 8)]
# (23.5, 32): севернее 26 — пад штыря, восточнее ходит короткое плечо; на западе свободно


def BB(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))


def ear_holes():
    a = math.radians(EAR_ANG)
    dx, dy = EAR_R * math.sin(a), EAR_R * math.cos(a)
    return [(EAR_SIGN * dx, MY + dy), (-EAR_SIGN * dx, MY - dy)]


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


SLOT = BB(-24.5, 24.5, CART_Y - 3.5, CART_Y + LB * (1 - math.cos(math.radians(37.7))) + 3.2, -50, 50)   # прорезь штыря, как v3

# ---------------- дно: пол + стенки до потолка, стад оси со ступенькой, окно кривошипа, рейки ----------------
base = BB(-26, 26, 0, L, 0, Z_FL) + walls(Z_FL, Z_CEIL)
base += Pos(0, AX, (Z_FL + Z_ARM - 0.05) / 2) * Cylinder(4.0, Z_ARM - 0.05 - Z_FL)   # ступенька: плечо лежит над лентой
base += Pos(0, AX, (Z_FL + Z_CEIL - 0.2) / 2) * Cylinder(2.5, Z_CEIL - 0.2 - Z_FL)   # стад оси Ø5
YH = PIN_R + SLOT_C + 3.0                                           # полуширина кулисы ленты
for s in (1, -1):                                                   # рейки: держат кулису по X
    base += BB(s * 14.3, s * 15.6, MY - 9.0, MY + 9.0, Z_FL, Z_CEIL - 0.2)
base -= Pos(0, MY, Z_FL / 2) * Cylinder(DISK_R + 0.5, Z_FL + 0.2)  # окно диска
for ex, ey in ear_holes():
    base -= Pos(ex, ey, Z_FL / 2) * Cylinder(1.7, Z_FL + 0.2)
base = ties(base, 0.8, Z_CEIL, 1.3)                                # самонарез, дно снизу целое 0.8

# ---------------- середина: потолок + стенки до палубы ----------------
mid = BB(-26, 26, 0, L, 0, CEIL_T) + walls(CEIL_T, Z_DECK - Z_CEIL)
mid -= SLOT
mid = ties(mid, 0, Z_DECK - Z_CEIL, 1.7)

# ---------------- палуба: прорезь, русло ложа, струны ----------------
deck = BB(-26, 26, 0, L, 0, DECK_T) - SLOT
for ry in (CART_Y - 12, CART_Y + 12):                               # бортики русла ложа (как v3)
    deck += BB(-26, 26, ry - 1.5, ry + 1.5, DECK_T, DECK_T + 4)
deck = ties(deck, 0, DECK_T + 4, 1.7)
for sx in (-22.0, -13.2, -4.4, 4.4, 13.2, 22.0):                    # линии струн за руслом — для вида
    y0, y1 = CART_Y + 13.5 + 1.5, L - 1
    r = Pos(sx, (y0 + y1) / 2, DECK_T) * Rot(90, 0, 0) * Cylinder(0.6, y1 - y0)
    r -= BB(sx - 1, sx + 1, y0 - 1, y1 + 1, DECK_T - 0.7, DECK_T)
    for tx, ty in TIE:
        if abs(tx - sx) < 3.6:
            r -= Pos(tx, ty, DECK_T) * Cylinder(3.6, 3)
    deck += r

# ---------------- плечо: плоское, прорезь вдоль короткого плеча, штырь вверх ----------------
U_MAX = R_CR
SX0 = XS - FIT_D / 2 - 0.1                                          # стад ходит по радиусу 15 .. 18.03
SX1 = math.hypot(XS, U_MAX) + FIT_D / 2 + 0.1
SW = FIT_D / 2 + 2.2
PIN_TOP = Z_DECK + DECK_T + 1.8
arm = Pos(0, 0, 0.8) * Cylinder(5, 1.6)
arm += BB(-2.5, 2.5, -LB, 0, 0, 1.6) + Pos(0, -LB, 0.8) * Cylinder(3.5, 1.6)
arm += BB(0, SX1 + 2.2, -SW, SW, 0, 1.6)                            # короткое плечо с прорезью
arm -= BB(SX0, SX1, -(FIT_D + 0.02) / 2, (FIT_D + 0.02) / 2, -0.1, 1.7)
arm -= Pos(0, 0, 0.8) * Cylinder(FIT_D / 2, 1.8)                    # на стад оси — плотно
pin_h = PIN_TOP - (Z_ARM + 1.6)
arm += Pos(0, -LB, 1.6 + pin_h / 2) * Cylinder(2.5, pin_h)

# ---------------- лента: плоская, стад вверх в прорезь плеча, кулиса у мотора ----------------
# система: (0, 0) — ось плеча, лента в середине хода; едет только по Y
JX0, JX1 = LANE_X - 4, LANE_X + 4
YC = MY - AX                                                        # кулиса: 28
SH = R_CR + PIN_R + 0.3                                             # полудлина прорези кулисы (в обе стороны)
rib = BB(JX0, XS + 4.5, -4.5, 4.5, 0, 1.6)                          # лапка под стад
rib += Pos(XS, 0, 1.6 + (Z_ARM + 1.6 - Z_RIB - 1.6) / 2) * Cylinder(2.5, Z_ARM + 1.6 - Z_RIB - 1.6)   # стад до верха плеча
rib += BB(JX0, JX1, -4.5, YC + YH, 0, 1.6)                          # тело по жёлобу
rib += BB(-SH - 1.2, JX0, YC - YH, YC + YH, 0, 1.6)                 # площадка кулисы (на запад)
rib -= BB(-SH, SH, YC - (PIN_R + SLOT_C), YC + (PIN_R + SLOT_C), -0.1, 1.7)

parts = [("mini1_base", base), ("mini1_mid", mid), ("mini1_deck", deck), ("mini1_arm", arm), ("mini1_lenta", rib)]
for n, p in parts:
    p = Part() + p
    bb = p.bounding_box()
    print("%s: %.1f x %.1f x %.1f, solids %d" % (n, bb.size.X, bb.size.Y, bb.size.Z, len(p.solids())))
    export_stl(p, os.path.join(OUT, n + ".stl"))

# ================= ПРОВЕРКА: полный оборот кривошипа шагом 30° =================
from clearance import Assembly


def S(n):
    return os.path.join(OUT, n + ".stl")


asm = Assembly()
asm.add("base", S("mini1_base"))
asm.add("mid", S("mini1_mid"), loc=(0, 0, Z_CEIL))
asm.add("deck", S("mini1_deck"), loc=(0, 0, Z_DECK))
asm.add("spacer", S("gdk_spacer0_x2"), loc=(0, MY, 0))
asm.add("motor", S("gdk_motor0_model"), loc=(0, MY, -4.0))
clear, touch = [], [("base", "mid"), ("mid", "deck"), ("spacer", "base"), ("motor", "spacer")]
worst = 0
for th in range(0, 360, 30):
    t = math.radians(th)
    u = R_CR * math.sin(t)                                          # палец кривошипа на +X: лента = R·sin θ
    phi = math.degrees(math.atan2(u, XS))
    worst = max(worst, abs(LB * math.sin(math.radians(phi))))
    c, r, a, z = "cr%d" % th, "rb%d" % th, "arm%d" % th, "lz%d" % th
    asm.add(c, S("gdk_crank0_x2"), loc=(0, MY, 0), rz=th)
    asm.add(r, S("mini1_lenta"), loc=(0, AX + u, Z_RIB))
    asm.add(a, S("mini1_arm"), loc=(0, AX, Z_ARM), rz=phi)
    asm.add(z, S("gs1_lozhe_v3"), loc=(LB * math.sin(math.radians(phi)), CART_Y, Z_DECK + DECK_T - RUN))
    clear += [(c, "base", 0.3), (c, "spacer", 0.3), (c, r, 0.1), (c, "mid", 0.2),
              (r, "base", 0.1), (r, "mid", 0.15), (r, "motor", 0.5),
              (a, "base", 0.01), (a, "mid", 0.15), (a, "deck", 0.15), (a, z, 0.0)]
    touch += [(a, r), (z, "deck")]
asm.check(clearances=clear, touching=touch, verbose=False)
print("стенд: лента ±10 (кривошип R10, полный оборот) -> ложе ±%.1f; высота до палубы %.0f" % (worst, Z_DECK + DECK_T))
