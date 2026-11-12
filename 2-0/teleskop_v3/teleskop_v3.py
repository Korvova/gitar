# -*- coding: utf-8 -*-
r"""ТЕЛЕСКОП v3 (12.11.2026) — на основе v2, чтобы всё держалось при любом положении гитары и печаталось без поддержек:
  1) полка плоская; ползун ведёт брусок-прямоугольник, который лежит в пазу на его верху (вровень);
     брусок — отдельная деталь в пазах двух стоек у краёв, стойки же — упоры хода;
  2) мост — трапеция, тележка держится за неё губами (не поднимается), надевается на мост с торца до установки моста;
  3) планка сверху связывает обе оси плавающих шестерён — шестерни не соскакивают, оси не гнутся;
  4) оси плавающих шестерён Ø4, отверстия шестерён Ø4.5; шестерня мотора Ø3.3 — садится по трубке мотора без перекоса;
  5) неподвижная рейка заодно с основанием (как в v2).
X поперёк грифа, Y вдоль, Z = 0 — низ основания. Ход ползуна ±11, тележки ±22. Ширина 50.
Запуск из этой папки: ..\.venv-b123d\Scripts\python teleskop_v3.py
"""
import math, os
from build123d import *

HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
for d in ("stl", "asm"):
    os.makedirs(d, exist_ok=True)

M, PA = 0.8, math.radians(20)
P = math.pi * M
ZM, ZF = 11, 12
RM, RF = M * ZM / 2, M * ZF / 2            # 4.4, 4.8
A = 2.5 * P                                # плавающие шестерни на ±A от центра ползуна
HALF, S = 25.0, 11.0
Z_FL, MOT_H = 2.5, 12.23
Z_M1 = Z_FL + MOT_H
YM = 15.5                                  # ось мотора
L1 = (15.0, 18.5)                          # шестерня мотора + ползун
L2 = (18.7, 21.2)                          # плавающие шестерни + рейки + мост
Z_P0, Z_P1 = 21.4, 23.4                    # ложе
Y_FIX, Y_CART, Y_SL = -RF, RF, YM - RM
Y_ROOT = Y_FIX - 1.2 * M
Y0, Y1 = -8.5, YM + 15.6
Y_LEDGE = YM - 14.3                        # край полки
YB0, YB1 = 12.1, 17.1                      # мост внизу (по стойкам); вверху шире на DT
YBP = (YB0 + YB1) / 2
DT = 1.0                                   # мост шире вверху на 0.5 с каждой стороны
DTB = 0.8                                  # хвост балки ползуна
CW, SLX = 10.0, S + 1.5
RL0, RL1, RLH = -2.0, 1.0, 1.6             # балка ползуна: низ по Y, высота
C = 0.2                                    # зазор скользящих посадок
R_AX, R_FB = 2.0, 2.25                     # ось Ø4, отверстие шестерни Ø4.5
R_MB = 1.65                                # шестерня мотора Ø3.3
Z_ST0, Z_ST1 = L2[1] + 0.15, L2[1] + 1.65  # планка осей
PIN_X, PIN_Y, PIN_R = 24.4, -3.5, 0.95     # упоры: филамент 1.75 в отверстие Ø1.9


def BB(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))


def CZ(r, z0, z1, x=0.0, y=0.0):
    return Pos(x, y, z0) * Cylinder(r, z1 - z0, align=(Align.CENTER, Align.CENTER, Align.MIN))


def prof_x(pts, x0, x1):
    """профиль (y, z) вытянуть вдоль X от x0 до x1"""
    return Pos(x0, 0, 0) * Rot(90, 90, 0) * extrude(make_face(Polyline(*(pts + [pts[0]]))), x1 - x0, dir=(0, 0, 1))


