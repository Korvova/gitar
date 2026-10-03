# -*- coding: utf-8 -*-
r"""ПРОБА МАГНИТНОГО РУСЛА (03.10.2026) — под магниты 20 × 10 × 5 N52 (по толщине 5) и провод ПЭТВ-2 0.3.

Схема (расчёт magnit/compare_magnets.py, lane_2phase.py): неподвижная пластина из 8 плоских катушек
без железа на ширину 52, её обнимает U-скоба: по 3 магнита с каждой стороны стоймя (10 вдоль хода,
20 по высоте), полюса N-S-N, напротив — разные полюса; снаружи стальные пластинки 1.5. Щель 4.
Катушки — в две фазы, к нашей плате с TMC2209 вместо мотора:
    фаза A: катушки 1, 4, 7 прямо + 6 наоборот;  фаза B: 2, 5, 8 прямо + 3 наоборот
    (номера 1..8 слева направо — выдавлены на нижней планке рамки).
Детали:
  mag_opravka_a / _b  — оправка: щёчка с сердечником 1.6 × 16 (окно катушки) + прижимная щёчка,
                        зазор 3.0 = толщина катушки (упоры сверху и снизу), 2 × М3;
  mag_ramka           — рамка 3 мм: окно 52 × 21 под 8 катушек, верхняя планка — рельс для скобы,
                        снизу лапки в основу; пазы под выводы;
  mag_osnova          — основа 90 × 40, держит рамку стоймя;
  mag_skoba           — U-скоба: гнёзда под 6 магнитов (вставлять снизу) и 2 стальные пластинки
                        30 × 20 × 1.5, мостик сверху с пазом — едет по верхней планке рамки; сверху ложе.
Пробный стенд шире грифа: скоба 33 мм при ходе ±22 выходит за край на 11 мм (в грифе — решать отдельно).
Запуск: .venv-b123d\Scripts\python magnit\gitara_magnit_proba.py
"""
import os
from build123d import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "Print", "Print")

# ---- катушка ----
NC, CW = 8, 6.5                  # 8 катушек по 6.5 на ширину 52
WIN_X, WIN_Z = 1.6, 16.0         # окно = активная высота 16
CT = 3.0                         # толщина катушки (по Y)
LEG = (CW - WIN_X) / 2           # ветвь 2.45
CH = WIN_Z + 2 * LEG             # высота катушки 20.9
# ---- магниты и скоба ----
MX, MZ, MT = 10.0, 20.0, 5.0     # магнит: вдоль хода, по высоте, толщина (намагничен по ней)
GAP = 4.0                        # щель между рядами магнитов (катушка 3 + 0.5 с каждой стороны)
ST = 1.5                         # сталь
WALL = 1.2
C = 0.15                         # зазоры посадок
# ---- высоты (z = 0 — низ катушек) ----
Z_ACT = LEG + WIN_Z / 2          # центр активной зоны 10.45
Z_M0 = Z_ACT - MZ / 2            # низ магнитов 0.45
BAR = 3.0                        # планки рамки
Z_TOP = CH + BAR                 # верх рамки 23.9
TRAVEL = 22.0


def BB(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))


# ================= оправка =================
CHEEK_X, CHEEK_Z, CHEEK_T = 16.0, 34.0, 2.5
SCREW_Z = CH / 2 + 3.0           # винты М3 выше и ниже катушки
op_a = BB(-CHEEK_X / 2, CHEEK_X / 2, -CHEEK_Z / 2, CHEEK_Z / 2, 0, CHEEK_T)          # щёчка (в своей системе: z — толщина)
op_a += BB(-WIN_X / 2 + 0.05, WIN_X / 2 - 0.05, -WIN_Z / 2 + 0.05, WIN_Z / 2 - 0.05, CHEEK_T, CHEEK_T + CT + 1.5)  # сердечник (+1.5 в прижимную)
op_b = BB(-CHEEK_X / 2, CHEEK_X / 2, -CHEEK_Z / 2, CHEEK_Z / 2, 0, CHEEK_T)
op_b -= BB(-WIN_X / 2 - 0.1, WIN_X / 2 + 0.1, -WIN_Z / 2 - 0.1, WIN_Z / 2 + 0.1, -0.1, CHEEK_T + 0.1)   # надевается на сердечник
op_b -= BB(WIN_X / 2, WIN_X / 2 + 0.6, WIN_Z / 2 - 1.0, CHEEK_Z / 2 + 0.1, -0.1, CHEEK_T + 0.1)        # прорезь под начало провода
for z in (-SCREW_Z, SCREW_Z):
    op_a -= Pos(0, z, CHEEK_T / 2) * Cylinder(1.3, CHEEK_T + 0.2)                     # самонарез М3
    op_b -= Pos(0, z, CHEEK_T / 2) * Cylinder(1.7, CHEEK_T + 0.2)
