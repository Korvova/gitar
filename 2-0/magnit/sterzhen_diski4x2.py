# Стержень из дисков Ø4×2 (N35): группы по G дисков, группы N-S-N-S; бегунок из 4 секций (2 фазы).
import numpy as np, magpylib as magpy
RHO, FF, WIRE, OD, BR = 1.72e-8, 0.5, 0.30, 0.34, 1.2
def run(G, r1, r0=2.6):
    L = 2.0 * G                                   # длина группы (полюса)
    c = magpy.Collection()
    for i in range(-6, 6):
        c.add(magpy.magnet.Cylinder(polarization=(0, 0, BR if i % 2 == 0 else -BR), dimension=(4e-3, L * 1e-3), position=(0, 0, (i + 0.5) * L * 1e-3)))
    w = L / 2                                     # секция = четверть периода (2L)
    n = int(FF * w * (r1 - r0) / (np.pi * (OD / 2) ** 2))
    res = RHO * n * 2 * np.pi * (r0 + r1) / 2 * 1e-3 / (np.pi * (WIRE / 2) ** 2 * 1e-6)
    km = []
    for X in np.linspace(-L / 2, L / 2, 9):
        ks = []
        for j in range(4):
            z = X + (j - 1.5) * w
            rr = np.linspace(r0, r1, 5); zz = np.linspace(z - w / 2, z + w / 2, 5)
            P = np.array([[r * 1e-3, 0, q * 1e-3] for r in rr for q in zz])
            ks.append(n * 2 * np.pi * rr.mean() * 1e-3 * c.getB(P)[:, 0].mean())
        km.append(np.sqrt((np.array(ks) ** 2).sum() / res))
    km = min(km)
    return n, res, km
for G in (2, 3, 4):
    for r1 in (5.0, 7.0):
        n, res, km = run(G, r1)
        f1 = km * np.sqrt(1.0) * 102; f3 = km * np.sqrt(3.0) * 102
        print(f"группы по {G} диска (полюс {2*G} мм), катушка до Ø{2*r1:.0f}: секция {n} витков {res:.2f} Ом; при 1 Вт ≈ {f1:.0f} г, при 3 Вт ≈ {f3:.0f} г")
