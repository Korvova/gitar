# -*- coding: utf-8 -*-
r"""НАСТОЯЩИЙ СТЕРЖЕНЬ «МАГНИТНЫЙ СТЕРЖЕНЬ + БЕГУЩАЯ КАТУШКА» на дисках 15×5 N52 (05.10.2026, стол 89).
Пришло: 15 дисков Ø15×5 (5 полюсов по 3 диска), шайбы М5 DIN 9021 (Ø15 / 5.3 / 1.2), шайбы М8, лист 1.5.
3D МКЭ (fem3d_zhelob.py): одна шайба М5 в стыке групп — ×1.16 к силе; две — ×1.17 (не стоит); три — хуже.
  * s15_sterzhen — брус 17 × 17 с открытым сверху жёлобом 15.4 под диски и шайбы: 3 диска — шайба — 3 диска
    навстречу (N-N у шайбы, S-S у следующей) …; концы сплошные — в пазы стоек. Печать лёжа жёлобом вверх;
  * s15_trubka + 4 × s15_nasadka — гильза как у стола 88 (трубка с нижней щёчкой + насадки; 05.10 без трубки
    было неудобно собирать). Насадка = щёчка + втулка
    высотой с шаг 8.1 (четверть периода 32.4); надевать на трубку втулкой вниз;
    снаружи 26 × 26; дырка 18 по стержню 17 (зазор 0.5 — как на столе 88);
  * s15_lozhe — ложе на верх гильзы; s15_osnova — основа со стойками, ось стержня на 16;
  * s15_os_namotki — квадрат 17.85 под гильзу + шестигранник 7 под патрон шуруповёрта.
Фазы как раньше: A = отсек 1 + отсек 3 наоборот, B = 2 + 4 наоборот.
Запуск: .venv-b123d\Scripts\python magnit\gitara_sterzhen_15.py
"""
import os
import sys
from build123d import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "Print", "Print")

DM, HM = 15.0, 5.0               # диск
WASH = 1.2                       # шайба М5 DIN 9021
POLE = 3 * HM                    # 15
NP = 5
PITCH_P = POLE + WASH            # шаг полюсов 16.2
ROD_L = NP * POLE + (NP - 1) * WASH + 0.4    # 80.2 — магнитная часть с запасом
D_BORE = DM + 0.4                # жёлоб 15.4
WALL_R = 0.8
SQ = D_BORE + 2 * WALL_R         # 17.0
PLUG = 6.0
C = 0.5
HOLE = SQ + 2 * C                # 18.0
FL_S = 0.8
WALL = 0.6
# 05.10, рисунок владельца: вместо стенок трубки — 4 штырька по её углам; насадки скользят по штырькам углами
# втулки (в углах втулки — пазы под штырьки). Втулка сидит прямо по стержню — под провод место как без трубки.
PIN = 2.0                        # штырёк 2 × 2, стоит снаружи угла дырки
PIN_C = 0.15                     # зазор паза
SL_I = HOLE                      # 18 — втулка насадки внутри = дырка по стержню
SL_O = SL_I + 2 * WALL           # 19.2 — сердечник под провод (по сторонам)
P0, P1 = HOLE / 2, HOLE / 2 + PIN                   # штырёк: от 9 до 11 по x и y
N0, N1 = P0 - PIN_C, P1 + PIN_C                     # паз в насадке
B1 = N1 + WALL                                      # бобышка в углу втулки до 11.75
PITCH = 2 * PITCH_P / 4          # 8.1 — четверть периода
SEC = PITCH - FL_S               # 7.3
NSEC = 4
BOB_L = NSEC * PITCH + FL_S      # 33.2
OUTER = 26.0                     # 05.10: 24 → 26 (с трубкой); со штырьками под провод 3.4 по сторонам
Z_AX = 2.0 + OUTER / 2 + 1.0     # 16 — над плитой основы 1 мм


def BB(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))


# ---- стержень: брус с открытым жёлобом (ось дисков = ось бруса), печать лёжа жёлобом вверх ----
ROD_T = ROD_L + 2 * PLUG
rod = BB(-ROD_T / 2, ROD_T / 2, -SQ / 2, SQ / 2, -SQ / 2, SQ / 2)
rod -= BB(-ROD_L / 2, ROD_L / 2, -D_BORE / 2, D_BORE / 2, -D_BORE / 2, SQ / 2 + 0.1)
rod_print = Pos(0, 0, SQ / 2) * rod


# ---- гильза: крышка + 4 насадки (щёчкой на стол) ----
CORN = [(sx, sy) for sx in (1, -1) for sy in (1, -1)]


def corners(a, b, z0, z1):                       # 4 квадратика [a, b]² по углам
    r = None
    for sx, sy in CORN:
        q = BB(*sorted((sx * a, sx * b)), *sorted((sy * a, sy * b)), z0, z1)
        r = q if r is None else r + q
    return r


def shechka(slots):
    sh = BB(-OUTER / 2, OUTER / 2, -OUTER / 2, OUTER / 2, 0, FL_S)
    sh -= BB(-HOLE / 2, HOLE / 2, -HOLE / 2, HOLE / 2, -0.1, FL_S + 0.1)
    if slots:
        sh -= corners(N0, N1, -0.1, FL_S + 0.1)                                  # пазы под штырьки
    sh -= BB(-0.7, 0.7, -OUTER / 2 - 0.1, -SL_O / 2, -0.1, FL_S + 0.1)        # прорезь под выводы
    return sh


