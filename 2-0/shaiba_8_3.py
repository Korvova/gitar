# -*- coding: utf-8 -*-
"""Цилиндр по заказу владельца (10.10): радиус 8.3 (Ø16.6), высота 3, в центре сверху глухая дырка Ø5 глубиной 1.2.
Печать дыркой вверх — без поддержек. Запуск: .venv-b123d\Scripts\python shaiba_8_3.py"""
import os
from build123d import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Print", "Print")
c = Pos(0, 0, 1.5) * Cylinder(8.3, 3.0)
c -= Pos(0, 0, 3.0 - 0.6 + 0.005) * Cylinder(2.5, 1.21)
c = Part() + c
bb = c.bounding_box()
print("cilindr_r8_3: %.1f x %.1f x %.1f" % (bb.size.X, bb.size.Y, bb.size.Z))
export_stl(c, os.path.join(OUT, "cilindr_r8_3.stl"))
