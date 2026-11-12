# -*- coding: utf-8 -*-
"""Проба мост-кассеты с кнопками, из двух частей (12.11.2026, вики 19.50). Лежит на столе, сверху ездит тележка v4 (рукой).
ЛОТОК (снизу): пол 0.6, гнездо пластины/платы 1.5, сзади канал 3.6 под выводные резисторы Ø2.2 и провода.
КРЫШКА (сверху, трапеция под тележку): гнёзда кнопок SMD 5.2×5.2×1.5, окна с крышками кнопок на буртиках, скосы по ходу.
Сборка: пластина в лоток → кнопки → крышки кнопок в окна крышки → крышку на лоток, штырьки Ø1.6 на плотную посадку."""
import os
from build123d import *
os.chdir(os.path.dirname(os.path.abspath(__file__))); os.makedirs("kaseta_stl", exist_ok=True)
HALF, Z_TOP, Z_SPL = 25.0, 21.2, 18.7                  # верх моста v4; разъём лоток/крышка = низ губ тележки
YB0, YBB1, DT = 12.1, 24.6, 1.0                        # крышка накрывает лоток целиком; тележка под эту ширину (teleskop_v4.py, YBB1)
PKX = (-21.4, -13.2, -4.4, 4.4, 13.2, 21.4); PKY = 17.0
Z0, ZF = 16.6, 17.2                                    # низ лотка, пол
ZB1, ZC1 = Z_SPL + 1.5, Z_SPL + 1.8                    # верх кнопки 20.2, низ верхней стенки 20.5 (буртик крышки 20.2..20.5)
PY0, PY1 = 13.4, 20.0                                  # гнездо пластины
RY0, RY1 = 20.0, 23.6                                  # канал резисторов/проводов
PEGS = [(x, 12.75) for x in (-20.0, -9.0, 9.0, 20.0)]
def BB(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))
def CZ(r, z0, z1, x, y):
    return Pos(x, y, z0) * Cylinder(r, z1 - z0, align=(Align.CENTER, Align.CENTER, Align.MIN))
def prof_x(pts, x0, x1):
    return Pos(x0, 0, 0) * Rot(90, 90, 0) * extrude(make_face(Polyline(*(pts + [pts[0]]))), x1 - x0, dir=(0, 0, 1))
# лоток
tray = BB(-HALF, HALF, YB0, 24.6, Z0 - 0.9, Z_SPL)                                   # дно ровное по всей ширине
tray -= BB(-HALF + 0.4, HALF - 0.4, PY0, PY1, ZF, Z_SPL + 1)                           # гнездо пластины/платы
tray -= BB(-HALF - 1, HALF + 1, RY0, RY1, Z0 - 0.6, Z_SPL + 1)                        # канал резисторов, сверху закрыт крышкой, выход на торцы
for x, y in PEGS:
    tray += CZ(0.6, Z_SPL - 0.01, Z_SPL + 1.2, x, y)
# крышка
lid = prof_x([(YB0, Z_SPL), (YBB1, Z_SPL), (YBB1 + DT, Z_TOP), (YB0 - DT, Z_TOP)], -HALF, HALF)
for px in PKX:
    lid -= BB(px - 2.8, px + 2.8, PKY - 2.8, PKY + 2.8, Z_SPL - 1, ZC1)                # кнопка + буртик крышки
    lid -= BB(px - 3.4, px + 3.4, PKY - 2.3, PKY + 2.3, Z_SPL - 1, Z_SPL + 0.5)        # выводы кнопки
    lid -= BB(px - 2.5, px + 2.5, PKY - 2.5, PKY + 2.5, ZC1 - 0.01, Z_TOP + 1)         # окно
    for sx in (-1, 1):
        xw = px + sx * 2.5
        tri = [(xw, Z_TOP + 0.01), (xw, Z_TOP - 0.3), (xw + sx * 0.8, Z_TOP + 0.01)]
        lid -= Pos(0, PKY + 2.5, 0) * Rot(90, 0, 0) * extrude(make_face(Polyline(*(tri + [tri[0]]))), 5.0)
lid -= BB(-HALF - 1, HALF + 1, RY0 - 0.25, RY1, Z_SPL - 1, ZB1)                     # канал резисторов: верхняя часть, к выводам кнопок
for x, y in PEGS:
    lid -= CZ(0.63, Z_SPL - 1, Z_SPL + 1.4, x, y)
cap = BB(-2.75, 2.75, -2.75, 2.75, 0, 0.3) + BB(-2.45, 2.45, -2.45, 2.45, 0.29, 0.3 + Z_TOP - ZC1)
plate = BB(-HALF + 0.5, HALF - 0.5, PY0 + 0.1, PY1 - 0.1, 0, 1.5)
btns = Part() + [BB(px - 2.6, px + 2.6, PKY - 2.6, PKY + 2.6, Z_SPL, ZB1) for px in PKX]
asm = {"tray": tray, "lid": lid, "caps": Part() + [Pos(px, PKY, ZB1) * cap for px in PKX], "plate": Pos(0, 0, ZF) * plate, "btns": btns}
for n, p in asm.items():
    export_stl(Part() + p, "kaseta_stl/asm_%s.stl" % n, tolerance=0.02, angular_tolerance=0.2)
for f in os.listdir("kaseta_stl"):
    if f[:2] in ("01", "02", "03") and not f.startswith(("01_kryshka_kasety", "02_lotok", "03_kryshka")):
        os.remove(os.path.join("kaseta_stl", f))
import trimesh
for n, p, rot in (("01_kryshka_kasety", lid, 180), ("02_lotok", tray, 0), ("03_kryshka_knopki_x6", cap, 0), ("04_plastina_vmesto_platy", plate, 0)):
    p = Rot(rot, 0, 0) * (Part() + p); bb = p.bounding_box(); p = Pos(-(bb.min.X + bb.max.X) / 2, -(bb.min.Y + bb.max.Y) / 2, -bb.min.Z) * p
    export_stl(p, "kaseta_stl/%s.stl" % n, tolerance=0.01, angular_tolerance=0.1)
    m = trimesh.load("kaseta_stl/%s.stl" % n); ov = float(m.area_faces[(m.face_normals[:, 2] < -0.72) & (m.triangles_center[:, 2] > 0.25)].sum())
    print(n, [round(v, 1) for v in (bb.size.X, bb.size.Y, bb.size.Z)], "герм", m.is_watertight, "нависание %.0f мм²" % ov)
print("ok")
