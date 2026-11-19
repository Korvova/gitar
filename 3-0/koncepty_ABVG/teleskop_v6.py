# -*- coding: utf-8 -*-
r"""ТЕЛЕСКОП v3 (12.11.2026) — на основе v2, чтобы всё держалось при любом положении гитары и печаталось без поддержек:
  1) полка плоская; ползун ведёт брусок-прямоугольник, который лежит в пазу на его верху (вровень);
     брусок — отдельная деталь в пазах двух стоек у краёв, стойки же — упоры хода;
  2) мост — трапеция, тележка держится за неё губами (не поднимается), надевается на мост с торца до установки моста;
  3) планка сверху связывает обе оси плавающих шестерён — шестерни не соскакивают, оси не гнутся;
  4) оси плавающих шестерён Ø4, отверстия шестерён Ø4.5; шестерня мотора Ø3.3 — садится по трубке мотора без перекоса;
  5) неподвижная рейка заодно с основанием (как в v2).
X поперёк грифа, Y вдоль, Z = 0 — низ основания. Ход ползуна ±11, тележки ±22. Ширина 50.
Запуск из этой папки: ..\.venv-b123d\Scripts\python teleskop_v3.py
"""
import math, os
from build123d import *

HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
SUF = "" if float(os.environ.get("BSH", "0")) == 0 else "_sdvig%+g" % float(os.environ.get("BSH"))
for d in ("stl" + SUF, "asm" + SUF):
    os.makedirs(d, exist_ok=True)

M, PA = 0.8, math.radians(20)
P = math.pi * M
ZM, ZF = 11, 12
RM, RF = M * ZM / 2, M * ZF / 2            # 4.4, 4.8
A = 2.5 * P                                # плавающие шестерни на ±A от центра ползуна
HALF, S = 25.0, 11.0
Z_FL, MOT_H = 2.5, 12.23
Z_M1 = Z_FL + MOT_H
LG_Y = (12.15, 23.1)                       # ножка моста по Y
Z_SL = 8.0  
XL, XO, XW = 21.6, 23.6, 23.8              # ножка: центр / наружная грань; внутренняя грань боковой стенки крышки                               # высота направляющих стенок ножек
YM = 15.5                                  # ось мотора
DZ = 4.4                                   # v6: всё над мотором выше на толщину платформы с магнитами (4.4: под головкой М2 2 мм — в мотор 1.5)
L1 = (15.0 + DZ, 18.5 + DZ)                          # шестерня мотора + ползун
L2 = (18.7 + DZ + 0.3, 21.2 + DZ + 0.3)                          # плавающие шестерни + рейки + мост
Z_P0, Z_P1 = 21.4 + DZ + 0.3, 23.4 + DZ + 0.3                    # ложе
Y_FIX, Y_CART, Y_SL = -RF, RF, YM - RM
Y_ROOT = Y_FIX - 1.2 * M
Y0, Y1 = -8.5, YM + 19.6                  # +2.4 сзади: полка рубашки с магнитами r до 17.6
Y_LEDGE = YM - 14.3                        # край полки
BSH = float(os.environ.get("BSH", "0"))      # СДВИГ МОСТА вдоль струн (крайние пальцы): мост, тележка, щель крышек; ножки/кнопки/мотор на месте
YB0, YB1 = 12.1 + BSH, 17.1 + BSH          # мост внизу; вверху шире на DT
YBL = 14.6                                 # центр ножек/кнопок по Y (не сдвигается)
YBP = (YB0 + YB1) / 2
DT = 1.0                                   # мост шире вверху на 0.5 с каждой стороны
DTB = 0.8                                  # хвост балки ползуна
CW, SLX = 10.0, S + 1.5
RL0, RL1, RLH = -2.0, 1.0, 1.6             # балка ползуна: низ по Y, высота
C = 0.2                                    # зазор скользящих посадок
R_AX, R_FB = 2.0, 2.3                      # ось Ø4, отверстие шестерни Ø4.6 (19.11 печать: 4.2 туго, должна крутиться свободно)
R_MB = 1.85                                # шестерня мотора и платформа Ø3.7 (19.11: 3.3 туго)
Z_ST0, Z_ST1 = L2[1] + 0.15, L2[1] + 1.65  # планка осей
PIN_X, PIN_Y, PIN_R = 24.4, -3.5, 0.95     # упоры: филамент 1.75 в отверстие Ø1.9


def BB(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))


def CZ(r, z0, z1, x=0.0, y=0.0):
    return Pos(x, y, z0) * Cylinder(r, z1 - z0, align=(Align.CENTER, Align.CENTER, Align.MIN))


def prof_x(pts, x0, x1):
    """профиль (y, z) вытянуть вдоль X от x0 до x1"""
    return Pos(x0, 0, 0) * Rot(90, 90, 0) * extrude(make_face(Polyline(*(pts + [pts[0]]))), x1 - x0, dir=(0, 0, 1))


