# -*- coding: utf-8 -*-
r"""Сцена: стенд «мотор в тележке» (gitara_motor1.py, стол 101) — гимбал 2204 на ребре, шестерня m1 z26 катится
по рейке, тележка ездит на Т-рельсах ±22. Пробел — анимация. Запуск: blender -b -P 2-0\scene_motor1.py"""
import math
import os
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "Print", "Print")
OUT = os.path.join(HERE, "Стенд_мотор_в_тележке.blend")
RP, Z_AX, Y_G1, Z_ROOF1 = 13.0, 20.0, 19.4, 36.7
FRAMES = 200
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.unit_settings.system, sc.unit_settings.scale_length, sc.unit_settings.length_unit = 'METRIC', 0.001, 'MILLIMETERS'
sc.frame_start, sc.frame_end = 1, FRAMES


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


def stl(fname, name, m, loc=(0, 0, 0), rot=(0, 0, 0)):
    bpy.ops.wm.stl_import(filepath=os.path.join(P, fname + ".stl"))
    ob = bpy.context.selected_objects[0]
    ob.name = name
    ob.data.materials.clear()
    ob.data.materials.append(m)
    ob.location, ob.rotation_euler = loc, rot
    return ob


stl("m1_osnova", "плита: рельсы и рейка m1", mat("плита", (0.8, 0.8, 0.84, 1)))
tel = stl("m1_telezhka", "рама-клетка", mat("тележка", (0.95, 0.72, 0.30, 1), 0.55))
lid = stl("m1_kryshka", "крышка на защёлках", mat("крышка", (0.80, 0.60, 0.25, 1), 0.55))
mot = stl("m1_motor_proverka", "гимбал 2204", mat("мотор", (0.15, 0.15, 0.17, 1)))
lz = stl("m1_lozhe", "ложе", mat("ложе", (0.85, 0.35, 0.35, 1)), (0, 10.0, Z_ROOF1))
# шестерня: в STL ось Z — ставим осью вдоль Y, торцом к мотору
g_piv = bpy.data.objects.new("шестерня (поворот)", None)
sc.collection.objects.link(g_piv)
g = stl("m1_shesternya", "шестерня m1 z26", mat("шестерня", (0.30, 0.70, 0.40, 1)), (0, 0, 0), (math.radians(90), 0, 0))
g.parent = g_piv
for f in range(1, FRAMES + 1):
    x = 22.0 * math.sin(2 * math.pi * (f - 1) / (FRAMES - 1))
    for ob in (tel, mot, lid):
        ob.location.x = x
        ob.keyframe_insert("location", index=0, frame=f)
    lz.location.x = x
    lz.keyframe_insert("location", index=0, frame=f)
    g_piv.location = (x, Y_G1, Z_AX)
    g_piv.rotation_euler = (0, x / RP, 0)
    g_piv.keyframe_insert("location", frame=f)
    g_piv.keyframe_insert("rotation_euler", index=1, frame=f)
tgt = bpy.data.objects.new("цель", None)
sc.collection.objects.link(tgt)
tgt.location = (0, 8, 12)
cam = bpy.data.objects.new("Камера", bpy.data.cameras.new("Камера"))
sc.collection.objects.link(cam)
cam.data.clip_start, cam.data.clip_end, cam.data.lens = 1, 50000, 35
cam.location = (75, 120, 80)
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
print("saved", OUT)
