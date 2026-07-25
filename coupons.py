# -*- coding: utf-8 -*-
"""
Калибровочные купоны для посадок барабана v9.4:
- 4 шайбы со шлицевой звёздочкой (10 пазов) с разным зазором — примерять на
  шестерню мотора. Метки-точки на верхней грани: 1..4 = от тугого к свободному.
- 3 кольца под выступ мотора (Ø16.6 / 16.8 / 17.0) — метки-точки 1..3.
Запуск: .venv-b123d\\Scripts\\python coupons.py
"""
from build123d import *
import math

OUT = r"C:\App\gitar\2-0\Print\Print"

# t — радиальный зазор относительно номинала шестерни (впадины Ø6.1 при t=0.05)
SPLINE_T = [0.0, 0.05, 0.125, 0.2]      # метки: 1 (туго) .. 4 (свободно)
PILOT_D = [16.6, 16.8, 17.0]            # метки: 1 .. 3

def spline_cut(t, h):
    cut = Pos(0, 0, h / 2) * Cylinder(2.4 + t, h)
    for k in range(10):
        a = k * 36
        r = math.radians(a)
        cut += Pos(2.4 * math.cos(r), 2.4 * math.sin(r), h / 2) * \
               Rot(0, 0, a) * Box(1.3, 0.85 + 2 * t, h)
    return cut

def dots(n, rad):
    d = None
    for i in range(n):
        a = math.radians(i * 360 / max(n, 1))
        s = Pos(rad * math.cos(a), rad * math.sin(a), 3.7) * Cylinder(0.6, 0.8)
        d = s if d is None else d + s
    return d

parts = []
for i, t in enumerate(SPLINE_T):
    p = Pos(0, 0, 2) * Cylinder(5.5, 4)
    p -= spline_cut(t, 4.2)
    p -= dots(i + 1, 4.3)
    parts.append((f"coupon_spline_{i+1}", p))

for i, dia in enumerate(PILOT_D):
    p = Pos(0, 0, 1.5) * Cylinder(10.5, 3)
    p -= Pos(0, 0, 1.5) * Cylinder(dia / 2, 3.2)
    p -= dots(i + 1, (dia / 2 + 10.5) / 2)
    parts.append((f"coupon_pilot_{i+1}", p))

for name, part in parts:
    p = part if isinstance(part, Part) else Part() + part
    export_stl(p, rf"{OUT}\{name}.stl")
    print(f"{name}: volume={p.volume:.0f} mm3, solids={len(p.solids())}")
print("done")
