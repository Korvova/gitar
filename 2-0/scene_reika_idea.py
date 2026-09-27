# -*- coding: utf-8 -*-
"""Концепт «рейка 1:1» для верхнего этажа (обсуждение с владельцем 27.09).

Цепочка: мотор (вал вертикально) → шестерня Ø29 → лента с зубьями на боковом краю (рейка) →
в секции-1 шестерня Ø16 с двумя венцами на одной оси: нижний венец цепляет рейку ленты,
верхний (над палубой) — рейку тележки, повёрнутую на 90°. Лента и тележка ходят 1:1 и равномерно:
пол-оборота мотора = 45 мм ленты = 45 мм тележки. Плеча, штыря и мёртвых точек нет.

Расстояние от секции-1 до деки в сцене укорочено (на самом деле мотор этажа 3 на y = 678).
Модуль зубьев m = 1. Запуск: blender -b -P 2-0\\scene_reika_idea.py
"""
import math
import os
import bmesh
import bpy

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Идея_рейка_1к1.blend")
M = 1.0                       # модуль зубьев
Z1, R1 = 29, 14.5             # шестерня на моторе: Ø29 → пол-оборота = 45.5 мм
Z2, R2 = 16, 8.0              # шестерня в секции-1: Ø16
ZF, T = 19.25, 1.6            # этаж 3: низ ленты и толщина
Z_DECK_TOP = 26.0
LANE_W = (6.0, 14.0)          # лента по x
G2 = (-2.0, 40.0)             # ось шестерни секции-1: x = край ленты (6) − R2
MOT = (6.0 - R1, 300.0)       # ось мотора (укорочено): x = край ленты − R1
FRAMES = 120
SWING = 90.0                  # мотор ± 90° = пол-оборота в каждую сторону от середины

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
    if alpha < 1.0:
        b.inputs["Alpha"].default_value = alpha
        m.blend_method = 'BLEND' if hasattr(m, "blend_method") else None
    m.diffuse_color = (rgba[0], rgba[1], rgba[2], alpha)
    return m


