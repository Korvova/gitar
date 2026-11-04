# -*- coding: utf-8 -*-
r"""Сцена: рольганг под 2204 (rolgang_2204.py) — три верхние шестерни ведут рейку тележки 20 мм, промежуточные в нижнем
слое крутят крайние; тележка ходит ±24 с паузами. Шестерня, на которой сейчас рейка, — ярче. Основание и крышка
полупрозрачные. Пробел — анимация. Запуск: blender -b -P 2-0\kasseta\scene_rolgang.py
"""
import json
import math
import os
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
P_STL = os.path.join(HERE, "..", "Print", "Print")
OUT = os.path.join(HERE, "Рольганг_2204.blend")
F = json.load(open(os.path.join(HERE, "rg_fazy.json")))
S, Y_P, Y_I, Z_L0, FL_COLLAR, Z_MTOP, RP, RI = (F[k] for k in ("S", "Y_P", "Y_I", "Z_L0", "FL_COLLAR", "Z_MTOP", "RP", "RI"))
PH_I = {1: F["PH_I"]["1"], -1: F["PH_I"]["-1"]}
RK_HALF = 10.0
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


stl("rg_osnovanie_niz", "основание: низ", mat("основание", (0.75, 0.75, 0.80, 1), 0.3))
stl("rg_osnovanie_verh", "основание: верх — палуба со штырьками (на клей)", mat("палуба", (0.70, 0.78, 0.85, 1), 0.35))
stl("rg_kryshka", "крышка над верхними шестернями", mat("крышка", (0.70, 0.75, 0.85, 1), 0.25))
stl("rg_rels", "рельс тележки", mat("рельс", (0.55, 0.55, 0.6, 1)))
bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=27.8 / 2, depth=12.23, location=(0, Y_P, 1.2 + 12.23 / 2))
bpy.context.object.name = "гимбал 2204 (неподвижен)"
bpy.context.object.data.materials.append(mat("мотор", (0.12, 0.12, 0.14, 1), 0.85))
stl("kas2204_flanec", "фланец на торец мотора", mat("фланец", (0.5, 0.5, 0.55, 1)), (0, Y_P, Z_MTOP))
top = {}
top[0] = stl("rg_shesternya_centr", "средняя шестерня (на моторе)", mat("средняя", (0.95, 0.55, 0.20, 1)), (0, Y_P, FL_COLLAR))
top[1] = stl("rg_shesternya_kraj_prav", "крайняя правая (метка •)", mat("крайняя прав", (0.95, 0.55, 0.20, 1)), (S, Y_P, Z_L0))
top[-1] = stl("rg_shesternya_kraj_lev", "крайняя левая (метка ••)", mat("крайняя лев", (0.95, 0.55, 0.20, 1)), (-S, Y_P, Z_L0))
idl = {sx: stl("rg_promezh", "промежуточная %s" % ("правая" if sx > 0 else "левая"), mat("промежуточные", (0.20, 0.70, 0.35, 1)),
               (sx * S / 2, Y_I, Z_L0)) for sx in (1, -1)}
cart = stl("rg_telezhka", "тележка 20 мм с рейкой", mat("тележка", (0.90, 0.25, 0.25, 1), 0.6))


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
    for k, ob in top.items():
        ob.rotation_euler = (0, 0, -c / RP)
        ob.keyframe_insert("rotation_euler", index=2, frame=f)
        on = abs(c - k * S) <= RK_HALF - 0.9                 # рейка над этой шестерней — ярче
        m = ob.data.materials[0]
        m.diffuse_color = (0.95, 0.55, 0.20, 1) if on else (0.55, 0.45, 0.35, 1)
        m.keyframe_insert("diffuse_color", frame=f)
    for sx, ob in idl.items():
        ob.rotation_euler = (0, 0, math.radians(PH_I[sx]) + c / RI)
        ob.keyframe_insert("rotation_euler", index=2, frame=f)

tgt = bpy.data.objects.new("цель", None)
sc.collection.objects.link(tgt)
tgt.location = (0, 12, 18)
cam = bpy.data.objects.new("Камера", bpy.data.cameras.new("Камера"))
sc.collection.objects.link(cam)
cam.data.clip_start, cam.data.clip_end, cam.data.lens = 1, 50000, 40
cam.location = (35, -85, 100)
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
print("рольганг: сцена сохранена")
