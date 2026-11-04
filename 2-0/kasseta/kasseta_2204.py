# -*- coding: utf-8 -*-
r"""Кассета под гимбал 2204 с Авито (04.11.2026): Ø27.8 × 12.23 (замер владельца), крутится весь торец стакана —
4 × М2 на Ø12 и отверстие в центре; неподвижная сторона (провода) — М2, расстояние не мерили → радиальные прорези.
Шестерёнчатая часть и всё над ней — как в кассете автора (Z_GEAR0 = 18.8): ползун, тележка, плавающие шестерни, упор
— те же детали (FDM-вариант: штырьки на ползуне, отверстие шестерён Ø2.4). Новое:
  * основание: стенки и полка-мостик начинаются выше (16.85) — под ними проходит фланец с головками винтов;
    неподвижная рейка лежит на полке, полка на стойках за краем мотора (|x| ≥ 16); прорези под винты статора;
  * шестерня мотора из двух частей: ФЛАНЕЦ Ø17.5 на 4 винта М2 к торцу (прикрутить ДО того, как задвинуть мотор —
    сверху между стенками не пролезет) и НОЖКА с шестернёй Z18 — сверху в шестигранник фланца, на клей.
Винты в мотор — не глубже резьбы (урок 19.9): во фланец М2 × 3 (фланец 1.6), в статор снизу М2 × 3 (основание 1.2).
Запуск: ..\.venv-b123d\Scripts\python kasseta_2204.py
"""
import math
import os
from build123d import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "Print", "Print")

MOT_D, MOT_H = 27.8, 12.23
T_BASE = 1.2
Z_MTOP = T_BASE + MOT_H                    # 13.43 — крутящийся торец
FL_T, FL_R = 1.6, 8.75                     # фланец
HEAD_H = 1.5                               # головки М2 над фланцем
ZW = Z_MTOP + FL_T + HEAD_H + 0.3          # 16.83 → низ стенок и полки
ZW = 16.85
# как у автора (cassette_parametry.py)
M, P = 0.5, math.pi * 0.5
ALPHA = math.radians(20)
BACKLASH, RACK_ADD, RACK_DED = 0.04, 0.38, 0.625
W, L = 24.0, 50.0
Z_GEAR0 = 1.2 + 17.5 + 0.1                 # 18.8 — как у автора, детали над ним те же
H_GEAR = 3.4
Z_RACK_TOP = Z_GEAR0 + H_GEAR + 0.05
Z_PLATE0 = Z_RACK_TOP + 0.05
T_PLATE = 1.2
Z_PLATE1 = Z_PLATE0 + T_PLATE
Z_CART0 = Z_PLATE1 + 0.1
Y_FLOAT, Y_PIN = 6.0, 16.5
SP_FLOAT = 5 * P
TONGUE = 18.0


def BB(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))


def rack(x1, x2, y_back, y_pitch, sign, phase, z0, z1):
    """рейка автора: sign=+1 — зубья в +Y, центры зубьев phase + k·P"""
    tip, root = y_pitch + sign * RACK_ADD, y_pitch - sign * RACK_DED
    hp, tn = P / 4 - BACKLASH / 2, math.tan(ALPHA)
    pts = [(x1, y_back), (x1, root)]
    k = math.ceil((x1 + RACK_DED - phase) / P)
    while phase + k * P + RACK_DED < x2:
        c = phase + k * P
        pts += [(c - hp - RACK_DED * tn, root), (c - hp + RACK_ADD * tn, tip), (c + hp - RACK_ADD * tn, tip), (c + hp + RACK_DED * tn, root)]
        k += 1
    pts += [(x2, root), (x2, y_back), (x1, y_back)]
    return Pos(0, 0, z0) * extrude(make_face(Polyline(*pts)), z1 - z0)


