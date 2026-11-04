# -*- coding: utf-8 -*-
r"""Кассета владельца (04.11.2026) — проба хода тележки на своём FDM-принтере, пока нет мотора: детали из STEP автора,
оси плавающих шестерён — кусок прутка филамента 1.75 вместо штифтов Ø1.5 (дырки в ползуне под посадку 1.75 — Ø1.85
с учётом усадки FDM; отверстие плавающей шестерни Ø2.0 — вращается свободно). Остальное как у автора.
Модуль зуба 0.5 — на сопле 0.4 зубья выйдут грубыми: проба кинематики, не финал (финал — фотополимер).
Запуск: ..\.venv-b123d\Scripts\python fdm_kasseta.py
"""
import math
import os
from build123d import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "Print", "Print")
P = math.pi * 0.5
SP_FLOAT, Y_FLOAT = 5 * P, 6.0


def load(n):
    return import_step(os.path.join(HERE, n + ".step"))


sld = load("04_polzun")
for x in (-SP_FLOAT / 2, SP_FLOAT / 2):
    sld = sld - Pos(x, Y_FLOAT, 0) * Cylinder(1.85 / 2, 200)          # ось-пруток 1.75 в посадку
flo = load("03_shesternya_plav_Z12") - Cylinder(1.0, 50)                 # Ø2.0 — свободно на прутке 1.75

parts = [("kas_osnovanie", load("01_osnovanie")), ("kas_shesternya_motora", load("02_shesternya_motora_Z18")),
         ("kas_plav_fdm", flo), ("kas_polzun_fdm", sld), ("kas_telezhka", load("05_telezhka")), ("kas_upor", load("06_upor_paza"))]
for n, p in parts:
    p = Part() + p
    bb = p.bounding_box()
    print("%s: %.1f x %.1f x %.1f, solids %d" % (n, bb.size.X, bb.size.Y, bb.size.Z, len(p.solids())))
    export_stl(p, os.path.join(OUT, n + ".stl"))
