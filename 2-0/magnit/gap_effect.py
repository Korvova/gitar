# -*- coding: utf-8 -*-
r"""Как щель между рядами магнитов влияет на силу (20×10×5 стоя, 3 полюса, катушки 8 × 6.5, провод в 3 мм).
Запуск: .venv-b123d\Scripts\python magnit\gap_effect.py"""
import numpy as np
import magpylib as magpy
RHO, FF, TC, H = 1.72e-8, 0.5, 3.0, 16.0
WIRE, WIRE_OD, BR = 0.30, 0.34, 1.35


def km(G, tc_wire):
    c = magpy.Collection()
    for side in (-1, 1):
        for p in range(3):
            c.add(magpy.magnet.Cuboid(polarization=(0, (1 if p % 2 == 0 else -1) * BR, 0), dimension=(10e-3, 5e-3, 20e-3),
                                      position=((p - 1) * 10e-3, side * (G / 2 + 2.5) * 1e-3, 0)))
    cw = 6.5; leg = (cw - 1.6) / 2
    n = int(FF * leg * tc_wire * 1e-6 / (np.pi * (WIRE_OD / 2) ** 2 * 1e-6))
    r = RHO * n * 2 * ((cw - leg) + (H + leg)) * 1e-3 / (np.pi * (WIRE / 2) ** 2 * 1e-6)
    out = []
    for X in np.linspace(-22, 22, 12):
        def B(x0, x1):
            P = np.stack(np.meshgrid(np.linspace(x0, x1, 5), np.linspace(-tc_wire / 2, tc_wire / 2, 3), np.linspace(-H / 2, H / 2, 7),
                                     indexing="ij"), -1).reshape(-1, 3) * 1e-3
            return c.getB(P)[:, 1].mean()
        xs = [(k - 3.5) * cw - X for k in range(8)]
        k = np.array([n * H * 1e-3 * (B(x - cw / 2, x - cw / 2 + leg) - B(x + cw / 2 - leg, x + cw / 2)) for x in xs])
        out.append(np.sqrt((k ** 2).sum() / r))
    return min(out), n


base, _ = km(4.0, 3.0)
for tag, G, tw in (("сейчас: провод 3, по 0.5 воздуха", 4.0, 3.0),
                   ("каркас 0.5 + провод 2, по 0.5 воздуха", 4.0, 2.0),
                   ("каркас 0.5 + провод 3, по 0.5 воздуха", 5.0, 3.0),
                   ("каркас 0.5 + провод 3, по 1 мм воздуха", 6.0, 3.0),
                   ("без каркаса, провод 3, по 1 мм воздуха", 5.0, 3.0)):
    K, n = km(G, tw)
    print(f"{tag}: щель {G:.0f} мм, витков {n}, сила на ватт {K / base * 100:.0f}% -> 300 г: {(0.3 * 9.81 / K) ** 2:.0f} Вт")
