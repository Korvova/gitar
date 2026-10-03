# -*- coding: utf-8 -*-
r"""Сцена: проба магнитного русла (gitara_magnit_proba.py) — настоящие детали стола 86.
Рамка с 8 катушками (оранжевые), основа, U-скоба (белая, полупрозрачная) с 6 магнитами (красные/синие)
и стальными пластинками (серые) ездит ±22 по верхней планке рамки. Плюс оправка рядом.
Запуск: blender -b -P 2-0\magnit\scene_magnit_proba.py
"""
import math
import os
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(os.path.dirname(HERE), "Print", "Print")
OUT = os.path.join(HERE, "Магнит_проба_стол86.blend")
FRAMES = 120

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.unit_settings.system = 'METRIC'
sc.unit_settings.scale_length = 0.001
sc.unit_settings.length_unit = 'MILLIMETERS'
sc.frame_start, sc.frame_end = 1, FRAMES


def mat(name, rgba, alpha=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rgba
    if alpha < 1:
        b.inputs["Alpha"].default_value = alpha
        try:
            m.surface_render_method = 'BLENDED'
        except Exception:
            pass
    m.diffuse_color = (rgba[0], rgba[1], rgba[2], alpha)
    return m


def stl(fname, name, m, loc=(0, 0, 0), parent=None):
    bpy.ops.wm.stl_import(filepath=os.path.join(P, fname + ".stl"))
    ob = bpy.context.selected_objects[0]
    ob.name = name
    ob.data.materials.clear()
    ob.data.materials.append(m)
    ob.location = loc
    if parent:
        ob.parent = parent
    return ob


stl("mag_osnova", "основа", mat("основа", (0.8, 0.8, 0.82, 1), 0.6))
stl("mag_ramka", "рамка катушек", mat("рамка", (0.9, 0.9, 0.92, 1), 0.5))
stl("mag_katushki_proverka", "8 катушек (провод 0.3, ~40 витков)", mat("катушки", (0.95, 0.55, 0.15, 1)))
sk = bpy.data.objects.new("скоба (едет)", None)
sc.collection.objects.link(sk)
stl("mag_skoba", "U-скоба с ложем", mat("скоба", (0.95, 0.95, 0.97, 1), 0.35), parent=sk)
stl("mag_magnity_proverka", "магниты 20×10×5", mat("магниты", (0.85, 0.15, 0.15, 1)), parent=sk)
stl("mag_stal_proverka", "стальные пластинки", mat("сталь", (0.45, 0.47, 0.5, 1)), parent=sk)
stl("mag_opravka_a", "оправка: щёчка с сердечником", mat("оправка", (0.25, 0.45, 0.80, 1)), loc=(0, -45, -10))
for f in range(1, FRAMES + 1, 2):
    sk.location = (22 * math.sin(2 * math.pi * (f - 1) / (FRAMES - 1)), 0, 0)
    sk.keyframe_insert("location", frame=f)


def camera(name, loc, target, lens):
    tgt = bpy.data.objects.new(name + " цель", None)
    sc.collection.objects.link(tgt)
    tgt.location = target
    c = bpy.data.objects.new(name, bpy.data.cameras.new(name))
    sc.collection.objects.link(c)
    c.data.clip_start, c.data.clip_end = 1, 10000
    c.data.lens = lens
    c.location = loc
    tc = c.constraints.new('TRACK_TO')
    tc.target = tgt
    tc.track_axis = 'TRACK_NEGATIVE_Z'
    tc.up_axis = 'UP_Y'
    return c


cam = camera("Камера: 3/4", (80, -110, 80), (0, -10, 8), 32)
camera("Камера: торец", (110, 0, 12), (0, 0, 12), 45)
sc.camera = cam
sun = bpy.data.objects.new("Солнце", bpy.data.lights.new("Солнце", "SUN"))
sun.data.energy = 3
sun.rotation_euler = (math.radians(35), math.radians(10), math.radians(40))
sc.collection.objects.link(sun)
sc.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("saved", OUT)
