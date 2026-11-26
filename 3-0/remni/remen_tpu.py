# -*- coding: utf-8 -*-
r"""Ремень для печати из TPU (26.11.2026, владелец): замкнутая петля с зубьями внутрь, под концевые ролики Ø5 на ±22.0 (remni4_v11).
Варианты по ширине (в модели это «высота» ремня): 2, 3, 4, 5 мм.
Зубья — как у GT2, но под печать соплом 0.4: шаг ~2.0, высота зуба 0.75, у основания 1.2, вершина скруглена; спинка 0.65; толщина ремня 1.4 (в модели v11 — 1.0).
52 зуба; длина по основанию зубьев на 0.5 % короче петли на роликах Ø5 с центрами ±22.0 (103.7) —
ремень натягивается сам за счёт TPU. Печатается кольцом плашмя (круг Ø ~34): ровно, без перегибов; на роликах сам ляжет овалом.
Запуск: ..\..\2-0\.venv-b123d\Scripts\python remen_tpu.py
"""
import math, os
from build123d import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "remen_tpu"); os.makedirs(OUT, exist_ok=True)
X_C, R_END = 22.0, 2.5                           # оси концевых роликов и их радиус в модели v11
N = 52
LOOP = 2 * (2 * X_C) + 2 * math.pi * R_END       # петля на роликах 103.7
L = LOOP * (1 - 0.005)                           # ремень короче петли на 0.5 % — натянется сам (TPU)
PITCH = L / N                                    # 1.985: на роликах растянется до 1.994 ≈ 2
R_ROOT = L / (2 * math.pi)                       # основание зубьев (делительная) 16.55
TB = 0.65                                        # спинка
H_T, W_B = 0.75, 1.2                             # зуб: высота, ширина у основания
TOOTH = [(-0.60, -0.05), (-0.60, 0.0), (-0.44, 0.40), (-0.30, 0.64), (-0.15, 0.73), (0.0, 0.75), (0.15, 0.73), (0.30, 0.64), (0.44, 0.40), (0.60, 0.0), (0.60, -0.05)]


def belt(h):
    ring = Cylinder(R_ROOT + TB, h, align=(Align.CENTER, Align.CENTER, Align.MIN)) - Cylinder(R_ROOT, h + 2, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((0, 0, -1)))
    teeth = []
    for k in range(N):
        a = 2 * math.pi * k / N
        c, s = math.cos(a), math.sin(a)                                  # нормаль наружу (c, s), касательная (−s, c)
        pts = [((R_ROOT - n) * c - t * s, (R_ROOT - n) * s + t * c) for t, n in TOOTH]
        teeth.append(extrude(make_face(Polyline(*(pts + [pts[0]]))), h))
    return ring + Part() + teeth


if __name__ == "__main__":
    import trimesh
    loop = 2 * (2 * X_C) + 2 * math.pi * R_END
    print("ремень: %d зубьев шагом %.3f, длина %.2f; петля на роликах ±%.1f — %.2f (натяг %.2f %%), кольцо Ø%.1f снаружи" % (
        N, PITCH, L, X_C, loop, 100 * (loop - L) / L, 2 * (R_ROOT + TB)))
    for h in (2, 3, 4, 5):
        p = belt(h)
        f = os.path.join(OUT, "remen_TPU_%dmm.stl" % h)
        export_stl(p, f, tolerance=0.005, angular_tolerance=0.05)
        m = trimesh.load(f)
        print("  ширина %d мм: %.1f × %.1f × %.1f, герметичен %s, объём %.0f мм³" % (h, *m.extents, m.is_watertight, m.volume))
