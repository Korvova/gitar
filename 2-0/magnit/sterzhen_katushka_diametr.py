# Магнитный стержень (диски Ø12, по 10 мм, N-S-N-S впритык) и бегущая катушка-муфта из 2 секций (2 фазы).
import numpy as np, magpylib as magpy
RHO, FF, WIRE, OD, BR = 1.72e-8, 0.5, 0.30, 0.34, 1.35
def rod():
    c = magpy.Collection()
    for i in range(-3, 3):
        c.add(magpy.magnet.Cylinder(polarization=(0, 0, BR if i % 2 == 0 else -BR), dimension=(12e-3, 10e-3), position=(0, 0, (i + 0.5) * 10e-3)))
    return c
R = rod()
def coil(r0, r1, w=5.0):
    n = int(FF * w * (r1 - r0) / (np.pi * (OD / 2) ** 2))
    res = RHO * n * 2 * np.pi * (r0 + r1) / 2 * 1e-3 / (np.pi * (WIRE / 2) ** 2 * 1e-6)
    return n, res
def k_at(z, r0, r1, w, n):
    rr = np.linspace(r0, r1, 5); zz = np.linspace(z - w / 2, z + w / 2, 5)
    P = np.array([[r * 1e-3, 0, q * 1e-3] for r in rr for q in zz])
    return n * 2 * np.pi * rr.mean() * 1e-3 * R.getB(P)[:, 0].mean()
print("бегунок: 4 секции по 5 мм (A B A' B' — шаг 5 = четверть периода 20), зазор до стержня 0.75")
for r1 in (8.5, 10.0, 11.5, 13.0, 15.0, 18.0):
    r0 = 6.75
    n, res = coil(r0, r1)
    km = []
    for X in np.linspace(-5, 5, 11):
        k = np.array([k_at(X + (j - 1.5) * 5.0, r0, r1, 5.0, n) for j in range(4)])
        km.append(np.sqrt((k ** 2).sum() / res))
    km = min(km)
    print(f"  наружный диаметр катушки {2 * r1:4.0f} мм (намотка {r1 - r0:.1f} мм): {n} витков/секция, 3 Н ≈ {(3 / km) ** 2:.1f} Вт, вес меди ~{8.96 * 4 * 5 * np.pi * (r1**2 - r0**2) * FF / 1000:.0f} г")
