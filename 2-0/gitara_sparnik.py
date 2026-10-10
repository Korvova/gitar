# -*- coding: utf-8 -*-
r"""СТЕНД «СПАРНИК» (10.10.2026, идея владельца): два одинаковых диска R20 — на моторе и свободный — и планка
с круглыми дырками на их пальцах. Планка ходит параллельно сама себе (как спарник паровоза): каждая её точка
описывает круг R20, щель вдоль планки ходит поперёк ±20 — штырь тележки в щели ходит поперёк, вдоль скользит.
  * дно 52 × 170 (мотор там же, где у стенда 95: y 147, уши NEMA14 через проставку gdk_spacer0_x2);
    стенок нет — тележку с направляющими поставим потом;
  * диски лежат НАД полом; у мотора — ступица отдельно (spar_stupica: звёздочка по шестерне мотора, сверху
    шестигранник в гнездо диска), чтобы диск печатать плашмя без поддержек;
  * в середине хода (все пальцы и планка в одну линию) свободный диск может «передумать» — сначала проверяем так;
    запасной палец на 90° не ставим: он торчит сквозь уровень планки и на части хода упирается в неё;
  * дырки планки 5.3 (по выбору владельца, стол 98), щель 5.3 вдоль середины планки.
Запуск: .venv-b123d\Scripts\python gitara_sparnik.py
"""
import math
import os
from build123d import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "Print", "Print")

W, L = 52, 170
MY, YI = 147.0, 27.0              # центр мотора и свободного диска
D = MY - YI                       # 120 — длина планки ц-ц
R = 20.0                          # радиус пальцев
DISK_R = 23.5
PIN_R, HOLE_D = 2.5, 5.3
Z_FL = 3.0                        # верх пола
Z_D0, DISK_T = Z_FL + 0.3, 2.3    # диск над полом: 3.3 … 5.6
Z_BAR = Z_D0 + DISK_T + 0.3       # планка: 5.9 … 7.5
BAR_T, STICK = 1.6, 1.5
Z_TOP = Z_BAR + BAR_T + STICK     # верх пальцев: 9.0
HUB_R = 13.5                      # проходит внутри проставки (r 14.2)
D0 = -2.2                         # низ ступицы над пилотом мотора (как gdk_crank0_x2)
HEX = 12.0                        # шестигранник ступица -> диск, под ключ
EAR_R, EAR_ANG = 43.85 / 2, 56.0
GEAR_D, GEAR_Z = 6.0, 10
GEAR_M = GEAR_D / (GEAR_Z + 2)
R_TIP, R_ROOT = GEAR_D / 2, GEAR_D / 2 - 2.25 * GEAR_M


def BB(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))


def star_hole(c, h, z0):
    """Вырез по зубьям шестерни z10 (как gitara_mini2_sektor.py)."""
    pts, pitch = [], 360.0 / GEAR_Z
    for i in range(GEAR_Z):
        a = i * pitch
        ra, rt = R_ROOT + c, R_TIP + c
        hr = min(15.0 + math.degrees(c / ra), pitch / 2 - 1.0)
        ht = min(3.8 + math.degrees(c / rt), hr - 1.0)
        for ang, r in ((a - hr, ra), (a - ht, rt), (a + ht, rt), (a + hr, ra)):
            pts.append((r * math.cos(math.radians(ang)), r * math.sin(math.radians(ang))))
    pts.append(pts[0])
    return Pos(0, 0, z0) * extrude(make_face(Polyline(*pts)), h)


def hexagon(af, h, z0):
    return Pos(0, 0, z0) * extrude(RegularPolygon(af / 2 / math.cos(math.radians(30)), 6), h)


# ---------------- дно ----------------
base = BB(-W / 2, W / 2, 0, L, 0, Z_FL)
base -= Pos(0, MY, Z_FL / 2) * Cylinder(HUB_R + 0.5, Z_FL + 0.2)                      # проход ступицы
a = math.radians(EAR_ANG)
for ex, ey in ((EAR_R * math.sin(a), MY + EAR_R * math.cos(a)), (-EAR_R * math.sin(a), MY - EAR_R * math.cos(a))):
    base -= Pos(ex, ey, Z_FL / 2) * Cylinder(1.7, Z_FL + 0.2)                          # винты мотора
