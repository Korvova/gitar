# -*- coding: utf-8 -*-
r"""Ремни TPU + ролики-шестерёнки к ним для подбора лучшей пары (26.11.2026, владелец).
Ремень: замкнутая петля с зубьями внутрь, под ролики Ø5 с центрами ±22.0 (remni4_v11); 52 зуба, длина на 0.5 % короче петли
на роликах — натягивается сам. Печать кольцом плашмя (Ø ~34). Ширина ремня (в модели «высота»): 2, 3, 4, 5 мм.
Два профиля зуба:
  A «обычный» — как GT2 под сопло 0.4: зуб 0.75, у основания 1.2, спинка 0.65 (толщина 1.4);
  B «глубокий» — для лучшего зацепа: зуб 1.0, у основания 1.35, спинка 0.9 (толщина 1.9).
К каждому ремню — свой ролик: 8 пазов по профилю зуба (+0.1 зазор), делительный радиус 2.54 (Ø5 как в модели),
юбки 0.6 с обеих сторон, между юбками ширина ремня + 0.4, ось Ø1.8. Ролики печатать PLA/PETG, лучше соплом 0.2–0.25.
Запуск: ..\..\2-0\.venv-b123d\Scripts\python remen_tpu.py
"""
import math, os
from build123d import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "remen_tpu"); os.makedirs(OUT, exist_ok=True)
for _f in os.listdir(OUT):
    if _f.endswith(".stl"): os.remove(os.path.join(OUT, _f))
X_C, R_END = 22.0, 2.5                           # оси концевых роликов и их радиус в модели v11
N = 52
LOOP = 2 * (2 * X_C) + 2 * math.pi * R_END       # петля на роликах 103.7
L = LOOP * (1 - 0.005)                           # ремень короче петли на 0.5 % — натянется сам (TPU)
PITCH = L / N                                    # 1.985: на роликах растянется до 1.994 ≈ 2
R_ROOT = L / (2 * math.pi)                       # основание зубьев ремня (делительная) 16.4
NP = 8                                           # зубьев ролика
RP = NP * LOOP / N / (2 * math.pi)               # делительный радиус ролика по растянутому шагу ≈ 2.54
CLR = 0.10                                       # зазор паза ролика
BORE = 0.9                                       # ось Ø1.8
T_FL = 0.6                                       # юбки


def tooth_pts(h, wb):
    """профиль зуба (t вдоль, n внутрь): основание wb, высота h, вершина скруглена"""
    w = wb / 2
    return [(-w, -0.05), (-w, 0.0), (-0.73 * w, 0.53 * h), (-0.5 * w, 0.85 * h), (-0.25 * w, 0.97 * h), (0.0, h),
            (0.25 * w, 0.97 * h), (0.5 * w, 0.85 * h), (0.73 * w, 0.53 * h), (w, 0.0), (w, -0.05)]


PROF = {"A_obychnyj": dict(h=0.75, wb=1.2, tb=0.65), "B_glubokij": dict(h=1.0, wb=1.35, tb=0.9)}


def ring_teeth(r, n, pts, height, z0=0.0):
    out = []
    for k in range(n):
        a = 2 * math.pi * k / n
        c, s = math.cos(a), math.sin(a)
        q = [((r - nn) * c - t * s, (r - nn) * s + t * c) for t, nn in pts]
        out.append(Pos(0, 0, z0) * extrude(make_face(Polyline(*(q + [q[0]]))), height))
    return out


def belt(pr, w):
    ring = Cylinder(R_ROOT + pr["tb"], w, align=(Align.CENTER, Align.CENTER, Align.MIN)) - Pos(0, 0, -1) * Cylinder(R_ROOT, w + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return ring + Part() + ring_teeth(R_ROOT, N, tooth_pts(pr["h"], pr["wb"]), w)


def pulley(pr, w):
    hub = w + 0.4
    p = Cylinder(RP, hub, align=(Align.CENTER, Align.CENTER, Align.MIN))
    k = 1 + 2 * CLR / pr["wb"]
    gp = [(t * k, (nn * (pr["h"] + CLR) / pr["h"]) if nn > 0 else nn - 0.3) for t, nn in tooth_pts(pr["h"], pr["wb"])]   # паз открыт наружу
    p -= Part() + ring_teeth(RP, NP, gp, hub + 2, -1)
    rf = RP + pr["tb"] + 0.3
    p += Pos(0, 0, -T_FL) * Cylinder(rf, T_FL, align=(Align.CENTER, Align.CENTER, Align.MIN))
    p += Pos(0, 0, hub) * Cylinder(rf, T_FL, align=(Align.CENTER, Align.CENTER, Align.MIN))
    p -= Cylinder(BORE, 100)
    return Pos(0, 0, T_FL) * p


if __name__ == "__main__":
    import trimesh
    print("ремень: %d зубьев шагом %.3f, длина %.2f; петля на роликах ±%.1f — %.2f (натяг %.2f %%); ролик %d зубьев, делительный Ø%.2f" % (
        N, PITCH, L, X_C, LOOP, 100 * (LOOP - L) / L, NP, 2 * RP))
    for name, pr in PROF.items():
        for w in (2, 3, 4, 5):
            for kind, part in (("remen", belt(pr, w)), ("rolik", pulley(pr, w))):
                f = os.path.join(OUT, "%s_%s_%dmm.stl" % (kind, name, w))
                export_stl(part, f, tolerance=0.004, angular_tolerance=0.05)
                m = trimesh.load(f)
                print("  %-28s %5.1f × %5.1f × %4.1f герм %s" % (os.path.basename(f)[:-4], *m.extents, m.is_watertight))
        print("  %s: стенка ролика от оси до дна паза %.2f мм" % (name, RP - pr["h"] - CLR - BORE))
