# -*- coding: utf-8 -*-
r"""Сцена: проба на 4 пальца (grif_4_telezhki_116.py, стол 116). Детали те, что на печать. Тележки 1 и 2 с мотором, 3 и 4 без мотора.
Пробел — анимация, тележки ходят независимо. Запуск: blender -b -P 2-0\kasseta\scene_grif_116.py"""
import math
import os
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
P_STL = os.path.join(HERE, "..", "Print", "Print")
OUT = os.path.join(HERE, "Гриф_4_пальца_116.blend")
RP, FR = 6.0, 240
Z_M0 = 5.52
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.unit_settings.system, sc.unit_settings.scale_length, sc.unit_settings.length_unit = 'METRIC', 0.001, 'MILLIMETERS'
sc.frame_start, sc.frame_end = 1, FR


def mat(name, rgba, alpha=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rgba
    if alpha < 1:
        b.inputs["Alpha"].default_value = alpha
        m.surface_render_method = 'BLENDED'
    m.diffuse_color = (rgba[0], rgba[1], rgba[2], alpha)
    return m


def stl(fname, name, m, y=0.0, rz=0.0):
    bpy.ops.wm.stl_import(filepath=os.path.join(P_STL, fname + ".stl"))
    ob = bpy.context.selected_objects[0]
    ob.name = name
    ob.data.materials.clear()
    ob.data.materials.append(m)
    ob.location = (0, y, 0)
    ob.rotation_euler = (0, 0, rz)
    return ob


BLK = mat("чёрный", (0.06, 0.06, 0.07, 1))
LEGM = mat("вкладки", (0.45, 0.45, 0.5, 1))
SVET = mat("кубик", (0.86, 0.83, 0.77, 1), 0.55)
SVET2 = mat("кубик без мотора", (0.70, 0.82, 0.70, 1), 0.55)
NIZ = mat("низ", (0.75, 0.72, 0.66, 1))
PLA = mat("пластина", (0.65, 0.62, 0.56, 1))
M_G = mat("шестерня", (0.95, 0.55, 0.15, 1))
M_F = mat("фланец", (0.9, 0.75, 0.25, 1))
M_M = mat("мотор", (0.12, 0.12, 0.14, 1))
PAD = mat("площадка", (0.10, 0.25, 0.75, 1))
RED = mat("упор", (0.8, 0.2, 0.2, 1))
M_MAG = mat("магнит", (0.8, 0.8, 0.85, 1))
M_49 = mat("датчик", (0.9, 0.1, 0.5, 1))
stl("gt4_platforma", "платформа на 4", BLK)
stl("gt4_vkladka", "вкладка 1", LEGM)
stl("gt4_vkladka", "вкладка 2", LEGM, 0.0, math.pi)
FILES = [("gt4_lozhe_9", 0.0), ("gt4_lozhe_3", 0.0), ("gt4_lozhe_3", math.pi), ("gt4_lozhe_9", math.pi)]
carts = []
for i, (fn, rz) in enumerate(FILES):
    y0 = (i - 1.5) * 30.0
    stl("gt_upor", "упор x+ %d" % (i + 1), RED, y0)
    has_m = i < 2
    for mx in (-22.0, -13.2, -4.4, 4.4, 13.2):
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=2.0, depth=1.9, location=(mx, y0 - 13.35, -0.95))
        bpy.context.object.name = "магнит"
        bpy.context.object.data.materials.append(M_MAG)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -12.5, 3.25))
    s49 = bpy.context.object
    s49.name = "датчик 49E %d" % (i + 1)
    s49.scale = (4.1, 3.0, 1.5)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    s49.data.materials.append(M_49)
    bpy.ops.object.select_all(action='DESELECT')
    cart = [s49, stl("gt_kubik", "кубик %d" % (i + 1), SVET if has_m else SVET2, y0), stl("gt_niz", "низ %d" % (i + 1), NIZ, y0),
            stl(fn, "площадка %d" % (i + 1), PAD, y0, rz)]
    rot = []
    if has_m:
        cart.append(stl("gt_plastina", "пластина %d" % (i + 1), PLA, y0))
        rot = [stl("gt_shesternya", "шестерня %d" % (i + 1), M_G, y0), stl("gt_flanec", "фланец %d" % (i + 1), M_F, y0)]
        bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=13.9, depth=12.23, location=(0, 0, Z_M0 + 12.23 / 2))
        mo = bpy.context.object
        mo.name = "мотор %d" % (i + 1)
        mo.data.materials.append(M_M)
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        mo.location = (0, y0, 0)
        bpy.ops.object.select_all(action='DESELECT')
        rot.append(mo)
    carts.append((cart, rot, y0, 0.13 * i, 2 - i % 2))
for f in range(1, FR + 1):
    t = (f - 1) / (FR - 1)
    for cart, rot, y0, ph, n in carts:
        c = 22.0 * math.sin(2 * math.pi * (t * n + ph))
        for ob in cart:
            ob.location = (c, y0, 0)
            ob.keyframe_insert("location", index=0, frame=f)
        for ob in rot:
            ob.location = (c, y0, 0)
            ob.rotation_euler = (0, 0, c / RP)
            ob.keyframe_insert("location", index=0, frame=f)
            ob.keyframe_insert("rotation_euler", index=2, frame=f)
tgt = bpy.data.objects.new("цель", None)
sc.collection.objects.link(tgt)
tgt.location = (0, 0, 8)
cam = bpy.data.objects.new("Камера", bpy.data.cameras.new("Камера"))
sc.collection.objects.link(cam)
cam.data.clip_start, cam.data.clip_end, cam.data.lens = 1, 50000, 50
cam.location = (150, -170, 150)
tc = cam.constraints.new('TRACK_TO')
tc.target, tc.track_axis, tc.up_axis = tgt, 'TRACK_NEGATIVE_Z', 'UP_Y'
sc.camera = cam
w = bpy.data.worlds.new("мир")
w.color = (0.92, 0.92, 0.9)
sc.world = w
sun = bpy.data.objects.new("Солнце", bpy.data.lights.new("Солнце", "SUN"))
sun.data.energy = 3
sun.rotation_euler = (math.radians(30), math.radians(15), math.radians(30))
sc.collection.objects.link(sun)
sc.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("сцена 116 сохранена")
