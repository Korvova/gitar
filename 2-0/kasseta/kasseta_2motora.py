# -*- coding: utf-8 -*-
r"""КОНЦЕПТ (04.11.2026, вопрос владельца): кассета на два мотора GB1806 вместо телескопа. Два мотора стоят рядом поперёк
грифа (оси вверх), у каждого шестерня m1 z14 (как стенд 103); одна рейка тележки длиной 30 переходит с шестерни на
шестерню — «электронный рольганг»: посредников нет, при ручном ходе крутится только тот мотор, на котором тележка.
Шестерни через 8 шагов рейки (8π = 25.13) — у обеих один и тот же угол при одном положении тележки, переход без удара;
прошивка с датчиками AS5048A держит оба мотора в фазе. Ход тележки ±24: на краях рейка на одной шестерне, посередине на
обеих. Тележка ездит по Т-рельсу вдоль задней стенки. Только для вида и проверки зацепления — не для печати.
Запуск: ..\.venv-b123d\Scripts\python kasseta_2motora.py
"""
import math
import os
from build123d import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "Print", "Print")
M, Z = 1.0, 14
RP = M * Z / 2                       # 7
PA = math.radians(20)
PITCH = math.pi * M
X_P = 4 * PITCH                      # ±12.57 — шестерни через 8 шагов
W, L = 24.0, 54.0                    # кассета вдоль грифа × поперёк
T_BASE = 1.2
MOT_R, MOT_H = 11.0, 20.5            # GB1806 с корпусом энкодера
Y_M = 11.0                           # оси моторов
Z_G0 = T_BASE + MOT_H + 0.4          # 22.1 — низ шестерён
G_T = 4.0
Y_RK = Y_M + RP                      # делительная линия рейки (зубья смотрят на −Y)
RK_HALF = 15.0                       # рейка 30
TRAVEL = 24.0


def BB(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))


def involute_gear_pts(m, z, pa, backlash=0.1, n=12):
    rp = m * z / 2
    rb, ra, rf = rp * math.cos(pa), rp + m, rp - 1.25 * m
    inv = lambda a: math.tan(a) - a
    half_t = (math.pi * m / 2 - backlash) / (2 * rp)
    pts = []
    for i in range(z):
        c = 2 * math.pi * i / z
        flank = []
        for k in range(n + 1):
            r = max(rb + (ra - rb) * k / n if rb > rf else rf + (ra - rf) * k / n, rb)
            a = math.acos(min(rb / r, 1.0))
            flank.append((r, half_t + inv(pa) - inv(a)))
        tooth = [(rf, -(half_t + inv(pa) + 0.02))] + [(r, -t) for r, t in flank] + [(r, t) for r, t in reversed(flank)] + [(rf, half_t + inv(pa) + 0.02)]
        pts += [(r * math.cos(c + t), r * math.sin(c + t)) for r, t in tooth]
    pts.append(pts[0])
    return pts


# шестерня: впадина смотрит на +Y (к рейке) при нулевом угле
_pitch = 360.0 / Z
_off = 90.0 - (round(90.0 / _pitch - 0.5) + 0.5) * _pitch
gear = Rot(0, 0, _off) * extrude(make_face(Polyline(*involute_gear_pts(M, Z, PA))), G_T)
gear -= Pos(0, 0, G_T / 2) * Cylinder(1.5, G_T + 0.2)