op_a += BB(-CHEEK_X / 2, CHEEK_X / 2, -CHEEK_Z / 2, -CHEEK_Z / 2 + 2, CHEEK_T, CHEEK_T + CT)   # упоры: зазор ровно CT
op_a += BB(-CHEEK_X / 2, CHEEK_X / 2, CHEEK_Z / 2 - 2, CHEEK_Z / 2, CHEEK_T, CHEEK_T + CT)
for z in (-SCREW_Z, SCREW_Z):
    op_a -= Pos(0, z, CHEEK_T + CT / 2) * Cylinder(1.3, CT + 0.2)
# защёлки (владелец 03.10: без винтов — отжал язычок и открыл): на длинных сторонах щёчки посередине
# гибкий язычок 1.2 × 8 вверх, крючок со скосом сверху — прижимная щёчка давится сверху и защёлкивается;
# выше крючка — ушко под палец. Винтовые дырки остались — на всякий случай.
ARM_T, ARM_W, LATCH_C = 1.2, 8.0, 0.15
Z_B_TOP = CHEEK_T + CT + CHEEK_T                                   # верх прижимной щёчки: 8.0
for s in (1, -1):
    x0 = s * (CHEEK_X / 2 + LATCH_C)                               # внутренняя грань язычка
    x1 = s * (CHEEK_X / 2 + LATCH_C + ARM_T)
    op_a += BB(min(x0, x1), max(x0, x1), -ARM_W / 2, ARM_W / 2, 0, Z_B_TOP + 4.0)   # язычок от низа щёчки
    op_a += BB(s * (CHEEK_X / 2 - 0.01), min(x0, x1) if s > 0 else max(x0, x1), -ARM_W / 2, ARM_W / 2, 0, CHEEK_T)  # перемычка к щёчке
    hook = Polyline((x0, Z_B_TOP + 0.05), (x0 - s * 1.1, Z_B_TOP + 0.05), (x0, Z_B_TOP + 1.6), (x0, Z_B_TOP + 0.05))
    op_a += extrude(Plane.XZ * make_face(hook), ARM_W / 2, both=True)   # крючок: снизу плоский, сверху скос
    ear0, ear1 = sorted((x1, x1 + s * 2.5))
    op_a += BB(ear0, ear1, -ARM_W / 2, ARM_W / 2, Z_B_TOP + 2.8, Z_B_TOP + 4.0)        # ушко наружу — отжимать пальцем

# ================= рамка катушек =================
RX = NC * CW / 2                 # 26
ramka = BB(-RX - 3, RX + 3, -CT / 2, CT / 2, -BAR, Z_TOP)
ramka -= BB(-RX, RX, -CT / 2 - 0.1, CT / 2 + 0.1, 0, CH)                              # окно под катушки (вклеить)
for k in range(NC):                                                                    # пазы под выводы в нижней планке
    x = -RX + (k + 0.5) * CW
    ramka -= BB(x - 1.5, x + 1.5, -CT / 2 - 0.1, CT / 2 + 0.1, -1.2, 0.01)
for x in (-20.0, 20.0):                                                                 # лапки в основу
    ramka += BB(x - 3, x + 3, -CT / 2, CT / 2, -BAR - 4, -BAR)
# номера катушек: точки на нижней планке (1..8 точек — сколько номер)
for k in range(NC):
    x = -RX + (k + 0.5) * CW
    for d in range(k + 1):
        xx = x - 2.6 + d * 0.65
        ramka -= Pos(xx, CT / 2, -BAR + 0.9) * Box(0.35, 0.6, 0.35)

# ================= основа =================
osnova = BB(-45, 45, -20, 20, -BAR - 4 - 3, -BAR - 4)
for x in (-20.0, 20.0):
    osnova += BB(x - 5, x + 5, -CT / 2 - 2, CT / 2 + 2, -BAR - 4, -BAR)               # стойка под лапку
    osnova -= BB(x - 3 - C, x + 3 + C, -CT / 2 - C, CT / 2 + C, -BAR - 4 - 1, -BAR + 0.1)
for x, y in ((-40, -15), (40, -15), (-40, 15), (40, 15)):
    osnova -= Pos(x, y, -BAR - 4 - 1.5) * Cylinder(1.7, 3.2)                          # к столу шурупами — по желанию

