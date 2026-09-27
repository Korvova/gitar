# -*- coding: utf-8 -*-
"""СТЕНД ОДНОГО ПАЛЬЦА v2 — ШАТУН ПРЯМО НА КРИВОШИП (указательный, 27.09.2026).

Идеи владельца: «не люблю перемычки, когда ходит внутри дырки-прямоугольника — чем меньше ходят,
тем лучше» и «зачем посредники — зелёную сразу на пимку в колесе». Здесь нет ни ленты, ни прорезей:
шарнирный четырёхзвенник — кривошип R10 (мотор, полный оборот) → шатун (две круглые дырки) → плечо
(качается на оси) → штырь → ложе. Только повороты в круглых дырках.
  * размеры подобраны так, чтобы полный оборот кривошипа давал ложе ровно ±20 (как стенд v1):
    длинное плечо LB и шатун LC считаются ниже из условия «крайние положения плеча — когда
    кривошип и шатун на одной линии»;
  * слои: плечо на полу (стад вверх) → шатун над ним на стаде плеча и пальце кривошипа;
    кривошип свой (палец выше, чем у gdk_crank0_x2, — под шатун), проставка — gdk_spacer0_x2;
  * всё печатается без поддержек; высота до палубы — 24; штырьки торчат над деталями на 1.5 (потолок 8.3).
В полном грифе так нельзя: мотор в деке в 50 см от плеча — там лента остаётся.
Запуск: .venv-b123d\\Scripts\\python gitara_mini2.py
"""
import math
import os
from build123d import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "Print", "Print")

W, L = 52, 100
CART_Y = 16                     # ложе
MY = 80.0                       # мотор
R_CR, PIN_R = 10.0, 2.5
RS = 18.0                       # короткое плечо: стад под шатун
DISK_R = R_CR + PIN_R + 1.0
FIT_D, HOLE_D = 5.1, 5.2        # на стад оси — плотно; дырки шатуна — свободно
Z_FL = 3.0
Z_ARM = Z_FL + 0.2              # плечо на полу
Z_LINK = Z_ARM + 1.6 + 0.2      # шатун: 5.0
STICK = 1.5                     # штырьки торчат над своей деталью (владелец: впритык могут выскочить)
Z_TOP = Z_LINK + 1.6 + STICK    # верх пальца кривошипа и стада плеча: 8.1
Z_CEIL = Z_TOP + 0.2            # потолок: 8.3
CEIL_T = 1.6
Z_DECK, DECK_T = 21.0, 3.0      # палуба: верх 24
RUN = 2.9
TRAVEL = 20.0                   # ложе ±20
EAR_R, EAR_ANG, EAR_SIGN = 43.85 / 2, 56.0, 1


def extremes(lb):
    """Для длинного плеча lb: расстояния от оси мотора до стада плеча в крайних положениях."""
    ax = CART_Y + lb
    d = MY - ax
    s = TRAVEL / lb
    return math.sqrt(RS ** 2 + d ** 2 + 2 * d * RS * s), math.sqrt(RS ** 2 + d ** 2 - 2 * d * RS * s)


lo, hi = 25.0, 45.0                                                 # LB: разность крайних = 2R
for _ in range(60):
    mid = (lo + hi) / 2
    dm, dp = extremes(mid)
    if dm - dp > 2 * R_CR:
        lo = mid
    else:
        hi = mid
LB = round((lo + hi) / 2, 2)
AX = CART_Y + LB
dm, dp = extremes(LB)
LC = round((dm + dp) / 2, 2)                                        # шатун центр — центр
TIE = [(23.5, 6), (-23.5, 6), (23.5, 36), (-23.5, 40), (23.5, L - 8), (-23.5, L - 8)]   # (23.5, 36): южнее 27 ходит пад штыря, севернее 43 — стад плеча


def BB(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))


def ear_holes():
    a = math.radians(EAR_ANG)
    dx, dy = EAR_R * math.sin(a), EAR_R * math.cos(a)
    return [(EAR_SIGN * dx, MY + dy), (-EAR_SIGN * dx, MY - dy)]


def walls(z0, z1):
    w = BB(-26, -24, 0, L, z0, z1) + BB(24, 26, 0, L, z0, z1)
    w += BB(-24, 24, 0, 2, z0, z1) + BB(-24, 24, L - 2, L, z0, z1)
    for x, y in TIE:
        s = 1 if x > 0 else -1
        w += BB(s * 21, s * 26, y - 4, y + 4, z0, z1)
    return w


def ties(part, z0, z1, r):
    for x, y in TIE:
        part -= Pos(x, y, (z0 + z1) / 2) * Cylinder(r, z1 - z0 + 0.2)
    return part


PHI_MAX = math.asin(TRAVEL / LB)
SLOT = BB(-24.5, 24.5, CART_Y - 3.5, CART_Y + max(LB * (1 - math.cos(PHI_MAX)) + 3.2, 10.7), -50, 50)   # прорезь штыря; 10.7 — под полозья ложа v3

