# -*- coding: utf-8 -*-
r"""Проверка кассеты владельца (04.11.2026, cassette_parametry.py, телескоп m0.5): тележка по всему ходу ±24 —
пересечения зубьев и деталей (объём, мм³) в положениях как в placed() автора. Детали — STEP из архива.
Запуск: ..\.venv-b123d\Scripts\python proverka_kasseta.py
"""
import math
import os
from build123d import *

HERE = os.path.dirname(os.path.abspath(__file__))
Y_PIN, Y_FLOAT = 16.5, 6.0
P = math.pi * 0.5
SP_FLOAT = 5 * P
Z_GEAR0 = 1.2 + 17.5 + 0.1


def load(n):
    return import_step(os.path.join(HERE, n + ".step"))


base, pin, flo, sld, cart = (load(n) for n in ("01_osnovanie", "02_shesternya_motora_Z18", "03_shesternya_plav_Z12",
                                               "04_polzun", "05_telezhka"))


def placed(d):
    s = d / 2
    a_f, a_p = -math.degrees(s / 3.0), math.degrees(s / 4.5)
    out = {"основание": base,
           "шестерня мотора": Pos(0, Y_PIN, Z_GEAR0) * Rot(0, 0, -a_p) * pin,
           "ползун": Pos(s, 0, 0) * sld,
           "тележка": Pos(d, 0, 0) * cart}
    for i, x in enumerate((-SP_FLOAT / 2, SP_FLOAT / 2)):
        out["плав%d" % i] = Pos(x + s, Y_FLOAT, Z_GEAR0 + 0.1) * Rot(0, 0, -a_f) * flo
    return out


PAIRS = [("шестерня мотора", "ползун"), ("шестерня мотора", "основание"), ("плав0", "основание"), ("плав1", "основание"),
         ("плав0", "тележка"), ("плав1", "тележка"), ("плав0", "ползун"), ("плав1", "ползун"), ("плав0", "плав1"),
         ("ползун", "основание"), ("тележка", "основание"), ("тележка", "ползун"), ("шестерня мотора", "плав0"),
         ("шестерня мотора", "плав1"), ("шестерня мотора", "тележка")]
worst = {p: (0.0, None) for p in PAIRS}
for d in (-24, -18, -12.3, -6, -1.1, 0, 0.7, 3.3, 9, 15.5, 21, 24):
    pl = placed(d)
    for a, b in PAIRS:
        v = (Part() + (pl[a] & pl[b])).volume
        if v > worst[(a, b)][0]:
            worst[(a, b)] = (v, d)
for (a, b), (v, d) in worst.items():
    print("%-16s × %-16s  %s" % (a, b, "чисто" if v < 0.01 else "ПЕРЕСЕЧЕНИЕ %.3f мм³ при d = %+.1f" % (v, d)))
