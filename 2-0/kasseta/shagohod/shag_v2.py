# -*- coding: utf-8 -*-
# Шагоход, крупная проба: E=3, вал Ø5, диски Ø14, рейки 3 мм. Два одинаковых вала с дисками на лыске. Z = 0 — верх бобышек.
import math, os
from build123d import *
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shag_v2"); os.makedirs(OUT, exist_ok=True)
E = 3.0; P = math.sqrt(3) * E; XI = 20.0
def bx(x0, x1, y0, y1, z0, z1):
    return Pos((x0+x1)/2, (y0+y1)/2, (z0+z1)/2) * Box(x1-x0, y1-y0, z1-z0)
def cy(r, z0, z1, x=0, y=0):
    return Pos(x, y, (z0+z1)/2) * Cylinder(r, z1-z0)
def poly(pts, z0, z1):
    return Pos(0, 0, z0) * extrude(Polygon(*pts, align=None), amount=z1-z0)
def dshape(r, flat, z0, z1, x=0, y=0):
    return Pos(x, y, 0) * (cy(r, z0, z1) - bx(-r-1, r+1, flat, r+1, z0-1, z1+1))
base = bx(-34, 34, -21.4, 21.4, -9, -6) + cy(8, -6, 0) + cy(8, -6, 0, XI, 0)
for s in (-1, 1):
    a, b = sorted((s*18.4, s*20.4)); base += bx(-34, 34, a, b, -6, 10.05)
base -= cy(2.7, -10, 1) + cy(2.7, -10, 1, XI, 0)
for sx in (-1, 1):
    x_ = sx * 24.4
    base -= poly([(x_-1.1, -20.6), (x_+1.1, -20.6), (x_+1.1, -20.4), (x_+1.5, -19.4), (x_-1.5, -19.4), (x_-1.1, -20.4)], -8, 12)
    base -= bx(x_-1.1, x_+1.1, -21.6, -20.3, -8, -6)
pts = [(-30, -9), (30, -9), (30, 9)]
for k in range(5, -6, -1):
    x = k * P; pts += [(x+1.45, 9), (x+0.95, 13), (x-0.95, 13), (x-1.45, 9)]
pts += [(-30, 9)]
rack = poly(pts, 0, 3.0) - cy(7.3, -1, 4) - cy(7.3, -1, 4, XI, 0)
def disc(k):
    a = math.radians(120.0 * (k - 1)); sx, cx = math.sin(a), math.cos(a)
    o = cy(7.0, 0, 3.3) - dshape(2.75, 1.75, -1, 5, -E * sx, -E * cx)
    for n_ in range(k):
        t = (n_ - (k - 1) / 2) * 1.6
        o -= cy(0.55, 2.8, 4, 4.9 * sx + t * cx, 4.9 * cx - t * sx)
    return o
# валы одной деталью со шляпкой/буртиком, печатать стоя, шляпкой на стол; Z в сборке: низ -14 и -11.1
vm = cy(11, 0, 4.9) + cy(2.5, 4.9, 14) + dshape(2.5, 1.5, 14, 23.9)
vs = cy(6, 0, 2) + cy(2.5, 2, 11.1) + dshape(2.5, 1.5, 11.1, 21)
cart = bx(-15, 15, -21.15, 21.15, 10.1, 12.1) + bx(-15, 15, 16.6, 18, 0.3, 10.1)
for k in range(-3, 3):
    x = (k + 0.5) * P; cart += bx(x-1, x+1, 13.8, 16.65, 0.3, 10.1)
for s in (-1, 1):
    a, b = sorted((s*20.55, s*21.15)); cart += bx(-15, 15, a, b, 8, 12.1)
cart += bx(-1, 1, -22.3, -21.1, 8.5, 12.1)
cart = Rot(180, 0, 0) * cart
stop = poly([(-1, -21.55), (1, -21.55), (1, -20.4), (1.35, -19.55), (-1.35, -19.55), (-1, -20.4)], -7.9, 7) + bx(-1.2, 1.2, -22.6, -21.5, -7.9, 12.1)
stop = Rot(0, 90, 0) * stop
for n, o in (("01_osnovanie", base), ("02_reika_x3", rack), ("03_disk_1_x2", disc(1)), ("03_disk_2_x2", disc(2)), ("03_disk_3_x2", disc(3)), ("05_val_centr_so_shlyapkoy", vm), ("06_val_bokovoi", vs), ("07_telezhka", cart), ("08_stopor_x2", stop)):
    export_stl(o, os.path.join(OUT, n + ".stl"), tolerance=0.02, angular_tolerance=0.2)
    print(n, o.is_valid, len(o.solids()))
