# -*- coding: utf-8 -*-
r"""МАКЕТ «ВТОРОЙ ДИСК У ТЕЛЕЖКИ» (10.10.2026, идея владельца, один палец, один мотор).
Диск на моторе (как стенд 99) — планка-спарник — второй диск у тележки повторяет поворот первого; его ВЫСОКИЙ
палец поднимается сквозь круглое окно мостика в прорезь тележки (прорезь вдоль грифа). Тележка-салазки лежит на
мостике между двумя бортиками и ходит только поперёк ±20: палец ходит по кругу, вдоль — скользит в прорези.
Давление пальца ученика уходит в ось второго диска — планка вбок не нагружена.
С стенда 99 (уже есть): диск на моторе spar_disk_motor, ступица spar_stupica. Новое: дно, второй диск с высоким
пальцем, планка без щели, мостик с окном, тележка-салазки.
Запуск: .venv-b123d\Scripts\python gitara_sparnik2.py
"""
import math
import os
from build123d import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "Print", "Print")

W = 52
Y0, L = -8.0, 170.0               # дно от y −8 до 170
MY, YI = 147.0, 27.0              # мотор и второй диск (у тележки)
D = MY - YI
R, DISK_R, PIN_R, HOLE_D = 20.0, 23.5, 2.5, 5.3
Z_FL = 3.0
Z_D0, DISK_T = Z_FL + 0.3, 2.3    # диски 3.3 … 5.6
Z_BAR, BAR_T = Z_D0 + DISK_T + 0.3, 1.6       # планка 5.9 … 7.5
Z_BR0, BR_T = Z_BAR + BAR_T + 0.5, 2.0        # мостик 8.0 … 10.0
Z_SL0, SL_T = Z_BR0 + BR_T + 0.3, 2.0         # салазки 10.3 … 12.3
Z_PT = Z_SL0 + SL_T - 0.3                     # верх высокого пальца 12.0
WIN_R = R + PIN_R + 0.7                       # окно мостика под круг пальца
SL_HY = 27.0                                  # салазки ±27 вдоль грифа (лежат на мостике за окном)
RAIL_IN = SL_HY + 0.3
BR_HX = R + 13 + 2                            # мостик ±35 поперёк (салазки ±13 ходят ±20)
LEG_X, LEG_YS = 32.0, (YI - 24, YI + 24)
EAR_R, EAR_ANG = 43.85 / 2, 56.0


def BB(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))


# ---------------- дно: мотор как у стенда 99, ось второго диска, ножки мостика ----------------
base = BB(-W / 2, W / 2, Y0, L, 0, Z_FL)
base += BB(-BR_HX, BR_HX, YI - 30, YI + 30, 0, Z_FL)                                     # уши под ножки мостика
base -= Pos(0, MY, Z_FL / 2) * Cylinder(13.5 + 0.5, Z_FL + 0.2)
a = math.radians(EAR_ANG)
for ex, ey in ((EAR_R * math.sin(a), MY + EAR_R * math.cos(a)), (-EAR_R * math.sin(a), MY - EAR_R * math.cos(a))):
    base -= Pos(ex, ey, Z_FL / 2) * Cylinder(1.7, Z_FL + 0.2)
base += Pos(0, YI, (Z_FL + Z_D0) / 2) * Cylinder(4.0, Z_D0 - Z_FL)                     # подпятник
stud_h = Z_D0 + DISK_T - 0.1 - Z_FL
base += Pos(0, YI, Z_FL + stud_h / 2) * Cylinder(2.5, stud_h)                           # ось второго диска
for ly in LEG_YS:
    for sx in (1, -1):
        base += BB(sx * LEG_X - 2.5, sx * LEG_X + 2.5, ly - 2.5, ly + 2.5, Z_FL, Z_BR0)  # вне маха планки (±24.5)
        base -= Pos(sx * LEG_X, ly, Z_BR0 - 4) * Cylinder(1.3, 8.1)                      # самонарез М3

# ---------------- второй диск: высокий палец до прорези салазок ----------------
disk2 = Pos(0, 0, DISK_T / 2) * Cylinder(DISK_R, DISK_T)
disk2 += Pos(R, 0, DISK_T + (Z_PT - Z_D0 - DISK_T) / 2) * Cylinder(PIN_R, Z_PT - Z_D0 - DISK_T)
disk2 -= Pos(0, 0, DISK_T / 2) * Cylinder(HOLE_D / 2, DISK_T + 0.2)

