# -*- coding: utf-8 -*-
r"""Проба на 4 пальца (стол 116, идея владельца 07.11): цельная платформа на 4 тележки с шагом 30, площадки со сдвигом, шаг пальцев 24.
Тележки и детали — со стола 114 (grif_telezhka_114.py). С мотором две, без мотора две: те ездят от пальца, шестерни у них нет.
Площадка садится на те же гнёзда в крыше, что борта ложа, над головками винтов; печать площадкой на стол.
Детали две: gt4_lozhe_9 (крайние) и gt4_lozhe_3 (средние); разворот на 180° меняет знак сдвига.
Запуск: ..\.venv-b123d\Scripts\python grif_4_telezhki_116.py
"""
from grif_telezhka_114 import *

PITCH_M, PITCH_F = 30.0, 24.0
YS = [(i - 1.5) * PITCH_M for i in range(4)]            # −45, −15, 15, 45
SHIFT = [(i - 1.5) * (PITCH_F - PITCH_M) for i in range(4)]   # +9, +3, −3, −9
Y4 = YS[-1] + PY                                        # 61
T_Y = [-58.7, -28.7, 28.7, 58.7]                        # шипы вкладок: 4 штуки на вкладку
MAG_R, MAG_H, MAG_Y = 2.05, 1.9, -5.0                   # магнит Ø4 × 1.9 (замер 07.11), в дне паза, дырка насквозь, на клей; верх −1.6
MAG_X = [x + S_X for x in (-22.0, -13.2, -4.4, 4.4, 13.2)]   # под датчиком на струнах 1–5; на струне 6 датчик за краем платформы — поля нет


def teeth_cell():
    c = None
    for k in range(-10, 11):
        xc = k * PITCH
        pr = [(xc - th - DED * tn, Y_RK + DED), (xc - th + ADD_R * tn, Y_RK - ADD_R), (xc + th - ADD_R * tn, Y_RK - ADD_R), (xc + th + DED * tn, Y_RK + DED)]
        t = Pos(0, 0, Z_SLOT - 0.01) * extrude(make_face(Polyline(*(pr + [pr[0]]))), Z_RK - Z_SLOT + 0.01)
        c = t if c is None else c + t
    return c & BB(-PX, PX, -PY, PY, Z_PL0 - 1, 10)


# ---------------- платформа: плита, 4 паза, 4 рейки, 4 рельса, 4 щели, упоры x− ----------------
pl4 = BB(-PX, PX, -Y4, Y4, Z_PL0, 0)
for y0 in YS:
    pl4 -= BB(-PX - 1, PX + 1, y0 + Y_S0, y0 + Y_S1, Z_SLOT, 1)
tc = teeth_cell()
for y0 in YS:
    pl4 += Pos(0, y0, 0) * tc
    pl4 += BB(-PX, PX, y0 + Y_S1 - 0.01, y0 + 9.0, -0.01, Z_CV)
    pl4 += prof_x([(y0 + 9.0 - 0.01, -0.01), (y0 + 11.25, -0.01), (y0 + 11.25, 0.0), (y0 + 11.85, Z_R), (y0 + 9.0 - 0.01, Z_R)], -PX, PX)
    pl4 += prof_x([(y0 - 11.25, -0.01), (y0 - 9.5, -0.01), (y0 - 9.5, Z_R), (y0 - 11.85, Z_R), (y0 - 11.25, 0.0)], -PX, PX)
    pl4 -= BB(-24.2, 24.2, y0 - 1.5, y0 + 1.5, Z_PL0 - 1, 1)
    pl4 += BB(-26.0, -25.05, y0 - 9.5, y0 - 8.6, -0.01, 2.5)
for y0 in YS:
    for mx in MAG_X:
        pl4 -= CZ(MAG_R, Z_PL0 - 1, Z_SLOT + 0.5, mx, y0 + MAG_Y)                          # дырка магнита насквозь
W_H = (W_Y1 - W_Y0) / 2                                 # половина толщины столбика
for ty in T_Y:
    for sx in (1, -1):
        x0, x1 = sorted((sx * (T_X0 - 0.1), sx * (T_X1 + 0.1)))
        pl4 -= BB(x0, x1, ty - W_H - 0.1, ty + W_H + 0.1, Z_PL0 - 1, 1)

# ---------------- вкладка на всю длину (вторая — та же, разворот на 180°) ----------------
vk4 = BB(T_X0, PX, -Y4, Y4, Z_ST0, Z_ST0 + 1.5)
vk4 += BB(24.3, PX, -Y4, Y4, Z_ST0 + 1.49, Z_PL0)
for ty in T_Y:
    vk4 += BB(T_X0, T_X1, ty - W_H, ty + W_H, Z_ST0 + 1.49, -0.1)
vk4b = Rot(0, 0, 180) * vk4

