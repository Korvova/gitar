# -*- coding: utf-8 -*-
"""Сцена Blender «Гитара_дека_v3.blend»: хребет деки v3 с моторами Ø36, кривошипы
на полный оборот (кулиса), ленты-хвосты, гребёнки «Е», проставка мотора 0,
секция-3 с лентами. Анимация: кривошипы крутятся на 360° со сдвигом 90° по этажам,
ленты ходят вперёд-назад. Пробел — проиграть.

Запуск (без открытия Blender):
  "C:\\Program Files\\Blender Foundation\\Blender 5.1\\blender.exe" -b -P 2-0\\scene_deka_v2.py
"""
import math
import os
import bpy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "2-0", "Print", "Print")
OUT = os.path.join(ROOT, "2-0", "Гитара_дека_v3.blend")

Z_FLOOR = [3, 8.4, 13.8, 19.2]
MY = [515, 565, 615, 678]
COMB_Y = (540, 590, 634)
LANE, R_CR = 10, 4.8
FLANGE_Z = [-4.0, 0.0, 0.0, 0.0]
FRAMES = 96

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.unit_settings.system = 'METRIC'
sc.unit_settings.scale_length = 0.001
sc.unit_settings.length_unit = 'MILLIMETERS'
sc.frame_start, sc.frame_end = 1, FRAMES

MATS = {}


def mat(name, rgba):
    if name in MATS:
        return MATS[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = rgba
    m.diffuse_color = rgba
    MATS[name] = m
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


C_BASE = mat("хребет", (0.78, 0.76, 0.72, 1))
C_MOT = mat("мотор", (0.25, 0.27, 0.30, 1))
C_CRANK = mat("кривошип", (0.25, 0.45, 0.80, 1))
C_TAIL = mat("хвост ленты", (0.85, 0.38, 0.18, 1))
C_EXT = mat("лента", (0.90, 0.62, 0.40, 1))
C_COMB = mat("гребёнка", (0.35, 0.62, 0.38, 1))
C_SEC = mat("секция-3", (0.85, 0.84, 0.80, 1))
C_TRAY = mat("рейка", (0.60, 0.65, 0.72, 1))

c_deka = coll("Дека v3")
c_mot = coll("Моторы Ø36 (модель)")
c_mech = coll("Кривошипы и хвосты")
c_sec = coll("Секция-3 с лентами")

imp("gdk1_base_v3", "Д1_хребет", (0, 480, 0), c_deka, C_BASE)
imp("gdk2_base_v3", "Д2_хребет", (0, 640, 0), c_deka, C_BASE)
imp("gdk_spacer0_v3", "проставка_мотора_0", (0, MY[0], 0), c_deka, C_COMB)
for i, yg in enumerate(COMB_Y):
    imp("gdk_comb_v3", f"гребёнка_{i}", (0, yg, 0), c_deka, C_COMB)
    imp("gdk_comb_key_v3", f"фиксатор_гребёнки_{i}", (0, yg, 0), c_deka, C_TRAY)
for k, my in enumerate(MY):
    imp(f"gdk_motor{k}_model", f"мотор_{k}", (0, my, FLANGE_Z[k]), c_mot, C_MOT)

imp("gs3_base", "секция3_дно", (0, 320, 0), c_sec, C_SEC)
for k, zf in enumerate(Z_FLOOR):
    imp("gs2_tray", f"секция3_рейка_{k}", (0, 320, zf - 1.6), c_sec, C_TRAY)

cranks, tails, exts = [], [], []
for k, (my, zf) in enumerate(zip(MY, Z_FLOOR)):
    cranks.append(imp(f"gdk_crank{k}_v3", f"кривошип_{k}", (0, my, 0), c_mech, C_CRANK))
    tails.append(imp(f"gdk_tail{k}_v3", f"хвост_{k}", (LANE, 480, zf + 0.05), c_mech, C_TAIL))
    exts.append(imp("gdk_ext", f"лента_секция3_{k}", (LANE, 320, zf + 0.05), c_sec, C_EXT))

# анимация: полный оборот, этажи со сдвигом 90°
for f in range(1, FRAMES + 1, 2):
    for k in range(4):
        th = 360.0 * (f - 1) / (FRAMES - 1) + 90 * k
        dy = R_CR * math.sin(math.radians(th))
        cranks[k].rotation_euler = (0, 0, math.radians(th))
        cranks[k].keyframe_insert("rotation_euler", frame=f)
        for ob, y0 in ((tails[k], 480), (exts[k], 320)):
            ob.location.y = y0 + dy
            ob.keyframe_insert("location", frame=f)

# камера и свет
cam = bpy.data.objects.new("Камера", bpy.data.cameras.new("Камера"))
sc.collection.objects.link(cam)
cam.data.clip_start, cam.data.clip_end = 1, 10000
cam.location = (-190, 470, 170)
cam.rotation_euler = (math.radians(58), 0, math.radians(-118))
sc.camera = cam
sun = bpy.data.objects.new("Солнце", bpy.data.lights.new("Солнце", "SUN"))
sun.data.energy = 3
sun.rotation_euler = (math.radians(40), math.radians(20), math.radians(30))
sc.collection.objects.link(sun)
sc.frame_set(1)

bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("saved", OUT)
