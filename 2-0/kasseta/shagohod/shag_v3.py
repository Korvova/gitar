# -*- coding: utf-8 -*-
# Коленвал со штырьками под корпус крупной пробы: рейки 1.8 мм с отверстиями Ø5.6, щёчки 1.2 мм, штырьки Ø5. Z = 0 — верх бобышек.
import math, os
from build123d import *
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shag_v3"); os.makedirs(OUT, exist_ok=True)
E = 3.0; P = math.sqrt(3) * E; XI = 20.0
def bx(x0, x1, y0, y1, z0, z1):
    return Pos((x0+x1)/2, (y0+y1)/2, (z0+z1)/2) * Box(x1-x0, y1-y0, z1-z0)
def cy(r, z0, z1, x=0, y=0):
    return Pos(x, y, (z0+z1)/2) * Cylinder(r, z1-z0)
def poly(pts, z0, z1):
    return Pos(0, 0, z0) * extrude(Polygon(*pts, align=None), amount=z1-z0)
def dshape(r, flat, z0, z1, x=0, y=0):
    return Pos(x, y, 0) * (cy(r, z0, z1) - bx(-r-1, r+1, flat, r+1, z0-1, z1+1))
def at(k):
    a = math.radians(120.0 * k); return E * math.sin(a), E * math.cos(a)
pts = [(-30, -9), (30, -9), (30, 9)]
for k in range(5, -6, -1):
    x = k * P; pts += [(x+1.45, 9), (x+0.5, 13), (x-0.5, 13), (x-1.45, 9)]
pts += [(-30, 9)]
rack = poly(pts, 0, 1.8) - cy(2.8, -1, 3) - cy(2.8, -1, 3, XI + 0.3, 0)
# щёка k: снизу отверстие-лыска (на вал или на штырёк предыдущей), сверху свой штырёк. Z детали: 0 — низ щеки
def crank(k):
    px, py = at(k)
    if k == 0: sx_, sy_ = 0.0, 0.0
    else: sx_, sy_ = at(k - 1)
    o = cy(6.5, 0, 1.2) - dshape(2.7, 1.7, -1, 3, sx_, sy_)
    if k < 2:
        o += cy(2.5, 1.2, 3.2, px, py) + dshape(2.5, 1.5, 3.2, 4.4, px, py)
    else:
        o += cy(2.5, 1.2, 3.3, px, py)
    for n_ in range(k + 1):
        o -= cy(0.45, 0.8, 2, 5.4 * math.sin(math.radians(150 + 22 * n_)) * 1.0, 5.4 * math.cos(math.radians(150 + 22 * n_)))
    return o
vm = cy(11, 0, 4.9) + cy(2.5, 4.9, 14) + dshape(2.5, 1.5, 14, 15.2)
vs = cy(6, 0, 2) + cy(2.5, 2, 11.1) + dshape(2.5, 1.5, 11.1, 12.3)
for n, o in (("02_reika_1.8mm_x3", rack), ("03_koleno_1_x2", crank(0)), ("03_koleno_2_x2", crank(1)), ("03_koleno_3_x2", crank(2)), ("05_val_centr_so_shlyapkoy", vm), ("06_val_bokovoi", vs)):
    export_stl(o, os.path.join(OUT, n + ".stl"), tolerance=0.02, angular_tolerance=0.2)
    print(n, o.is_valid, len(o.solids()))
