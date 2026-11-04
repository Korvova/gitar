# -*- coding: utf-8 -*-
r"""Сцена: только механизм кассеты — тележка выдвигается и втягивается (±24), с паузами на краях. Основание и тележка
полупрозрачные, чтобы видеть зацепления: шестерня мотора Z18 → рейка ползуна; плавающие Z12 на ползуне катятся по
неподвижной рейке основания и толкают рейку тележки — тележка идёт вдвое дальше ползуна. Пробел — анимация.
Запуск: blender -b -P 2-0\kasseta\scene_kasseta_mehanizm.py
"""
import math
import os
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
P_STL = os.path.join(HERE, "..", "Print", "Print")
OUT = os.path.join(HERE, "Кассета_механизм.blend")
Y_PIN, Y_FLOAT = 16.5, 6.0
P = math.pi * 0.5
SP_FLOAT = 5 * P
Z_GEAR0 = 1.2 + 17.5 + 0.1
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


stl("kas_osnovanie", "основание с неподвижной рейкой (не двигается)", mat("основание", (0.75, 0.75, 0.80, 1), 0.25))
pin = stl("kas_shesternya_motora", "шестерня мотора Z18 (крутит мотор)", mat("шестерня мотора", (0.95, 0.55, 0.20, 1)))
fl = [stl("kas_plav_fdm", "плавающая Z12 %d" % (i + 1), mat("плавающие", (0.20, 0.75, 0.35, 1))) for i in range(2)]
sld = stl("kas_polzun_fdm", "ползун (едет на половину хода)", mat("ползун", (0.25, 0.50, 0.90, 1), 0.85))
cart = stl("kas_telezhka", "тележка (едет на весь ход ±24)", mat("тележка", (0.90, 0.25, 0.25, 1), 0.55))


def travel(f):
    """ход тележки по кадру: 0 → +24 (выдвинулась) → пауза → −24 → пауза → 0"""
    t = (f - 1) / (FR - 1)
    keys = [(0.00, 0), (0.22, 24), (0.30, 24), (0.70, -24), (0.78, -24), (1.00, 0)]
    for (t0, d0), (t1, d1) in zip(keys, keys[1:]):
        if t <= t1:
            u = (t - t0) / (t1 - t0) if t1 > t0 else 1
            return d0 + (d1 - d0) * (0.5 - 0.5 * math.cos(math.pi * u))     # плавно разгон/торможение
    return 0


for f in range(1, FR + 1):
    d = travel(f)
    s = d / 2
    pin.location, pin.rotation_euler = (0, Y_PIN, Z_GEAR0), (0, 0, -s / 4.5)
    sld.location, cart.location = (s, 0, 0), (d, 0, 0)
    for ob in (pin, sld, cart):
        ob.keyframe_insert("location", frame=f)
    pin.keyframe_insert("rotation_euler", index=2, frame=f)
    for ob, x in zip(fl, (-SP_FLOAT / 2, SP_FLOAT / 2)):
        ob.location, ob.rotation_euler = (x + s, Y_FLOAT, Z_GEAR0 + 0.1), (0, 0, s / 3.0)
        ob.keyframe_insert("location", frame=f)
        ob.keyframe_insert("rotation_euler", index=2, frame=f)

# камера сверху-сбоку: видно, что тележка уходит вдвое дальше ползуна
tgt = bpy.data.objects.new("цель", None)
sc.collection.objects.link(tgt)
tgt.location = (0, 12, 20)
cam = bpy.data.objects.new("Камера", bpy.data.cameras.new("Камера"))
sc.collection.objects.link(cam)
cam.data.clip_start, cam.data.clip_end, cam.data.lens = 1, 50000, 45
cam.location = (35, -75, 95)
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
print("механизм кассеты: кадров %d" % FR)
