# -*- coding: utf-8 -*-
r"""Концепт В в ряд на 4 пальца (18.11.2026, владелец): без колпака с магнитами, модули с шагом 30 как на столе 116,
площадки 15 мм сдвинуты на ±3 и ±9 — пальцы на шаге 24. Воротник мотора срезан по ±15 от оси, соседние основания сливаются.
Датчик положения пока не рисуем (потом — по схеме 116: 3×49E в платформе, 2 магнита на тележке).
Запуск из этой папки: ..\..\2-0\.venv-b123d\Scripts\python ryad_V4.py
"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from build123d import *
import koncept_C as K
T = K.T
os.chdir(HERE); os.makedirs("asm_V4", exist_ok=True)
BB, CZ = T.BB, T.CZ
S, A, RF, RM, YM, CW = T.S, T.A, T.RF, T.RM, T.YM, T.CW
P = 30.0                                                                           # шаг модулей
PF = 24.0                                                                          # шаг пальцев
W = 15.0                                                                           # площадка вдоль струн
base1 = K.base & BB(-T.HALF - 1, T.HALF + 1, YM - P / 2, YM + P / 2, -1, 40)
cb = K.cart.bounding_box()
YC0, YC1 = K.Y_CART + K.DED, K.Y_CB + 2.0                                          # верх тележки
YCC = (YC0 + YC1) / 2
Z_T = K.Z_P1                                                                       # верх тележки 28.1
Z_PD0, Z_PD1 = Z_T + 0.2, Z_T + 1.8                                                # площадка над соседними тележками


def pad_part(d):
    """площадка со сдвигом d вдоль струн + подставка над своей тележкой"""
    p = BB(-CW, CW, YCC + d - W / 2, YCC + d + W / 2, Z_PD0, Z_PD1)
    p += BB(-CW, CW, YC0, YC1, Z_T - 0.01, Z_PD0 + 0.01)
    return p


YS = [(i - 1.5) * P - YM for i in range(4)]                                       # сдвиг модуля: ось мотора на (i−1.5)·30
SH = [-(i - 1.5) * (P - PF) for i in range(4)]                                     # сдвиги площадок: +9, +3, −3, −9
pads = [pad_part(d) for d in SH]
row = base1
for y in YS[1:]:
    pass
base_row = Part() + [Pos(0, y, 0) * base1 for y in YS]


def stat(i):
    y = YS[i]
    return {"рейка": Pos(0, y, 0) * K.fix, "брусок": Pos(0, y, 0) * K.beam, "мост": Pos(0, y, 0) * K.most, "мотор": Pos(0, y, 0) * K.motor}


def moving(i, s):
    y = YS[i]; rf = -math.degrees(s / RF)
    return {"ползун": Pos(s, y, 0) * K.sl, "плав1": Pos(s - A, y + K.Y_G, 0) * Rot(0, 0, rf) * K.flo0,
            "плав2": Pos(s + A, y + K.Y_G, 0) * Rot(0, 0, rf) * K.flo0, "тележка": Pos(2 * s, y, 0) * (K.cart + pads[i]),
            "шестерня": Pos(0, y + YM, 0) * Rot(0, 0, math.degrees(s / RM)) * K.gm}


if __name__ == "__main__":
    def iv(a, b):
        try:
            r = a & b
            return 0.0 if r is None else r.volume
        except Exception:
            return 0.0
    bad = 0
    for i in range(3):                                                             # соседи i и i+1, тележки в разных положениях
        for s1 in (-S, 0, S):
            for s2 in (-S, 0, S):
                m1, m2 = moving(i, s1), moving(i + 1, s2)
                for a, pa in m1.items():
                    for b, pb in {**m2, **stat(i + 1), "основание": Pos(0, YS[i + 1], 0) * base1}.items():
                        v = iv(pa, pb)
                        if v > 0.05: bad += 1; print("  модули %d/%d s=%+.0f/%+.0f %s × %s %.2f" % (i + 1, i + 2, s1, s2, a, b, v))
                for a, pa in m2.items():
                    for b, pb in {**stat(i), "основание": Pos(0, YS[i], 0) * base1}.items():
                        v = iv(pa, pb)
                        if v > 0.05: bad += 1; print("  модули %d/%d s=%+.0f/%+.0f %s × %s %.2f" % (i + 2, i + 1, s2, s1, a, b, v))
    for i in range(4):                                                             # своя площадка по ходу
        for s in (-S, 0, S):
            m = moving(i, s)
            for b, pb in {**stat(i), "основание": Pos(0, YS[i], 0) * base1}.items():
                v = iv(Pos(2 * s, YS[i], 0) * pads[i], pb)
                if v > 0.05: bad += 1; print("  модуль %d s=%+.0f площадка × %s %.2f" % (i + 1, s, b, v))
    centers = [YS[i] + YCC + SH[i] for i in range(4)]
    print("ряд В×4: %s; шаг модулей %.0f, площадки на %s (шаг %s); длина платформы %.1f; высота до верха площадок %.1f" % (
        "ЧИСТО" if not bad else "%d проблем" % bad, P, ["%.1f" % c for c in centers], ["%.1f" % (centers[k + 1] - centers[k]) for k in range(3)],
        4 * P, Z_PD1))
    for n, p in (("base_row", base_row), ("fix", K.fix), ("beam", K.beam), ("most", K.most), ("motor", K.motor), ("slider", K.sl), ("flo", K.flo0),
                 ("cart", K.cart), ("gm", K.gm), ("plat", K.plat)):
        export_stl(Part() + p, "asm_V4/%s.stl" % n, tolerance=0.02, angular_tolerance=0.2)
    for i in range(4):
        export_stl(Part() + pads[i], "asm_V4/pad%d.stl" % i, tolerance=0.02, angular_tolerance=0.2)
    open("asm_V4/params.txt", "w").write(" ".join("%f" % v for v in YS + [YM, K.Y_G]))
    print("asm_V4 готово")