def gear(z, z0, z1, gap_deg, bl=0.15):
    rp = M * z / 2
    rb, ra, rf = rp * math.cos(PA), rp + 0.9 * M, rp - 1.25 * M
    inv = lambda a: math.tan(a) - a
    ht = (P / 2 - bl) / (2 * rp)
    pts = []
    for i in range(z):
        c = 2 * math.pi * i / z
        fl = []
        for k in range(9):
            r = max(rb, rf) + (ra - max(rb, rf)) * k / 8
            fl.append((r, ht + inv(PA) - inv(math.acos(min(rb / r, 1.0)))))
        t = [(rf, -(ht + inv(PA) + 0.03))] + [(r, -a) for r, a in fl] + [(r, a) for r, a in reversed(fl)] + [(rf, ht + inv(PA) + 0.03)]
        pts += [(r * math.cos(c + a), r * math.sin(c + a)) for r, a in t]
    g = extrude(make_face(Polyline(*(pts + [pts[0]]))), z1 - z0)
    return Pos(0, 0, z0) * Rot(0, 0, gap_deg - 180.0 / z) * g


def rack(x0, x1, yp, sgn, z0, z1, body):
    tn, th, add, ded = math.tan(PA), (P / 2 - 0.15) / 2, 0.9 * M, 1.2 * M
    out = BB(x0, x1, yp - sgn * ded, yp - sgn * (ded + body), z0, z1)
    for k in range(int(x0 / P) - 1, int(x1 / P) + 2):
        xc = k * P
        pr = [(xc - th - ded * tn, yp - sgn * (ded + 0.01)), (xc - th + add * tn, yp + sgn * add), (xc + th - add * tn, yp + sgn * add), (xc + th + ded * tn, yp - sgn * (ded + 0.01))]
        out += Pos(0, 0, z0) * extrude(make_face(Polyline(*(pr + [pr[0]]))), z1 - z0, dir=(0, 0, 1))
    return out & BB(x0, x1, -50, 50, z0, z1)


# (1) основание: неподвижная рейка, полка с балкой-хвостом, стойки моста, гнездо мотора, отверстия упоров
base = BB(-HALF, HALF, Y0, Y1, 0, Z_FL)
base += BB(-HALF, HALF, Y0, Y_LEDGE, 0, L1[0])
# брусок-прямоугольник в пазу ползуна, вровень с ним: отдельная деталь, кладётся в пазы двух стоек сверху (капля клея); стойки же — упоры хода; ведёт ползун вбок, от подъёма не держит
BM_Y = (4.9, 8.1, 4.9, 8.1)                      # брусок-прямоугольник 3.2: низ y0..y1, верх y0..y1
Z_BM0, Z_BM1 = 16.5, 18.45
for sx in (-1, 1):
    base += BB(sx * (SLX + S + 0.2), sx * HALF, 3.7, YB0 + 0.01, 0, Z_BM1)       # стойка бруска = упор ползуна
    x0_, x1_ = sorted((sx * (SLX + S), sx * (HALF + 1)))
    base -= prof_x([(BM_Y[0] - 0.1, Z_BM0 - 0.05), (BM_Y[1] + 0.1, Z_BM0 - 0.05), (BM_Y[3] + 0.1, Z_BM1 + 1), (BM_Y[2] - 0.1, Z_BM1 + 1)], x0_, x1_)   # паз под конец бруска
beam = prof_x([(BM_Y[0], Z_BM0), (BM_Y[1], Z_BM0), (BM_Y[3], Z_BM1), (BM_Y[2], Z_BM1)], -HALF, HALF)
base += BB(-HALF, HALF, Y0, Y_ROOT + 0.01, 0, L2[1])
base += prof_x([(Y_ROOT, L2[0] - 1.7), (Y_ROOT, L2[0] + 0.01), (Y_FIX + 0.7 * M, L2[0] + 0.01)], -HALF, HALF)   # скос под зубьями
base += rack(-HALF, HALF, Y_FIX, 1, L2[0], L2[1], 0.3)
base += BB(-HALF, HALF, Y_ROOT, -4.0, L1[0] - 0.01, L2[0] - 0.2)                  # стенка под зубьями до ползуна (зазор 0.2), без пустоты
for sx in (-1, 1):
    base += BB(sx * 21, sx * HALF, YB0, YB1, 0, L2[0]) + CZ(1.5, L2[0] - 0.01, L2[1], sx * 22.5, YBP)
