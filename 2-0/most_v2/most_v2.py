# -*- coding: utf-8 -*-
"""Мост с кнопками + тележка, проба v2 (13.11.2026). Длина 50, X — ход тележки ±22, Y поперёк, Z вверх.
ЛОТОК: стенки = рельсы (сверху ездит тележка, снаружи V-пазы под её губы, в правой стенке канавка упора хода).
  Внутри плата 1.6 с 6 SMD-кнопками 5.2×5.2×1.5 (ход 0.3) и зона резисторов, провода — в прорезь торца.
КРЫШКА лотка с окнами, 2 винта М2 сверху (в зоне резисторов). ТОЛКАТЕЛИ (TPU или PLA) с буртиком — не выпадают.
ТЕЛЕЖКА защёлкивается сверху губами за V-пазы; сверху окно и ПЛАСТИНА (TPU): тонкий пружинящий пояс,
  жёсткий центр с гнездом таблетки Ø10×2.7 и каналом провода, снизу штырь. Ход 0.5 = 0.2 зазор + 0.3 кнопка."""
import math, os
from build123d import *
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE); os.makedirs("stl", exist_ok=True)
H = 25.0; PX = (-19.5, -13.2, -4.4, 4.4, 13.2, 19.5); BY = 0.0   # крайние ±19.5 (торцы 22.4..25 сплошные, там штифты крышки)
YI, YO = 3.6, 11.0                                                      # полость лотка ±3.6 (кнопка 5.2 + зазор); YO — для стоек основания
Z_FL, Z_PCB, Z_BT = 1.0, 2.6, 4.1                                       # пол, верх платы, верх кнопки
Z_LD0, Z_LD1 = 4.4, 5.6                                                 # крышка лотка
Z_RL = 6.1                                                              # верх рельсов на крышке = низ тележки
YW = YI + 1.2; YT = YW + 0.8                                            # лоток ±4.8 (стенки 1.2); рельсы-хвост на крышке, верх ±5.6
CW, CY = 10.0, YT + 1.3                                                 # тележка ±10 по X, ±6.9 по Y
Z_CT = 7.4                                                              # верх тележки
def BB(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))
def CZ(r, z0, z1, x=0.0, y=0.0):
    return Pos(x, y, z0) * Cylinder(r, z1 - z0, align=(Align.CENTER, Align.CENTER, Align.MIN))
def prof_x(pts, x0, x1):
    return Pos(x0, 0, 0) * Rot(90, 90, 0) * extrude(make_face(Polyline(*(pts + [pts[0]]))), x1 - x0, dir=(0, 0, 1))
# ---------------- лоток ----------------
XE = 22.4                                                               # торцы 22.4..25 сплошные
tray = BB(-H, H, -YW, YW, 0, Z_LD0) - BB(-XE, XE, -YI, YI, Z_FL, Z_LD0 + 1)
PIN = [(-23.7, 0.0), (23.7, 0.0)]                                       # штифты крышки: филамент 1.75 (+капля клея)
for x, y in PIN:
    tray -= CZ(0.95, Z_LD0 - 3.0, Z_LD0 + 1, x, y)
tray -= BB(-H - 1, -XE + 0.5, -2.4, -1.0, Z_FL, Z_FL + 1.6)                # прорезь проводов в торце (ниже кнопок)
# ---------------- плата (пока печатная пластина), кнопки, SMD-резисторы 0805 в промежутках ----------------
pcb = BB(-XE + 0.15, XE - 0.15, -YI + 0.15, YI - 0.15, Z_FL, Z_PCB)
btns = Part() + [BB(x - 2.6, x + 2.6, BY - 2.6, BY + 2.6, Z_PCB, Z_BT) for x in PX]
res = Part() + [BB((PX[i] + PX[i + 1]) / 2 - 0.63, (PX[i] + PX[i + 1]) / 2 + 0.63, BY - 1.0, BY + 1.0, Z_PCB, Z_PCB + 0.5) for i in range(5)]
# ---------------- крышка лотка с рельсами-хвостом ----------------
lid = prof_x([(-YW, Z_LD0), (YW, Z_LD0), (YT, Z_RL), (-YT, Z_RL)], -H, H) - BB(-H - 1, H + 1, -YW + 1.0, YW - 1.0, Z_LD1, Z_RL + 1)
lid -= BB(-22.75, 22.75, -5.2, -4.4, Z_RL - 0.6, Z_RL + 1)                  # канавка упора хода в рельсе
for x in PX:
    lid -= BB(x - 2.2, x + 2.2, BY - 2.2, BY + 2.2, Z_LD0 - 1, Z_LD1 + 1)   # окно 4.4×4.4
for x, y in PIN:
    lid -= CZ(0.95, Z_LD0 - 1, Z_LD1 + 1, x, y)
lid -= BB(-22.1, 22.1, BY - 3.1, BY + 3.1, Z_LD1 - 0.6, Z_LD1 + 1)                # выемка под ленту TPU
tape = BB(-22.0, 22.0, BY - 3.0, BY + 3.0, Z_LD1 - 0.6, Z_LD1)                    # лента TPU 0.6, вровень с крышкой
bumps = Part() + [BB(x - 2.0, x + 2.0, BY - 2.0, BY + 2.0, Z_BT, Z_LD1 - 0.59) for x in PX]   # бугорки 4×4
tape += bumps
# ---------------- тележка ----------------
cart = BB(-CW, CW, -CY, CY, Z_RL, Z_CT)
Z_LP = Z_LD0 - 0.5                                                       # низ губ: обнимают хвост крышки, надевается с торца
for s in (-1, 1):
    pts = [(s * CY, Z_LP), (s * CY, Z_RL + 0.01), (s * (YT + 0.1), Z_RL + 0.01), (s * (YW + 0.1), Z_LD0), (s * (YW + 0.1), Z_LP)]
    cart += prof_x(pts if s > 0 else pts[::-1], -CW, CW)
