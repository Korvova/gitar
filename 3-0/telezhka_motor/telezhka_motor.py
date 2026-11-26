# -*- coding: utf-8 -*-
"""Блок на 2 пальца «тележка = мотор» (26.11, владелец): GB1806 ПЛАШМЯ — ротор вниз (на нём шестерня z10), стакан с AS5600 вверх.
Шестерня катится по неподвижной рейке на полу; тележка (шапка на стакане + 2 ножки + полоз) скользит полозом по рельсу-ласточке.
Кнопка Ø6.4×5 на шапке, над ней клавиша-площадка 15×15 на гибкой шейке. Детали: основание (1), тележка ×2 (разные места площадки), клавиша ×2, шестерня ×2.
Запуск: python telezhka_motor.py → STL в ./stl, сборка в ./asm (для blender_telezhka_motor.py)."""
import os, math
from build123d import *
HERE = os.path.dirname(os.path.abspath(__file__))
OUT, ASM = os.path.join(HERE, "stl"), os.path.join(HERE, "asm")
for d in (OUT, ASM):
    os.makedirs(d, exist_ok=True)
    for f in os.listdir(d):
        if f.endswith(".stl"): os.remove(os.path.join(d, f))
M, PA = 1.0, math.radians(20); P = math.pi * M


def BB(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))


def CZ(r, z0, z1, x=0.0, y=0.0):
    return Pos(x, y, z0) * Cylinder(r, z1 - z0, align=(Align.CENTER, Align.CENTER, Align.MIN))


def prof_x(pts, x0, x1):                                   # профиль (y, z) вдоль X
    return Pos(x0, 0, 0) * Rot(90, 90, 0) * extrude(make_face(Polyline(*(pts + [pts[0]]))), x1 - x0, dir=(0, 0, 1))


def gear(z, z0, z1, bl=0.15):
    rp = M * z / 2; rb, ra, rf = rp * math.cos(PA), rp + 0.9 * M, rp - 1.25 * M
    inv = lambda a: math.tan(a) - a
    ht = (P / 2 - bl) / (2 * rp); pts = []
    for i in range(z):
        c = 2 * math.pi * i / z; fl = []
        for k in range(9):
            r = max(rb, rf) + (ra - max(rb, rf)) * k / 8
            fl.append((r, ht + inv(PA) - inv(math.acos(min(rb / r, 1.0)))))
        t = [(rf, -(ht + inv(PA) + 0.03))] + [(r, -a) for r, a in fl] + [(r, a) for r, a in reversed(fl)] + [(rf, ht + inv(PA) + 0.03)]
        pts += [(r * math.cos(c + a), r * math.sin(c + a)) for r, a in t]
    return Pos(0, 0, z0) * extrude(make_face(Polyline(*(pts + [pts[0]]))), z1 - z0)


def rack(x0, x1, yp, sgn, z0, z1, body):                   # рейка вдоль X, делительная y=yp, зубья в сторону sgn
    tn, th, add, ded = math.tan(PA), (P / 2 - 0.15) / 2, 0.9 * M, 1.2 * M
    out = BB(x0, x1, yp - sgn * ded, yp - sgn * (ded + body), z0, z1)
    for k in range(int(x0 / P) - 1, int(x1 / P) + 2):
        xc = k * P
        pr = [(xc - th - ded * tn, yp - sgn * (ded + 0.01)), (xc - th + add * tn, yp + sgn * add), (xc + th - add * tn, yp + sgn * add), (xc + th + ded * tn, yp - sgn * (ded + 0.01))]
        out += Pos(0, 0, z0) * extrude(make_face(Polyline(*(pr + [pr[0]]))), z1 - z0, dir=(0, 0, 1))
    return out & BB(x0, x1, -80, 80, z0, z1)


def iv(a, b):
    try:
        r = a & b
        return 0.0 if r is None else r.volume
    except Exception:
        return 0.0


