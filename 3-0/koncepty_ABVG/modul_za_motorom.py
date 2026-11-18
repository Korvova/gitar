# -*- coding: utf-8 -*-
r"""Один модуль концепта В: тележка ЦЕЛИКОМ за краем своего мотора (владелец 19.11). Рейка тележки цепляет шестерни у края мотора,
сама тележка и площадка уходят вперёд за мотор, лежат на балке-хвосте, которая стоит за мотором на колоннах по краям;
крючки «Г» тележки обнимают балку — не поднимается. Над своим мотором тележки нет.
Запуск: ..\..\2-0\.venv-b123d\Scripts\python modul_za_motorom.py
"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from build123d import *
import ryad_V4b as V
K, T, R = V.K, V.T, V.R
os.chdir(HERE); os.makedirs("asm_zm", exist_ok=True)
BB, CZ, PX, rack = T.BB, T.CZ, T.prof_x, T.rack
S, A, RF, RM, YM, CW, HALF, L2 = T.S, T.A, T.RF, T.RM, T.YM, T.CW, T.HALF, T.L2
DED, C = K.DED, 0.2
W = 15.0
Y_MOT0 = YM - 13.9                                                                 # передний край мотора (1.6)
Y_P1 = Y_MOT0                                                                      # площадка целиком перед мотором
Y_P0 = Y_P1 - W
ZB, ZT = L2[1] + 0.15, R.Z_PD1                                                     # низ и верх тележки
# балка-хвост за мотором (под серединой площадки), колонны по краям
Y_BC = (Y_P0 + Y_P1) / 2
BM_B, BM_T = 3.0, 5.0
beam = PX([(Y_BC - BM_B / 2, L2[0]), (Y_BC + BM_B / 2, L2[0]), (Y_BC + BM_T / 2, L2[1]), (Y_BC - BM_T / 2, L2[1])], -HALF, HALF)
base = V.base_o + BB(-HALF, HALF, Y_P0 - 1.0, Y_MOT0 + 0.01 - 1.1, 0, T.Z_FL)     # пол вперёд под балку
for sx in (-1, 1):
    base += BB(*sorted((sx * 21.0, sx * HALF)), Y_BC - 1.5, Y_BC + 1.5, T.Z_FL - 0.01, L2[0] + 0.01)
# тележка: рейка у шестерён + плита вперёд + площадка + крючки вокруг балки
cart = rack(-CW, CW, K.Y_FIX - 0.05, 1, L2[0], L2[1] + 0.16, 0.3)
Y_RB = K.Y_FIX - 0.05 - DED - 0.3
cart += BB(-CW, CW, Y_P0, Y_RB + DED + 0.3 + 0.8, ZB, ZT)                           # плита от площадки до рейки
for sg in (1, -1):
    pts = [(Y_BC + sg * (BM_B / 2 + C), L2[0]), (Y_BC + sg * (BM_B / 2 + C + 1.2), L2[0]), (Y_BC + sg * (BM_T / 2 + C + 1.2), L2[1] + 0.16),
           (Y_BC + sg * (BM_T / 2 + C + 1.2), ZB + 0.5), (Y_BC + sg * (BM_T / 2 + C), ZB + 0.5), (Y_BC + sg * (BM_T / 2 + C), L2[1])]
    cart += PX(pts if sg < 0 else pts[::-1], -CW, CW)

if __name__ == "__main__":
    def iv(a, b):
        try:
            r = a & b
            return 0.0 if r is None else r.volume
        except Exception:
            return 0.0
    st = {"основание": base, "рейка": V.fix_o, "брусок": K.beam, "мотор": K.motor, "балка": beam}
    bad = 0
    for s in (-S, -5.5, 0, 5.5, S):
        rf = math.degrees(s / RF)
        mv = {"ползун": Pos(s, 0, 0) * K.sl, "плав1": Pos(s - A, K.Y_G, 0) * Rot(0, 0, rf) * K.flo0, "плав2": Pos(s + A, K.Y_G, 0) * Rot(0, 0, rf) * K.flo0,
              "шестерня": Pos(0, YM, 0) * Rot(0, 0, math.degrees(s / RM)) * K.gm}
        c = Pos(2 * s, 0, 0) * cart
        for n, p in {**st, **mv}.items():
            v = iv(c, p)
            if v > 0.05: bad += 1; print("  s=%+.1f тележка × %s %.2f" % (s, n, v))
        for n in ("плав1", "плав2", "ползун"):
            for m in ("рейка", "основание", "балка"):
                v = iv(mv[n], st[m])
                if v > 0.05: bad += 1; print("  s=%+.1f %s × %s %.2f" % (s, n, m, v))
    if iv(Pos(0, 0, 0.6) * cart, beam) < 0.01:
        bad += 1; print("  тележка поднимается")
    print("модуль «тележка за мотором»: %s; площадка y %.1f…%.1f, край мотора %.1f; модуль вдоль струн %.1f" % (
        "ЧИСТО" if not bad else "%d проблем" % bad, Y_P0, Y_P1, Y_MOT0, base.bounding_box().size.Y))
    for n, p in (("base", base), ("fix", V.fix_o), ("beam_k", K.beam), ("beam", beam), ("motor", K.motor), ("slider", K.sl), ("flo", K.flo0),
                 ("cart", cart), ("gm", K.gm), ("plat", K.plat)):
        export_stl(Part() + p, "asm_zm/%s.stl" % n, tolerance=0.02, angular_tolerance=0.2)
    print("asm_zm готово")
