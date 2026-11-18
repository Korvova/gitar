# -*- coding: utf-8 -*-
r"""Ряд В×4, вариант Б (19.11.2026, владелец): у крайних модулей тележка переехала вперёд, на сторону шестерён
(рейки поменяны местами, неподвижная рейка — за шестернями на своих стойках, её спинка — хвост, за неё держится губа тележки),
мост над мотором им не нужен. Крайние модули смотрят шестернями к середине: левый развёрнут на 180°, правый стоит как есть.
Площадки крайних почти над своей тележкой. Средние модули — как в ryad_V4.py.
Запуск из этой папки: ..\..\2-0\.venv-b123d\Scripts\python ryad_V4b.py
"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from build123d import *
import ryad_V4 as R
K, T = R.K, R.T
os.chdir(HERE); os.makedirs("asm_V4b", exist_ok=True)
BB, CZ, PX, rack = T.BB, T.CZ, T.prof_x, T.rack
S, A, RF, RM, YM, CW, HALF, L2 = T.S, T.A, T.RF, T.RM, T.YM, T.CW, T.HALF, T.L2
DED, DT, C = K.DED, 1.0, 0.2
W, Z_T, Z_PD0, Z_PD1 = R.W, R.Z_T, R.Z_PD0, R.Z_PD1
P12 = 30.4                                                                         # крайний к соседнему: шестернями друг к другу
CM = [-36.0 - P12 / 2 - 0, -36.0 + P12 / 2, 36.0 - P12 / 2, 36.0 + P12 / 2]       # площадка 1 — на стыке моторов 1 и 2 (владелец 19.11)                                       # вторая пара — зеркало первой (владелец 19.11)                                              # оси моторов
ROT = [True, False, True, False]
PADC = [-36.0, -12.0, 12.0, 36.0]                                                  # центры площадок (шаг 24)

# ---------------- крайний модуль (в локальных координатах концепта В) ----------------
Y_FO = K.Y_CART                                                                    # неподвижная рейка за шестернями, зубья к ним (−y)
fix_o = rack(-HALF, HALF, Y_FO, -1, L2[0], L2[1], 1.4)
YB_R = Y_FO + DED + 1.4                                                            # спинка рейки
fix_o += PX([(YB_R - 0.01, L2[0]), (YB_R, L2[0]), (YB_R + DT, L2[1]), (YB_R - 0.01, L2[1])], -HALF, HALF)   # спинка — хвост
base_o = R.base1
for sx in (-1, 1):
    base_o += BB(*sorted((sx * 23.7, sx * HALF)), Y_FO - 0.3, YB_R, T.Z_FL - 0.01, L2[0] - 0.01)          # стойки под концы рейки
Z_P0 = L2[1] + 0.2
cart_o = rack(-CW, CW, K.Y_FIX - 0.05, 1, L2[0], L2[1] + 0.16, 0.3)               # рейка тележки перед шестернями, зубья к ним (+y)
Y_CO0 = K.Y_FIX - 0.05 - DED - 0.3
cart_o += BB(-CW, CW, Y_CO0, YB_R + DT + 1.4, L2[1] + 0.15, Z_T)                 # плита над шестернями до губы
cart_o += PX([(YB_R + 0.2, L2[0]), (YB_R + 1.4, L2[0]), (YB_R + DT + 1.4, L2[1] + 0.16), (YB_R + DT + 1.4, Z_P0 + 0.01),
              (YB_R + DT + 0.2, Z_P0 + 0.01), (YB_R + DT + 0.2, L2[1] + 0.16)], -CW, CW)                    # губа за спинку рейки


# передняя балка для левого крайнего (площадка свисает вперёд на ~5 мм): колонны на передних стойках, балка под площадкой
ZBM0, ZBM1 = L2[1] + 0.4, Z_T
cols_f = None
for sx in (-1, 1):
    c_ = BB(*sorted((sx * 23.7, sx * HALF)), 0.5, Y_CO0 - 0.09, L2[0] - 0.01, ZBM0 + 0.01)
    cols_f = c_ if cols_f is None else cols_f + c_
beam_f = BB(-HALF, HALF, -6.6, Y_CO0 - 0.09, ZBM0, ZBM1)                           # под всем свесом площадки


Y_CM1 = 28.6                                                                       # средняя тележка удлинена назад, к своей площадке
cart_m = K.cart + BB(-CW, CW, R.YC1 - 0.01, Y_CM1, K.Z_P0, Z_T)


def pad_m(i):
    yc = local_pad_center(i)
    return BB(-CW, CW, yc - W / 2, yc + W / 2, Z_PD0, Z_PD1) + BB(-CW, CW, R.YC0, Y_CM1, Z_T - 0.01, Z_PD0 + 0.01)


def local_pad_center(i):
    return YM + (CM[i] - PADC[i]) if ROT[i] else PADC[i] - CM[i] + YM


def pad_o(i):
    yc = local_pad_center(i)
    p = BB(-CW, CW, yc - W / 2, yc + W / 2, Z_PD0, Z_PD1)
    p += BB(-CW, CW, Y_CO0, YB_R + DT + 1.4, Z_T - 0.01, Z_PD0 + 0.01)
    return p


def place(i, p):
    t = Pos(0, CM[i], 0) * (Rot(0, 0, 180) if ROT[i] else Rot(0, 0, 0)) * Pos(0, -YM, 0)
    return t * p


OUT = (0, 3)
pads = {0: pad_o(0), 3: pad_o(3), 1: pad_m(1), 2: pad_m(2)}


def stat(i):
    if i in OUT:
        d = {"основание": base_o + cols_f, "рейка": fix_o, "брусок": K.beam, "мотор": K.motor}
        d["балка"] = beam_f
    else:
        d = {"основание": R.base1, "рейка": K.fix, "брусок": K.beam, "мост": K.most, "мотор": K.motor}
    return {k: place(i, v) for k, v in d.items()}


def moving(i, s):
    sg = 1 if i in OUT else -1
    rf = sg * math.degrees(s / RF)
    cart = (cart_o if i in OUT else cart_m) + pads[i]
    d = {"ползун": Pos(s, 0, 0) * K.sl, "плав1": Pos(s - A, K.Y_G, 0) * Rot(0, 0, rf) * K.flo0, "плав2": Pos(s + A, K.Y_G, 0) * Rot(0, 0, rf) * K.flo0,
         "тележка": Pos(2 * s, 0, 0) * cart, "шестерня": Pos(0, YM, 0) * Rot(0, 0, math.degrees(s / RM)) * K.gm}
    return {k: place(i, v) for k, v in d.items()}


fillers = [BB(-HALF, HALF, CM[k] + 15.0 - 0.01, CM[k + 1] - 15.0 + 0.01, 0, T.Z_FL) for k in range(3)]
base_row = Part() + [stat(i)["основание"] for i in range(4)] + fillers

if __name__ == "__main__":
    def iv(a, b):
        try:
            r = a & b
            return 0.0 if r is None else r.volume
        except Exception:
            return 0.0
    bad = 0
    for i in OUT:                                                                  # свой модуль: новая тележка по всему ходу
        for s in (-S, -5.5, 0, 5.5, S):
            m, st = moving(i, s), stat(i)
            for a in ("тележка",):
                for b, pb in {**st, **{k: v for k, v in m.items() if k != a}}.items():
                    v = iv(m[a], pb)
                    if v > 0.05: bad += 1; print("  модуль %d s=%+.1f %s × %s %.2f" % (i + 1, s, a, b, v))
            for a in ("ползун", "плав1", "плав2"):
                for b in ("рейка", "основание"):
                    v = iv(m[a], st[b])
                    if v > 0.05: bad += 1; print("  модуль %d s=%+.1f %s × %s %.2f" % (i + 1, s, a, b, v))
        if iv(Pos(0, 0, -0.3) * moving(i, 0)["тележка"], stat(i)["балка"]) < 0.01:
            print("  внимание: площадка левого крайнего не ложится на балку")
        if iv(Pos(0, 0, 0.6) * moving(i, 0)["тележка"], stat(i)["рейка"]) < 0.01:
            bad += 1; print("  модуль %d: тележка поднимается" % (i + 1))
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
    print("ряд В×4 Б: %s; площадки на %s; длина платформы %.1f, высота до верха площадок %.1f" % ("ЧИСТО" if not bad else "%d проблем" % bad, PADC, bb.size.Y, Z_PD1))
    for n, p in (("base_row", base_row), ("fix", K.fix), ("fix_o", fix_o), ("beam", K.beam), ("most", K.most), ("motor", K.motor), ("slider", K.sl),
                 ("flo", K.flo0), ("cart", cart_m), ("cart_o", cart_o), ("gm", K.gm), ("plat", K.plat), ("beam_f", place(0, beam_f) + place(3, beam_f))):
        export_stl(Part() + p, "asm_V4b/%s.stl" % n, tolerance=0.02, angular_tolerance=0.2)
    for i in range(4):
        export_stl(Part() + pads[i], "asm_V4b/pad%d.stl" % i, tolerance=0.02, angular_tolerance=0.2)
    open("asm_V4b/params.txt", "w").write(" ".join("%f" % v for v in CM + [YM, K.Y_G]))
    print("asm_V4b готово")
