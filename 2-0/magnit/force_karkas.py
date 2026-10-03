# -*- coding: utf-8 -*-
r"""Сила тяги варианта «катушка в каркасе» (щель 5) против голой катушки (щель 4): магниты 20×10×5 стоя,
8 катушек по 6.5 (40 витков провода 0.3), две фазы последовательно от нашей платы (как в пробе),
и для сравнения — каждой катушкой отдельно. Сила в граммах при токе 1 / 1.5 / 2 А.
Запуск: .venv-b123d\Scripts\python magnit\force_karkas.py"""
import numpy as np
import magpylib as magpy
BR, H, TC, CW, N = 1.35, 16.0, 3.0, 6.5, 40
LEG = (CW - 1.6) / 2
PH = [0, 1, 3, 0, 1, 2, 0, 1]          # A+ B+ B− A+ B+ A− A+ B+ (как спаяно)


def forces(G):
    out2, outi = [], []
    for X in np.linspace(-22, 22, 23):
        c = magpy.Collection()
        for side in (-1, 1):
            for p in range(3):
                c.add(magpy.magnet.Cuboid(polarization=(0, (1 if p % 2 == 0 else -1) * BR, 0), dimension=(10e-3, 5e-3, 20e-3),
                                          position=((X + (p - 1) * 10) * 1e-3, side * (G / 2 + 2.5) * 1e-3, 0)))

        def B(x0, x1):
            P = np.stack(np.meshgrid(np.linspace(x0, x1, 5), np.linspace(-TC / 2, TC / 2, 3), np.linspace(-H / 2, H / 2, 7),
                                     indexing="ij"), -1).reshape(-1, 3) * 1e-3
            return c.getB(P)[:, 1].mean()
        k = np.array([N * H * 1e-3 * (B(x - CW / 2, x - CW / 2 + LEG) - B(x + CW / 2 - LEG, x + CW / 2))
                      for x in [(i - 3.5) * CW for i in range(8)]])
        kA = sum(k[i] * (1 if PH[i] == 0 else -1) for i in range(8) if PH[i] in (0, 2))
        kB = sum(k[i] * (1 if PH[i] == 1 else -1) for i in range(8) if PH[i] in (1, 3))
        out2.append(np.hypot(kA, kB))                     # Н на 1 А в фазах (синус/косинус)
        outi.append(np.sqrt((k ** 2).sum()))              # Н на 1 А, если ток в каждой катушке по её силе
    return np.array(out2), np.array(outi)


for tag, G in (("голая катушка, щель 4", 4.0), ("в каркасе, щель 5", 5.0)):
    f2, fi = forces(G)
    g = lambda f, i: f * i * 102
    print(f"{tag}: от нашей платы (2 фазы) мин/середина — 1 А: {g(f2.min(), 1):.0f}/{g(f2[11], 1):.0f} г, "
          f"1.5 А: {g(f2.min(), 1.5):.0f}/{g(f2[11], 1.5):.0f} г, 2 А: {g(f2.min(), 2):.0f}/{g(f2[11], 2):.0f} г; "
          f"по катушке отдельно 2 А: {g(fi.min(), 2):.0f} г")
