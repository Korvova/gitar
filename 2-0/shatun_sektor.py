# -*- coding: utf-8 -*-
r"""Стенд v2: кривошип ходит туда-сюда в секторе (не полный оборот) — подбор длины шатуна и сектора,
чтобы угол передачи (шатун к плечу) был как можно ближе к 90° на всём ходе ложа ±20.
Варианты: A — кривошип R10 как есть (меняем только шатун); B — кривошип больше (нужно новое дно).
Запуск: .venv-b123d\Scripts\python shatun_sektor.py"""
import math
import numpy as np

CART_Y, MY, LB, RS = 16.0, 80.0, 32.51, 18.0
AX = CART_Y + LB
PHM = math.asin(20 / LB)                         # плечо ±38° = ложе ±20


def study(R, LC):
    """Обходим кривошип по кругу, для каждого угла — положение плеча (восточная ветвь), угол передачи."""
    rows = []
    for th in np.radians(np.arange(0, 360, 0.5)):
        cx, cy = R * math.cos(th), MY + R * math.sin(th)
        dx, dy = cx, cy - AX
        d = math.hypot(dx, dy)
        if d > RS + LC or d < abs(RS - LC):
            rows.append(None); continue
        a = (RS ** 2 - LC ** 2 + d ** 2) / (2 * d)
        h = math.sqrt(max(RS ** 2 - a ** 2, 0))
        px, py = a * dx / d, a * dy / d
        sx, sy = max([(px + h * dy / d, py - h * dx / d), (px - h * dy / d, py + h * dx / d)], key=lambda q: q[0])
        phi = math.atan2(sy, sx)
        lx, ly = sx - (cx), (AX + sy) - cy
        ux, uy = -sy, sx                          # скорость стада плеча
        mu = 90 - math.degrees(math.acos(min(1, abs(lx * ux + ly * uy) / (math.hypot(lx, ly) * RS))))
        rows.append((math.degrees(th), phi, mu))
    return rows


def best_sector(rows):
    """Самый короткий непрерывный кусок обхода, где плечо проходит от −38° до +38°, и его худший угол."""
    best = None
    n = len(rows)
    for i in range(n):
        if rows[i] is None or abs(rows[i][1] + PHM) > 0.02:
            continue
        mu_min, j, steps = 90, i, 0
        while steps < n:
            r = rows[j % n]
            if r is None:
                break
            mu_min = min(mu_min, r[2])
            if abs(r[1] - PHM) < 0.02:
                sweep = steps * 0.5
                if best is None or mu_min > best[0]:
                    best = (mu_min, sweep, rows[i][0])
                break
            j += 1; steps += 1
    return best


print("A: кривошип R10 (дно то же), подбираем длину шатуна; ход — сектор туда-сюда")
for LC in np.arange(25, 45.1, 2.5):
    b = best_sector(study(10.0, LC))
    if b:
        print(f"  шатун {LC:4.1f}: худший угол передачи {b[0]:4.0f}°, кривошип ходит {b[1]:5.1f}°")
print("сейчас: шатун 34.87, полный оборот — худший угол 31°")
print("\nB: кривошип больше (новое дно с окном шире), шатун подбираем")
for R in (14.0, 17.0, 20.0):
    res = []
    for LC in np.arange(20, 50.1, 1.0):
        b = best_sector(study(R, LC))
        if b:
            res.append((b[0], LC, b[1]))
    m = max(res)
    print(f"  R{R:.0f}: лучший угол {m[0]:.0f}° при шатуне {m[1]:.0f}, кривошип ходит {m[2]:.0f}°")
