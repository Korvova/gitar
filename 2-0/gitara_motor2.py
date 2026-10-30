# -*- coding: utf-8 -*-
r"""СТЕНД ОДНОГО ПАЛЬЦА «МОТОР В ТЕЛЕЖКЕ» ПОД GB1806 (30.10.2026, Т. Моторчик в тележке, 19.16) — нарисован заранее,
пока моторы едут, по чертежу продавца: Ø22; с корпусом энкодера AS5048A длина 20.5 (корпус + основание статора 7.5,
крутящийся стакан 13); неподвижная сторона — торец корпуса энкодера с 4 × М2 на Ø18 (под 45°, 135°, 225°, 315°) и
двумя головками винтов корпуса под 90°/270°; крутится стакан с торцом 4 × М2 на Ø6 — на него шестерня.
Отличия от стенда 2204 (gitara_motor1.py, стол 101):
  * шестерня m1 z14 (Ø14 по делительной): сила ~0.06 Н·м/А / 7 мм ≈ 870 г на ампер (номинал 0.66 А ≈ 570 г);
    чтобы мотор Ø22 не лёг на пол, рейка поднята на гребень (делительная линия z 10.1); у рейки головка зуба 0.8 m —
    у шестерни z14 нет подреза;
  * мотор прикручен корпусом энкодера к задней стенке 3 винтами М2 (повёрнут на 45°: винты справа, сверху, слева) (урок 2204, 19.9: винты перебили выводы обмоток).
    SCREW_IN — на сколько винт заходит в мотор: ЗАМЕРИТЬ на пришедшем моторе глубину резьбы и поставить сюда;
    толщина стенки под головкой = SCREW_L − SCREW_IN;
  * окна в боках клетки у корпуса энкодера — под разъём AS5048A и провода фаз (мотор можно повернуть на 90°);
  * полозья по ширине коробки и зазор вокруг рейки 1.5 — как на исправленной тележке 102.
Детали (всё без поддержек): m2_osnova, m2_telezhka (печать стоя), m2_kryshka (крышей на стол), m2_shesternya, m2_lozhe.
Запуск: .venv-b123d\Scripts\python gitara_motor2.py
"""
import math
import os
from build123d import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "Print", "Print")

M, Z = 1.0, 14
RP = M * Z / 2                       # 7 — делительный радиус
PA = math.radians(20)
RK_ADD = 0.8 * M                     # головка зуба рейки (укорочена: без подреза шестерни z14)
TRAVEL = 22.0
MOT_R = 11.0                         # Ø22
MOT_FIX = 7.5                        # корпус энкодера + основание статора — неподвижно
MOT_L = 20.5                         # весь мотор с корпусом энкодера
SCREW_L = 4.0                        # длина винтов М2 в задней стенке
SCREW_IN = 1.5                       # !!! на сколько винт заходит в мотор — замерить глубину резьбы и поправить
Z_FL = 2.5                           # верх плиты
Z_FLR0, Z_FLR1 = 4.0, 5.5            # пол тележки под мотором
Z_AX = Z_FLR1 + 0.6 + MOT_R          # 17.1 — ось мотора: низ мотора на 0.6 выше пола
Z_PITCH = Z_AX - RP                  # 10.1 — делительная линия рейки (рейка на гребне)
WALL_T = 3.0
Y_ST = 0.0                           # торец корпуса энкодера — на задней стенке (стенка y −3 … 0)
Y_ROT = Y_ST + MOT_L                 # 20.5 — крутящийся торец стакана
G_T, G_GAP = 4.0, 0.4                # шестерня толщиной 4, от торца стакана 0.4
Y_G0, Y_G1 = Y_ROT + G_GAP, Y_ROT + G_GAP + G_T
HEAD_H = 1.6                         # головки винтов шестерни торчат вперёд (у шестерни нет места под зенковку)
HALF_X = 26.0                        # плита = ширина грифа 52
C = 0.3                              # зазор скольжения
SK_W = 12.0                          # ширина полоза вдоль грифа
WALL_Y0 = Y_ST - WALL_T
Y_FR0 = Y_G1 + HEAD_H + 0.6          # передний полоз и стойка — за головками винтов шестерни
RAIL_YS = (WALL_Y0 - SK_W / 2, Y_FR0 + SK_W / 2)


def BB(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))