base += Pos(0, YI, (Z_FL + Z_D0) / 2) * Cylinder(4.0, Z_D0 - Z_FL)                     # шайба-подпятник под диск
stud_h = Z_D0 + DISK_T - 0.1 - Z_FL                                     # ось вровень с диском — над ней ходит планка
base += Pos(0, YI, Z_FL + stud_h / 2) * Cylinder(2.5, stud_h)                           # ось свободного диска Ø5
for x in (-20, 20):                                                                      # 4 дырки Ø3.4 — потом прикрутить направляющие тележки
    base -= Pos(x, 80, Z_FL / 2) * Cylinder(1.7, Z_FL + 0.2)
    base -= Pos(x, 95, Z_FL / 2) * Cylinder(1.7, Z_FL + 0.2)


# ---------------- диски: плашмя, палец вверх ----------------
def disk(center_hole):
    d = Pos(0, 0, DISK_T / 2) * Cylinder(DISK_R, DISK_T)
    d += Pos(R, 0, DISK_T + (Z_TOP - Z_D0 - DISK_T) / 2) * Cylinder(PIN_R, Z_TOP - Z_D0 - DISK_T)
    return d - center_hole


disk_m = disk(hexagon(HEX + 0.25, 2.0 + 0.1, -0.1))                                   # гнездо шестигранника снизу
disk_i = disk(Pos(0, 0, DISK_T / 2) * Cylinder(HOLE_D / 2, DISK_T + 0.2))              # на ось Ø5
# ступица мотора: звёздочка по шестерне, сверху шестигранник в гнездо диска
hub = Pos(0, 0, (Z_D0 - D0) / 2) * Cylinder(HUB_R, Z_D0 - D0) + hexagon(HEX, 2.0, Z_D0 - D0)
hub -= star_hole(0.10, Z_D0 - D0 + 2.2, -0.1)

# ---------------- планка: дырки на пальцы, щель вдоль середины ----------------
BW = 9.0
bar = Pos(0, 0, BAR_T / 2) * Cylinder(4.4, BAR_T) + Pos(0, D, BAR_T / 2) * Cylinder(4.4, BAR_T)
bar += BB(-BW / 2, BW / 2, 0, D, 0, BAR_T)
for y in (0, D):
    bar -= Pos(0, y, BAR_T / 2) * Cylinder(HOLE_D / 2, BAR_T + 0.2)
SL0, SL1 = 15.0, D - 15.0
bar -= BB(-HOLE_D / 2, HOLE_D / 2, SL0, SL1, -0.1, BAR_T + 0.1)

parts = [("spar_base", base), ("spar_disk_motor", disk_m), ("spar_disk_svob", disk_i), ("spar_stupica", hub),
         ("spar_planka", bar)]
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
asm.add("base", S("spar_base"))
asm.add("spacer", S("gdk_spacer0_x2"), loc=(0, MY, 0))
asm.add("motor", S("gdk_motor0_model"), loc=(0, MY, -4.0))
clear, touch = [], [("spacer", "base"), ("motor", "spacer")]
for thd in range(0, 360, 15):
    th = math.radians(thd)
    dm, di, hb, br = "dm%d" % thd, "di%d" % thd, "hub%d" % thd, "bar%d" % thd
    asm.add(hb, S("spar_stupica"), loc=(0, MY, D0), rz=thd)
    asm.add(dm, S("spar_disk_motor"), loc=(0, MY, Z_D0), rz=thd)
    asm.add(di, S("spar_disk_svob"), loc=(0, YI, Z_D0), rz=thd)
    asm.add(br, S("spar_planka"), loc=(R * math.cos(th), YI + R * math.sin(th), Z_BAR))
    clear += [(dm, "base", 0.3), (hb, "spacer", 0.3), (hb, "base", 0.3),
              (br, "base", 0.3)]   # планка с дисками — шарнир (зазор пальца 0.15), проверяется касанием
    touch += [(br, dm), (br, di), (hb, dm), (di, "base")]
asm.check(clearances=clear, touching=touch, verbose=False)
print("спарник: диски R%.0f, планка ц-ц %.0f, щель %.0f…%.0f, ход щели поперёк ±%.0f" % (R, D, SL0, SL1, R))
