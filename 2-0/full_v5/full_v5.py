# -*- coding: utf-8 -*-
r"""ПОЛНЫЙ МАКЕТ v5 (13.11.2026): привод телескоп v3 + мост с кнопками most_v2.
Мост-лоток стоит на стойках основания над мотором и ползуном (Y 7..29, низ на z 18.7), тележка most_v2 (П-язычок,
накладка, таблетка) ездит по стенкам лотка, а от её передней губы вниз идёт рейка — та же, что у v3, к плавающим шестерням.
Упоры хода — стойки основания (как в v3), зуб/канавка most_v2 убраны. Саморезы М2 крышки идут насквозь в стойки основания.
Запуск: ..\.venv-b123d\Scripts\python full_v5.py"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path[:0] = [os.path.join(ROOT, d) for d in ("gitar_teleskop_v3", "gitar_most_v2", "teleskop_v3", "most_v2")]   # рядом лежат папки привода и моста
from build123d import *
import teleskop_v3 as T, most_v2 as M
os.chdir(HERE)
for d in ("stl", "asm"): os.makedirs(d, exist_ok=True)
BB, CZ = T.BB, T.CZ
Y_FR = T.Y_CART + 1.2 * T.M                                               # передняя грань тележки = основание зубьев рейки
YBR, ZT = Y_FR + M.CY, T.L2[0]                                            # центр моста по Y (тележка начинается от рейки), низ лотка
G = Pos(0, YBR, ZT)
lid_l = M.lid + M.BB(-22.75, 22.75, -5.2, -4.4, M.Z_RL - 0.6, M.Z_RL)     # канавку упора заполнить (упоры — стойки)
cart_l = M.cart - M.BB(-0.75, 0.75, -5.1, -4.5, M.Z_RL - 0.6, M.Z_RL)
# --- тележка: рейка v3 снизу передней губы ---
Y_IN = YBR - M.YW - 0.2                                                   # рейка до лотка (зазор 0.2)
Z_LIP = ZT + M.Z_LP
cart = G * cart_l
cart += T.rack(-M.CW, M.CW, T.Y_CART, -1, T.L2[0], T.L2[1], Y_IN - Y_FR)
cart += BB(-M.CW, M.CW, Y_FR, Y_IN, T.L2[1] - 0.01, Z_LIP + 0.01)
# --- лоток: узкий + 2 задних уха (под ними таблетки и подушки) ---
Y_EAR = 29.0
tray = G * M.tray
for sx in (-1, 1):
    x0, x1 = sorted((sx * 12.5, sx * T.HALF))
    tray += BB(x0, x1, YBR + M.YW - 0.01, Y_EAR, ZT, ZT + 1.6)
# --- основание: стойки под уши, подушки TPU, упоры, карманы таблеток ---
base = T.base
T_PAD, CXY = 1.2, (18.0, 22.5)
PEGS = [(22.2, 13.6), (22.6, 28.2)]; STOPS = [(24.2, 12.9), (24.2, 25.0)]
pads = []
for sx in (-1, 1):
    base -= CZ(1.6, ZT, ZT + 5, sx * 22.5, T.YBP)
    x0, x1 = sorted((sx * 21, sx * T.HALF))
    base += BB(x0, x1, T.YB0, Y_EAR, 0, ZT)
    x0, x1 = sorted((sx * 20.95, sx * 25.05))
    base -= BB(x0, x1, 12.15, Y_EAR + 0.05, ZT - T_PAD, ZT + 0.01)          # стойки ниже на толщину подушки
    base -= CZ(5.5, ZT - 4, ZT + 1, sx * CXY[0], CXY[1])                   # карман под таблетку (не касается)
    pad = BB(sx * 21.0, sx * 25.0, 12.2, Y_EAR, ZT - T_PAD, ZT) - CZ(5.5, 0, 40, sx * CXY[0], CXY[1])
    for x, y in STOPS:
        base += CZ(0.8, ZT - T_PAD - 0.01, ZT - 0.3, sx * x, y)              # упор: мост проседает на 0.3 и встаёт жёстко
        pad -= CZ(1.1, 0, 40, sx * x, y)
    for x, y in PEGS:
        pad += CZ(0.75, ZT - T_PAD - 1.4, ZT + 0.7, sx * x, y)               # штырьки подушки: вниз в стойку, вверх в лоток
        base -= CZ(0.85, ZT - T_PAD - 1.5, ZT, sx * x, y)
        tray -= CZ(0.85, ZT - 1, ZT + 0.8, sx * x, y)
    pads.append(pad)
lid, tape, pcb, btns, res = (G * p for p in (lid_l, M.tape, M.pcb, M.btns, M.res))
cover = G * M.cover
coins_b = Part() + [CZ(5.0, ZT - 2.7, ZT, sx * CXY[0], CXY[1]) for sx in (-1, 1)]   # таблетки приклеены снизу к ушам лотка

sl = T.sl - BB(-T.SLX - 1, T.SLX + 1, -3, 3, T.L2[1], T.Z_ST1 + 1)            # оси шестерён вровень с шестернями, планки нет (держать будет крышка шестерён)
def pose(s):
    p = T.pose(s); p.pop("тележка"); p.pop("планка"); p["ползун"] = Pos(s, 0, 0) * sl
    p["тележка"] = Pos(2 * s, 0, 0) * cart; p["накладка"] = Pos(2 * s, 0, 0) * cover
    return p
PRINT = [("01_osnovanie", base, 0), ("02_lotok", tray, 0), ("03_kryshka_lotka", lid, 0), ("04_lenta_TPU", tape, 180),
         ("05_plastina_vmesto_platy", pcb, 0), ("06_telezhka", cart, 180), ("07_nakladka_telezhki", cover, 180), ("14_podushka_TPU_L_bokom", Rot(0, 90, 0) * pads[0], 0), ("15_podushka_TPU_P_bokom", Rot(0, 90, 0) * pads[1], 0),
         ("08_shest_motora", T.pin_m0, 0), ("09_maket_motora", T.motor, 0), ("10_polzun", sl, 0),
         ("11_shest_plav_x2", T.flo0, 0), ("13_brusok", T.beam, 0)]
if __name__ == "__main__":
    import trimesh
    def iv(a, b):
        try:
            r = a & b; return 0.0 if r is None else r.volume
        except Exception: return 0.0
    stat = {"подушка Л": pads[0], "подушка П": pads[1], "таблетки": coins_b, "основание": base, "брусок": T.beam, "мотор": T.motor, "лоток": tray, "крышка": lid, "лента": tape, "плата": pcb, "кнопки": btns}
    bad = 0
    for a in ("кнопки", "плата", "лента", "подушка Л", "подушка П", "таблетки"):
        for b in ("лоток", "крышка", "основание", "мотор"):
            if a != b and iv(stat[a], stat[b]) > 0.03: bad += 1; print("  СТАТИКА %s × %s" % (a, b))
    for s in (-T.S, -8.25, -5.5, -2.75, 0, 2.75, 5.5, 8.25, T.S):
        al = {**stat, **pose(s)}; ns = list(al)
        for i, a in enumerate(ns):
            for b in ns[i + 1:]:
                if (a in stat and b in stat) or {a, b} == {"мотор", "шест.мотора"} or {a, b} == {"тележка", "накладка"}: continue
                v = iv(al[a], al[b])
                if v > 0.03: bad += 1; print("  ПЕРЕСЕЧЕНИЕ s=%+.2f %s × %s %.2f" % (s, a, b, v))
    bb = (Part() + [base, tray, lid, cart, cover]).bounding_box()
    print("габарит %.1f × %.1f × %.1f (верх накладки %.1f, таблетки %.1f)" % (bb.size.X, bb.size.Y, bb.size.Z, ZT + M.Z_CT + M.T_CV, ZT + M.Z_CT + M.T_CV))
    print("проверка: %s" % ("ЧИСТО" if not bad else "%d проблем" % bad))
    for n, p, rot in PRINT:
        p = Rot(rot, 0, 0) * (Part() + p); b = p.bounding_box(); p = Pos(-(b.min.X + b.max.X) / 2, -(b.min.Y + b.max.Y) / 2, -b.min.Z) * p
        export_stl(p, "stl/%s.stl" % n, tolerance=0.01, angular_tolerance=0.1)
        m = trimesh.load("stl/%s.stl" % n); ov = float(m.area_faces[(m.face_normals[:, 2] < -0.72) & (m.triangles_center[:, 2] > 0.25)].sum())
        print("  %-26s %5.1f × %5.1f × %4.1f герм %s нависание %.0f мм²" % (n, b.size.X, b.size.Y, b.size.Z, m.is_watertight, ov))
    for n, p in (("base", base), ("beam", T.beam), ("motor", T.motor), ("slider", sl), ("flo", T.flo0), ("pin_m", T.pin_m0),
                 ("tray", tray), ("lid", lid), ("tape", tape), ("pcb", pcb), ("btns", btns), ("res", res), ("cart", cart), ("cover", cover), ("pads", pads[0] + pads[1]), ("coins_b", coins_b),):
        export_stl(Part() + p, "asm/%s.stl" % n, tolerance=0.02, angular_tolerance=0.2)
    print("asm ok")
