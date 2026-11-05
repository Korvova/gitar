# -*- coding: utf-8 -*-
r"""Сцена: барабанный кулачок на 2204 (baraban_2204.py, стол 110) — мотор неподвижен внутри барабана, барабан крутится,
палец тележки идёт по винтовой канавке, тележка ±24 с паузами. Барабан полупрозрачный — видно мотор внутри.
Пробел — анимация. Запуск: blender -b -P 2-0\kasseta\scene_baraban.py
"""
import math
import os
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
P_STL = os.path.join(HERE, "..", "Print", "Print")
OUT = os.path.join(HERE, "Барабан_2204.blend")
TRAVEL, X0 = 24.0, -28.0
R_OUT = 27.8 / 2 + 0.05 + 3.2
Z_AX = 3.0 + 1.0 + R_OUT
RHO0, DEG_PER_MM = -325.0, -6.0           # угол барабана при тележке в 0 и на мм хода (из проверки baraban_2204.py)
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


stl("bar_rama", "рама: дно и щёки", mat("рама", (0.75, 0.75, 0.80, 1), 0.35))
stl("bar_rels", "рельс (ласточкин хвост)", mat("рельс", (0.55, 0.55, 0.6, 1)))
bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=27.8 / 2, depth=12.23, location=(X0 - 2.5 + 12.23 / 2, 0, Z_AX),
                                    rotation=(0, math.radians(90), 0))
bpy.context.object.name = "гимбал 2204 внутри барабана (неподвижен)"
bpy.context.object.data.materials.append(mat("мотор", (0.12, 0.12, 0.14, 1)))
drum = stl("bar_baraban", "барабан с винтовой канавкой", mat("барабан", (0.95, 0.75, 0.35, 1), 0.7))
drum.location = (X0, 0, Z_AX)
drum.rotation_mode = 'ZYX'
cart = stl("bar_telezhka", "тележка с пальцем", mat("тележка", (0.90, 0.25, 0.25, 1), 0.8))


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
    drum.rotation_euler = (0, math.radians(90), math.radians(RHO0 + DEG_PER_MM * c))   # Ry(90) · Rz(ρ)
    drum.keyframe_insert("rotation_euler", frame=f)

tgt = bpy.data.objects.new("цель", None)
sc.collection.objects.link(tgt)
tgt.location = (0, 0, 25)
cam = bpy.data.objects.new("Камера", bpy.data.cameras.new("Камера"))
sc.collection.objects.link(cam)
cam.data.clip_start, cam.data.clip_end, cam.data.lens = 1, 50000, 40
cam.location = (60, -110, 90)
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
print("барабан: сцена сохранена")
