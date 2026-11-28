# -*- coding: utf-8 -*-
r"""Стенд «гусеницы» на один мотор (28.11.2026, владелец: «проверим, как вообще всё пойдёт»).
Одна вертикальная петля ремня поперёк хода, как в remni_gusenica_v5: ролики Ø10 (12 зубьев, шаг 2.66) на концах (x = ±20.6),
ведущий — на роторе GB1806 (мотор лёжа, ось вдоль y), свободный — на болте М2 в столбике. Сверху крышка-клавиша с прорезью:
качается на гибком язычке вдоль длинного края (язычок на стенке), под серединой другого длинного края — круглая кнопка Ø6 в стакане («ваза»).
Тележка: площадка 8.5 × 10, стойка через прорезь, зуб между ушками-пилами ремня, лапки под крышкой; вставляется через
расширение прорези на конце (за ходом).
Детали (PLA/PETG, сопло 0.4, кроме ремня — TPU):
  gus_osnova        — дно + стойка-кронштейн мотора (6 отверстий М2 на Ø18 под стакан, центр Ø6 под провода) + столбик свободного ролика
                       (резьба М2 Ø1.7) + стакан кнопки Ø6 (гнездо Ø6.7, прорезь выводов) + паз под стенку
  gus_klavisha      — стенка + язычок + крышка-клавиша одной деталью (печать вверх ногами, крышкой на стол)
  gus_ved_rolik     — ведущий Ø10: проставка до ротора 6.7 + 4 штыря Ø1.6 в М2 ротора (на Ø6)
  gus_svob_rolik    — свободный Ø10, отверстие Ø2.2 под болт М2
  gus_telezhka      — тележка
  gus_remen_3mm     — ремень TPU 43 зуба, ушки-пилы (и gus_remen_3mm_bez_ushek)
Крепёж: мотор — 4–6 × М2 через кронштейн в стакан (длиннее штатных на 3, как на стенде 21.22); свободный ролик — М2 × 10 (не дотягивать).
Запуск: ..\..\..\2-0\.venv-b123d\Scripts\python stend_gus.py
"""
import math, os
from build123d import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "stl"); os.makedirs(OUT, exist_ok=True)
for _f in os.listdir(OUT):
    if _f.endswith(".stl"): os.remove(os.path.join(OUT, _f))

# --- ремень и ролики (профиль как remen_04: зуб 0.9 × 0.7, спинка 0.9, пазы прямоугольные) ---
P = 2.659                                    # шаг на роликах
N = 43                                       # зубьев ремня
NP = 12                                      # зубьев ролика
R_D = NP * P / (2 * math.pi)                 # Ø10.16
LOOP = N * P
X_R = (LOOP - 2 * math.pi * R_D) / 4         # оси роликов ±20.6
L = LOOP * (1 - 0.005); R_ROOT = L / (2 * math.pi)
H, WT, TB = 0.7, 0.9, 0.9
CLR, CLR_DNO = 0.10, 0.02
T_FL = 0.6; R_FL = R_D + TB + 0.3
W = 3.0                                      # ремень 3 мм
T_W, G_T, LL, HP = 1.5, 0.10, 3.0, 1.5       # зуб тележки, зазор, ушко-пила


def BB(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))


def CY(r, y0, y1, x, z):                     # цилиндр с осью вдоль y
    return Pos(x, y0, z) * Rot(-90, 0, 0) * Cylinder(r, y1 - y0, align=(Align.CENTER, Align.CENTER, Align.MIN))


def CZ(r, z0, z1, x=0.0, y=0.0):
    return Pos(x, y, z0) * Cylinder(r, z1 - z0, align=(Align.CENTER, Align.CENTER, Align.MIN))


def ring_teeth(r, n, pts, height, z0=0.0):
    out = []
    for k in range(n):
        a = 2 * math.pi * k / n; c, s = math.cos(a), math.sin(a)
        q = [((r - nn) * c - t * s, (r - nn) * s + t * c) for t, nn in pts]
        out.append(Pos(0, 0, z0) * extrude(make_face(Polyline(*(q + [q[0]]))), height))
    return out


