# -*- coding: utf-8 -*-
r"""СТЕНД ОДНОГО ПАЛЬЦА «МОТОР В ТЕЛЕЖКЕ» (29.10.2026, Т. Моторчик в тележке, 19.16) — проба на гимбале 2204 260kV.
Мотор владельца: Ø27.7 × 13, неподвижна сторона с проводами (плоская, без дырок — приклеить), крутится сторона
с 4 × М2 на Ø12. Мотор стоит на ребре (ось вдоль грифа), на крутящейся стороне шестерня m1 z26 (Ø26 по делительной):
29.10 (владелец) — больше z20, чтобы мотор целиком был выше рейки и сидел в клетке с полом; дырки 4 × М2 на Ø12 внутри впадин.
Шестерня катится по рейке m1 поперёк грифа; тележка ездит ±22 на двух Т-рельсах (рельсы ещё и не дают шестерне
отжаться вверх — 19.5). Сила: ~37 мН·м/А / 13 мм ≈ 290 г на ампер.
Детали (всё без поддержек): m1_osnova (плита + 2 рельса + рейка), m1_telezhka (рама-клетка, печать стоя),
m1_kryshka (на 4 защёлках, печать крышей на стол), m1_shesternya (плашмя), m1_lozhe (клеить на крышку).
Запуск: .venv-b123d\Scripts\python gitara_motor1.py
"""
import math
import os
import numpy as np
from build123d import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "Print", "Print")

M, Z = 1.0, 26                       # 29.10 (владелец): шестерня больше — мотор целиком выше рейки, в клетке с полом
RP = M * Z / 2                       # 13 — делительный радиус
PA = math.radians(20)
TRAVEL = 22.0
MOT_D, MOT_L = 27.7, 13.0
MOT_R = MOT_D / 2
Z_FL = 2.5                           # верх плиты
Z_PITCH = 7.0                        # делительная линия рейки
Z_AX = Z_PITCH + RP                  # 20 — ось мотора (низ мотора 6.15 — выше полозьев)
Y_ST = 1.0                           # неподвижный торец мотора — на клеевом кольце (стенка y −3 … 0, кольцо 0 … 1)
Y_BELL = Y_ST + MOT_L                # крутящийся торец
G_T, G_GAP = 5.0, 0.4                # шестерня толщиной 5, от торца мотора 0.4
Y_G0, Y_G1 = Y_BELL + G_GAP, Y_BELL + G_GAP + G_T
RAIL_YS = (-9.0, 26.5)               # оси рельсов вдоль грифа (за стенкой тележки и за шестерней)
HALF_X = 26.0                        # 29.10 (владелец): плита = ширина грифа 52, тележка на краях выезжает за грань наполовину
C = 0.3                              # зазор скольжения


def BB(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))


def involute_gear_pts(m, z, pa, backlash=0.1, n=12):
    """контур эвольвентной шестерни (2D, ось Z), зубья симметричны относительно оси X"""
    rp = m * z / 2
    rb = rp * math.cos(pa)
    ra = rp + m
    rf = rp - 1.25 * m
    inv = lambda a: math.tan(a) - a
    # половина угловой толщины зуба на делительной окружности (с люфтом)
    half_t = (math.pi * m / 2 - backlash) / (2 * rp)
    pts = []
    for i in range(z):
        c = 2 * math.pi * i / z
        flank = []
        for k in range(n + 1):
            r = rb + (ra - rb) * k / n if rb > rf else rf + (ra - rf) * k / n
            r = max(r, rb)
            a = math.acos(min(rb / r, 1.0))
            th = half_t + inv(pa) - inv(a)
            flank.append((r, th))
        tooth = [(rf, -(half_t + inv(pa) + 0.02))] + [(r, -th) for r, th in flank] + [(r, th) for r, th in reversed(flank)] + [(rf, half_t + inv(pa) + 0.02)]
        for r, th in tooth:
            pts.append((r * math.cos(c + th), r * math.sin(c + th)))
    pts.append(pts[0])
    return pts


