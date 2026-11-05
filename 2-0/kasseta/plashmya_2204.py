# -*- coding: utf-8 -*-
r"""МОТОР ПЛАШМЯ В ТЕЛЕЖКЕ — проба на гимбале 2204 (05.11.2026, идея владельца). Мотор лежит осью вверх, сторона с
проводами вниз — на пластине тележки. Сквозь крутящуюся трубку мотора (Ø3, сквозная) — винт М3: сверху головка в крышке,
крышка на крутящемся торце (4 × М2 на Ø12); снизу, под тележкой, на винт вкручена шестерня m1 z12 (дырка Ø2.6 под
саморез М3) — головку и шестерню на клей. Шестерня катится по рейке поперёк куска грифа; тележка ездит по двум
рельсам-ласточкиным хвостам (как в телескопе); ложе — над мотором на стойках (крышка крутится). Ход ±24.
Сила: 37 мН·м/А ÷ 6 мм ≈ 630 г на ампер. Детали без поддержек: pl_grif (дном на стол), pl_telezhka (вверх ногами),
pl_kryshka, pl_shesternya, pl_lozhe (пластиной на стол, стойки вверх).
Запуск: ..\.venv-b123d\Scripts\python plashmya_2204.py
"""
import math
import os
from build123d import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "Print", "Print")

MOT_D, MOT_H = 27.8, 12.23
M, Z, PA = 1.0, 12, math.radians(20)
RP = M * Z / 2                         # 6
ADD_G, ADD_R, DED = 0.85, 0.7, 1.25
PITCH = math.pi * M
TRAVEL = 24.0
G_T = 5.0
Z_FL = 3.0                             # верх куска грифа
Z_G0, Z_G1 = Z_FL + 0.6, Z_FL + 0.6 + G_T          # шестерня 3.6 … 8.6
Z_C0, Z_C1 = Z_G1 + 0.4, Z_G1 + 0.4 + 3.0          # пластина тележки 9.0 … 12.0
Z_M0, Z_M1 = Z_C1, Z_C1 + MOT_H                    # мотор 12.0 … 24.23
Z_K1 = Z_M1 + 3.0                                  # крышка 24.23 … 27.23
Y_RK = -RP                                         # делительная рейки (ось шестерни y = 0)
Y_RAIL = 17.0                                      # рельсы y ±17 — снаружи мотора (R 13.9)
RB, RT, RH = 3.0, 4.2, 1.2                         # гребень: низ, верх, высота
C_G = 0.15
GX0, GX1 = -30.0, 30.0                             # кусок грифа поперёк (с запасом под рельсы)


def BB(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))


def prof_x(pts, x0, x1):
    return Pos(x0, 0, 0) * Rot(90, 90, 0) * extrude(make_face(Polyline(*(pts + [pts[0]]))), x1 - x0)


def gear_pts(m, z, pa, backlash=0.1, n=12, add=1.0):
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


# ---------------- шестерня: впадина на −Y (к рейке), дырка Ø2.6 под винт М3 ----------------
_p = 360.0 / Z
OFF = 270.0 - (round(270.0 / _p - 0.5) + 0.5) * _p
gear = Rot(0, 0, OFF) * extrude(make_face(Polyline(*gear_pts(M, Z, PA, add=ADD_G))), G_T) - Cylinder(1.3, 50)

