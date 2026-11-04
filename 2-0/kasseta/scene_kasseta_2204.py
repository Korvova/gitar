# -*- coding: utf-8 -*-
r"""Сцена: кассета под гимбал 2204 (kasseta_2204.py, стол 107) — мотор неподвижен, фланец с ножкой и шестернёй крутятся,
тележка выдвигается и втягивается ±24 с паузами. Основание полупрозрачное. Пробел — анимация.
Запуск: blender -b -P 2-0\kasseta\scene_kasseta_2204.py
"""
import math
import os
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
P_STL = os.path.join(HERE, "..", "Print", "Print")
OUT = os.path.join(HERE, "Кассета_2204.blend")
Y_PIN, Y_FLOAT = 16.5, 6.0
SP_FLOAT = 5 * math.pi * 0.5
Z_GEAR0 = 18.8
Z_MTOP, ZW = 1.2 + 12.23, 16.85
FR = 360

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


def stl(fname, name, m):
    bpy.ops.wm.stl_import(filepath=os.path.join(P_STL, fname + ".stl"))
    ob = bpy.context.selected_objects[0]
    ob.name = name
    ob.data.materials.clear()
    ob.data.materials.append(m)
    return ob


stl("kas2204_osnovanie", "основание под 2204 (не двигается)", mat("основание", (0.75, 0.75, 0.80, 1), 0.3))
bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=27.8 / 2, depth=12.23, location=(0, Y_PIN, 1.2 + 12.23 / 2))
bpy.context.object.name = "гимбал 2204 (неподвижен; крутится торец)"
bpy.context.object.data.materials.append(mat("мотор", (0.12, 0.12, 0.14, 1), 0.8))
stl("kas2204_upor", "упор-вкладыш в конце канавки (клей)", mat("упор", (0.95, 0.15, 0.15, 1)))
fl = stl("kas2204_flanec", "фланец на торец мотора (4 × М2 на Ø12)", mat("фланец", (0.55, 0.55, 0.6, 1)))
nz = stl("kas2204_nozhka_shesternya", "ножка с шестернёй Z18", mat("шестерня мотора", (0.95, 0.55, 0.20, 1)))
flo = [stl("kas_plav_fdm", "плавающая Z12 %d" % (i + 1), mat("плавающие", (0.20, 0.75, 0.35, 1))) for i in range(2)]
sld = stl("kas_polzun_fdm", "ползун (полхода)", mat("ползун", (0.25, 0.50, 0.90, 1), 0.85))
cart = stl("kas_telezhka", "тележка (ход ±24)", mat("тележка", (0.90, 0.25, 0.25, 1), 0.6))


def travel(f):
    t = (f - 1) / (FR - 1)
    keys = [(0.00, 0), (0.22, 24), (0.30, 24), (0.70, -24), (0.78, -24), (1.00, 0)]
    for (t0, d0), (t1, d1) in zip(keys, keys[1:]):
        if t <= t1:
            u = (t - t0) / (t1 - t0) if t1 > t0 else 1
            return d0 + (d1 - d0) * (0.5 - 0.5 * math.cos(math.pi * u))
    return 0


for f in range(1, FR + 1):
    d = travel(f)
    s = d / 2
    for ob, z in ((fl, Z_MTOP), (nz, ZW - 0.05)):
        ob.location, ob.rotation_euler = (0, Y_PIN, z), (0, 0, -s / 4.5)
        ob.keyframe_insert("location", frame=f)
        ob.keyframe_insert("rotation_euler", index=2, frame=f)
    sld.location, cart.location = (s, 0, 0), (d, 0, 0)
    sld.keyframe_insert("location", frame=f)
    cart.keyframe_insert("location", frame=f)
    for ob, x in zip(flo, (-SP_FLOAT / 2, SP_FLOAT / 2)):
        ob.location, ob.rotation_euler = (x + s, Y_FLOAT, Z_GEAR0 + 0.1), (0, 0, s / 3.0)
        ob.keyframe_insert("location", frame=f)
        ob.keyframe_insert("rotation_euler", index=2, frame=f)

tgt = bpy.data.objects.new("цель", None)
sc.collection.objects.link(tgt)
tgt.location = (0, 14, 14)
cam = bpy.data.objects.new("Камера", bpy.data.cameras.new("Камера"))
sc.collection.objects.link(cam)
cam.data.clip_start, cam.data.clip_end, cam.data.lens = 1, 50000, 45
cam.location = (45, -80, 85)
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
print("кассета 2204: сцена сохранена")
