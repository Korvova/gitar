# -*- coding: utf-8 -*-
r"""РОЛЬГАНГ под гимбал 2204 (04.11.2026, идея владельца) — вместо телескопа: меньше мелких деталей, зубья модуль 1.
Три верхние шестерни z12 в ряд через 5 шагов рейки (5π = 15.71): средняя — на моторе (через фланец, как кассета 2204),
крайние — от средней через промежуточные z10 в НИЖНЕМ слое (они под рейкой, рейка в верхнем слое их не касается).
Крайние шестерни двухэтажные: верх (z12) — к рейке, низ (z12) — к промежуточной, повёрнут на подобранный угол (фаза
сходится точно, без люфта). Тележка 20 мм, рейка 20: на краях хода на одной шестерне, у переходов — на двух.
Все шестерни на штырьках Ø3 из «палубы» над мотором; сверху их держат крышка (над верхними) и рельс тележки (над
промежуточными) — отдельная деталь «верхняя рамка», клеится на стенки после того, как шестерни надеты.
Головка зуба 0.85 m у шестерён и 0.7 m у рейки — без подреза малых шестерён. Всё печатается без поддержек.
Детали: rg_osnovanie_niz + rg_osnovanie_verh (на клей), rg_kryshka, rg_rels, rg_shesternya_centr (в шестигранник kas2204_flanec), крайние прав/лев,
rg_promezh ×2, rg_telezhka. Запуск: ..\.venv-b123d\Scripts\python rolgang_2204.py
"""
import math
import os
from build123d import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "Print", "Print")

M, PA = 1.0, math.radians(20)
ZP, ZI = 12, 10
RP, RI = M * ZP / 2, M * ZI / 2           # 6, 5
ADD_G, ADD_R, DED = 0.85, 0.7, 1.25
PITCH = math.pi * M
S = 5 * PITCH                              # 15.71
RK_HALF = 10.0                             # тележка и рейка 20
T = 3.0
# мотор и фланец — как kasseta_2204.py
MOT_D, MOT_H, T_BASE = 27.8, 12.23, 1.2
Z_MTOP = T_BASE + MOT_H                    # 13.43
ZW = 16.85                                 # низ палубы и стенок над мотором
FL_COLLAR = ZW - 0.05                      # верх втулки фланца 16.8
HEX = 5.0
# слои
Z_D1 = ZW + 1.5                            # верх палубы 18.35
Z_L0, Z_L1 = Z_D1 + 0.1, Z_D1 + 0.1 + T    # нижний слой 18.45 … 21.45
Z_U0, Z_U1 = Z_L1 + 0.1, Z_L1 + 0.1 + T    # верхний 21.55 … 24.55
Z_CV0, Z_CV1 = Z_U1 + 0.1, Z_U1 + 0.6      # крышка над верхними шестернями 24.65 … 25.15
Z_C0, Z_C1 = Z_CV1 + 0.1, Z_CV1 + 2.1      # тележка 25.25 … 27.25
# раскладка по Y (вдоль грифа)
W, L = 24.0, 50.0
Y_P = 8.8                                  # ось ряда шестерён = ось мотора
D_I = RP + RI                              # 11
DY_I = math.sqrt(D_I ** 2 - (S / 2) ** 2)  # 7.70 — промежуточные к рейке (+Y), в нижнем слое
Y_I = Y_P + DY_I
Y_RK = Y_P + RP                            # делительная рейки 14.8
RK_BACK = Y_RK + DED + 1.5                 # 17.55
RAIL_Y0, RAIL_Y1 = 19.4, 21.6              # шляпка рельса
STEM_Y0, STEM_Y1 = 20.0, 21.0


def BB(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))


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


def gear(z, h):
    return extrude(make_face(Polyline(*gear_pts(M, z, PA, add=ADD_G))), h)


_p = 360.0 / ZP
OFF_P = 90.0 - (round(90.0 / _p - 0.5) + 0.5) * _p        # впадина верхней шестерни на +Y (к рейке) при c = 0
G12 = gear(ZP, T)
G10 = gear(ZI, T)


# ---------------- фазы: промежуточная под среднюю, низ крайней под промежуточную (подбор перебором) ----------------
def a_pin(c):            # угол верхних шестерён, град (рейка на +x → по часовой)
    return OFF_P - math.degrees(c / RP)


def a_idl(ph, c):        # угол промежуточной
    return ph + math.degrees(c / RI)


