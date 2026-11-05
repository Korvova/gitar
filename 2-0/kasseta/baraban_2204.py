# -*- coding: utf-8 -*-
r"""БАРАБАННЫЙ КУЛАЧОК — проба на гимбале 2204 с Авито (05.11.2026, идея владельца): мотор неподвижен ВНУТРИ барабана,
барабан-трубка надета на крутящийся стакан мотора (на клей), на барабане винтовая V-канавка на 0.8 оборота = весь ход
48 мм. Палец тележки с конусом 90° сидит в канавке сверху; тележка ездит по рельсу-ласточкину хвосту над барабаном.
Барабан крутится — палец едет вдоль оси, тележка ±24. Концы канавки — упоры хода.
  * сила ≈ момент · 2π / шаг витка: шаг 60 мм/об → ~390 г на ампер у 2204 (37 мН·м/А); подъём витка ~29° —
    палец сам проворачивает барабан (ручной ход);
  * V-канавка и конусный палец — без люфта по оси, печать барабана стоя без поддержек (стенки канавки 45°).
Детали: bar_rama (дно + две щеки, печать дном на стол), bar_baraban (стоя, глухим торцом вниз), bar_rels (полоской
на стол), bar_telezhka (вверх ногами). Мотор: неподвижная сторона — к левой щеке, винты М2 × 3 через радиальные
прорези; правый торец барабана — на ось Ø5 правой щеки.
Запуск: ..\.venv-b123d\Scripts\python baraban_2204.py
"""
import math
import os
from build123d import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "Print", "Print")

MOT_D, MOT_L = 27.8, 12.23
BASE_L = 2.0                          # неподвижное основание мотора (стакан крутится от него до торца)
TRAVEL = 24.0
TURN = 0.8                            # витков на весь ход
LEAD = 2 * TRAVEL / TURN              # 60 мм на оборот
R_IN = MOT_D / 2 + 0.05               # барабан на стакан — плотно, на клей
WALL = 3.2
R_OUT = R_IN + WALL                   # 17.15
G_D, G_W = 1.9, 3.6                   # V-канавка: глубина, ширина по верху (стенки 45°)
X0 = -TRAVEL - 4.0                    # левый край барабана (у неподвижной стороны мотора)
X1 = TRAVEL + 4.0
D_LEN = X1 - X0                       # 56
Z_AX = 3.0 + 1.0 + R_OUT              # ось: дно 3 + зазор 1
CHEEK_T = 4.0
Y0, Y1 = -22.0, 22.0                  # рама поперёк (вдоль грифа) — проба, не кассета


def BB(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))


# ---------------- барабан: строим вдоль Z (0 … D_LEN), потом кладём осью вдоль X ----------------
drum = Cylinder(R_OUT, D_LEN, align=(Align.CENTER, Align.CENTER, Align.MIN))
drum -= Pos(0, 0, -0.1) * Cylinder(R_IN, MOT_L - BASE_L + 0.1 + 0.6, align=(Align.CENTER, Align.CENTER, Align.MIN))  # на стакан
drum -= Pos(0, 0, -0.1) * Cylinder(R_IN - 1.5, D_LEN - 2.4, align=(Align.CENTER, Align.CENTER, Align.MIN))         # пустота, торец 2.5
drum -= Cylinder(2.75, 200)                                                                         # ось Ø5 (+0.5)
# винтовая V-канавка: от z = 4 до z = D_LEN − 4 (это ход ±24), 0.8 оборота; профиль — треугольник 45°
z_g0 = -X0 - TRAVEL                                                                                 # 4
helix = Helix(pitch=LEAD, height=2 * TRAVEL, radius=R_OUT, center=(0, 0, z_g0))
p0 = helix @ 0
t0 = helix % 0
prof = Plane(origin=p0, z_dir=t0) * Polygon((-(G_W / 2 + 0.6), 0.6), ((G_W / 2 + 0.6), 0.6), (0, -G_D), align=None)
groove = sweep(prof, path=helix, is_frenet=True)
drum -= groove
# концы канавки скругляем «лункой» — палец упирается мягко
for t in (0.0, 1.0):
    pe = helix @ t
    drum -= Pos(pe.X, pe.Y, pe.Z) * Sphere(G_W / 2)

