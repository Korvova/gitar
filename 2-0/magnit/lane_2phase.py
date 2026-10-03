# -*- coding: utf-8 -*-
r"""Русло под магниты 15 × 10 × 5 N52 (как 15.3 на вики), но катушки — в ДВЕ фазы (03.10):
чтобы подключить к нашей плате с TMC2209 (или DRV8833) вместо шагового мотора.
Скоба: по 3 магнита с каждой стороны, шаг полюсов 10 (электрический период 20 мм), щель 4.
Пластина катушек 3 мм, без железа. Две фазы = катушки со сдвигом 90° электр. = 5 мм.
Варианты: N катушек шириной 52/N подряд, фазы по кругу A+, B+, A−, B− (для шага ≈ 5 мм).
Печатает силу вбок на 1 А в фазе и мощность на 300 / 500 г (провод 0.3 мм, как есть у владельца).
Запуск: .venv-b123d\Scripts\python magnit\lane_2phase.py"""
import numpy as np
import magpylib as magpy

BR, RHO, FF = 1.43, 1.72e-8, 0.5
TAU, T, H, G, TC = 10.0, 5.0, 15.0, 4.0, 3.0
WIRE, WIRE_OD = 0.30, 0.34


def carriage(X):
    c = magpy.Collection()
    for side in (-1, 1):
        for p in range(3):
            s = 1 if p % 2 == 0 else -1
            c.add(magpy.magnet.Cuboid(polarization=(0, s * BR, 0), dimension=(TAU * 1e-3, T * 1e-3, H * 1e-3),
                                      position=((X + (p - 1) * TAU) * 1e-3, side * (G / 2 + T / 2) * 1e-3, 0)))
    return c


def leg_B(col, x0, x1):
    xs = np.linspace(x0, x1, 5); ys = np.linspace(-TC / 2, TC / 2, 3); zs = np.linspace(-H / 2, H / 2, 7)
    P = np.stack(np.meshgrid(xs, ys, zs, indexing="ij"), -1).reshape(-1, 3) * 1e-3
    return col.getB(P)[:, 1].mean()


for ncoil in (8, 10, 11):
    cw = 52.0 / ncoil
    leg = (cw - 1.6) / 2                                      # окно 1.6 мм (оправка)
    n = int(FF * leg * TC * 1e-6 / (np.pi * (WIRE_OD / 2) ** 2 * 1e-6))
    l_turn = 2 * ((cw - leg) + (H + leg)) * 1e-3
    r = RHO * n * l_turn / (np.pi * (WIRE / 2) ** 2 * 1e-6)
    step_deg = cw / (2 * TAU) * 360                           # электрический сдвиг между соседними катушками
    xs = [(k - (ncoil - 1) / 2) * cw for k in range(ncoil)]
    el = [(k * step_deg) % 360 for k in range(ncoil)]
    # ближайшая фаза: A+ 0, B+ 90, A− 180, B− 270
    ph = [int(round(e / 90)) % 4 for e in el]
    F = []
    for X in np.linspace(-22, 22, 23):
        col = carriage(X)
        kA = kB = 0.0
        for xc, q in zip(xs, ph):
            k = n * H * 1e-3 * (leg_B(col, xc - cw / 2, xc - cw / 2 + leg) - leg_B(col, xc + cw / 2 - leg, xc + cw / 2))
            if q == 0: kA += k
            elif q == 2: kA -= k
            elif q == 1: kB += k
            else: kB -= k
        F.append(np.hypot(kA, kB))
    F = np.array(F)
    rph = r * ncoil / 2                                       # сопротивление фазы (катушки последовательно)
    i300 = 0.3 * 9.81 / F.min(); i500 = 0.5 * 9.81 / F.min()
    print(f"{ncoil} катушек по {cw:.1f} мм (сдвиг {step_deg:.0f}°, фазы {''.join('AbaB'[q] for q in ph)}): "
          f"{n} витков, фаза {rph:.1f} Ом; сила на 1 А: середина {F[11] * 102:.0f} г, мин {F.min() * 102:.0f} г; "
          f"300 г: {i300:.2f} А, {2 * i300 ** 2 * rph:.1f} Вт; 500 г: {i500:.2f} А, {2 * i500 ** 2 * rph:.1f} Вт")

print("\nтот же расчёт, если каждой катушкой управлять отдельно (ток только в катушках под скобой, по силе):")
for ncoil in (8, 10):
    cw = 52.0 / ncoil
    leg = (cw - 1.6) / 2
    n = int(FF * leg * TC * 1e-6 / (np.pi * (WIRE_OD / 2) ** 2 * 1e-6))
    l_turn = 2 * ((cw - leg) + (H + leg)) * 1e-3
    r = RHO * n * l_turn / (np.pi * (WIRE / 2) ** 2 * 1e-6)
    xs = [(k - (ncoil - 1) / 2) * cw for k in range(ncoil)]
    Km = []
    for X in np.linspace(-22, 22, 23):
        col = carriage(X)
        k = np.array([n * H * 1e-3 * (leg_B(col, xc - cw / 2, xc - cw / 2 + leg) - leg_B(col, xc + cw / 2 - leg, xc + cw / 2)) for xc in xs])
        Km.append(np.sqrt((k ** 2).sum() / r))
    Km = np.array(Km)
    print(f"  {ncoil} катушек: Км мин {Km.min():.2f} Н/√Вт, середина {Km[11]:.2f}; 300 г: {(0.3 * 9.81 / Km.min()) ** 2:.1f} Вт (середина {(0.3 * 9.81 / Km[11]) ** 2:.1f}); 500 г: {(0.5 * 9.81 / Km.min()) ** 2:.1f} Вт")
