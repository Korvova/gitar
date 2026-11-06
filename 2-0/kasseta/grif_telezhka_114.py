# -*- coding: utf-8 -*-
r"""СТЕНД НА ОДНУ ТЕЛЕЖКУ ПО ВИКИ 19.42 + 19.43 (06.11.2026): мотор 2204 перевёрнут, провода через его трубку, полая шестерня в пазу
платформы, рейка со скосом, узкий задний рельс, два зеркальных окна. Размеры — из scene_grif_simmetria.py, посадки и зубья — со стола 112.
Z = 0 — верх платформы, X поперёк грифа (ход ±22), Y вдоль. Датчика нет (19.40). Всё без поддержек, поэтому отступления от сцены:
  * крышка над зубьями — отдельная планка (нависала бы), лежит в уступе стенки за зубьями, на клей;
  * упор x+ — отдельный, клеится после того, как тележка надета с торца (иначе щёчка не пройдёт);
  * шестерня и фланец — две детали, сцеплены квадратом 6.4 на клей (между ними был бы навес);
  * кубик печатается крышей на стол, верхний край — фаска 0.8 вместо R1; нижний этаж — z 0.3…3.7, кубик начинается с z 3.7
    (плашки лежат верхом на столе; язычки 3.7…4.1 отошли к кубику), на 4 штырьках и клею;
  * борта ложа — отдельно, на штырьках в крыше; щёчка над зубьями шестерни срезана на 45° (до y −6.05 вместо −4.9);
  * потолок полости 16.25 вместо 16.2 (мотор 12.23 лёг бы на фланец в натяг); зазор по скосам 0.15 как на столе 112 (в сцене 0.2);
  * зубья рейки укорочены как на столе 112: вершина y 5.3 (в сцене 5.0).
Запуск: ..\.venv-b123d\Scripts\python grif_telezhka_114.py
"""
import math
import os
from build123d import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "Print", "Print")

# ---- общее ----
M, Z_T, PA = 1.0, 12, math.radians(20)
RP = M * Z_T / 2                       # 6
ADD_G, ADD_R, DED = 0.85, 0.7, 1.25    # как на столе 112
PITCH = math.pi * M
TRAVEL = 22.0
HX, HY = 14.7, 14.7                    # тележка
PX, PY = 26.0, 16.0                    # платформа
Z_PL0, Z_SLOT = -2.0, -1.5             # низ платформы, дно паза
Z_RK, Z_CV, Z_R = 0.8, 1.0, 2.4        # верх зубьев, низ крышки зубьев, верх рельсов
Y_S0, Y_S1 = -7.3, 7.25                # паз
Z_G0 = -1.3                            # низ шестерни
Z_P0, Z_P1 = 2.6, 3.7                  # плашки
Z_FL1 = 3.98                           # верх фланца
Z_M0, Z_M1 = 4.02, 16.25               # мотор 12.23 (неподвижный торец прижат к потолку полости)
Z_TOP = 17.7                           # верх крыши
Z_B1 = 21.5                            # верх бортов ложа
R_CUT = 14.1                           # полость под мотор Ø27.8
C_RL = 0.15                            # зазор по скосу
LEG_H, LEG_T, LEG_Y, LEG_PX = 30.0, 2.8, 14.0, 18.0
SQ = 6.4                               # квадрат шестерня-фланец


def BB(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))


def prof_x(pts, x0, x1):
    """контур в плоскости (y, z), вытянутый вдоль x"""
    return Pos(x0, 0, 0) * Rot(90, 90, 0) * extrude(make_face(Polyline(*(pts + [pts[0]]))), x1 - x0)


def CZ(r, z0, z1, x=0.0, y=0.0):
    return Pos(x, y, z0) * Cylinder(r, z1 - z0, align=(Align.CENTER, Align.CENTER, Align.MIN))


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


