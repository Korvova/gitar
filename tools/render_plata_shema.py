# -*- coding: utf-8 -*-
"""Схема стенда одного мотора для «Т. Плата для мотора»: ESP32 — S2209 V4 — триггер и мотор.

Запуск: .venv-b123d\\Scripts\\python tools\\render_plata_shema.py  ->  wiki/img/plata_shema.png
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "wiki", "img", "plata_shema.png")

fig, ax = plt.subplots(figsize=(14, 8), dpi=130)
ax.set_xlim(0, 140)
ax.set_ylim(0, 80)
ax.axis("off")


def box(x, y, w, h, title, color):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.5",
                                fc=color, ec="#222", lw=1.6))
    ax.text(x + w / 2, y + h + 2.2, title, ha="center", va="bottom", fontsize=15, weight="bold")


def pin(x, y, name, side, bold=True):
    ax.plot([x], [y], "o", ms=7, color="#d9a400", mec="#222", zorder=5)
    dx, ha = (2, "left") if side == "r" else (-2, "right")
    ax.text(x + dx, y, name, ha=ha, va="center", fontsize=12, weight="bold" if bold else "normal",
            color="#111" if bold else "#888")


def wire(x0, y0, x1, y1, color, label=None, mid=None):
    xm = mid if mid is not None else (x0 + x1) / 2
    ax.plot([x0, xm, xm, x1], [y0, y0, y1, y1], color=color, lw=2.6, solid_capstyle="round", zorder=3)
    if label:
        ax.text(xm, max(y0, y1) + 1.0, label, ha="center", va="bottom", fontsize=10, color=color)


box(6, 5, 26, 65, "ESP32", "#dfe8f5")
box(58, 18, 28, 52, "Драйвер S2209 V4", "#f3ead7")
box(112, 50, 24, 20, "PD-триггер", "#e3f2e1")
box(112, 14, 24, 22, "Мотор Ø36", "#e9e3ee")
ax.text(124, 47, "от зарядки Type-C", ha="center", va="top", fontsize=10, color="#444")

# левая сторона драйвера (сверху вниз, как на плате)
left = [("EN", 64), ("MS1", 58), ("MS2", 52), ("TX", 46), ("RX", 40), ("CLK", 34), ("STEP", 28), ("DIR", 22)]
for n, y in left:
    pin(58, y, n, "r", bold=n not in ("MS1", "MS2", "CLK"))
# правая сторона драйвера
right = [("VM", 64), ("GND", 58), ("A2", 52), ("A1", 46), ("B1", 40), ("B2", 34), ("VIO", 28), ("GND", 22)]
for n, y in right:
    pin(86, y, n, "l")

# ножки ESP
esp = {"D27": 64, "D16": 46, "D17": 40, "D25": 28, "D26": 22, "3V3": 13, "GND": 8}
for n, y in esp.items():
    pin(32, y, n, "l")

wire(32, 64, 58, 64, "#7a3fb5")                       # EN
wire(32, 46, 58, 46, "#1f77b4")                       # D16 -> TX
wire(32, 40, 58, 40, "#e07b00")                       # D17 -> R -> RX
ax.add_patch(FancyBboxPatch((41, 38.6), 8, 2.8, boxstyle="round,pad=0.1", fc="#fff3c4", ec="#222", lw=1.4, zorder=6))
ax.text(45, 40, "1 кОм", ha="center", va="center", fontsize=9.5, zorder=7)
wire(32, 28, 58, 28, "#2a9d4b")                       # STEP
wire(32, 22, 58, 22, "#b5651d")                       # DIR
# 3V3 и GND идут под драйвером на его правую сторону
ax.plot([32, 96, 96, 86], [13, 13, 28, 28], color="#d62728", lw=2.6, zorder=3)
ax.plot([32, 100, 100, 86], [8, 8, 22, 22], color="#222", lw=2.6, zorder=3)
ax.text(50, 13.6, "3V3 → VIO", fontsize=10, color="#d62728", va="bottom")
ax.text(50, 8.6, "GND → GND у VIO", fontsize=10, color="#222", va="bottom")

# триггер
pin(112, 64, "VBUS (+)", "r")
pin(112, 58, "GND (−)", "r")
wire(86, 64, 112, 64, "#d62728")
wire(86, 58, 112, 58, "#222")

# мотор
for (n, y, c) in (("чёрный", 31, "#222"), ("оранжевый", 27, "#e07b00"), ("красный", 23, "#d62728"), ("синий", 19, "#1f77b4")):
    pin(112, y, n, "r")
for ys, yd, c, m in ((52, 31, "#222", 104), (46, 27, "#e07b00", 102), (40, 23, "#d62728", 106), (34, 19, "#1f77b4", 108)):
    wire(86, ys, 112, yd, c, mid=m)

ax.text(70, 76.5, "Стенд одного мотора: что куда", ha="center", fontsize=18, weight="bold")
ax.text(70, 1.0, "НЕ подключать: RX0 / TX0 на ESP (это USB)  ·  VIN ESP к VM/VBUS (сгорит ESP)  ·  "
        "штырьки DIAG и INDEX у EN — пустые", ha="center", fontsize=11, color="#b00020")
fig.savefig(OUT, bbox_inches="tight", facecolor="white")
print("ok", OUT)
