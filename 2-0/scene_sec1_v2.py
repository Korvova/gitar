# -*- coding: utf-8 -*-
"""Сцена Blender «Гитара_секция1_v2.blend»: секция-1 v2 в сборе — 4 плиты стопки, палуба с
руслами, 4 плеча, 4 спицы, 4 тележки с ложем (шаг 26/25/24), секция-2 для масштаба.
Анимация: плечи качаются ±22.6° со сдвигом 90° по этажам, тележки ездят ±20 мм, спицы — вдоль.
Коллекции можно прятать (глаз в Outliner), чтобы заглянуть внутрь. Пробел — проиграть.

Запуск: "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" -b -P 2-0\scene_sec1_v2.py
"""
import math
import os
import bpy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "2-0", "Print", "Print")
OUT = os.path.join(ROOT, "2-0", "Гитара_секция1_v2.blend")

CARTS_Y = [16, 42, 67, 91]
AXES_Y = [y + 52 for y in CARTS_Y]
Z_FLOOR = [3, 8.4, 13.8, 19.2]
FLOOR, Z_DECK, DECK_T, LANE_X = 1.6, 23, 3, 10
SWING = 22.6
FRAMES = 96

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.unit_settings.system = 'METRIC'
sc.unit_settings.scale_length = 0.001
sc.unit_settings.length_unit = 'MILLIMETERS'
sc.frame_start, sc.frame_end = 1, FRAMES
MATS = {}


def mat(name, rgba):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = rgba
    m.diffuse_color = rgba
    return m


def coll(name):
    c = bpy.data.collections.new(name)
    sc.collection.children.link(c)
    return c


def imp(stl, name, loc, collection, color, rz=0.0):
    before = set(bpy.data.objects)
    bpy.ops.wm.stl_import(filepath=os.path.join(SRC, stl + ".stl"))
    ob = [o for o in bpy.data.objects if o not in before][0]
    ob.name = name
    for c in ob.users_collection:
        c.objects.unlink(ob)
    collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (0, 0, math.radians(rz))
    ob.data.materials.clear()
    ob.data.materials.append(color)
    return ob


C_PL = mat("плита", (0.80, 0.78, 0.74, 1))
C_DECK = mat("палуба", (0.70, 0.68, 0.64, 1))
C_ARM = mat("плечо", (0.25, 0.45, 0.80, 1))
C_SP = mat("спица", (0.85, 0.38, 0.18, 1))
CART_C = [mat("ложе_%d" % k, c) for k, c in enumerate(((0.35, 0.55, 0.95, 1), (0.95, 0.55, 0.25, 1),
                                                       (0.40, 0.75, 0.45, 1), (0.95, 0.78, 0.30, 1)))]
C_SEC2 = mat("секция-2", (0.60, 0.65, 0.72, 1))

c_pl = coll("Плиты стопки (дно + межэтажки)")
c_deck = coll("Палуба с руслами")
c_mech = coll("Плечи и спицы")
c_cart = coll("Тележки с ложем")
c_sec2 = coll("Секция-2 (для масштаба)")

imp("gs1_p0_base_v2", "дно", (0, 0, 0), c_pl, C_PL)
for k in (1, 2, 3):
    imp("gs1_p%d_mid_v2" % k, "межэтажка_%d" % k, (0, 0, Z_FLOOR[k] - FLOOR), c_pl, C_PL)
imp("gs1_p4_deck_v2", "палуба", (0, 0, Z_DECK), c_deck, C_DECK)
imp("gs2_base", "секция2_дно", (0, 160, 0), c_sec2, C_SEC2)

arms, spicas, carts = [], [], []
for k in range(4):
    arms.append(imp("gs1_arm%d_v2" % k, "плечо_%d" % k, (0, AXES_Y[k], Z_FLOOR[k] + 0.2), c_mech, C_ARM))
    spicas.append(imp("gs1_spica%d_v2" % k, "спица_%d" % k, (LANE_X, AXES_Y[k] - 4, Z_FLOOR[k] + 0.2), c_mech, C_SP))
    carts.append(imp("gs1_cart_lozhe_v2", "ложе_%d" % k, (0, CARTS_Y[k], Z_DECK + DECK_T), c_cart, CART_C[k]))

for f in range(1, FRAMES + 1, 2):
    for k in range(4):
        th = SWING * math.sin(2 * math.pi * (f - 1) / (FRAMES - 1) + k * math.pi / 2)
        r = math.radians(th)
        arms[k].rotation_euler = (0, 0, r)
        arms[k].keyframe_insert("rotation_euler", frame=f)
        carts[k].location.x = 52 * math.sin(r)
        carts[k].keyframe_insert("location", frame=f)
        spicas[k].location.y = AXES_Y[k] - 4 + LANE_X * math.sin(r)
        spicas[k].keyframe_insert("location", frame=f)

cam = bpy.data.objects.new("Камера", bpy.data.cameras.new("Камера"))
sc.collection.objects.link(cam)
cam.data.clip_start, cam.data.clip_end = 1, 10000
cam.location = (140, -60, 150)
cam.rotation_euler = (math.radians(52), 0, math.radians(125))
sc.camera = cam
sun = bpy.data.objects.new("Солнце", bpy.data.lights.new("Солнце", "SUN"))
sun.data.energy = 3
sun.rotation_euler = (math.radians(40), math.radians(20), math.radians(30))
sc.collection.objects.link(sun)
sc.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("saved", OUT)
