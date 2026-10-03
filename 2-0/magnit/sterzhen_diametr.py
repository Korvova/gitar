import numpy as np, magpylib as magpy
RHO, FF, WIRE, OD, BR = 1.72e-8, 0.5, 0.30, 0.34, 1.43
def km(D, L, wind):
    c = magpy.Collection()
    for i in range(-4, 4):
        c.add(magpy.magnet.Cylinder(polarization=(0, 0, BR if i % 2 == 0 else -BR), dimension=(D * 1e-3, L * 1e-3), position=(0, 0, (i + 0.5) * L * 1e-3)))
    r0 = D / 2 + 0.75; r1 = r0 + wind; w = L / 2
    n = int(FF * w * wind / (np.pi * (OD / 2) ** 2))
    res = RHO * n * 2 * np.pi * (r0 + r1) / 2 * 1e-3 / (np.pi * (WIRE / 2) ** 2 * 1e-6)
    out = []
    for X in np.linspace(-L / 2, L / 2, 7):
        ks = []
        for j in range(4):
            z = X + (j - 1.5) * w
            rr = np.linspace(r0, r1, 5); zz = np.linspace(z - w / 2, z + w / 2, 5)
            P = np.array([[r * 1e-3, 0, q * 1e-3] for r in rr for q in zz])
            ks.append(n * 2 * np.pi * rr.mean() * 1e-3 * c.getB(P)[:, 0].mean())
        out.append(np.sqrt((np.array(ks) ** 2).sum() / res))
    return min(out), 2 * r1
print("N52, полюс = длина магнита, катушка-бегунок 4 секции, намотка 4 мм")
for D, L in ((10, 10), (12, 10), (12, 12), (15, 12), (20, 15)):
    k, odc = km(D, L, 4.0)
    print(f"  магнит Ø{D}×{L}: катушка снаружи Ø{odc:.0f} мм — 500 г: {(4.9 / k) ** 2:.1f} Вт, 1 кг: {(9.81 / k) ** 2:.1f} Вт")
print("диски 15×5: полюс из 2 (10 мм) или 3 (15 мм) дисков")
for D, L in ((15, 10), (15, 15)):
    k, odc = km(D, L, 4.0)
    print(f"  Ø{D}, полюс {L}: катушка Ø{odc:.0f} — 500 г: {(4.9 / k) ** 2:.1f} Вт, 1 кг: {(9.81 / k) ** 2:.1f} Вт")