# в сборке: ось барабана — X, неподвижная сторона мотора слева (x = X0)
DR = Pos(X0, 0, Z_AX) * Rot(0, 90, 0)                                                              # z барабана → +x

# ---------------- рама: дно, левая щека (под мотор), правая щека (ось Ø5) ----------------
rama = BB(X0 - CHEEK_T - 1.0, X1 + CHEEK_T + 1.0, Y0, Y1, 0, 3.0)
XL, XR = X0 - 0.5 - BASE_L, X1 + 0.6                                                                # грани щёк
H_CH = Z_AX + R_OUT + 8.0
rama += BB(XL - CHEEK_T, XL, Y0, Y1, 2.99, H_CH)
rama += BB(XR, XR + CHEEK_T, Y0, Y1, 2.99, H_CH)
rama -= Pos(XR + CHEEK_T / 2, 0, Z_AX) * Rot(0, 90, 0) * Cylinder(2.6, CHEEK_T + 1)           # дырка Ø5.2 под ось
# ось — отдельная деталь (печать стоя): Ø5 × 9 со шляпкой Ø8 × 1.5, вставляется снаружи сквозь правую щеку в барабан
os_ = Cylinder(2.5, 9.0, align=(Align.CENTER, Align.CENTER, Align.MIN)) + Cylinder(4.0, 1.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
# левая щека: окно под центр мотора и провода вниз, радиальные прорези под винты статора (как стенд 101)
rama -= Pos(XL - CHEEK_T / 2, 0, Z_AX) * Rot(0, 90, 0) * Cylinder(5.0, CHEEK_T + 1)
rama -= BB(XL - CHEEK_T - 1, XL + 1, -6, 6, 3.0, Z_AX - 3)
for ang in (0, 90, 180, 270):
    a = math.radians(ang + 45)
    for r in [5.5 + 0.5 * k for k in range(9)]:
        rama -= Pos(XL - CHEEK_T / 2, r * math.cos(a), Z_AX + r * math.sin(a)) * Rot(0, 90, 0) * Cylinder(1.15, CHEEK_T + 1)
# гнёзда под рельс сверху щёк
Z_RL = Z_AX + R_OUT + 6.0                                                                           # низ рельса
Y_RL = 9.5                                                                          # рельс сбоку: палец — ровно над осью барабана
for xc in (XL - CHEEK_T / 2, XR + CHEEK_T / 2):
    rama -= BB(xc - CHEEK_T / 2 - 0.1, xc + CHEEK_T / 2 + 0.1, Y_RL - 2.6, Y_RL + 2.6, Z_RL - 0.01, H_CH + 1)

# ---------------- рельс: полоска 5 × 2 + гребень ласточкина хвоста (как у ползуна) ----------------
RB, RT, RH = 3.0, 4.2, 1.2
rl = BB(XL - CHEEK_T, XR + CHEEK_T, Y_RL - 2.5, Y_RL + 2.5, Z_RL, Z_RL + 2.0)
z_rb = Z_RL + 2.0
rl += Pos(XL - CHEEK_T, 0, 0) * Rot(90, 90, 0) * Pos(0, 0, 0) * extrude(make_face(Polyline(
    (Y_RL - RB / 2, z_rb - 0.01), (Y_RL + RB / 2, z_rb - 0.01), (Y_RL + RT / 2, z_rb + RH), (Y_RL - RT / 2, z_rb + RH),
    (Y_RL - RB / 2, z_rb - 0.01))), XR + CHEEK_T - (XL - CHEEK_T))

# ---------------- тележка: пластина 20 × 24, паз ласточкина хвоста под гребень, палец с конусом вниз в канавку ----------------
C_G = 0.15
Z_TOP_RIB = z_rb + RH
CT_Z0 = Z_RL - 0.0                                                                                 # низ бруска полоза
ct = BB(-10, 10, -8, Y_RL + 5.0, Z_TOP_RIB + 0.1, Z_TOP_RIB + 2.6)                                # пластина
ct += BB(-10, 10, Y_RL - 5.0, Y_RL + 5.0, z_rb + 0.1, Z_TOP_RIB + 0.11)                            # брусок полоза
ct -= Pos(-11, 0, 0) * Rot(90, 90, 0) * extrude(make_face(Polyline(
    (Y_RL - RB / 2 - C_G, z_rb + 0.09), (Y_RL + RB / 2 + C_G, z_rb + 0.09), (Y_RL + RT / 2 + C_G, Z_TOP_RIB + 0.1),
    (Y_RL - RT / 2 - C_G, Z_TOP_RIB + 0.1), (Y_RL - RB / 2 - C_G, z_rb + 0.09))), 22)
# палец: ровно над осью барабана (входит в канавку по радиусу), конус 45° = как стенки канавки, вершина на 0.25 выше дна
Y_PIN = 0.0
z_drum_top = Z_AX + math.sqrt(R_OUT ** 2 - Y_PIN ** 2)                                             # верх барабана под пальцем
ct += BB(-2, 2, Y_PIN - 2, Y_PIN + 2, z_drum_top + 1.0, Z_TOP_RIB + 0.2)
TIP = G_D - 0.25                                                                                  # вершина конуса под поверхностью
ct += Pos(0, Y_PIN, z_drum_top + 1.0) * Rot(180, 0, 0) * Cone(TIP + 1.0, 0.0, TIP + 1.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
print("барабан Ø%.1f × %.0f, ось %.1f над столом, шаг %.0f мм/об, подъём витка %.0f°, сила ≈ %.0f г/А"
      % (2 * R_OUT, D_LEN, Z_AX, LEAD, math.degrees(math.atan(LEAD / (2 * math.pi * R_OUT))), 0.037 * 2 * math.pi / (LEAD / 1000) / 9.81 * 1000))

# ---------------- РУЧНАЯ ПРОБА (05.11, владелец): без мотора, крутить ручкой — то же снаружи ----------------
HEX_AF = 5.0
drum_r = Cylinder(R_OUT, D_LEN, align=(Align.CENTER, Align.CENTER, Align.MIN)) - groove
for t in (0.0, 1.0):
    pe = helix @ t
    drum_r -= Pos(pe.X, pe.Y, pe.Z) * Sphere(G_W / 2)
drum_r -= Pos(0, 0, D_LEN - 10.0) * Cylinder(2.75, 10.1, align=(Align.CENTER, Align.CENTER, Align.MIN))       # ось Ø5 справа
drum_r -= Pos(0, 0, -0.1) * extrude(RegularPolygon((HEX_AF + 0.3) / 2 / math.cos(math.radians(30)), 6), 8.1)   # гнездо слева
rama_r = rama + BB(XL - CHEEK_T, XL, -6, 6, 3.0 - 0.01, Z_AX - 2.9)                                          # заделать окно проводов
rama_r += Pos(XL - CHEEK_T / 2, 0, Z_AX) * Rot(0, 90, 0) * (Cylinder(5.2, CHEEK_T) - Cylinder(2.7, CHEEK_T + 1))   # окно → втулка Ø5.4
# ручка: диск Ø24 × 4 с насечкой, вал Ø5 сквозь щеку и зазор 2.5, шестигранник 5 × 7 в барабан
L_SH = CHEEK_T + 0.3 + (X0 - XL)                                                                             # от наружной грани щеки до торца барабана
ruchka = Cylinder(12.0, 4.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
for k in range(16):
    a_ = math.radians(22.5 * k)
    ruchka -= Pos(12.3 * math.cos(a_), 12.3 * math.sin(a_), 2.0) * Cylinder(1.0, 4.2)
ruchka += Pos(0, 0, 4.0 - 0.01) * Cylinder(2.5, L_SH + 0.01, align=(Align.CENTER, Align.CENTER, Align.MIN))
ruchka += Pos(0, 0, 4.0 + L_SH - 0.01) * extrude(RegularPolygon(HEX_AF / 2 / math.cos(math.radians(30)), 6), 7.0)

parts = [("bar_baraban", drum), ("bar_rama", rama), ("bar_rels", rl), ("bar_telezhka", ct), ("bar_os", os_),
         ("bar_baraban_ruchnoj", drum_r), ("bar_rama_ruchnaja", rama_r), ("bar_ruchka", ruchka)]
for n, p in parts:
    p = Part() + p
    bb = p.bounding_box()
    print("%s: %.1f x %.1f x %.1f, solids %d" % (n, bb.size.X, bb.size.Y, bb.size.Z, len(p.solids())))
    export_stl(p, os.path.join(OUT, n + ".stl"))

# ================= ПРОВЕРКА: палец в канавке по всему ходу, барабан не задевает раму =================
def drum_at(rho):
    return DR * Rot(0, 0, rho) * drum


def pin_rho(c):
    """угол барабана, при котором канавка проходит под пальцем, когда тележка в c (подбор по минимуму пересечения)"""
    t = (c + TRAVEL) / (2 * TRAVEL)
    best = (9e9, 0)
    for k in range(-40, 41):
        rho = k * 9.0
        v = (Part() + (drum_at(rho) & Pos(c, 0, 0) * ct)).volume
        best = min(best, (v, rho))
    lo, hi = best[1] - 9, best[1] + 9
    for k in range(37):
        rho = lo + k * 0.5
        v = (Part() + (drum_at(rho) & Pos(c, 0, 0) * ct)).volume
        best = min(best, (v, rho))
    return best


prev = None
for c in (-24.0, -16.0, -8.0, 0.0, 8.0, 16.0, 24.0):
    v, rho = pin_rho(c)
    d = "" if prev is None else "  (Δугла на 8 мм: %.1f°)" % (rho - prev)
    prev = rho
    print("тележка %+5.1f: угол барабана %+7.1f°, пересечение пальца с барабаном %.3f мм³%s" % (c, rho, v, d))
osw = Pos(XR + CHEEK_T + 1.5, 0, Z_AX) * Rot(0, -90, 0) * os_                                       # ось в сборке
print("ось × рама: %.3f, ось × барабан: %.3f" % ((Part() + (osw & rama)).volume, (Part() + (osw & drum_at(0))).volume))
v0, r0 = pin_rho(0.0)
for dr in (-6, 6):
    print("барабан повёрнут на %+d° от нужного: палец врезается %.2f мм³ (> 0 — палец в канавке)" % (dr, (Part() + (drum_at(r0 + dr) & ct)).volume))
for nm, part in (("рама", rama), ("рельс", rl)):
    print("барабан × %s: %.3f мм³" % (nm, (Part() + (drum_at(0) & part)).volume))
print("рельс × тележка: %.3f мм³; рельс × рама (в гнёздах): %.3f" % ((Part() + (rl & ct)).volume, (Part() + (rl & rama)).volume))

# ручная проба: ручка сквозь щеку в гнездо барабана, ходом пальца — как у моторной (снаружи барабан тот же)
rk_w = Pos(XL - CHEEK_T - 4.0 - 0.3, 0, Z_AX) * Rot(0, 90, 0) * ruchka
print("ручка × рама: %.3f, ручка × барабан (шестигранник в гнезде): %.3f" %
      ((Part() + (rk_w & rama_r)).volume, (Part() + (rk_w & DR * drum_r)).volume))
v, r = pin_rho(0.0)
print("ручной барабан: палец × барабан при c = 0: %.3f" % (Part() + (DR * Rot(0, 0, r) * drum_r & ct)).volume)
