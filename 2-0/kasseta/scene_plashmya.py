# -*- coding: utf-8 -*-
r"""Сцена: мотор плашмя в тележке (plashmya_2204.py, стол 112) — шестерня под тележкой катится по рейке поперёк куска
грифа, тележка с мотором ходит ±24. Пробел — анимация. Запуск: blender -b -P 2-0\kasseta\scene_plashmya.py"""
import math
import os
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
P_STL = os.path.join(HERE, "..", "Print", "Print")
OUT = os.path.join(HERE, "Мотор_плашмя_2204.blend")
RP, Z_G0, Z_M0, MOT_H = 6.0, 3.6, 12.0, 12.23
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


stl("pl_grif", "кусок грифа: рейка и рельсы", mat("гриф", (0.80, 0.78, 0.72, 1)))
ct = stl("pl_telezhka", "тележка", mat("тележка", (0.30, 0.55, 0.85, 1), 0.8))
lz = stl("pl_lozhe", "ложе над мотором", mat("ложе", (0.90, 0.30, 0.30, 1), 0.5))
bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=27.8 / 2, depth=MOT_H, location=(0, 0, Z_M0 + MOT_H / 2))
mot = bpy.context.object
mot.name = "гимбал 2204 плашмя"
mot.data.materials.append(mat("мотор", (0.12, 0.12, 0.14, 1)))
kr = stl("pl_kryshka", "крышка на крутящемся торце", mat("крышка", (0.6, 0.6, 0.65, 1)))
g = stl("pl_shesternya", "шестерня под тележкой", mat("шестерня", (0.95, 0.55, 0.20, 1)))
# винт М3×20 из набора (DIN 912: круглая головка Ø5.5 × 3) — сверху в гнездо крышки, внизу сам нарезает резьбу в квадратной дырке шестерни
Z_HEAD = Z_M0 + MOT_H + 3.0 - 2.0                      # дно гнезда головки в крышке

m_v = mat("винт", (0.85, 0.85, 0.9, 1))
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=1.5, depth=20.0, location=(0, 0, Z_HEAD - 10.0))
vint = bpy.context.object
vint.name = "винт М3×20 — вставляется сверху"
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=2.75, depth=3.0, location=(0, 0, Z_HEAD + 1.5))
hd = bpy.context.object
for o in (vint, hd):
    o.select_set(True)
bpy.context.view_layer.objects.active = vint
bpy.ops.object.join()
bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
vint.data.materials.append(m_v)


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
    for ob in (ct, lz):
        ob.location = (c, 0, 0)
        ob.keyframe_insert("location", frame=f)
    mot.location = (c, 0, Z_M0 + MOT_H / 2)
    mot.keyframe_insert("location", frame=f)
    for ob in (vint,):
        ob.location, ob.rotation_euler = (c, 0, 0), (0, 0, -c / RP)
        ob.keyframe_insert("location", frame=f)
        ob.keyframe_insert("rotation_euler", index=2, frame=f)
    for ob, z in ((kr, Z_M0 + MOT_H), (g, Z_G0)):
        ob.location, ob.rotation_euler = (c, 0, z), (0, 0, -c / RP)
        ob.keyframe_insert("location", frame=f)
        ob.keyframe_insert("rotation_euler", index=2, frame=f)
tgt = bpy.data.objects.new("цель", None)
sc.collection.objects.link(tgt)
tgt.location = (0, 0, 12)
cam = bpy.data.objects.new("Камера", bpy.data.cameras.new("Камера"))
sc.collection.objects.link(cam)
cam.data.clip_start, cam.data.clip_end, cam.data.lens = 1, 50000, 40
cam.location = (60, -100, 70)
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
print("плашмя: сцена сохранена")