# ---------------- площадка со сдвигом d: на двух стойках, штырьки в гнёзда крыши (x ±11.25, y ±5) ----------------
PAD_Y, PAD_X, PAD_T = 22.0, 24.0, 2.0
Z_PAD0 = Z_TOP + PL_T + 2.0 + 0.1                       # над головками винтов
RAIL_END = HY - 1.0


def lozhe(d):
    y0, y1 = d - PAD_Y / 2, d + PAD_Y / 2
    p = BB(-PAD_X / 2, PAD_X / 2, y0, y1, Z_PAD0, Z_PAD0 + PAD_T)
    r0, r1 = max(min(y0, -6.5), -RAIL_END), min(max(y1, 6.5), RAIL_END)
    for sx in (1, -1):
        x0, x1 = sorted((sx * 10.5, sx * 12.0))
        p += BB(x0, x1, r0, r1, Z_TOP, Z_PAD0 + PAD_T)                                 # стойка до верха площадки — печать без навеса
        for sy in (1, -1):
            p += BB(x0, x1, sy * 5.0 - 0.6, sy * 5.0 + 0.6, Z_M1 + 0.2, Z_TOP + 0.01)
    return p


lz9, lz3 = lozhe(9.0), lozhe(3.0)
PADS = [lz9, lz3, Rot(0, 0, 180) * lz3, Rot(0, 0, 180) * lz9]
for n, p in (("gt4_platforma", pl4), ("gt4_vkladka", vk4), ("gt4_lozhe_9", lz9), ("gt4_lozhe_3", lz3)):
    p = Part() + p
    bb = p.bounding_box()
    print("%s: %.1f x %.1f x %.1f, solids %d" % (n, bb.size.X, bb.size.Y, bb.size.Z, len(p.solids())))
    export_stl(p, os.path.join(OUT, n + ".stl"))

# ================= ПРОВЕРКА =================
bad4 = 0


def hit(nm, a, b, c=""):
    global bad4
    v = vol(a, b)
    if v > 0.01:
        bad4 += 1
        print("ПЕРЕСЕЧЕНИЕ %s: %.3f %s" % (nm, v, c))


print("вкладки × платформа: %.3f, %.3f" % (vol(vk4, pl4), vol(vk4b, pl4)))
print("датчик × низ %.3f, × кубик %.3f, × платформа %.3f; зазор датчик—магнит %.1f мм; x магнитов %s" % (vol(S49, ni), vol(S49, ku), vol(Pos(22, 0, 0) * S49, pl), 0.9 + 1.6, [round(x, 2) for x in MAG_X]))
for c in (-22.0, 0.0, 22.0):
    hit("датчик × платформа", Pos(c, YS[1], 0) * S49, pl4, "c = %+.0f" % c)
    hit("датчик × мотор", S49, motor)
    hit("датчик × фланец", S49, fl)
for i, y0 in enumerate(YS):
    for c in (-22.0, -7.7, 0.0, 15.2, 22.0):
        a = math.degrees(c / RP)
        cart = Pos(c, y0, 0)
        for nm, p in (("низ", ni), ("кубик", ku), ("шестерня", Rot(0, 0, a) * gear), ("фланец", Rot(0, 0, a) * fl), ("площадка", PADS[i])):
            hit("%s %d × платформа" % (nm, i + 1), cart * p, pl4, "c = %+.1f" % c)
        hit("площадка %d × своя тележка" % (i + 1), cart * PADS[i], cart * plast, "c = %+.1f" % c)
for i in range(3):                                       # соседи в разных положениях
    for c1 in (-22.0, 0.0, 22.0):
        for c2 in (-22.0, -11.0, 0.0, 11.0, 22.0):
            A, B = Pos(c1, YS[i], 0), Pos(c2, YS[i + 1], 0)
            tag_ = "тележки %d и %d, c = %+.0f, %+.0f" % (i + 1, i + 2, c1, c2)
            hit("площадка × площадка", A * PADS[i], B * PADS[i + 1], tag_)
            for nm, p in (("кубик", ku), ("низ", ni), ("пластина", plast)):
                hit("площадка × соседний " + nm, A * PADS[i], B * p, tag_)
                hit("площадка × соседний " + nm, B * PADS[i + 1], A * p, tag_)
            hit("кубик × кубик", A * ku, B * ku, tag_)
            hit("низ × низ", A * ni, B * ni, tag_)
print("проба на 4: %s; длина платформы %.0f мм; верх площадки %.1f от низа платформы; зазор между площадками %.1f мм" % (
    "чисто" if not bad4 else "ЕСТЬ ПЕРЕСЕЧЕНИЯ: %d" % bad4, 2 * Y4, Z_PAD0 + PAD_T - Z_PL0, PITCH_F - PAD_Y))
