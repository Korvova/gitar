# -*- coding: utf-8 -*-
r"""ПЛОСКИЙ ДИСК-КУЛАЧОК — ручная проба без мотора (05.11.2026, идея владельца). Диск лежит плашмя и крутится, в верхней
грани канавка через центр; штырёк тележки идёт по канавке, тележка едет по прямой ±24. Крутить диск пальцем за рифлёный край.
Канавка: точка на расстоянии x от центра при повороте x/K — x = K·θ, θ ±75° (всего 150°), получается форма «сердечком»,
обе половины в одной половине диска. Сила с мотором 2204: 37 мН·м/А ÷ K ≈ 200 г на ампер.
Тележка — между двумя рельсами, клин 45° по бокам (как ящик в столе): штырёк короткий, стенки канавки прямые — вверх не толкает.
Детали без поддержек: disk_osnovanie (дном на стол), disk_disk (гнездом оси на стол), disk_rels ×2 (лёжа),
disk_telezhka (вверх ногами, штырёк вверх). Рельсы лежат на стойках, на клей.
Запуск: ..\.venv-b123d\Scripts\python disk_2204.py
"""
import json
import math
import os
from build123d import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "Print", "Print")

TRAVEL = 24.0
TH_M = math.radians(75.0)              # поворот диска на полный ход в одну сторону
K = TRAVEL / TH_M                      # 18.33 мм на радиан
PIN_D, G_W, G_D = 3.6, 3.9, 2.6        # штырёк, канавка: ширина, глубина
R_D = 29.0                             # диск Ø58
Z_B = 3.0                              # верх основания
Z_D0, D_T = 3.6, 7.0                   # низ диска (на воротнике), толщина
Z_D1 = Z_D0 + D_T                      # 10.6
Z_FL = Z_D1 - G_D                      # дно канавки 8.0
Z_P0, Z_P1 = Z_D1 + 0.4, Z_D1 + 3.4    # тележка и рельсы 11 … 14
Z_M = (Z_P0 + Z_P1) / 2                # середина клина
CX, CY = 10.0, 10.0                    # тележка 20 × 20
Y_R0, Y_R1 = 10.2, 15.0                # рельс
X_POST0, X_END = 30.0, 35.0            # стойки рельсов и конец рельса
Y_B = 22.0                             # основание по y — диск торчит наружу, за него и крутить


def BB(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))


def prof_x(pts, x0, x1):
    """профиль в плоскости (y, z), вытянутый вдоль x от x0 до x1"""
    return Pos(x0, 0, 0) * Rot(90, 90, 0) * extrude(make_face(Polyline(*(pts + [pts[0]]))), x1 - x0)


# ---------------- диск: канавка через центр, снизу гнездо оси с конусной крышей (без поддержек), рифлёный край ----------------
def path(t):
    return K * t * math.cos(t), K * t * math.sin(t)


N = 120
left, right = [], []
for i in range(N + 1):
    t = -TH_M + 2 * TH_M * i / N
    x, y = path(t)
    x2, y2 = path(t + 1e-4)
    tx, ty = x2 - x, y2 - y
    L = math.hypot(tx, ty)
    nx, ny = -ty / L, tx / L
    left.append((x + nx * G_W / 2, y + ny * G_W / 2))
    right.append((x - nx * G_W / 2, y - ny * G_W / 2))