def involute_gear_pts(m, z, pa, backlash=0.1, n=12):
    """контур эвольвентной шестерни (2D, ось Z), зубья симметричны относительно оси X"""
    rp = m * z / 2
    rb = rp * math.cos(pa)
    ra = rp + m
    rf = rp - 1.25 * m
    inv = lambda a: math.tan(a) - a
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


def prof_x(pts, x0, x1):
    """профиль (y, z) — вытянуть вдоль X от x0 до x1"""
    return Pos(x0, 0, 0) * Rot(90, 90, 0) * extrude(make_face(Polyline(*(pts + [pts[0]]))), x1 - x0)


# ---------------- шестерня m1 z14: 4 × М2 на Ø6 сквозь, центр Ø3 (головки винтов снаружи) ----------------
_pitch = 360.0 / Z
_off = 270.0 - (round(270.0 / _pitch - 0.5) + 0.5) * _pitch     # впадина ровно внизу (−Y)
gear = Rot(0, 0, _off) * extrude(make_face(Polyline(*involute_gear_pts(M, Z, PA))), G_T)
gear -= Pos(0, 0, G_T / 2) * Cylinder(1.5, G_T + 0.2)
for k in range(4):
    a = math.radians(45 + 90 * k)
    gear -= Pos(3 * math.cos(a), 3 * math.sin(a), G_T / 2) * Cylinder(1.1, G_T + 0.2)

# ---------------- плита: 2 Т-рельса поперёк + рейка m1 на гребне под шестернёй ----------------
base = BB(-HALF_X, HALF_X, RAIL_YS[0] - 8, RAIL_YS[1] + 8, 0, Z_FL)
RAIL_P = [(-2, Z_FL - 0.01), (2, Z_FL - 0.01), (2, 6.0), (4, 8.0), (4, 10.0), (-4, 10.0), (-4, 8.0), (-2, 6.0)]
SLOT_P = [(-2 - C, 3.8), (2 + C, 3.8), (2 + C, 6.0 - C), (4 + C, 8.0 - C), (4 + C, 10.0 + C), (-4 - C, 10.0 + C), (-4 - C, 8.0 - C), (-2 - C, 6.0 - C)]
for ry in RAIL_YS:
    base += Pos(0, ry, 0) * prof_x(RAIL_P, -HALF_X, HALF_X)