base += CZ(15.6, Z_FL - 0.01, Z_FL + 4, 0, YM) & BB(-HALF, HALF, Y_LEDGE, Y1, 0, 30)
base -= CZ(14.1, Z_FL, 40, 0, YM)
for ang in (45, 135, 225, 315):
    for r_ in (5.6, 6.1, 6.6):
        base -= CZ(1.3, -1, Z_FL + 1, r_ * math.cos(math.radians(ang)), YM + r_ * math.sin(math.radians(ang)))
base -= BB(-5.5, 5.5, YM + 6.0, YM + 12.5, -1, Z_FL + 1)
base -= CZ(5.0, Z_FL - 0.25, Z_FL + 1, 0, YM) + CZ(2.0, -1, Z_FL + 1, 0, YM)

# (2) мост-трапеция на штырьках
most = prof_x([(YB0, L2[0]), (YB1, L2[0]), (YB1 + DT, L2[1]), (YB0 - DT, L2[1])], -HALF, HALF)
for sx in (-1, 1):
    most -= CZ(1.62, 0, 40, sx * 22.5, YBP)

# (3) шестерня мотора и макет мотора
pin_m0 = gear(ZM, Z_M1 + 0.1, L1[1], -90) - CZ(R_MB, 0, 40)                    # у оси мотора, x = y = 0
pin_m = Pos(0, YM, 0) * pin_m0
motor = CZ(13.9, Z_FL, Z_M1, 0, YM) + CZ(1.5, Z_M1 - 0.01, L1[1], 0, YM)

# (4) ползун: паз-хвост снизу, рейка к мотору, две оси Ø4 до планки
sl = BB(-SLX, SLX, -3.8, Y_SL - 1.2 * M, *L1) + rack(-SLX, SLX, Y_SL, 1, L1[0], L1[1], 0.5)
sl -= prof_x([(BM_Y[0] - C, Z_BM0 - C), (BM_Y[1] + C, Z_BM0 - C), (BM_Y[3] + C, L1[1] + 1), (BM_Y[2] - C, L1[1] + 1)], -SLX - 1, SLX + 1)   # паз сверху под брусок
for x in (-A, A):
    sl += CZ(R_AX, L1[1] - 0.01, Z_ST1, x, 0)

# (5) плавающая шестерня ×2 (у своей оси) и планка осей
flo0 = gear(ZF, L2[0], L2[1], 90 + 180.0 / ZF) - CZ(R_FB, 0, 40)
strap = BB(-A - 2.8, A + 2.8, -1.8, 1.8, Z_ST0, Z_ST1) - CZ(R_AX + 0.02, 0, 40, -A, 0) - CZ(R_AX + 0.02, 0, 40, A, 0)

# (6) тележка: рейка спереди, губы по трапеции моста, ложе
Y_CF, Y_CB = YB0 - 0.2, YB1 + 0.2
cart = rack(-CW, CW, Y_CART, -1, L2[0], L2[1], Y_CF - (Y_CART + 1.2 * M))
cart -= prof_x([(Y_CF + 0.01, L2[0] - 0.01), (Y_CF + 0.01, L2[1] + 0.02), (Y_CF - DT, L2[1] + 0.02)], -CW - 1, CW + 1)   # передняя губа под мост
cart += BB(-CW, CW, Y_CB, Y_CB + 2.0, L2[0], Z_P0 + 0.01)
cart -= prof_x([(Y_CB - 0.01, L2[0] - 0.01), (Y_CB - 0.01, L2[1] + 0.02), (Y_CB + DT, L2[1] + 0.02)], -CW - 1, CW + 1)   # задняя губа под мост
cart += BB(-CW, CW, Y_CART + 1.2 * M, Y_CF - DT, L2[1] - 0.01, Z_P0 + 0.01)
cart += BB(-CW, CW, Y_CART + 1.2 * M, Y_CB + 2.0, Z_P0, Z_P1)                                       # ложе
BY = (Y_CF - 3.0, Y_CB - 1.0)
bort = BB(CW - 1.5, CW, Y_CART + 2, Y_CB + 1.5, Z_P1, Z_P1 + 3)
for y in BY:
    bort += BB(CW - 1.5, CW, y - 1.5, y + 1.5, Z_P1 - 1.4, Z_P1 + 0.01)
    for sx in (-1, 1):
        x0_, x1_ = sorted((sx * (CW - 1.6), sx * (CW + 1)))
        cart -= BB(x0_, x1_, y - 1.6, y + 1.6, Z_P1 - 1.5, Z_P1 + 1)

