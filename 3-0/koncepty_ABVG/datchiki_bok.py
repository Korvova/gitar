# -*- coding: utf-8 -*-
"""Датчики положения для ряда 19.59 (19.11, идея владельца): магниты БОКОМ в платформе ротора (по кромке),
два 49E в стойках-прямоугольниках по бокам мотора, вставляются СВЕРХУ, ножки вверх и дальше по канавкам стойки вниз.
8 магнитов N/S через один → период 90°, датчики на −11.25° и 191.25° (разница ≡ 22.5° — квадратура)."""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from build123d import *
import modul_za_motorom as Z
V, K, T = Z.V, Z.K, Z.T
os.chdir(HERE); os.makedirs("asm_dat", exist_ok=True)
BB, CZ, YM = T.BB, T.CZ, T.YM
MAG_D, MAG_T, MAG_N = 4.0, 1.9, 8                                               # магниты владельца Ø4×1.9 (как в v6-А, стол 118)
Z_PL0, Z_PL1 = T.Z_M1 + 0.1, T.Z_M1 + 0.1 + T.DZ
PL_R = T.PL_R                                                                    # штатная платформа r13.5 (владелец: магниты Ø4 в неё боком входят)
Z_MC = (Z_PL0 + Z_PL1) / 2
GAP = 0.8                                                                        # лицо датчика — магнит
SEN_T, SEN_W, SEN_H = 1.5, 4.1, 3.0                                              # 49E: толщина, ширина, высота
RS = PL_R + GAP + SEN_T / 2                                                      # центр датчика по радиусу
Z_TOP = T.L1[0] - 0.25                                                           # верх стойки — под ползуном
X_IN, X_OUT = PL_R + GAP, PL_R + GAP + 5.0                                       # стойка по X (от кромки платформы + зазор)
ANG = (-11.25, 191.25)
# платформа с гнёздами магнитов по кромке: штатная платформа + обод-юбка
plat = T.plat
mags = Part()
for k in range(MAG_N):
    a = 360.0 * k / MAG_N
    plat -= Rot(0, 0, a) * Pos(PL_R - MAG_T / 2 + 0.01, 0, Z_MC) * Rot(0, 90, 0) * Cylinder(MAG_D / 2 + 0.05, MAG_T + 0.02)
    mags += Rot(0, 0, a) * Pos(PL_R - MAG_T / 2, 0, Z_MC) * Rot(0, 90, 0) * Cylinder(MAG_D / 2, MAG_T)
# стойки с датчиками (в координатах модуля: ось мотора в (0, YM))
posts, sens, slots = Part(), Part(), []
for ang in ANG:
    a = math.radians(ang); sx = 1 if math.cos(a) > 0 else -1
    sy = YM + RS * math.sin(a)                                                   # y центра датчика
    xi, xo = sorted((sx * X_IN, sx * X_OUT))
    p = BB(xi, xo, sy - 3.2, sy + 3.2, T.Z_FL - 1.0, Z_TOP)                      # стойка — отдельная деталь, низом в прорезь кольца/пола
    slots.append(BB(xi - 0.15, xo + 0.15, sy - 3.35, sy + 3.35, T.Z_FL - 1.05, T.Z_FL + 4.2))
    xs0, xs1 = sorted((sx * (X_IN - 0.05), sx * (X_IN + SEN_T + 0.1)))
    p -= BB(xs0, xs1, sy - SEN_W / 2 - 0.1, sy + SEN_W / 2 + 0.1, Z_MC - SEN_H / 2 - 0.1, Z_TOP + 1)   # гнездо: сверху, окно к платформе
    xg0, xg1 = sorted((sx * (X_IN + 0.5), sx * (X_OUT + 1)))
    p -= BB(xg0, xg1, sy - 1.5, sy + 1.5, Z_TOP - 1.0, Z_TOP + 1)                # канавка сверху для ножек — наружу
    for k in (-1, 0, 1):                                                         # 3 канавки по наружной грани вниз
        xc = sx * X_OUT
        p -= BB(*sorted((xc - sx * 0.8, xc + sx * 0.5)), sy + k * 1.27 - 0.4, sy + k * 1.27 + 0.4, T.Z_FL + 0.5, Z_TOP + 1)
    posts += p
    sens += BB(*sorted((sx * X_IN, sx * (X_IN + SEN_T))), sy - SEN_W / 2, sy + SEN_W / 2, Z_MC - SEN_H / 2, Z_MC + SEN_H / 2)
def iv(a, b):
    r = a & b; return 0.0 if r is None else r.volume
bad = 0
for nm, base, extra in (("З", Z.base, {"балка": Z.beam}), ("П", V.base_o, {"рейка": V.fix_o})):
    for n, q in {"основание": base, "мотор": K.motor, "брусок": K.beam, **extra}.items():
        v = iv(posts, q)
        if n == "основание":
            q = q - slots[0] - slots[1]; v = iv(posts, q)                       # в основании — прорези под стойки
        if v > 0.05: bad += 1; print("  модуль %s: стойки × %s %.2f" % (nm, n, v))
    for s in (-T.S, -5.5, 0, 5.5, T.S):
        v = iv(posts, Pos(s, 0, 0) * K.sl)
        if v > 0.05: bad += 1; print("  модуль %s s=%+.1f: стойки × ползун %.2f" % (nm, s, v))
v = iv(posts, Pos(0, YM, 0) * plat) + iv(Pos(0, YM, 0) * plat, K.motor) * 0
if v > 0.05: bad += 1; print("  стойки × платформа %.2f" % v)
print("датчики сбоку:", "ЧИСТО" if not bad else "%d проблем" % bad, "| зазор датчик—магнит %.1f, датчики на y %.1f и %.1f (ось мотора %.1f)" % (GAP, YM + RS * math.sin(math.radians(ANG[0])), YM + RS * math.sin(math.radians(ANG[1])), YM))
for n, p in (("posts", posts), ("sens", sens), ("plat_mag", plat), ("mags", mags), ("slots", slots[0] + slots[1])):
    export_stl(Part() + p, "asm_dat/%s.stl" % n, tolerance=0.02, angular_tolerance=0.2)
