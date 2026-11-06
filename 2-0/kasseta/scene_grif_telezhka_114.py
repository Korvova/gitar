# -*- coding: utf-8 -*-
r"""Сцена: стенд на одну тележку по вики 19.42/19.43 (grif_telezhka_114.py, стол 114) — детали те же, что на печать.
Пробел — анимация: тележка ±22, шестерня катится по рейке, мотор крутится вместе с ней. Кубик полупрозрачный.
Запуск: blender -b -P 2-0\kasseta\scene_grif_telezhka_114.py"""
import math
import os
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
P_STL = os.path.join(HERE, "..", "Print", "Print")
OUT = os.path.join(HERE, "Стенд_тележка_114.blend")
RP = 6.0
FR = 240
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


def stl(fname, name, m, rz=0.0):
    bpy.ops.wm.stl_import(filepath=os.path.join(P_STL, fname + ".stl"))
    ob = bpy.context.selected_objects[0]
    ob.name = name
    ob.data.materials.clear()
    ob.data.materials.append(m)
    ob.rotation_euler = (0, 0, rz)
    return ob


BLK = mat("чёрный", (0.06, 0.06, 0.07, 1))
LEGM = mat("ножки", (0.45, 0.45, 0.5, 1))
stl("gt_platforma", "платформа", BLK)
stl("gt_kryshka_reiki", "крышка над зубьями (планка)", mat("планка", (0.2, 0.2, 0.24, 1)))
stl("gt_upor", "упор x+ (клеить после надевания)", mat("упор", (0.8, 0.2, 0.2, 1)))
stl("gt_nozhka", "ножка 1", LEGM)
stl("gt_nozhka", "ножка 2", LEGM, math.pi)
SVET = mat("кубик", (0.86, 0.83, 0.77, 1), 0.45)
cart = [stl("gt_kubik", "кубик", SVET), stl("gt_niz", "нижний этаж", mat("низ", (0.75, 0.72, 0.66, 1))),
        stl("gt_bort", "борт ложа 1", mat("борт", (0.86, 0.83, 0.77, 1))), stl("gt_bort", "борт ложа 2", bpy.data.materials["борт"], math.pi)]
for o in cart[2:]:
    pass
RZ = {cart[2].name: 0.0, cart[3].name: math.pi}
M_G = mat("шестерня", (0.95, 0.55, 0.15, 1))
rot = [stl("gt_shesternya", "шестерня", M_G), stl("gt_flanec", "фланец", mat("фланец", (0.9, 0.75, 0.25, 1)))]
bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=13.9, depth=12.23, location=(0, 0, 4.02 + 12.23 / 2))
motor = bpy.context.object
motor.name = "мотор 2204 (перевёрнут)"
motor.data.materials.append(mat("мотор", (0.12, 0.12, 0.14, 1)))
bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
bpy.ops.object.select_all(action='DESELECT')
for f in range(1, FR + 1):
    c = 22.0 * math.sin(2 * math.pi * (f - 1) / (FR - 1))
    for ob in cart:
        ob.location = (c, 0, 0)
        ob.keyframe_insert("location", frame=f)
    for ob in rot + [motor]:
        ob.location = (c, 0, 0)
        ob.rotation_euler = (0, 0, c / RP)
        ob.keyframe_insert("location", frame=f)
        ob.keyframe_insert("rotation_euler", index=2, frame=f)
tgt = bpy.data.objects.new("цель", None)
sc.collection.objects.link(tgt)
tgt.location = (0, 0, 2)
cam = bpy.data.objects.new("Камера", bpy.data.cameras.new("Камера"))
sc.collection.objects.link(cam)
cam.data.clip_start, cam.data.clip_end, cam.data.lens = 1, 50000, 50
cam.location = (70, -110, 70)
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
print("стенд: сцена сохранена")
