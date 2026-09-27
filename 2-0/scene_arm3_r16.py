# -*- coding: utf-8 -*-
"""Сцена: секция-1 v2, этаж 3 с плечом R16 (gitara_arm3_r16.py) — плечо качается ±25°,
спица едет ±6.8, тележка ±22. Плита p3 и палуба прозрачные. Старое плечо R10 — серым для сравнения.
Запуск: blender -b -P 2-0\\scene_arm3_r16.py
"""
import math
import os
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "Print", "Print")
OUT = os.path.join(HERE, "Секция1_плечо3_R16.blend")
RS, LB, AX_Y, CART_Y = 16.0, 52.0, 143.0, 91.0
Z3, FLOOR, Z_DECK, DECK_T = 19.2, 1.6, 23.0, 3.0
PHI = math.degrees(math.asin(22 / LB))
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


def stl(fname, name, m, loc=(0, 0, 0)):
    bpy.ops.wm.stl_import(filepath=os.path.join(P, fname + ".stl"))
    ob = bpy.context.selected_objects[0]
    ob.name = name
    ob.data.materials.clear()
    ob.data.materials.append(m)
    ob.location = loc
    return ob


C_PLATE = mat("плита p3 (прозрачная)", (0.8, 0.8, 0.8, 1), 0.25)
C_DECK = mat("палуба (прозрачная)", (0.85, 0.82, 0.76, 1), 0.15)
C_ARM = mat("плечо R16", (0.25, 0.45, 0.80, 1))
C_OLD = mat("старое плечо R10", (0.5, 0.5, 0.5, 1), 0.35)
C_SP = mat("спица 3", (0.85, 0.38, 0.18, 1))
C_CART = mat("тележка", (0.95, 0.72, 0.30, 1))

stl("gs1_p3_mid_v2", "плита p3", C_PLATE, (0, 0, Z3 - FLOOR))
stl("gs1_p4_deck_v2", "палуба", C_DECK, (0, 0, Z_DECK))
arm = stl("gs1_arm3_r16", "плечо 3 R16", C_ARM, (0, AX_Y, Z3 + 0.2))
old = stl("gs1_arm3_v2", "старое плечо 3 (R10, для сравнения)", C_OLD, (0, AX_Y, Z3 + 0.2 - 0.01))
sp = stl("gs1_spica3_r16", "спица 3 (новая)", C_SP)
cart = stl("gs1_cart_v2", "тележка 3 (мизинец)", C_CART)
old.hide_render = True

for f in range(1, FRAMES + 1, 2):
    phi = PHI * math.sin(2 * math.pi * (f - 1) / (FRAMES - 1))
    t = math.radians(phi)
    for ob in (arm, old):
        ob.rotation_euler = (0, 0, t)
        ob.keyframe_insert("rotation_euler", frame=f)
    sp.location = (RS * math.cos(t), AX_Y + RS * math.sin(t), Z3 + 0.2)
    sp.keyframe_insert("location", frame=f)
    cart.location = (LB * math.sin(t), CART_Y, Z_DECK + DECK_T)
    cart.keyframe_insert("location", frame=f)


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


cam = camera("Камера: сверху", (40, 110, 230), (0, 120, 20), 40)
camera("Камера: сбоку", (110, 60, 90), (0, 125, 20), 35)
sc.camera = cam
sun = bpy.data.objects.new("Солнце", bpy.data.lights.new("Солнце", "SUN"))
sun.data.energy = 3
sun.rotation_euler = (math.radians(30), math.radians(15), math.radians(30))
sc.collection.objects.link(sun)
sc.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("saved", OUT)
