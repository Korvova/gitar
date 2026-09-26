# -*- coding: utf-8 -*-
"""Крупно: гнездо драйвера 1 со стороны меди — перемычка MS1 и куда ставить щупы.
Запуск: python из KiCad 10 render_gnezdo1.py -> ../wiki/img/plata4_gnezdo1_prozvonka.png
"""
import os
import pcbnew
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "wiki", "img", "plata4_gnezdo1_prozvonka.png")
b = pcbnew.LoadBoard(os.path.join(HERE, "plata_4_motora.kicad_pcb"))
mm = pcbnew.ToMM
P, X1 = 2.54, 26.0                       # ножка 1 гнезда драйвера 1
Y_T, Y_S, Y_D = 11.4, 24.1, 19.0
fx = lambda x: 92 - x                     # сторона меди — зеркально

fig, ax = plt.subplots(figsize=(13, 11), dpi=100)
ax.add_patch(plt.Rectangle((fx(56), -2), 60, 36, fc="#d9c98a", ec="none"))
for t in b.GetTracks():
    x1, y1, x2, y2 = mm(t.GetStart().x), mm(t.GetStart().y), mm(t.GetEnd().x), mm(t.GetEnd().y)
    col = {"VIO": "#e0a000", "GND": "#555", "VM": "#c00", "UART": "#1f77b4"}.get(t.GetNetname(), "#9a9a9a")
    ax.plot([fx(x1), fx(x2)], [y1, y2], color=col, lw=mm(t.GetWidth()) * 6, solid_capstyle="round", alpha=0.85)
for f in b.GetFootprints():
    for p in f.Pads():
        x, y = mm(p.GetPosition().x), mm(p.GetPosition().y)
        ax.add_patch(plt.Circle((fx(x), y), 0.75, fc="#eee", ec="#333", lw=0.8, zorder=4))

top = ["VM", "GND", "A2", "A1", "B1", "B2", "VIO", "GND"]
bot = ["EN", "MS1", "MS2", "TX", "RX", "CLK", "STEP", "DIR"]
for i in range(8):
    ax.text(fx(X1 + i * P), Y_T - 1.7, top[i], ha="center", fontsize=9, rotation=90, va="bottom")
    ax.text(fx(X1 + i * P), Y_S + 1.6, bot[i], ha="center", fontsize=9, rotation=90, va="top")

ms1 = (fx(X1 + P), Y_S)
dend = (fx(X1 + P), Y_D)
vio = (fx(X1 + 6 * P), Y_T)
ax.plot([ms1[0], dend[0]], [ms1[1], dend[1]], color="#d00000", lw=5, zorder=6)
for pt in (ms1, dend):
    ax.add_patch(plt.Circle(pt, 1.0, fc="#ffd400", ec="#d00000", lw=2.5, zorder=7))
ax.annotate("перемычка MS1\n(твой проводок)", xy=((ms1[0] + dend[0]) / 2, 21.5), xytext=(fx(X1 + P) + 7, 30),
            fontsize=12, color="#d00000", arrowprops=dict(arrowstyle="->", color="#d00000", lw=1.5))
ax.annotate("ЩУП 1: площадка MS1", xy=ms1, xytext=(ms1[0] - 14, 31), fontsize=12, weight="bold",
            arrowprops=dict(arrowstyle="->", lw=2))
ax.annotate("ЩУП 2: ножка VIO\n(7-я в ряду VM…GND)", xy=vio, xytext=(vio[0] + 6, 2), fontsize=12, weight="bold",
            arrowprops=dict(arrowstyle="->", lw=2))
ax.annotate("конец жёлтой полосы VIO —\nсюда приходит перемычка", xy=dend, xytext=(dend[0] + 8, 16.5), fontsize=11,
            arrowprops=dict(arrowstyle="->", lw=1.3))
ax.text(fx(X1 + 3.5 * P), 35.5, "Гнездо драйвера 1, СТОРОНА МЕДИ (плата перевёрнута). Прозвонка, питание выключено.\n"
        "Жёлтое — VIO, синее — UART, красное — VM, серое тёмное — GND", ha="center", fontsize=12)
ax.set_xlim(fx(52), fx(20))
ax.set_ylim(38, -1)
ax.set_aspect("equal")
ax.axis("off")
fig.savefig(OUT, bbox_inches="tight", facecolor="white")
print("ok", OUT)