def gear(z, z0, z1, gap_deg, bl=0.15):
    rp = M * z / 2
    rb, ra, rf = rp * math.cos(PA), rp + 0.9 * M, rp - 1.25 * M
    inv = lambda a: math.tan(a) - a
    ht = (P / 2 - bl) / (2 * rp)
    pts = []
    for i in range(z):
        c = 2 * math.pi * i / z
        fl = []
        for k in range(9):
            r = max(rb, rf) + (ra - max(rb, rf)) * k / 8
            fl.append((r, ht + inv(PA) - inv(math.acos(min(rb / r, 1.0)))))
        t = [(rf, -(ht + inv(PA) + 0.03))] + [(r, -a) for r, a in fl] + [(r, a) for r, a in reversed(fl)] + [(rf, ht + inv(PA) + 0.03)]
        pts += [(r * math.cos(c + a), r * math.sin(c + a)) for r, a in t]
    g = extrude(make_face(Polyline(*(pts + [pts[0]]))), z1 - z0)
    return Pos(0, 0, z0) * Rot(0, 0, gap_deg - 180.0 / z) * g


def rack(x0, x1, yp, sgn, z0, z1, body):
    tn, th, add, ded = math.tan(PA), (P / 2 - 0.15) / 2, 0.9 * M, 1.2 * M
    out = BB(x0, x1, yp - sgn * ded, yp - sgn * (ded + body), z0, z1)
    for k in range(int(x0 / P) - 1, int(x1 / P) + 2):
        xc = k * P
        pr = [(xc - th - ded * tn, yp - sgn * (ded + 0.01)), (xc - th + add * tn, yp + sgn * add), (xc + th - add * tn, yp + sgn * add), (xc + th + ded * tn, yp - sgn * (ded + 0.01))]
        out += Pos(0, 0, z0) * extrude(make_face(Polyline(*(pr + [pr[0]]))), z1 - z0, dir=(0, 0, 1))
    return out & BB(x0, x1, -50, 50, z0, z1)


# (1) основание: неподвижная рейка, полка с балкой-хвостом, стойки моста, гнездо мотора, отверстия упоров
base = BB(-HALF, HALF, Y0, Y1, 0, Z_FL)
base += BB(-HALF, HALF, Y0, Y_LEDGE, 0, L1[0])
# брусок-прямоугольник в пазу ползуна, вровень с ним: отдельная деталь, кладётся в пазы двух стоек сверху (капля клея); стойки же — упоры хода; ведёт ползун вбок, от подъёма не держит
BM_Y = (4.9, 8.1, 4.9, 8.1)                      # брусок-прямоугольник 3.2: низ y0..y1, верх y0..y1
Z_BM0, Z_BM1 = 16.5 + DZ, 18.45 + DZ
for sx in (-1, 1):
    base += BB(sx * (SLX + S + 0.2), sx * HALF, 3.7, 12.11, 0, Z_BM1)       # стойка бруска = упор ползуна
    x0_, x1_ = sorted((sx * (SLX + S), sx * (HALF + 1)))
    base -= prof_x([(BM_Y[0] - 0.1, Z_BM0 - 0.05), (BM_Y[1] + 0.1, Z_BM0 - 0.05), (BM_Y[3] + 0.1, Z_BM1 + 1), (BM_Y[2] - 0.1, Z_BM1 + 1)], x0_, x1_)   # паз под конец бруска
beam = prof_x([(BM_Y[0], Z_BM0), (BM_Y[1], Z_BM0), (BM_Y[3], Z_BM1), (BM_Y[2], Z_BM1)], -HALF, HALF)
base += BB(-HALF, HALF, Y0, Y_ROOT + 0.01, 0, L2[1])
base += prof_x([(Y_ROOT, L2[0] - 1.7), (Y_ROOT, L2[0] + 0.01), (Y_FIX + 0.7 * M, L2[0] + 0.01)], -HALF, HALF)   # скос под зубьями
base += rack(-HALF, HALF, Y_FIX, 1, L2[0], L2[1], 0.3)
base += BB(-HALF, HALF, Y_ROOT, -4.0, L1[0] - 0.01, L2[0] - 0.2)                  # стенка под зубьями до ползуна (зазор 0.2), без пустоты
for sx in (-1, 1):
    # v6: стоек нет — мост стоит на НОЖКАХ (отдельные детали), ножки — на кнопках в полу; направляющие стенки вокруг ножек
    x0_, x1_ = sorted((sx * 18.0, sx * 19.2)); base += BB(x0_, x1_, LG_Y[0] - 1.4, LG_Y[1] + 1.4, 0, Z_SL)   # зазор 0.4 — ножка стенок не касается
    for y0_, y1_ in ((LG_Y[0] - 1.4, LG_Y[0] - 0.4), (LG_Y[1] + 0.4, LG_Y[1] + 1.4)):
        x0_, x1_ = sorted((sx * 18.0, sx * XW)); base += BB(x0_, x1_, y0_, y1_, 0, Z_SL)
    base -= BB(*sorted((sx * (XL - 2.75), sx * (XL + 2.75))), YBL - 2.75, YBL + 2.75, Z_FL - 1.0, Z_FL + 1)   # гнездо кнопки 5.2×5.2 (вровень −1.0)
    base -= BB(*sorted((sx * 21.0, sx * 24.0)), LG_Y[1] - 4, LG_Y[1] - 1, -1, Z_FL + 1)                         # выход проводов кнопки и вибро вниз
