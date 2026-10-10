# -*- coding: utf-8 -*-
r"""Идея 10.10: спарник на 4 тележки — вид на гриф. Планки по этажам (ближняя к деке тележка — верхний этаж),
у каждой планки на конце ПАЛЕЦ вверх; у тележки внизу «лапа» с прорезью ВДОЛЬ грифа — палец планки ходит в ней.
Тележки на шаге 26/25/24 (V позиция). Диски обоих концов спарника — в деке (за кадром слева).
Полуоборот дисков: тележка поперёк ±20, конец планки вдоль грифа 0…−20 (к деке) — в лапе своей тележки.
Запуск: blender -b -P scene_sparnik_4.py -> Спарник_4_тележки.blend"""
import math
import os
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "Спарник_4_тележки.blend")
R = 20.0
CARS = [("указательный", 60.0), ("средний", 86.0), ("безымянный", 111.0), ("мизинец", 135.0)]
FLOOR = [-5.0, -10.0, -15.0, -20.0]              # низ планки на своём этаже
BAR_T, BAR_W, PIN_R = 1.6, 8.0, 2.5
FOOT_T, FOOT_L, FOOT_W = 1.6, 30.0, 10.0         # лапа тележки: прорезь вдоль грифа 0…−20 + запас
FRAMES = 200

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.unit_settings.system = "METRIC"
sc.unit_settings.scale_length = 0.001
sc.unit_settings.length_unit = "MILLIMETERS"
sc.frame_start, sc.frame_end = 1, FRAMES


def mat(name, rgba, alpha=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rgba
    b.inputs["Alpha"].default_value = alpha
    if alpha < 1:
        m.surface_render_method = "BLENDED"
    m.diffuse_color = (rgba[0], rgba[1], rgba[2], alpha)
    return m


def box(name, x0, x1, y0, y1, z0, z1, m, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    o = bpy.context.object
    o.name = name
    o.scale = (abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))
    o.data.materials.append(m)
    if parent:
        o.parent = parent
    return o


def cyl(name, x, y, z0, z1, r, m, parent=None):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=z1 - z0, location=(x, y, (z0 + z1) / 2), vertices=24)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(m)
    if parent:
        o.parent = parent
    return o


def empty(name):
    e = bpy.data.objects.new(name, None)
    sc.collection.objects.link(e)
    return e


def label(text, loc, size=4.0):
    bpy.ops.object.text_add(location=loc, rotation=(math.radians(55), 0, 0))
    t = bpy.context.object
    t.data.body = text
    t.data.size = size
    t.data.align_x = "CENTER"
    t.data.materials.append(M_TXT)


M_NECK = mat("гриф (прозрачный)", (0.55, 0.38, 0.2, 1), 0.12)
M_TXT = mat("текст", (0.05, 0.05, 0.05, 1))
COLS = [(0.9, 0.3, 0.3, 1), (0.95, 0.65, 0.15, 1), (0.3, 0.7, 0.35, 1), (0.3, 0.5, 0.95, 1)]

box("гриф 50 мм", -25, 25, -10, 175, -24, 0, M_NECK)
label("дека — диски спарников (за кадром)", (0, -30, 6), 5)

movers = []
for k, (name, cy) in enumerate(CARS):
    m = mat(name, COLS[k])
    zb = FLOOR[k]
    # планка: из деки (y −10) до пальца под своей тележкой; палец на конце вверх
    bar = empty("%s: планка (этаж %d)" % (name, k + 1))
    box("планка", -BAR_W / 2, BAR_W / 2, -10 - cy, 0, 0, BAR_T, m, bar)          # локально: палец в (0, 0)
    cyl("палец планки", 0, 0, BAR_T, BAR_T + FOOT_T + 0.6, PIN_R, m, bar)
    # тележка: площадка над грифом, штырь вниз до своей лапы, лапа с прорезью вдоль грифа
    car = empty("%s: тележка" % name)
    z_foot = zb + BAR_T + 0.3
    box("площадка", -10, 10, -7, 7, 0.5, 2.5, m, car)
    for s in (1, -1):
        box("бортик", s * 10 - (1.6 if s > 0 else 0), s * 10 + (0 if s > 0 else 1.6), -7, 7, 2.5, 7.5, m, car)
    box("штырь тележки", -2.5, 2.5, -2.5, 2.5, z_foot + FOOT_T, 0.5, m, car)
    foot_y0 = -R - PIN_R - 3                                                        # прорезь: палец ходит 0…−20
    box("лапа: бок", -FOOT_W / 2, -PIN_R - 0.3, foot_y0, 5, z_foot, z_foot + FOOT_T, m, car)
    box("лапа: бок", PIN_R + 0.3, FOOT_W / 2, foot_y0, 5, z_foot, z_foot + FOOT_T, m, car)
    box("лапа: торец", -FOOT_W / 2, FOOT_W / 2, 2.8, 5, z_foot, z_foot + FOOT_T, m, car)
    box("лапа: торец", -FOOT_W / 2, FOOT_W / 2, foot_y0, foot_y0 + 2.2, z_foot, z_foot + FOOT_T, m, car)
    label(name, (-34, cy, 3), 3.5)
    movers.append((bar, car, cy, zb))

# анимация: полуоборот дисков θ 180…360…180: поперёк x = R·cosθ (±20), вдоль y = R·sinθ (0…−20, к деке)
for f in range(1, FRAMES + 1):
    th = math.pi + math.pi * (1 - math.cos(2 * math.pi * (f - 1) / (FRAMES - 1))) / 2
    x, dy = R * math.cos(th), R * math.sin(th)
    for bar, car, cy, zb in movers:
        bar.location = (x, cy + dy, zb)
        bar.keyframe_insert("location", frame=f)
        car.location = (x, cy, 0)
        car.keyframe_insert("location", frame=f)

# проверка зазоров (аналитически): штырь тележки j проходит сквозь этажи выше своего; чужая планка там — до пальца + кольцо
worst = 99
for j, (_, cj) in enumerate(CARS):
    for k, (_, ck) in enumerate(CARS):
        if k < j:                                  # планка k — на этаже выше лапы тележки j: её конец ≤ ck + PIN_R + 0.3 (палец в лапе)
            gap = (cj - 2.5) - (ck + PIN_R)
            worst = min(worst, gap)
print("наименьший зазор вдоль грифа: конец чужой планки до штыря следующей тележки = %.1f мм" % worst)

tgt = empty("цель")
tgt.location = (0, 95, -8)
cam = bpy.data.objects.new("Камера", bpy.data.cameras.new("Камера"))
sc.collection.objects.link(cam)
cam.data.clip_start, cam.data.clip_end, cam.data.lens = 1, 50000, 35
cam.location = (150, -40, 110)
tc = cam.constraints.new("TRACK_TO")
tc.target, tc.track_axis, tc.up_axis = tgt, "TRACK_NEGATIVE_Z", "UP_Y"
sc.camera = cam
sun = bpy.data.objects.new("Солнце", bpy.data.lights.new("Солнце", "SUN"))
sun.data.energy = 3
sun.rotation_euler = (math.radians(30), math.radians(15), math.radians(30))
sc.collection.objects.link(sun)
sc.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("saved", OUT)
