# -*- coding: utf-8 -*-
"""Секция-1 v2, этаж 3 (мизинец): плечо с коротким плечом 16 вместо 10 + своя спица (27.09).

Зачем: лента ходила ±4.2 мм, рычаг 52:10 растягивал это в 5.2 раза — люфт и шаг мотора тоже ×5.2.
С плечом 52:16 (×3.25) лента ходит ±6.8 мм на тот же ход тележки ±22.

Почему 16, а не больше: при махе +25° пад стада подходит к бобышке стяжки (23.5, 150) — её край x = 21.
При 16 пад доходит до x 18.5, спица до 20. Остальные плиты секции не меняются: ось та же (0, 143),
стад на плите p3 тот же. Меняются только плечо 3 и спица 3 — стад теперь на x = 16, а лента
по-прежнему уходит на юг по жёлобу x 6..14 (голова спицы с «коленом» вбок на 6 мм).

В деке к этому — кривошип 3 R10 (gitara_crank3_big.py 10 45): ±6.8 мм ленты — это сектор ±43°.
Запуск: .venv-b123d\\Scripts\\python gitara_arm3_r16.py
"""
import math
from build123d import *

OUT = r"C:\App\gitar\2-0\Print\Print"
RS = 16.0                       # короткое плечо (было LANE_X = 10)
LB = 52.0                       # длинное плечо, как было
LANE_X = 10
AX_Y = 143                      # ось плеча 3 = CARTS_Y[3] + 52
FIT_D = 5.1
Z_FLOOR3, FLOOR, Z_DECK, DECK_T = 19.2, 1.6, 23, 3
CART_Y = 91
PHI = math.degrees(math.asin(22 / LB))          # мах плеча на ход тележки ±22
PHI_CHK = 22.6                                  # проверка — как в gitara_sec1_v2.py: на ±25° штырь и так упирается в концы прорезей плит (общая граница секции)


def BB(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))


# ---------- плечо 3: как в gitara_sec1_v2.py, только короткое плечо RS ----------
a = Pos(0, 0, 0.8) * Cylinder(5, 1.6)
a += BB(-2.5, 2.5, -LB, 0, 0, 1.6)
a += Pos(0, -LB, 0.8) * Cylinder(3.5, 1.6)
a += BB(0, RS, -2.5, 2.5, 0, 1.6)
a += Pos(RS, 0, 0.8) * Cylinder(4, 1.6)
a -= Pos(0, 0, 0.8) * Cylinder(FIT_D / 2, 1.8)
a += Pos(RS, 0, 2.5) * Cylinder(2.5, 1.8)
pin_h = (Z_DECK + DECK_T + 4) - (Z_FLOOR3 + 0.2 + 1.6)
a += Pos(0, -LB, 1.6 + pin_h / 2) * Cylinder(2.5, pin_h)
arm = Part() + a

# ---------- спица 3: кольцо на стаде (0,0), колено на 6 мм к жёлобу, дальше как было ----------
DX = LANE_X - RS                 # −6: жёлоб левее стада
END = 178 - AX_Y                 # конец спицы на мир y 178 (стык с лентой секции-2), как было
s = Pos(0, 0, 2.6) * Cylinder(5.0, 1.6)                           # кольцо (5.5 -> 5.0: на махе +12° задевало бобышку стяжки x 21)
s += BB(DX - 4, 4, 3, 7, 1.8, 3.4)                                # колено вбок, над плечом
s += BB(DX - 4, DX + 4, 3, 15, 1.8, 3.4)                          # ступень над плечом
s += BB(DX - 4, DX + 4, 11, 15, 0, 3.4)                           # соединитель вниз (дальше от диска оси)
s += BB(DX - 4, DX + 4, 11, END, 0, 1.6)                          # тело ленты на полу
s -= Pos(0, 0, 2.6) * Cylinder(FIT_D / 2, 1.8)                    # плотно на стад
s -= BB(DX - 4.1, DX + 4.1, END - 18, END + 0.1, 0.8, 1.7)        # стык-защёлка, как в v2
s += Pos(DX, END - 11.5, 2.0) * Cylinder(1.5, 2.4)
s -= Pos(DX, END - 6.5, 0.4) * Cylinder(1.75, 1.0)
spica = Part() + s

for p, n in ((arm, "gs1_arm3_r16"), (spica, "gs1_spica3_r16")):
    bb = p.bounding_box()
    print("%s: %.1f x %.1f x %.1f, solids %d" % (n, bb.size.X, bb.size.Y, bb.size.Z, len(p.solids())))
    export_stl(p, rf"{OUT}\{n}.stl")

# ================= ПРОВЕРКА: мах 0 / ±PHI с шагом ~5° =================
from clearance import Assembly

asm = Assembly()
asm.add("p3", OUT + r"\gs1_p3_mid_v2.stl", loc=(0, 0, Z_FLOOR3 - FLOOR))
asm.add("deck", OUT + r"\gs1_p4_deck_v2.stl", loc=(0, 0, Z_DECK))
clear, touch = [], []
angles = [-PHI_CHK, -PHI_CHK / 2, 0, PHI_CHK / 2, PHI_CHK]
for i, phi in enumerate(angles):
    t = math.radians(phi)
    an, sn, cn = "arm%d" % i, "sp%d" % i, "cart%d" % i
    z = Z_FLOOR3 + 0.2
    asm.add(an, OUT + r"\gs1_arm3_r16.stl", loc=(0, AX_Y, z), rz=phi)
    # спица едет за стадом жёстко (в жизни по X она гнётся на RS(1−cos) — проверяем с худшим сдвигом)
    asm.add(sn, OUT + r"\gs1_spica3_r16.stl", loc=(RS * math.cos(t), AX_Y + RS * math.sin(t), z))
    asm.add(cn, OUT + r"\gs1_cart_v2.stl", loc=(LB * math.sin(t), CART_Y, Z_DECK + DECK_T))
    clear += [(an, "p3", 0.01), (an, "deck", 0.15), (sn, "p3", 0.1), (sn, "deck", 0.15), (an, cn, 0.0)]
    touch += [(an, sn), (cn, "deck")]
asm.check(clearances=clear, touching=touch, verbose=False)
print("мах плеча ±%.1f°, лента ±%.2f мм, рычаг ×%.2f (было ×5.2)" % (PHI, RS * math.sin(math.radians(PHI)), LB / RS))
