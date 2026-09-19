# -*- coding: utf-8 -*-
"""3D-модели модулей для платы 4 моторов: драйвер S2209 V4 и ESP32 DevKit (30 ножек).
Нужны только для картинки и примерки в KiCad / Blender. Ноль модели — центр модуля,
Z=0 — низ текстолита модуля, ножки уходят вниз.

Запуск: ..\\2-0\\.venv-b123d\\Scripts\\python make_models.py  ->  models/s2209.step, models/esp32_devkit30.step
"""
import os
from build123d import Box, Cylinder, Compound, Pos, Color, export_step

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "models")
os.makedirs(OUT, exist_ok=True)

P = 2.54
PIN_DOWN = 6.0


def colored(shape, rgb, label):
    shape.color = Color(*rgb)
    shape.label = label
    return shape


def pins(n, y, x0):
    out = []
    for i in range(n):
        out.append(Pos(x0 + i * P, y, -PIN_DOWN / 2 + 0.8) * Box(0.64, 0.64, PIN_DOWN + 1.6))
    return out


def driver():
    parts = [colored(Pos(0, 0, 0.8) * Box(20.32, 15.24, 1.6), (0.92, 0.92, 0.9), "pcb")]
    parts.append(colored(Pos(0, 0, 1.6 + 0.5) * Box(5, 5, 1.0), (0.1, 0.1, 0.1), "chip"))
    # радиатор: основание и рёбра
    parts.append(colored(Pos(0, 0, 1.6 + 1.0 + 1.0) * Box(9, 9, 2.0), (0.1, 0.25, 0.75), "heatsink"))
    for i in range(5):
        parts.append(colored(Pos(-3.6 + i * 1.8, 0, 1.6 + 3.0 + 4.5) * Box(0.9, 9, 9.0), (0.1, 0.25, 0.75), "fin"))
    gold = (0.85, 0.7, 0.2)
    for y in (-6.35, 6.35):
        for p in pins(8, y, -3.5 * P):
            parts.append(colored(p, gold, "pin"))
    # штырьки DIAG / INDEX вверх
    for i in range(2):
        parts.append(colored(Pos(3.5 * P - i * P, 6.35 - P, 1.6 + 3.0) * Box(0.64, 0.64, 6.0), gold, "diag"))
    return Compound(label="s2209", children=parts)


def esp():
    L, W = 51.5, 28.2
    # ряды ножек: 15 штук, первый в 7.5 мм от края с антенной
    x_first = -L / 2 + 7.5
    parts = [colored(Pos(0, 0, 0.8) * Box(L, W, 1.6), (0.08, 0.08, 0.1), "pcb")]
    parts.append(colored(Pos(-L / 2 + 6.5 + 9, 0, 1.6 + 1.6) * Box(18, 16, 3.2), (0.75, 0.76, 0.78), "shield"))
    parts.append(colored(Pos(-L / 2 + 3.2, 0, 1.6 + 0.4) * Box(6.0, 18, 0.8), (0.15, 0.15, 0.17), "antenna"))
    parts.append(colored(Pos(L / 2 - 3.6, 0, 1.6 + 1.6) * Box(7.4, 9.0, 3.2), (0.8, 0.8, 0.82), "usb"))
    parts.append(colored(Pos(L / 2 - 14, 4, 1.6 + 0.8) * Box(5, 5, 1.6), (0.1, 0.1, 0.1), "uart"))
    for sx in (-1, 1):
        parts.append(colored(Pos(L / 2 - 4, sx * 9.5, 1.6 + 0.9) * Cylinder(1.6, 1.8), (0.85, 0.85, 0.85), "btn"))
    gold = (0.85, 0.7, 0.2)
    for y in (-12.7, 12.7):
        for p in pins(15, y, x_first):
            parts.append(colored(p, gold, "pin"))
    return Compound(label="esp32_devkit30", children=parts)


export_step(driver(), os.path.join(OUT, "s2209.step"))
export_step(esp(), os.path.join(OUT, "esp32_devkit30.step"))
print("ok", OUT)