def best_phase(fixed, moving_at, pitch, steps=36, cs=(0.0, 0.5, 1.1, 1.7)):
    """перебор фазы: грубо, потом точнее вокруг лучшей"""
    def score(ph, lim):
        w = 0.0
        for c in cs:
            w = max(w, (Part() + (fixed(c) & moving_at(ph, c))).volume)
            if w > lim:
                break
        return w
    best = (9.0, 0.0)
    for k in range(steps):
        ph = k * pitch / steps
        best = min(best, (score(ph, best[0]), ph))
    step = pitch / steps
    for k in range(-10, 11):
        ph = best[1] + k * step / 10
        best = min(best, (score(ph, best[0]), ph))
    return best


PH_I, OFF_K = {}, {}
for sx in (1, -1):
    w1, PH_I[sx] = best_phase(lambda c: Pos(0, Y_P, 0) * Rot(0, 0, a_pin(c)) * G12,
                              lambda ph, c: Pos(sx * S / 2, Y_I, 0) * Rot(0, 0, a_idl(ph, c)) * G10, 360.0 / ZI)
    w2, ph_k = best_phase(lambda c: Pos(sx * S / 2, Y_I, 0) * Rot(0, 0, a_idl(PH_I[sx], c)) * G10,
                          lambda ph, c: Pos(sx * S, Y_P, 0) * Rot(0, 0, ph - math.degrees(c / RP)) * G12, 360.0 / ZP)
    OFF_K[sx] = ph_k - OFF_P
    print("сторона %+d: промежуточная %.2f° (%.3f), низ крайней повёрнут на %.2f° (%.3f)" % (sx, PH_I[sx], w1, OFF_K[sx], w2))

# ---------------- детали ----------------
# средняя: шестерня во оба слоя + ножка Ø8 вниз сквозь палубу + шестигранник во фланец
g_c = Pos(0, 0, Z_L0) * Rot(0, 0, OFF_P) * gear(ZP, Z_U1 - Z_L0)
g_c += Pos(0, 0, (FL_COLLAR + Z_L0) / 2) * Cylinder(4.0, Z_L0 - FL_COLLAR + 0.02)
g_c += Pos(0, 0, FL_COLLAR - 1.9) * extrude(RegularPolygon(HEX / 2 / math.cos(math.radians(30)), 6), 1.9 + 0.01)
g_c = Pos(0, 0, -FL_COLLAR) * g_c                         # начало — верх втулки фланца
# крайняя: верх (к рейке) + низ (к промежуточной, повёрнут), отверстие Ø3.4 на штырёк
G_K = {}
for sx in (1, -1):
    gk = Pos(0, 0, Z_U0 - 0.11) * Rot(0, 0, OFF_P) * gear(ZP, T + 0.11) + Pos(0, 0, Z_L0) * Rot(0, 0, OFF_P + OFF_K[sx]) * gear(ZP, T)
    gk = Pos(0, 0, -Z_L0) * (gk - Cylinder(1.7, 100))
    for k in range(1 if sx > 0 else 2):                                              # метка сверху: правая • , левая ••
        gk -= Pos(3.0 * math.cos(math.radians(90 + 40 * k)), 3.0 * math.sin(math.radians(90 + 40 * k)), 2 * T + 0.1) * Cylinder(0.5, 1.0)
    G_K[sx] = gk
# промежуточная
g_i = gear(ZI, T - 0.1) - Cylinder(1.7, 20)      # на 0.1 тоньше: верхний этаж крайней заходит в нижний слой на 0.01          # фаза задаётся при установке (крутится свободно)

# основание: дно, стенки, палуба над мотором, штырьки, стойки рельса
b = BB(-L / 2, L / 2, 0, W, 0, T_BASE)
for y0, y1 in ((0, 1.5), (W - 1.5, W)):                                             # передняя и задняя стенки
    b += BB(-L / 2, L / 2, y0, y1, ZW - 0.01, Z_CV0)
    for sx in (1, -1):                                                              # до дна — только по краям (мотор задвигается
        b += BB(*sorted((sx * 14.4, sx * L / 2)), y0, y1, T_BASE - 0.01, ZW + 0.01)   # спереди между опорами)