# ---------------- (1) платформа: паз, зубья, спинка рейки со скосом, задний рельс, щель, упор x−, гнёзда ножек ----------------
pl = BB(-PX, PX, -PY, PY, Z_PL0, 0)
pl -= BB(-PX - 1, PX + 1, Y_S0, Y_S1, Z_SLOT, 1)                                       # паз, концы открыты
Y_RK = RP                                                                              # делительная рейки: ось шестерни y = 0
tn, th = math.tan(PA), (PITCH / 2 - 0.1) / 2
for k in range(-10, 11):
    xc = k * PITCH
    pr = [(xc - th - DED * tn, Y_RK + DED), (xc - th + ADD_R * tn, Y_RK - ADD_R), (xc + th - ADD_R * tn, Y_RK - ADD_R), (xc + th + DED * tn, Y_RK + DED)]
    pl += Pos(0, 0, Z_SLOT - 0.01) * extrude(make_face(Polyline(*(pr + [pr[0]]))), Z_RK - Z_SLOT + 0.01)
pl = pl & BB(-PX, PX, -PY - 1, PY + 1, Z_PL0 - 1, 10)                                  # зубья обрезать по краю
pl += BB(-PX, PX, Y_S1 - 0.01, 9.0, -0.01, Z_CV)                                       # стенка за зубьями до низа крышки
pl += prof_x([(9.0 - 0.01, -0.01), (11.25, -0.01), (11.25, 0.0), (11.85, Z_R), (9.0 - 0.01, Z_R)], -PX, PX)  # спинка рейки со скосом
pl += prof_x([(-11.25, -0.01), (-9.5, -0.01), (-9.5, Z_R), (-11.85, Z_R), (-11.25, 0.0)], -PX, PX)            # задний рельс
pl -= BB(-24.2, 24.2, -1.5, 1.5, Z_PL0 - 1, 1)                                         # щель под провода
pl += BB(-26.0, -25.05, -9.5, -7.3, -0.01, 2.5)                                        # упор x−
upor = BB(25.05, 26.0, -9.5, -7.3, 0, 2.5)                                             # упор x+ — отдельно, после надевания тележки
for sx in (1, -1):
    for sy in (1, -1):
        pl -= BB(sx * LEG_PX - 1.5, sx * LEG_PX + 1.5, sy * LEG_Y - 1.5, sy * LEG_Y + 1.5, Z_PL0 - 1, 1)

# крышка над зубьями — планка в уступе за зубьями (y 7.25…9 уже срезано до Z_CV)
kr_r = BB(-PX, PX, 5.0, 8.95, Z_CV, Z_R)

# ножка: доска под платформу, два штырька в гнёзда (показана на +Y, вторая — та же)
leg = BB(-PX, PX, LEG_Y - LEG_T / 2, LEG_Y + LEG_T / 2, Z_PL0 - LEG_H, Z_PL0)
for sx in (1, -1):
    leg += BB(sx * LEG_PX - LEG_T / 2, sx * LEG_PX + LEG_T / 2, LEG_Y - LEG_T / 2, LEG_Y + LEG_T / 2, Z_PL0 - 0.01, -0.1)
leg2 = Rot(0, 0, 180) * leg

# ---------------- (2) шестерня: зубья и шейка, сверху квадрат; печать зубьями на стол. Просвет Ø3.2 под провода ----------------
_p = 360.0 / Z_T
OFF = 90.0 - (round(90.0 / _p - 0.5) + 0.5) * _p                                       # впадина на +Y, к рейке
gear = Pos(0, 0, Z_G0) * Rot(0, 0, OFF) * extrude(make_face(Polyline(*gear_pts(M, Z_T, PA, add=ADD_G))), Z_RK - Z_G0)
gear += CZ(4.7, Z_RK - 0.01, Z_P0)                                                     # шейка Ø9.4
gear += Pos(0, 0, Z_P0 - 0.01) * Rot(0, 0, 45) * Box(SQ, SQ, 1.01, align=(Align.CENTER, Align.CENTER, Align.MIN))
gear -= CZ(1.6, Z_G0 - 1, 10)
# фланец Ø15: на крутящийся торец мотора, эпоксидка; 4 × Ø2.1 на Ø12 — только страховка, не глубже 1.5 мм в мотор
fl = CZ(7.5, Z_P0, Z_FL1)
fl -= Pos(0, 0, Z_P0 - 1) * Rot(0, 0, 45) * Box(SQ + 0.2, SQ + 0.2, 5, align=(Align.CENTER, Align.CENTER, Align.MIN))
for a in (45, 135, 225, 315):
    fl -= CZ(1.05, Z_P0 - 1, Z_FL1 + 1, 6 * math.cos(math.radians(a)), 6 * math.sin(math.radians(a)))

