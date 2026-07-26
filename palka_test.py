# -*- coding: utf-8 -*-
"""ТЕСТ-НАБОР механизма «палка» (одна станция, поиграться руками).
Запуск: .venv-b123d\\Scripts\\python palka_test.py
Плита-стенд 250x70: канал тележки (поперёк), стойка оси, губки-направляющие
спицы, отверстие оси кривошипа. Детали: треугольник (плечо 65/21.2),
спица 85, шатун 45, серьга (межцентр 4), кривошип со звёздочкой на шестерню
NEMA14 + 3 отверстия пальца (r6/6.5/7), тележка-ползун.
Все шарниры — штифты из филамента 1.75 (отверстия Ø1.9).
"""
from build123d import *
import math as _m

OUT = r"C:\App\gitar\2-0\Print\Print"
PIN = 0.95                                     # отверстия под штифт 1.75


def BB(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(
        abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))


def spline_cut(h, t=0.0):
    cut = Pos(0, 0, h / 2) * Cylinder(2.45 + t, h + 0.2)
    for k in range(10):
        a = k * 36
        r = _m.radians(a)
        cut += Pos((2.4 + t) * _m.cos(r), (2.4 + t) * _m.sin(r), h / 2) * \
               Rot(0, 0, a) * Box(1.3, 0.95 + 2 * t, h + 0.2)
    return cut


# ---------------- плита-стенд ----------------
plate = BB(0, 250, -35, 35, 0, 3)
plate += BB(16, 20, -35, 35, 3, 9)             # рельсы канала тележки
plate += BB(40, 44, -35, 35, 3, 9)
plate += Pos(95, -2, 4) * Cylinder(4, 2)       # прилив оси треугольника
plate -= Pos(95, -2, 2.5) * Cylinder(PIN, 5.5)  # ось (штифт снизу)
for gx in (130, 172):                          # губки-направляющие спицы
    plate += BB(gx - 4, gx + 4, -26, -24.2, 3, 8)
    plate += BB(gx - 4, gx + 4, -19.8, -18, 3, 8)
plate -= Pos(230, -22, 1.5) * Cylinder(PIN, 3.2)   # ось кривошипа

# ---------------- треугольник (локально: ось в 0,0) ----------------
tri = Pos(0, 0, 0.8) * Cylinder(11, 1.6)       # основание-диск
tri += BB(-66.6, 0, -2, 2, 0, 1.6)             # плечо 65 к серьге
tri += BB(-2, 2, -22.8, 0, 0, 1.6)             # плечо 21.2 к спице
tri -= Pos(0, 0, 0.8) * Cylinder(PIN, 1.8)     # ось
tri -= Pos(-65, 0, 0.8) * Cylinder(PIN, 1.8)   # tip (серьга)
tri -= Pos(0, -21.2, 0.8) * Cylinder(PIN, 1.8)  # угол-1 (спица)

# ---------------- спица, шатун, серьга ----------------
spica = BB(0, 97, -2, 2, 0, 1.6)
spica -= Pos(4, 0, 0.8) * Cylinder(PIN, 1.8)
spica -= Pos(93.5, 0, 0.8) * Cylinder(PIN, 1.8)   # ц-ц 89.5 = до шатуна/кривошипа

shatun = BB(0, 45, -2, 2, 0, 1.6)
shatun -= Pos(3, 0, 0.8) * Cylinder(PIN, 1.8)
shatun -= Pos(42, 0, 0.8) * Cylinder(PIN, 1.8)

serga = BB(0, 10, -2.2, 2.2, 0, 1.6)
serga -= Pos(3, 0, 0.8) * Cylinder(PIN, 1.8)
serga -= Pos(7, 0, 0.8) * Cylinder(PIN, 1.8)

# ---------------- кривошип: звёздочка на шестерню + 3 радиуса пальца ----
crank = Pos(0, 0, 1.25) * Cylinder(11, 2.5)
crank -= spline_cut(2.5, 0)                    # свободная посадка на шестерню
for r in (6.0, 6.5, 7.0):
    crank -= Pos(r, 0, 1.25) * Cylinder(PIN, 2.7)

# ---------------- тележка-ползун ----------------
cart = BB(-9.5, 9.5, -12, 12, 0, 8)
cart -= Pos(0, 0, 2.5) * Cylinder(PIN, 5.2)    # гнездо пальца серьги (снизу)

parts = [("ptest_plate_v1", plate), ("ptest_triangle_v1", tri),
         ("ptest_spica_v1", spica), ("ptest_shatun_v1", shatun),
         ("ptest_serga_v1", serga), ("ptest_crank_v1", crank),
         ("ptest_cart_v1", cart)]
for name, part in parts:
    p = part if isinstance(part, Part) else Part() + part
    export_stl(p, rf"{OUT}\{name}.stl")
    print(f"{name}: volume={p.volume:.0f} mm3, solids={len(p.solids())}")
print("export done")