# ---------------- дно ----------------
base = BB(-26, 26, 0, L, 0, Z_FL) + walls(Z_FL, Z_CEIL)
base += Pos(0, AX, (Z_FL + Z_ARM + 1.6 + STICK) / 2) * Cylinder(2.5, Z_ARM + 1.6 + STICK - Z_FL)   # стад оси: торчит над плечом на 1.5
base -= Pos(0, MY, Z_FL / 2) * Cylinder(DISK_R + 0.5, Z_FL + 0.2)  # окно кривошипа
for ex, ey in ear_holes():
    base -= Pos(ex, ey, Z_FL / 2) * Cylinder(1.7, Z_FL + 0.2)
base = ties(base, 0.8, Z_CEIL, 1.3)

# ---------------- середина и палуба (как стенд v1) ----------------
mid = BB(-26, 26, 0, L, 0, CEIL_T) + walls(CEIL_T, Z_DECK - Z_CEIL)
mid -= SLOT
mid = ties(mid, 0, Z_DECK - Z_CEIL, 1.7)
deck = BB(-26, 26, 0, L, 0, DECK_T) - SLOT
for ry in (CART_Y - 12, CART_Y + 12):
    deck += BB(-26, 26, ry - 1.5, ry + 1.5, DECK_T, DECK_T + 4)
deck = ties(deck, 0, DECK_T + 4, 1.7)
for sx in (-22.0, -13.2, -4.4, 4.4, 13.2, 22.0):
    y0, y1 = CART_Y + 13.5 + 1.5, L - 1
    r = Pos(sx, (y0 + y1) / 2, DECK_T) * Rot(90, 0, 0) * Cylinder(0.6, y1 - y0)
    r -= BB(sx - 1, sx + 1, y0 - 1, y1 + 1, DECK_T - 0.7, DECK_T)
    for tx, ty in TIE:
        if abs(tx - sx) < 3.6:
            r -= Pos(tx, ty, DECK_T) * Cylinder(3.6, 3)
    deck += r

# ---------------- плечо: на полу, круглая дырка на оси, стад вверх под шатун, штырь в ложе ----------------
LZ_T = 2.0                                                          # дно ложа v3
PIN_TOP = Z_DECK + DECK_T + LZ_T + 0.3                              # штырь на 0.3 выше дна ложа: шайба держит ложе, не зажимая
SCREW_D, SCREW_H = 2.6, 10.0                                        # дырка под самонарез М3 с шайбой (владелец)
WASHER_R, HEAD_R, HEAD_H = 3.5, 2.75, 2.2                           # шайба М3 Ø7, головка — для проверки
arm = Pos(0, 0, 0.8) * Cylinder(5, 1.6)
arm += BB(-2.5, 2.5, -LB, 0, 0, 1.6) + Pos(0, -LB, 0.8) * Cylinder(3.5, 1.6)
arm += BB(0, RS, -2.5, 2.5, 0, 1.6) + Pos(RS, 0, 0.8) * Cylinder(4, 1.6)
arm -= Pos(0, 0, 0.8) * Cylinder(FIT_D / 2, 1.8)
arm += Pos(RS, 0, 1.6 + (Z_TOP - Z_ARM - 1.6) / 2) * Cylinder(2.5, Z_TOP - Z_ARM - 1.6)   # стад под шатун, торчит на 1.5
pin_h = PIN_TOP - (Z_ARM + 1.6)
arm += Pos(0, -LB, 1.6 + pin_h / 2) * Cylinder(2.5, pin_h)
arm -= Pos(0, -LB, 1.6 + pin_h - SCREW_H / 2 + 0.05) * Cylinder(SCREW_D / 2, SCREW_H + 0.1)
screw = Pos(0, 0, 0.25) * Cylinder(WASHER_R, 0.5) + Pos(0, 0, 0.5 + HEAD_H / 2) * Cylinder(HEAD_R, HEAD_H)   # шайба + головка (только проверка)

# ---------------- шатун: дырка у кривошипа (0, 0), у плеча (0, LC) ----------------
link = Pos(0, 0, 0.8) * Cylinder(4.4, 1.6) + Pos(0, LC, 0.8) * Cylinder(4.4, 1.6)
link += BB(-2.8, 2.8, 0, LC, 0, 1.6)
for y in (0, LC):
    link -= Pos(0, y, 0.8) * Cylinder(HOLE_D / 2, 1.8)

# ---------------- кривошип стенда: как gdk_crank0_x2, палец до верха шатуна ----------------
GEAR_D, GEAR_Z = 6.0, 10
GEAR_M = GEAR_D / (GEAR_Z + 2)
R_TIP, R_ROOT = GEAR_D / 2, GEAR_D / 2 - 2.25 * GEAR_M