PRINT = [("01_osnovanie", base, 0, 1), ("02_most", most, 0, 1), ("03_shest_motora", pin_m0, 0, 1), ("04_maket_motora", motor, 0, 1),
         ("05_polzun", sl, 0, 1), ("06_shest_plav_x2", flo0, 0, 2), ("07_planka_osej", strap, 0, 1), ("08_telezhka", cart, 180, 1),
         ("09_bort_x2", Rot(0, 90, 0) * bort, 0, 2), ("10_brusok", beam, 0, 1)]


def pose(s):
    rf = -math.degrees(s / RF)
    return {"ползун": Pos(s, 0, 0) * sl, "планка": Pos(s, 0, 0) * strap,
            "плав1": Pos(s - A, 0, 0) * Rot(0, 0, rf) * flo0, "плав2": Pos(s + A, 0, 0) * Rot(0, 0, rf) * flo0,
            "шест.мотора": Pos(0, YM, 0) * Rot(0, 0, math.degrees(s / RM)) * pin_m0, "тележка": Pos(2 * s, 0, 0) * cart}


if __name__ == "__main__":
    import numpy as np, trimesh
    print("высота %.1f, основание %.0f × %.1f, тележка %.0f" % (Z_P1, 2 * HALF, Y1 - Y0, 2 * CW))
    stat = {"основание": base, "мост": most, "мотор": motor, "брусок": beam}
    bad = 0
    for s in (-S, -8.25, -5.5, -2.75, 0, 2.75, 5.5, 8.25, S):
        al = {**stat, **pose(s)}
        ns = list(al)
        for i, a in enumerate(ns):
            for b in ns[i + 1:]:
                if (a in stat and b in stat) or {a, b} == {"мотор", "шест.мотора"}:
                    continue
                try:
                    v = (al[a] & al[b]).volume
                except Exception:
                    v = 0.0
                if v > 0.03:
                    bad += 1
                    print("  ПЕРЕСЕЧЕНИЕ s=%+.2f %s × %s: %.2f мм³" % (s, a, b, v))
    for d in (S + 0.4, -S - 0.4):
        if (Pos(d, 0, 0) * sl & base).volume < 0.01:
            bad += 1
            print("  упор не держит на %+.1f" % d)
    def iv(a, b):
        r = a & b
        try:
            return 0.0 if r is None else r.volume
        except Exception:
            return 0.0
    for nm, part, other, lift in (("тележка", cart, most, 0.6),):
        if iv(Pos(0, 0, lift) * part, other) < 0.01:
            bad += 1
            print("  %s поднимается на %.1f мм — не держится" % (nm, lift))
    print("проверка хода и посадок: %s" % ("ЧИСТО" if not bad else "%d проблем" % bad))
    print("файлы на печать (нависания > 45° выше стола, без коротких мостиков):")
    for n, p, flip, cnt in PRINT:
        p = Rot(flip, 0, 0) * (Part() + p)
        bb = p.bounding_box()
        p = Pos(-(bb.min.X + bb.max.X) / 2, -(bb.min.Y + bb.max.Y) / 2, -bb.min.Z) * p
        export_stl(p, "stl/%s.stl" % n, tolerance=0.01, angular_tolerance=0.1)
        m = trimesh.load("stl/%s.stl" % n)
        cz = m.triangles_center[:, 2]; nz = m.face_normals[:, 2]
        over = (nz < -0.72) & (cz > 0.25)
        ov_area = float(m.area_faces[over].sum())
        print("  %-20s ×%d  %5.1f × %5.1f × %5.1f  герм %s  нависание %.1f мм²" % (n, cnt, bb.size.X, bb.size.Y, bb.size.Z, m.is_watertight, ov_area))
    for n, p in (("base", base), ("beam", beam), ("most", most), ("motor", motor), ("slider", sl), ("strap", strap), ("cart", cart), ("flo", flo0), ("pin_m", pin_m0)):
        export_stl(Part() + p, "asm/%s.stl" % n, tolerance=0.02, angular_tolerance=0.2)
    print("asm готово")
