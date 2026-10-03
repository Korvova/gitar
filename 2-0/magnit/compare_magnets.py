# -*- coding: utf-8 -*-
r"""Сравнение магнитов из Ozon для скобы (03.10): что даёт силу на ватт в русле 52 мм, высота ≤ 25.
Скоба — магниты с двух сторон пластины катушек (щель 4, пластина 3), полюса N-S-N, катушки без железа,
каждой катушкой управляем отдельно (лучший случай). Км = сила / √(мощность), мин. по ходу ±22.
Запуск: .venv-b123d\Scripts\python magnit\compare_magnets.py"""
import numpy as np
import magpylib as magpy

RHO, FF, G, TC = 1.72e-8, 0.5, 4.0, 3.0
WIRE, WIRE_OD = 0.30, 0.34


def mk(kind, X, a, b, t, npole, br):
    c = magpy.Collection()
    for side in (-1, 1):
        for p in range(npole):
            s = 1 if p % 2 == 0 else -1
            pos = ((X + (p - (npole - 1) / 2) * a) * 1e-3, side * (G / 2 + t / 2) * 1e-3, 0)
            if kind == "disk":
                m = magpy.magnet.Cylinder(polarization=(0, 0, s * br), dimension=(a * 1e-3, t * 1e-3), position=pos)
                m.rotate_from_angax(90, "x", anchor=None)
            else:
                m = magpy.magnet.Cuboid(polarization=(0, s * br, 0), dimension=(a * 1e-3, t * 1e-3, b * 1e-3), position=pos)
            c.add(m)
    return c


def km(kind, a, b, t, npole, br, ncoil):
    h = b if kind != "disk" else a * 0.8                     # активная высота катушки
    cw = 52.0 / ncoil
    leg = (cw - 1.6) / 2
    n = int(FF * leg * TC * 1e-6 / (np.pi * (WIRE_OD / 2) ** 2 * 1e-6))
    r = RHO * n * 2 * ((cw - leg) + (h + leg)) * 1e-3 / (np.pi * (WIRE / 2) ** 2 * 1e-6)
    xs = [(k - (ncoil - 1) / 2) * cw for k in range(ncoil)]
    out = []
    for X in np.linspace(-22, 22, 23):
        col = mk(kind, X, a, b, t, npole, br)

        def B(x0, x1):
            P = np.stack(np.meshgrid(np.linspace(x0, x1, 5), np.linspace(-TC / 2, TC / 2, 3), np.linspace(-h / 2, h / 2, 7),
                                     indexing="ij"), -1).reshape(-1, 3) * 1e-3
            return col.getB(P)[:, 1].mean()
        k = np.array([n * h * 1e-3 * (B(x - cw / 2, x - cw / 2 + leg) - B(x + cw / 2 - leg, x + cw / 2)) for x in xs])
        out.append(np.sqrt((k ** 2).sum() / r))
    return np.array(out), h


cases = [("15×10×5 N52 (план, гранью 10 вдоль хода, 3 полюса)", "box", 10, 15, 5, 3, 1.43, 8),
         ("диск Ø15×5 (3 полюса, шаг 15)", "disk", 15, 15, 5, 3, 1.35, 6),
         ("20×10×5 лёжа: 20 вдоль хода, 10 высота (2 полюса)", "box", 20, 10, 5, 2, 1.35, 4),
         ("20×10×5 стоя: 10 вдоль хода, 20 высота (3 полюса) — выше 25 мм", "box", 10, 20, 5, 3, 1.35, 8),
         ("20×10×3 с дыркой лёжа (2 полюса)", "box", 20, 10, 3, 2, 1.3, 4)]
for tag, kind, a, b, t, npole, br, nc in cases:
    K, h = km(kind, a, b, t, npole, br, nc)
    stack = 1.5 + 0.3 + 1.2 + 0.5 + 2 + h + 2 + 1
    print(f"{tag}: Км мин {K.min():.2f}, середина {K[11]:.2f} Н/√Вт -> 300 г: {(0.3 * 9.81 / K.min()) ** 2:.0f} Вт, "
          f"500 г: {(0.5 * 9.81 / K.min()) ** 2:.0f} Вт; высота стопки ~{stack:.1f} мм; длина скобы {a * npole:.0f} мм")

# 20×10×5 стоя, но катушка ниже магнита: активная 16 + лобовые по 2 = 20 — всё в высоте магнита, стопка 25
import types
K = None
def km_h(a, b, t, npole, br, ncoil, h):
    global km
    cw = 52.0 / ncoil; leg = (cw - 1.6) / 2
    n = int(FF * leg * TC * 1e-6 / (np.pi * (WIRE_OD / 2) ** 2 * 1e-6))
    r = RHO * n * 2 * ((cw - leg) + (h + leg)) * 1e-3 / (np.pi * (WIRE / 2) ** 2 * 1e-6)
    xs = [(k - (ncoil - 1) / 2) * cw for k in range(ncoil)]
    out = []
    for X in np.linspace(-22, 22, 23):
        col = mk("box", X, a, b, t, npole, br)
        def B(x0, x1):
            P = np.stack(np.meshgrid(np.linspace(x0, x1, 5), np.linspace(-TC / 2, TC / 2, 3), np.linspace(-h / 2, h / 2, 7),
                                     indexing="ij"), -1).reshape(-1, 3) * 1e-3
            return col.getB(P)[:, 1].mean()
        k = np.array([n * h * 1e-3 * (B(x - cw / 2, x - cw / 2 + leg) - B(x + cw / 2 - leg, x + cw / 2)) for x in xs])
        out.append(np.sqrt((k ** 2).sum() / r))
    return np.array(out)
K = km_h(10, 20, 5, 3, 1.35, 8, 16.0)
stack = 1.5 + 0.3 + 1.2 + 0.5 + 20 + 0.5 + 1
print(f"20×10×5 стоя, катушка 16 + лобовые внутри высоты магнита: Км мин {K.min():.2f} -> 300 г: {(0.3 * 9.81 / K.min()) ** 2:.0f} Вт, "
      f"500 г: {(0.5 * 9.81 / K.min()) ** 2:.0f} Вт; высота стопки ~{stack:.1f} мм")
