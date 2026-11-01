# -*- coding: utf-8 -*-
r"""Опыт «дно грифа в руках» (01.11.2026, вики 20.8): полоса 2.5 мм длиной 295 (влезает по диагонали стола 256),
ширина 52 → 58 (гриф расширяется к XII), сверху гравировка 6 струн и меток ладов. Печать PETG плашмя, заполнение 100%.
Держать как гитару боком и проверить: пружинит ли от нажима, от рывка на себя, от нажатия на голову.
Запуск: .venv-b123d\Scripts\python test_polosa_grifa.py
"""
import math
import os
from build123d import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Print", "Print")
L, W0, W1, T = 295.0, 52.0, 58.0, 2.5
GR = 0.4                                          # глубина гравировки

pol = extrude(make_face(Polyline((0, -W0 / 2), (L, -W1 / 2), (L, W1 / 2), (0, W0 / 2), (0, -W0 / 2))), T)
for sy in (-22.0, -13.2, -4.4, 4.4, 13.2, 22.0):    # струны — параллельные, шаг 8.8
    pol -= Pos(L / 2, sy, T - GR / 2 + 0.01) * Box(L - 6, 0.6, GR)
for n in range(1, 13):                            # метки ладов по краям (мензура 650, порожек в x = 0)
    x = 650 - 650 / 2 ** (n / 12)
    if x < L - 2:
        w = (W0 + (W1 - W0) * x / L) / 2
        for sy in (1, -1):
            pol -= Pos(x, sy * (w - 2.5), T - GR / 2 + 0.01) * Box(0.8, 5.2, GR)
pol = Rot(0, 0, 45) * Pos(-L / 2, 0, 0) * pol     # по диагонали стола
p = Part() + pol
bb = p.bounding_box()
print("test_polosa_grifa: %.1f x %.1f x %.1f" % (bb.size.X, bb.size.Y, bb.size.Z))
export_stl(p, os.path.join(OUT, "test_polosa_grifa.stl"))