base += CZ(15.6, Z_FL - 0.01, Z_FL + 4, 0, YM) & BB(-HALF, HALF, Y_LEDGE, Y1, 0, 30)
base -= CZ(14.1, Z_FL, 40, 0, YM)
for ang in (45, 135, 225, 315):
    for r_ in (5.6, 6.1, 6.6):
        base -= CZ(1.3, -1, Z_FL + 1, r_ * math.cos(math.radians(ang)), YM + r_ * math.sin(math.radians(ang)))
base -= BB(-5.5, 5.5, YM + 6.0, YM + 12.5, -1, Z_FL + 1)
base -= CZ(5.0, Z_FL - 0.25, Z_FL + 1, 0, YM) + CZ(2.0, -1, Z_FL + 1, 0, YM)

# (2) мост-трапеция на штырьках
most = prof_x([(YB0, L2[0]), (YB1, L2[0]), (YB1 + DT, L2[1]), (YB0 - DT, L2[1])], -HALF, HALF)

# (3) шестерня мотора и макет мотора
PL_R, MG_R, MG_N = 13.5, 10.0, 8                                                   # платформа на роторе, кольцо магнитов Ø5×2 (полюса N/S через один)
plat = CZ(PL_R, Z_M1 + 0.1, Z_M1 + 0.1 + DZ)
for k in range(MG_N):
    a = 2 * math.pi * k / MG_N
    pass                                                                        # магнитов на платформе больше нет — они внизу, в рубашке
mags = Part() + [CZ(2.0, Z_M1 + 0.1 + DZ - 1.9, Z_M1 + 0.1 + DZ, MG_R * math.cos(2 * math.pi * k / MG_N), MG_R * math.sin(2 * math.pi * k / MG_N)) for k in range(MG_N)]
# крепление к крутящемуся торцу 2204 (владелец 16.11): 4 × М2 на Ø12 между магнитами, головки утоплены на 2 — под головкой 2.0, М2×4 входит в мотор на 1.5;
# шестерня отдельно (иначе к винтам не подлезть): квадрат 4.9 в гнездо платформы, на клей; в центре Ø3.3 по трубке мотора
Z_PT = Z_M1 + 0.1 + DZ                                                           # верх платформы
plat -= CZ(R_MB, 0, 40)
for k in range(4):
    a = math.radians(22.5 + 90 * k)
    plat -= CZ(1.1, Z_PT - DZ - 1, Z_PT + 1, 6 * math.cos(a), 6 * math.sin(a))
    plat -= CZ(1.95, Z_PT - 2.0, Z_PT + 1, 6 * math.cos(a), 6 * math.sin(a))
