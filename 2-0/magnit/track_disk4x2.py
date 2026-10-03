# -*- coding: utf-8 -*-
r"""Идея владельца 03.10: неподвижная дорожка столбиков из дисков 4 × 2 (ось вверх, N-S-N-S),
сверху едет тележка с катушками (одна толкает, другая тянет — две фазы, как шаговик).
Катушки плоские, лежат над торцами столбиков с зазором 0.3; ток в ветвях — поперёк дорожки,
поле — вверх, сила — вдоль дорожки. Без железа. Сила на 1 А по положению тележки.
Запуск: .venv-b123d\Scripts\python magnit\track_disk4x2.py"""
import numpy as np
import magpylib as magpy

BR, D, TAU = 1.2, 4.0, 5.0
WIRE, WIRE_OD, FF, RHO = 0.30, 0.34, 0.5, 1.72e-8
GAP = 0.3


def track(hm, rows):
    """Дорожка вдоль x на 52 мм: столбики Ø4 высотой hm, rows рядов поперёк (y)."""
    c = magpy.Collection()
    n = int(52 // TAU)
    for i in range(n):
        s = 1 if i % 2 == 0 else -1
        for r in range(rows):
            c.add(magpy.magnet.Cylinder(polarization=(0, 0, s * BR), dimension=(D * 1e-3, hm * 1e-3),
                                        position=((i - (n - 1) / 2) * TAU * 1e-3, (r - (rows - 1) / 2) * D * 1e-3, -hm / 2 * 1e-3)))
    return c, n * rows


def force(hm, rows, tc):
    col, ndisk = track(hm, rows)
    cw, leg = 1.5 * TAU, 0.5 * TAU
    la = rows * D                                             # активная длина ветви поперёк дорожки
    n = int(FF * leg * tc * 1e-6 / (np.pi * (WIRE_OD / 2) ** 2 * 1e-6))
    l_turn = 2 * ((cw - leg) + la + leg) * 1e-3
    r = RHO * n * l_turn / (np.pi * (WIRE / 2) ** 2 * 1e-6)
    offs, el = [-cw, 0.0, cw], [0, 270, 180]                  # тележка: 3 катушки A+, B−, A−
    zs = np.linspace(GAP, GAP + tc, 4)

    def legB(x0, x1):
        xs = np.linspace(x0, x1, 5); ys = np.linspace(-la / 2, la / 2, 5)
        P = np.stack(np.meshgrid(xs, ys, zs, indexing="ij"), -1).reshape(-1, 3) * 1e-3
        return col.getB(P)[:, 2].mean()
    F = []
    for X in np.linspace(-15, 15, 13):                        # тележка в средней части дорожки
        kA = kB = 0.0
        for o, e in zip(offs, el):
            xc = X + o
            k = n * la * 1e-3 * (legB(xc - cw / 2, xc - cw / 2 + leg) - legB(xc + cw / 2 - leg, xc + cw / 2))
            if e == 0: kA += k
            elif e == 180: kA -= k
            else: kB -= k
        F.append(np.hypot(kA, kB))
    return np.array(F), ndisk, n, r


for hm, rows, tc, tag in ((8.0, 1, 3.0, "столбики по 4 диска, 1 ряд"),
                          (16.0, 1, 3.0, "столбики по 8 дисков, 1 ряд"),
                          (4.0, 2, 3.0, "столбики по 2 диска, 2 ряда рядом"),
                          (8.0, 2, 3.0, "столбики по 4 диска, 2 ряда рядом")):
    F, nd, n, r = force(hm, rows, tc)
    print(f"{tag}: дисков на дорожку {nd * int(hm / 2)}; катушка {n} витков {r:.2f} Ом; "
          f"сила при 1 А: средняя {F.mean() * 102:.0f} г, мин {F.min() * 102:.0f} г; при 1.5 А средняя {F.mean() * 153:.0f} г")
