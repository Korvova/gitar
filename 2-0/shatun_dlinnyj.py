# -*- coding: utf-8 -*-
r"""Стенд с шатуном, если стенд можно удлинить (владелец 03.10): мотор дальше от плеча, шатун длинный,
длинное плечо LB длиннее. Кривошип — полный оборот (ничего не заклинит). Для каждой раскладки:
радиус кривошипа R подбирается так, чтобы ложе ходило ровно ±20; печатаем худший угол передачи
(шатун к плечу и шатун к кривошипу) и момент мотора на палец 3 Н.
Запуск: .venv-b123d\Scripts\python shatun_dlinnyj.py"""
import math
import numpy as np

RS, F, TRAVEL = 18.0, 3.0, 20.0


def solve_R(LB, d):
    """R: разность расстояний от оси мотора до стада плеча в крайних положениях = 2R (как в gitara_mini2.py)."""
    s = TRAVEL / LB
    dm = math.sqrt(RS ** 2 + d ** 2 + 2 * d * RS * s)
    dp = math.sqrt(RS ** 2 + d ** 2 - 2 * d * RS * s)
    return (dm - dp) / 2, (dm + dp) / 2


def run(LB, d):
    R, LC = solve_R(LB, d)
    AX, MY = 0.0, d                                   # ось плеча (0,0), мотор (0,d)
    mus, dx = [], []
    prev = None
    for th in np.radians(np.arange(0, 360, 0.5)):
        cx, cy = R * math.cos(th), MY + R * math.sin(th)
        dd = math.hypot(cx, cy)
        a = (RS ** 2 - LC ** 2 + dd ** 2) / (2 * dd)
        h = math.sqrt(max(RS ** 2 - a ** 2, 0))
        px, py = a * cx / dd, a * cy / dd
        sx, sy = max([(px + h * cy / dd, py - h * cx / dd), (px - h * cy / dd, py + h * cx / dd)], key=lambda q: q[0])
        phi = math.atan2(sy, sx)
        lx, ly = sx - cx, sy - cy
        mu = 90 - math.degrees(math.acos(min(1, abs(lx * (-sy) + ly * sx) / (LC * RS))))
        mus.append(mu)
        x = LB * math.sin(phi)
        if prev is not None:
            dx.append(abs(x - prev) / math.radians(0.5))
        prev = x
    return R, LC, min(mus), F * max(dx) / 1000


print(" LB  | мотор от оси | R кривошипа | шатун | худший угол | момент на 3 Н | длина стенда ~")
for LB in (32.5, 40, 50, 60):
    for d in (32.0, 50.0, 70.0, 90.0):
        R, LC, mu, t = run(LB, d)
        L = 16 + LB + d + R + 20
        print(f" {LB:4.1f} |   {d:4.0f}       |   {R:5.1f}     | {LC:5.1f} |    {mu:4.0f}°    |  {t:.3f} Н·м    | {L:4.0f} мм")