# ---------------- шестерня m1 z20: 4 × М2 на Ø12 (под головку — зенковка Ø4.2 × 1.8), центр Ø8 ----------------
_pitch = 360.0 / Z
_off = 270.0 - (round(270.0 / _pitch - 0.5) + 0.5) * _pitch     # впадина ровно внизу (−Y)
gear = Rot(0, 0, _off) * extrude(make_face(Polyline(*involute_gear_pts(M, Z, PA))), G_T)   # впадина на −Y (низ)
gear -= Pos(0, 0, G_T / 2) * Cylinder(4.0, G_T + 0.2)
for k in range(4):
    a = math.radians(45 + 90 * k)
    x, y = 6 * math.cos(a), 6 * math.sin(a)
    gear -= Pos(x, y, G_T / 2) * Cylinder(1.1, G_T + 0.2)
    gear -= Pos(x, y, G_T - 0.9 + 0.01) * Cylinder(2.1, 1.82)

# ---------------- плита: 2 Т-рельса поперёк + рейка m1 под шестернёй ----------------
base = BB(-HALF_X, HALF_X, RAIL_YS[0] - 8, RAIL_YS[1] + 8, 0, Z_FL)
def prof_x(pts, x0, x1):
    """профиль (y, z) — вытянуть вдоль X от x0 до x1"""
    return Pos(x0, 0, 0) * Rot(90, 90, 0) * extrude(make_face(Polyline(*(pts + [pts[0]]))), x1 - x0)


# Т-рельс с фаской 45° под шляпкой — печатается без поддержек
RAIL_P = [(-2, Z_FL - 0.01), (2, Z_FL - 0.01), (2, 6.0), (4, 8.0), (4, 10.0), (-4, 10.0), (-4, 8.0), (-2, 6.0)]
SLOT_P = [(-2 - C, 3.8), (2 + C, 3.8), (2 + C, 6.0 - C), (4 + C, 8.0 - C), (4 + C, 10.0 + C), (-4 - C, 10.0 + C), (-4 - C, 8.0 - C), (-2 - C, 6.0 - C)]
for ry in RAIL_YS:
    base += Pos(0, ry, 0) * prof_x(RAIL_P, -HALF_X, HALF_X)
