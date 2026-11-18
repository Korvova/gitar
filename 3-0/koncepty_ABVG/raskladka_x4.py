# -*- coding: utf-8 -*-
"""Раскладка 4 модулей (18.11): 1 Б-повёрнут (накладка +15.8), 2 Б-повёрнут (3.8), 3 А-прямой (0.8), 4 Б-прямой (3.8) — пальцы шаг 24.
Сдвиги заданы в глобальных мм вдоль струн; для повёрнутого модуля локальный сдвиг = −глобальный."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from build123d import *
import teleskop_v6 as T
os.chdir(HERE); os.makedirs("asm_x4", exist_ok=True); os.makedirs("stl_x4", exist_ok=True)
BB, CZ = T.BB, T.CZ
L, Y0, Y1 = T.Y1 - T.Y0, T.Y0, T.Y1
PAD_A, PAD_B, PL = T.YC_CART, -10.1, 12.0
CB0, CB1 = -10.3, -3.9                                                           # верх тележки Б по Y
Z1 = T.Z_P1
def cap_B(sh):                                                                   # накладка тележки Б: площадка у переднего края + сдвиг
    yp = PAD_B + sh; y0 = min(yp - PL / 2, CB0); y1 = max(yp + PL / 2, CB1)
    c = BB(-T.CW, T.CW, y0, y1, Z1, Z1 + 1.6)
    for sx in (-1, 1):
        c += CZ(1.0, Z1 - 1.4, Z1 + 0.01, sx * 5.0, (CB0 + CB1) / 2)
    return c, (y0, y1)
def cap_A(sh):
    yp = PAD_A + sh; y0 = min(yp - PL / 2, T.Y_CART + 1.2 * T.M); y1 = max(yp + PL / 2, T.Y_CB + 2.0)
    return T.make_cap(sh), (y0, y1)
MODS = [("Б", True, 15.8), ("Б", True, -3.8), ("А", False, 0.8), ("Б", False, 3.8)]   # (вариант, повёрнут, глоб. сдвиг)
start, rows = 0.0, []
for i, (v, rot, g) in enumerate(MODS):
    loc = -g if rot else g
    cap, (y0, y1) = (cap_B if v == "Б" else cap_A)(loc)
    oy = start + Y1 if rot else start - Y0
    gy = sorted(((oy - y0, oy - y1) if rot else (oy + y0, oy + y1)))
    pad = (oy - ((PAD_B if v == "Б" else PAD_A) + loc)) if rot else (oy + (PAD_B if v == "Б" else PAD_A) + loc)
    export_stl(Part() + cap, "asm_x4/cap%d.stl" % (i + 1))
    p = Rot(180, 0, 0) * (Part() + cap); b = p.bounding_box(); p = Pos(-(b.min.X + b.max.X) / 2, -(b.min.Y + b.max.Y) / 2, -b.min.Z) * p
    export_stl(p, "stl_x4/17_nakladka_mod%d_%s_sdvig%+.1f.stl" % (i + 1, v, g), tolerance=0.01, angular_tolerance=0.1)
    rows.append((i + 1, v, rot, oy, pad, gy)); start += L
for r in rows:
    print("модуль %d %s %s: начало Y=%.1f, палец %.1f, накладка+тележка %.1f..%.1f" % (r[0], r[1], "повёрнут" if r[2] else "прямой", r[3], r[4], *r[5]))
pads = [r[4] for r in rows]; print("шаг пальцев:", [round(pads[k + 1] - pads[k], 1) for k in range(3)])
for k in range(3):
    gap = rows[k + 1][5][0] - rows[k][5][1]
    print("зазор между накладками %d–%d: %.1f мм" % (k + 1, k + 2, gap))
