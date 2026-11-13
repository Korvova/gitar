# -*- coding: utf-8 -*-
r"""Проба балки с кнопками (13.11.2026) — без привода, рукой: корпус, плата-пластина с ячейками, крышка, лента, тележка, накладка.
Геометрия из ..\gitar_most_v2\most_v2.py. Корпус: крышка садится на 2 штырька (без клея, пока тест).
Пластина вместо текстолита: перегородки между кнопками, кнопки кладутся в ячейки (выводы вдоль Y), вдоль +Y канал проводов → прорезь в торце.
Лента: вокруг каждого бугорка П-прорезь — бугорок на язычке, можно печатать даже из PLA."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "gitar_most_v2")); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "most_v2"))
from build123d import *
import most_v2 as M
os.chdir(HERE); os.makedirs("stl", exist_ok=True); os.makedirs("asm", exist_ok=True)
BB, CZ, BY = M.BB, M.CZ, M.BY
YI, YW, YT, CW, CY = M.YI, M.YW, M.YT, M.CW, M.CY
Z_FL, Z_PCB, Z_BT, Z_LD0, Z_LD1, Z_RL, Z_CT = M.Z_FL, M.Z_PCB, M.Z_BT, M.Z_LD0, M.Z_LD1, M.Z_RL, M.Z_CT
PX = tuple(8.5 * (i - 2.5) for i in range(6))                              # кнопки с одинаковым шагом 8.5: ±4.25, ±12.75, ±21.25
H, XE = 25.0, 24.2                                                         # длина 50 как гриф, торцы 0.8 (крепление крышки — клей, потом придумаем)
PIN = []
Y_WC = 2.4                                                                 # канал проводов: y 2.4..3.6
# корпус (крышку пока на клей)
tray = BB(-H, H, -YW, YW, 0, Z_LD0) - BB(-XE, XE, -YI, YI, Z_FL, Z_LD0 + 1)
for x, y in PIN:
    tray += CZ(0.8, Z_LD0 - 0.01, Z_LD0 + 1.0, x, y)                       # штырёк под крышку
tray -= BB(-H - 1, -XE + 0.5, Y_WC - 0.2, YI - 0.4, Z_PCB, Z_LD0 + 1)     # прорезь проводов в торце
# пластина с ячейками
CELL = 2.75
pcb = BB(-XE + 0.15, XE - 0.15, -YI + 0.15, YI - 0.15, Z_FL, Z_PCB)
walls = BB(-XE + 0.15, XE - 0.15, -YI + 0.15, Y_WC, Z_PCB - 0.01, Z_LD0 - 0.1)
for x in PX:
    walls -= BB(x - CELL, x + CELL, -YI, YI, Z_PCB - 1, Z_LD0)
for sx in (1, -1):                                                         # за крайними ячейками оставалась стенка 0.05 — убрана
    walls -= BB(*sorted((sx * (PX[-1] + CELL - 0.01), sx * (XE + 1))), -YI, YI, Z_PCB - 1, Z_LD0)
pcb += walls
btns = Part() + [BB(x - 2.6, x + 2.6, BY - 2.6, BY + 2.6, Z_PCB, Z_BT) for x in PX]
# крышка с рельсами-хвостом
TL = 24.8                                                                  # полудлина ленты
lid = M.prof_x([(-YW, Z_LD0), (YW, Z_LD0), (YT, Z_RL), (-YT, Z_RL)], -H, H) - BB(-H - 1, H + 1, -YW + 1.0, YW - 1.0, Z_LD1 - 0.6, Z_RL + 1)
lid += BB(-H, H, -YW + 1.0, YW - 1.0, Z_LD0, Z_LD1 - 0.6)
for x in PX:
    lid -= BB(x - 2.2, x + 2.2, BY - 2.2, BY + 2.2, Z_LD0 - 1, Z_LD1 + 1)   # окно 4.4×4.4
for x, y in PIN:
    lid -= CZ(0.95, Z_LD0 - 1, Z_LD1 + 1, x, y)
for x, y in PIN:
    lid -= CZ(0.95, Z_LD0 - 1, Z_LD1 + 1, x, y)
# лента: все П в одну сторону (корень к +X)
TY = 3.6
tape = BB(-TL, TL, -TY, TY, Z_LD1 - 0.6, Z_LD1)
TP0, TP1 = -2.2, 3.5                                                       # язычок ленты: кончик / корень от центра кнопки
for x in PX:
    tp1 = min(TP1, TL - 0.9 - x)                                            # у торца ленты оставить край 0.8 (было 0.15, не печаталось)
    u = BB(x + TP0 - 0.4, x + tp1 - 0.1, -2.6, 2.6, 0, 10) - BB(x + TP0, x + tp1, -2.2, 2.2, 0, 10)
    tape -= u & BB(-40, 40, -5, 5, Z_LD1 - 0.7, Z_LD1 + 0.1)
tape += Part() + [BB(x - 2.0, x + 2.0, BY - 2.0, BY + 2.0, Z_BT, Z_LD1 - 0.59) for x in PX]
# тележка: один П-язычок того же размера и в ту же сторону, что П ленты — линии совпали = можно жать
cart = BB(-CW, CW, -CY, CY, Z_RL, Z_CT)
for s_ in (-1, 1):
    pts = [(s_ * CY, M.Z_LP), (s_ * CY, Z_RL + 0.01), (s_ * (YT + M.CL), Z_RL + 0.01), (s_ * (YW + M.CL), Z_LD0), (s_ * (YW + M.CL), M.Z_LP)]
    cart += M.prof_x(pts if s_ > 0 else pts[::-1], -CW, CW)
T_TG = 0.6
TG_R, TG_Y = 8.5, 5.0                                                      # широкий язычок под палец: корень +8.5, полуширина 5
cart -= BB(TP0 - 0.4, TG_R, -TG_Y - 0.4, TG_Y + 0.4, Z_RL - 0.01, Z_CT + 1)  # только сквозь крышу: ниже прорезь подрезала скос паза на 0.07   # перекладина П на той же линии, что у ленты
cart += BB(TP0, TG_R + 0.01, -TG_Y, TG_Y, Z_CT - T_TG, Z_CT)              # язычок 10.7×10×0.6, корень к +X
_zt, _zb = Z_CT - T_TG + 0.01, Z_LD1 + 0.2                               # нажимник на кончике язычка — пирамидкой, чтобы не закусывал (владелец 13.11)
cart += Plane(origin=(TP0 + 0.8, 0, _zt), z_dir=(0, 0, -1)) * extrude(Rectangle(1.6, 3.0), _zt - _zb, taper=22)
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
    for xc in (-22, -21.25, -12.75, -4.25, 0, 4.25, 8.5, 12.75, 21.25, 22):
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