# ---------------- кусок грифа: плита, рейка поперёк, два рельса ----------------
grif = BB(GX0, GX1, -21, 21, 0, Z_FL)
tn, th = math.tan(PA), (PITCH / 2 - 0.1) / 2
grif += BB(GX0, GX1, Y_RK - DED - 2.0, Y_RK - DED + 0.01, Z_FL - 0.01, Z_G1)          # спинка рейки
for k in range(-int(GX1 // PITCH) - 1, int(GX1 // PITCH) + 2):
    xc = k * PITCH
    pr = [(xc - th - DED * tn, Y_RK - DED), (xc - th + ADD_R * tn, Y_RK + ADD_R), (xc + th - ADD_R * tn, Y_RK + ADD_R),
          (xc + th + DED * tn, Y_RK - DED)]
    grif += Pos(0, 0, Z_FL - 0.01) * extrude(make_face(Polyline(*(pr + [pr[0]]))), Z_G1 - Z_FL + 0.01)
grif = grif & BB(GX0, GX1, -30, 30, -1, 50)                                              # зубья обрезать по краю
for sy in (1, -1):
    y = sy * Y_RAIL
    grif += BB(GX0, GX1, y - RB / 2, y + RB / 2, Z_FL - 0.01, Z_C0 + 0.01)               # ножка рельса
    grif += prof_x([(y - RB / 2, Z_C0), (y + RB / 2, Z_C0), (y + RT / 2, Z_C0 + RH), (y - RT / 2, Z_C0 + RH)], GX0, GX1)

# ---------------- тележка: пластина под мотор, пазы под рельсы, окно под винт, прорези под винты статора ----------------
CX = 16.0
ct = BB(-CX, CX, -21, 21, Z_C0, Z_C1)
for sy in (1, -1):
    y = sy * Y_RAIL
    ct -= prof_x([(y - RB / 2 - C_G, Z_C0 - 0.01), (y + RB / 2 + C_G, Z_C0 - 0.01), (y + RT / 2 + C_G, Z_C0 + RH + 0.1),
                  (y - RT / 2 - C_G, Z_C0 + RH + 0.1)], -CX - 1, CX + 1)
ct -= Pos(0, 0, (Z_C0 + Z_C1) / 2) * Cylinder(3.0, Z_C1 - Z_C0 + 0.2)                   # окно Ø6 под винт и трубку
for ang in (45, 135, 225, 315):                                                         # прорези r 5.5 … 9.5 под М2 статора
    a = math.radians(ang)
    for r in [5.5 + 0.5 * k for k in range(9)]:
        ct -= Pos(r * math.cos(a), r * math.sin(a), (Z_C0 + Z_C1) / 2) * Cylinder(1.15, Z_C1 - Z_C0 + 0.2)
for sx in (1, -1):                                                                      # гнёзда стоек ложа
    for sy in (1, -1):
        ct -= Pos(sx * 13.0, sy * 12.0, Z_C1 - 1.0) * Cylinder(1.6, 2.1)
# карман под пайку и провода: площадки у края донышка МЕЖДУ двумя винтами (фото 05.11) — мотор ставить проводами к +Y,
# провода выходят за край мотора (R 13.9) и лежат на пластине; карман не доходит до паза рельса (y 14.75)
Y_PR0, Y_PR1 = 8.0, 14.0           # большое окно насквозь (просьба владельца): от шестерни (R 6.85) до паза рельса (14.75),
ct -= BB(-10.5, 10.5, Y_PR0, Y_PR1, Z_C0 - 0.1, Z_C1 + 0.1)                             # по x — между гнёздами стоек ложа
grif -= BB(-TRAVEL - 3.0, TRAVEL + 3.0, Y_PR0 - 0.5, Y_PR1 + 0.5, -0.1, Z_FL + 0.1)    # щель в грифе вдоль хода — провода ходят с тележкой

# ---------------- крышка на крутящийся торец: 4 × М2 на Ø12, в центре винт М3 (головка — в гнезде, на клей) ----------------
kr = Cylinder(9.0, 3.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
kr -= Cylinder(1.65, 10)
kr -= Pos(0, 0, 3.0 - 2.0) * Cylinder(3.0, 2.1, align=(Align.CENTER, Align.CENTER, Align.MIN))                # головка М3
for a in (0, 90, 180, 270):
    x, y = 6 * math.cos(math.radians(a + 45)), 6 * math.sin(math.radians(a + 45))
    kr -= Pos(x, y, 0) * Cylinder(1.1, 10)
    kr -= Pos(x, y, 3.0 - 1.5) * Cylinder(2.0, 1.6, align=(Align.CENTER, Align.CENTER, Align.MIN))          # головки М2

# ---------------- ложе: ровная площадка 26 × 30 над мотором на 4 стойках (печать площадкой на стол, стойки вверх) ----------------
Z_L0 = Z_K1 + 0.8                                                                       # над крышкой и головкой винта
lz = BB(-14.6, 14.6, -15, 15, Z_L0, Z_L0 + 2.0)                                   # шире — стойки не торчат за край
for sx in (1, -1):
    for sy in (1, -1):
        lz += Pos(sx * 13.0, sy * 12.0, (Z_C1 - 1.0 + Z_L0) / 2) * Cylinder(1.5, Z_L0 - Z_C1 + 1.0 + 0.01)

parts = [("pl_grif", grif), ("pl_telezhka", ct), ("pl_kryshka", kr), ("pl_shesternya", gear), ("pl_lozhe", lz)]
for n, p in parts:
    p = Part() + p
    bb = p.bounding_box()
    print("%s: %.1f x %.1f x %.1f, solids %d" % (n, bb.size.X, bb.size.Y, bb.size.Z, len(p.solids())))
    export_stl(p, os.path.join(OUT, n + ".stl"))

# ================= ПРОВЕРКА: ход ±24 =================
motor = Pos(0, 0, Z_M0 + MOT_H / 2) * Cylinder(MOT_D / 2, MOT_H)
vint = Pos(0, 0, (Z_G0 + Z_K1) / 2) * Cylinder(1.45, Z_K1 - Z_G0)
bad = 0
for c in (-24, -17.3, -9.1, -2.4, 0, 1.3, 7.7, 15.2, 24):
    a = -math.degrees(c / RP)
    g = Pos(c, 0, Z_G0) * Rot(0, 0, a) * gear
    pl = {"тележка": Pos(c, 0, 0) * ct, "мотор": Pos(c, 0, 0) * motor, "крышка": Pos(c, 0, Z_M1) * Rot(0, 0, a) * kr,
          "ложе": Pos(c, 0, 0) * lz, "шестерня": g}
    for nm, p in pl.items():
        v = (Part() + (p & grif)).volume
        if v > 0.01:
            bad += 1
            print("ПЕРЕСЕЧЕНИЕ %s × гриф: %.3f при c = %+.1f" % (nm, v, c))
    for p1, p2 in (("шестерня", "тележка"), ("крышка", "ложе"), ("мотор", "ложе")):
        v = (Part() + (pl[p1] & pl[p2])).volume
        if v > 0.01:
            bad += 1
            print("ПЕРЕСЕЧЕНИЕ %s × %s: %.3f при c = %+.1f" % (p1, p2, v, c))
g_off = Pos(0, 0, Z_G0) * Rot(0, 0, 15) * gear
print("шестерня на пол-зуба × рейка: %.2f мм³ (> 0 — в зацеплении)" % (Part() + (g_off & grif)).volume)
print("винт × шестерня (саморез в Ø2.6): %.2f; винт × тележка: %.3f" % ((Part() + (vint & Pos(0, 0, Z_G0) * gear)).volume, (Part() + (vint & ct)).volume))
print("мотор плашмя: %s; высота до ложа %.1f мм" % ("чисто" if not bad else "ЕСТЬ ПЕРЕСЕЧЕНИЯ: %d" % bad, Z_L0 + 2.0))
