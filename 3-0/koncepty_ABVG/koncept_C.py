# -*- coding: utf-8 -*-
"""Концепт В (18.11): компактный модуль ≈ ширине мотора. Плавающие шестерни подняты НАД шестерню мотора,
передней стенки с рейкой нет — неподвижная рейка = планка на стойках над ползуном. Модуль вдоль струн ~32 мм вместо 43.6.
Мост с ножками сзади над мотором. Датчики/крышки пока не рисуем — смотрим механику и габарит."""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from build123d import *
import teleskop_v6 as T
os.chdir(HERE); os.makedirs("asm_C", exist_ok=True)
BB, CZ, PX, gear, rack = T.BB, T.CZ, T.prof_x, T.gear, T.rack
M, RF, RM, A, S, L1, L2, HALF, CW, YM = T.M, T.RF, T.RM, T.A, T.S, T.L1, T.L2, T.HALF, T.CW, T.YM
DED, C, DT = 1.2 * M, 0.2, 1.0
Y_G = 7.5                                    # ось плавающих шестерён (перед шестернёй мотора, но выше неё)
Y_FIX, Y_CART = Y_G - RF, Y_G + RF           # 2.7 / 12.3
Y_SL = YM - RM                               # рейка ползуна к шестерне мотора (11.1)
Y0, Y1 = -0.6, 31.6                          # габарит модуля вдоль струн
BMY0, BMY1 = 1.9, 5.1                        # брусок-направляющая ползуна
Z_BM0, Z_BM1 = T.Z_BM0, T.Z_BM1
YB0, YB1 = 14.6, 19.6                        # мост над мотором
Z_P0, Z_P1 = L2[1] + 0.2, L2[1] + 2.2
SLX = 12.5
# основание
base = BB(-HALF, HALF, Y0, Y1, 0, T.Z_FL)
base += CZ(15.6, T.Z_FL - 0.01, T.Z_FL + 4, 0, YM) - CZ(14.1, 0, 40, 0, YM)
for sx in (-1, 1):
    x0, x1 = sorted((sx * (SLX + S + 0.2), sx * HALF))
    base += BB(x0, x1, Y0, 6.2, 0, L2[0])                                         # стойка: держит брусок и неподвижную рейку
    base -= BB(x0 - 1, x1 + 1, BMY0 - 0.1, BMY1 + 0.1, Z_BM0 - 0.05, L2[0] + 1)    # паз под брусок (сверху)
beam = BB(-HALF, HALF, BMY0, BMY1, Z_BM0, Z_BM1)
# 19.11 (владелец): у бруска ножки-упоры у внутренних граней стоек — кладётся в пазы и не ездит вдоль X (без клея и без прижима сверху)
X_ST = SLX + S + 0.2                                                             # внутренняя грань стойки 23.7
LEG_T, LEG_H = 1.0, 1.5                                                          # толщина ножки по X, вниз от бруска (до низа ползуна)
for sx in (-1, 1):
    beam += BB(*sorted((sx * (X_ST - 0.1), sx * (X_ST - 0.1 - LEG_T))), BMY0, BMY1, Z_BM0 - LEG_H, Z_BM0 + 0.01)
fix = rack(-HALF, HALF, Y_FIX, 1, L2[0], L2[1], 1.4)                              # неподвижная рейка-планка, концами на стойках
# ползун: рейка к мотору сзади, паз под брусок, оси плавающих шестерён
sl = BB(-SLX, SLX, BMY0 - 1.6, Y_SL - DED, *L1) + rack(-SLX, SLX, Y_SL, 1, L1[0], L1[1], 0.5)
sl -= BB(-SLX - 1, SLX + 1, BMY0 - C, BMY1 + C, Z_BM0 - C, L1[1] + 1)
for sx in (-1, 1):                                                               # вырез в концах ползуна под ножки бруска (ход до упора)
    x_in = X_ST - 0.1 - LEG_T - S - C
    sl -= BB(*sorted((sx * x_in, sx * (SLX + 1))), BMY0 - C, BMY1 + C, L1[0] - 1, L1[1] + 1)
