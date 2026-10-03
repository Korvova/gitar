# -*- coding: utf-8 -*-
r"""Концепт «катушка в каркасе» (идея владельца 03.10): мотаем прямо в каркас, каркасы вставляем в рамку
кассетами. Каркас 6.5 × 20.9 × 4: сердечник 1.6 × 16, две щёчки по 0.5 (голубые), между ними провод 3 мм.
Рамка 4 мм, скоба со щелью 5 (по 0.5 воздуха с каждой стороны). Фигуры условные.
Кадры: 1–160 — 8 каркасов по одному опускаются в рамку; 160–200 — скоба садится; дальше — ход ±22.
Сзади — один каркас крупно: щёчка спереди прозрачная, видно витки.
Запуск: blender -b -P 2-0\magnit\scene_karkas_idea.py
"""
import math
import os
import bpy

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Идея_каркас_катушки.blend")
CW, CH, WX, WY = 6.5, 20.9, 1.6, 16.0
FL, WIRE_T = 0.5, 3.0
BT = WIRE_T + 2 * FL                     # толщина каркаса 4
G = BT + 1.0                             # щель скобы 5
D, NZ, NL = 0.34, 8, 5
FRAMES = 300

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.unit_settings.system = 'METRIC'
sc.unit_settings.scale_length = 0.001
sc.frame_start, sc.frame_end = 1, FRAMES


def mat(name, rgba, alpha=1.0, metal=0.0):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rgba
    b.inputs["Metallic"].default_value = metal
    if alpha < 1:
        b.inputs["Alpha"].default_value = alpha
        try:
            m.surface_render_method = 'BLENDED'
        except Exception:
            pass
    return m


def box(name, x0, x1, y0, y1, z0, z1, m, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), rotation=(0, 0, 0))
    ob = bpy.context.object
    ob.name = name
    ob.scale = (x1 - x0, y1 - y0, z1 - z0)
    ob.data.materials.append(m)
    if parent:
        ob.parent = parent
    return ob


C_FL = mat("каркас (щёчки)", (0.45, 0.65, 0.95, 1))
C_FLT = mat("каркас: передняя щёчка прозрачная", (0.45, 0.65, 0.95, 1), 0.25)
C_CU = mat("медь", (0.90, 0.40, 0.12, 1), metal=0.3)
C_FR = mat("рамка", (0.93, 0.93, 0.95, 1), 0.6)
C_N, C_S = mat("магнит N", (0.85, 0.15, 0.15, 1)), mat("магнит S", (0.15, 0.30, 0.85, 1))
C_FE = mat("сталь", (0.45, 0.47, 0.5, 1), metal=0.6)
C_SK = mat("скоба", (0.95, 0.95, 0.97, 1), 0.3)

# витки одной катушки — кривая в системе каркаса: окно вдоль Z (стоймя), толщина по Y (±1.5), выводы вниз
pts = []
for L in range(NL):
    r = D / 2 + L * D
    hx, hz = WX / 2 + r, WY / 2 + r
    for i in range(NZ):
        k = i if L % 2 == 0 else NZ - 1 - i
        y = -WIRE_T / 2 + D / 2 + k * D
        for (x, z) in ((hx, -hz), (-hx, -hz), (-hx, hz), (hx, hz)):
            pts.append((x, y, z))
        pts.append((hx, y, -hz))
pts = [(WX / 2 + 0.3, -WIRE_T / 2 + D / 2, -CH / 2 - 6)] + pts + [(pts[-1][0] + 1.0, pts[-1][1], -CH / 2 - 6)]
cu = bpy.data.curves.new("витки", "CURVE")
cu.dimensions = '3D'; cu.bevel_depth = D / 2 * 0.9; cu.bevel_resolution = 1
sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
for p_, (x, y, z) in zip(sp.points, pts):
    p_.co = (x, y, z, 1)
cu.materials.append(C_CU)