# ---------------- основание под 2204 ----------------
b = BB(-L / 2, L / 2, 0, W, 0, T_BASE)
b += BB(-L / 2, L / 2, 0, 1.5, ZW, Z_CART0 + 0.2)                                   # левая стенка
b += BB(-L / 2, L / 2, 22.5, W, ZW, Z_PLATE0 - 0.05)                                # правая стенка с пазом
b += BB(-L / 2, L / 2, 22.5, W, Z_PLATE1 + 0.05, Z_PLATE1 + 0.85)
for x1, x2 in ((-L / 2, -L / 2 + 3), (L / 2 - 3, L / 2)):                           # стойки стенок на концах
    for y1, y2 in ((0, 1.5), (22.5, W)):
        b += BB(x1, x2, y1, y2, T_BASE - 0.01, ZW + 0.5)
b += BB(TONGUE / 2 + 12.05, L / 2, 22.5, W, Z_PLATE0 - 0.1, Z_PLATE1 + 0.1)          # закрытый конец паза
# полка-мостик под плавающими шестернями и неподвижной рейкой: над фланцем, на стойках за краем мотора
b += BB(-20.5, 20.5, 3.8, 11.0, ZW, Z_GEAR0)
for sx in (1, -1):
    b += BB(*sorted((sx * 16.0, sx * 20.5)), 3.8, 11.0, T_BASE - 0.01, ZW + 0.01)
b += rack(-16, 16, 11, 9, -1, 0, Z_GEAR0 - 0.01, Z_RACK_TOP)                       # неподвижная рейка (как у автора)
# под мотор: окно Ø9, 2 радиальные прорези под винты статора (мотор повернуть, чтобы 2 противоположные дырки встали в них) (r 5.5 … 9.5), дырки крепления кассеты
b -= Pos(0, Y_PIN, T_BASE / 2) * Cylinder(4.5, T_BASE + 0.2)
for a in (0, 180):                                                                  # 2 прорези напротив: к краю (+Y) места нет
    sl = BB(5.5, 9.5, -1.15, 1.15, -0.1, T_BASE + 0.1) + Pos(5.5, 0, T_BASE / 2) * Cylinder(1.15, T_BASE + 0.2) \
        + Pos(9.5, 0, T_BASE / 2) * Cylinder(1.15, T_BASE + 0.2)
    b -= Pos(0, Y_PIN, 0) * Rot(0, 0, a) * sl
for x in (-23.5, 23.5):
    for y in (6, 18):
        b -= Pos(x, y, T_BASE / 2) * Cylinder(1.1, T_BASE + 0.2)

# ---------------- фланец на торец мотора: 4 × М2 на Ø12, гнездо-шестигранник 5 под ножку ----------------
HEX = 5.0
fl = Pos(0, 0, FL_T / 2) * Cylinder(FL_R, FL_T)
fl += Pos(0, 0, FL_T + (ZW - 0.05 - Z_MTOP - FL_T) / 2) * Cylinder(4.0, ZW - 0.05 - Z_MTOP - FL_T)   # втулка Ø8 до низа стенок
fl -= Pos(0, 0, FL_T + 0.3) * extrude(RegularPolygon((HEX + 0.25) / 2 / math.cos(math.radians(30)), 6), 10)
for a in (0, 90, 180, 270):
    fl -= Pos(6 * math.cos(math.radians(a)), 6 * math.sin(math.radians(a)), FL_T / 2) * Cylinder(1.1, FL_T + 0.2)
FL_TOP = ZW - 0.05 - Z_MTOP                # высота фланца с втулкой (3.37)

# ---------------- ножка с шестернёй: шестерня автора Z18 + ножка Ø8 вниз + шестигранник во фланец ----------------
gear = import_step(os.path.join(HERE, "02_shesternya_motora_Z18.step"))           # z 0 … 3.4, глухие дырки снизу
STEM = Z_GEAR0 - (ZW - 0.05)               # от верха втулки до низа шестерни
nozh = Pos(0, 0, STEM) * gear + Pos(0, 0, STEM / 2) * Cylinder(4.0, STEM + 0.01)
nozh += Pos(0, 0, -(FL_T + 0.3 - 0.0)) * extrude(RegularPolygon(HEX / 2 / math.cos(math.radians(30)), 6), FL_T + 0.3)  # в гнездо

