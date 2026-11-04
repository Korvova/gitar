# -*- coding: utf-8 -*-
r"""Макет мотора GB1806 для кассеты (04.11.2026), пока моторы едут: проверить силу хода тележки и люфт.
Габарит как у мотора без корпуса энкодера (так у автора кассеты): корпус Ø22 × 14 на основании (z 1.2 … 15.2), выступ
Ø9.5 × 3.5 (до z 18.7), шестерня Z18 садится на 4 штырька выступа (у автора — шпильки М2 на Ø6). Ось D-профиля Ø5
сквозь корпус и окно Ø9 в основании, снизу ручка: держишь ручку — шестерня стоит (люфт тележки), крутишь — едет.
Детали: корпус (дырки снизу под прутки — печать как стоит), выступ (штырьки вверх), ось (стоя),
ручка, подставка (кассета на 8 мм выше стола, U-окно под ручку). Всё без поддержек.
Запуск: ..\.venv-b123d\Scripts\python maket_motora.py
"""
import math
import os
from build123d import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "Print", "Print")
Y_PIN = 16.5
T_BASE = 1.2
Z_BODY1 = T_BASE + 14.0                 # верх корпуса
Z_BOSS1 = Z_BODY1 + 3.5                 # верх выступа (шестерня с 18.8)
KNOB_T, KNOB_GAP = 4.0, 1.0             # ручка под основанием
STAND_H = 8.0


def d_shape(r, flat):
    """D-профиль: круг r со срезом на расстоянии flat от центра (по +X)"""
    return Circle(r) - Pos(flat + r, 0) * Rectangle(2 * r, 4 * r)


# корпус: цилиндр с осевым отверстием. 04.11: штырьки вниз убраны — корпус задвигается в основание сбоку под стенку
# (зазор 0.3), штырьки 1 мм не пускали. Вместо них 4 глухие дырки Ø1.85 × 4 напротив дырок М2 основания (150, 210, 270,
# 330° на Ø18): когда корпус на месте, снизу сквозь основание вставить кусочки прутка 1.75 (капля клея)
body = Pos(0, 0, 7.0) * Cylinder(11.0, 14.0)
body -= Cylinder(2.6, 40)                                           # ось Ø5 — зазор 0.1 на сторону
for a in (150, 210, 270, 330):
    x, y = 9 * math.cos(math.radians(a)), 9 * math.sin(math.radians(a))
    body -= Pos(x, y, 2.0) * Cylinder(0.925, 4.0)
# выступ: Ø9.5 × 3.5, 4 штырька вверх Ø2.0 × 2.4 на Ø6 (0, 90, 180, 270°) — в глухие дырки шестерни, D-отверстие под ось
boss = Pos(0, 0, 1.75) * Cylinder(4.75, 3.5)
boss -= extrude(d_shape(2.55, 2.05), 3.6)
for a in (0, 90, 180, 270):
    boss += Pos(3 * math.cos(math.radians(a)), 3 * math.sin(math.radians(a)), 3.5 + 1.2) * Cylinder(1.0, 2.4)
# ось D Ø5 (срез на 2.0): от верха выступа вниз сквозь корпус, основание, зазор — и в ручку
AX_L = 3.5 + 14.0 + T_BASE + KNOB_GAP + KNOB_T
axle = extrude(d_shape(2.5, 2.0), AX_L)
# ручка: Ø20 с насечкой, D-отверстие
knob = Pos(0, 0, KNOB_T / 2) * Cylinder(10.0, KNOB_T)
for k in range(12):
    a = math.radians(30 * k)
    knob -= Pos(10.2 * math.cos(a), 10.2 * math.sin(a), KNOB_T / 2) * Cylinder(1.0, KNOB_T + 0.2)
knob -= extrude(d_shape(2.55, 2.05), KNOB_T + 0.1)
# подставка: рамка 50 × 24 высотой 8, U-окно под ручку (x ±12, от y 4 до края 24), штырьки в 4 дырки крепления
stand = Pos(0, 12, STAND_H / 2) * Box(50, 24, STAND_H)
stand -= Pos(0, 14 + 0.5, STAND_H / 2) * Box(24, 21, STAND_H + 1)
for x in (-23.5, 23.5):
    for y in (6, 18):
        stand += Pos(x, y, STAND_H + 0.5) * Cylinder(0.95, 1.0)

