# -*- coding: utf-8 -*-
"""Шатун стенда-сектора (как mini2s_shatun, ц-ц 95.08) с дырками поменьше — против люфта (владелец 10.10).
Было 5.5 на пальцы Ø5 (5.1/5.2 на стенде 82 печатались туго) — делаем 5.3 и 5.2: какой сядет без люфта, но вращается."""
import os
from build123d import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Print", "Print")
LC = 95.08
for d in (5.3, 5.2):
    link = Pos(0, 0, 0.8) * Cylinder(4.4, 1.6) + Pos(0, LC, 0.8) * Cylinder(4.4, 1.6)
    link += Pos(0, LC / 2, 0.8) * Box(5.6, LC, 1.6)
    for y in (0, LC):
        link -= Pos(0, y, 0.8) * Cylinder(d / 2, 1.8)
    n = "mini2s_shatun_d%d" % round(d * 10)
    export_stl(Part() + link, os.path.join(OUT, n + ".stl"))
    print(n)