# ---------------- планка без щели ----------------
bar = Pos(0, 0, BAR_T / 2) * Cylinder(4.4, BAR_T) + Pos(0, D, BAR_T / 2) * Cylinder(4.4, BAR_T)
bar += BB(-3.5, 3.5, 0, D, 0, BAR_T)
for y in (0, D):
    bar -= Pos(0, y, BAR_T / 2) * Cylinder(HOLE_D / 2, BAR_T + 0.2)

# ---------------- мостик: круглое окно под палец, бортики вдоль поперёк (держат салазки) ----------------
most = BB(-BR_HX, BR_HX, -30, 30, 0, BR_T)
most -= Pos(0, 0, BR_T / 2) * Cylinder(WIN_R, BR_T + 0.2)
for sy in (1, -1):
    y0, y1 = sorted((sy * RAIL_IN, sy * (RAIL_IN + 2.5)))
    most += BB(-BR_HX, BR_HX, y0, y1, BR_T, BR_T + 2.5)
for ly in LEG_YS:
    for sx in (1, -1):
        most -= Pos(sx * LEG_X, ly - YI, BR_T / 2) * Cylinder(1.7, BR_T + 0.2)

# ---------------- салазки-тележка: прорезь вдоль грифа под палец, бортики под палец ученика ----------------
sl = BB(-13, 13, -SL_HY, SL_HY, 0, SL_T)
sl -= BB(-HOLE_D / 2 - 0.05, HOLE_D / 2 + 0.05, -(R + PIN_R + 0.4), R + PIN_R + 0.4, -0.1, SL_T + 0.1)
for sx in (1, -1):
    sl += BB(sx * 13 - (1.6 if sx > 0 else 0), sx * 13 + (0 if sx > 0 else 1.6), -10, 10, SL_T, SL_T + 6)   # бортики ложа

parts = [("spar2_base", base), ("spar2_disk", disk2), ("spar2_planka", bar), ("spar2_most", most), ("spar2_salazki", sl)]
for n, p in parts:
    p = Part() + p
    bb = p.bounding_box()
    print("%s: %.1f x %.1f x %.1f, solids %d" % (n, bb.size.X, bb.size.Y, bb.size.Z, len(p.solids())))
    export_stl(p, os.path.join(OUT, n + ".stl"))

# ================= ПРОВЕРКА: полный оборот шагом 15° =================
from clearance import Assembly


def S(n):
    return os.path.join(OUT, n + ".stl")


asm = Assembly()
asm.add("base", S("spar2_base"))
asm.add("spacer", S("gdk_spacer0_x2"), loc=(0, MY, 0))
asm.add("motor", S("gdk_motor0_model"), loc=(0, MY, -4.0))
asm.add("most", S("spar2_most"), loc=(0, YI, Z_BR0))
clear, touch = [], [("spacer", "base"), ("motor", "spacer"), ("most", "base")]
for thd in range(0, 360, 15):
    th = math.radians(thd)
    dm, di, hb, br, sl_ = "dm%d" % thd, "di%d" % thd, "hub%d" % thd, "bar%d" % thd, "sl%d" % thd
    asm.add(hb, S("spar_stupica"), loc=(0, MY, -2.2), rz=thd)
    asm.add(dm, S("spar_disk_motor"), loc=(0, MY, Z_D0), rz=thd)
    asm.add(di, S("spar2_disk"), loc=(0, YI, Z_D0), rz=thd)
    asm.add(br, S("spar2_planka"), loc=(R * math.cos(th), YI + R * math.sin(th), Z_BAR))
    asm.add(sl_, S("spar2_salazki"), loc=(R * math.cos(th), YI, Z_SL0))
    clear += [(dm, "base", 0.3), (hb, "spacer", 0.3), (hb, "base", 0.3), (br, "base", 0.3), (br, "most", 0.3),
              (di, "most", 0.3), (dm, "most", 0.3), (sl_, "base", 0.3)]
    touch += [(br, dm), (br, di), (hb, dm), (di, "base"), (sl_, "most"), (sl_, di)]
asm.check(clearances=clear, touching=touch, verbose=False)
print("макет «второй диск у тележки»: диски R%.0f, планка ц-ц %.0f, тележка поперёк ±%.0f" % (R, D, R))
