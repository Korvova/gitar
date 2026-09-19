# -*- coding: utf-8 -*-
"""Эскиз компоновки платы на 4 мотора для «Т. Плата для 4-х моторов».

Запуск: 2-0\\.venv-b123d\\Scripts\\python tools\\render_plata4_komponovka.py  ->  wiki/img/plata4_komponovka.png
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "wiki", "img", "plata4_komponovka.png")

fig, ax = plt.subplots(figsize=(13, 7.5), dpi=120)
ax.set_xlim(-6, 126)
ax.set_ylim(-10, 74)
ax.axis("off")
ax.set_aspect("equal")


def bx(x, y, w, h, t, c, fs=10):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.2,rounding_size=1", fc=c, ec="#222", lw=1.4))
    ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=fs)


ax.add_patch(Rectangle((0, 0), 120, 62, fc="#2f6b3a", ec="#111", lw=2))
ax.text(60, 68, "Плата на 4 мотора: идея компоновки (вид сверху)", ha="center", fontsize=15, weight="bold")

# шина питания от триггера
ax.add_patch(Rectangle((22, 46.5), 94, 2.2, fc="#d62728", ec="none"))
ax.add_patch(Rectangle((22, 43.3), 94, 2.2, fc="#111", ec="none"))
ax.text(118, 47.6, "VM", fontsize=8, color="w", ha="right", va="center")
ax.text(118, 44.4, "GND", fontsize=8, color="w", ha="right", va="center")

for k in range(4):
    x = 26 + k * 23
    bx(x, 52, 14, 8, "мотор %d\nразъём" % k, "#f5f5f5", 9)
    bx(x - 1, 22, 16, 20, "драйвер %d\nS2209\n(в гнезде)" % k, "#f3ead7", 9)
    ax.plot([x + 7, x + 7], [42, 52], color="#e0a000", lw=3)
    ax.plot([x + 7, x + 7], [14.5, 22], color="#7fc8ff", lw=3)

bx(2, 38, 17, 12, "триггер\nType-C\nнаружу", "#e3f2e1", 9)
ax.annotate("", xy=(-5, 44), xytext=(2, 44), arrowprops=dict(arrowstyle="->", lw=2))
ax.plot([19, 22], [47.6, 47.6], color="#d62728", lw=3)
ax.plot([19, 22], [44.4, 44.4], color="#111", lw=3)
ax.add_patch(plt.Circle((12, 28), 5, fc="#333", ec="#111"))
ax.text(12, 28, "470\nмкФ", color="w", fontsize=8, ha="center", va="center")

bx(40, 2, 54, 12, "ESP32 (в гнезде)", "#dfe8f5", 11)
ax.plot([19, 40], [8, 8], color="#7fc8ff", lw=3)
bx(6, 4.5, 13, 7, "1 кОм", "#fff3c4", 9)
ax.text(12.5, 14.5, "резистор: D17 → RX\nвсех драйверов", ha="center", fontsize=8, color="w")

for (x, y) in ((3, 59), (117, 59), (117, 3)):
    ax.add_patch(plt.Circle((x, y), 1.6, fc="w", ec="#111"))

ax.text(60, -5, "жёлтое — провода мотора   ·   голубое — STEP / DIR / EN / UART   ·   красное и чёрное — питание от триггера",
        ha="center", fontsize=10)
fig.savefig(OUT, bbox_inches="tight", facecolor="white")
print("ok", OUT)