parts = [("kas_maket_korpus", body), ("kas_maket_vystup", boss), ("kas_maket_os", axle), ("kas_maket_ruchka", knob),
         ("kas_podstavka", stand)]
for n, p in parts:
    p = Part() + p
    bb = p.bounding_box()
    print("%s: %.1f x %.1f x %.1f, solids %d" % (n, bb.size.X, bb.size.Y, bb.size.Z, len(p.solids())))
    export_stl(p, os.path.join(OUT, n + ".stl"))

# ================= ПРОВЕРКА: макет на месте мотора, тележка по ходу ±24 =================
P = math.pi * 0.5
SP_FLOAT, Y_FLOAT, Z_GEAR0 = 5 * P, 6.0, T_BASE + 17.5 + 0.1


def load(n):
    return import_step(os.path.join(HERE, n + ".step"))


base, pin, flo, sld, cart = (load(n) for n in ("01_osnovanie", "02_shesternya_motora_Z18", "03_shesternya_plav_Z12",
                                               "04_polzun", "05_telezhka"))
mk = {"корпус макета": Pos(0, Y_PIN, T_BASE) * body,
      "выступ": Pos(0, Y_PIN, Z_BODY1) * boss,
      "ось": Pos(0, Y_PIN, Z_BOSS1 - AX_L) * axle,
      "ручка": Pos(0, Y_PIN, -KNOB_GAP - KNOB_T) * knob,
      "подставка": Pos(0, 0, -STAND_H) * stand}
bad = 0
for d in (-24, -12, 0, 12, 24):
    s = d / 2
    a_f, a_p = -math.degrees(s / 3.0), math.degrees(s / 4.5)
    kas = {"основание": base, "шестерня": Pos(0, Y_PIN, Z_GEAR0) * Rot(0, 0, -a_p) * pin, "ползун": Pos(s, 0, 0) * sld,
           "тележка": Pos(d, 0, 0) * cart}
    for i, x in enumerate((-SP_FLOAT / 2, SP_FLOAT / 2)):
        kas["плав%d" % i] = Pos(x + s, Y_FLOAT, Z_GEAR0 + 0.1) * Rot(0, 0, -a_f) * flo
    # выступ со штырьками крутится вместе с шестерней
    mk_d = dict(mk)
    mk_d["выступ"] = Pos(0, Y_PIN, Z_BODY1) * Rot(0, 0, -a_p) * boss
    for a, pa in mk_d.items():
        for b, pb in kas.items():
            if (a, b) in (("выступ", "шестерня"), ("подставка", "основание"), ("корпус макета", "основание")):
                continue                                          # посадки: штырьки в дырки
            v = (Part() + (pa & pb)).volume
            if v > 0.01:
                bad += 1
                print("ПЕРЕСЕЧЕНИЕ %s × %s: %.3f мм³ при d = %+d" % (a, b, v, d))
# штырьки выступа — в дырки шестерни, корпус — в дырки основания (врезаться не должны)
for (a, pa), (b, pb) in (((("выступ", Pos(0, Y_PIN, Z_BODY1) * boss)), ("шестерня", Pos(0, Y_PIN, Z_GEAR0) * pin)),
                         ((("корпус", Pos(0, Y_PIN, T_BASE) * body)), ("основание", base)),
                         ((("подставка", Pos(0, 0, -STAND_H) * stand)), ("основание", base))):
    v = (Part() + (pa & pb)).volume
    if v > 0.01:
        bad += 1
        print("ПОСАДКА ВРЕЗАЕТСЯ %s × %s: %.3f мм³" % (a, b, v))
print("макет мотора: %s" % ("чисто" if not bad else "ЕСТЬ ПЕРЕСЕЧЕНИЯ: %d" % bad))
