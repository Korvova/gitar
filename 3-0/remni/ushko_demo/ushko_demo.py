# -*- coding: utf-8 -*-
r"""Показ идеи (26.11): «ушко» на спинке ремня + кармашек тележки — тележка без клея. Ремень под сопло 0.4 (remen_04), ширина 3.
Ушко — выступ 2 × 1 на спинке верхней ветви, только в нижних 2 мм ремня; кармашек тележки садится на него сверху,
потолок кармашка — в верхнем 1 мм ремня, поэтому по высоте ничего не добавляется. С внутренней стороны (зубья) ничего нет —
там проходит ведущий ролик. Запуск: ..\..\..\2-0\.venv-b123d\Scripts\python ushko_demo.py, потом blender -b -P ushko_scene.py"""
import math, os
from build123d import *
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
XC, R, TB, H, WT, W = 22.0, 2.5, 0.9, 0.7, 0.9, 3.0
LOOP = 4 * XC + 2 * math.pi * R; N = 39; P = LOOP / N


def at(s):                                        # точка на внутренней стороне петли, касательная, нормаль внутрь
    s %= LOOP
    if s < 2 * XC: return (-XC + s, R), (1, 0), (0, -1)
    s -= 2 * XC
    if s < math.pi * R:
        a = math.pi / 2 - s / R; return (XC + R * math.cos(a), R * math.sin(a)), (math.sin(a), -math.cos(a)), (-math.cos(a), -math.sin(a))
    s -= math.pi * R
    if s < 2 * XC: return (XC - s, -R), (-1, 0), (0, 1)
    s -= 2 * XC
    a = -math.pi / 2 - s / R; return (-XC + R * math.cos(a), R * math.sin(a)), (math.sin(a), -math.cos(a)), (-math.cos(a), -math.sin(a))


def stadium(r):
    return Pos(0, 0, 0) * (Box(2 * XC, 2 * r, W, align=(Align.CENTER, Align.CENTER, Align.MIN)) +
                           Pos(-XC, 0, 0) * Cylinder(r, W, align=(Align.CENTER, Align.CENTER, Align.MIN)) +
                           Pos(XC, 0, 0) * Cylinder(r, W, align=(Align.CENTER, Align.CENTER, Align.MIN)))


belt = stadium(R + TB) - Pos(0, 0, -1) * Box(2 * XC, 2 * R, W + 2, align=(Align.CENTER, Align.CENTER, Align.MIN)) \
       - Pos(-XC, 0, -1) * Cylinder(R, W + 2, align=(Align.CENTER, Align.CENTER, Align.MIN)) - Pos(XC, 0, -1) * Cylinder(R, W + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
for k in range(N):
    (x, y), (tx, ty), (nx, ny) = at(XC + (k + 0.5) * P)          # зубья между ними — ось x = 0 приходится на впадину
    u = WT / 2
    pts = [(x - tx * u - nx * 0.05, y - ty * u - ny * 0.05), (x + tx * u - nx * 0.05, y + ty * u - ny * 0.05),
           (x + tx * u + nx * H, y + ty * u + ny * H), (x - tx * u + nx * H, y - ty * u + ny * H)]
    belt += extrude(make_face(Polyline(*(pts + [pts[0]]))), W)
LUG = (1.0, R + TB, R + TB + 1.0, 2.0)                          # ушко: ±1 по x, от спинки на 1.0, высотой 2.0 (нижние 2 мм)
belt += Pos(0, (LUG[1] + LUG[2]) / 2, 0) * Box(2 * LUG[0], LUG[2] - LUG[1] + 0.02, LUG[3], align=(Align.CENTER, Align.CENTER, Align.MIN))

G, WL = 0.1, 0.9                                                # зазор, стенки кармашка (2 линии сопла 0.4)
Y0 = R + TB + G                                                 # внутренняя грань кармашка — в 0.1 от спинки
pocket = Pos(0, 0, 0) * Box(2 * (LUG[0] + G + WL), (LUG[2] + G + WL) - Y0, W - 0.3, align=(Align.CENTER, Align.MIN, Align.MIN))
pocket = Pos(0, Y0, 0.3) * pocket
pocket -= Pos(0, (Y0 - 1 + LUG[2] + G) / 2, -1) * Box(2 * (LUG[0] + G), LUG[2] + G - (Y0 - 1), LUG[3] + G + 1, align=(Align.CENTER, Align.CENTER, Align.MIN))
Z_COV0, Z_COV1 = W + 0.2, W + 1.0                               # крышка над ремнём (как в v11)
YS0, YS1 = 3.0, 4.6                                             # прорезь в крышке
plate = Pos(0, (Y0 + 4.5) / 2, W - 0.05) * Box(6.0, 4.5 - Y0, Z_COV1 + 0.25 - W, align=(Align.CENTER, Align.CENTER, Align.MIN))
pad = Pos(0, 0, Z_COV1 + 0.2) * Box(7.5, 10.0, 1.2, align=(Align.CENTER, Align.CENTER, Align.MIN))
cart = pocket + plate + pad
cover = Pos(0, 0, Z_COV0) * Box(2 * XC + 8, 16, Z_COV1 - Z_COV0, align=(Align.CENTER, Align.CENTER, Align.MIN)) - \
        Pos(0, (YS0 + YS1) / 2, 0) * Box(2 * XC, YS1 - YS0, 20)
rol = Part()
for x in (-XC, 0.0, XC):                                        # ролики упрощённо (по дну зубьев) + юбки
    rol += Pos(x, 0, 0) * Cylinder(R - H, W + 0.1, align=(Align.CENTER, Align.CENTER, Align.MIN))
    rol += Pos(x, 0, -0.3) * Cylinder(R + TB + 0.3, 0.3, align=(Align.CENTER, Align.CENTER, Align.MIN))
print("кармашек × ремень: %.3f мм³ (должно быть 0)" % ((cart & belt).volume if (cart & belt) else 0.0))
print("кармашек × ролики на всём ходу:", max(((Pos(s, 0, 0) * cart) & rol).volume if ((Pos(s, 0, 0) * cart) & rol) else 0 for s in (-21, -10, 0, 10, 21)))
for n, p in (("belt", belt), ("cart", cart), ("cover", cover), ("rollers", rol)):
    export_stl(p, n + ".stl", tolerance=0.01, angular_tolerance=0.1)
print("ok")
