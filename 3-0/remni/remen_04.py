# -*- coding: utf-8 -*-
r"""Ремни TPU + ролики под стандартное сопло Bambu 0.4 (26.11.2026, владелец: «зубцы и шестерни — чтобы идеально под это сопло»).
Сопло 0.4 кладёт линию ~0.45 → самая тонкая стенка — 2 линии ≈ 0.9. С 8 зубьями на Ø5 зуб ролика у дна выходил ~0.27 (меньше линии),
поэтому здесь ролик на 6 зубьев (тот же Ø5), шаг ремня 2.66, ремень 39 зубьев на ту же петлю (ролики Ø5 с центрами ±22).
Ремень: зуб прямой 0.9 × 0.7 (2 линии), спинка 0.9 (2 линии), на 0.5 % короче петли — натянется сам; печать кольцом плашмя, TPU.
Ролик: 6 пазов прямоугольных 1.1 (зуб + 0.1 с боков) глубиной 0.8, без скосов (владелец: TPU-зуб сам сядет),
зуб ролика у дна ≥ 0.7, стенка от оси Ø1.8 до дна паза 0.84; юбки 0.6; PLA/PETG.
Ушки-«пилы» (владелец 26.11): на спинке два ушка по 3 мм вдоль ремня с промежутком 1.7 под зуб тележки (1.5 + 0.1 с боков);
грань к зубу вертикальная, вынос 1.5, наружу — скат до спинки; во всю ширину ремня. На краю хода наружное ушко заходит на ролик
и гнётся вместе с ремнём, толкающее остаётся на прямом (3-0/remni/ushko_demo/pila_demo.blend). Пробная тележка (PLA): площадка 8.5 × 7 × 1.2
и зуб 1.5 × 2.6 на всю ширину ремня — вставить между ушками, тянуть.
Ширина ремня 2 / 3 / 4 / 5. Запуск: ..\..\2-0\.venv-b123d\Scripts\python remen_04.py
"""
import math, os
from build123d import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "remen_04"); os.makedirs(OUT, exist_ok=True)
for _f in os.listdir(OUT):
    if _f.endswith(".stl"): os.remove(os.path.join(OUT, _f))
X_C, R_END = 22.0, 2.5
LOOP = 2 * (2 * X_C) + 2 * math.pi * R_END       # петля на роликах 103.7
N, NP = 39, 6                                    # зубьев ремня / ролика
L = LOOP * (1 - 0.005)                           # натяг 0.5 %
R_ROOT = L / (2 * math.pi)                       # внутренняя сторона спинки ремня
RP = NP * LOOP / N / (2 * math.pi)               # радиус ролика по растянутому шагу ≈ 2.54
H, WT, TB = 0.7, 0.9, 0.9                        # зуб ремня: высота, ширина; спинка
CLR = 0.10                                       # зазор паза (владелец: паз просто прямоугольный, без скосов у входа)
BORE, T_FL = 0.9, 0.6                            # ось Ø1.8, юбки


def ring_teeth(r, n, pts, height, z0=0.0):
    out = []
    for k in range(n):
        a = 2 * math.pi * k / n
        c, s = math.cos(a), math.sin(a)
        q = [((r - nn) * c - t * s, (r - nn) * s + t * c) for t, nn in pts]
        out.append(Pos(0, 0, z0) * extrude(make_face(Polyline(*(q + [q[0]]))), height))
    return out


T_W, G_T = 1.5, 0.10                             # зуб тележки вдоль хода, зазор
LL, HP = 3.0, 1.5                                # ушко: длина вдоль ремня, вынос у толкающей грани


def lugs(w):
    rb = R_ROOT + TB                             # спинка снаружи
    out = Part()
    for sd in (-1, 1):
        g0 = T_W / 2 + G_T
        pts = [(g0, -0.1), (g0, HP), (g0 + LL, 0.05), (g0 + LL, -0.1)]
        q = []
        for t, n in pts:
            a = math.pi / 2 + sd * t / rb        # ушки на «12 часов» кольца
            q.append(((rb + n) * math.cos(a), (rb + n) * math.sin(a)))
        if sd < 0: q = q[::-1]
        out += extrude(make_face(Polyline(*(q + [q[0]]))), w)
    return out


def cart(w):
    """пробная тележка: площадка 8.5 × 7 × 1.2 (печать площадкой на стол), зуб 1.5 × 2.6 высотой w"""
    plate = Box(8.5, 7.0, 1.2, align=(Align.CENTER, Align.MIN, Align.MIN))
    tooth = Pos(0, 7.0 - 2.6, 1.2) * Box(T_W, 2.6, w, align=(Align.CENTER, Align.MIN, Align.MIN))
    return plate + tooth


def belt(w, ushki=True):
    u, c = WT / 2, 0.1
    tooth = [(-u, -0.05), (-u, H - c), (-u + c, H), (u - c, H), (u, H - c), (u, -0.05)]
    ring = Cylinder(R_ROOT + TB, w, align=(Align.CENTER, Align.CENTER, Align.MIN)) - Pos(0, 0, -1) * Cylinder(R_ROOT, w + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    b = ring + Part() + ring_teeth(R_ROOT, N, tooth, w)
    return b + lugs(w) if ushki else b


def pulley(w):
    hub = w + 0.4
    p = Cylinder(RP, hub, align=(Align.CENTER, Align.CENTER, Align.MIN))
    g, d = WT / 2 + CLR, H + CLR                                                   # полуширина паза, глубина
    groove = [(-g, -0.3), (-g, d), (g, d), (g, -0.3)]                              # паз прямоугольный, открыт наружу
    p -= Part() + ring_teeth(RP, NP, groove, hub + 2, -1)
    rf = RP + TB + 0.3
    p += Pos(0, 0, -T_FL) * Cylinder(rf, T_FL, align=(Align.CENTER, Align.CENTER, Align.MIN))
    p += Pos(0, 0, hub) * Cylinder(rf, T_FL, align=(Align.CENTER, Align.CENTER, Align.MIN))
    p -= Cylinder(BORE, 100)
    return Pos(0, 0, T_FL) * p


if __name__ == "__main__":
    import trimesh
    r_dno = RP - H - CLR
    zub_dno = 2 * math.pi * r_dno / NP - 2 * (WT / 2 + CLR)
    print("ремень: %d зубьев, шаг %.3f (на роликах %.3f), длина %.2f, Ø%.1f; ролик %d зубьев, Ø%.2f; зуб ролика у дна %.2f, стенка от оси %.2f" % (
        N, L / N, LOOP / N, L, 2 * (R_ROOT + TB), NP, 2 * RP, zub_dno, r_dno - BORE))
    for w in (2, 3, 4, 5):
        for kind, part in (("remen04", belt(w)), ("remen04_bez_ushek", belt(w, False)), ("rolik04", pulley(w)), ("telezhka04", cart(w))):
            f = os.path.join(OUT, "%s_%dmm.stl" % (kind, w))
            export_stl(part, f, tolerance=0.004, angular_tolerance=0.05)
            m = trimesh.load(f)
            print("  %-16s %5.1f × %5.1f × %4.1f герм %s" % (os.path.basename(f)[:-4], *m.extents, m.is_watertight))