parts = [("kas2204_osnovanie", b), ("kas2204_flanec", fl), ("kas2204_nozhka_shesternya", nozh)]
for n, p in parts:
    p = Part() + p
    bb = p.bounding_box()
    print("%s: %.1f x %.1f x %.1f, solids %d" % (n, bb.size.X, bb.size.Y, bb.size.Z, len(p.solids())))
    export_stl(p, os.path.join(OUT, n + ".stl"))

# ================= ПРОВЕРКА: ход ±24, мотор задвигается сбоку =================
def load(n):
    return import_step(os.path.join(HERE, n + ".step"))


sld = load("04_polzun")
for x in (-SP_FLOAT / 2, SP_FLOAT / 2):
    sld = sld + Pos(x, Y_FLOAT, (Z_GEAR0 + 0.3 + Z_PLATE1) / 2) * Cylinder(1.0, Z_PLATE1 - Z_GEAR0 - 0.3)
flo = load("03_shesternya_plav_Z12") - Cylinder(1.2, 50)
cart = load("05_telezhka")
motor = Pos(0, Y_PIN, T_BASE + MOT_H / 2) * Cylinder(MOT_D / 2, MOT_H)
heads = Pos(0, Y_PIN, Z_MTOP + FL_T + HEAD_H / 2) * (Cylinder(7.9, HEAD_H) - Cylinder(4.1, HEAD_H + 0.1))  # кольцо головок
bad = 0
for d in (-24, -16, -8, -2, 0, 3, 9, 17, 24):
    s = d / 2
    a_f, a_p = -math.degrees(s / 3.0), math.degrees(s / 4.5)
    rot = Rot(0, 0, -a_p)
    pl = {"основание": b, "мотор": motor, "головки винтов": heads,
          "фланец": Pos(0, Y_PIN, Z_MTOP) * rot * fl,
          "ножка с шестернёй": Pos(0, Y_PIN, ZW - 0.05) * rot * nozh,
          "ползун": Pos(s, 0, 0) * sld, "тележка": Pos(d, 0, 0) * cart}
    for i, x in enumerate((-SP_FLOAT / 2, SP_FLOAT / 2)):
        pl["плав%d" % i] = Pos(x + s, Y_FLOAT, Z_GEAR0 + 0.1) * Rot(0, 0, -a_f) * flo
    names = list(pl)
    for i, a in enumerate(names):
        for c in names[i + 1:]:
            if {a, c} in ({"мотор", "основание"}, {"мотор", "фланец"}, {"фланец", "ножка с шестернёй"},
                          {"фланец", "головки винтов"}, {"мотор", "головки винтов"}):
                continue                                                         # посадки
            v = (Part() + (pl[a] & pl[c])).volume
            if v > 0.01:
                bad += 1
                print("ПЕРЕСЕЧЕНИЕ %s × %s: %.3f мм³ при d = %+d" % (a, c, v, d))
# зацепление: шестерня ножки на пол-зуба — должна врезаться в рейку ползуна
v = (Part() + (Pos(0, Y_PIN, ZW - 0.05) * Rot(0, 0, 10) * nozh & sld)).volume
print("шестерня ножки на пол-зуба × ползун: %.2f мм³ (> 0 — в зацеплении)" % v)
# мотор с фланцем и головками задвигается сбоку (+Y)
for dy in (4, 8, 12, 16, 22, 30):
    m = Pos(0, dy, 0) * (motor + Pos(0, Y_PIN, Z_MTOP) * fl.moved(Location()) + heads)
    v = (Part() + (m & b)).volume
    if v > 0.01:
        bad += 1
        print("мотор с фланцем не задвигается: сдвиг +%d — пересечение %.3f" % (dy, v))
print("кассета 2204: %s" % ("чисто" if not bad else "ЕСТЬ ПЕРЕСЕЧЕНИЯ: %d" % bad))