# ---------- размеры ----------
HALF, FL = 25.0, 2.5                                       # полуширина грифа, пол основания 0..2.5
LANE, PITCH, S = 23.0, 17.0, 22.0                          # шаг тележек вдоль грифа (мотор Ø22), шаг площадок, ход ±22
ZP = 5.0                                                   # шестерня z10 → делительный радиус 5
Z_G0, Z_G1 = FL + 0.3, FL + 3.3                            # шестерня 2.8..5.8
Z_RF = Z_G1 + 0.3                                          # торец ротора 6.1 (ротор внизу)
R_M, H_M, H_CAP = 11.0, 13.0, 7.5                          # мотор Ø22 × 13 + стакан 7.5 (чертёж продавца)
Z_CAP1 = Z_RF + H_M + H_CAP                                # верх стакана 26.6
T_HAT = 1.6
Z_HAT1 = Z_CAP1 + T_HAT                                    # шапка тележки на стакане
BTN_D, BTN_H, BTN_HP, BTN_DP = 6.4, 3.5, 1.5, 2.6          # кнопка Ø6.4 × (3.5 + шток 1.5)
Z_PAD0 = Z_HAT1 + BTN_H + BTN_HP + 0.1                     # низ клавиши на 0.1 над штоком
T_PAD = 1.4
Y_RAIL, RAIL_B, RAIL_T, RAIL_H = -8.8, 0.8, 1.3, 2.5       # рельс-ласточка: от оси мотора −8.8, низ ±0.8, верх ±1.3 (всё в пределах своей ленты ±11.5)
G = 0.25                                                    # зазор полоза на рельсе
XA0, XA1 = 12.1, 13.4                                       # ножки тележки по бокам мотора (крутится колокол Ø22)
YR0, YR1 = -11.3, -6.3                                      # полоз — в стороне от шестерни (её Ø11.8) и не выходит за свою ленту
PADS = [-9.0, -26.0]                                        # 26.11: блок = ПОЛОВИНА четвёрки: площадки сдвинуты от осей на −9 и −3 (вторая половина — этот же блок, повёрнутый на 180°: +3, +9)
Y_LO, Y_HI = -1.5 * LANE, 0.5 * LANE                       # стык половин — посередине между лентами 2 и 3

# ---------- основание: пол + 2 рейки + 2 рельса ----------
base = BB(-HALF, HALF, Y_LO, Y_HI, 0, FL)
for k in range(2):
    yc = -LANE * k
    base += rack(-HALF, HALF, yc + ZP, -1, FL - 0.01, Z_G1, 1.8)
    yr = yc + Y_RAIL
    base += prof_x([(yr - RAIL_B, FL - 0.01), (yr + RAIL_B, FL - 0.01), (yr + RAIL_T, FL + RAIL_H), (yr - RAIL_T, FL + RAIL_H)], -HALF, HALF)

# ---------- шестерня на ротор: z10 + ступица до торца ротора + 4 штыря Ø1.9 в отверстия М2 (Ø6) ----------
pin = gear(10, Z_G0, Z_G1) + CZ(3.9, Z_G1 - 0.01, Z_RF + 0.01)
for a in (0, 90, 180, 270):
    pin += CZ(0.95, Z_RF, Z_RF + 1.5, 3 * math.cos(math.radians(a)), 3 * math.sin(math.radians(a)))
pin -= CZ(0.8, Z_G0 - 1, Z_RF + 2)
motor = CZ(R_M, Z_RF, Z_RF + H_M) + CZ(R_M, Z_RF + H_M - 0.01, Z_CAP1)


def root_y(k):                                                  # корень клавиши — в пределах площадки ±5 и своей шапки
    yc = -LANE * k; yp = PADS[k]
    return max(yp - 5.0, yc - 10.8), min(yp + 5.0, yc + 10.8)


