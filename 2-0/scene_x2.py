# -*- coding: utf-8 -*-
"""Симуляция: весь гриф в режиме ×2 (27.09.2026) — дека ×2 (кривошипы R15 рычажком) + ленты через
секции 2–3 + секция-1 v3 (плечо 36 : 18) + 4 ложа. Каждый палец ходит своим ритмом.
Цепочка: кривошип θ → лента u = −15·sin θ → плечо sin φ = u / 18 → ложе x = 36·sin φ = 2u.
Детали — из Print/Print (gitara_deka.py с DEKA_X2=1, gitara_sec1_v3.py). Секции 2–3 — прозрачным брусом.
Запуск: blender -b -P 2-0\\scene_x2.py
"""
import math
import os
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "Print", "Print")
OUT = os.path.join(HERE, "Гриф_x2.blend")
FRAMES = 240

# секция-1 v3
LB, RS = 36.0, 18.0
CARTS_Y = [16, 42, 67, 91]
AXES_Y = [y + LB for y in CARTS_Y]
Z_FLOOR = [3, 8.4, 13.8, 19.2]
FLOOR, Z_DECK, DECK_T, RUN = 1.6, 23.0, 3.0, 2.9
# дека ×2
R_CR, LANE, DK_Y0 = 15.0, 10.0, 480.0
MY = [515, 565, 615, 678]
FLANGE_Z = [-4.0, 0.0, 0.0, 0.0]
COMB_Y = (540, 590, 634)
TH_MAX = math.degrees(math.asin(10 / R_CR))      # ложе ±20 → лента ±10 → кривошип ±41.8°
FINGER = ["мизинец", "безымянный", "средний", "указательный"]   # этаж 3..0 → палец; этаж k = FINGER[3 − k]

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


def box(name, x0, x1, y0, y1, z0, z1, m):
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), rotation=(0, 0, 0))
    ob = bpy.context.object
    ob.name = name
    ob.scale = (x1 - x0, y1 - y0, z1 - z0)
    ob.data.materials.append(m)
    return ob


C_GLASS = mat("плиты (прозрачные)", (0.8, 0.8, 0.82, 1), 0.12)
C_DECK = mat("палуба (прозрачная)", (0.85, 0.82, 0.76, 1), 0.2)
C_NECK = mat("секции 2–3 (прозрачные)", (0.85, 0.82, 0.76, 1), 0.06)
C_ARM = mat("плечи 36:18", (0.25, 0.45, 0.80, 1))
C_RIB = [mat("лента этаж %d" % k, c) for k, c in enumerate(
    [(0.85, 0.38, 0.18, 1), (0.30, 0.65, 0.35, 1), (0.60, 0.35, 0.75, 1), (0.90, 0.75, 0.20, 1)])]
C_LOZHE = mat("ложа", (0.95, 0.72, 0.30, 1))
C_CRANK = mat("кривошипы R15", (0.25, 0.45, 0.80, 1))
C_MOT = mat("моторы", (0.25, 0.27, 0.30, 1))
C_COMB = mat("гребёнки", (0.55, 0.55, 0.6, 1))

# секция-1 v3
stl("gs1_p0_base_v3", "секция-1: дно", C_GLASS)
for k in (1, 2, 3):
    stl("gs1_p%d_mid_v3" % k, "секция-1: плита %d" % k, C_GLASS, (0, 0, Z_FLOOR[k] - FLOOR))
stl("gs1_p4_deck_v3", "секция-1: палуба", C_DECK, (0, 0, Z_DECK))
# секции 2–3 — прозрачный брус
box("секции 2–3 (условно)", -26, 26, 160, 480, 0, 23, C_NECK)
# дека ×2
stl("gdk1_base_x2", "дека Д1 (×2: окно рычажка 0)", C_GLASS, (0, DK_Y0, 0))
stl("gdk2_base_v3", "дека Д2", C_GLASS, (0, 640, 0))
stl("gdk_spacer0_v3", "проставка мотора 0", C_COMB, (0, MY[0], 0))
for i, yg in enumerate(COMB_Y):
    stl("gdk_comb_v3", "гребёнка %d" % i, C_COMB, (0, yg, 0))

arms, spicas, lozhes, cranks, tails, mids = [], [], [], [], [], []
for k in range(4):
    who = FINGER[3 - k]
    z = Z_FLOOR[k] + 0.2
    arms.append(stl("gs1_arm%d_v3" % k, "плечо %d (%s)" % (k, who), C_ARM, (0, AXES_Y[k], z)))
    spicas.append(stl("gs1_spica%d_v3" % k, "спица %d" % k, C_RIB[k], (0, AXES_Y[k], z)))
    lozhes.append(stl("gs1_lozhe_v3", "ложе %d — %s" % (k, who), C_LOZHE, (0, CARTS_Y[k], Z_DECK + DECK_T - RUN)))
    mids.append(box("лента %d через секции 2–3" % k, LANE - 4, LANE + 4, 178, 480, Z_FLOOR[k] + 0.05, Z_FLOOR[k] + 1.65, C_RIB[k]))
    stl("gdk_motor%d_model" % k, "мотор %d (%s)" % (k, who), C_MOT, (0, MY[k], FLANGE_Z[k]))
    cranks.append(stl("gdk_crank%d_x2" % k, "кривошип %d R15" % k, C_CRANK, (0, MY[k], 0)))
    tails.append(stl("gdk_tail%d_x2" % k, "хвост %d" % k, C_RIB[k], (LANE, DK_Y0, Z_FLOOR[k] + 0.05)))
bpy.context.view_layer.update()

# ритм: каждый палец прыгает по струнам своим темпом (кривошип ±41.8° = ложе ±20)
SPEED = [1.0, 1.5, 0.75, 2.0]
PHASE = [0.0, 0.8, 1.9, 2.7]
for f in range(1, FRAMES + 1, 2):
    t = (f - 1) / (FRAMES - 1)
    for k in range(4):
        th = math.radians(TH_MAX) * math.sin(2 * math.pi * SPEED[k] * t + PHASE[k])
        u = -R_CR * math.sin(th)                       # лента
        phi = math.asin(u / RS)
        cranks[k].rotation_euler = (0, 0, th)
        cranks[k].keyframe_insert("rotation_euler", frame=f)
        for ob, y0 in ((tails[k], DK_Y0), (mids[k], (178 + 480) / 2), (spicas[k], AXES_Y[k])):
            ob.location.y = y0 + u
            ob.keyframe_insert("location", index=1, frame=f)
        arms[k].rotation_euler = (0, 0, phi)
        arms[k].keyframe_insert("rotation_euler", frame=f)
        lozhes[k].location.x = LB * math.sin(phi)
        lozhes[k].keyframe_insert("location", index=0, frame=f)


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


cam = camera("Камера: весь гриф", (260, 150, 420), (0, 400, 10), 28)
camera("Камера: секция-1 сверху", (30, 70, 230), (0, 75, 20), 40)
camera("Камера: дека сверху", (30, 600, 220), (0, 600, 10), 40)
sc.camera = cam
sun = bpy.data.objects.new("Солнце", bpy.data.lights.new("Солнце", "SUN"))
sun.data.energy = 3
sun.rotation_euler = (math.radians(30), math.radians(15), math.radians(30))
sc.collection.objects.link(sun)
sc.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("saved", OUT)
