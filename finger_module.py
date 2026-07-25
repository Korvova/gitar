# -*- coding: utf-8 -*-
"""
Мини-прототип "одна струна" v6: SG90 ЛЁЖА НА БОКУ + РЕЙКА-ШЕСТЕРНЯ (инсайт юзера).

SG90 лежит на боку в кармане грифа (высота лёжа всего ~12 мм), вал горизонтально
вдоль грифа, смотрит на поперечный паз. На валу шестерня m1 z12 (прессуется на
шлицы + винт M2). У тележки снизу крыло-РЕЙКА: шестерня катит рейку ->
тележка ездит влево-вправо поперёк грифа. Ход ~17 мм.
Для 4 пальцев: два серво в карманах сверху грифа, два снизу, в шахматном порядке.

Детали:
  base_v6.stl     - подставка: плита + 2 седла
  neck_v6.stl     - гриф 44x22x156: лежачий карман SG90 + паз + канал крыла + лады
  carriage_v6.stl - тележка с кольцом и крылом-рейкой (печать на боку)
  pinion_v6.stl   - шестерня m1 z12, бора Ø4.6 на шлицы SG90, ступень под винт M2

Координаты грифа: низ z=0, накладка z=22. Паз x=-190. Вал SG90: (-179 торец, y=0, z=16.6).
"""
from build123d import *
import math

OUT = r"C:\app\Esp-gitar"

# ---------------- параметры ----------------
# SG90 лёжа: длина 22.5 (X) + вал, ширина 23 с ушками вдоль Y, высота 12.2
SG_SHAFT_OFF = 5.9                 # вал смещён вдоль длинной оси (Y)
POCKET_FLOOR = 10.5                # пол кармана: ось вала z = 10.5 + 6.1 = 16.6
AXIS_Z = POCKET_FLOOR + 6.1
X_SHAFT_FACE = -179.0              # торец корпуса со стороны вала

# шестерня m1 z12: делит. радиус 6, вершины 6.8, впадины 4.75
PIN_TEETH, PIN_RP, PIN_RT, PIN_RR = 12, 6.0, 6.8, 4.75

# рейка: шаг pi, делит. линия = AXIS_Z - 6 = 10.6
RACK_P = math.pi
RACK_ROOT, RACK_TIP = 9.6, 11.4    # плато корней / вершины зубьев

# гриф
NECK_W, NECK_H = 44.0, 22.0
X_FACE, X_END = -42.0, -198.0
XSLOT = -190.0
NECK_SEAT = 10.0

# ---------------- база (как v5) ----------------
plate = Pos(-112.5, 0, -2) * Box(115, 60, 4)
SADDLES = (-75.0, -150.0)
SAD_TOP = NECK_SEAT + 7.4
base = plate
for xc in SADDLES:
    base += Pos(xc, 0, SAD_TOP / 2) * Box(30, 52, SAD_TOP)
for xc in SADDLES:
    base -= Pos(xc, 0, NECK_SEAT + 4.2) * Box(20.6, 44.6, 8.4)
    for sy in (-1, 1):
        base -= Pos(xc, sy * 24, NECK_SEAT + 3.5) * Rot(X=90) * Cylinder(1.4, 5)

# ---------------- гриф ----------------
neck = Pos((X_FACE + X_END) / 2, 0, NECK_H / 2) * Box(X_FACE - X_END, NECK_W, NECK_H)
frets = [Pos(xf, 0, NECK_H + 0.4) * Box(1.6, NECK_W, 0.8) for xf in (-70, -95, -120, -145)]

slot = Pos(XSLOT, 0, 15.6) * Box(8, 36, 15.2)                       # паз тележки, пол z=8
wing_ch = Pos(-182.3, 0, 10.3) * Box(7.4, 42, 4.6)                  # канал крыла-рейки z 8..12.6
pin_cav = Pos(-182.3, 0, 17.55) * Box(7.4, 16, 10.1)                # полость шестерни, открыта сверху
pocket = Pos(X_SHAFT_FACE + 11.4, -SG_SHAFT_OFF, 16.5) * Box(22.8, 23.8, 12.2)  # пол 10.4
tab_slits = Pos(-174.2, -SG_SHAFT_OFF, 16.5) * Box(2.8, 33.6, 12.2) # щели под ушки фланца
wire_groove = Pos(-158.5, 13.5, 13) * Box(6, 17, 5)                 # провода к боку +Y

dimples = [Pos(xc, sy * 19, 3.7) * Rot(X=90) * Cylinder(1.25, 7)
           for xc in SADDLES for sy in (-1, 1)]

neck_part = neck
for f in frets:
    neck_part += f
for c in [slot, wing_ch, pin_cav, pocket, tab_slits, wire_groove] + dimples:
    neck_part -= c

