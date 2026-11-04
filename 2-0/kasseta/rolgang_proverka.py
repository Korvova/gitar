# -*- coding: utf-8 -*-
r"""Рольганг (04.11.2026, идея владельца): три верхние шестерни z12 через 6 шагов рейки (m0.8 → 15.08), средняя на моторе,
крайние — от средней через промежуточные в нижнем слое; тележка 20 мм с рейкой 20. Проверка ДО модели:
  1) какие зубья у промежуточной (z13…16) и её фаза — чтобы она одновременно цеплялась со средней и крайней;
  2) рейка 20 по ходу ±24: на скольких шестернях, нет ли пересечений при переходе.
Запуск: ..\.venv-b123d\Scripts\python rolgang_proverka.py
"""
import math
from build123d import *

M = 0.8
PA = math.radians(20)
ZP = 12
RP = M * ZP / 2                    # 4.8
PITCH = math.pi * M
S = 6 * PITCH                      # 15.08 — шаг верхних шестерён
RK_HALF = 10.0                     # рейка 20 (тележка 20)
T = 3.0


def gear_pts(m, z, pa, backlash=0.08, n=12, add=1.0):
    rp = m * z / 2
    rb, ra, rf = rp * math.cos(pa), rp + add * m, rp - 1.25 * m
    inv = lambda a: math.tan(a) - a
    half_t = (math.pi * m / 2 - backlash) / (2 * rp)
    pts = []
    for i in range(z):
        c = 2 * math.pi * i / z
        fl = []
        for k in range(n + 1):
            r = max(rb + (ra - rb) * k / n if rb > rf else rf + (ra - rf) * k / n, rb)
            a = math.acos(min(rb / r, 1.0))
            fl.append((r, half_t + inv(pa) - inv(a)))
        tooth = [(rf, -(half_t + inv(pa) + 0.02))] + [(r, -t) for r, t in fl] + [(r, t) for r, t in reversed(fl)] + [(rf, half_t + inv(pa) + 0.02)]
        pts += [(r * math.cos(c + t), r * math.sin(c + t)) for r, t in tooth]
    pts.append(pts[0])
    return pts


def gear(z, add=1.0):
    return extrude(make_face(Polyline(*gear_pts(M, z, PA, add=add))), T)


# верхняя шестерня z12: впадина на +Y (к рейке) при угле 0
_p = 360.0 / ZP
OFF_P = 90.0 - (round(90.0 / _p - 0.5) + 0.5) * _p
pin = Rot(0, 0, OFF_P) * gear(ZP)

# рейка (зубья на −Y), головка 0.7 m — z12 без подреза
ADD, DED = 0.7 * M, 1.25 * M
tn = math.tan(PA)
th = (PITCH / 2 - 0.08) / 2
Y_RK = RP
rk = Pos(0, 0, 0) * extrude(make_face(Polyline((-RK_HALF, Y_RK + DED), (RK_HALF, Y_RK + DED), (RK_HALF, Y_RK + DED + 2),
                                               (-RK_HALF, Y_RK + DED + 2), (-RK_HALF, Y_RK + DED))), T)
for i in range(-7, 8):
    xc = i * PITCH
    pr = [(xc - th - DED * tn, Y_RK + DED), (xc - th + ADD * tn, Y_RK - ADD), (xc + th - ADD * tn, Y_RK - ADD), (xc + th + DED * tn, Y_RK + DED)]
    rk += extrude(make_face(Polyline(*(pr + [pr[0]]))), T)
rk = rk & Pos(0, Y_RK, T / 2) * Box(2 * RK_HALF, 10, T + 1)


def pin_at(x, c):
    return Pos(x, 0, 0) * Rot(0, 0, -math.degrees(c / RP)) * pin       # рейка на +x → шестерня по часовой


# ---- 1) промежуточная ----
best = None
for zi in (13, 14, 15, 16):
    ri = M * zi / 2
    d = RP + ri
    if d <= S / 2:
        continue
    dy = math.sqrt(d * d - (S / 2) ** 2)
    idl0 = gear(zi)
    res = []
    for k in range(24):                                                  # перебор фазы промежуточной
        ph = k * (360.0 / zi) / 24
        worst = 0.0
        for c in (0.0, 0.37, 0.9, 1.6):
            ang_i = ph + math.degrees(c / ri)                            # промежуточная — в обратную сторону
            idl = Pos(S / 2, -dy, 0) * Rot(0, 0, ang_i) * idl0
            v = (Part() + (idl & pin_at(0, c))).volume + (Part() + (idl & pin_at(S, c))).volume
            worst = max(worst, v)
        res.append((worst, ph))
    w, ph = min(res)
    span = dy + ri + M + (Y_RK + DED + 2)                                # от низа промежуточной до спинки рейки
    print("промежуточная z%d: R %.1f, сдвиг вниз %.2f, лучшая фаза %.2f° → пересечение %.3f мм³; ширина по Y %.1f мм"
          % (zi, ri, dy, ph, w, span))
    if w < 0.01 and span < 23 and best is None:
        best = (zi, ph, dy)
print("выбрана:", best)

# ---- 2) рейка по ходу ±24 ----
worst, on_min, both = 0.0, 9, []
for i in range(-96, 97):
    c = i * 0.25
    r = Pos(c, 0, 0) * rk
    on = 0
    for x in (-S, 0, S):
        v = (Part() + (pin_at(x, c) & r)).volume
        worst = max(worst, v)
        if c - RK_HALF <= x - 0.9 and c + RK_HALF >= x + 0.9:         # рейка заходит за ось шестерни ≥ 0.9
            on += 1
    on_min = min(on_min, on)
    if on >= 2:
        both.append(c)
print("рейка × шестерни по ходу ±24: наибольшее пересечение %.3f мм³; минимум шестерён под рейкой %d" % (worst, on_min))
print("на двух шестернях сразу: c от %.2f до %.2f (и зеркально)" % (min(x for x in both if x > 0), max(x for x in both if x > 0)))
r = Pos(0, 0, 0) * rk
print("пол-зуба при c=0: %.2f мм³ (> 0 — в зацеплении)" % (Part() + (Pos(0, 0, 0) * Rot(0, 0, 15) * pin & r)).volume)
