# -*- coding: utf-8 -*-
"""Калибровка маркера на обрезке текстолита (станок TTC3018, GRBL / Candle).

K1 — сверло 1.0: два отверстия. K2 — маркер, НЕ снимая заготовку: крестики в тех же
координатах + проба рисунка (три дорожки с зазором 1.0 и ряд площадок, как на плате).
По тому, куда ушёл крестик от отверстия, считается смещение маркера от шпинделя.

Ноль X, Y — левый ближний угол обрезка (нужно поле 70 x 40 мм). Z0 сверла — медь.
Z0 маркера — кончик маркера касается меди (перезанулить только Z).

Запуск: python make_kalibr.py  ->  gcode/K1_kalibr_sverlo_1.0.nc, gcode/K2_kalibr_marker.nc
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "gcode")
os.makedirs(OUT, exist_ok=True)

HOLES = [(10.0, 10.0), (60.0, 10.0)]
SAFE_Z = 3.0
DRILL_DEPTH, DRILL_PECK, DRILL_FEED = -1.9, -0.9, 50
PEN_DOWN, PEN_UP, PEN_FEED = -1.0, 3.0, 500      # маркер подпружинен: поджать на 1 мм

# ---------- K1: сверло ----------
g = ["(K1: kalibrovka, sverlo 1.0, 2 otverstiya)", "(X0 Y0 - leviy blizhniy ugol obrezka, Z0 - med)",
     "G21 G90 G94", "G17", "M3 S1000", "G4 P2", "G0 Z%.1f" % SAFE_Z]
for x, y in HOLES:
    g += ["G0 X%.2f Y%.2f" % (x, y), "G1 Z%.2f F%d" % (DRILL_PECK, DRILL_FEED), "G0 Z0.3",
          "G1 Z%.2f F%d" % (DRILL_DEPTH, DRILL_FEED), "G0 Z%.1f" % SAFE_Z]
g += ["M5", "G0 X0 Y0", "M2"]
open(os.path.join(OUT, "K1_kalibr_sverlo_1.0.nc"), "w").write("\n".join(g) + "\n")


# ---------- K2: маркер ----------
def line(pts):
    out = ["G0 X%.2f Y%.2f" % pts[0], "G1 Z%.2f F300" % PEN_DOWN]
    out += ["G1 X%.2f Y%.2f F%d" % (x, y, PEN_FEED) for x, y in pts[1:]]
    out += ["G0 Z%.1f" % PEN_UP]
    return out


g = ["(K2: kalibrovka, marker - shpindel VYKLYUCHEN)", "(Z0 - konchik markera kasaetsya medi)",
     "G21 G90 G94", "G17", "M5", "G0 Z%.1f" % PEN_UP]
for x, y in HOLES:                                   # крестики 10 мм в координатах отверстий
    g += line([(x - 5, y), (x + 5, y)])
    g += line([(x, y - 5), (x, y + 5)])
for i in range(3):                                   # три дорожки, шаг 2.2 (зазор 1.0 при линии 1.2)
    y = 22.0 + i * 2.2
    g += line([(10, y), (60, y)])
for i in range(8):                                   # ряд площадок, шаг 2.54: штрих 1.0 мм поперёк ряда
    x = 10 + i * 2.54
    g += line([(x, 32.5), (x, 33.5)])
g += line([(40, 30), (40, 36), (46, 36), (46, 30), (40, 30)])   # квадрат 6x6 — проверка размера
g += ["G0 X0 Y0", "M2"]
open(os.path.join(OUT, "K2_kalibr_marker.nc"), "w").write("\n".join(g) + "\n")
print("ok", OUT)
