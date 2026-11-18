# -*- coding: utf-8 -*-
"""Концепт Б (18.11): тележка СПЕРЕДИ над шестернями, зубья рейки смотрят внутрь (к шестерням).
Неподвижная рейка переезжает назад (за шестерни) на стойки бруска; передняя стенка основания = направляющая-хвост для тележки.
Палец оказывается у переднего края модуля — сдвиг без длинной накладки. Мост/ножки здесь не рисуем (вопрос «где тележка»)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from build123d import *
import teleskop_v6 as T
os.chdir(HERE); os.makedirs("asm_B", exist_ok=True)
BB, CZ, PX = T.BB, T.CZ, T.prof_x
L2, RF, M, HALF, CW, DT = T.L2, T.RF, T.M, T.HALF, T.CW, 0.5
DED = 1.2 * M
# основание: снять старую переднюю рейку и её стенку выше L2[0]-0.2, сделать направляющую-хвост
RY0, RY1 = -8.4, -6.2                                                            # направляющая внизу (вверху шире вперёд на DT)
baseB = T.base - BB(-HALF - 1, HALF + 1, T.Y0 - 1, -3.9, L2[0] - 0.2, 40)
baseB += PX([(RY0, L2[0] - 0.21), (RY1, L2[0] - 0.21), (RY1, L2[1]), (RY0 - DT, L2[1])], -HALF, HALF)
# неподвижная рейка — за шестернями, зубья к шестерням (−Y), лежит концами на стойках бруска
fixB = T.rack(-HALF, HALF, RF, -1, L2[0], L2[1], 1.6)
for sx in (-1, 1):
    fixB += BB(*sorted((sx * 23.7, sx * HALF)), RF + DED - 0.01, RF + DED + 1.6, T.Z_BM1, L2[0] + 0.01)   # опоры на стойки
# тележка Б: рейка зубьями внутрь (+Y), тело над направляющей, губа спереди под скос, площадка под палец выступает вперёд
Z_P0, Z_P1 = L2[1] + 0.2, L2[1] + 2.2
cartB = T.rack(-CW, CW, -RF, 1, L2[0], L2[1], 0.3)                               # зубья на y −4.8, тело до −6.06
cartB += BB(-CW, CW, -RF - DED - 0.3, -3.9, L2[1] - 0.01, Z_P0 + 0.01)            # перемычка зубьев к верху
cartB += BB(-CW, CW, RY0 - DT - 1.4, -3.9, Z_P0, Z_P1)                            # верх тележки (над шестернями и направляющей)
cartB += PX([(RY0 - DT - 0.2, L2[1] + 0.01), (RY0 - 0.2, L2[0]), (RY0 - 1.4, L2[0]), (RY0 - DT - 1.4, L2[1] + 0.01), (RY0 - DT - 1.4, Z_P0 + 0.01), (RY0 - DT - 0.2, Z_P0 + 0.01)][::-1], -CW, CW)   # губа под скос
padB = BB(-CW, CW, RY0 - DT - 1.4 - 6.0, -3.9, Z_P1, Z_P1 + 1.6)               # накладка: палец у переднего края (выступ 6 за край)
def iv(a, b):
    r = a & b; return 0.0 if r is None else r.volume
bad = 0
for s in (-T.S, -5.5, 0, 5.5, T.S):
    p = T.pose(s); p.pop("тележка", None); p.pop("накладка", None)
    import math
    rf = math.degrees(s / RF)                                                     # рейка неподвижна СВЕРХУ (+Y) → шестерни крутятся в другую сторону
    p["плав1"] = Pos(s - T.A, 0, 0) * Rot(0, 0, rf) * T.flo0; p["плав2"] = Pos(s + T.A, 0, 0) * Rot(0, 0, rf) * T.flo0
    c = Pos(2 * s, 0, 0) * (cartB + padB)
    for n, q in {**p, "основание": baseB, "рейка Б": fixB, "брусок": T.beam, "мотор": T.motor}.items():
        v = iv(c, q)
        if v > 0.05: bad += 1; print("  Б: s=%+.1f тележка × %s %.2f" % (s, n, v))
    for n in ("плав1", "плав2", "ползун"):
        v = iv(p[n], fixB)
        if v > 0.03: bad += 1; print("  Б: s=%+.1f рейка × %s %.2f" % (s, n, v))
print("концепт Б:", "ЧИСТО" if not bad else "%d проблем" % bad, "| центр пальца y=%.1f (сейчас ~%.1f)" % ((RY0 - DT - 7.4 - 3.9) / 2, T.YC_CART))
for n, p in (("baseB", baseB), ("fixB", fixB), ("cartB", cartB), ("padB", padB)):
    export_stl(Part() + p, "asm_B/%s.stl" % n, tolerance=0.02, angular_tolerance=0.2)
