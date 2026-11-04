# -*- coding: utf-8 -*-
r"""Кассета владельца (04.11.2026) — проба хода тележки на своём FDM-принтере, пока нет мотора: детали из STEP автора,
оси плавающих шестерён — штырьки Ø2 заодно с ползуном (отверстие шестерни Ø2.4); шестерни лежат на полке-мостике
основания над мотором, сверху их держит ползун (04.11, идея владельца). Остальное как у автора.
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


Z_GEAR0, Z_PLATE0, Z_PLATE1 = 1.2 + 17.5 + 0.1, 22.3, 23.5
# 04.11 (владелец): плавающие шестерни лежат на полке основания, а оси-штырьки — заодно с ползуном (без прутков)
sld = load("04_polzun")
for x in (-SP_FLOAT / 2, SP_FLOAT / 2):
    sld = sld + Pos(x, Y_FLOAT, (Z_GEAR0 + 0.3 + Z_PLATE1) / 2) * Cylinder(1.0, Z_PLATE1 - Z_GEAR0 - 0.3)   # штырёк Ø2 до 0.3 над полкой
flo = load("03_shesternya_plav_Z12") - Cylinder(1.2, 50)                 # Ø2.4 — свободно на штырьке Ø2
# полка-мостик под плавающими шестернями во весь их ход (x ±20.5), над мотором (верх мотора 15.2) — под ней пусто;
# верх полки = низ рейки 18.8: шестерня (18.9 … 22.1) лежит на ней с зазором 0.1, сверху ползун (22.3) — не соскочит
SHELF = Pos(0, (3.8 + 8.6) / 2, (15.6 + Z_GEAR0) / 2) * Box(41.0, 8.6 - 3.8, Z_GEAR0 - 15.6)
base = load("01_osnovanie") + SHELF

parts = [("kas_osnovanie", base), ("kas_shesternya_motora", load("02_shesternya_motora_Z18")),
         ("kas_plav_fdm", flo), ("kas_polzun_fdm", sld), ("kas_telezhka", load("05_telezhka")), ("kas_upor", load("06_upor_paza"))]
for n, p in parts:
    p = Part() + p
    bb = p.bounding_box()
    print("%s: %.1f x %.1f x %.1f, solids %d" % (n, bb.size.X, bb.size.Y, bb.size.Z, len(p.solids())))
    export_stl(p, os.path.join(OUT, n + ".stl"))

# ================= ПРОВЕРКА: полка и штырьки по всему ходу ±24 =================
Y_PIN = 16.5
pin = load("02_shesternya_motora_Z18")
cart = load("05_telezhka")
body = Pos(0, Y_PIN, 1.2 + 7.0) * Cylinder(11.0, 14.0)                 # мотор / макет мотора
boss = Pos(0, Y_PIN, 15.2 + 1.75) * Cylinder(4.75, 3.5)
bad = 0
for d in (-24, -16, -8, -2, 0, 3, 9, 17, 24):
    s_ = d / 2
    a_f, a_p = -math.degrees(s_ / 3.0), math.degrees(s_ / 4.5)
    pl = {"полка+основание": base, "ползун со штырьками": Pos(s_, 0, 0) * sld, "тележка": Pos(d, 0, 0) * cart,
          "шестерня мотора": Pos(0, Y_PIN, Z_GEAR0) * Rot(0, 0, -a_p) * pin, "мотор": body, "выступ": boss}
    for i, x in enumerate((-SP_FLOAT / 2, SP_FLOAT / 2)):
        pl["плав%d" % i] = Pos(x + s_, Y_FLOAT, Z_GEAR0 + 0.1) * Rot(0, 0, -a_f) * flo
    names = list(pl)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if {a, b} in ({"мотор", "полка+основание"}, {"мотор", "выступ"}, {"выступ", "шестерня мотора"}):
                continue                                            # посадки
            v = (Part() + (pl[a] & pl[b])).volume
            if v > 0.01:
                bad += 1
                print("ПЕРЕСЕЧЕНИЕ %s × %s: %.3f мм³ при d = %+d" % (a, b, v, d))
v = (Part() + (body & base)).volume
print("мотор × основание с полкой: %.3f мм³ (должно быть 0)" % v)
print("кассета FDM: %s" % ("чисто" if not bad and v < 0.01 else "ЕСТЬ ПЕРЕСЕЧЕНИЯ"))
