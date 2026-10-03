# -*- coding: utf-8 -*-
"""Проба магнитного русла из того, что есть у владельца (03.10): диски 4 × 2 мм (49 шт, «0.2 кг»,
намагничены по оси — сплав не указан, считаем N35, Br 1.2 Тл) и провод ПЭТВ-2 0.3 мм, 20 м.

Тележка — U-скоба: с двух сторон пластины катушек по ряду полюсов, полюс — столбик из дисков
(ось столбика смотрит на пластину), полюса N-S-N-S с шагом TAU. Пластина катушек — без железа,
две фазы A/B (как шаговик: драйвер TMC2209 с нашей платы или DRV8833). Катушки шириной 1.5·TAU
подряд: A+, B−, A−, B+, … (сдвиг 270° электрических).
Печатает: витки, сопротивление, силу вбок на 1 А по ходу ±22 мм — без стальных пластин
(со сталью за магнитами — заметно больше).
Запуск: .venv-b123d\\Scripts\\python magnit\\lane_disk4x2.py
"""
import numpy as np
import magpylib as magpy

BR = 1.2                       # Тл, N35 (сплав не указан)
D = 4.0                        # диаметр диска
TAU = 5.0                      # шаг полюсов
G = 4.0                        # щель между рядами магнитов (пластина 3 + по 0.5)
TC = 3.0                       # толщина пластины катушек
WIRE, WIRE_OD, FF = 0.30, 0.34, 0.5
CW = 1.5 * TAU                 # ширина катушки
LEG = CW / 3                   # ширина ветви (окно = ветвь)
NCOIL = 7                      # 7 × 7.5 = 52.5 — на ширину грифа
RHO = 1.72e-8


def carriage(X, hm, npole):
    c = magpy.Collection()
    for side in (-1, 1):
        for p in range(npole):
            s = 1 if p % 2 == 0 else -1
            c.add(magpy.magnet.Cylinder(polarization=(0, 0, s * BR), dimension=(D * 1e-3, hm * 1e-3),   # ось диска — на пластину (после поворота z -> y)
                                        position=((X + (p - (npole - 1) / 2) * TAU) * 1e-3,
                                                  side * (G / 2 + hm / 2) * 1e-3, 0),
                                        ).rotate_from_angax(90, "x", anchor=None))
    return c


def leg_B(col, x0, x1, h):
    xs = np.linspace(x0, x1, 5); ys = np.linspace(-TC / 2, TC / 2, 3); zs = np.linspace(-h / 2, h / 2, 5)
    P = np.stack(np.meshgrid(xs, ys, zs, indexing="ij"), -1).reshape(-1, 3) * 1e-3
    return col.getB(P)[:, 1].mean()


area = LEG * TC * 1e-6
N = int(FF * area / (np.pi * (WIRE_OD / 2) ** 2 * 1e-6))
H_ACT = D + 1.0                                                   # активная высота катушки
l_turn = 2 * ((CW - LEG) + H_ACT + LEG) * 1e-3
R = RHO * N * l_turn / (np.pi * (WIRE / 2) ** 2 * 1e-6)
wire_m = N * l_turn * NCOIL
coil_x = [(k - (NCOIL - 1) / 2) * CW for k in range(NCOIL)]
elec = [(k * 270) % 360 for k in range(NCOIL)]                    # 0 A+, 90 B+, 180 A−, 270 B−
print(f"катушка: {N} витков, {R:.2f} Ом, на 7 катушек провода {wire_m:.1f} м (есть 20 м)")
print(f"фаза: {NCOIL // 2 + 1} / {NCOIL // 2} катушки последовательно ≈ {R * 4:.1f} / {R * 3:.1f} Ом")

