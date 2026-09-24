# -*- coding: utf-8 -*-
"""Картинка: где ставить 4 перемычки (вид со стороны деталей и со стороны меди).
Запуск: python из KiCad 10 render_peremychki.py -> ../wiki/img/plata4_peremychki.png
"""
import os
import pcbnew
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "wiki", "img", "plata4_peremychki.png")
b = pcbnew.LoadBoard(os.path.join(HERE, "plata_4_motora.kicad_pcb"))
mm = pcbnew.ToMM
pads = [(mm(p.GetPosition().x), mm(p.GetPosition().y), p.GetNetname()) for f in b.GetFootprints() for p in f.Pads()]
tracks = [(mm(t.GetStart().x), mm(t.GetStart().y), mm(t.GetEnd().x), mm(t.GetEnd().y), mm(t.GetWidth())) for t in b.GetTracks()]
jumps = [(mm(d.GetStart().x), mm(d.GetStart().y), mm(d.GetEnd().x), mm(d.GetEnd().y))
         for d in b.GetDrawings() if d.GetLayer() == pcbnew.Dwgs_User]

fig, axs = plt.subplots(1, 2, figsize=(18, 10), dpi=100)
for ax, mirror, title in ((axs[0], False, "Сторона ДЕТАЛЕЙ (сверху)"), (axs[1], True, "Сторона МЕДИ (плата перевёрнута)")):
    fx = (lambda x: 92 - x) if mirror else (lambda x: x)
    ax.add_patch(plt.Rectangle((0, 0), 92, 92, fc="#d9c98a", ec="k"))
    for x1, y1, x2, y2, w in tracks:
        ax.plot([fx(x1), fx(x2)], [y1, y2], color="#9a9a9a", lw=w * 2.2, solid_capstyle="round")
    for x, y, n in pads:
        ax.add_patch(plt.Circle((fx(x), y), 0.8, fc="#bbb", ec="#555", lw=0.5, zorder=4))
    for i, (x1, y1, x2, y2) in enumerate(jumps):
        top = abs(y2 - y1) > 15          # длинная = GND сверху
        if top != (not mirror):
            continue
        ax.plot([fx(x1), fx(x2)], [y1, y2], color="#d00000", lw=4, zorder=6)
        for x, y in ((x1, y1), (x2, y2)):
            ax.add_patch(plt.Circle((fx(x), y), 1.3, fc="#ffd400", ec="#d00000", lw=2, zorder=7))
    ax.set_xlim(-2, 94)
    ax.set_ylim(94, -2)
    ax.set_aspect("equal")
    ax.set_title(title, fontsize=15, weight="bold")
    ax.axis("off")

a = axs[0]
a.text(46.3, 5.5, "GND: прямой провод 21 мм\nмежду двумя отверстиями\nсправа от драйвера 1", ha="center", va="bottom", fontsize=11, color="#d00000")
a.text(15, 17, "драйвер 0", fontsize=10, ha="center"); a.text(36, 17, "драйвер 1", fontsize=10, ha="center")
a.text(31, 46, "ESP32", fontsize=12, ha="center"); a.text(24, 74, "драйвер 2", fontsize=10, ha="center"); a.text(45, 74, "драйвер 3", fontsize=10, ha="center")
a.text(75, 25, "триггер", fontsize=10, ha="center"); a.text(59.5, 60, "C1", fontsize=10, ha="center")
m = axs[1]
m.text(92 - 28.5, 33, "MS1 др.1", fontsize=10, color="#d00000", ha="left")
m.text(92 - 26, 63, "MS2 др.2", fontsize=10, color="#d00000", ha="right")
m.text(92 - 49.5, 63, "MS1+MS2 др.3", fontsize=10, color="#d00000", ha="right")
m.text(46, 90, "три адресных: изолированный провод ~5 мм, от ножки MS вниз/вверх на полосу VIO", ha="center", fontsize=11, color="#d00000")
fig.suptitle("Четыре перемычки на плате (красное). Драйверы и ESP при этом НЕ вставлены", fontsize=15)
fig.savefig(OUT, bbox_inches="tight", facecolor="white")
print("ok", OUT, len(jumps))
