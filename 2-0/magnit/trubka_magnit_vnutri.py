# Трубчатый мотор: магнит Ø12 осевой в трубке, секции катушек на трубке с шагом P. Сила на 1 А и на √Вт.
import numpy as np, magpylib as magpy
RHO, FF, WIRE, OD = 1.72e-8, 0.5, 0.30, 0.34
def calc(Dm=12, Lm=20, br=1.43, P=8.8, Wsec=7.8, r0=7.25, r1=11.0, nsec=10):
    n = int(FF * Wsec * (r1 - r0) / (np.pi * (OD / 2) ** 2))           # витков в секции
    lt = 2 * np.pi * (r0 + r1) / 2 * 1e-3
    R = RHO * n * lt / (np.pi * (WIRE / 2) ** 2 * 1e-6)
    zs = [(k - (nsec - 1) / 2) * P for k in range(nsec)]
    out = []
    for X in np.linspace(-22, 22, 23):
        m = magpy.magnet.Cylinder(polarization=(0, 0, br), dimension=(Dm * 1e-3, Lm * 1e-3), position=(0, 0, X * 1e-3))
        k = []
        for z in zs:
            rr = np.linspace(r0, r1, 4); zz = np.linspace(z - Wsec / 2, z + Wsec / 2, 6)
            P3 = np.array([[r * 1e-3, 0, q * 1e-3] for r in rr for q in zz])
            B = m.getB(P3)
            Br = B[:, 0].mean()
            rm = rr.mean() * 1e-3
            k.append(n * 2 * np.pi * rm * Br)          # Н/А (сила на катушку = на магнит с обратным знаком)
        k = np.array(k)
        out.append((np.sqrt((k ** 2).sum() / R), np.abs(k).max()))
    km = np.array([o[0] for o in out])
    return n, R, km.min(), km.mean()
print("магнит Ø12, катушки r 7.25..11 (толщина намотки 3.75), секции по 7.8 с шагом 8.8, провод 0.3:")
for Lm in (12, 16, 20, 24):
    n, R, kmin, kmean = calc(Lm=Lm)
    P3 = (3 / kmin) ** 2
    print(f"  магнит длиной {Lm}: секция {n} витков {R:.1f} Ом; Км мин {kmin:.2f} Н/√Вт -> 3 Н ≈ {P3:.1f} Вт (в худшей точке), 5 Н ≈ {(5/kmin)**2:.1f} Вт")
print("толще намотка (r до 12.5, гриф выше):")
n, R, kmin, kmean = calc(Lm=20, r1=12.5)
print(f"  магнит 20: {n} витков {R:.1f} Ом; 3 Н ≈ {(3/kmin)**2:.1f} Вт")
print("для сравнения плоское русло 20×10×5: 300 г (2.9 Н) ≈ 9 Вт")