# рейка: зубья вверх, делительная линия z 7; шаг π·m, профиль — трапеция 20°, люфт 0.1 по толщине
P = math.pi * M
rk_y0, rk_y1 = Y_G0 + 0.3, Y_G1 - 0.3
base += BB(-HALF_X, HALF_X, rk_y0, rk_y1, Z_FL, Z_PITCH - 1.25 * M)
kmax = int((HALF_X + P) // P)
xs = [k * P for k in range(-kmax, kmax + 1)]                                    # зуб рейки в x = 0; зубья до самого края
for xc in xs:
    t_half = (P / 2 - 0.1) / 2                                           # полтолщины зуба на делительной
    za, zf = Z_PITCH + M, Z_PITCH - 1.25 * M
    tan = math.tan(PA)
    prof = [(xc - t_half - (Z_PITCH - zf) * tan, zf), (xc - t_half + (za - Z_PITCH) * tan, za),
            (xc + t_half - (za - Z_PITCH) * tan, za), (xc + t_half + (Z_PITCH - zf) * tan, zf)]
    tooth = extrude(make_face(Polyline(*(prof + [prof[0]]))), rk_y1 - rk_y0)      # профиль (x, z) в XY, толщина по Z
    base += Pos(0, rk_y1, 0) * Rot(90, 0, 0) * tooth                                   # Z -> −Y, Y -> Z

for sx in (1, -1):                                                                    # срез по краю грифа
    base -= BB(*sorted((sx * HALF_X, sx * (HALF_X + 10))), -50, 60, -1, 20)

# ---------------- тележка-клетка (29.10, владелец): рама с полом под мотором, задней стенкой (клеевое кольцо Ø20,
# окно под провода вниз) и боками; сверху крышка на 4 защёлках — мотор с шестернёй вставляется сверху ----------------
SK_HX = 16.8                         # = CHEEK_X1; 29.10 (владелец): полозья по ширине коробки — меньше перекос и закусывание
WALL_Y0 = Y_ST - 4.0                 # задняя стенка y −3 … 0
Z_SK0 = 4.0                          # низ полозьев = низ пола: рама печатается стоя, всем низом на столе
Z_FLR0, Z_FLR1 = 4.0, 5.5            # пол под мотором (низ мотора 6.15)
G_OR = RP + M                        # 14 — наружный радиус шестерни
CHEEK_X0 = max(MOT_R, G_OR) + 0.6    # 14.6
CHEEK_X1 = CHEEK_X0 + 2.2            # 16.8
Z_TOPF = Z_AX + G_OR + 0.7           # 34.7 — верх рамы = низ крышки
Y_FR0 = Y_G1 + 1.0                   # передняя стойка за шестернёй
Y_RK0 = Y_G0 - 0.2                   # от сюда к груди — над рейкой
fr = BB(-CHEEK_X1, CHEEK_X1, WALL_Y0, Y_ST - 1, Z_FLR0, Z_TOPF)                     # задняя стенка
fr -= Pos(0, Y_ST - 2.5, Z_AX) * Rot(90, 0, 0) * Cylinder(5.0, 3.2)                  # окно под центральную трубку
fr -= BB(-10, 10, WALL_Y0 - 0.1, Y_ST - 0.9, Z_FLR1, Z_AX - 10.5)                     # окно под провода вниз (под кольцом)
ring = Pos(0, Y_ST - 0.5, Z_AX) * Rot(90, 0, 0) * (Cylinder(10.0, 1.0) - Cylinder(5.0, 1.2))
fr += ring                                                                              # клеевое кольцо Ø20 (обод мотора свободен)
# 29.10 (владелец): на стороне с проводами тоже М2 — 2 винта по диагонали вместо клея. Дырки не мерили — делаю
# радиальные прорези под 45° и 225° от r 5.5 до 9.5 (подходит расстояние между диагональными дырками 11…19 мм):
# мотор повернуть так, чтобы его дырки встали в прорези; снаружи стенки — паз под головку М2
for ang in (45, 225):
    slot = BB(5.5, 9.5, Y_ST - 4.2, Y_ST + 0.2, -1.15, 1.15) + Pos(5.5, Y_ST - 2.0, 0) * Rot(90, 0, 0) * Cylinder(1.15, 4.4)         + Pos(9.5, Y_ST - 2.0, 0) * Rot(90, 0, 0) * Cylinder(1.15, 4.4)
    head = BB(5.5, 9.5, Y_ST - 4.2, Y_ST - 2.5, -2.1, 2.1) + Pos(5.5, Y_ST - 3.35, 0) * Rot(90, 0, 0) * Cylinder(2.1, 1.7)         + Pos(9.5, Y_ST - 3.35, 0) * Rot(90, 0, 0) * Cylinder(2.1, 1.7)
    fr -= Pos(0, 0, Z_AX) * Rot(0, -ang, 0) * (slot + head)
fr += BB(-CHEEK_X1, CHEEK_X1, WALL_Y0, Y_RK0, Z_FLR0, Z_FLR1)                         # пол под мотором (до рейки)
for sx in (1, -1):
    x0, x1 = sorted((sx * CHEEK_X0, sx * CHEEK_X1))
    fr += BB(x0, x1, WALL_Y0, Y_RK0, Z_FLR0, Z_TOPF)                                    # бока у мотора — от пола
    fr += BB(x0, x1, Y_RK0 - 0.01, RAIL_YS[1] - 4 - C - 0.2, 8.5, Z_TOPF)             # бока над рейкой — выше её зубьев, до шляпки рельса
fr += BB(-CHEEK_X1, CHEEK_X1, Y_FR0, Y_FR0 + 3, 13.0 - 0.01, Z_TOPF)                  # передняя стойка — на полозе
for ry in RAIL_YS:                                                                      # полозья с Т-пазом
    fr += BB(-SK_HX, SK_HX, ry - 6, ry + 6, Z_SK0, 13.0)
    fr -= Pos(0, ry, 0) * prof_x(SLOT_P, -SK_HX - 0.1, SK_HX + 0.1)
fr -= Pos(0, (Y_G0 + Y_G1) / 2, Z_AX) * Rot(90, 0, 0) * Cylinder(G_OR + 0.6, G_T + 1.2)   # место шестерне
fr -= Pos(0, (Y_ST + Y_BELL) / 2, Z_AX) * Rot(90, 0, 0) * Cylinder(MOT_R + 0.5, MOT_L + 0.2)   # мотор (зазор 0.5)
# выступы под защёлки — снаружи боков, по 2 на бок
SNAP_YS = (2.0, 15.0)
LEDGE_Z0 = Z_TOPF - 5.2
for sx in (1, -1):
    for sy in SNAP_YS:
        x0, x1 = sorted((sx * CHEEK_X1, sx * (CHEEK_X1 + 0.6)))
        fr += BB(x0, x1, sy - 3, sy + 3, LEDGE_Z0, LEDGE_Z0 + 1.0)

# крышка: плита на верх рамы, 4 крючка вниз снаружи боков с зубом под выступ (печать крышей на стол, крючки вверх)
LID_T = 2.0
lid = BB(-CHEEK_X1 - 2.6, CHEEK_X1 + 2.6, WALL_Y0, Y_FR0 + 3, 0, LID_T)
HK_X0 = CHEEK_X1 + 0.7                                  # внутренняя грань крючка (выступ 0.6 + 0.1)
for sx in (1, -1):
    for sy in SNAP_YS:
        x0, x1 = sorted((sx * HK_X0, sx * (HK_X0 + 1.6)))
        lid += BB(x0, x1, sy - 2.8, sy + 2.8, -(5.2 + 1.3), 0.01)                        # язычок вниз
        # зуб внутрь под выступ: верх зуба (защёлка) на 0.1 ниже выступа, снизу скос для надевания
        tx0, tx1 = sorted((sx * (CHEEK_X1 + 0.05), sx * HK_X0))
        lid += BB(tx0, tx1, sy - 2.8, sy + 2.8, -(5.2 + 1.2), -(5.2 + 0.1))
lid = Pos(0, 0, Z_TOPF) * lid

# ---------------- ложе: на крышку (клеить) ----------------
lz = BB(-12, 12, -12, 12, 0, 2.0)
for sx in (1, -1):
    lz += BB(sx * 12 - (1.6 if sx > 0 else 0), sx * 12 + (0 if sx > 0 else 1.6), -12, 12, 2.0, 7.0)
tel = fr
Z_ROOF1 = Z_TOPF + LID_T

# мотор для проверки
motor = Pos(0, (Y_ST + Y_BELL) / 2, Z_AX) * Rot(90, 0, 0) * Cylinder(MOT_R, MOT_L)

parts = [("m1_osnova", base), ("m1_telezhka", tel), ("m1_kryshka", lid), ("m1_shesternya", gear), ("m1_lozhe", lz), ("m1_motor_proverka", motor)]
for n, p in parts:
    p = Part() + p
    bb = p.bounding_box()
    print("%s: %.1f x %.1f x %.1f, solids %d" % (n, bb.size.X, bb.size.Y, bb.size.Z, len(p.solids())))
    export_stl(p, os.path.join(OUT, n + ".stl"))

# ================= ПРОВЕРКА ЗАЦЕПЛЕНИЯ: шестерня катится по рейке ±22 =================
def gear_at(x, sign):
    a = sign * math.degrees(x / RP)
    g = Pos(x, Y_G1, Z_AX) * Rot(0, a, 0) * Rot(90, 0, 0) * gear      # ось шестерни вдоль Y, торец у мотора — Y_G0
    return g


rack = base
for sign in (1, -1):
    worst = 0.0
    for x in (-22, -14.7, -7.3, -3.1, 0, 2.2, 5.5, 11, 18.3, 22):
        v = (Part() + (gear_at(x, sign) & rack)).volume
        worst = max(worst, v)
    print("знак %+d: наибольшее пересечение шестерни с рейкой %.3f мм³" % (sign, worst))

# ================= ПРОВЕРКА ТЕЛЕЖКИ: ход ±22 =================
from clearance import Assembly
S = lambda n: os.path.join(OUT, n + ".stl")
export_stl(Part() + Pos(0, (Y_G0 + Y_G1) / 2, Z_AX) * Rot(90, 0, 0) * Cylinder(RP + M, G_T), S("m1_shesternya_obem"))
asm = Assembly()
asm.add("base", S("m1_osnova"))
clear, touch = [], []
for x in (-22, -11, 0, 11, 22):
    t, mo, g = "tel%d" % x, "mot%d" % x, "g%d" % x
    asm.add(t, S("m1_telezhka"), loc=(x, 0, 0))
    asm.add(mo, S("m1_motor_proverka"), loc=(x, 0, 0))
    asm.add(g, S("m1_shesternya_obem"), loc=(x, 0, 0))
    asm.add("lid%d" % x, S("m1_kryshka"), loc=(x, 0, 0))
    clear += [(t, "base", 0.29), (mo, "base", 0.5), (g, t, 0.5), (g, mo, 0.3), (g, "lid%d" % x, 0.5), (mo, "lid%d" % x, 0.5),
              ("lid%d" % x, "base", 0.5)]
    touch += [(mo, t), ("lid%d" % x, t)]
asm.check(clearances=clear, touching=touch, verbose=False)
print("стенд «мотор в тележке»: шестерня m1 z%d, рейка ±%.0f, ось мотора %.0f над столом, верх тележки %.1f" % (Z, HALF_X, Z_AX, Z_ROOF1))
