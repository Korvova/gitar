# -*- coding: utf-8 -*-
r"""Сцена: кассета владельца (04.11.2026) — мотор неподвижен, шестерня Z18 двигает ползун, плавающие Z12 катятся
по неподвижной рейке и толкают тележку вдвое дальше ползуна; ход тележки ±24. Пробел — анимация.
Запуск: blender -b -P 2-0\kasseta\scene_kasseta.py
"""
import math
import os
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
P_STL = os.path.join(HERE, "..", "Print", "Print")
OUT = os.path.join(HERE, "Кассета.blend")
Y_PIN, Y_FLOAT = 16.5, 6.0
P = math.pi * 0.5
SP_FLOAT = 5 * P
Z_GEAR0 = 1.2 + 17.5 + 0.1
FR = 200

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


stl("kas_osnovanie", "основание с неподвижной рейкой", mat("основание", (0.80, 0.80, 0.84, 1), 0.5))
pin = stl("kas_shesternya_motora", "шестерня мотора Z18", mat("шестерня мотора", (0.95, 0.55, 0.20, 1)))
fl = [stl("kas_plav_fdm", "плавающая шестерня Z12 %d" % (i + 1), mat("плавающие", (0.30, 0.70, 0.40, 1))) for i in range(2)]
sld = stl("kas_polzun_fdm", "ползун", mat("ползун", (0.30, 0.55, 0.85, 1), 0.7))
cart = stl("kas_telezhka", "тележка (палец сверху)", mat("тележка", (0.85, 0.30, 0.30, 1)))
# мотор GB1806 без корпуса энкодера — для вида: корпус Ø22 × 14 + выступ Ø9.5 × 3.5, неподвижен
mm = mat("мотор", (0.12, 0.12, 0.14, 1), 0.6)
bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=11, depth=14, location=(0, Y_PIN, 1.2 + 7))
bpy.context.object.name = "GB1806 (неподвижен)"
bpy.context.object.data.materials.append(mm)
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=4.75, depth=3.5, location=(0, Y_PIN, 1.2 + 14 + 1.75))
bpy.context.object.name = "GB1806: выступ Ø9.5"
bpy.context.object.data.materials.append(mm)

for f in range(1, FR + 1):
    d = 24.0 * math.sin(2 * math.pi * (f - 1) / (FR - 1))
    s = d / 2
    a_f, a_p = -s / 3.0, s / 4.5
    pin.location, pin.rotation_euler = (0, Y_PIN, Z_GEAR0), (0, 0, -a_p)
    sld.location = (s, 0, 0)
    cart.location = (d, 0, 0)
    for ob in (pin, sld, cart):
        ob.keyframe_insert("location", frame=f)
    pin.keyframe_insert("rotation_euler", index=2, frame=f)
    for ob, x in zip(fl, (-SP_FLOAT / 2, SP_FLOAT / 2)):
        ob.location, ob.rotation_euler = (x + s, Y_FLOAT, Z_GEAR0 + 0.1), (0, 0, -a_f)
        ob.keyframe_insert("location", frame=f)
        ob.keyframe_insert("rotation_euler", index=2, frame=f)

tgt = bpy.data.objects.new("цель", None)
sc.collection.objects.link(tgt)
tgt.location = (0, 12, 14)
cam = bpy.data.objects.new("Камера", bpy.data.cameras.new("Камера"))
sc.collection.objects.link(cam)
cam.data.clip_start, cam.data.clip_end, cam.data.lens = 1, 50000, 50
cam.location = (70, -80, 80)
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
print("кассета: сцена сохранена")