cart += BB(-0.75, 0.75, -5.1, -4.5, Z_RL - 0.5, Z_RL + 0.01)               # зуб упора хода
T_TG, TG_X0, TG_X1, TG_Y = 0.8, -6.0, 8.5, 4.0                           # П-язычок вдоль X: толщина, кончик, корень, полуширина
cart -= BB(TG_X0 - 0.5, TG_X1, -TG_Y - 0.5, TG_Y + 0.5, Z_RL - 1, Z_CT + 1)   # П-прорезь 0.5
cart += BB(TG_X0, TG_X1 + 0.01, -TG_Y, TG_Y, Z_CT - T_TG, Z_CT)          # язычок, корень у края +X
cart += BB(-2.3, 2.3, -2.3, 2.3, Z_LD1 + 0.2, Z_CT - T_TG + 0.01)         # штырь 4.6×4.6, до ленты 0.2
PEG = [(x, sy * 5.7) for x in (-8.3, 9.2) for sy in (-1, 1)]
for x, y in PEG:
    cart -= CZ(0.65, Z_CT - 1.0, Z_CT + 1, x, y)                          # гнёзда штырьков накладки
# ---------------- накладка 0.4 (2 слоя PLA/TPU, продавливается) ----------------
T_CV = 0.4
cover = BB(-CW, CW, -CY, CY, Z_CT, Z_CT + T_CV)
for x, y in PEG:
    cover += CZ(0.55, Z_CT - 0.9, Z_CT + 0.01, x, y)
coin = CZ(5.0, Z_CT, Z_CT + 2.7)   # таблетка на своём скотче поверх язычка
PRINT = [("01_lotok", tray, 0), ("02_kryshka_lotka", lid, 0), ("03_lenta_TPU", tape, 180), ("04_plastina_vmesto_platy", pcb, 0),
         ("05_telezhka", cart, 180), ("06_nakladka_telezhki", cover, 180)]
if __name__ == "__main__":
    import trimesh
    def iv(a, b):
        r = a & b
        try: return 0.0 if r is None else r.volume
        except Exception: return 0.0
    stat = {"лоток": tray, "крышка": lid, "лента": tape, "плата": pcb, "кнопки": btns}
    bad = 0
    for xc in (-22, -17.6, -13.2, -8.8, -4.4, 0, 4.4, 8.8, 13.2, 17.6, 22):
        mv = {"тележка": Pos(xc, 0, 0) * cart, "накладка": Pos(xc, 0, 0) * cover}
        for a, A in mv.items():
            for b, Bp in stat.items():
                v = iv(A, Bp)
                if v > 0.03: bad += 1; print("  ПЕРЕСЕЧЕНИЕ x=%+.1f %s × %s %.2f" % (xc, a, b, v))
    if iv(Pos(0, 0, 0.5) * cart, lid) < 0.01: bad += 1; print("  тележка снимается вверх")
    for d in (22.3, -22.3):
        if iv(Pos(d, 0, 0) * cart, lid) < 0.01: bad += 1; print("  упор не держит", d)
    pin_tip = BB(-2.3, 2.3, -2.3, 2.3, Z_LD1 - 0.6, Z_LD1 - 0.3)                                   # куда доходит штырь при нажатии 0.5 (продавив ленту на 0.3)
    on, off = iv(Pos(4.4, 0, 0) * pin_tip, bumps), iv(Pos(8.8, 0, 0) * pin_tip, bumps)
    print("над струной под штырём бугорок (%.2f мм³), между струн: %.2f — там под лентой сплошная крышка" % (on, off))
    if not (on > 0.01 and off < 0.01): bad += 1
    bad += (iv(cover, cart) > 0.03)
    print("проверка: %s" % ("ЧИСТО" if not bad else "%d проблем" % bad))
    for n, p, rot in PRINT:
        p = Rot(rot, 0, 0) * (Part() + p); bb = p.bounding_box(); p = Pos(-(bb.min.X + bb.max.X) / 2, -(bb.min.Y + bb.max.Y) / 2, -bb.min.Z) * p
        export_stl(p, "stl/%s.stl" % n, tolerance=0.01, angular_tolerance=0.1)
        m = trimesh.load("stl/%s.stl" % n); ov = float(m.area_faces[(m.face_normals[:, 2] < -0.72) & (m.triangles_center[:, 2] > 0.25)].sum())
        print("  %-26s %5.1f × %5.1f × %4.1f герм %s нависание %.0f мм²" % (n, bb.size.X, bb.size.Y, bb.size.Z, m.is_watertight, ov))
    os.makedirs("asm", exist_ok=True)
    for n, p in (("tray", tray), ("lid", lid), ("plungers", tape), ("pcb", pcb), ("btns", btns), ("res", res),
                 ("cart", Pos(4.4, 0, 0) * cart), ("cover", Pos(4.4, 0, 0) * cover), ("coin", Pos(4.4, 0, 0) * coin)):
        export_stl(Part() + p, "asm/%s.stl" % n, tolerance=0.02, angular_tolerance=0.2)