# ================= скоба =================
YM0, YM1 = GAP / 2, GAP / 2 + MT                    # магнит по Y: 2 .. 7
YS1 = YM1 + ST + 0.1                                 # сталь до 8.6
YW1 = YS1 + WALL                                     # наружная стенка до 9.8
XM = 3 * MX / 2 + C                                  # гнездо магнитов по X: ±15.15
XE = XM + WALL                                       # торцевые стенки ±16.35
Z_BR0 = Z_TOP - 1.5                                  # низ мостика (паз 1.5 глубиной садится на верхнюю планку)
Z_BR1 = Z_BR0 + 2.5
skoba = BB(-XE, XE, -YW1, YW1, Z_M0 - 0.6, Z_BR1)                                     # сплошной брус
skoba -= BB(-XE - 0.1, XE + 0.1, -YM0, YM0, Z_M0 - 0.7, Z_BR0)                         # щель под рамку (ниже мостика)
skoba -= BB(-XE - 0.1, XE + 0.1, -CT / 2 - 0.2, CT / 2 + 0.2, Z_BR0 - 0.01, Z_TOP + 0.01)   # паз мостика на верхнюю планку
for s in (1, -1):
    y0, y1 = sorted((s * YM0, s * YS1))
    skoba -= BB(-XM, XM, y0 - 0.01 * s, y1, Z_M0 - 0.7, Z_M0 + MZ + C)               # гнездо: 3 магнита + сталь, вставлять снизу
# ложе сверху на мостике
LZ_X, LZ_Y = 12.0, 11.0
skoba += BB(-LZ_X, LZ_X, -LZ_Y, LZ_Y, Z_BR1, Z_BR1 + 1.5)
for s in (1, -1):
    skoba += BB(s * LZ_X - (1.6 if s > 0 else 0), s * LZ_X + (0 if s > 0 else 1.6), -LZ_Y, LZ_Y, Z_BR1 + 1.5, Z_BR1 + 6.5)

# магниты и сталь — только для проверки и сцены
mag = Part()
stal = Part()
for s in (1, -1):
    for p in range(3):
        y0, y1 = sorted((s * YM0, s * YM1))
        mag += BB(-15 + p * MX, -5 + p * MX, y0, y1, Z_M0, Z_M0 + MZ)
    y0, y1 = sorted((s * YM1, s * (YM1 + ST)))
    stal += BB(-15, 15, y0, y1, Z_M0, Z_M0 + MZ)
kat = Part()
for k in range(NC):
    x0 = -RX + k * CW
    kat += BB(x0, x0 + CW, -CT / 2, CT / 2, 0, CH) - BB(x0 + LEG, x0 + CW - LEG, -CT, CT, LEG, LEG + WIN_Z)

parts = [("mag_opravka_a", op_a), ("mag_opravka_b", op_b), ("mag_ramka", ramka), ("mag_osnova", osnova),
         ("mag_skoba", skoba), ("mag_magnity_proverka", mag), ("mag_stal_proverka", stal), ("mag_katushki_proverka", kat)]
for n, p in parts:
    p = Part() + p
    bb = p.bounding_box()
    print("%s: %.1f x %.1f x %.1f, solids %d" % (n, bb.size.X, bb.size.Y, bb.size.Z, len(p.solids())))
    export_stl(p, os.path.join(OUT, n + ".stl"))

# ================= проверка: ход скобы ±22 =================
import sys
sys.path.insert(0, os.path.dirname(HERE))
from clearance import Assembly


def S(n):
    return os.path.join(OUT, n + ".stl")


asm = Assembly()
asm.add("ramka", S("mag_ramka"))
asm.add("kat", S("mag_katushki_proverka"))
asm.add("osnova", S("mag_osnova"))
clear, touch = [], [("ramka", "osnova")]
for i, x in enumerate((-TRAVEL, -11, 0, 11, TRAVEL)):
    sk, mg, st = "sk%d" % i, "mg%d" % i, "st%d" % i
    asm.add(sk, S("mag_skoba"), loc=(x, 0, 0))
    asm.add(mg, S("mag_magnity_proverka"), loc=(x, 0, 0))
    asm.add(st, S("mag_stal_proverka"), loc=(x, 0, 0))
    clear += [(mg, "kat", 0.4), (mg, "ramka", 0.4), (st, "ramka", 0.4), (sk, "osnova", 0.3), (mg, "osnova", 0.3)]
    touch += [(sk, "ramka"), (mg, sk), (st, sk)]                     # мостик лежит на верхней планке; магниты и сталь в гнёздах
asm.check(clearances=clear, touching=touch, verbose=False)
wire = NC * int(0.5 * LEG * CT / 0.0908) * 2 * ((CW - LEG) + (CH - LEG)) / 1000
print("катушка: ~%d витков провода 0.3; на 8 катушек ~%.0f м (есть 20 м); скоба ходит ±%.0f" % (int(0.5 * LEG * CT / 0.0908), wire, TRAVEL))