P = math.pi * M
rk_y0, rk_y1 = Y_G0 + 0.3, Y_G1 - 0.3
Z_RK_F, Z_RK_A = Z_PITCH - 1.25 * M, Z_PITCH + RK_ADD
base += BB(-HALF_X, HALF_X, rk_y0, rk_y1, Z_FL - 0.01, Z_RK_F)                        # гребень под рейку
kmax = int((HALF_X + P) // P)
tan = math.tan(PA)
for xc in [k * P for k in range(-kmax, kmax + 1)]:                                    # зуб рейки в x = 0; до самого края
    t_half = (P / 2 - 0.1) / 2
    prof = [(xc - t_half - (Z_PITCH - Z_RK_F) * tan, Z_RK_F), (xc - t_half + (Z_RK_A - Z_PITCH) * tan, Z_RK_A),
            (xc + t_half - (Z_RK_A - Z_PITCH) * tan, Z_RK_A), (xc + t_half + (Z_PITCH - Z_RK_F) * tan, Z_RK_F)]
    tooth = extrude(make_face(Polyline(*(prof + [prof[0]]))), rk_y1 - rk_y0)
    base += Pos(0, rk_y1, 0) * Rot(90, 0, 0) * tooth
for sx in (1, -1):                                                                    # срез по краю грифа
    base -= BB(*sorted((sx * HALF_X, sx * (HALF_X + 10))), -50, 80, -1, 30)

# ---------------- тележка-клетка: задняя стенка с 4 × М2 на Ø18, пол, бока с окнами у корпуса энкодера ----------------
G_OR = RP + M                        # 8 — наружный радиус шестерни
CHEEK_X0 = max(MOT_R, G_OR) + 0.6    # 11.6
CHEEK_X1 = CHEEK_X0 + 2.2            # 13.8
SK_HX = CHEEK_X1                     # полозья по ширине коробки (как тележка 102)
Z_SK0, Z_SK1 = 4.0, 13.0             # полоз: низ = низ пола (печать стоя)
Z_TOPF = Z_AX + MOT_R + 0.7          # 28.8 — верх рамы = низ крышки
Y_RK0 = rk_y0 - 1.5                  # пол кончается за 1.5 до рейки
Z_CH_RK = Z_RK_A + 1.5               # бока над рейкой — на 1.5 выше её зубьев
fr = BB(-CHEEK_X1, CHEEK_X1, WALL_Y0, Y_ST, Z_FLR0, Z_TOPF)                         # задняя стенка
fr -= Pos(0, Y_ST - WALL_T / 2, Z_AX) * Rot(90, 0, 0) * Cylinder(4.0, WALL_T + 0.2)   # окно в центре
CB = WALL_T - (SCREW_L - SCREW_IN)                                                   # зенковка под головку снаружи
# мотор повёрнут на 45° от чертежа: винты справа, сверху и слева (снизу дырку закрывает задний полоз — не подлезть),
# головки винтов корпуса энкодера — по диагоналям
for ang in (0, 90, 180):
    a = math.radians(ang)
    x, z = 9 * math.cos(a), Z_AX + 9 * math.sin(a)
    fr -= Pos(x, Y_ST - WALL_T / 2, z) * Rot(90, 0, 0) * Cylinder(1.15, WALL_T + 0.2)
    if CB > 0.05:
        fr -= Pos(x, WALL_Y0 + CB / 2 - 0.05, z) * Rot(90, 0, 0) * Cylinder(2.1, CB + 0.1)
for k in range(4):                                                                    # головки винтов корпуса энкодера
    a = math.radians(45 + 90 * k)
    fr -= Pos(9.4 * math.cos(a), Y_ST - 0.9, Z_AX + 9.4 * math.sin(a)) * Rot(90, 0, 0) * Cylinder(2.4, 2.0)
fr += BB(-CHEEK_X1, CHEEK_X1, WALL_Y0, Y_RK0, Z_FLR0, Z_FLR1)                         # пол под мотором
for sx in (1, -1):
    x0, x1 = sorted((sx * CHEEK_X0, sx * CHEEK_X1))
    fr += BB(x0, x1, WALL_Y0, Y_RK0, Z_FLR0, Z_TOPF)                                    # бока у мотора — от пола
    fr += BB(x0, x1, Y_RK0 - 0.01, RAIL_YS[1] - 4 - C - 0.2, Z_CH_RK, Z_TOPF)           # бока над рейкой
    fr -= BB(x0 - 0.1, x1 + 0.1, Y_ST + 0.5, Y_ST + MOT_FIX + 0.5, Z_AX - 6, Z_AX + 6)  # окно: разъём энкодера, провода
fr += BB(-CHEEK_X1, CHEEK_X1, Y_FR0, Y_FR0 + 3, Z_SK1 - 0.01, Z_TOPF)                 # передняя стойка — на полозе
for ry in RAIL_YS:                                                                      # полозья с Т-пазом
    fr += BB(-SK_HX, SK_HX, ry - SK_W / 2, ry + SK_W / 2, Z_SK0, Z_SK1)
    fr -= Pos(0, ry, 0) * prof_x(SLOT_P, -SK_HX - 0.1, SK_HX + 0.1)
fr -= Pos(0, (Y_G0 + Y_G1) / 2, Z_AX) * Rot(90, 0, 0) * Cylinder(G_OR + 0.6, G_T + 1.2)   # место шестерне
fr -= Pos(0, (Y_ST + Y_ROT) / 2, Z_AX) * Rot(90, 0, 0) * Cylinder(MOT_R + 0.5, MOT_L)       # мотор (зазор 0.5)
SNAP_YS = (3.0, 15.0)
LEDGE_Z0 = Z_TOPF - 5.2
for sx in (1, -1):                                                                      # выступы под защёлки
    for sy in SNAP_YS:
        x0, x1 = sorted((sx * CHEEK_X1, sx * (CHEEK_X1 + 0.6)))
        fr += BB(x0, x1, sy - 3, sy + 3, LEDGE_Z0, LEDGE_Z0 + 1.0)

# крышка на 4 защёлках (как стенд 2204)
LID_T = 2.0
lid = BB(-CHEEK_X1 - 2.6, CHEEK_X1 + 2.6, WALL_Y0, Y_FR0 + 3, 0, LID_T)
HK_X0 = CHEEK_X1 + 0.7
for sx in (1, -1):
    for sy in SNAP_YS:
        x0, x1 = sorted((sx * HK_X0, sx * (HK_X0 + 1.6)))
        lid += BB(x0, x1, sy - 2.8, sy + 2.8, -(5.2 + 1.3), 0.01)
        tx0, tx1 = sorted((sx * (CHEEK_X1 + 0.05), sx * HK_X0))
        lid += BB(tx0, tx1, sy - 2.8, sy + 2.8, -(5.2 + 1.2), -(5.2 + 0.1))
lid = Pos(0, 0, Z_TOPF) * lid

# ложе: на крышку (клеить)
lz = BB(-12, 12, -12, 12, 0, 2.0)
for sx in (1, -1):
    lz += BB(sx * 12 - (1.6 if sx > 0 else 0), sx * 12 + (0 if sx > 0 else 1.6), -12, 12, 2.0, 7.0)
Z_ROOF1 = Z_TOPF + LID_T

# мотор для проверки: корпус энкодера + стакан одним цилиндром; головки винтов шестерни — кольцом r 3 ± 1.9
motor = Pos(0, (Y_ST + Y_ROT) / 2, Z_AX) * Rot(90, 0, 0) * Cylinder(MOT_R, MOT_L)
heads = Pos(0, Y_G1 + HEAD_H / 2, Z_AX) * Rot(90, 0, 0) * Cylinder(4.9, HEAD_H)

parts = [("m2_osnova", base), ("m2_telezhka", fr), ("m2_kryshka", lid), ("m2_shesternya", gear), ("m2_lozhe", lz),
         ("m2_motor_proverka", motor + heads)]
for n, p in parts:
    p = Part() + p
    bb = p.bounding_box()
    print("%s: %.1f x %.1f x %.1f, solids %d" % (n, bb.size.X, bb.size.Y, bb.size.Z, len(p.solids())))
    export_stl(p, os.path.join(OUT, n + ".stl"))

# ================= ПРОВЕРКА ЗАЦЕПЛЕНИЯ: шестерня катится по рейке ±22 =================
for sign in (1, -1):
    worst = 0.0
    for x in (-22, -14.7, -7.3, -3.1, 0, 0.6, 1.1, 2.2, 5.5, 11, 18.3, 22):
        g = Pos(x, Y_G1, Z_AX) * Rot(0, sign * math.degrees(x / RP), 0) * Rot(90, 0, 0) * gear
        worst = max(worst, (Part() + (g & base)).volume)
    print("знак %+d: наибольшее пересечение шестерни с рейкой %.3f мм³" % (sign, worst))

# ================= ПРОВЕРКА ТЕЛЕЖКИ: ход ±22 =================
from clearance import Assembly
S = lambda n: os.path.join(OUT, n + ".stl")
export_stl(Part() + Pos(0, (Y_G0 + Y_G1) / 2, Z_AX) * Rot(90, 0, 0) * Cylinder(RP + M, G_T), S("m2_shesternya_obem"))
asm = Assembly()
asm.add("base", S("m2_osnova"))
clear, touch = [], []
for x in (-22, -11, 0, 11, 22):
    t, mo, g, l = "tel%d" % x, "mot%d" % x, "g%d" % x, "lid%d" % x
    asm.add(t, S("m2_telezhka"), loc=(x, 0, 0))
    asm.add(mo, S("m2_motor_proverka"), loc=(x, 0, 0))
    asm.add(g, S("m2_shesternya_obem"), loc=(x, 0, 0))
    asm.add(l, S("m2_kryshka"), loc=(x, 0, 0))
    clear += [(t, "base", 0.29), (mo, "base", 0.5), (g, t, 0.5), (g, l, 0.5), (mo, l, 0.5), (l, "base", 0.5)]
    touch += [(mo, t), (l, t), (g, mo)]
asm.check(clearances=clear, touching=touch, verbose=False)
print("стенд GB1806: шестерня m1 z%d (%.0f г/А), ось мотора %.1f, рейка %.1f, верх тележки %.1f, вдоль грифа %.1f…%.1f; "
      "винты М2×%.0f заходят в мотор на %.1f" % (Z, 0.06 / (RP / 1000) / 9.81 * 1000, Z_AX, Z_PITCH, Z_ROOF1, WALL_Y0,
                                                  Y_FR0 + 3, SCREW_L, SCREW_IN))