poly = left + right[::-1]
gr = Pos(0, 0, Z_FL) * extrude(make_face(Polyline(*(poly + [poly[0]]))), G_D + 1.0)
for t in (-TH_M, TH_M):                                                                # концы канавки — упоры хода
    x, y = path(t)
    gr += Pos(x, y, Z_FL) * Cylinder(G_W / 2, G_D + 1.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
disk = Pos(0, 0, Z_D0) * Cylinder(R_D, D_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
disk -= gr
for k in range(36):
    a = math.radians(10.0 * k)
    disk -= Pos((R_D + 0.4) * math.cos(a), (R_D + 0.4) * math.sin(a), Z_D0 + D_T / 2) * Cylinder(1.0, D_T + 0.2)
R_H = 2.15                                                                             # гнездо оси: Ø4.3
H_ST = 1.65
disk -= Pos(0, 0, Z_D0 - 0.01) * Cylinder(R_H, H_ST + 0.01, align=(Align.CENTER, Align.CENTER, Align.MIN))
disk -= Pos(0, 0, Z_D0 + H_ST - 0.001) * Cone(R_H, 0.01, R_H, align=(Align.CENTER, Align.CENTER, Align.MIN))

# ---------------- основание: плита, воротник, ось с конусом, 4 стойки под концы рельсов ----------------
osn = BB(-X_END, X_END, -Y_B, Y_B, 0, Z_B)
osn += Pos(0, 0, Z_B - 0.01) * Cylinder(6.0, Z_D0 - Z_B + 0.01, align=(Align.CENTER, Align.CENTER, Align.MIN))
osn += Pos(0, 0, Z_D0 - 0.01) * Cylinder(2.0, 1.41, align=(Align.CENTER, Align.CENTER, Align.MIN))
osn += Pos(0, 0, Z_D0 + 1.4 - 0.01) * Cone(2.0, 0.05, 1.95, align=(Align.CENTER, Align.CENTER, Align.MIN))
for sx in (1, -1):
    for sy in (1, -1):
        x0, x1 = sorted((sx * X_POST0, sx * X_END))
        y0, y1 = sorted((sy * Y_R0, sy * (Y_R1 + 2.0)))
        osn += BB(x0, x1, y0, y1, Z_B - 0.01, Z_P0)                                    # площадка под рельс
        y2, y3 = sorted((sy * (Y_R1 + 0.2), sy * (Y_R1 + 2.0)))
        osn += BB(x0, x1, y2, y3, Z_P0 - 0.01, Z_P1)                                   # бортик снаружи рельса

# ---------------- рельс (на +Y; второй — тот же, повёрнутый на 180°): клин-паз со стороны тележки ----------------
C = 0.15
TG = 0.8                                                                               # вылет клина тележки
HW = 0.9                                                                               # полувысота клина у борта тележки
rels = BB(-X_END, X_END, Y_R0, Y_R1, Z_P0, Z_P1)
y_a, y_b = Y_R0 - 0.1, CY + TG + C
rels -= prof_x([(y_a, Z_M - (HW - (y_a - CY)) - C), (y_b, Z_M - (HW - (y_b - CY)) - C), (y_b, Z_M + (HW - (y_b - CY)) + C), (y_a, Z_M + (HW - (y_a - CY)) + C)], -X_END - 1, X_END + 1)
rels2 = Rot(0, 0, 180) * rels

# ---------------- тележка: пластина, клин по бокам, штырёк вниз прямо от пластины ----------------
ct = BB(-CX, CX, -CY, CY, Z_P0, Z_P1)
for sy in (1, -1):
    pts = [(sy * (CY - 0.01), Z_M - HW), (sy * (CY + TG), Z_M - (HW - TG)), (sy * (CY + TG), Z_M + (HW - TG)), (sy * (CY - 0.01), Z_M + HW)]
    ct += prof_x(pts, -CX, CX)
ct += Pos(0, 0, Z_FL + 0.3) * Cylinder(PIN_D / 2, Z_P0 - Z_FL - 0.3 + 0.01, align=(Align.CENTER, Align.CENTER, Align.MIN))

parts = [("disk_osnovanie", osn), ("disk_disk", disk), ("disk_rels", rels), ("disk_telezhka", ct)]
for n, p in parts:
    p = Part() + p
    bb = p.bounding_box()
    print("%s: %.1f x %.1f x %.1f, solids %d" % (n, bb.size.X, bb.size.Y, bb.size.Z, len(p.solids())))
    export_stl(p, os.path.join(OUT, n + ".stl"))
json.dump({"K": K, "TRAVEL": TRAVEL}, open(os.path.join(HERE, "disk_param.json"), "w"))

# ================= ПРОВЕРКА =================
bad = 0
def vol(a, b):
    return (Part() + (a & b)).volume
for c in (-24, -18, -11.7, -5, -1.3, 0, 2.2, 7.9, 15, 20.3, 24):
    th = math.degrees(c / K)
    d = Rot(0, 0, -th) * disk
    t = Pos(c, 0, 0) * ct
    for nm, a, b in (("штырёк × диск", t, d), ("тележка × рельс", t, rels), ("тележка × рельс2", t, rels2), ("тележка × основание", t, osn),
                     ("диск × основание", d, osn), ("диск × рельс", d, rels), ("диск × рельс2", d, rels2)):
        v = vol(a, b)
        if v > 0.01:
            bad += 1
            print("ПЕРЕСЕЧЕНИЕ %s: %.3f при c = %+.1f" % (nm, v, c))
print("рельс × основание: %.3f; рельс2 × основание: %.3f" % (vol(rels, osn), vol(rels2, osn)))
for dd in (-8, 8):
    print("диск не довёрнут на %+d° при c = 10: штырёк врезается %.2f мм³ (> 0 — штырёк в канавке)" % (dd, vol(Pos(10, 0, 0) * ct, Rot(0, 0, -math.degrees(10 / K) + dd) * disk)))
print("диск-кулачок: %s; K = %.2f мм/рад, сила ≈ %.0f г/А, высота до верха тележки %.1f мм" % ("чисто" if not bad else "ЕСТЬ ПЕРЕСЕЧЕНИЯ: %d" % bad, K, 0.037 / (K / 1000) / 9.81 * 1000, Z_P1))