# ---------- тележка: шапка + 2 ножки + полоз с пазом-ласточкой + гнездо кнопки + гнездо корня клавиши ----------
def cart(k):
    yc = -LANE * k; yp = PADS[k]
    c = BB(-XA1, XA1, yc - 11.4, yc + 11.4, Z_CAP1, Z_HAT1)                       # шапка
    c -= CZ(5.0, Z_CAP1 - 1, Z_HAT1 + 1, 0, yc)                                  # центр открыт (головки винтов стакана)
    for a0 in (45, 135, 225, 315):                                               # 4 дуговых паза М2 на Ø18 (±20°)
        for da in range(-20, 21, 4):
            a = math.radians(a0 + da)
            c -= CZ(1.2, Z_CAP1 - 1, Z_HAT1 + 1, 9 * math.cos(a), yc + 9 * math.sin(a))
    legs = BB(-XA1, XA1, yc + YR0, yc + YR1, FL + 0.2, Z_G1)                                         # полоз
    for sx in (-1, 1):                                                                                # ножки + шип в гнездо шапки (клей)
        legs += BB(*sorted((sx * XA0, sx * XA1)), yc + YR0 + 1.0, yc + YR1, FL + 0.2, Z_CAP1)
        tn = BB(*sorted((sx * (XA0 + 0.25), sx * (XA1 - 0.25))), yc + YR0 + 1.4, yc + YR1 - 0.4, Z_CAP1 - 0.01, Z_CAP1 + 0.6)
        legs += tn; tb = tn.bounding_box()
        c -= BB(tb.min.X - 0.1, tb.max.X + 0.1, tb.min.Y - 0.1, tb.max.Y + 0.1, Z_CAP1 - 0.01, Z_CAP1 + 0.7)
    yr = yc + Y_RAIL
    legs -= prof_x([(yr - RAIL_B - G, FL - 0.5), (yr + RAIL_B + G, FL - 0.5), (yr + RAIL_T + G, FL + RAIL_H + G), (yr - RAIL_T - G, FL + RAIL_H + G)], -XA1 - 1, XA1 + 1)   # паз — сквозь полоз и ножки
    xb = 3.0                                                                                          # кнопка ближе к свободному краю клавиши
    ybn = min(max(yp, yc - 7.0), yc + 7.0)                                                            # кнопка — на своей шапке (площадка может свисать к соседу)
    ring = CZ(BTN_D / 2 + 0.15 + 0.8, Z_HAT1 - 0.01, Z_HAT1 + 2.5, xb, ybn) - CZ(BTN_D / 2 + 0.15, Z_HAT1, Z_HAT1 + 5, xb, ybn)
    ring -= BB(xb - 1.1, xb + 1.1, ybn - 5, ybn + 5, Z_HAT1, Z_HAT1 + 5)                           # щели под выводы
    c += ring
    r0, r1 = root_y(k)
    c -= BB(-7.5 - 0.1, -5.5 + 0.1, r0 - 0.1, r1 + 0.1, Z_HAT1 - 1.0, Z_HAT1 + 0.1)                 # гнездо корня клавиши
    btn = CZ(BTN_D / 2, Z_HAT1, Z_HAT1 + BTN_H, xb, ybn) + CZ(BTN_DP / 2, Z_HAT1 + BTN_H - 0.01, Z_HAT1 + BTN_H + BTN_HP, xb, ybn)
    return c, legs, btn


def key(k):                                                     # клавиша 15×15: корень слева (в гнездо шапки, клей), гибкая шейка, площадка
    yp = PADS[k]
    p = BB(-7.5, 7.5, yp - 7.5, yp + 7.5, Z_PAD0, Z_PAD0 + T_PAD)
    p -= BB(-5.5, -4.3, yp - 8, yp + 8, Z_PAD0 + 0.7, Z_PAD0 + T_PAD + 1)                           # шейка 0.7 — гнётся
    r0, r1 = root_y(k)
    p += BB(-7.5, -5.5, r0, r1, Z_HAT1 - 0.9, Z_PAD0 + 0.01)                                        # корень-стойка
    return p


carts = [cart(k) for k in range(2)]
keys = [key(k) for k in range(2)]