plat -= Pos(0, 0, Z_PT - 1.5) * Box(5.1, 5.1, 3.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
gear_m = gear(ZM, Z_PT, L1[1], -90) + Pos(0, 0, Z_PT - 1.4) * Box(4.9, 4.9, 1.41, align=(Align.CENTER, Align.CENTER, Align.MIN))
gear_m -= CZ(R_MB, 0, 40)
pin_m0 = gear_m                                                                   # у оси мотора, x = y = 0
pin_m = Pos(0, YM, 0) * pin_m0
motor = CZ(13.9, Z_FL, Z_M1, 0, YM) + CZ(1.5, Z_M1 - 0.01, L1[1], 0, YM)

# (4) ползун: паз-хвост снизу, рейка к мотору, две оси Ø4 до планки
sl = BB(-SLX, SLX, -3.8, Y_SL - 1.2 * M, *L1) + rack(-SLX, SLX, Y_SL, 1, L1[0], L1[1], 0.5)
sl -= prof_x([(BM_Y[0] - C, Z_BM0 - C), (BM_Y[1] + C, Z_BM0 - C), (BM_Y[3] + C, L1[1] + 1), (BM_Y[2] - C, L1[1] + 1)], -SLX - 1, SLX + 1)   # паз сверху под брусок
for x in (-A, A):
    sl += CZ(R_AX, L1[1] - 0.01, L2[1], x, 0)                                   # оси вровень с шестернями (планки осей нет, 18.11)

# (5) плавающая шестерня ×2 (у своей оси) и планка осей
flo0 = gear(ZF, L2[0], L2[1], 90 + 180.0 / ZF) - CZ(R_FB, 0, 40)
strap = BB(-A - 2.8, A + 2.8, -1.8, 1.8, Z_ST0, Z_ST1) - CZ(R_AX + 0.02, 0, 40, -A, 0) - CZ(R_AX + 0.02, 0, 40, A, 0)

# (6) тележка: рейка спереди, губы по трапеции моста, ложе
Y_CF, Y_CB = YB0 - 0.2, YB1 + 0.2
MESH = 0.25                                 # рейка тележки ближе к плавающим шестерням (проскоки на печати)
cart = rack(-CW, CW, Y_CART - MESH, -1, L2[0], L2[1], Y_CF - (Y_CART + 1.2 * M) + MESH)
cart -= prof_x([(Y_CF + 0.01, L2[0] - 0.01), (Y_CF + 0.01, L2[1] + 0.02), (Y_CF - DT, L2[1] + 0.02)], -CW - 1, CW + 1)   # передняя губа под мост
cart += BB(-CW, CW, Y_CB, Y_CB + 2.0, L2[0], Z_P0 + 0.01)
cart -= prof_x([(Y_CB - 0.01, L2[0] - 0.01), (Y_CB - 0.01, L2[1] + 0.02), (Y_CB + DT, L2[1] + 0.02)], -CW - 1, CW + 1)   # задняя губа под мост
cart += BB(-CW, CW, Y_CART + 1.2 * M, Y_CF - DT, L2[1] - 0.01, Z_P0 + 0.01)
cart += BB(-CW, CW, Y_CART + 1.2 * M, Y_CB + 2.0, Z_P0, Z_P1)                                       # ложе
BY = (Y_CF - 3.0, Y_CB - 1.0)
bort = BB(CW - 1.5, CW, Y_CART + 2, Y_CB + 1.5, Z_P1, Z_P1 + 3)
for y in BY:
    bort += BB(CW - 1.5, CW, y - 1.5, y + 1.5, Z_P1 - 1.4, Z_P1 + 0.01)
    for sx in (-1, 1):
        x0_, x1_ = sorted((sx * (CW - 1.6), sx * (CW + 1)))
        cart -= BB(x0_, x1_, y - 1.6, y + 1.6, Z_P1 - 1.5, Z_P1 + 1)

# (7) ножки ×2 жёстко на кнопках; мост лежит на ножках через TPU-подушки (мягкое соединение) — вибрирует только мост с тележкой
Z_BT = Z_FL + 0.5                                                                # верх кнопки (гнездо −1.0, кнопка 1.5)
PAD_T = 0.8                                                                      # TPU-подушка между ножкой и мостом
Z_LT = L2[0]                                                                     # ножки срощены с мостом (одна деталь, 18.11)
Z_CN = Z_BT + 0.8 + 1.2 + 5.2                                                  # центр таблетки в ножке
Z_LB = Z_BT + PAD_T                                                              # низ ножки: под ней мягкая TPU-подушка на кнопке
Z_GR0, Z_GR1 = 19.8, 21.8                                                        # паз снаружи ножки: в него входит ребро боковой стенки крышки — мост не вынуть вверх
legs, pads = [], []
for sx in (-1, 1):
    x0_, x1_ = sorted((sx * 19.6, sx * XO))
    lg = BB(x0_, x1_, LG_Y[0], LG_Y[1], Z_LB, Z_LT - 0.6)                         # вне моста ниже — под юбкой тележки
    yt0, yt1 = max(LG_Y[0], YB0), min(LG_Y[1], YB1)
    if yt1 - yt0 > 0.5:
        lg += BB(x0_, x1_, yt0, yt1, Z_LT - 0.61, Z_LT + 0.01)                   # под мостом — до моста (срастается)
    lg -= BB(*sorted((sx * (XL - 1.55), sx * (XL + 1.55))), LG_Y[0] + 0.35, LG_Y[1] + 1, Z_CN - 5.1, Z_CN + 5.1)   # карман таблетки Ø10×3, открыт назад
    lg -= CZ(0.85, Z_LB - 0.1, Z_LB + 1.5, sx * XL, YBL)                       # гнездо штырька подушки снизу
    lg -= BB(*sorted((sx * (XO - 0.8), sx * (XO + 1))), LG_Y[0] - 1, LG_Y[1] + 1, Z_GR0, Z_GR1)
    legs.append(lg)
    pd = BB(x0_, x1_, LG_Y[0], LG_Y[1], Z_BT, Z_LB) + CZ(0.75, Z_LB - 0.01, Z_LB + 1.4, sx * XL, YBL)   # TPU 0.8, штырёк вверх в ножку
    pads.append(pd)
# вибро-таблетки Ø10×2.7 — НА МОСТУ: держатель снизу моста у торцов, таблетка стоймя, вставляется с задней стороны (там и выход провода)
CXH, CYH = 17.85, 17.35
VIBRO = False                                                                   # пока проверяем положение — держателей таблеток нет (владелец 16.11)
for sx in (-1, 1):
    x0_, x1_ = sorted((sx * 16.2, sx * 19.5))
    hold = BB(x0_, x1_, YB0, YB1, L2[0] - 11.0, L2[0] + 0.01) + BB(x0_, x1_, YB1 - 0.01, CYH + 5.3, L2[0] - 11.0, L2[0] - 0.6)
    hold -= BB(*sorted((sx * (CXH - 1.45), sx * (CXH + 1.45))), CYH - 5.15, CYH + 6, L2[0] - 10.7, L2[0] - 0.3)
    if VIBRO:
        most += hold
coins = Part() + [Pos(sx * CXH, CYH, L2[0] - 5.5) * Rot(0, 90, 0) * Cylinder(5.0, 2.7) for sx in (-1, 1)] if VIBRO else Pos(0, 0, -60) * Box(0.1, 0.1, 0.1)
coins = Part() + [Pos(sx * XL, LG_Y[0] + 0.45 + 5.05, Z_CN) * Rot(0, 90, 0) * Cylinder(5.0, 3.0) for sx in (-1, 1)]   # таблетки в ножках
btns = Part() + [BB(sx * XL - 2.6, sx * XL + 2.6, YBL - 2.6, YBL + 2.6, Z_FL - 1.0, Z_BT) for sx in (-1, 1)]
# 49E ×2 под мостом над кольцом магнитов, в квадратуре: углы −6° и 196.5° (разница 22.5° по модулю 90° при 8 полюсах)
# === 49E СНИЗУ (17.11): рубашка на колоколе, полка снизу с 8 магнитами Ø4×1.9 лицом вниз (N/S через один),
# два 49E лежат в гнёздах основания лицом вверх, ножки сразу вниз сквозь дно; зазор магнит—датчик 2.5 (импульсы → синус)
R_J0, R_J1, R_JF = 14.0, 15.0, 19.0                                              # рубашка: внутр./наруж., полка
MG_RB = 16.4                                                                     # радиус кольца магнитов
Z_HS = Z_FL + 4.0                                                                # лицо датчиков = верх ободка мотора
Z_JF0 = Z_HS + 2.5                                                               # низ полки = низ магнитов
Z_JF1 = Z_JF0 + 2.4
Z_PB, Z_PTOP = Z_M1 + 0.1, Z_M1 + 0.1 + DZ                                    # платформа ротора (низ/верх)
jacket = CZ(R_J1, Z_JF0, Z_PB) - CZ(R_J0, 0, Z_PB + 0.01)                        # юбка вокруг колокола
jacket += CZ(R_J1, Z_PB - 0.01, Z_PTOP) - CZ(PL_R - 0.2, 0, 40)                  # кольцо, сращивает юбку с платформой
jacket += CZ(R_JF, Z_JF0, Z_JF1) - CZ(R_J0, 0, 40)                               # полка с магнитами
jacket += (Pos(0, 0, Z_JF1 - 0.01) * Cone(R_JF, R_J1, R_JF - R_J1 + 0.01, align=(Align.CENTER, Align.CENTER, Align.MIN))) - CZ(R_J0, 0, 40)   # скос 45° над полкой — печать вверх ногами без поддержек
jacket += plat                                                                   # ОДНА деталь: платформа + юбка + полка
mags = Part()
for k in range(MG_N):
    a = 2 * math.pi * k / MG_N
    jacket -= CZ(2.05, Z_JF0 - 1, Z_JF0 + 2.0, MG_RB * math.cos(a), MG_RB * math.sin(a))
    mags += CZ(2.0, Z_JF0, Z_JF0 + 1.9, MG_RB * math.cos(a), MG_RB * math.sin(a))
base -= CZ(R_JF + 0.5, Z_JF0 - 0.4, Z_JF1 + 0.5, 0, YM) + Pos(0, YM, Z_JF1 + 0.49) * Cone(R_JF + 0.5, R_J1 + 0.4, R_JF - R_J1 + 0.1, align=(Align.CENTER, Align.CENTER, Align.MIN)) + CZ(R_J1 + 0.4, Z_JF0 - 0.4, Z_PTOP + 0.2, 0, YM)   # место полке и рубашке
H_ANG = (-11.25, 191.25)                                                         # по бокам, разница 202.5° ≡ 22.5° (четверть периода 90°)
hall = Part()
for ang in H_ANG:
    a = math.radians(ang); hx, hy = MG_RB * math.cos(a), YM + MG_RB * math.sin(a)
    sg = 1 if hx > 0 else -1                                                      # наружу (к стенке) — сторона выводов
    # гнездо ровно по осям, параллельно стенкам: датчик 3.0 по X × 4.1 по Y, лицом вверх, ножки наружу по X
    x_in, x_out = hx - sg * 1.6, hx + sg * 2.4                                     # площадка: от ободка до 0.4 за датчиком
    base += BB(*sorted((x_in, x_out)), hy - 3.1, hy + 3.1, Z_FL - 0.01, Z_HS)
    rim = BB(*sorted((x_in, x_out)), hy - 3.1, hy + 3.1, Z_HS - 0.01, Z_HS + 0.8) - BB(*sorted((hx - sg * 1.6, x_out + sg)), hy - 2.15, hy + 2.15, Z_HS - 1, Z_HS + 2)
    base += rim                                                                   # бортики с трёх сторон, наружная сторона открыта — выводы
    base -= BB(*sorted((hx - sg * 1.6, x_out + sg)), hy - 2.15, hy + 2.15, Z_HS - 1.6, Z_HS + 1)   # гнездо 3.2×4.3, открыто наружу
    base -= BB(*sorted((x_out, x_out + sg * 0.9)), hy - 1.6, hy + 1.6, -1, Z_HS + 1)            # щель для проводов вниз сквозь дно
    hall += BB(hx - 1.5, hx + 1.5, hy - 2.05, hy + 2.05, Z_HS - 1.5, Z_HS)
# подушка из двух половинок, склеить плоскостями (владелец 16.11): у каждой пластинка 0.4 и свой штырёк — печать без поддержек
_zm = Z_LT + PAD_T / 2
pad_lo = pads[1] & BB(-40, 40, -40, 60, -10, _zm)                                    # низ: штырёк вниз в ножку
pad_hi = pads[1] & BB(-40, 40, -40, 60, _zm, 60)                                     # верх: штырёк вверх в мост
# === КРЫШКИ (18.11): сверху видно только мост, щель и тележку; всё на 4 винтах М2 сверху ===
Z_CV0, Z_CV1 = Z_P1 - 2.0, Z_P1 - 0.8                                            # крыша на 0.8 ниже верха тележки
Y_SL0, Y_SL1 = Y_CART + 1.2 * M - 0.36, Y_CB + 2.0 + 0.4                        # щель под тележку
most = most & BB(-XO, XO, -50, 50, -50, 80)                                      # мост укорочен — между боковыми стенками крышки
most = most + legs[0] + legs[1]                                                  # МОСТ + НОЖКИ = одна деталь
legs = [Pos(0, 0, -80) * Box(0.1, 0.1, 0.1)] * 2                                # (для проверок — ножки теперь внутри моста)
# передняя крышка: полоса над шестернями + 2 упора на стенку рейки, 2 винта в стенку рейки
Y_TF, Z_TF = -7.2, 23.4                                                          # винты передней крышки — сбоку, в блок рейки
cov_f = BB(-HALF, HALF, Y0, Y_SL0, Z_CV0, Z_CV1)
SC_B, Z_SB_ = 29.0, 15.0                                                         # винты задней крышки — сбоку, в колонны
cov_b = BB(-HALF, HALF, Y_SL1, Y1, Z_CV0, Z_CV1) + BB(-HALF, HALF, Y1 - 1.2, Y1, 12.5, Z_CV0 + 0.01)
def scr_x(sx, y, z):                                                             # винт М2 вдоль X снаружи: проход 2.2 + выемка под головку Ø4 глубиной 1.4
    return Pos(sx * (HALF - 0.7), y, z) * Rot(0, 90, 0) * Cylinder(2.0, 1.4 + 0.01) + Pos(sx * (HALF - 2.6), y, z) * Rot(0, 90, 0) * Cylinder(1.1, 5.2)
def pilot_x(sx, y, z):
    return Pos(sx * (HALF - 2.6 - 3.0), y, z) * Rot(0, 90, 0) * Cylinder(0.8, 6.2)
for sx in (-1, 1):
    x0_, x1_ = sorted((sx * 22.4, sx * HALF))
    tab = BB(x0_, x1_, Y_TF - 1.25, Y_TF + 1.25, Z_TF - 2.6, Z_CV0 + 0.01)          # ушко передней крышки (вровень с боком)
    base -= BB(*sorted((sx * 22.2, sx * (HALF + 1))), Y_TF - 1.4, Y_TF + 1.4, Z_TF - 2.8, Z_CV0 + 1)
    cov_f += tab - scr_x(sx, Y_TF, Z_TF)
    base -= pilot_x(sx, Y_TF, Z_TF)
    x0_, x1_ = sorted((sx * XW, sx * HALF))
    wall = BB(x0_, x1_, LG_Y[0], Y_SL1 + 0.01, Z_FL, L2[0] - 0.5) + BB(x0_, x1_, Y_SL1, Y1, Z_FL, Z_CV0 + 0.01)
    wall += BB(*sorted((sx * (XO - 0.6), sx * XW + sx * 0.01)), LG_Y[0] + 0.5, LG_Y[1] - 0.5, Z_GR0 + 0.5, Z_GR1 - 0.5)   # ребро в паз ножки
    wall += BB(*sorted((sx * 22.4, sx * HALF)), SC_B - 1.6, SC_B + 1.6, Z_SB_ - 1.6, Z_SB_ + 1.6)                    # утолщение под винт
    cov_b += wall - scr_x(sx, SC_B, Z_SB_)
    x0_, x1_ = sorted((sx * 19.6, sx * 22.4))
    base += BB(x0_, x1_, 27.0, 31.0, Z_FL - 0.01, Z_SB_ + 4)                     # колонна под боковой винт задней крышки
    base -= pilot_x(sx, SC_B, Z_SB_)
# === НАКЛАДКИ ТЕЛЕЖКИ (18.11): тележка одна на все модули, палец ставится на накладку, сдвинутую вдоль струн ===
# накладка лежит на верху тележки (на 0.8 выше крышек модуля) и может вылезать над крышками и за край модуля
YC_CART = (Y_CART + 1.2 * M + Y_CB + 2.0) / 2                                    # центр верха тележки по Y
CAP_T, PAD_L = 1.6, 12.0                                                        # толщина накладки, длина площадки под палец
for sx in (-1, 1):
    cart -= CZ(1.05, Z_P1 - 1.5, Z_P1 + 1, sx * 5.0, YC_CART)                   # 2 гнезда под штырьки накладки
def make_cap(shift):
    yp = YC_CART + shift
    y0 = min(yp - PAD_L / 2, Y_CART + 1.2 * M); y1 = max(yp + PAD_L / 2, Y_CB + 2.0)
    c = BB(-CW, CW, y0, y1, Z_P1, Z_P1 + CAP_T)
    for sx in (-1, 1):
        c += CZ(1.0, Z_P1 - 1.4, Z_P1 + 0.01, sx * 5.0, YC_CART)
    return c
CAP_SHIFTS = (0.0, -9.0, -28.6)                                                  # средний / средние пальцы / крайние пальцы (к шестерням)
caps = {sh: make_cap(sh) for sh in CAP_SHIFTS}
PRINT = [("01_osnovanie", base, 0, 1), ("02_most", most, 180, 1),  ("03b_shest_motora", gear_m, 180, 1), ("03a_kolpak_rotora_s_magnitami", jacket, 180, 1), ("04_maket_motora", motor, 0, 1),
         ("05_polzun", sl, 0, 1), ("06_shest_plav_x2", flo0, 0, 2), ("08_telezhka", cart, 180, 1), ("17_nakladka_telezhki_0", caps[0.0], 180, 1), ("17_nakladka_telezhki_m10", caps[-9.0], 180, 1), ("17_nakladka_telezhki_m29", caps[-28.6], 180, 1), ("15_kryshka_perednjaja", cov_f, 180, 1), ("16_kryshka_zadnjaja_P", cov_b, 180, 1),
         ("10_brusok", beam, 0, 1), ("13_podushka_TPU_pod_nozhku_x2", pads[0], 0, 2)]


def pose(s):
    rf = -math.degrees(s / RF)
    return {"ползун": Pos(s, 0, 0) * sl, 
            "плав1": Pos(s - A, 0, 0) * Rot(0, 0, rf) * flo0, "плав2": Pos(s + A, 0, 0) * Rot(0, 0, rf) * flo0,
            "шест.мотора": Pos(0, YM, 0) * Rot(0, 0, math.degrees(s / RM)) * pin_m0, "тележка": Pos(2 * s, 0, 0) * cart, "накладка": Pos(2 * s, 0, 0) * caps[-28.6]}


if __name__ == "__main__":
    import numpy as np, trimesh
    print("высота %.1f, основание %.0f × %.1f, тележка %.0f" % (Z_P1, 2 * HALF, Y1 - Y0, 2 * CW))
    stat = {"крышка П": cov_b, "крышка перед": cov_f, "рубашка": Pos(0, YM, 0) * jacket, "основание": base, "мост": most, "мотор": motor, "брусок": beam, "ножка Л": legs[0], "ножка П": legs[1], "таблетки": coins, "кнопки": btns, "49E": hall, "подушки": pads[0] + pads[1]}
    bad = 0
    for s in (-S, -8.25, -5.5, -2.75, 0, 2.75, 5.5, 8.25, S):
        al = {**stat, **pose(s)}
        ns = list(al)
        for i, a in enumerate(ns):
            for b in ns[i + 1:]:
                if (a in stat and b in stat) or {a, b} == {"мотор", "шест.мотора"} or {a, b} == {"рубашка", "шест.мотора"} or {a, b} == {"тележка", "накладка"}:   # крутятся вместе (квадрат шестерни в колпаке)
                    continue
                try:
                    v = (al[a] & al[b]).volume
                except Exception:
                    v = 0.0
                if v > 0.03:
                    bad += 1
                    print("  ПЕРЕСЕЧЕНИЕ s=%+.2f %s × %s: %.2f мм³" % (s, a, b, v))
    SP = [("ножка Л", "основание"), ("ножка П", "основание"), ("ножка Л", "мотор"), ("ножка П", "мотор"), ("таблетки", "ножка Л"), ("таблетки", "ножка П"), ("таблетки", "мост"), ("таблетки", "основание"), ("таблетки", "мотор"),
          ("кнопки", "основание"), ("49E", "основание"), ("крышка П", "основание"), ("крышка перед", "основание"), ("крышка П", "ножка Л"), ("крышка П", "ножка П"), ("крышка П", "мост"), ("крышка перед", "мост"), ("крышка П", "рубашка"), ("крышка П", "мотор"), ("крышка П", "брусок"), ("крышка перед", "брусок"), ("рубашка", "основание"), ("рубашка", "49E"), ("рубашка", "мотор"), ("рубашка", "ножка Л"), ("рубашка", "ножка П"), ("рубашка", "мост"), ("ножка Л", "мост"), ("ножка П", "мост"), ("подушки", "основание"), ("подушки", "кнопки"), ("подушки", "ножка Л"), ("подушки", "ножка П")]
    for a, b in SP:
        v = (stat[a] & stat[b]); v = 0.0 if v is None else v.volume
        if v > 0.03: bad += 1; print("  СТАТИКА %s × %s %.2f" % (a, b, v))
    dn = Pos(0, 0, -0.3)                                                           # нажали: мост+ножки+тележка вниз на ход кнопки
    for s_ in (-S, 0, S):
        pz = pose(s_)
        mv = {"мост": dn * most, "таблетки": dn * coins, "тележка": dn * pz["тележка"], "накладка": dn * pz["накладка"]}
        fx = {"крышка П": cov_b, "крышка перед": cov_f, "ножка Л": legs[0], "ножка П": legs[1], "основание": base, "ползун": pz["ползун"], "плав1": pz["плав1"], "плав2": pz["плав2"], "шест.мотора": pz["шест.мотора"], "мотор": motor}
        for a, AA in mv.items():
            for b, Bp in fx.items():
                r = AA & Bp; v = 0.0 if r is None else r.volume
                if v > 0.03: bad += 1; print("  НАЖАТИЕ s=%+.0f %s × %s %.2f" % (s_, a, b, v))
    hz = min(hall.bounding_box().min.Z - (Z_M1 + 0.1 + DZ), 99); print("  зазор 49E — магниты %.1f мм" % hz)
    for d in (S + 0.4, -S - 0.4):
        if (Pos(d, 0, 0) * sl & base).volume < 0.01:
            bad += 1
            print("  упор не держит на %+.1f" % d)
    def iv(a, b):
        r = a & b
        try:
            return 0.0 if r is None else r.volume
        except Exception:
            return 0.0
    for nm, part, other, lift in (("тележка", cart, most, 0.6),):
        if iv(Pos(0, 0, lift) * part, other) < 0.01:
            bad += 1
            print("  %s поднимается на %.1f мм — не держится" % (nm, lift))
    print("проверка хода и посадок: %s" % ("ЧИСТО" if not bad else "%d проблем" % bad))
    print("файлы на печать (нависания > 45° выше стола, без коротких мостиков):")
    for n, p, flip, cnt in PRINT:
        p = Rot(flip, 0, 0) * (Part() + p)
        bb = p.bounding_box()
        p = Pos(-(bb.min.X + bb.max.X) / 2, -(bb.min.Y + bb.max.Y) / 2, -bb.min.Z) * p
        export_stl(p, ("stl" + SUF + "/%s.stl") % n, tolerance=0.01, angular_tolerance=0.1)
        m = trimesh.load(("stl" + SUF + "/%s.stl") % n)
        cz = m.triangles_center[:, 2]; nz = m.face_normals[:, 2]
        over = (nz < -0.72) & (cz > 0.25)
        ov_area = float(m.area_faces[over].sum())
        print("  %-20s ×%d  %5.1f × %5.1f × %5.1f  герм %s  нависание %.1f мм²" % (n, cnt, bb.size.X, bb.size.Y, bb.size.Z, m.is_watertight, ov_area))
    for n, p in (("base", base), ("beam", beam), ("most", most), ("motor", motor), ("slider", sl), ("cart", cart), ("flo", flo0), ("legs", legs[0] + legs[1]), ("pads", pads[0] + pads[1]), ("coins", coins), ("btns", btns), ("hall", hall), ("mags", mags), ("jacket", jacket), ("cov_f", cov_f), ("cov_b", cov_b), ("cap0", caps[0.0]), ("cap10", caps[-9.0]), ("cap29", caps[-28.6]), ("pin_m", pin_m0)):
        export_stl(Part() + p, ("asm" + SUF + "/%s.stl") % n, tolerance=0.02, angular_tolerance=0.2)
    print("asm готово")
