# -*- coding: utf-8 -*-
r"""Общие FDM-детали кассеты (ползун, тележка, плавающая шестерня) — для fdm_kasseta.py (стол 106) и kasseta_2204.py (107).
  * ползун: штырьки-оси Ø2 под плавающие шестерни; на гребне ласточкина хвоста — стопор тележки на двух дорожках:
    выступ Ø1.75 × 0.6 у −X (печатается) и гнездо Ø1.85 у +X под кусочек прутка 1.75 (вклеить ПОСЛЕ того, как тележку
    надели с +X и сдвинули к −X — гнездо открыто);
  * тележка: в потолке паза две канавки 2.0 × 0.8 во всю длину, в каждой ключ 1 мм со сдвигом от середины — выступ
    упирается в свой ключ, когда тележка сдвинута относительно ползуна на ±12.5 (рабочий ход ±12) — не съедет;
  * плавающая шестерня: отверстие Ø2.4.
"""
import math
import os
from build123d import *

HERE = os.path.dirname(os.path.abspath(__file__))
P = math.pi * 0.5
SP_FLOAT, Y_FLOAT = 5 * P, 6.0
Z_GEAR0, Z_PLATE1 = 18.8, 23.5
Z_CART0 = Z_PLATE1 + 0.1
Z_RIB = Z_PLATE1 + 1.2                  # верх гребня 24.7, потолок паза тележки 24.9
# стопор тележки — две дорожки на гребне (гребень сверху y 8.8 … 15.2): дорожка A (y 10.3) — выступ у −X и ключ тележки
# справа от её середины, дорожка B (y 13.7) — пруток у +X и ключ слева; каждый выступ встречает только свой ключ
Y_A, Y_B = 10.3, 13.7
X_STOP = 11.0                           # выступы на гребне (ползун ±13)
STOP_R, STOP_H = 0.875, 0.6
REL = 12.5                              # упор: тележка относительно ползуна ±12.5 (рабочий ход ±12)
KEY_W = 1.0
KEY_IN = REL - X_STOP + STOP_R          # 2.375 — ближняя к середине грань ключа


def load(n):
    return import_step(os.path.join(HERE, n + ".step"))


def polzun():
    s = load("04_polzun")
    for x in (-SP_FLOAT / 2, SP_FLOAT / 2):
        s = s + Pos(x, Y_FLOAT, (Z_GEAR0 + 0.3 + Z_PLATE1) / 2) * Cylinder(1.0, Z_PLATE1 - Z_GEAR0 - 0.3)
    s = s + Pos(-X_STOP, Y_A, Z_RIB + STOP_H / 2 - 0.01) * Cylinder(STOP_R, STOP_H + 0.02)       # выступ −X (дорожка A)
    s = s - Pos(X_STOP, Y_B, Z_RIB - 0.75) * Cylinder(0.925, 1.6)                                 # гнездо под пруток +X (B)
    return s


def shtyr_prutok():
    """кусочек прутка 1.75 в гнезде +X (для проверок): торчит над гребнем на 0.6"""
    return Pos(X_STOP, Y_B, Z_RIB - 1.5 / 2 + STOP_H / 2) * Cylinder(STOP_R, 1.5 + STOP_H)


def telezhka():
    c = load("05_telezhka")
    zc = Z_CART0 + 1.3 + 0.4                                                                      # канавки 24.9 … 25.7
    for y, kx in ((Y_A, KEY_IN + KEY_W / 2), (Y_B, -(KEY_IN + KEY_W / 2))):
        ch = Pos(0, y, zc - 0.01) * Box(30, 2.0, 0.8 + 0.02) - Pos(kx, y, zc) * Box(KEY_W, 3.0, 1.0)
        c = c - ch
    return c


def plav():
    return load("03_shesternya_plav_Z12") - Cylinder(1.2, 50)
