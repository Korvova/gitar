# -*- coding: utf-8 -*-
r"""Ряд на 4 пальца из пар (19.11.2026, владелец): в паре модуль «З» — тележка целиком за краем своего мотора, на балке
(modul_za_motorom.py), и модуль «П» — тележка на половине своего мотора (над шестернями, губа за спинку неподвижной рейки).
Порядок З1 П1 | П2 З2: тележка З1 уходит вперёд за свой мотор к модулю П1; модули П в середине смотрят шестернями друг к другу.
Площадки на шаге 24. Запуск: ..\..\2-0\.venv-b123d\Scripts\python ryad_V4d.py
"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from build123d import *
import modul_za_motorom as Z
V, K, T, R = Z.V, Z.K, Z.T, Z.R
os.chdir(HERE); os.makedirs("asm_V4d", exist_ok=True)
BB, CZ = T.BB, T.CZ
S, A, RF, RM, YM, CW, HALF = T.S, T.A, T.RF, T.RM, T.YM, T.CW, T.HALF
W = 15.0
C_H = (V.Y_CO0 + V.YB_R + V.DT + 1.4) / 2                                         # центр тележки П (площадка целиком на ней)
C_Z = (Z.Y_P0 + Z.Y_P1) / 2                                                        # центр площадки З (за мотором)
PADC = [-36.0, -12.0, 12.0, 36.0]
ROT = [True, True, False, False]
TYPE = ["З", "П", "П", "З"]


def motor_for(i):
    c = C_Z if TYPE[i] == "З" else C_H
    return PADC[i] + (c - YM) if ROT[i] else PADC[i] - (c - YM)


CM = [motor_for(i) for i in range(4)]
SHIFT_Z = 5.0                                                                      # крайние модули З ближе к П на 5 мм вместе с балкой (владелец 19.11)
CM[0] += SHIFT_Z; CM[3] -= SHIFT_Z
PADC = [PADC[0] + SHIFT_Z, PADC[1], PADC[2], PADC[3] - SHIFT_Z]
pad_H = BB(-CW, CW, C_H - W / 2, C_H + W / 2, R.Z_PD0, R.Z_PD1) + BB(-CW, CW, V.Y_CO0, V.YB_R + V.DT + 1.4, R.Z_T - 0.01, R.Z_PD0 + 0.01)
cart_H = V.cart_o + pad_H


def place(i, p):
    return Pos(0, CM[i], 0) * (Rot(0, 0, 180) if ROT[i] else Rot(0, 0, 0)) * Pos(0, -YM, 0) * p


def stat(i):
    if TYPE[i] == "З":
        d = {"основание": Z.base, "рейка": V.fix_o, "брусок": K.beam, "мотор": K.motor, "балка": Z.beam}
    else:
        d = {"основание": V.base_o, "рейка": V.fix_o, "брусок": K.beam, "мотор": K.motor}
    return {k: place(i, v) for k, v in d.items()}


def moving(i, s):
    rf = math.degrees(s / RF)
    cart = Z.cart if TYPE[i] == "З" else cart_H
    d = {"ползун": Pos(s, 0, 0) * K.sl, "плав1": Pos(s - A, K.Y_G, 0) * Rot(0, 0, rf) * K.flo0, "плав2": Pos(s + A, K.Y_G, 0) * Rot(0, 0, rf) * K.flo0,
         "тележка": Pos(2 * s, 0, 0) * cart, "шестерня": Pos(0, YM, 0) * Rot(0, 0, math.degrees(s / RM)) * K.gm}
    return {k: place(i, v) for k, v in d.items()}


filler = BB(-HALF, HALF, CM[1] + 15.0 - 0.01, CM[2] - 15.0 + 0.01, 0, T.Z_FL)
base_row = Part() + [stat(i)["основание"] for i in range(4)] + [filler]

if __name__ == "__main__":
    def iv(a, b):
        try:
            r = a & b
            return 0.0 if r is None else r.volume
        except Exception:
            return 0.0
    bad = 0
    for i in (1,):                                                                  # модуль П: тележка с площадкой по ходу (З проверен отдельно)
        for s in (-S, -5.5, 0, 5.5, S):
            m, st = moving(i, s), stat(i)
            for b, pb in {**st, **{k: v for k, v in m.items() if k != "тележка"}}.items():
                v = iv(m["тележка"], pb)
                if v > 0.05: bad += 1; print("  П s=%+.1f тележка × %s %.2f" % (s, b, v))
        if iv(Pos(0, 0, 0.6) * moving(i, 0)["тележка"], stat(i)["рейка"]) < 0.01:
            bad += 1; print("  П: тележка поднимается")
    for i in range(3):
        for s1 in (-S, 0, S):
            for s2 in (-S, 0, S):
                m1, m2 = moving(i, s1), moving(i + 1, s2)
                for a, pa in m1.items():
                    for b, pb in {**m2, **stat(i + 1)}.items():
                        v = iv(pa, pb)
                        if v > 0.05: bad += 1; print("  модули %d/%d s=%+.0f/%+.0f %s × %s %.2f" % (i + 1, i + 2, s1, s2, a, b, v))
                for a, pa in m2.items():
                    for b, pb in stat(i).items():
                        v = iv(pa, pb)
                        if v > 0.05: bad += 1; print("  модули %d/%d s=%+.0f/%+.0f %s × %s %.2f" % (i + 2, i + 1, s2, s1, a, b, v))
    bb = base_row.bounding_box()
    print("ряд З П | П З: %s; моторы на %s; площадки на %s; длина платформы %.1f; высота до верха площадок %.1f" % (
        "ЧИСТО" if not bad else "%d проблем" % bad, ["%.1f" % c for c in CM], PADC, bb.size.Y, R.Z_PD1))
    for n, p in (("base_row", base_row), ("fix", V.fix_o), ("beam_k", K.beam), ("beam_z", Z.beam), ("motor", K.motor), ("slider", K.sl), ("flo", K.flo0),
                 ("cart_z", Z.cart), ("cart_h", cart_H), ("gm", K.gm), ("plat", K.plat)):
        export_stl(Part() + p, "asm_V4d/%s.stl" % n, tolerance=0.02, angular_tolerance=0.2)
    open("asm_V4d/params.txt", "w").write(" ".join("%f" % v for v in CM + [YM, K.Y_G]))
    print("asm_V4d готово")
