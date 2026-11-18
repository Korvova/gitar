# -*- coding: utf-8 -*-
"""Концепт Г (18.11): мотор ЛЁЖА (ось вдоль струн). Телескоп работает в вертикальной плоскости у торца мотора:
шестерня на роторе → рейка ползуна сверху → плавающие шестерни (ось вдоль струн) катятся по неподвижной рейке передней стенки → рейка тележки.
Модуль вдоль струн ≈ 23 мм < шага пальцев 24 → тележка прямо под пальцем, накладок нет. Высота ~31."""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from build123d import *
import teleskop_v6 as T
os.chdir(HERE); os.makedirs("asm_D", exist_ok=True)
BB, CZ, gear, rack = T.BB, T.CZ, T.gear, T.rack
M, RF, RM, A, S, HALF, CW = T.M, T.RF, T.RM, T.A, T.S, T.HALF, T.CW
DED, ZM_, ZF_ = 1.2 * M, T.ZM, T.ZF
R_MOT, H_MOT = 13.9, 12.23
FL = 1.0                                     # пол
Y_MB, Y_MF = 1.2, 1.2 + H_MOT                # мотор: от задней стенки до торца колокола
Y_PL0, Y_PL1 = Y_MF + 0.1, Y_MF + 2.1        # платформа на колоколе (крепёж шестерни)
Y_P0, Y_P1 = Y_PL1, Y_PL1 + 3.5              # слой шестерни мотора + рейки ползуна
Y_G0, Y_G1 = Y_P1 + 0.3, Y_P1 + 2.8          # слой плавающих шестерён + неподвижной рейки + рейки тележки
Y_FW0, Y_FW1 = Y_G1 + 0.2, Y_G1 + 1.4        # передняя стенка
ZC = FL + R_MOT + 0.1                        # ось мотора
Z_SR = ZC + RM                               # делительная рейки ползуна
Z_G = Z_SR + 1.9                             # ось плавающих шестерён
Z_FX, Z_CR = Z_G - RF, Z_G + RF              # неподвижная рейка (зубья вверх) / рейка тележки (зубья вниз)
Z_TOPW = FL + 2 * R_MOT + 0.3                # верх стенок = над мотором
Z_C0, Z_C1 = Z_TOPW + 0.1, Z_TOPW + 2.1      # тело тележки
def toY(p):                                  # деталь, построенную «в плоскости XY с толщиной по Z», повернуть: Y→Z, Z→−Y
    return Rot(90, 0, 0) * p
def rackXZ(x0, x1, zp, sgn, y0, y1, body):   # рейка вдоль X в вертикальной плоскости, зубья по ±Z
    return toY(rack(x0, x1, zp, sgn, -y1, -y0, body))
def gearXZ(z, y0, y1, gap):
    return toY(gear(z, -y1, -y0, gap))
# основание: пол, задняя стенка (к ней мотор), торцевые стойки, передняя стенка с неподвижной рейкой
base = BB(-HALF, HALF, 0, Y_FW1, 0, FL) + BB(-HALF, HALF, 0, Y_MB, 0, Z_TOPW)
base += BB(-HALF, HALF, Y_FW0, Y_FW1, 0, Z_TOPW)
base += rackXZ(-HALF, HALF, Z_FX, 1, Y_G0, Y_FW0 + 0.01, 1.2)
base += BB(-HALF, HALF, Y_G0, Y_FW0 + 0.01, FL - 0.01, Z_FX - DED - 1.19)      # под рейкой до пола — сплошная стенка
for sx in (-1, 1):
    base += BB(*sorted((sx * 23.7, sx * HALF)), Y_MB, Y_P1 + 0.2, 0, Z_TOPW)   # торцевые стойки только в слое ползуна (над слоем шестерён ездит рейка тележки)