b += BB(-L / 2, L / 2, 1.5 - 0.01, W - 1.5 + 0.01, ZW, Z_D1)                         # палуба
b -= Pos(0, Y_P, (ZW + Z_D1) / 2) * Cylinder(4.6, 2.0)                               # проход ножки средней шестерни
for sx in (1, -1):
    b += Pos(sx * S, Y_P, (Z_D1 + Z_U1) / 2) * Cylinder(1.5, Z_U1 - Z_D1 + 0.01)    # штырёк крайней
    b += Pos(sx * S / 2, Y_I, (Z_D1 + Z_L1) / 2) * Cylinder(1.5, Z_L1 - Z_D1 + 0.01)  # штырёк промежуточной
for x in (0.0, 16.0, -16.0):                                                        # стойки под рельс
    b += BB(x - 1.2, x + 1.2, STEM_Y0, STEM_Y1, Z_D1 - 0.01, Z_U0)
b -= Pos(0, Y_P, T_BASE / 2) * Cylinder(4.5, T_BASE + 0.2)                           # окно под мотор
for a in (0, 180):                                                                  # прорези под винты статора
    sl = BB(5.5, 9.5, -1.15, 1.15, -0.1, T_BASE + 0.1) + Pos(5.5, 0, T_BASE / 2) * Cylinder(1.15, T_BASE + 0.2) \
        + Pos(9.5, 0, T_BASE / 2) * Cylinder(1.15, T_BASE + 0.2)
    b -= Pos(0, Y_P, 0) * Rot(0, 0, a) * sl
for x in (-23.5, 23.5):
    for y in (6, 18):
        b -= Pos(x, y, T_BASE / 2) * Cylinder(1.1, T_BASE + 0.2)

# крышка над верхними шестернями — клеится на переднюю стенку; рельс тележки — клеится на 3 стойки
# 04.11 (владелец): основание из двух частей — без поддержек. Разрез по низу палубы (ZW): НИЗ — дно, опоры стенок и 4
# угловые стойки (дном на стол), ВЕРХ — палуба со штырьками, стенки, стойки рельса (палубой на стол). На стойках низа
# фиксаторы Ø3 × 2, в палубе дырки Ø3.3 × 2.2; собрать на клей
_LOWZ = BB(-40, 40, -10, 40, -1, ZW)
b_niz = b & _LOWZ
b_verh = b - _LOWZ
CORNERS = [(sx * 21.5, y) for sx in (1, -1) for y in (2.25, 21.75)]
for x, y in CORNERS:
    b_niz += BB(x - 3.5, x + 3.5, y - 2.25, y + 2.25, T_BASE - 0.01, ZW)               # угловые стойки 7 × 4.5
    b_niz += Pos(x, y, ZW + 1.0) * Cylinder(1.5, 2.0)                                  # фиксатор
    b_verh -= Pos(x, y, ZW + 1.1) * Cylinder(1.65, 2.2)
b = b_niz + b_verh                                                                     # для проверок — собранное

kr = BB(-L / 2, L / 2, 0, 13.6, Z_CV0, Z_CV1)
rl = BB(-L / 2, L / 2, STEM_Y0, STEM_Y1, Z_U0, Z_U1 - 1.0 + 0.01) + BB(-L / 2, L / 2, RAIL_Y0, RAIL_Y1, Z_U1 - 1.0, Z_U1)

# тележка: пластина, рейка вниз в верхний слой, полоз вокруг шляпки рельса
ct = BB(-RK_HALF, RK_HALF, 1.6, 22.0, Z_C0, Z_C1)
rk = BB(-RK_HALF, RK_HALF, Y_RK + DED, RK_BACK, Z_U0, Z_C0 + 0.01)
tn, th = math.tan(PA), (PITCH / 2 - 0.1) / 2
for i in range(-4, 5):
    xc = i * PITCH
    pr = [(xc - th - DED * tn, Y_RK + DED), (xc - th + ADD_R * tn, Y_RK - ADD_R), (xc + th - ADD_R * tn, Y_RK - ADD_R),
          (xc + th + DED * tn, Y_RK + DED)]
    rk += Pos(0, 0, Z_U0) * extrude(make_face(Polyline(*(pr + [pr[0]]))), T)
ct += rk & BB(-RK_HALF, RK_HALF, 0, W, Z_U0 - 1, Z_C1)
for y0, y1, ly0, ly1 in ((19.0, 19.3, 19.0, 19.8), (21.7, 22.0, 21.2, 22.0)):        # стенки полоза и губы под шляпку
    ct += BB(-RK_HALF, RK_HALF, y0, y1, Z_U1 - 1.3, Z_C0 + 0.01)
    ct += BB(-RK_HALF, RK_HALF, ly0, ly1, Z_U1 - 1.3, Z_U1 - 1.1)

