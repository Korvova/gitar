# -*- coding: utf-8 -*-
"""Сцена: стенд одного пальца (gitara_mini1.py) — кривошип R10 крутится полными оборотами,
лента ±10, плечо 36 : 18, ложе ±20. Дно, середина и палуба прозрачные.
Запуск: blender -b -P 2-0\\scene_mini1.py
"""
import math
import os
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "Print", "Print")
OUT = os.path.join(HERE, "Стенд_один_палец.blend")
CART_Y, LB, RS, AX, MY, R_CR = 16, 36.0, 18.0, 52.0, 80.0, 10.0
Z_RIB, Z_CEIL, Z_DECK, DECK_T, RUN = 3.2, 6.8, 21.0, 3.0, 2.9
FRAMES = 240

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


C_GLASS = mat("корпус (прозрачный)", (0.8, 0.8, 0.82, 1), 0.15)
C_DECK = mat("палуба (прозрачная)", (0.85, 0.82, 0.76, 1), 0.25)
C_ARM = mat("плечо 36:18", (0.25, 0.45, 0.80, 1))
C_RIB = mat("лента", (0.85, 0.38, 0.18, 1))
C_LZ = mat("ложе", (0.95, 0.72, 0.30, 1))
C_CR = mat("кривошип R10", (0.25, 0.45, 0.80, 1))
C_MOT = mat("мотор", (0.25, 0.27, 0.30, 1))

stl("mini1_base", "дно", C_GLASS)
stl("mini1_mid", "середина (потолок)", C_GLASS, (0, 0, Z_CEIL))
stl("mini1_deck", "палуба", C_DECK, (0, 0, Z_DECK))
stl("gdk_spacer0_v3", "проставка", C_MOT, (0, MY, 0))
stl("gdk_motor0_model", "мотор (указательный)", C_MOT, (0, MY, -4.0))
cr = stl("gdk_crank0_x2", "кривошип R10", C_CR, (0, MY, 0))
rib = stl("mini1_lenta", "лента", C_RIB, (0, AX, Z_RIB))
arm = stl("mini1_arm", "плечо", C_ARM, (0, AX, Z_RIB))
lz = stl("gs1_lozhe_v3", "ложе указательного", C_LZ, (0, CART_Y, Z_DECK + DECK_T - RUN))

for f in range(1, FRAMES + 1, 2):
    th = 2 * math.pi * 2 * (f - 1) / (FRAMES - 1)                  # 2 полных оборота за ролик
    u = R_CR * math.sin(th)
    phi = math.asin(u / RS)
    cr.rotation_euler = (0, 0, th)
    cr.keyframe_insert("rotation_euler", frame=f)
    rib.location.y = AX + u
    rib.keyframe_insert("location", index=1, frame=f)
    arm.rotation_euler = (0, 0, phi)
    arm.keyframe_insert("rotation_euler", frame=f)
    lz.location.x = LB * math.sin(phi)
    lz.keyframe_insert("location", index=0, frame=f)


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


cam = camera("Камера: сверху", (40, 30, 250), (0, 55, 10), 35)
camera("Камера: сбоку", (150, -60, 110), (0, 55, 5), 35)
sc.camera = cam
sun = bpy.data.objects.new("Солнце", bpy.data.lights.new("Солнце", "SUN"))
sun.data.energy = 3
sun.rotation_euler = (math.radians(30), math.radians(15), math.radians(30))
sc.collection.objects.link(sun)
sc.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("saved", OUT)
