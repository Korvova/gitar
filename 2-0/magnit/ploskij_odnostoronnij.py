# Плоский односторонний мотор: каретка — 2 магнита 20×10×5 (N вниз, S вниз, 10 вдоль хода), сверху сталь;
# на дне паза плоские катушки (ось вертикально), ветви поперёк хода длиной ~20 (вдоль грифа). Сталь — методом отражений.
import numpy as np, magpylib as magpy
RHO, FF, WIRE, OD, BR = 1.72e-8, 0.5, 0.30, 0.34, 1.35
MX, MY, MT = 10.0, 20.0, 5.0
def cart(X, gap, top_steel, bot_steel, TC):
    c = magpy.Collection()
    zb = gap                              # низ магнитов над верхом катушек (катушки z −TC..0)
    for p, s in ((-1, 1), (1, -1)):
        x = X + p * MX / 2
        c.add(magpy.magnet.Cuboid(polarization=(0, 0, -s * BR), dimension=(MX * 1e-3, MY * 1e-3, MT * 1e-3), position=(x * 1e-3, 0, (zb + MT / 2) * 1e-3)))
        if top_steel:                     # сталь на верхней грани: отражение выше
            c.add(magpy.magnet.Cuboid(polarization=(0, 0, -s * BR), dimension=(MX * 1e-3, MY * 1e-3, MT * 1e-3), position=(x * 1e-3, 0, (zb + 1.5 * MT) * 1e-3)))
        if bot_steel:                     # сталь под катушками (плоскость z = −TC): отражение ниже
            zs = -TC
            for zc, st in (((zb + MT / 2), 1),) + (((zb + 1.5 * MT), 1),) if top_steel else (((zb + MT / 2), 1),):
                c.add(magpy.magnet.Cuboid(polarization=(0, 0, -s * BR), dimension=(MX * 1e-3, MY * 1e-3, MT * 1e-3), position=(x * 1e-3, 0, (2 * zs - zc) * 1e-3)))
    return c
def run(gap=0.75, top=True, bot=False, TC=3.0, CW=6.5, ncoil=10):
    leg = (CW - 1.6) / 2
    n = int(FF * leg * TC / (np.pi * (OD / 2) ** 2))
    lt = 2 * ((CW - leg) + (MY + leg)) * 1e-3
    R = RHO * n * lt / (np.pi * (WIRE / 2) ** 2 * 1e-6)
    xs = [(k - (ncoil - 1) / 2) * CW for k in range(ncoil)]
    km = []
    for X in np.linspace(-22, 22, 23):
        c = cart(X, gap, top, bot, TC)
        def Bz(x0, x1):
            P = np.stack(np.meshgrid(np.linspace(x0, x1, 4), np.linspace(-MY / 2, MY / 2, 5), np.linspace(-TC, 0, 3), indexing="ij"), -1).reshape(-1, 3) * 1e-3
            return c.getB(P)[:, 2].mean()
        k = np.array([n * MY * 1e-3 * (Bz(x - CW / 2, x - CW / 2 + leg) - Bz(x + CW / 2 - leg, x + CW / 2)) for x in xs])
        km.append(np.sqrt((k ** 2).sum() / R))
    km = np.array(km)
    return km.min(), km[11]
for tag, kw in (("без стали вообще", dict(top=False, bot=False)),
                ("сталь на каретке (как в предложении)", dict(top=True, bot=False)),
                ("сталь на каретке + сталь под катушками", dict(top=True, bot=True))):
    kmin, kmid = run(**kw)
    print(f"{tag}: 3 Н ≈ {(3 / kmin) ** 2:.1f} Вт в худшей точке, {(3 / kmid) ** 2:.1f} Вт в середине (катушки 10 × 6.5 на 65 мм, зазор 0.75)")
# прижим каретки к стали под катушками: магнит над сталью на расстоянии gap+TC — сила как между магнитом и отражением
c1 = magpy.Collection(*[magpy.magnet.Cuboid(polarization=(0, 0, -s * BR), dimension=(MX * 1e-3, MY * 1e-3, MT * 1e-3), position=(p * MX / 2 * 1e-3, 0, (0.75 + MT / 2) * 1e-3), meshing=200) for p, s in ((-1, 1), (1, -1))])
c2 = magpy.Collection(*[magpy.magnet.Cuboid(polarization=(0, 0, -s * BR), dimension=(MX * 1e-3, MY * 1e-3, MT * 1e-3), position=(p * MX / 2 * 1e-3, 0, (2 * -3.0 - (0.75 + MT / 2)) * 1e-3)) for p, s in ((-1, 1), (1, -1))])
F, T = magpy.getFT(c2, c1)
print("прижим каретки к стали под катушками: %.1f Н (%.0f г)" % (abs(np.array(F).reshape(-1, 3).sum(axis=0)[2]), abs(np.array(F).reshape(-1, 3).sum(axis=0)[2]) * 102))
print("\nподбор ширины катушки (сталь на каретке, без стали снизу):")
for CW, nc in ((8.0, 8), (10.0, 7), (13.0, 5), (16.0, 4)):
    kmin, kmid = run(top=True, bot=False, CW=CW, ncoil=nc)
    print(f"  катушки {nc} × {CW}: 3 Н ≈ {(3 / kmin) ** 2:.1f} Вт (худшая), {(3 / kmid) ** 2:.1f} (середина)")
print("с толстой катушкой 5 мм (паз глубже), CW 10:")
kmin, kmid = run(top=True, bot=False, CW=10.0, ncoil=7, TC=5.0)
print(f"  3 Н ≈ {(3 / kmin) ** 2:.1f} Вт")
kmin, kmid = run(top=True, bot=True, CW=10.0, ncoil=7, TC=3.0)
print(f"  + сталь снизу, CW 10: 3 Н ≈ {(3 / kmin) ** 2:.1f} Вт")