parts = [("rg_osnovanie_niz", b_niz), ("rg_osnovanie_verh", b_verh), ("rg_kryshka", kr), ("rg_rels", rl), ("rg_shesternya_centr", g_c),
         ("rg_shesternya_kraj_prav", G_K[1]), ("rg_shesternya_kraj_lev", G_K[-1]), ("rg_promezh", g_i), ("rg_telezhka", ct)]
import json
json.dump({"PH_I": {str(k): v for k, v in PH_I.items()}, "S": S, "Y_P": Y_P, "Y_I": Y_I, "Z_L0": Z_L0, "FL_COLLAR": FL_COLLAR,
           "Z_MTOP": Z_MTOP, "RP": RP, "RI": RI}, open(os.path.join(HERE, "rg_fazy.json"), "w"), indent=1)
for n, p in parts:
    p = Part() + p
    bb = p.bounding_box()
    print("%s: %.1f x %.1f x %.1f, solids %d" % (n, bb.size.X, bb.size.Y, bb.size.Z, len(p.solids())))
    export_stl(p, os.path.join(OUT, n + ".stl"))

# ================= ПРОВЕРКА: ход ±24, мотор задвигается спереди =================
FL_R, FL_T = 8.75, 1.6
fl = Pos(0, Y_P, Z_MTOP + FL_T / 2) * Cylinder(FL_R, FL_T) + Pos(0, Y_P, (Z_MTOP + FL_COLLAR) / 2) * Cylinder(4.0, FL_COLLAR - Z_MTOP)
heads = Pos(0, Y_P, Z_MTOP + FL_T + 0.75) * (Cylinder(7.9, 1.5) - Cylinder(4.1, 1.6))
motor = Pos(0, Y_P, T_BASE + MOT_H / 2) * Cylinder(MOT_D / 2, MOT_H)


def assembly(c):
    a = {"основание": b, "крышка": kr, "рельс": rl, "мотор": motor, "фланец": fl, "головки": heads,
         "средняя": Pos(0, Y_P, FL_COLLAR) * Rot(0, 0, -math.degrees(c / RP)) * g_c,
         "тележка": Pos(c, 0, 0) * ct}
    for sx in (1, -1):
        a["крайняя%+d" % sx] = Pos(sx * S, Y_P, Z_L0) * Rot(0, 0, -math.degrees(c / RP)) * G_K[sx]
        a["промеж%+d" % sx] = Pos(sx * S / 2, Y_I, Z_L0) * Rot(0, 0, PH_I[sx] + math.degrees(c / RI)) * g_i
    return a


SKIP = [{"мотор", "основание"}, {"мотор", "фланец"}, {"фланец", "головки"}, {"мотор", "головки"}, {"фланец", "средняя"},
        {"основание", "крышка"}, {"основание", "рельс"}]
bad = 0
for c in (-24, -17.3, -12, -8.7, -6, -2.2, 0, 1.5, 6.8, 9.1, 13, 18.4, 24):
    a = assembly(c)
    nm = list(a)
    for i, p in enumerate(nm):
        for q in nm[i + 1:]:
            if {p, q} in SKIP:
                continue
            v = (Part() + (a[p] & a[q])).volume
            if v > 0.01:
                bad += 1
                print("ПЕРЕСЕЧЕНИЕ %s × %s: %.3f мм³ при c = %+.1f" % (p, q, v, c))
# зацепление: средняя на пол-зуба — врезается в промежуточные и рейку
a0 = assembly(0)
gc_off = Pos(0, Y_P, FL_COLLAR) * Rot(0, 0, 15) * g_c
print("средняя на пол-зуба × промежуточная: %.2f, × тележка: %.2f (> 0 — в зацеплении)" %
      ((Part() + (gc_off & a0["промеж+1"])).volume, (Part() + (gc_off & a0["тележка"])).volume))
# мотор с фланцем и головками задвигается спереди (−Y)
for dy in (-4, -8, -14, -22, -30):
    m = Pos(0, dy, 0) * (motor + fl + heads)
    v = (Part() + (m & b)).volume
    if v > 0.01:
        bad += 1
        print("мотор не задвигается: сдвиг %d — %.3f" % (dy, v))
print("рольганг 2204: %s" % ("чисто" if not bad else "ЕСТЬ ПЕРЕСЕЧЕНИЯ: %d" % bad))
