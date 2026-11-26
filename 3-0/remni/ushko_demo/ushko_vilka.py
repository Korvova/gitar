# -*- coding: utf-8 -*-
r"""ВИЛКА (26.11, ремень 2 мм): ушко во всю высоту ремня 2 × 1.5 × 2, потолка нет — пластина тележки садится на ушко сверху
из прорези, по бокам зубцы вилки, сзади стенка под крышкой (держит от подъёма).
Показ идеи (26.11): «ушко» на спинке ремня + кармашек тележки — тележка без клея. Ремень под сопло 0.4 (remen_04), ширина 3.
Ушко — выступ 2 × 1 на спинке верхней ветви, только в нижних 2 мм ремня; кармашек тележки садится на него сверху,
потолок кармашка — в верхнем 1 мм ремня, поэтому по высоте ничего не добавляется. С внутренней стороны (зубья) ничего нет —
там проходит ведущий ролик. Запуск: ..\..\..\2-0\.venv-b123d\Scripts\python ushko_demo.py, потом blender -b -P ushko_scene.py"""
import math, os
from build123d import *
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
XC, R, TB, H, WT, W = 22.0, 2.5, 0.9, 0.7, 0.9, 2.0
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
LUG = (1.0, R + TB, R + TB + 1.5, W)                            # ушко: ±1 по x, вынос 1.5, во всю высоту ремня
belt += Pos(0, (LUG[1] + LUG[2]) / 2 - 0.01, 0) * Box(2 * LUG[0], LUG[2] - LUG[1] + 0.02, LUG[3], align=(Align.CENTER, Align.CENTER, Align.MIN))
G, WL = 0.1, 0.9
Z_COV0, Z_COV1 = W + 0.2, W + 1.0
YS0, YS1 = R + TB - 0.1, R + TB + 1.5                           # прорезь 3.3..4.9 — как в v13, прямо над ушком
Y0 = R + TB + G
YOUT = LUG[2] + G + WL                                          # задняя стенка вилки (под крышкой)
fork = Pos(0, Y0, 0.3) * Box(2 * (LUG[0] + G + WL), YOUT - Y0, Z_COV0 - 0.05 - 0.3, align=(Align.CENTER, Align.MIN, Align.MIN))
fork -= Pos(0, (LUG[1] - 1 + LUG[2] + G) / 2, -1) * Box(2 * (LUG[0] + G), LUG[2] + G - (LUG[1] - 1), W + G + 1, align=(Align.CENTER, Align.CENTER, Align.MIN))
plate = Pos(0, (YS0 + 0.1 + YS1 - 0.1) / 2, W + G) * Box(6.0, YS1 - YS0 - 0.2, Z_COV1 + 0.25 - W - G, align=(Align.CENTER, Align.CENTER, Align.MIN))
pad = Pos(0, 0, Z_COV1 + 0.2) * Box(8.5, 10.0, 1.2, align=(Align.CENTER, Align.CENTER, Align.MIN))
cart = fork + plate + pad
cover = Pos(0, 0, Z_COV0) * Box(2 * XC + 8, 16, Z_COV1 - Z_COV0, align=(Align.CENTER, Align.CENTER, Align.MIN)) -         Pos(0, (YS0 + YS1) / 2, 0) * Box(2 * XC, YS1 - YS0, 20)
rol = Part()
for x in (-XC, 0.0, XC):                                        # ролики упрощённо (по дну зубьев) + юбки
    rol += Pos(x, 0, 0) * Cylinder(R - H, W + 0.1, align=(Align.CENTER, Align.CENTER, Align.MIN))
    rol += Pos(x, 0, -0.3) * Cylinder(R + TB + 0.3, 0.3, align=(Align.CENTER, Align.CENTER, Align.MIN))
print("кармашек × ремень: %.3f мм³ (должно быть 0)" % ((cart & belt).volume if (cart & belt) else 0.0))
print("кармашек × ролики на всём ходу:", max(((Pos(s, 0, 0) * cart) & rol).volume if ((Pos(s, 0, 0) * cart) & rol) else 0 for s in (-21, -10, 0, 10, 21)))
for n, p in (("belt", belt), ("cart", cart), ("cover", cover), ("rollers", rol)):
    export_stl(p, "v_" + n + ".stl", tolerance=0.01, angular_tolerance=0.1)
iv = lambda a, b: ((a & b).volume if (a & b) else 0.0)
print("вилка × крышка %.3f, вилка поднята на 0.1 × крышка %.3f (должно быть >0 — держит)" % (iv(cart, cover), iv(Pos(0, 0, 0.1) * cart, cover)))
print("ok")