def mesh_obj(name, verts2d, z0, h, m, loc=(0, 0, 0)):
    """Призма из 2D-контура (по часовой/против — неважно), высота h от z0."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bot = [bm.verts.new((x, y, z0)) for x, y in verts2d]
    top = [bm.verts.new((x, y, z0 + h)) for x, y in verts2d]
    bm.faces.new(bot[::-1])
    bm.faces.new(top)
    n = len(verts2d)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((bot[i], bot[j], top[j], top[i]))
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    sc.collection.objects.link(ob)
    ob.location = loc
    ob.data.materials.append(m)
    return ob


def gear2d(z, r, m=M):
    ra, rf = r + m, r - 1.25 * m
    pts = []
    for i in range(z):
        a = 2 * math.pi * i / z
        p = math.pi / z
        for da, rr in ((-p * 0.95, rf), (-p * 0.35, ra), (p * 0.35, ra), (p * 0.95, rf)):
            pts.append((rr * math.cos(a + da), rr * math.sin(a + da)))
    return pts


def rack2d_y(x_edge, y0, y1, side, m=M):
    """Рейка вдоль Y: сплошная полоса от x_edge внутрь (side = +1: тело к +x), зубья наружу."""
    pitch = math.pi * m
    body = 3.0
    pts = [(x_edge + side * body, y0), (x_edge + side * body, y1)]
    y = y1
    teeth = []
    while y - pitch >= y0:
        yc = y - pitch / 2
        teeth += [(x_edge, y), (x_edge, yc + pitch * 0.3), (x_edge - side * 2.25 * m, yc + pitch * 0.15),
                  (x_edge - side * 2.25 * m, yc - pitch * 0.15), (x_edge, yc - pitch * 0.3)]
        y -= pitch
    pts += teeth + [(x_edge, y0)]
    return pts


def rack2d_x(y_edge, x0, x1, side, m=M):
    pts = [(x, y) for (y, x) in rack2d_y(y_edge, x0, x1, side, m)]
    return pts[::-1]


C_DECK = mat("палуба (прозрачная)", (0.85, 0.82, 0.76, 1), 0.35)
C_LENT = mat("лента с зубьями", (0.85, 0.38, 0.18, 1))
C_G1 = mat("шестерня мотора", (0.25, 0.45, 0.80, 1))
C_G2 = mat("шестерня секции-1", (0.35, 0.62, 0.38, 1))
C_CART = mat("тележка с рейкой", (0.95, 0.72, 0.30, 1))
C_MOT = mat("мотор", (0.25, 0.27, 0.30, 1))
C_FLOOR = mat("пол этажа", (0.75, 0.75, 0.75, 1), 0.5)

# палуба секции-1 (прозрачная) и пол этажа 3 — для ориентира
mesh_obj("палуба секции-1", [(-26, 0), (26, 0), (26, 160), (-26, 160)], 23.0, 3.0, C_DECK)
mesh_obj("пол этажа 3", [(-26, 0), (26, 0), (26, 330), (-26, 330)], ZF - 1.6, 1.4, C_FLOOR)

# лента этажа 3: полоса + рейки на западном краю (у секции-1 и у мотора)
lent = mesh_obj("лента этажа 3", [(LANE_W[0], 10), (LANE_W[1], 10), (LANE_W[1], 330), (LANE_W[0], 330)], ZF, T, C_LENT)
for nm, (y0, y1) in (("рейка ленты у секции-1", (10, 75)), ("рейка ленты у мотора", (260, 330))):
    r = mesh_obj(nm, rack2d_y(LANE_W[0], y0, y1, +1), ZF, T, C_LENT)
    r.parent = lent

# мотор и его шестерня Ø29
bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=18.25, depth=22, location=(MOT[0], MOT[1], ZF - 3 - 11), rotation=(0, 0, 0))
bpy.context.object.name = "мотор Ø36"
bpy.context.object.data.materials.append(C_MOT)
g1 = mesh_obj("шестерня мотора Ø29 (z29)", gear2d(Z1, R1), ZF, T, C_G1, loc=(MOT[0], MOT[1], 0))

# шестерня секции-1: два венца на одной оси (нижний — лента, верхний над палубой — тележка)
g2 = mesh_obj("шестерня секции-1, нижний венец (z16)", gear2d(Z2, R2), ZF, T, C_G2, loc=(G2[0], G2[1], 0))
g2top = mesh_obj("шестерня секции-1, верхний венец", gear2d(Z2, R2), Z_DECK_TOP + 0.5, T, C_G2, loc=(G2[0], G2[1], 0))
g2top.parent = g2
g2top.location = (0, 0, 0)
bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=2.5, depth=Z_DECK_TOP + 2.5 - ZF + 1, location=(0, 0, (ZF + Z_DECK_TOP + 2.1) / 2), rotation=(0, 0, 0))
ax = bpy.context.object
ax.name = "ось шестерни (сквозь палубу)"
ax.data.materials.append(C_G2)
ax.parent = g2

# тележка: рейка вдоль X (зубья к шестерне, на юг от неё не мешает) + ложе
cart = mesh_obj("рейка тележки", rack2d_x(G2[1] + R2, -40, 40, +1), Z_DECK_TOP + 0.5, T, C_CART)
lozhe = mesh_obj("ложе пальца", [(-12, G2[1] + R2 + 3), (12, G2[1] + R2 + 3), (12, G2[1] + R2 + 18), (-12, G2[1] + R2 + 18)],
                 Z_DECK_TOP + 0.5, 6, C_CART)
lozhe.parent = cart

# анимация: мотор ±90° → лента ±R1·φ → шестерня секции-1 → тележка ±R1·φ (1:1)
for f in range(1, FRAMES + 1, 2):
    phi = math.radians(SWING) * math.sin(2 * math.pi * (f - 1) / (FRAMES - 1))
    dy = R1 * phi
    g1.rotation_euler = (0, 0, phi)
    g1.keyframe_insert("rotation_euler", frame=f)
    lent.location = (0, -dy, 0)
    lent.keyframe_insert("location", frame=f)
    psi = dy / R2
    g2.rotation_euler = (0, 0, -psi)
    g2.keyframe_insert("rotation_euler", frame=f)
    cart.location = (dy, 0, 0)
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


cam = camera("Камера: общий вид", (230, 60, 230), (0, 165, 12), 32)
camera("Камера: секция-1 крупно", (95, -45, 95), (0, 40, 22), 40)
sc.camera = cam
sun = bpy.data.objects.new("Солнце", bpy.data.lights.new("Солнце", "SUN"))
sun.data.energy = 3
sun.rotation_euler = (math.radians(40), math.radians(20), math.radians(30))
sc.collection.objects.link(sun)
sc.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("saved", OUT)