for hm, npole, tag in ((4.0, 6, "по 2 диска в полюсе, 6 полюсов на сторону — 24 диска"),
                       (8.0, 6, "по 4 диска в полюсе, 6 полюсов на сторону — 48 дисков")):
    Fs = []
    for X in np.linspace(-22, 22, 23):
        col = carriage(X, hm, npole)
        kA = kB = 0.0
        for xc, e in zip(coil_x, elec):
            bl = leg_B(col, xc - CW / 2, xc - CW / 2 + LEG, H_ACT)
            br = leg_B(col, xc + CW / 2 - LEG, xc + CW / 2, H_ACT)
            k = N * H_ACT * 1e-3 * (bl - br)                      # Н/А
            if e == 0: kA += k
            elif e == 180: kA -= k
            elif e == 90: kB += k
            else: kB -= k
        Fs.append(np.hypot(kA, kB))                               # сила при 1 А в фазах (синус/косинус)
    Fs = np.array(Fs)
    print(f"\n{tag}:")
    print(f"  сила вбок при 1 А: середина {Fs[11] * 102:.0f} г, у краёв ±22 {Fs[0] * 102:.0f} / {Fs[-1] * 102:.0f} г, мин {Fs.min() * 102:.0f} г")
    print(f"  при 1.5 А: середина {Fs[11] * 153:.0f} г, мин {Fs.min() * 153:.0f} г; нагрев ~{1.5 ** 2 * R * 4:.1f} Вт на фазу")


# ---------- 03.10: плитка вместо столбика — полюс из 2×2 столбиков рядом (торец ~8 × 8) ----------
def carriage_tile(X, depth, npole, tau, nx, nz):
    c = magpy.Collection()
    for side in (-1, 1):
        for p in range(npole):
            s = 1 if p % 2 == 0 else -1
            for ix in range(nx):
                for iz in range(nz):
                    c.add(magpy.magnet.Cylinder(polarization=(0, 0, s * BR), dimension=(D * 1e-3, depth * 1e-3),
                                                position=((X + (p - (npole - 1) / 2) * tau + (ix - (nx - 1) / 2) * D) * 1e-3,
                                                          side * (G / 2 + depth / 2) * 1e-3, (iz - (nz - 1) / 2) * D * 1e-3),
                                                ).rotate_from_angax(90, "x", anchor=None))
    return c


def lane(tau, h_act, make):
    cw, leg = 1.5 * tau, 0.5 * tau
    n = int(FF * leg * TC * 1e-6 / (np.pi * (WIRE_OD / 2) ** 2 * 1e-6))
    l_turn = 2 * ((cw - leg) + h_act + leg) * 1e-3
    r = RHO * n * l_turn / (np.pi * (WIRE / 2) ** 2 * 1e-6)
    ncoil = int(52.5 // cw)
    xs = [(k - (ncoil - 1) / 2) * cw for k in range(ncoil)]
    el = [(k * 270) % 360 for k in range(ncoil)]
    F = []
    for X in np.linspace(-22, 22, 23):
        col = make(X)
        kA = kB = 0.0
        for xc, e in zip(xs, el):
            k = n * h_act * 1e-3 * (leg_B(col, xc - cw / 2, xc - cw / 2 + leg, h_act) - leg_B(col, xc + cw / 2 - leg, xc + cw / 2, h_act))
            if e == 0: kA += k
            elif e == 180: kA -= k
            elif e == 90: kB += k
            else: kB -= k
        F.append(np.hypot(kA, kB))
    F = np.array(F)
    return n, r, ncoil, n * l_turn * ncoil, F


print("\n=== плитка: полюс 2 × 2 столбика по 2 диска (торец 8 × 8, глубина 4), шаг 10, 3 полюса на сторону — 48 дисков ===")
n, r, nc, wm, F = lane(10.0, 9.0, lambda X: carriage_tile(X, 4.0, 3, 10.0, 2, 2))
print(f"  катушки: {nc} шт по {n} витков, {r:.2f} Ом, провода {wm:.1f} м")
print(f"  сила вбок при 1 А: середина {F[11] * 102:.0f} г, у краёв {F[0] * 102:.0f} / {F[-1] * 102:.0f} г, мин {F.min() * 102:.0f} г; при 1.5 А середина {F[11] * 153:.0f} г")
print("=== столбик 8 дисков (Ø4 × 16) торцом к катушкам, шаг 5, 6 полюсов на сторону — 96 дисков (для сравнения) ===")
n, r, nc, wm, F = lane(5.0, 5.0, lambda X: carriage(X, 16.0, 6))
print(f"  сила вбок при 1 А: середина {F[11] * 102:.0f} г, мин {F.min() * 102:.0f} г")
