# -*- coding: utf-8 -*-
"""Концепт грифа v2 (24.11, владелец): основание грифа — тонкая плита со скошенными краями (сплюснутый ласточкин хвост),
по ней едет «поезд»: блок с 4 тележками → коробка с платами → толкатель во всю ширину (внутри провода к деке).
У каждого вагона снизу губы, охватывают скосы плиты. Сверху блока — крышка-юбка, видно только тележки.
x — поперёк (±25), y — вдоль грифа (дека в +y), z = 0 — верх плиты = низ окантовки блока. → ../19.73_grif_kontsept2/asm"""
import os
from build123d import *
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "19.73_grif_kontsept2", "asm"); os.makedirs(OUT, exist_ok=True)
W, TH, C = 25.0, 2.0, 0.25                # 24.11 (владелец): плита 2 мм — хватит; высоту потом оптимизировать целиком
WT, WB = 23.0, 21.0                       # плита: вверху шире (23), внизу уже (21) — губы заходят под скос, вагон не поднять
BL = 73.7                                 # блок ±73.7 по y
def prof(pts, y0, y1):
    return extrude(make_face(Polyline(*[(x, y0, z) for x, z in pts + [pts[0]]])), y1 - y0, dir=(0, 1, 0))
chan = prof([(-WB - C, -TH - 1), (WB + C, -TH - 1), (WB + C, -TH), (WT + C, 0.01), (-WT - C, 0.01), (-WB - C, -TH)], -900, 900)
def sled(y0, y1, z1):                     # вагон: короб ±25 от низа плиты до z1 минус канал под плиту
    return Box(2 * W, y1 - y0, z1 + TH, align=(Align.CENTER, Align.MIN, Align.MIN)).moved(Location((0, y0, -TH))) - chan
base = prof([(-WB, -TH), (WB, -TH), (WT, 0), (-WT, 0)], -300, 300)
guby = sled(-BL, BL, 0.0)                                                         # губы блока (под окантовкой)
Y_B0, Y_B1 = BL + 0.5, BL + 40.5
box = sled(Y_B0, Y_B1, 16.0) - Box(2 * W - 3, Y_B1 - Y_B0 - 3, 20, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((0, (Y_B0 + Y_B1) / 2, 1.5)))
plata = Box(40, 34, 1.6, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((0, (Y_B0 + Y_B1) / 2, 4.0)))
Y_T0, Y_T1 = Y_B1, 480.0
tolk = sled(Y_T0, Y_T1, 15.0) - Box(40, Y_T1 - Y_T0 + 2, 10, align=(Align.CENTER, Align.MIN, Align.MIN)).moved(Location((0, Y_T0 - 1, 2.5)))   # толкатель полый
provod = Box(12, Y_T1 - Y_T0 + 20, 3, align=(Align.CENTER, Align.MIN, Align.MIN)).moved(Location((0, Y_T0 - 10, 3.0)))
kr = Box(2 * W + 1.6, 2 * BL + 1.6, 23.0, align=(Align.CENTER, Align.CENTER, Align.MIN)) - Box(2 * W, 2 * BL, 30, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((0, 0, -1)))
lines = Part()
for xs in (-17.5, -10.5, -3.5, 3.5, 10.5, 17.5):                                    # струны и лады — рисунок на плите
    lines += Box(0.6, 600, 0.1, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((xs, 0, 0)))
y, k = -300, 0
while y < 300:
    lines += Box(2 * WT, 1.0, 0.12, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((0, y, 0))); y += 36 - k; k += 1
P = {"osnovanie": base, "guby_bloka": guby, "korobka_plat": box, "plata": plata, "tolkatel": tolk, "provoda": provod, "kryshka_jubka": kr, "risunok": lines}
for n, p in P.items():
    export_stl(p, os.path.join(OUT, n + ".stl"), tolerance=0.05, angular_tolerance=0.2)
print("плита %.0f→%.0f × %.1f, ширина поезда 50; пересечения с плитой:" % (2 * WT, 2 * WB, TH), {n: round((p & base).volume, 3) if (p & base) else 0 for n, p in P.items() if n not in ("osnovanie", "risunok", "plata", "provoda", "kryshka_jubka")})