# ---------- проверка: ход ±22 (крайние и середина), обе тележки в разных фазах ----------
def moving(k, s):
    yc = -LANE * k; c, l, b = carts[k]
    return {"cart": Pos(s, 0, 0) * (c + l), "btn": Pos(s, 0, 0) * b, "key": Pos(s, 0, 0) * keys[k], "motor": Pos(s, yc, 0) * motor,
            "pin": Pos(s, yc, 0) * Rot(0, 0, math.degrees(-s / ZP)) * pin}


bad = 0
for s1 in (-S, 0, S):
    for s2 in (-S, 0, S):
        A, B = moving(0, s1), moving(1, s2)
        for na, qa in A.items():
            for nb, qb in B.items():
                v = iv(qa, qb)
                if v > 0.02: bad += 1; print("  лента1 %s(s=%+.0f) × лента2 %s(s=%+.0f): %.2f" % (na, s1, nb, s2, v))
ROT2 = lambda q: Pos(0, 2 * Y_LO, 0) * Rot(0, 0, 180) * q                    # вторая половина четвёрки
for s1 in (-S, 0, S):
    for s2 in (-S, 0, S):
        A = moving(1, s1); B = {n: ROT2(q) for n, q in moving(1, s2).items()}
        for na, qa in A.items():
            for nb, qb in B.items():
                v = iv(qa, qb)
                if v > 0.02: bad += 1; print("  стык половин: лента2 %s(s=%+.0f) × лента3 %s(s=%+.0f): %.2f" % (na, s1, nb, s2, v))
v = iv(base, ROT2(base)); print("  основания половин встык: пересечение %.3f" % v)
for k in range(2):
    for s in (-S, -S / 2, 0, S / 2, S):
        m = moving(k, s)
        for n in ("cart", "motor", "key"):
            v = iv(m[n], base)
            if v > 0.02: bad += 1; print("  лента%d %s × основание (s=%+.0f): %.2f" % (k + 1, n, s, v))
        for n1, n2 in (("cart", "motor"), ("cart", "pin"), ("key", "cart"), ("key", "btn"), ("btn", "motor")):
            v = iv(m[n1], m[n2])
            if v > 0.02: bad += 1; print("  лента%d %s × %s (s=%+.0f): %.2f" % (k + 1, n1, n2, s, v))
    vp = iv(Pos(0, -LANE * k, 0) * pin, base)
    print("  лента%d: шестерня × рейка %.3f мм³ (зацепление), верх клавиши %.1f мм" % (k + 1, vp, Z_PAD0 + T_PAD))
print("БЛОК «тележка = мотор» плашмя ×2: %s | длина %.1f, ширина %.0f, мотор в крайних за гриф на %.1f" % ("ЧИСТО" if not bad else "%d проблем" % bad, Y_HI - Y_LO, 2 * HALF, S + R_M - HALF))


# ---------- выгрузка ----------
def put(name, part, rot=(0, 0, 0)):
    p = Rot(*rot) * part; b = p.bounding_box(); p = Pos(-(b.min.X + b.max.X) / 2, -(b.min.Y + b.max.Y) / 2, -b.min.Z) * p
    export_stl(p, os.path.join(OUT, name + ".stl"), tolerance=0.01, angular_tolerance=0.1)


put("01_osnovanie", base)
put("02a_shapka_1", carts[0][0])
put("02b_shapka_2", carts[1][0])
put("05_nozhki_poloz_x2", carts[0][1])
put("03_klavisha_x2", keys[0], (180, 0, 0))
put("04_shesternya_x2", pin)
for n, p in (("base", base), ("cart1", carts[0][0] + carts[0][1]), ("cart2", carts[1][0] + carts[1][1]), ("key1", keys[0]), ("key2", keys[1]), ("btn1", carts[0][2]), ("btn2", carts[1][2]), ("pin", pin), ("motor", motor)):
    export_stl(p, os.path.join(ASM, n + ".stl"), tolerance=0.02, angular_tolerance=0.2)
open(os.path.join(ASM, "params.txt"), "w").write("%f %f %f %f" % (LANE, S, ZP, Y_LO))
