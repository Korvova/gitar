# -*- coding: utf-8 -*-
r"""ОПЫТ «МАГНИТНЫЙ СТЕРЖЕНЬ + БЕГУЩАЯ КАТУШКА» (03.10.2026) из дисков владельца Ø4 × 2 и провода 0.3.
Идея владельца: стержень квадратный снаружи (катушка не крутится и собирать проще), внутри круглые гнёзда
под магниты; части клеить суперклеем; катушка катается по квадратному стержню.
  * sz_kasseta — кассета 5.6 × 5.6 × 8: гнездо Ø4.15 под 4 диска (полюс 8 мм); скос на углу торца — «здесь N».
    8 кассет склеить торцами в стержень: скос к скосу, гладкий к гладкому → полюса N-S-N-S;
  * sz_zaglushka — 2 заглушки 5.6 × 5.6 × 6 на концы стержня (в гнёзда стоек);
  * sz_zhelob — кондуктор: жёлоб для склейки стержня ровно (кассеты отталкиваются — прижать пальцем);
  * sz_katushka — гильза: квадратная дырка 6.0 (по стержню 5.6, зазор 0.2), 4 отсека по 3.4 с шагом 4.0
    (= четверть периода 16), щёчки 0.6, снаружи 13 × 13; ~50 витков провода 0.3 в отсеке; прорези под выводы.
    Фазы: A = отсек 1 + отсек 3 наоборот, B = 2 + 4 наоборот — к нашей плате вместо мотора;
  * sz_lozhe — ложе 24 × 20, снизу паз на верх щёчек гильзы — клеить;
  * sz_osnova — основа с двумя стойками, квадратные гнёзда под заглушки, ось стержня на высоте 9;
  * sz_os_namotki — ось для намотки: квадрат 5.85 под гильзу + шестигранник 5.85 под патрон шуруповёрта.
Ход бегунка ±22 (стержень 64 мм магнитов + заглушки). Всё печатается без поддержек.
Запуск: .venv-b123d\Scripts\python magnit\gitara_sterzhen_proba.py
"""
import os
import sys
from build123d import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "Print", "Print")

D_BORE = 4.6                     # жёлоб под диски Ø4 (04.10: 4.15 — туго, кассеты печатались плохо)
SQ = 6.4                         # стержень снаружи (стенки жёлоба 0.9)
POLE = 8.0                       # 4 диска × 2
NG = 8
PLUG = 6.0
ROD_L = NG * POLE                # 64
C = 0.2                          # зазор гильзы по стержню
HOLE = SQ + 2 * C                # 6.0
CORE_W = 0.6                     # стенка гильзы вокруг дырки
FL = 0.6                         # щёчка
PITCH = POLE / 2                 # шаг отсеков = четверть периода (16) = 4.0
SEC = PITCH - FL                 # ширина отсека 3.4
NSEC = 4
BOB_L = NSEC * PITCH + FL        # 16.6
OUTER = 13.0                     # гильза снаружи
Z_AX = 9.0                       # ось стержня над основой


def BB(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))


# ---- стержень одной деталью (владелец 04.10: кассеты и стрелки печатались плохо): брус SQ × SQ, концы
# сплошные — сразу в пазы стоек; сверху вдоль магнитной части открытый жёлоб под диски (ось дисков = ось бруса),
# диски вкладываются сверху группами по 4 навстречу (N-S-N-S) и проклеиваются; полярность — маркером.
# Печать лёжа жёлобом вверх, без поддержек.
ROD_T = ROD_L + 2 * PLUG
sterzhen_cel = BB(-ROD_T / 2, ROD_T / 2, -SQ / 2, SQ / 2, -SQ / 2, SQ / 2)
sterzhen_cel -= BB(-ROD_L / 2, ROD_L / 2, -D_BORE / 2, D_BORE / 2, -D_BORE / 2, SQ / 2 + 0.1)      # жёлоб: дно на 2.3 ниже оси
sterzhen_cel = Pos(0, 0, SQ / 2) * sterzhen_cel                                                     # низом на стол
kas = zag = None


# ---- гильза катушки: ось вдоль X, печать лёжа (щёчки стоят на столе) ----
kat = BB(-BOB_L / 2, BOB_L / 2, -(HOLE / 2 + CORE_W), HOLE / 2 + CORE_W, -(HOLE / 2 + CORE_W), HOLE / 2 + CORE_W)
for k in range(NSEC + 1):
    x = -BOB_L / 2 + k * PITCH
    kat += BB(x, x + FL, -OUTER / 2, OUTER / 2, -OUTER / 2, OUTER / 2)
kat -= BB(-BOB_L / 2 - 0.1, BOB_L / 2 + 0.1, -HOLE / 2, HOLE / 2, -HOLE / 2, HOLE / 2)   # квадратная дырка
for k in range(NSEC + 1):                                                         # прорези под выводы (снизу)
    x = -BOB_L / 2 + k * PITCH
    kat -= BB(x - 0.1, x + FL + 0.1, -0.6, 0.6, -OUTER / 2 - 0.1, -HOLE / 2 - CORE_W - 0.3)