def star_hole(c, h, z0):
    """Вырез по зубьям шестерни z10 (как в gitara_deka.py, купон 66)."""
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


D0, DT = -2.2, Z_FL - 0.35                                          # как gdk_crank0_x2: над пилотом мотора, под полом
crank = Pos(0, 0, (D0 + DT) / 2) * Cylinder(DISK_R, DT - D0)
crank -= star_hole(0.10, DT - D0 + 0.2, D0 - 0.1)
crank += Pos(R_CR, 0, (DT + Z_TOP) / 2) * Cylinder(PIN_R, Z_TOP - DT)                 # палец: торчит над шатуном на 1.5

parts = [("mini2_base", base), ("mini2_mid", mid), ("mini2_deck", deck), ("mini2_arm", arm),
         ("mini2_shatun", link), ("mini2_crank", crank), ("mini2_vint_proverka", screw)]
for n, p in parts:
    p = Part() + p
    bb = p.bounding_box()
    print("%s: %.1f x %.1f x %.1f, solids %d" % (n, bb.size.X, bb.size.Y, bb.size.Z, len(p.solids())))
    export_stl(p, os.path.join(OUT, n + ".stl"))


# ================= ПРОВЕРКА: полный оборот шагом 15° =================
def rocker(th):
    """Положение плеча при угле кривошипа th: стад плеча — пересечение окружностей (восточная точка)."""
    cx, cy = R_CR * math.cos(th), MY + R_CR * math.sin(th)
    dx, dy = cx, cy - AX
    d = math.hypot(dx, dy)
    a = (RS ** 2 - LC ** 2 + d ** 2) / (2 * d)
    h = math.sqrt(max(RS ** 2 - a ** 2, 0))
    px, py = a * dx / d, a * dy / d
    cands = [(px + h * dy / d, py - h * dx / d), (px - h * dy / d, py + h * dx / d)]
    sx, sy = max(cands, key=lambda q: q[0])
    return math.atan2(sy, sx), (cx, cy), (sx, AX + sy)


from clearance import Assembly


def S(n):
    return os.path.join(OUT, n + ".stl")


asm = Assembly()
asm.add("base", S("mini2_base"))
asm.add("mid", S("mini2_mid"), loc=(0, 0, Z_CEIL))
asm.add("deck", S("mini2_deck"), loc=(0, 0, Z_DECK))
asm.add("spacer", S("gdk_spacer0_x2"), loc=(0, MY, 0))
asm.add("motor", S("gdk_motor0_model"), loc=(0, MY, -4.0))
clear, touch = [], [("base", "mid"), ("mid", "deck"), ("spacer", "base"), ("motor", "spacer")]
worst, tr_min = 0, 180
for thd in range(0, 360, 15):
    th = math.radians(thd)
    phi, (cx, cy), (sx, sy) = rocker(th)
    worst = max(worst, abs(LB * math.sin(phi)))
    ang = math.degrees(math.acos(abs(((cx - sx) * (sx - 0) + (cy - sy) * (sy - AX)) / (LC * RS))))
    tr_min = min(tr_min, ang)                                       # угол передачи: шатун к плечу
    alpha = math.degrees(math.atan2(-(sx - cx), sy - cy))           # шатун: локальная +Y — на стад плеча
    c, a, k, z = "cr%d" % thd, "arm%d" % thd, "sh%d" % thd, "lz%d" % thd
    asm.add(c, S("mini2_crank"), loc=(0, MY, 0), rz=thd)
    asm.add(a, S("mini2_arm"), loc=(0, AX, Z_ARM), rz=math.degrees(phi))
    asm.add(k, S("mini2_shatun"), loc=(cx, cy, Z_LINK), rz=alpha)
    asm.add(z, S("gs1_lozhe_v3"), loc=(LB * math.sin(phi), CART_Y, Z_DECK + DECK_T - RUN))
    w = "sc%d" % thd
    asm.add(w, S("mini2_vint_proverka"), loc=(LB * math.sin(phi), AX - LB * math.cos(phi), PIN_TOP))
    clear += [(w, z, 0.1)]                                          # шайба над дном ложа и мимо бортиков
    clear += [(c, "base", 0.3), (c, "spacer", 0.3), (c, "mid", 0.15), (c, a, 0.5),
              (a, "base", 0.01), (a, "mid", 0.15), (a, "deck", 0.15), (a, z, 0.0),
              (k, "base", 0.1), (k, "mid", 0.15), (k, z, 0.3)]
    touch += [(k, c), (k, a), (z, "deck")]
asm.check(clearances=clear, touching=touch, verbose=False)
print("стенд с шатуном: LB %.2f, шатун %.2f, ось плеча y %.2f; ложе ±%.1f; мин. угол передачи %.0f°"
      % (LB, LC, AX, worst, tr_min))
