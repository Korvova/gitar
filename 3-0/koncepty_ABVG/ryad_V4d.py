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
# 19.11, владелец: шаг всех пальцев одинаковый и меньше 24. Модули П в середине — шестернями друг к другу, ближе 30.4 их не поставить
# (ползуны), поэтому шаг 17: моторы П на ±15.2, площадки П на ±8.5, площадки З на ±25.5, моторы З — от своих площадок.
PITCH = float(os.environ.get("PITCH", "17.0"))
CM_H = float(os.environ.get("CM_H", "15.2"))
C_Z = (Z.Y_P0 + Z.Y_P1) / 2                                                        # центр площадки З (за мотором)
C_H = YM - (CM_H - PITCH / 2)                                                      # центр площадки П на тележке (8.8)
PADC = [-1.5 * PITCH, -0.5 * PITCH, 0.5 * PITCH, 1.5 * PITCH]
ROT = [True, True, False, False]
TYPE = ["З", "П", "П", "З"]


def motor_for(i):
    c = C_Z if TYPE[i] == "З" else C_H
    return PADC[i] + (c - YM) if ROT[i] else PADC[i] - (c - YM)


CM = [motor_for(i) for i in range(4)]
pad_H = BB(-CW, CW, C_H - W / 2, C_H + W / 2, R.Z_PD0, R.Z_PD1) + BB(-CW, CW, V.Y_CO0, V.YB_R + V.DT + 1.4, R.Z_T - 0.01, R.Z_PD0 + 0.01)
cart_H = V.cart_o + pad_H


# --- клик модуля «П» (19.11): стойки 49E у П повёрнуты (33.75° / 236.25°), место под концами рейки свободно.
# Неподвижная рейка (по её спинке едет тележка П) + 2 колонны прямо вниз = одна деталь; перевёрнутая «Т» в стакане на кнопке Ø6.
XCP, YCP = Z.XCB, 13.9                                                           # стакан под концом рейки (по центру гнезда, гнездо не заходит под ползун)
base_P = V.base_o
for sx in (-1, 1):
    base_P -= BB(*sorted((sx * 23.6, sx * (HALF + 1))), V.Y_FO - 0.4, V.YB_R + 0.1, T.Z_FL + 0.01, T.L2[0] + 1)   # старые стойки рейки
fix_P, btns_P, legs_P, fix_P_body = V.fix_o, Part(), Part(), V.fix_o
for sx in (-1, 1):
    base_P += Z.cup_at(sx * XCP, YCP)
    btns_P += Z.btn_at(sx * XCP, YCP)
    if Z.KLAV2:
        base_P -= Z.sock_cut(sx * XCP, YCP)
    fix_P_body += Z.socket_at(sx * XCP, YCP - 1.9, YCP + 1.9, T.L2[0])           # гнездо под колонну (ножка — отдельная деталь, на клей)
    legs_P += Z.leg_place(sx * XCP, YCP, Z.leg0)

fix_P = fix_P_body + legs_P                                                       # в сборе (для проверок)

def place(i, p):
    return Pos(0, CM[i], 0) * (Rot(0, 0, 180) if ROT[i] else Rot(0, 0, 0)) * Pos(0, -YM, 0) * p


def stat(i):
    if TYPE[i] == "З":
        d = {"основание": Z.base, "рейка": V.fix_o, "брусок": K.beam, "мотор": K.motor, "балка": Z.beam}
    else:
        d = {"основание": base_P, "рейка": fix_P, "брусок": K.beam, "мотор": K.motor}
    return {k: place(i, v) for k, v in d.items()}


def moving(i, s):
    rf = math.degrees(s / RF)
    cart = Z.cart if TYPE[i] == "З" else cart_H
    d = {"ползун": Pos(s, 0, 0) * K.sl, "плав1": Pos(s - A, K.Y_G, 0) * Rot(0, 0, rf) * K.flo0, "плав2": Pos(s + A, K.Y_G, 0) * Rot(0, 0, rf) * K.flo0,
         "тележка": Pos(2 * s, 0, 0) * cart, "шестерня": Pos(0, YM, 0) * Rot(0, 0, math.degrees(s / RM)) * K.gm}
    return {k: place(i, v) for k, v in d.items()}


filler = BB(-HALF, HALF, CM[1] + 15.0 - 0.01, CM[2] - 15.0 + 0.01, 0, T.Z_FL)
base_row = Part() + [stat(i)["основание"] for i in range(4)] + [filler]
import datchiki_bok as DB                                                         # прорези под стойки 49E — в общем основании ряда
SLOTS = [place(i, Part() + (DB.slots_p if TYPE[i] == "П" else DB.slots_z)) for i in range(4)]
for sl_ in SLOTS:
    base_row -= sl_

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
    for i in range(4):                                                             # стойки 49E своего типа × детали модуля
        pp = DB.posts_p if TYPE[i] == "П" else DB.posts_z
        for nm, q in stat(i).items():
            if nm == "основание": continue
            v = iv(place(i, pp), q)
            if v > 0.05: bad += 1; print("  модуль %d: стойки 49E × %s %.2f" % (i + 1, nm, v))
        for s_ in (-S, 0, S):
            for nm, q in moving(i, s_).items():
                v = iv(place(i, pp), q)
                if v > 0.05: bad += 1; print("  модуль %d s=%+.0f: стойки 49E × %s %.2f" % (i + 1, s_, nm, v))
    for i in range(3):                                                             # неподвижные соседних модулей + стойки 49E соседей
        a_, b_ = stat(i), stat(i + 1)
        a_["стойки"] = place(i, DB.posts_p if TYPE[i] == "П" else DB.posts_z); b_["стойки"] = place(i + 1, DB.posts_p if TYPE[i + 1] == "П" else DB.posts_z)
        for na, pa in a_.items():
            for nb, pb in b_.items():
                if na == "основание" and nb == "основание": continue
                if na == "основание": pa = pa - SLOTS[i + 1]
                if nb == "основание": pb = pb - SLOTS[i]
                v = iv(pa, pb)
                if v > 0.05: bad += 1; print("  неподв. %d/%d: %s × %s %.2f" % (i + 1, i + 2, na, nb, v))
    for i in (1, 2):
        v = iv(Pos(0, 0, -0.3) * place(i, fix_P), place(i, base_P))
        if v > 0.05: bad += 1; print("  П%d нажато × основание %.2f" % (i + 1, v))
    bb = base_row.bounding_box()
    print("ряд З П | П З: %s; моторы на %s; площадки на %s; длина платформы %.1f; высота до верха площадок %.1f" % (
        "ЧИСТО" if not bad else "%d проблем" % bad, ["%.1f" % c for c in CM], PADC, bb.size.Y, R.Z_PD1))
    for n, p in (("base_row", base_row), ("fix", V.fix_o), ("fix_p", fix_P), ("btns_p", btns_P), ("beam_k", K.beam), ("beam_z", Z.beam), ("motor", K.motor), ("slider", K.sl), ("flo", K.flo0),
                 ("cart_z", Z.cart), ("cart_h", cart_H), ("gm", K.gm), ("plat", K.plat)):
        export_stl(Part() + p, "asm_V4d/%s.stl" % n, tolerance=0.02, angular_tolerance=0.2)
    open("asm_V4d/params.txt", "w").write(" ".join("%f" % v for v in CM + [YM, K.Y_G]))
    print("asm_V4d готово")