# ---- гильза СБОРНАЯ (владелец 04.10: цельная лёжа печатается плохо): трубка-сердечник (печать стоя) +
# 5 плоских щёчек с квадратной дыркой (надеть и приклеить) + шаблон 3.4 мм — вкладывать между щёчками при склейке ----
TUBE = HOLE + 2 * CORE_W                                    # 8.0 снаружи
g_tr = BB(-TUBE / 2, TUBE / 2, -TUBE / 2, TUBE / 2, 0, BOB_L) - BB(-HOLE / 2, HOLE / 2, -HOLE / 2, HOLE / 2, -0.1, BOB_L + 0.1)
g_sh = BB(-OUTER / 2, OUTER / 2, -OUTER / 2, OUTER / 2, 0, FL) - BB(-TUBE / 2 - 0.1, TUBE / 2 + 0.1, -TUBE / 2 - 0.1, TUBE / 2 + 0.1, -0.1, FL + 0.1)
g_sh -= BB(-0.6, 0.6, -OUTER / 2 - 0.1, -TUBE / 2 + 0.05, -0.1, FL + 0.1)                     # прорезь под выводы
g_tpl = BB(0, SEC, -OUTER / 2, OUTER / 2, 0, 3) - BB(-0.1, SEC + 0.1, -TUBE / 2 - 0.15, TUBE / 2 + 0.15, -0.1, 3.1)   # шаблон-вилка 3.4

# ---- ложе: снизу паз на верх щёчек ----
LZ_X, LZ_Y, LZ_T = 12.0, 10.0, 2.0
lozhe = BB(-LZ_X, LZ_X, -LZ_Y, LZ_Y, 0, LZ_T)
lozhe += BB(-BOB_L / 2 - 1.2, BOB_L / 2 + 1.2, -OUTER / 2 - 1.2, OUTER / 2 + 1.2, -1.5, 0)   # юбка на гильзу
lozhe -= BB(-BOB_L / 2 - 0.1, BOB_L / 2 + 0.1, -OUTER / 2 - 0.1, OUTER / 2 + 0.1, -1.6, 0.01)
for s in (1, -1):
    lozhe += BB(s * LZ_X - (1.6 if s > 0 else 0), s * LZ_X + (0 if s > 0 else 1.6), -LZ_Y, LZ_Y, LZ_T, LZ_T + 5)

# ---- основа со стойками ----
XP = ROD_L / 2                                         # торец магнитной части
osnova = BB(-XP - PLUG - 8, XP + PLUG + 8, -12, 12, 0, 2)
for s in (1, -1):
    x0, x1 = sorted((s * (XP + 1.0), s * (XP + PLUG + 4)))
    osnova += BB(x0, x1, -6, 6, 2, Z_AX + SQ / 2 + 2.5)
    g0, g1 = sorted((s * (XP + 0.9), s * (XP + PLUG + 0.1)))
    osnova -= BB(g0, g1, -SQ / 2 - 0.15, SQ / 2 + 0.15, Z_AX - SQ / 2 - 0.15, Z_AX + SQ / 2 + 0.15)   # гнездо под заглушку
    osnova -= BB(g0, g1, -SQ / 2 - 0.15, SQ / 2 + 0.15, Z_AX, Z_AX + SQ / 2 + 3)                      # сверху открыто — вкладывать

# ---- ось для намотки (владелец 03.10: «чтобы было просто намотать»): квадрат под дырку гильзы + шестигранный
# хвостовик под патрон шуруповёрта; печать лёжа на грани, квадрат и шестигранник соосны (оба ровно 5.85 по граням) ----
SQ_W = HOLE - 0.15                                       # 5.85 — гильза сидит плотно, не проворачивается
os_n = BB(0, BOB_L + 4, -SQ_W / 2, SQ_W / 2, 0, SQ_W)
hexa = RegularPolygon(SQ_W / 2 / 0.8660254, 6, rotation=30)              # шестигранник 5.85 под ключ
os_n += Pos(BOB_L + 4, 0, SQ_W / 2) * Rot(0, 90, 0) * extrude(hexa, 25)
os_n = Part() + os_n

# ---- для проверки: стержень целиком (кассеты + заглушки) ----
sterzhen = BB(-XP - PLUG, XP + PLUG, -SQ / 2, SQ / 2, -SQ / 2, SQ / 2)

parts = [("sz_sterzhen", sterzhen_cel), ("sz_katushka", kat),
         ("sz_lozhe", lozhe), ("sz_gilza_trubka", g_tr), ("sz_gilza_shechka", g_sh), ("sz_gilza_shablon", g_tpl), ("sz_osnova", osnova), ("sz_os_namotki", os_n), ("sz_sterzhen_proverka", sterzhen)]
for n, p in parts:
    p = Part() + p
    bb = p.bounding_box()
    print("%s: %.1f x %.1f x %.1f, solids %d" % (n, bb.size.X, bb.size.Y, bb.size.Z, len(p.solids())))
    export_stl(p, os.path.join(OUT, n + ".stl"))

# ---- проверка: гильза по стержню на всём ходу, ложе на гильзе ----
sys.path.insert(0, os.path.dirname(HERE))
from clearance import Assembly


def S(n):
    return os.path.join(OUT, n + ".stl")


asm = Assembly()
asm.add("osnova", S("sz_osnova"))
asm.add("rod", S("sz_sterzhen_proverka"), loc=(0, 0, Z_AX))
travel = XP - BOB_L / 2 - 1.0
clear, touch = [], [("rod", "osnova")]
for i, x in enumerate((-travel, 0, travel)):
    k, l = "kat%d" % i, "lz%d" % i
    asm.add(k, S("sz_katushka"), loc=(x, 0, Z_AX))
    asm.add(l, S("sz_lozhe"), loc=(x, 0, Z_AX + OUTER / 2))
    clear += [(k, "rod", 0.15), (k, "osnova", 0.5), (l, "osnova", 0.5)]
    touch += [(l, k)]
asm.check(clearances=clear, touching=touch, verbose=False)
print("ход бегунка ±%.1f; отсек %.1f × %.1f мм -> ~%d витков провода 0.3" % (
    travel, SEC, (OUTER - HOLE) / 2 - CORE_W, int(0.5 * SEC * ((OUTER - HOLE) / 2 - CORE_W) / 0.0908)))