# основание: нижняя щёчка + 4 штырька по углам на всю длину гильзы (печать стоя, щёчкой на стол)
g_tr = shechka(False) + corners(P0, P1, FL_S - 0.1, BOB_L)
# насадка: щёчка + втулка по стержню, в углах втулки бобышки с пазами под штырьки
g_nas = shechka(True) + BB(-SL_O / 2, SL_O / 2, -SL_O / 2, SL_O / 2, 0, PITCH) + corners(P0 - WALL, B1, 0, PITCH)
g_nas -= BB(-SL_I / 2, SL_I / 2, -SL_I / 2, SL_I / 2, -0.1, PITCH + 0.1)
g_nas -= corners(N0, N1, -0.1, PITCH + 0.1)
kat_s = g_tr
for k in range(NSEC):
    kat_s = kat_s + Pos(0, 0, FL_S + (k + 1) * PITCH) * Rot(0, 180, 0) * g_nas
kat_s = Rot(0, 90, 0) * Pos(0, 0, -BOB_L / 2) * kat_s

# ---- ложе на верх гильзы ----
LZ_X, LZ_Y, LZ_T = BOB_L / 2 + 2.5, 13.0, 2.0
lozhe = BB(-LZ_X, LZ_X, -LZ_Y, LZ_Y, 0, LZ_T)
lozhe += BB(-BOB_L / 2 - 1.2, BOB_L / 2 + 1.2, -OUTER / 2 - 1.2, OUTER / 2 + 1.2, -1.5, 0)
lozhe -= BB(-BOB_L / 2 - 0.1, BOB_L / 2 + 0.1, -OUTER / 2 - 0.1, OUTER / 2 + 0.1, -1.6, 0.01)
for s in (1, -1):
    lozhe += BB(s * LZ_X - (1.6 if s > 0 else 0), s * LZ_X + (0 if s > 0 else 1.6), -LZ_Y, LZ_Y, LZ_T, LZ_T + 5)

# ---- основа со стойками ----
XP = ROD_L / 2
osnova = BB(-XP - PLUG - 8, XP + PLUG + 8, -16, 16, 0, 2)
for s in (1, -1):
    x0, x1 = sorted((s * (XP + 1.0), s * (XP + PLUG + 4)))
    osnova += BB(x0, x1, -SQ / 2 - 3, SQ / 2 + 3, 2, Z_AX + SQ / 2 + 2.5)
    g0, g1 = sorted((s * (XP + 0.9), s * (XP + PLUG + 0.1)))
    osnova -= BB(g0, g1, -SQ / 2 - 0.2, SQ / 2 + 0.2, Z_AX - SQ / 2 - 0.2, Z_AX + SQ / 2 + 3)

# ---- ось для намотки: квадрат под гильзу + шестигранник 7 под шуруповёрт ПО ОСИ квадрата (05.10: был у нижней
# грани — биение); печать СТОЯ: квадрат на столе, шестигранник вверх — соосно и без поддержек ----
SQ_W = HOLE - 0.15                                       # 17.85
HEX = 7.0
os_n = BB(-SQ_W / 2, SQ_W / 2, -SQ_W / 2, SQ_W / 2, 0, BOB_L + 4)
hexa = RegularPolygon(HEX / 2 / 0.8660254, 6)
os_n += Pos(0, 0, BOB_L + 4) * extrude(hexa, 25)
os_n = Part() + os_n

parts = [("s15_sterzhen", rod_print), ("s15_osnovanie_shtyri", g_tr), ("s15_nasadka", g_nas), ("s15_gilza_sobrannaya", kat_s),
         ("s15_lozhe", lozhe), ("s15_osnova", osnova), ("s15_os_namotki", os_n), ("s15_sterzhen_proverka", rod)]
for n, p in parts:
    p = Part() + p
    bb = p.bounding_box()
    print("%s: %.1f x %.1f x %.1f, solids %d" % (n, bb.size.X, bb.size.Y, bb.size.Z, len(p.solids())))
    export_stl(p, os.path.join(OUT, n + ".stl"))

sys.path.insert(0, os.path.dirname(HERE))
from clearance import Assembly


def S(n):
    return os.path.join(OUT, n + ".stl")


asm = Assembly()
asm.add("osnova", S("s15_osnova"))
asm.add("rod", S("s15_sterzhen_proverka"), loc=(0, 0, Z_AX))
travel = XP - BOB_L / 2 - 1.0
clear, touch = [], [("rod", "osnova")]
for i, x in enumerate((-travel, 0, travel)):
    k, l = "kat%d" % i, "lz%d" % i
    asm.add(k, S("s15_gilza_sobrannaya"), loc=(x, 0, Z_AX))
    asm.add(l, S("s15_lozhe"), loc=(x, 0, Z_AX + OUTER / 2))
    clear += [(k, "rod", 0.3), (k, "osnova", 0.5), (l, "osnova", 0.5)]
    touch += [(l, k)]
asm.check(clearances=clear, touching=touch, verbose=False)
depth = (OUTER - SL_O) / 2                                   # по сторонам; в углах меньше — бобышки
print("ход бегунка ±%.1f; отсек %.1f × %.1f мм -> ~%d витков провода 0.3 в отсеке" % (
    travel, SEC, depth, int(SEC * depth / 0.12)))