def bobbin(name, front_transparent=False):
    e = bpy.data.objects.new(name, None)
    sc.collection.objects.link(e)
    box(name + ": задняя щёчка 0.5", -CW / 2, CW / 2, WIRE_T / 2, WIRE_T / 2 + FL, -CH / 2, CH / 2, C_FL, e)
    box(name + ": передняя щёчка 0.5", -CW / 2, CW / 2, -WIRE_T / 2 - FL, -WIRE_T / 2, -CH / 2, CH / 2, C_FLT if front_transparent else C_FL, e)
    box(name + ": сердечник 1.6 × 16", -WX / 2, WX / 2, -WIRE_T / 2, WIRE_T / 2, -WY / 2, WY / 2, C_FL, e)
    w = bpy.data.objects.new(name + ": провод", cu)
    sc.collection.objects.link(w)
    w.parent = e
    return e


# рамка 4 мм с окном 52 × 21
box("рамка: низ", -29, 29, -BT / 2, BT / 2, -CH / 2 - 3, -CH / 2, C_FR)
box("рамка: верх (рельс)", -29, 29, -BT / 2, BT / 2, CH / 2, CH / 2 + 3, C_FR)
for s in (1, -1):
    box("рамка: стойка", s * 26, s * 29, -BT / 2, BT / 2, -CH / 2, CH / 2, C_FR)
for k in range(8):
    b = bobbin("каркас %d" % (k + 1))
    x = -26 + k * CW + CW / 2
    f0 = 10 + k * 18
    b.location = (x, 0, 45); b.keyframe_insert("location", frame=1); b.keyframe_insert("location", frame=f0)
    b.location = (x, 0, 0); b.keyframe_insert("location", frame=f0 + 15)

# скоба: магниты 20×10×5 по 3 с каждой стороны, щель G, сталь снаружи
sk = bpy.data.objects.new("скоба (едет)", None)
sc.collection.objects.link(sk)
for side in (1, -1):
    for p in range(3):
        n_face = (p % 2 == 0) == (side > 0)
        y0, y1 = sorted((side * G / 2, side * (G / 2 + 5)))
        box("магнит 20×10×5", -15 + p * 10, -5 + p * 10, y0, y1, -10, 10, C_N if n_face else C_S, sk)
    y0, y1 = sorted((side * (G / 2 + 5), side * (G / 2 + 6.5)))
    box("сталь 1.5", -15, 15, y0, y1, -10, 10, C_FE, sk)
box("мостик", -16, 16, -(G / 2 + 7.7), G / 2 + 7.7, CH / 2 + 3.3, CH / 2 + 5.8, C_SK, sk)
sk.location = (0, 0, 60); sk.keyframe_insert("location", frame=1); sk.keyframe_insert("location", frame=160)
sk.location = (0, 0, 0); sk.keyframe_insert("location", frame=200)
for f in range(200, FRAMES + 1, 2):
    sk.location = (22 * math.sin(2 * math.pi * (f - 200) / (FRAMES - 200)), 0, 0)
    sk.keyframe_insert("location", frame=f)

# один каркас крупно справа (×3), передняя щёчка прозрачная
big = bobbin("каркас крупно", front_transparent=True)
big.location = (0, 90, 0); big.scale = (3, 3, 3)

for name, loc, tgt, lens in (("Камера: всё", (80, -130, 60), (0, 0, 0), 32),
                             ("Камера: торец (видно щель)", (150, 0, 0), (0, 0, 0), 70),
                             ("Камера: каркас крупно", (70, 20, 45), (0, 90, 0), 30)):
    t = bpy.data.objects.new(name + " цель", None); sc.collection.objects.link(t); t.location = tgt
    c = bpy.data.objects.new(name, bpy.data.cameras.new(name)); sc.collection.objects.link(c)
    c.data.lens = lens; c.data.clip_start = 1; c.location = loc
    tc = c.constraints.new('TRACK_TO'); tc.target = t; tc.track_axis = 'TRACK_NEGATIVE_Z'; tc.up_axis = 'UP_Y'
    if name.startswith("Камера: всё"):
        sc.camera = c
sun = bpy.data.objects.new("Солнце", bpy.data.lights.new("Солнце", "SUN"))
sun.data.energy = 3.5
sun.rotation_euler = (math.radians(35), math.radians(10), math.radians(40))
sc.collection.objects.link(sun)
sc.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("saved", OUT)
