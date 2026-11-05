# -*- coding: utf-8 -*-
r"""Сцена: плоский диск-кулачок (disk_2204.py, стол 113) — диск крутится, штырёк тележки идёт по канавке, тележка ±24 между
двумя рельсами. Тележка полупрозрачная. Пробел — анимация. Запуск: blender -b -P 2-0\kasseta\scene_disk.py"""
import json
import math
import os
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
P_STL = os.path.join(HERE, "..", "Print", "Print")
OUT = os.path.join(HERE, "Диск_кулачок.blend")
K = json.load(open(os.path.join(HERE, "disk_param.json")))["K"]
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


stl("disk_osnovanie", "основание со стойками", mat("основание", (0.80, 0.78, 0.72, 1)))
disk = stl("disk_disk", "диск с канавкой", mat("диск", (0.95, 0.55, 0.20, 1)))
m_r = mat("рельс", (0.55, 0.55, 0.6, 1))
stl("disk_rels", "рельс 1", m_r)
r2 = stl("disk_rels", "рельс 2", m_r)
r2.rotation_euler = (0, 0, math.pi)
cart = stl("disk_telezhka", "тележка со штырьком", mat("тележка", (0.30, 0.55, 0.85, 1), 0.65))


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
    disk.rotation_euler = (0, 0, -c / K)
    disk.keyframe_insert("rotation_euler", index=2, frame=f)
tgt = bpy.data.objects.new("цель", None)
sc.collection.objects.link(tgt)
tgt.location = (0, 0, 6)
cam = bpy.data.objects.new("Камера", bpy.data.cameras.new("Камера"))
sc.collection.objects.link(cam)
cam.data.clip_start, cam.data.clip_end, cam.data.lens = 1, 50000, 40
cam.location = (50, -100, 110)
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
print("диск: сцена сохранена")