for x in (-A, A):
    sl += CZ(T.R_AX, L1[1] - 0.01, L2[1], x, Y_G)
flo0 = T.flo0
# тележка вокруг моста-трапеции (как v3), рейка спереди зубьями к шестерням
Y_CF, Y_CB = YB0 - 0.2, YB1 + 0.2
cart = rack(-CW, CW, Y_CART - 0.25, -1, L2[0], L2[1], Y_CF - (Y_CART + DED) + 0.25)
cart -= PX([(Y_CF + 0.01, L2[0] - 0.01), (Y_CF + 0.01, L2[1] + 0.02), (Y_CF - DT, L2[1] + 0.02)], -CW - 1, CW + 1)
cart += BB(-CW, CW, Y_CB, Y_CB + 2.0, L2[0], Z_P0 + 0.01)
cart -= PX([(Y_CB - 0.01, L2[0] - 0.01), (Y_CB - 0.01, L2[1] + 0.02), (Y_CB + DT, L2[1] + 0.02)], -CW - 1, CW + 1)
cart += BB(-CW, CW, Y_CART + DED, Y_CF - DT, L2[1] - 0.01, Z_P0 + 0.01)
cart += BB(-CW, CW, Y_CART + DED, Y_CB + 2.0, Z_P0, Z_P1)
# мост + ножки (одна деталь), ножки на кнопках
Z_LB = T.Z_FL + 0.5 + 0.8
most = PX([(YB0, L2[0]), (YB1, L2[0]), (YB1 + DT, L2[1]), (YB0 - DT, L2[1])], -23.6, 23.6)
for sx in (-1, 1):
    most += BB(*sorted((sx * 19.6, sx * 23.6)), YB0, YB1, Z_LB, L2[0] + 0.01)
plat, gm, motor = T.plat, T.gear_m, T.motor
def iv(a, b):
    r = a & b; return 0.0 if r is None else r.volume
stat = {"основание": base, "брусок": beam, "рейка": fix, "мост": most, "мотор": motor, "платформа": Pos(0, YM, 0) * plat}
bad = 0
for s in (-S, -8.25, -5.5, -2.75, 0, 2.75, 5.5, 8.25, S):
    rf = -math.degrees(s / RF)
    mv = {"ползун": Pos(s, 0, 0) * sl, "плав1": Pos(s - A, Y_G, 0) * Rot(0, 0, rf) * flo0, "плав2": Pos(s + A, Y_G, 0) * Rot(0, 0, rf) * flo0,
          "тележка": Pos(2 * s, 0, 0) * cart, "шест.мотора": Pos(0, YM, 0) * Rot(0, 0, math.degrees(s / RM)) * gm}
    al = {**stat, **mv}; ns = list(al)
    for i, a in enumerate(ns):
        for b in ns[i + 1:]:
            if (a in stat and b in stat) or {a, b} in ({"мотор", "шест.мотора"}, {"платформа", "шест.мотора"}): continue
            v = iv(al[a], al[b])
            if v > 0.05: bad += 1; print("  s=%+.2f %s × %s %.2f" % (s, a, b, v))
print("концепт В:", "ЧИСТО" if not bad else "%d проблем" % bad, "| длина модуля вдоль струн %.1f (было 43.6), палец y≈%.1f" % (Y1 - Y0, (Y_CART + DED + Y_CB + 2) / 2))
for n, p in (("base", base), ("beam", beam), ("fix", fix), ("slider", sl), ("flo", flo0), ("cart", cart), ("most", most), ("plat", plat), ("gm", gm), ("motor", motor)):
    export_stl(Part() + p, "asm_C/%s.stl" % n, tolerance=0.02, angular_tolerance=0.2)