# рейка тележки: зубья на −Y, зуб в x = 0 (головка 0.8 m — без подреза z14), центр рейки = центр тележки
ADD, DED = 0.8 * M, 1.25 * M
tan = math.tan(PA)
t_half = (PITCH / 2 - 0.1) / 2
rk = BB(-RK_HALF, RK_HALF, Y_RK + DED, Y_RK + DED + 2.0, 0, G_T)
k = int(RK_HALF // PITCH)
for i in range(-k, k + 1):
    xc = i * PITCH
    prof = [(xc - t_half - DED * tan, Y_RK + DED), (xc - t_half + ADD * tan, Y_RK - ADD), (xc + t_half - ADD * tan, Y_RK - ADD),
            (xc + t_half + DED * tan, Y_RK + DED)]
    rk += extrude(make_face(Polyline(*(prof + [prof[0]]))), G_T)
rk = rk & BB(-RK_HALF, RK_HALF, 0, W, -1, G_T + 1)
# тележка: пластина над шестернями + рейка снизу + полоз на Т-рельс у задней стенки (y ≈ 21)
Z_C0 = Z_G0 + G_T + 0.3
cart = BB(-RK_HALF, RK_HALF, 2.0, W - 0.5, Z_C0, Z_C0 + 2.5) + Pos(0, 0, Z_G0) * rk
Z_RAIL0, Z_RAIL1 = T_BASE + MOT_H + 0.3, Z_G0 + 2.3                                      # рельс над моторами (верх мотора 21.7)
cart += BB(-RK_HALF, RK_HALF, 19.5, W - 0.5, Z_RAIL0, Z_C0 + 0.01)                        # полоз
cart -= BB(-RK_HALF - 1, RK_HALF + 1, 20.3, 22.7, Z_RAIL0 - 0.1, Z_RAIL1 + 0.2)             # паз под рельс
# основание: дно, 2 мотора, рельс вдоль задней стенки на стойках по краям
base = BB(-L / 2, L / 2, 0, W, 0, T_BASE)
for sx in (1, -1):
    base += BB(*sorted((sx * (L / 2 - 3), sx * L / 2)), 20.5, 22.5, T_BASE - 0.01, Z_RAIL0 + 0.01)   # стойки рельса по краям
base += BB(-L / 2, L / 2, 20.5, 22.5, Z_RAIL0, Z_RAIL1)                                    # рельс над моторами
motor = Cylinder(MOT_R, MOT_H)

parts = [("k2m_osnovanie", base), ("k2m_shesternya", gear), ("k2m_telezhka", cart), ("k2m_motor", Pos(0, 0, MOT_H / 2) * motor)]
for n, p in parts:
    p = Part() + p
    export_stl(p, os.path.join(OUT, n + ".stl"))

# ================= ПРОВЕРКА: зацепление обеих шестерён по ходу ±24 =================
def gear_at(xg, c):
    a = -math.degrees((c - 0) / RP)              # рейка едет на +x → шестерня под ней крутится по часовой (сверху)
    return Pos(xg, Y_M, Z_G0) * Rot(0, 0, a) * gear


worst = 0.0
engaged = []
for c in [i * 0.5 for i in range(-48, 49)]:
    ct = Pos(c, 0, 0) * cart
    on = []
    for xg in (-X_P, X_P):
        v = (Part() + (gear_at(xg, c) & ct)).volume
        worst = max(worst, v)
        if abs(c - xg) <= RK_HALF - 1.5:
            on.append(xg)
    engaged.append((c, len(on)))
print("наибольшее пересечение шестерён с тележкой: %.3f мм³" % worst)
print("на скольких шестернях рейка: на краях хода %d, посередине %d, минимум %d" %
      (engaged[0][1], dict(engaged)[0.0], min(e for _, e in engaged)))
v = (Part() + (Pos(0, 0, 0) * cart & (Pos(-X_P, Y_M, Z_G0) * Rot(0, 0, 360 / Z / 2) * gear))).volume
print("шестерня на пол-зуба при c = 0: %.2f мм³ (> 0 — в зацеплении)" % v)
for c in (-TRAVEL, 0, TRAVEL):
    v = (Part() + (Pos(c, 0, 0) * cart & base)).volume
    print("тележка × основание при %+d: %.3f мм³" % (c, v))
mot = {sx: Pos(sx * X_P, Y_M, T_BASE + MOT_H / 2) * motor for sx in (1, -1)}
v = (Part() + (mot[1] & mot[-1])).volume
print("мотор × мотор: %.3f мм³ (зазор между ними %.1f мм)" % (v, 2 * X_P - 2 * MOT_R))
for c in (-TRAVEL, -12, 0, 12, TRAVEL):
    for sx in (1, -1):
        for nm, pp in (("тележка", Pos(c, 0, 0) * cart), ("основание", base)):
            v = (Part() + (mot[sx] & pp)).volume
            if v > 0.01:
                print("ПЕРЕСЕЧЕНИЕ мотор %+d × %s при %+d: %.3f" % (sx, nm, c, v))
print("моторы проверены")
