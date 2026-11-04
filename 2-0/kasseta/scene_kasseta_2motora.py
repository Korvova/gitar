# -*- coding: utf-8 -*-
r"""Сцена-концепт: кассета на два GB1806 (kasseta_2motora.py) — рейка тележки переходит с шестерни на шестерню, ход ±24
с паузами; шестерни, на которых сейчас рейка, подсвечены. Пробел — анимация.
Запуск: blender -b -P 2-0\kasseta\scene_kasseta_2motora.py
"""
import math
import os
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
P_STL = os.path.join(HERE, "..", "Print", "Print")
OUT = os.path.join(HERE, "Кассета_2_мотора.blend")
X_P, Y_M, Z_G0, RP = 4 * math.pi, 11.0, 1.2 + 20.5 + 0.4, 7.0
RK_HALF = 15.0
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


def stl(fname, name, m, loc=(0, 0, 0)):
    bpy.ops.wm.stl_import(filepath=os.path.join(P_STL, fname + ".stl"))
    ob = bpy.context.selected_objects[0]
    ob.name = name
    ob.data.materials.clear()
    ob.data.materials.append(m)
    ob.location = loc
    return ob


stl("k2m_osnovanie", "основание с рельсом", mat("основание", (0.75, 0.75, 0.80, 1), 0.35))
M_MOT = mat("мотор", (0.12, 0.12, 0.14, 1), 0.85)
gears = []
for i, sx in enumerate((-1, 1)):
    stl("k2m_motor", "GB1806 %d (неподвижен)" % (i + 1), M_MOT, (sx * X_P, Y_M, 1.2))
    gears.append(stl("k2m_shesternya", "шестерня m1 z14 мотора %d" % (i + 1), mat("шестерня %d" % i, (0.95, 0.55, 0.20, 1)),
                     (sx * X_P, Y_M, Z_G0)))
cart = stl("k2m_telezhka", "тележка с рейкой 30", mat("тележка", (0.90, 0.25, 0.25, 1), 0.6))


def travel(f):
    t = (f - 1) / (FR - 1)
    keys = [(0.00, 0), (0.22, 24), (0.30, 24), (0.70, -24), (0.78, -24), (1.00, 0)]
    for (t0, d0), (t1, d1) in zip(keys, keys[1:]):
        if t <= t1:
            u = (t - t0) / (t1 - t0) if t1 > t0 else 1
            return d0 + (d1 - d0) * (0.5 - 0.5 * math.cos(math.pi * u))
    return 0


for f in range(1, FR + 1):
    c = travel(f)
    cart.location = (c, 0, 0)
    cart.keyframe_insert("location", frame=f)
    for g, sx in zip(gears, (-1, 1)):
        g.rotation_euler = (0, 0, -c / RP)                 # обе в фазе (прошивка держит по датчикам)
        g.keyframe_insert("rotation_euler", index=2, frame=f)
        on = abs(c - sx * X_P) <= RK_HALF - 1.5            # рейка на этой шестерне — ярче
        col = (0.95, 0.55, 0.20, 1) if on else (0.55, 0.45, 0.35, 1)
        m = g.data.materials[0]
        m.diffuse_color = col
        m.keyframe_insert("diffuse_color", frame=f)

tgt = bpy.data.objects.new("цель", None)
sc.collection.objects.link(tgt)
tgt.location = (0, 12, 18)
cam = bpy.data.objects.new("Камера", bpy.data.cameras.new("Камера"))
sc.collection.objects.link(cam)
cam.data.clip_start, cam.data.clip_end, cam.data.lens = 1, 50000, 40
cam.location = (40, -90, 95)
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
print("кассета на 2 мотора: сцена сохранена")
