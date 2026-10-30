# -*- coding: utf-8 -*-
r"""Схема подключения стенда 2204 (вики 19.30): ESP32 — SimpleFOC Mini V2 (DRV8316) — гимбал, питание от PD-триггера.
Запуск: 2-0\.venv-b123d\Scripts\python tools/render_stend2204_shema.py
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "wiki", "img", "stend2204_podkluchenie.png")

fig, ax = plt.subplots(figsize=(11, 7), dpi=110)
ax.set_xlim(0, 110)
ax.set_ylim(0, 70)
ax.axis("off")


def box(x, y, w, h, title, color, below=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.6", fc=color, ec="#333", lw=1.4))
    if below:                                       # сверху у платы провода питания — подпись снизу
        ax.text(x + w / 2, y - 1.6, title, ha="center", va="top", fontsize=11, weight="bold")
    else:
        ax.text(x + w / 2, y + h + 1.6, title, ha="center", va="bottom", fontsize=11, weight="bold")


def wire(x0, y0, x1, y1, color, label=None, lx=None):
    ax.plot([x0, x1], [y0, y1], color=color, lw=2.4, solid_capstyle="round")
    if label:
        ax.text(lx if lx is not None else (x0 + x1) / 2, y0 + 0.8, label, ha="center", va="bottom", fontsize=9, color="#222")


# блоки
box(2, 6, 22, 34, "ESP32 (USB от компьютера)", "#e8f1fb")
box(42, 6, 26, 34, "SimpleFOC Mini V2 (DRV8316)", "#eaf6ea", below=True)
box(86, 14, 20, 18, "Гимбал 2204", "#fbeee6")
box(40, 55, 30, 8, "PD-триггер + зарядник 12 В 2.25 А", "#fdf6dc")

# ESP32 -> плата: GND, IN1..3, EN
sig = [("GND", "GND", "#000000", 36), ("GPIO 25", "IN1", "#d33", 31), ("GPIO 26", "IN2", "#e90", 26),
       ("GPIO 27", "IN3", "#2a2", 21), ("GPIO 14", "EN", "#36c", 16)]
for a, b, c, y in sig:
    ax.text(23, y, a, ha="right", va="center", fontsize=10)
    ax.text(43, y, b, ha="left", va="center", fontsize=10)
    wire(24, y, 42, y, c)
ax.text(43, 11, "VDD (выход 3.3 В), VCC ×0.101 (делитель),\nCS1–CS3 (ток) — не подключать", ha="left", va="center", fontsize=8.5, color="#a00")

# плата -> мотор
for i, (n, c) in enumerate((("M1", "#555"), ("M2", "#888"), ("M3", "#bbb"))):
    y = 28 - i * 5
    ax.text(67, y, n, ha="right", va="center", fontsize=10)
    ax.text(87, y, "фаза", ha="left", va="center", fontsize=9)
    wire(68, y, 86, y, c)
ax.text(96, 10, "порядок любой:\nдва поменять — другая сторона", ha="center", va="top", fontsize=8.5)

# питание
wire(48, 55, 48, 41, "#d00")
wire(62, 55, 62, 41, "#000")
ax.text(47, 49.5, "VBUS → +", ha="right", va="center", fontsize=10, color="#d00")
ax.text(63, 49.5, "GND → −", ha="left", va="center", fontsize=10)
ax.text(72, 59, "12 В: включён только переключатель 1, кабель C–C\nпроверить мультиметром до подключения!", ha="left", va="center", fontsize=8.5, color="#a00")

plt.savefig(OUT, bbox_inches="tight", facecolor="white")
print(OUT)
