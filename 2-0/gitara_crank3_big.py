# -*- coding: utf-8 -*-
"""Кривошип 3 с большим радиусом + хвост ленты 3 под него (проба владельца 27.09).

Зачем: с радиусом 4.8 крайние струны стоят почти в «мёртвых точках» кривошипа (±62°):
между струнами 1–2 и 5–6 диск крутится на 35°, а тележка едет медленно — палец не чувствует
движения. С радиусом R_BIG = 7.5 те же ±4.2 мм хода ленты — это ±34°, движение почти равномерное.

Кривошип — как astra_crank3_A3 (усиленный, «астра», стоит у владельца): та же посадка Ø5.8 на
шестерню, та же высота диска и пальца, тот же конус-усиление под диском; больше только радиус
пальца и диска. Палец — на ЗАПАДНОЙ стороне (x = −R_BIG): рабочий сектор 180° ± 50°.

Хвост 3: прорезь-кулиса только с западной стороны (x −10.3 … −1.5 от оси мотора), лента на
востоке (x 6…14) целая. Полный оборот больше нельзя — тележка уехала бы за концы прорези
в секции-1; прошивка держит мотор внутри откалиброванных струн.

Запуск: .venv-b123d\\Scripts\\python gitara_crank3_big.py -> Print/Print/gdk_crank3_big.stl, gdk_tail3_big.stl
"""
import math
import os
import sys
from build123d import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "Print", "Print")
sys.path.insert(0, HERE)

R_BIG = float(sys.argv[1]) if len(sys.argv) > 1 else 7.5       # 10 — под плечо 3 R16 (gitara_arm3_r16.py)
SFX = "big" if R_BIG == 7.5 else "r%g" % R_BIG
K = 3
Z_FLOOR = [3, 8.4, 13.8, 19.2]
FLANGE_Z = 0.0
SHAFT_OUT = 6.5
GEAR_D = 6.0
BORE_D = GEAR_D - 0.2
HUB_R = GEAR_D / 2 + 1.2
PIN_R = 2.5
DISK_T = 1.8
DISK_R = R_BIG + PIN_R + 1.0
SLOT_C = 0.15
LANE, MY3 = 10, 678
SLOT_X = (-(R_BIG + PIN_R + 0.3), -1.5)          # прорезь хвоста, от оси мотора (запад)
SWEEP = int(sys.argv[2]) if len(sys.argv) > 2 else 50                                       # рабочий сектор пальца: 180° ± 50°


def BB(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))


def disk_top(k):
    return Z_FLOOR[k] - 0.35


# ---------- кривошип: исходный v3 + усиление «астры» A3, радиус R_BIG, палец на западе ----------
dt = disk_top(K)
d0 = dt - DISK_T
hub_z0 = FLANGE_Z + 2.2
c = Pos(0, 0, d0 + DISK_T / 2) * Cylinder(DISK_R, DISK_T)
c += Pos(0, 0, (hub_z0 + d0) / 2) * Cylinder(HUB_R, d0 - hub_z0)
start = 3.4                                        # как у A3: шейка через дно 3 мм + зазор
height = min(4.1, d0 - start)
c += Pos(0, 0, start + height / 2) * Cone(HUB_R, DISK_R, height)
if d0 > start + height:
    c += Pos(0, 0, (start + height + d0) / 2) * Cylinder(DISK_R, d0 - start - height)
top = FLANGE_Z + SHAFT_OUT + 0.2
# посадка на шестерню z10 Ø6.0: круглое Ø5.8 проворачивалось (владелец 27.09) — теперь по зубьям.
# Профиль — star_hole из gitara_deka.py (купон 66, «звёздочка»), зазор STAR_C по радиусу
STAR_C = 0.10
GEAR_Z = 10
GEAR_M = GEAR_D / (GEAR_Z + 2)
R_TIP, R_ROOT = GEAR_D / 2, GEAR_D / 2 - 2.25 * GEAR_M
TOOTH_TIP_HALF, TOOTH_ROOT_HALF = 3.8, 15.0


def star_hole(cl, h, z0):
    pts = []
    pitch = 360.0 / GEAR_Z
    for i in range(GEAR_Z):
        a = i * pitch
        ra, rt = R_ROOT + cl, R_TIP + cl
        dr, dtt = math.degrees(cl / ra), math.degrees(cl / rt)
        hr = min(TOOTH_ROOT_HALF + dr, pitch / 2 - 1.0)      # не больше полушага — иначе контур пересекает сам себя
        ht = min(TOOTH_TIP_HALF + dtt, hr - 1.0)
        for ang, r in ((a - hr, ra), (a - ht, rt), (a + ht, rt), (a + hr, ra)):
            pts.append((r * math.cos(math.radians(ang)), r * math.sin(math.radians(ang))))
    pts.append(pts[0])
    return Pos(0, 0, z0) * extrude(make_face(Polyline(*pts)), h)


