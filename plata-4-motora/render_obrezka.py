# -*- coding: utf-8 -*-
"""Схема обрезки платы: две параллельные линии с перемычками, прижимы на концах заготовки.
Запуск: ..\\2-0\\.venv-b123d\\Scripts\\python render_obrezka.py  ->  ../wiki/img/plata4_obrezka.png
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "wiki", "img", "plata4_obrezka.png")

# всё в координатах от центра левого крестика (как в файле 3_obrezka)
XL, XR = -8.5, 84.6                # линии реза
Y0, Y1 = -50.0, 50.0               # кромки заготовки (примерно)
YC0, YC1 = -56.0, 64.0             # рез идёт с запасом за кромки
TABS = [-25.0, 35.0]
BX0, BX1 = -45.0, 120.0            # концы заготовки

fig, ax = plt.subplots(figsize=(15, 9), dpi=110)
ax.add_patch(plt.Rectangle((BX0, Y0), BX1 - BX0, Y1 - Y0, fc="#d9a066", ec="k", lw=1.5))
ax.add_patch(plt.Rectangle((XL, Y0), XR - XL, Y1 - Y0, fc="#c9814a", ec="none"))
ax.add_patch(plt.Rectangle((-5.7, -37.4), 63.4, 87.4 - 12, fc="none", ec="#1b2a8a", lw=2, ls=":"))
ax.text(30, 8, "ПЛАТА\n(синий пунктир — рисунок)", ha="center", va="center", fontsize=14, color="#1b2a8a")
ax.text(70, -30, "место\nпод триггер", ha="center", va="center", fontsize=11, color="#5a3a1a")
for x in (-27, 103):
    ax.text(x, 0, "обрезок", ha="center", va="center", fontsize=13, color="#5a3a1a", rotation=90)

for cx, name in ((0, "Л"), (53.3, "П")):
    cy = 0 if name == "Л" else 8.5
    ax.plot([cx - 2, cx + 2], [cy, cy], color="k", lw=2)
    ax.plot([cx, cx], [cy - 2, cy + 2], color="k", lw=2)
    ax.text(cx + 3, cy + 2, name, fontsize=13, weight="bold")
ax.annotate("ноль X0 Y0 —\nцентр левого крестика", xy=(0, 0), xytext=(6, -14), fontsize=11,
            arrowprops=dict(arrowstyle="->", lw=1.3))

for x in (XL, XR):
    ax.plot([x, x], [YC0, YC1], color="#d00000", lw=5, solid_capstyle="butt")
    for t in TABS:
        ax.plot([x, x], [t - 1.5, t + 1.5], color="#ffd400", lw=8, solid_capstyle="butt")
ax.annotate("перемычки 3 мм —\nфреза не дорезает 0.8 мм", xy=(XR, 35), xytext=(92, 53), fontsize=11,
            arrowprops=dict(arrowstyle="->", lw=1.3))
ax.annotate("", xy=(XL, 35), xytext=(92, 56), arrowprops=dict(arrowstyle="->", lw=1.3))
ax.text(XL, YC0 - 4, "рез 1", ha="center", fontsize=12, color="#d00000")
ax.text(XR, YC0 - 4, "рез 2", ha="center", fontsize=12, color="#d00000")

for x in (BX0 - 6, BX1 - 8):
    ax.add_patch(plt.Rectangle((x, -8), 14, 16, fc="#3fbf3f", ec="#1a6b1a", lw=1.5))
    ax.text(x + 7, 0, "прижим", ha="center", va="center", fontsize=9, rotation=90)

ax.annotate("", xy=(XL, -66), xytext=(0, -66), arrowprops=dict(arrowstyle="<->", lw=1.3))
ax.text(XL / 2, -71, "8.5", ha="center", fontsize=11)
ax.annotate("", xy=(0, -66), xytext=(XR, -66), arrowprops=dict(arrowstyle="<->", lw=1.3))
ax.text(XR / 2, -71, "84.6 мм от левого крестика", ha="center", fontsize=11)

ax.text(37, 72, "Обрезка: два реза кукурузой 1.0 (красное), по 2 перемычки на каждом (жёлтое). Вид сверху, ты снизу",
        ha="center", fontsize=13, weight="bold")
ax.text(37, -78, "Ближняя и дальняя кромки платы — кромки самой заготовки. Резы выходят за кромки по воздуху",
        ha="center", fontsize=11)
ax.set_xlim(-58, 132)
ax.set_ylim(-82, 78)
ax.set_aspect("equal")
ax.axis("off")
fig.savefig(OUT, bbox_inches="tight", facecolor="white")
print("ok", OUT)