# брусок-направляющая ползуна над рейкой ползуна, концами в торцевых стойках
BY0, BY1, BZ0, BZ1 = Y_P0 + 0.6, Y_P1 - 0.6, Z_SR + DED + 1.6, Z_SR + DED + 3.4
beam = BB(-HALF + 0.01, HALF - 0.01, BY0, BY1, BZ0, BZ1)
motor = toY(Pos(0, ZC, -Y_MF) * Cylinder(R_MOT, H_MOT, align=(Align.CENTER, Align.CENTER, Align.MIN)))
plat = toY(Pos(0, ZC, -Y_PL1) * Cylinder(13.0, Y_PL1 - Y_PL0, align=(Align.CENTER, Align.CENTER, Align.MIN)))
PIN_GAP, PIN_SG = float(os.environ.get("PG", "25")), float(os.environ.get("PS", "1"))
pin0 = gearXZ(ZM_, Y_P0, Y_P1 - 0.2, PIN_GAP)                                     # у оси, x=z=0
SLX = 12.5
sl = rackXZ(-SLX, SLX, Z_SR, -1, Y_P0 + 0.1, Y_P1, 0.5) + BB(-SLX, SLX, Y_P0 + 0.1, Y_P1, Z_SR + DED + 0.49, BZ1 + 1.2)
sl -= BB(-SLX - 1, SLX + 1, BY0 - 0.2, BY1 + 0.2, BZ0 - 0.2, BZ1 + 0.2)         # канал под брусок
for x in (-A, A):
    sl += Pos(x, Y_P1 - 0.01, Z_G) * Rot(-90, 0, 0) * Cylinder(T.R_AX, Y_G1 - Y_P1 + 0.01, align=(Align.CENTER, Align.CENTER, Align.MIN))
flo0 = gearXZ(ZF_, Y_G0, Y_G1, 90 + 180.0 / ZF_) - toY(CZ(T.R_FB, -40, 40))
cart = rackXZ(-CW, CW, Z_CR, -1, Y_G0, Y_G1, Z_C0 - (Z_CR + DED) + 0.01) + BB(-CW, CW, 0.0, Y_FW1, Z_C0, Z_C1)
def iv(a, b):
    r = a & b; return 0.0 if r is None else r.volume
stat = {"основание": base, "брусок": beam, "мотор": motor, "платформа": plat}
bad = 0
for s in (-S, -5.5, -2.75, 0, 2.75, 5.5, S):
    rf = math.degrees(s / RF)                                                    # ось шестерён вдоль +Y: знак вращения
    mv = {"ползун": Pos(s, 0, 0) * sl, "тележка": Pos(2 * s, 0, 0) * cart,
          "плав1": Pos(s - A, 0, Z_G) * Rot(0, rf, 0) * flo0, "плав2": Pos(s + A, 0, Z_G) * Rot(0, rf, 0) * flo0,
          "шест.мотора": Pos(0, 0, ZC) * Rot(0, PIN_SG * math.degrees(s / RM), 0) * pin0}
    al = {**stat, **mv}; ns = list(al)
    for i, a in enumerate(ns):
        for b in ns[i + 1:]:
            if (a in stat and b in stat) or {a, b} in ({"платформа", "шест.мотора"},): continue
            v = iv(al[a], al[b])
            if v > 0.05: bad += 1; print("  s=%+.2f %s × %s %.2f" % (s, a, b, v))
print("концепт Г:", "ЧИСТО" if not bad else "%d проблем" % bad, "| вдоль струн %.1f мм, высота %.1f мм" % (Y_FW1, Z_C1))
for n, p in (("base", base), ("beam", beam), ("motor", motor), ("plat", plat), ("pin", pin0), ("slider", sl), ("flo", flo0), ("cart", cart)):
    export_stl(Part() + p, "asm_D/%s.stl" % n, tolerance=0.02, angular_tolerance=0.2)
open("asm_D/params.txt", "w").write("%f %f %f %f\n" % (ZC, Z_G, RF, RM))