def pulley(w, bore=None):                    # ось по z, низ нижней юбки на z = 0
    hub = w + 0.4
    p = Cylinder(R_D, hub, align=(Align.CENTER, Align.CENTER, Align.MIN))
    g, d = WT / 2 + CLR, H + CLR_DNO
    p -= Part() + ring_teeth(R_D, NP, [(-g, -0.3), (-g, d), (g, d), (g, -0.3)], hub + 2, -1)
    p += Pos(0, 0, -T_FL) * Cylinder(R_FL, T_FL, align=(Align.CENTER, Align.CENTER, Align.MIN))
    p += Pos(0, 0, hub) * Cylinder(R_FL, T_FL, align=(Align.CENTER, Align.CENTER, Align.MIN))
    if bore: p -= Cylinder(bore, 100)
    return Pos(0, 0, T_FL) * p


def belt_ring(w, ushki=True):
    u, c = WT / 2, 0.1
    tooth = [(-u, -0.05), (-u, H - c), (-u + c, H), (u - c, H), (u, H - c), (u, -0.05)]
    ring = Cylinder(R_ROOT + TB, w, align=(Align.CENTER, Align.CENTER, Align.MIN)) - Pos(0, 0, -1) * Cylinder(R_ROOT, w + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    b = ring + Part() + ring_teeth(R_ROOT, N, tooth, w)
    if ushki:
        rb = R_ROOT + TB
        for sd in (-1, 1):
            g0 = T_W / 2 + G_T + 0.1          # зазор зуб–ушко 0.2 (сопло 0.4)
            pts = [(g0, -0.1), (g0, HP), (g0 + LL, 0.5), (g0 + LL, -0.1)]   # конец ската — ступенька 0.5 (печатается)
            q = [((rb + n) * math.cos(math.pi / 2 + sd * t / rb), (rb + n) * math.sin(math.pi / 2 + sd * t / rb)) for t, n in pts]
            if sd < 0: q = q[::-1]
            b += extrude(make_face(Polyline(*(q + [q[0]]))), w)
    return b


# --- стенд: петля в плоскости x-z на y = 0 (ремень y ±1.5), мотор со стороны −y ---
T_B = 2.5                                    # дно
R_M, L_ROT, L_CAP = 11.0, 13.0, 7.5          # GB1806: ротор-корпус 13 (крутится!), стакан 7.5 (неподвижен)
Z_M = T_B + R_M + 0.5                        # ось мотора и роликов 14.0
Y_ROT = -9.0                                 # торец ротора (проставка ведущего 6.7)
Y_CAP0 = Y_ROT - L_ROT; Y_CAP1 = Y_CAP0 - L_CAP          # стакан −22 … −29.5
T_BR = 2.5                                   # кронштейн мотора
Z_TOP = Z_M + R_D; Z_BACK = Z_TOP + TB       # верхняя ветвь
Z_PL0 = Z_BACK + HP + 0.22; Z_PL1 = Z_PL0 + 1.2          # крышка-клавиша
Z_C0 = Z_PL1 + 0.2; Z_C1 = Z_C0 + 1.2        # площадка тележки
SLOT = 0.9                                   # прорезь ±0.9
PW0 = -8.4                                   # свободный край крышки (кнопка под ним)
HG0, HG1 = 3.6, 5.0                          # язычок
WL0, WL1 = 5.0, 5.8                          # стенка
XP = 25.7                                    # крышка по x
X_KEY0, X_KEY1, KEY_W = 23.0, 25.0, 2.2      # расширение прорези для лапок (за ходом ±21)
BTN_D, BTN_H, BTN_HP = 6.4, 3.5, 1.5          # 28.11 (владелец): круглая кнопка Ø6 в стакане («ваза», как в модулях 19.x): корпус Ø6.4 × 3.5, шток 1.5
R_SOCK, CUP_W = 3.35, 0.8                      # гнездо Ø6.7, стенка стакана
Y_BTN = -6.0                                  # центр кнопки: стакан не задевает ремень и ушки (до y = −1.5 зазор 0.35)
FREE_POST = (-X_R, -6.6, -2.6)               # столбик свободного ролика: x, y0, y1


def osnova():
    b = BB(-28.0, 34.5, Y_CAP1 - T_BR, 8.0, 0, T_B)
    br = BB(X_R - 13.5, X_R + 13.5, Y_CAP1 - T_BR, Y_CAP1, 0, Z_M + 12.0)           # кронштейн за стаканом
    for a in range(0, 360, 60):
        x, z = X_R + 9 * math.cos(math.radians(a + 30)), Z_M + 9 * math.sin(math.radians(a + 30))
        br -= CY(1.1, Y_CAP1 - T_BR - 1, Y_CAP1 + 1, x, z) + CY(2.0, Y_CAP1 - T_BR - 1, Y_CAP1 - T_BR + 1.2, x, z)
    br -= CY(3.0, Y_CAP1 - T_BR - 1, Y_CAP1 + 1, X_R, Z_M)                           # провода стакана
    b += br
    for xg in (X_R - 13.5, X_R + 13.5 - 2.0):                                          # косынки за кронштейном
        b += BB(xg, xg + 2.0, Y_CAP1 - T_BR - 5.0, Y_CAP1 - T_BR + 0.01, T_B - 0.01, T_B + 6.0)
    x, y0, y1 = FREE_POST
    post = BB(x - 2.5, x + 2.5, y0, y1, T_B - 0.01, Z_M + 3.0)
    post -= CY(0.85, y0 - 1, y1 + 1, x, Z_M)                                           # М2 как саморез
    b += post
    z_body = Z_PL0 - 0.05 - BTN_HP                                                     # верх корпуса кнопки (шток касается низа крышки)
    z_floor = z_body - BTN_H                                                           # дно стакана
    b += CZ(R_SOCK + CUP_W, T_B - 0.01, z_body, 0, Y_BTN)                              # «ваза»: столбик-стакан
    b -= CZ(R_SOCK, z_floor, z_body + 1, 0, Y_BTN)                                     # гнездо Ø6.7
    b -= BB(-0.6, 0.6, Y_BTN - R_SOCK - CUP_W - 1, Y_BTN + R_SOCK + CUP_W + 1, z_floor - 2.0, z_body + 1)   # прорезь выводов (насквозь поперёк, вниз на 2)
    b -= BB(-27.2, 27.2, WL0 - 0.05, WL1 + 0.05, 1.0, T_B + 1)                         # паз под стенку
    return b


def klavisha():
    k = BB(-27.0, 27.0, WL0, WL1, 1.0, Z_PL1)                                          # стенка (низ в пазу дна)
    k += BB(-XP, XP, PW0, HG0, Z_PL0, Z_PL1)                                           # крышка
    k += BB(-XP, XP, HG0 - 0.01, WL0 + 0.01, Z_PL1 - 0.5, Z_PL1)                       # язычок 0.5
    k -= BB(-24.2, X_KEY1, -SLOT, SLOT, Z_PL0 - 1, Z_PL1 + 1)                          # прорезь
    k -= BB(X_KEY0, X_KEY1, -KEY_W, KEY_W, Z_PL0 - 1, Z_PL1 + 1)                       # расширение — вставить тележку
    return k


def ved_rolik():
    p = Pos(X_R, 0, Z_M) * Rot(90, 0, 0) * Pos(0, 0, -(T_FL * 2 + W + 0.4) / 2) * pulley(W)   # ролик по оси y, центр на y = 0
    p += CY(4.0, Y_ROT, -(W + 0.4) / 2 - T_FL + 0.01, X_R, Z_M)                        # проставка до ротора
    for a in (0, 90, 180, 270):
        p += CY(0.8, Y_ROT - 1.5, Y_ROT + 0.01, X_R + 3 * math.cos(math.radians(a)), Z_M + 3 * math.sin(math.radians(a)))
    return p


def svob_rolik():
    return Pos(-X_R, 0, Z_M) * Rot(90, 0, 0) * Pos(0, 0, -(T_FL * 2 + W + 0.4) / 2) * pulley(W, 1.1)


def telezhka(xc=0.0):
    t = BB(xc - 4.25, xc + 4.25, -5.0, 5.0, Z_C0, Z_C1)                                # площадка
    t += BB(xc - T_W / 2, xc + T_W / 2, -0.7, 0.7, Z_PL0 - 0.1, Z_C0 + 0.01)           # стойка в прорези
    t += BB(xc - T_W / 2, xc + T_W / 2, -1.9, 1.9, Z_PL0 - 0.45, Z_PL0 - 0.1)          # лапки
    t += BB(xc - T_W / 2, xc + T_W / 2, -W / 2, W / 2, Z_BACK + 0.1, Z_PL0 - 0.44)     # зуб между ушками
    return t


def belt_loop(xc=0.0):
    """ремень на роликах для проверки: петля (спинка) + ушки-пилы на верхней ветви у тележки xc"""
    def stadium(r):
        return BB(-X_R, X_R, -W / 2, W / 2, Z_M - r, Z_M + r) + CY(r, -W / 2, W / 2, -X_R, Z_M) + CY(r, -W / 2, W / 2, X_R, Z_M)
    b = stadium(R_D + TB) - stadium(R_D)
    for sd in (-1, 1):
        g0 = T_W / 2 + G_T + 0.1
        x0, x1 = xc + sd * g0, xc + sd * (g0 + LL)
        if abs(x1) > X_R: x1 = sd * X_R                                                # на ролике ушко гнётся — проверяем прямой кусок
        if (x1 - x0) * sd > 0.2:
            b += BB(*sorted((x0, x1)), -W / 2, W / 2, Z_BACK - 0.01, Z_BACK + HP)
    return b


if __name__ == "__main__":
    import trimesh
    mot = CY(R_M, Y_CAP1, Y_ROT, X_R, Z_M)
    stat = {"основа": osnova(), "клавиша": klavisha(), "мотор": mot, "свободный": svob_rolik()}
    rot = {"ведущий": ved_rolik()}
    bad = 0
    def iv(a, b):
        try:
            r = a & b; return 0.0 if r is None else r.volume
        except Exception:
            return 0.0
    allp = {**stat, **rot}
    ok_pairs = [{"основа", "клавиша"}, {"основа", "мотор"}, {"мотор", "ведущий"}]
    names = list(allp)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            if {names[i], names[j]} in ok_pairs: continue
            v = iv(allp[names[i]], allp[names[j]])
            if v > 0.01: bad += 1; print("  %s × %s %.3f" % (names[i], names[j], v))
    for xc in (-21, -15, -8, 0, 8, 15, 21):
        t, bl = telezhka(xc), belt_loop(xc)
        for n, q in allp.items():
            for nm, part in (("тележка", t), ("ремень", bl)):
                if nm == "ремень" and n in ("ведущий", "свободный"): continue
                v = iv(part, q)
                if v > 0.01: bad += 1; print("  x=%+d %s × %s %.3f" % (xc, nm, n, v))
        if iv(t, bl) > 0.01: bad += 1; print("  x=%+d тележка × ремень/ушки %.3f" % (xc, iv(t, bl)))
    t0 = telezhka(0)
    if iv(Pos(0, 0, 0.3) * t0, klavisha()) < 0.01: bad += 1; print("  тележка поднимается выше 0.3 — лапки не держат")
    print("СТЕНД ГУСЕНИЦЫ: %s | ролики Ø%.2f на ±%.2f, ремень %d зубьев (длина %.2f, кольцо Ø%.1f); ось мотора %.1f; верх площадки %.1f" % (
        "ЧИСТО" if not bad else "%d проблем" % bad, 2 * R_D, X_R, N, L, 2 * (R_ROOT + TB), Z_M, Z_C1))
    print("  крышка: низ %.2f, шток кнопки Ø6 — верх %.2f; стакан Ø%.1f до y = %.2f (ремень с −1.5)" % (Z_PL0, Z_PL0 - 0.05, 2 * (R_SOCK + CUP_W), Y_BTN + R_SOCK + CUP_W))
    parts = {"gus_osnova": (osnova(), (0, 0, 0)), "gus_klavisha": (klavisha(), (180, 0, 0)),
             "gus_ved_rolik": (ved_rolik(), (-90, 0, 0)), "gus_svob_rolik": (svob_rolik(), (-90, 0, 0)),   # наружной юбкой на стол, штыри вверх
             "gus_telezhka": (telezhka(), (180, 0, 0)), "gus_remen_3mm": (belt_ring(W), (0, 0, 0)), "gus_remen_3mm_bez_ushek": (belt_ring(W, False), (0, 0, 0))}
    for n, (p, r) in parts.items():
        q = Rot(*r) * p; bb = q.bounding_box(); q = Pos(-(bb.min.X + bb.max.X) / 2, -(bb.min.Y + bb.max.Y) / 2, -bb.min.Z) * q
        f = os.path.join(OUT, n + ".stl"); export_stl(q, f, tolerance=0.004, angular_tolerance=0.05)
        m = trimesh.load(f); print("  %-26s %5.1f × %5.1f × %4.1f герм %s" % (n, *m.extents, m.is_watertight))
    A = os.path.join(HERE, "asm"); os.makedirs(A, exist_ok=True)
    for n, p in (("osnova", osnova()), ("klavisha", klavisha()), ("motor", mot), ("ved", ved_rolik()), ("svob", svob_rolik()), ("tel", telezhka(0)), ("remen", belt_loop(0))):
        export_stl(p, os.path.join(A, n + ".stl"), tolerance=0.01, angular_tolerance=0.1)
    print("готово")