c -= star_hole(STAR_C, top - hub_z0 + 0.1, hub_z0 - 0.1)
pin_top = Z_FLOOR[K] + 1.45
c += Pos(-R_BIG, 0, (dt + pin_top) / 2) * Cylinder(PIN_R, pin_top - dt)
crank = Part() + c


# ---------- хвост ленты 3: как reference_tail3_v3, кулиса только на западе ----------
def lap_top(seg, y0):
    seg -= BB(-4.1, 4.1, y0 - 0.1, y0 + 18, -0.1, 0.8)
    seg -= Pos(0, y0 + 6.5, 1.2) * Cylinder(1.75, 1.0)
    seg += Pos(0, y0 + 11.5, 0.4) * Cylinder(1.5, 0.8)
    return seg


YOKE_HALF_Y = PIN_R + SLOT_C + 1.5
yc = MY3 - 480
ln = yc + YOKE_HALF_Y
t = lap_top(BB(-4, 4, 0, ln, 0, 1.6), 0)
x_w = SLOT_X[0] - 1.2 - LANE                        # западный край площадки (в системе ленты)
t += BB(x_w, -4, yc - YOKE_HALF_Y, ln, 0, 1.6)
t -= BB(SLOT_X[0] - LANE, SLOT_X[1] - LANE, yc - (PIN_R + SLOT_C), yc + (PIN_R + SLOT_C), -0.1, 1.7)
tail = Part() + t

for p, n in ((crank, "gdk_crank3_" + SFX), (tail, "gdk_tail3_" + SFX)):
    bb = p.bounding_box()
    print("%s: %.1f x %.1f x %.1f, solids %d" % (n, bb.size.X, bb.size.Y, bb.size.Z, len(p.solids())))
    export_stl(p, os.path.join(OUT, n + ".stl"))

# ================= ПРОВЕРКА: рабочий сектор 180° ± 50° с шагом 10° =================
from clearance import Assembly

asm = Assembly()
asm.add("d2", os.path.join(OUT, "gdk2_base_v3.stl"), loc=(0, 640, 0))
asm.add("d1", os.path.join(OUT, "gdk1_base_v3.stl"), loc=(0, 480, 0))
asm.add("motor3", os.path.join(OUT, "gdk_motor3_model.stl"), loc=(0, MY3, FLANGE_Z))
asm.add("tail2", os.path.join(OUT, "gdk_tail2_v3.stl"), loc=(LANE, 480, Z_FLOOR[2] + 0.05))
clear, touch = [], []
worst_pin = 99
for a in range(180 - SWEEP, 180 + SWEEP + 1, 10):
    th = math.radians(a)
    dy = -R_BIG * math.sin(th - math.pi)           # палец на западе: y пальца = R sin(a), лента едет с ним
    ypin = R_BIG * math.sin(th)
    cn, tn = "cr%d" % a, "tl%d" % a
    asm.add(cn, os.path.join(OUT, "gdk_crank3_" + SFX + ".stl"), loc=(0, MY3, 0), rz=a - 180)
    asm.add(tn, os.path.join(OUT, "gdk_tail3_" + SFX + ".stl"), loc=(LANE, 480 + ypin, Z_FLOOR[K] + 0.05))
    for obst, need in (("d2", 0.3), ("d1", 0.3), ("tail2", 0.2)):
        clear.append((cn, obst, need))
        clear.append((tn, obst, need))
    # свой мотор не проверяем: ступица сидит на его шестерне с натягом (как в gitara_deka.py); винты ушей на r 19+ — диск r 11 до них не достаёт
    clear.append((tn, "motor3", 0.3))
    clear.append((cn, tn, 0.05))                   # палец в прорези без вреза (зазор 0.15 по Y)
    xpin = R_BIG * math.cos(th)
    worst_pin = min(worst_pin, (xpin - PIN_R) - SLOT_X[0], SLOT_X[1] - (xpin + PIN_R))
print("палец в прорези по X: мин. запас до концов %.2f мм" % worst_pin)
assert worst_pin > 0.2, "палец упирается в конец прорези"
asm.check(clearances=[x for x in clear if x], touching=touch, verbose=False)
print("ход ленты в секторе ±%d°: ±%.2f мм (нужно ~±4.2 на струны 1–6)" % (SWEEP, R_BIG * math.sin(math.radians(SWEEP))))
