# -*- coding: utf-8 -*-
r"""Сцена-эскиз: 4 тележки стола 114 (шаг моторов 30) со смещённым ложем — идея владельца 06.11: моторы стоят как им удобно,
площадка под палец на каждой тележке сдвинута вдоль грифа на своё расстояние, шаг пальцев 24. Сдвиги ±3 и ±9.
Площадка и стойки под ней нарисованы только здесь, на печать пока не выведены. Пробел — анимация (тележки ходят независимо).
Запуск: blender -b -P 2-0\kasseta\scene_4_telezhki_lozhe.py"""
import math
import os
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
P_STL = os.path.join(HERE, "..", "Print", "Print")
OUT = os.path.join(HERE, "Гриф_смещённое_ложе.blend")
RP = 6.0
FR = 240
PITCH_M = 30.0                         # шаг моторов и тележек
PITCH_F = 24.0                         # шаг пальцев
PAD_Y, PAD_X = 22.0, 24.0              # площадка вдоль и поперёк грифа
Z_TOP, Z_PAD0, Z_PAD1 = 17.7, 20.9, 22.4   # крыша; площадка над головками винтов (их верх 20.8)
HY = 14.7
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


def stl(fname, name, m, y=0.0):
    bpy.ops.wm.stl_import(filepath=os.path.join(P_STL, fname + ".stl"))
    ob = bpy.context.selected_objects[0]
    ob.name = name
    ob.data.materials.clear()
    ob.data.materials.append(m)
    ob.location = (0, y, 0)
    return ob


def box(name, x0, x1, y0, y1, z0, z1, m):
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    ob = bpy.context.object
    ob.name = name
    ob.scale = (x1 - x0, y1 - y0, z1 - z0)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    ob.data.materials.append(m)
    bpy.ops.object.select_all(action='DESELECT')
    return ob


BLK = mat("чёрный", (0.06, 0.06, 0.07, 1))
SVET = mat("кубик", (0.86, 0.83, 0.77, 1), 0.55)
NIZ = mat("низ", (0.75, 0.72, 0.66, 1))
PLA = mat("пластина", (0.65, 0.62, 0.56, 1))
M_G = mat("шестерня", (0.95, 0.55, 0.15, 1))
M_F = mat("фланец", (0.9, 0.75, 0.25, 1))
M_M = mat("мотор", (0.12, 0.12, 0.14, 1))
PAD = mat("ложе под палец", (0.10, 0.25, 0.75, 1))
ST = mat("стойки ложа", (0.25, 0.40, 0.80, 1))
carts = []
for i in range(4):
    y0 = (i - 1.5) * PITCH_M
    yf = (i - 1.5) * PITCH_F           # где должен быть палец
    d = yf - y0                        # сдвиг площадки от центра тележки
    stl("gt_platforma", "платформа %d" % (i + 1), BLK, y0)
    stl("gt_kryshka_reiki", "планка над зубьями %d" % (i + 1), BLK, y0)
    cart = [stl("gt_kubik", "кубик %d" % (i + 1), SVET, y0), stl("gt_niz", "низ %d" % (i + 1), NIZ, y0), stl("gt_plastina", "пластина %d" % (i + 1), PLA, y0)]
    y_a, y_b = yf - PAD_Y / 2, yf + PAD_Y / 2
    cart.append(box("ложе %d (сдвиг %+.0f мм)" % (i + 1, d), -PAD_X / 2, PAD_X / 2, y_a, y_b, Z_PAD0, Z_PAD1, PAD))
    s_a, s_b = max(y_a, y0 - HY + 1), min(y_b, y0 + HY - 1)    # стойки только над тележкой
    for sx in (1, -1):
        x0, x1 = sorted((sx * 9.5, sx * 12.0))
        cart.append(box("стойка ложа %d" % (i + 1), x0, x1, s_a, s_b, Z_TOP, Z_PAD0 + 0.01, ST))
    rot = [stl("gt_shesternya", "шестерня %d" % (i + 1), M_G, y0), stl("gt_flanec", "фланец %d" % (i + 1), M_F, y0)]
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=13.9, depth=12.23, location=(0, 0, 4.02 + 12.23 / 2))
    motor = bpy.context.object
    motor.name = "мотор %d" % (i + 1)
    motor.data.materials.append(M_M)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    motor.location = (0, y0, 0)
    bpy.ops.object.select_all(action='DESELECT')
    rot.append(motor)
    carts.append((cart, rot, y0, 0.13 * i, [ob.location.y for ob in cart]))

for f in range(1, FR + 1):
    t = (f - 1) / (FR - 1)
    for k, (cart, rot, y0, ph, ys) in enumerate(carts):
        c = 22.0 * math.sin(2 * math.pi * (t + ph) * (1 if k % 2 else 2))
        for ob, y in zip(cart, ys):
            ob.location = (c, y, 0)
            ob.keyframe_insert("location", index=0, frame=f)
        for ob in rot:
            ob.location = (c, y0, 0)
            ob.rotation_euler = (0, 0, c / RP)
            ob.keyframe_insert("location", index=0, frame=f)
            ob.keyframe_insert("rotation_euler", index=2, frame=f)
tgt = bpy.data.objects.new("цель", None)
sc.collection.objects.link(tgt)
tgt.location = (0, 0, 8)
cam = bpy.data.objects.new("Камера", bpy.data.cameras.new("Камера"))
sc.collection.objects.link(cam)
cam.data.clip_start, cam.data.clip_end, cam.data.lens = 1, 50000, 50
cam.location = (130, -130, 130)
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
print("сцена со смещённым ложем сохранена")