# ---------------- тележка: корпус + стойка + кольцо + крыло-рейка (печать на боку) ----------------
# печатные оси: x_p = поперёк грифа (Y), y_p = высота (Z-8), z_p = вдоль грифа (X+193.7)
carriage = Pos(0, 6, 3.7) * Box(12, 12, 7.4)                        # корпус: z 8..20
carriage += Pos(0, 16.5, 1.5) * Box(4, 9, 3)                        # стойка
carriage += Pos(0, 32, 1.2) * Cylinder(12.5, 2.4)                   # кольцо Ø18 внутр.
carriage -= Pos(0, 32, 1.2) * Cylinder(9, 4)
carriage += Pos(0, 0.8, 11.25) * Box(24, 1.6, 7.7)                  # крыло: y_p 0..1.6 (z 8..9.6)
# зубья рейки: трапеции поперёк крыла, шаг pi
tooth_2d = [(-1.25, 0), (1.25, 0), (0.55, 1.8), (-0.55, 1.8)]
for i in range(-3, 4):
    yc = i * RACK_P
    pts = [(yc + dx, 1.6 + dz) for dx, dz in tooth_2d]
    tooth = extrude(make_face(
        (Curve() + [Line(pts[j], pts[(j + 1) % 4]) for j in range(4)]).edges()), 7.7)
    carriage += Pos(0, 0, 7.4) * tooth

# ---------------- шестерня (печать плашмя зубьями вверх) ----------------
gear_pts = []
for k in range(PIN_TEETH):
    a = k * 30.0
    for ang, r in ((a - 8.5, PIN_RR), (a - 4.0, PIN_RT), (a + 4.0, PIN_RT), (a + 8.5, PIN_RR)):
        t = math.radians(ang)
        gear_pts.append((PIN_RR * 0 + r * math.cos(t), r * math.sin(t)))
gear_lines = [Line(gear_pts[i], gear_pts[(i + 1) % len(gear_pts)]) for i in range(len(gear_pts))]
pinion = extrude(make_face((Curve() + gear_lines).edges()), 4)      # тело зубьев, толщина 4
pinion += Pos(0, 0, 5.5) * Cylinder(4.5, 3)                         # хаб к серво
pinion -= Pos(0, 0, 5.25) * Cylinder(2.3, 4.6)                      # бора Ø4.6 на шлицы (натяг)
pinion -= Cylinder(1.2, 20)                                         # канал винта M2, ступень-упор

# ---------------- экспорт ----------------
parts = [("base_v6", base), ("neck_v6", neck_part), ("carriage_v6", carriage), ("pinion_v6", pinion)]
for name, part in parts:
    p = part if isinstance(part, Part) else Part() + part
    export_stl(p, rf"{OUT}\{name}.stl")
    print(f"{name}: volume={p.volume:.0f} mm3, solids={len(p.solids())}")

# ---------------- проверка + рендер ----------------
import numpy as np
import trimesh
import pyvista as pv

meshes = {}
for name, _ in parts:
    m = trimesh.load(rf"{OUT}\{name}.stl")
    print(f"{name}: watertight={m.is_watertight}, bodies={m.body_count}")
    meshes[name] = m

asm = pv.Plotter(off_screen=True, window_size=(1500, 950))
asm.add_mesh(pv.wrap(meshes["base_v6"]), color="#9fb4c7", smooth_shading=False)
nk = meshes["neck_v6"].copy()
nk.apply_translation([0, 0, NECK_SEAT])
asm.add_mesh(pv.wrap(nk), color="#c7b49f", smooth_shading=False)
cr = meshes["carriage_v6"].copy()
cr.apply_transform(np.array([[0, 0, 1, XSLOT - 3.7], [1, 0, 0, 0],
                             [0, 1, 0, NECK_SEAT + 8], [0, 0, 0, 1]], dtype=float))
asm.add_mesh(pv.wrap(cr), color="#4fae8a", smooth_shading=False)
pn = meshes["pinion_v6"].copy()
pn.apply_transform(np.array([[0, 0, 1, -183.5], [0, 1, 0, 0],
                             [-1, 0, 0, NECK_SEAT + AXIS_Z], [0, 0, 0, 1]], dtype=float))
asm.add_mesh(pv.wrap(pn), color="#8a7fd4", smooth_shading=False)
asm.set_background("white")
asm.camera_position = "iso"
asm.camera.zoom(1.25)
asm.screenshot(rf"{OUT}\_v6_assembly_iso.png")

pl2 = pv.Plotter(off_screen=True, window_size=(1400, 900))
pl2.add_mesh(pv.wrap(nk), color="#c7b49f", smooth_shading=False, opacity=0.55)
pl2.add_mesh(pv.wrap(cr), color="#4fae8a", smooth_shading=False)
pl2.add_mesh(pv.wrap(pn), color="#8a7fd4", smooth_shading=False)
pl2.set_background("white")
pl2.camera_position = [(-255, -80, 100), (-180, 0, 28), (0, 0, 1)]
pl2.screenshot(rf"{OUT}\_v6_gear_closeup.png")
print("renders done")