# ---------------- (3) кубик: полость Ø28.2, в потолке карманы; печать крышей на стол ----------------
ku = BB(-HX, HX, -HY, HY, Z_P1, Z_TOP)
ku = fillet(ku.edges().filter_by(Axis.Z), 1.0)
ku = chamfer(ku.faces().sort_by(Axis.Z)[-1].edges(), 0.8)
ku -= CZ(R_CUT, Z_P1 - 1, Z_M1)
ku -= BB(-5.5, 5.5, -12.5, -6.0, Z_M1 - 0.1, 17.0)                                     # карман под пайку
ku -= BB(-1.2, 1.2, -9.0, 1.0, Z_M1 - 0.1, 17.0)                                       # канавка под провода к центру
ku -= CZ(5.0, Z_M1 - 0.1, 16.5)                                                        # над подшипником (внутреннее кольцо крутится)
for sx in (1, -1):
    for sy in (1, -1):
        ku += CZ(0.9, Z_P1 - 0.8, Z_P1 + 0.01, sx * 12.6, sy * 13.2)                   # штырьки к нижнему этажу
        ku -= BB(sx * 11.25 - 0.85, sx * 11.25 + 0.85, sy * 5.0 - 0.7, sy * 5.0 + 0.7, Z_M1 - 0.1, Z_TOP + 1)  # гнёзда бортов ложа

# борт ложа (x+; второй тот же): печать лёжа, штырьки той же толщины
bort = BB(10.5, 12.0, -12.5, 12.5, Z_TOP, Z_B1)
for sy in (1, -1):
    bort += BB(10.5, 12.0, sy * 5.0 - 0.6, sy * 5.0 + 0.6, Z_M1 + 0.2, Z_TOP + 0.01)
bort2 = Rot(0, 0, 180) * bort

# ---------------- (4) нижний этаж тележки z 0.3…3.7: плашки, юбка, лапы, щёчки; печать верхом на стол ----------------
ni = BB(-HX, HX, -HY, -5.0, Z_P0, Z_P1) - CZ(8.0, Z_P0 - 1, Z_P1 + 1)                  # задняя плашка, вырез R8 под фланец
ni += BB(-HX, HX, 9.3, HY, Z_P0, Z_P1)                                                 # передняя плашка
ni += BB(8.0, 10.6, -5.0, 9.3, Z_P0, Z_P1)                                             # перемычка
for sx in (1, -1):
    x0, x1 = sorted((sx * R_CUT, sx * HX))
    ni += BB(x0, x1, -HY, HY, Z_P0, Z_P1)                                              # юбка: верх
    for y0, y1 in ((-HY, -12.1), (-4.7, 4.7), (12.1, HY)):
        ni += BB(x0, x1, y0, y1, 0.3, Z_P0 + 0.01)                                     # юбка: стенки между окнами
    x2, x3 = sorted((sx * 2.05, sx * 3.0))
    ni += BB(x2, x3, -9.3, -7.45, 0.3, Z_P0 + 0.01)                                    # щёчка упора
    ni += Pos(x2, 0, 0) * Rot(90, 90, 0) * extrude(make_face(Polyline((-7.46, Z_R), (-7.46, Z_CV), (-6.05, Z_CV), (-7.46, Z_R))), x3 - x2)  # над зубьями, 45°
ni_y = lambda z: 11.25 + 0.6 * z / Z_R + C_RL                                          # внутренняя грань лапы = скос + зазор
for sy in (1, -1):
    ni += prof_x([(sy * ni_y(Z_P0 + 0.01), Z_P0 + 0.01), (sy * HY, Z_P0 + 0.01), (sy * HY, 0.3), (sy * ni_y(0.3), 0.3)], -R_CUT - 0.01, R_CUT + 0.01)  # лапы
ni = ni & (Pos(0, 0, 0.0) * fillet(BB(-HX, HX, -HY, HY, 0.0, 5.0).edges().filter_by(Axis.Z), 1.0))   # углы как у кубика
for sx in (1, -1):
    for sy in (1, -1):
        ni -= CZ(1.0, Z_P1 - 0.85, Z_P1 + 1, sx * 12.6, sy * 13.2)                     # гнёзда штырьков
        ni -= Pos(sx * 12.6, sy * 13.2, Z_P1 - 0.85 - 1.0 + 0.01) * Cone(0.0, 1.0, 1.0, align=(Align.CENTER, Align.CENTER, Align.MIN))  # потолок гнезда — конус

