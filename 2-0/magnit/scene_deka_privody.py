# -*- coding: utf-8 -*-
r"""Идея 08.10 (владелец): линейные приводы «стержень + катушка» (стол 89) лежат в ДЕКЕ вместо моторов и прямо
толкают ленты-спицы своих этажей вдоль грифа; у тележки ленту в поперечный ход переводит рычаг-уголок 1:1
(плечи 30 перпендикулярно: ход ленты s → ход тележки s, линейно). Гриф 50 мм — внутри только ленты и рычаги.
Анимация: ход ±22 (6 струн). Запуск: blender -b -P scene_deka_privody.py -> Дека_линейные_приводы.blend"""
import math
import os
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "Дека_линейные_приводы.blend")

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.unit_settings.system = "METRIC"
sc.unit_settings.scale_length = 0.001
sc.unit_settings.length_unit = "MILLIMETERS"


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


M_NECK = mat("гриф", (0.55, 0.38, 0.2, 1), 0.15)
M_DECK = mat("дека", (0.7, 0.6, 0.45, 1), 0.12)
M_ROD = mat("стержень", (0.55, 0.75, 0.95, 1))
M_CU = mat("катушка", (0.85, 0.42, 0.15, 1))
M_LEV = mat("рычаг", (0.3, 0.3, 0.3, 1))
M_TXT = mat("текст", (0.05, 0.05, 0.05, 1))
COL = [mat("палец %d" % i, c) for i, c in enumerate([(0.9, 0.3, 0.3, 1), (0.95, 0.65, 0.15, 1),
                                                      (0.3, 0.7, 0.35, 1), (0.3, 0.5, 0.95, 1)])]


def box(name, x0, x1, y0, y1, z0, z1, m, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    o = bpy.context.object
    o.name = name
    o.scale = (abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))
    o.data.materials.append(m)
    if parent:
        o.parent = parent
    return o


def bar(name, p0, p1, w, t, m, parent=None):
    """брусок от точки p0 до p1 (сечение w × t)"""
    dx, dy, dz = (p1[i] - p0[i] for i in range(3))
    L = math.sqrt(dx * dx + dy * dy + dz * dz)
    bpy.ops.mesh.primitive_cube_add(size=1, location=tuple((p0[i] + p1[i]) / 2 for i in range(3)))
    o = bpy.context.object
    o.name = name
    o.scale = (w, L, t)
    o.rotation_euler = (math.atan2(dz, math.hypot(dx, dy)), 0, -math.atan2(dx, dy))
    o.data.materials.append(m)
    if parent:
        o.parent = parent
    return o


def label(text, loc, size=6.0):
    bpy.ops.object.text_add(location=loc, rotation=(math.radians(50), 0, 0))
    t = bpy.context.object
    t.data.body = text
    t.data.size = size
    t.data.align_x = "CENTER"
    t.data.materials.append(M_TXT)


def empty(name, loc=(0, 0, 0)):
    e = bpy.data.objects.new(name, None)
    e.location = loc
    sc.collection.objects.link(e)
    return e


# ---- гриф и дека ----
box("Гриф 50 мм", -25, 25, 0, 300, -20, 0, M_NECK)
box("Дека", -95, 95, -170, 0, -62, 0, M_DECK)
label("ГРИФ 50 мм: внутри только ленты-этажи и рычаги", (0, 150, 30))
label("ДЕКА: 4 линейных привода (стол 89)", (0, -120, 30))

