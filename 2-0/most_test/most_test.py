# -*- coding: utf-8 -*-
r"""Проба балки с кнопками (13.11.2026) — без привода, рукой: корпус, плата-пластина с ячейками, крышка, лента, тележка, накладка.
Геометрия из ..\gitar_most_v2\most_v2.py. Корпус: крышка садится на 2 штырька (без клея, пока тест).
Пластина вместо текстолита: перегородки между кнопками, кнопки кладутся в ячейки (выводы вдоль Y), вдоль +Y канал проводов → прорезь в торце.
Лента: вокруг каждого бугорка П-прорезь — бугорок на язычке, можно печатать даже из PLA."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "gitar_most_v2"))
from build123d import *
import most_v2 as M
os.chdir(HERE); os.makedirs("stl", exist_ok=True); os.makedirs("asm", exist_ok=True)
BB, CZ, PX, BY = M.BB, M.CZ, M.PX, M.BY
H, XE, YI, YW = M.H, M.XE, M.YI, M.YW
Z_FL, Z_PCB, Z_BT, Z_LD0, Z_LD1 = M.Z_FL, M.Z_PCB, M.Z_BT, M.Z_LD0, M.Z_LD1
PIN = [(-23.7, 0.0), (23.7, 0.0)]
Y_WC = 2.4                                                                 # канал проводов: y 2.4..3.6
# корпус
tray = BB(-H, H, -YW, YW, 0, Z_LD0) - BB(-XE, XE, -YI, YI, Z_FL, Z_LD0 + 1)
for x, y in PIN:
    tray += CZ(0.8, Z_LD0 - 0.01, Z_LD0 + 1.0, x, y)                       # штырёк под крышку
tray -= BB(-H - 1, -XE + 0.5, Y_WC - 0.2, YI - 0.4, Z_PCB, Z_LD0 + 1)     # прорезь проводов в торце (над пластиной)
# пластина с ячейками
CELL = 2.75                                                                # полуразмер ячейки (кнопка 5.2 + 0.3)
pcb = BB(-XE + 0.15, XE - 0.15, -YI + 0.15, YI - 0.15, Z_FL, Z_PCB)
walls = BB(-XE + 0.15, XE - 0.15, -YI + 0.15, Y_WC, Z_PCB - 0.01, Z_LD0 - 0.1)
for x in PX:
    walls -= BB(x - CELL, x + CELL, -YI, YI, Z_PCB - 1, Z_LD0)
pcb += walls
btns = Part() + [BB(x - 2.6, x + 2.6, BY - 2.6, BY + 2.6, Z_PCB, Z_BT) for x in PX]
# крышка: шире выемка под ленту, отверстия под штырьки (у M.lid уже Ø1.9)
TY = 3.6
lid = M.lid + BB(-22.75, 22.75, -5.2, -4.4, M.Z_RL - 0.6, M.Z_RL)        # без канавки упора (в тесте не нужна)
lid -= BB(-22.6, 22.6, -YW + 1.0, YW - 1.0, Z_LD1 - 0.6, Z_LD1 + 1)      # выемка до самых рельсов — без щели-овражка
# лента с П-прорезями
tape = BB(-22.5, 22.5, -TY, TY, Z_LD1 - 0.6, Z_LD1)
for x in PX:
    if abs(x) > 19:                                                        # крайние: корень к торцу ленты, рамка замкнута (не рвётся)
        d = 1 if x > 0 else -1
        xa, xb = sorted((x - d * 2.6, x + d * 2.4)); xi = sorted((x - d * 2.2, x + d * 2.5))
    else:                                                                  # средние: корень к середине ленты
        sx = 1 if x < 0 else -1
        xa, xb = sorted((x - sx * 2.6, x + sx * 3.4)); xi = sorted((x - sx * 2.2, x + sx * 3.5))
    u = BB(xa, xb, -2.6, 2.6, 0, 10) - BB(*xi, -2.2, 2.2, 0, 10)
    tape -= u & BB(-30, 30, -5, 5, Z_LD1 - 0.7, Z_LD1 + 0.1)
tape += Part() + [BB(x - 2.0, x + 2.0, BY - 2.0, BY + 2.0, Z_BT, Z_LD1 - 0.59) for x in PX]
cart, cover = M.cart - BB(-0.75, 0.75, -5.1, -4.5, M.Z_RL - 0.6, M.Z_RL), None   # без зуба упора, без накладки (тест)
for x, y in M.PEG:
    cart += CZ(0.66, M.Z_CT - 1.01, M.Z_CT, x, y)                         # гнёзда штырьков накладки заделать
PRINT = [("01_korpus", tray, 0), ("02_plastina_jachejki", pcb, 0), ("03_kryshka", lid, 0), ("04_lenta_PLA_ili_TPU", tape, 180),
         ("05_telezhka", cart, 180)]
if __name__ == "__main__":
    import trimesh
    def iv(a, b):
        try:
            r = a & b; return 0.0 if r is None else r.volume
        except Exception: return 0.0
    P = {"корпус": tray, "пластина": pcb, "кнопки": btns, "крышка": lid, "лента": tape}
    bad = 0; ns = list(P)
    for i, a in enumerate(ns):
        for b in ns[i + 1:]:
            v = iv(P[a], P[b])
            if v > 0.02: bad += 1; print("  ПЕРЕСЕЧЕНИЕ %s × %s %.2f" % (a, b, v))
    for xc in (-22, -13.2, -4.4, 0, 4.4, 8.8, 13.2, 19.5, 22):
        for a, A in (("тележка", cart),):
            for b in ns:
                v = iv(Pos(xc, 0, 0) * A, P[b])
                if v > 0.02: bad += 1; print("  ХОД x=%+.1f %s × %s %.2f" % (xc, a, b, v))
    print("проверка: %s" % ("ЧИСТО" if not bad else "%d проблем" % bad))
    for n, p, rot in PRINT:
        p = Rot(rot, 0, 0) * (Part() + p); b = p.bounding_box(); p = Pos(-(b.min.X + b.max.X) / 2, -(b.min.Y + b.max.Y) / 2, -b.min.Z) * p
        export_stl(p, "stl/%s.stl" % n, tolerance=0.01, angular_tolerance=0.1)
        m = trimesh.load("stl/%s.stl" % n); ov = float(m.area_faces[(m.face_normals[:, 2] < -0.72) & (m.triangles_center[:, 2] > 0.25)].sum())
        print("  %-24s %5.1f × %5.1f × %4.1f герм %s нависание %.0f мм²" % (n, b.size.X, b.size.Y, b.size.Z, m.is_watertight, ov))
    for n, p in P.items():
        export_stl(Part() + p, "asm/%s.stl" % n, tolerance=0.02, angular_tolerance=0.2)
    export_stl(Pos(4.4, 0, 0) * cart, "asm/тележка.stl")