parts = [("gt_platforma", pl), ("gt_kryshka_reiki", kr_r), ("gt_upor", upor), ("gt_nozhka", leg), ("gt_shesternya", gear), ("gt_flanec", fl),
         ("gt_kubik", ku), ("gt_bort", bort), ("gt_niz", ni)]
for n, p in parts:
    p = Part() + p
    bb = p.bounding_box()
    print("%s: %.1f x %.1f x %.1f, solids %d" % (n, bb.size.X, bb.size.Y, bb.size.Z, len(p.solids())))
    export_stl(p, os.path.join(OUT, n + ".stl"))

# ================= ПРОВЕРКА =================
bad = 0


def vol(a, b):
    return (Part() + (a & b)).volume


motor = CZ(13.9, Z_M0, Z_M1)
fixed = {"платформа": pl, "крышка рейки": kr_r, "упор x+": upor}
for c in (-22, -17.3, -9.1, -2.4, 0, 1.3, 7.7, 15.2, 22):
    a = math.degrees(c / RP)
    rot = {"шестерня": Pos(c, 0, 0) * Rot(0, 0, a) * gear, "фланец": Pos(c, 0, 0) * Rot(0, 0, a) * fl}
    cart = {"кубик": Pos(c, 0, 0) * ku, "низ": Pos(c, 0, 0) * ni, "борт": Pos(c, 0, 0) * bort, "мотор": Pos(c, 0, 0) * motor}
    for n1, p1 in list(rot.items()) + list(cart.items()):
        for n2, p2 in fixed.items():
            v = vol(p1, p2)
            if v > 0.01:
                bad += 1
                print("ПЕРЕСЕЧЕНИЕ %s × %s: %.3f при c = %+.1f" % (n1, n2, v, c))
    for n1, p1 in rot.items():
        for n2, p2 in cart.items():
            if n2 == "мотор":
                continue
            v = vol(p1, p2)
            if v > 0.01:
                bad += 1
                print("ПЕРЕСЕЧЕНИЕ %s × %s: %.3f при c = %+.1f" % (n1, n2, v, c))
print("мотор × кубик: %.3f; мотор × низ: %.3f; шестерня × фланец: %.3f; кубик × низ (штырьки в гнёздах): %.3f; борт × кубик: %.3f" % (
    vol(motor, ku), vol(motor, ni), vol(gear, fl), vol(ku, ni), vol(bort, ku)))
print("шестерня на пол-зуба × рейка: %.2f мм³ (> 0 — в зацеплении)" % vol(Rot(0, 0, 15) * gear, pl))
print("упор: при c = +22 щёчка × упор x+ %.3f; при c = +22.3 %.3f (> 0 — упирается); при c = −22.3 × упор x− %.3f" % (
    vol(Pos(22, 0, 0) * ni, upor), vol(Pos(22.3, 0, 0) * ni, upor), vol(Pos(-22.3, 0, 0) * ni, pl)))
print("надевание с торца x+ без упора: c = 30: %.3f; c = 45: %.3f" % (
    vol(Pos(30, 0, 0) * ni, pl) + vol(Pos(30, 0, 0) * Rot(0, 0, math.degrees(30 / RP)) * gear, pl), vol(Pos(45, 0, 0) * ni, pl)))
print("ножки × платформа: %.3f, %.3f; просвет щели под трубкой: ±1.5 мм при Ø3.2" % (vol(leg, pl), vol(leg2, pl)))
print("зазоры: кубик у мотора %.2f, стенка %.2f; дно паза %.2f; над карманом %.2f" % (R_CUT - 13.9, HX - R_CUT, Z_SLOT - Z_PL0, Z_TOP - 17.0))
print("стенд: %s; высота от низа основания (−6.5 в изделии) до крыши %.1f мм" % ("чисто" if not bad else "ЕСТЬ ПЕРЕСЕЧЕНИЯ: %d" % bad, Z_TOP + 6.5))