L = 30.0                                        # плечи рычага-уголка
FING = [  # (палец, x привода в деке, x полосы ленты в грифе, этаж z, y тележки, рычаг: +1 = плечо к ленте вправо)
    ("указательный", -66, -15, -4, 170, -1),
    ("средний", -22, -5, -8, 200, -1),
    ("безымянный", 22, 5, -12, 230, 1),
    ("мизинец", 66, 15, -16, 260, 1),
]
movers = []
for i, (name, xa, lane, zf, ycar, side) in enumerate(FING):
    m = COL[i]
    ZA, YC = -40.0, -104.0
    # привод: стержень неподвижно, катушка едет вдоль грифа
    box("%s: стержень (неподвижно)" % name, xa - 8.5, xa + 8.5, YC - 46.1, YC + 46.1, ZA - 8.5, ZA + 8.5, M_ROD)
    for s in (1, -1):
        box("стойка стержня", xa - 11, xa + 11, YC + s * 46.1 - (6 if s > 0 else 0), YC + s * 46.1 + (0 if s > 0 else 6),
            -62, ZA + 11, M_DECK)
    mv = empty("%s: катушка + лента (едут вдоль грифа)" % name)
    box("%s: катушка" % name, xa - 13, xa + 13, YC - 16.6, YC + 16.6, ZA - 13, ZA + 13, M_CU, mv)
    yfront = YC + 16.6
    bar("лента в деке", (xa, yfront, ZA + 9), (xa, -35, ZA + 9), 8, 2, m, mv)
    bar("лента: переход на этаж", (xa, -35, ZA + 9), (lane, -5, zf), 8, 2, m, mv)
    py = ycar + L                                # ось рычага
    bar("лента в грифе", (lane, -5, zf), (lane, py, zf), 8, 2, m, mv)
    movers.append(mv)
    # рычаг-уголок: ось (px, py); плечо A к ленте (по x), плечо B к тележке (по −y)
    px = lane - side * L
    lev = empty("%s: рычаг 1:1" % name, (px, py, zf))
    bar("плечо к ленте", (0, 0, 0), (side * L, 0, 0), 4, 2, M_LEV, lev)
    bar("плечо к тележке", (0, 0, 0), (0, -L, 0), 4, 2, M_LEV, lev)
    bpy.ops.mesh.primitive_cylinder_add(radius=2.5, depth=4, location=(px, py, zf))
    bpy.context.object.data.materials.append(M_LEV)
    car = empty("%s: тележка" % name, (px, ycar, 0))
    box("палубка тележки", -9, 9, -7, 7, 0, 3, m, car)
    for s in (1, -1):
        box("бортик", s * 9 - (2 if s > 0 else 0), s * 9 + (0 if s > 0 else 2), -7, 7, 3, 10, m, car)
    bar("штырь в тележку", (0, 0, zf), (0, 0, 0), 2.5, 2.5, M_LEV, car)
    movers.append((lev, car, side, px, mv))
    label(name, (lane, py + 12, 6), 4.5)

# ---- анимация: ход ленты s = 22·sin, рычаг θ = asin(s / L)·знак, тележка x = px ± s ----
sc.frame_start, sc.frame_end = 1, 160
for f in range(1, 161, 2):
    s = 22.0 * math.sin(2 * math.pi * (f - 1) / 160)
    for it in movers:
        if not isinstance(it, tuple):
            continue
        lev, car, side, px, mv = it
        mv.location.y = s
        mv.keyframe_insert("location", index=1, frame=f)
        th = math.asin(s / L) * (1 if side > 0 else -1)
        lev.rotation_euler.z = th
        lev.keyframe_insert("rotation_euler", index=2, frame=f)
        car.location.x = px + L * math.sin(th)
        car.keyframe_insert("location", index=0, frame=f)

bpy.ops.object.light_add(type="SUN", location=(0, 0, 300), rotation=(math.radians(30), math.radians(15), 0))
bpy.context.object.data.energy = 3.5
bpy.ops.object.camera_add(location=(260, -330, 300))
cam = bpy.context.object
tgt = empty("цель камеры", (0, 40, -20))
c = cam.constraints.new("TRACK_TO")
c.target = tgt
c.track_axis, c.up_axis = "TRACK_NEGATIVE_Z", "UP_Y"
cam.data.lens = 35
cam.data.clip_start, cam.data.clip_end = 1, 50000
sc.camera = cam
w = bpy.data.worlds.new("мир")
w.color = (0.92, 0.92, 0.9)
sc.world = w
for a in bpy.data.screens:
    pass
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("сохранено", OUT)
