# -*- coding: utf-8 -*-
r"""СТЕНД ОДНОГО ПАЛЬЦА НА МАГНИТНОЙ ПРИБЛУДЕ (09.10.2026) — вариант А «Магнитный + Кривошип».
Тот же стенд, что gitara_mini1.py (кусок грифа 52 x 110, высота до палубы 24, плечо 36 с прорезью, ложе v3),
но вместо мотора с кривошипом — приблуда со стола 89 (стержень s15_sterzhen + гильза 26 x 26 x 33):
  * приблуда лежит за южным краем стенда, ось стержня вдоль ленты (x = 10, как жёлоб ленты), на высоте 22;
  * катушка едет ±10 и прямо толкает/тянет ленту: под гильзой седло (mini3_sedlo) с пальцем Ø5 вниз
    в круглую дырку на хвосте ленты — лента ходит только вдоль Y, поэтому шарнир простой «палец в дырку»;
  * лента ±10 -> плечо 36 : 15..18 -> ложе ±20 (как mini1). Сила на ложе ≈ сила приблуды / 2…2.4;
  * дно одной деталью 52 x 216 (влезает в стол P2S): стенд + площадка приблуды со стойками стержня;
    лента проходит в рельсах по дну и в туннеле под северной стойкой; мостики сверху не дают ей выгнуться;
  * середина, палуба и плечо — от mini1 (стол 81), ложе — gs1_lozhe_v3. Новые детали: дно, лента, седло.
Седло держится на гильзе юбкой 1.5 мм; приклеить или стянуть стяжкой через два паза.
Запуск: .venv-b123d\Scripts\python gitara_mini3.py
"""
import math
import os
from build123d import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "Print", "Print")

W, L = 52, 110                  # стенд, как mini1
CART_Y, LB, XS = 16, 36.0, 15.0
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
RAIL_Y1 = Y_D + TRAVEL + 14
for x0, x1 in ((LANE_X - 5.0, LANE_X - 4.2), (LANE_X + 4.2, LANE_X + 5.0)):     # рельсы ленты
    base += BB(x0, x1, L, RAIL_Y1, Z_FL, Z_FL + 2.3)
base -= BB(LANE_X - 4.2, LANE_X + 4.2, L - 3, Y_D - XP + 1, Z_FL - 0.01, Z_FL + 2.5)   # проход в стене и туннель
for yb in (L + 3.5, ST_N0 + 10 + 5):                                             # мостики над лентой
    base += BB(LANE_X - 5.0, LANE_X + 5.0, yb - 1.5, yb + 1.5, Z_FL + 2.3, Z_FL + 3.3)
base = ties(base, 0.8, Z_CEIL, 1.3)

# ---------------- лента: стад вверх у плеча, длинный хвост с дыркой под палец седла ----------------
# система ленты: (0, 0) — ось плеча, лента в середине хода
JX0, JX1 = LANE_X - 4, LANE_X + 4
Y_PIN = Y_D - AX                                         # дырка: под центром гильзы
rib = BB(JX0, XS + 4.5, -4.5, 4.5, 0, 1.6)
rib += Pos(XS, 0, 1.6 + (Z_ARM - Z_RIB) / 2) * Cylinder(2.5, Z_ARM - Z_RIB)
rib += BB(JX0, JX1, -4.5, Y_PIN + 6, 0, 1.6)
rib -= Pos(LANE_X, Y_PIN, 0.8) * Cylinder((FIT_D + 0.1) / 2, 1.8)

# ---------------- седло (10.10): пластина под медью + две торцевые вилки, бортиков по бокам нет ----------------
# вилки обнимают крайние щёчки гильзы снаружи (по оси) и стержень с боков — до оси и выше, держат катушку вдоль хода
FORK_T, FORK_W = 2.5, 3.5                                   # толщина вилки вдоль оси, ширина зубца
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
pin_h = Z_SED - PIN_BOT
sed += Pos(0, 0, -pin_h / 2) * Cylinder(2.5, pin_h)

# медь для проверки: цилиндр Ø CU_D между крайними щёчками
cu = Rot(90, 0, 0) * Cylinder(CU_D / 2, BOB_L - 2 * 0.8)
cu -= Rot(90, 0, 0) * Cylinder(SQ / 2 + 2.5, BOB_L)

parts = [("mini3_base", base), ("mini3_lenta", rib), ("mini3_sedlo", sed), ("mini3_med_proverka", cu)]
for n, p in parts:
    p = Part() + p
    bb = p.bounding_box()
    print("%s: %.1f x %.1f x %.1f, solids %d" % (n, bb.size.X, bb.size.Y, bb.size.Z, len(p.solids())))
    export_stl(p, os.path.join(OUT, n + ".stl"))

# ================= ПРОВЕРКА: катушка ±10 шагом 2.5 =================
from clearance import Assembly


def S(n):
    return os.path.join(OUT, n + ".stl")


asm = Assembly()
asm.add("base", S("mini3_base"))
asm.add("mid", S("mini1_mid"), loc=(0, 0, Z_CEIL))
asm.add("deck", S("mini1_deck"), loc=(0, 0, Z_DECK))
asm.add("rod", S("s15_sterzhen_proverka"), loc=(LANE_X, Y_D, Z_AX), rz=90)
clear, touch = [("rod", "mid", 1.0)], [("mid", "deck"), ("rod", "base")]   # base<->mid: заглушка fcl 999, реальное пересечение 0
worst = 0
for i, u in enumerate([-10, -7.5, -5, -2.5, 0, 2.5, 5, 7.5, 10]):
    phi = math.degrees(math.atan2(u, XS))
    worst = max(worst, abs(LB * math.sin(math.radians(phi))))
    k, s, r, a, z = "kat%d" % i, "sed%d" % i, "rb%d" % i, "arm%d" % i, "lz%d" % i
    asm.add(k, S("s15_gilza_sobrannaya"), loc=(LANE_X, Y_D + u, Z_AX), rz=90)
    asm.add(s, S("mini3_sedlo"), loc=(LANE_X, Y_D + u, Z_SED))
    asm.add("cu%d" % i, S("mini3_med_proverka"), loc=(LANE_X, Y_D + u, Z_AX))
    asm.add(r, S("mini3_lenta"), loc=(0, AX + u, Z_RIB))
    asm.add(a, S("mini1_arm"), loc=(0, AX, Z_ARM), rz=phi)
    asm.add(z, S("gs1_lozhe_v3"), loc=(LB * math.sin(math.radians(phi)), CART_Y, Z_DECK + DECK_T - RUN))
    clear += [(k, "rod", 0.3), (k, "base", 0.5), (s, "base", 0.3), (s, "rod", 0.5), (s, "cu%d" % i, 0.3), ("cu%d" % i, "base", 0.5),
              (r, "base", 0.1), (r, "mid", 0.15),
              (a, "base", 0.01), (a, "mid", 0.15), (a, "deck", 0.15), (a, z, 0.0)]
    touch += [(a, r), (z, "deck"), (s, r)]
asm.check(clearances=clear, touching=touch, verbose=False)
print("приблуда ±%.0f -> лента ±%.0f -> ложе ±%.1f; дно %.0f x %.0f" % (TRAVEL, TRAVEL, worst, W, Y_END))
