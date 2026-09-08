# -*- coding: utf-8 -*-
"""ДЕМО «ГИБКИЙ ПРУТОК» (идея юзера): два прутка в каналах с плавными
дугами толкают/тянут тележку с центра; большой вал наматывает их упруго.
Запуск: blender -b -P flex_demo.py
- пруток A: от центра тележки на север, дуга R15, канал на восток, ложится
  на вал сверху; пруток B — зеркально снизу;
- вал крутится: один пруток выталкивается из канала, другой втягивается,
  тележка ездит +-20; концы на ободе — «ключи» (красные бобышки);
- прутки показаны как трубки, скользящие по своим каналам (серые направляющие).
"""
import bpy, math, mathutils

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.fps = 24
sc.frame_start, sc.frame_end = 1, 120

XL = 40.0                 # дорожка тележки
RARC = 15.0               # радиус дуги канала
YCH = 30.0                # каналы (демо-гриф широкий, концепт)
DCX, DCY, RD = 175.0, 0.0, 30.0   # вал
ZR = 2.0                  # высота прутков
RODL = 190.0              # длина прутка


def mat(name, rgba):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = rgba
    return m

M_BASE = mat("base", (0.62, 0.62, 0.62, 1))
M_CART = mat("cart", (0.8, 0.8, 0.82, 1))
M_GUIDE = mat("guide", (0.45, 0.45, 0.48, 1))
M_RODA = mat("rodA", (0.85, 0.25, 0.15, 1))
M_RODB = mat("rodB", (0.15, 0.45, 0.85, 1))
M_GOLD = mat("gold", (0.78, 0.65, 0.22, 1))
M_KEY = mat("key", (0.9, 0.1, 0.1, 1))


def rod_z(sg):
    return 2.0 if sg > 0 else 3.4


def path_pts(sg):
    """Полный путь прутка sg=+1 (A, север) от (XL, -20*sg... старт у тележки)
    до максимальной намотки на вал. Шаг ~2 мм, равномерно."""
    pts = []
    # 1) дорожка: от самого южного положения конца (cy=-20) на север
    y0, y1 = -20.0 * 1, (YCH - RARC)
    # параметризуем: для A конец идёт от y=-20 до +... вдоль x=XL
    yy = -20.0
    while yy < y1:
        pts.append((XL, sg * max(yy, -20.0) if False else (yy if sg > 0 else -yy), ZR))
        yy += 2.0
    # честно: для A путь: (XL, y) y от -20 до YCH-RARC; для B зеркально
    pts = []
    yy = -20.0 * sg
    step = 2.0 * sg
    while (yy * sg) < (YCH - RARC):
        pts.append((XL, yy, rod_z(sg)))
        yy += step
    # 2) дуга R15: центр (XL+RARC, sg*(YCH-RARC)), от 180° к 90° (для A)
    cx, cy = XL + RARC, sg * (YCH - RARC)
    n = 12
    for i in range(n + 1):
        a = math.radians(180 - 90 * i / n)
        pts.append((cx + RARC * math.cos(a), cy + sg * RARC * math.sin(a), rod_z(sg)))
    # 3) канал вдоль y=sg*YCH до касания вала
    xx = cx + RARC + 2
    while xx < DCX:
        pts.append((xx, sg * YCH, rod_z(sg)))
        xx += 2.0
    # 4) намотка на вал: от касания (сверху для A) по восточной стороне
    n = 40
    for i in range(n + 1):
        a = math.radians(90 * sg - sg * 110 * i / n)
        pts.append((DCX + RD * math.cos(a), DCY + RD * math.sin(a), rod_z(sg)))
    return pts


def curve_obj(name, pts, m, bevel):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = bevel
    cu.bevel_factor_mapping_start = 'SPLINE'
    cu.bevel_factor_mapping_end = 'SPLINE'
    spl = cu.splines.new('POLY')
    spl.points.add(len(pts) - 1)
    for p, (x, y, z) in zip(spl.points, pts):
        p.co = (x, y, z, 1)
    ob = bpy.data.objects.new(name, cu)
    ob.data.materials.append(m)
    sc.collection.objects.link(ob)
    return ob


# ---- основание ----
def box(name, x0, x1, y0, y1, z0, z1, m):
    bpy.ops.mesh.primitive_cube_add()
    ob = bpy.context.object
    ob.name = name
    ob.scale = ((x1 - x0) / 2, (y1 - y0) / 2, (z1 - z0) / 2)
    ob.location = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    ob.data.materials.append(m)
    return ob

box("Neck", 0, 130, -36, 36, 0, 1.0, M_BASE)
box("Deck", 130, 240, -60, 60, 0, 1.0, M_BASE)

# ---- вал ----
disc_e = bpy.data.objects.new("Val", None)
disc_e.location = (DCX, DCY, 0)
sc.collection.objects.link(disc_e)
bpy.ops.mesh.primitive_cylinder_add(radius=RD, depth=3, location=(DCX, DCY, 2.5))
disc = bpy.context.object
disc.data.materials.append(M_GOLD)
disc.parent = disc_e
disc.matrix_parent_inverse = disc_e.matrix_world.inverted()
# «ключи» — точки крепления прутков на ободе
for sg, nm in ((1, 'A'), (-1, 'B')):
    a = math.radians(sg * (90 - math.degrees((RODL - 158.6) / RD)))
    bpy.ops.mesh.primitive_cylinder_add(radius=1.6, depth=3,
        location=(DCX + RD * math.cos(a), DCY + RD * math.sin(a), 4.5))
    k = bpy.context.object
    k.name = "Key%s" % nm
    k.data.materials.append(M_KEY)
    k.parent = disc_e
    k.matrix_parent_inverse = disc_e.matrix_world.inverted()

# ---- тележка ----
cart = box("Cart", XL - 8, XL + 8, -8, 8, 4.0, 11.0, M_CART)

# ---- каналы (направляющие, тонкие серые) и прутки (толстые цветные) ----
PL = {}
for sg, nm, mrod in ((1, 'A', M_RODA), (-1, 'B', M_RODB)):
    pts = path_pts(sg)
    curve_obj("Guide%s" % nm, pts, M_GUIDE, 0.5)
    rod = curve_obj("Rod%s" % nm, pts, mrod, 1.1)
    # длина пути (примерно, по точкам)
    total = 0.0
    for i in range(1, len(pts)):
        total += (mathutils.Vector(pts[i]) - mathutils.Vector(pts[i - 1])).length
    PL[nm] = (rod, total)

# ---- анимация ----
for fr in range(1, 121):
    t = 2 * math.pi * (fr - 1) / 120.0
    cy = 20.0 * math.sin(t)
    cart.location = (XL, cy, 7.5)
    cart.keyframe_insert("location", frame=fr)
    disc_e.rotation_euler = (0, 0, -cy / RD)
    disc_e.keyframe_insert("rotation_euler", frame=fr)
    for sg, nm in ((1, 'A'), (-1, 'B')):
        rod, total = PL[nm]
        # конец прутка у тележки: пройдено от старта пути (cy=-20 для A)
        off = (cy + 20.0) if sg > 0 else (20.0 - cy)
        rod.data.bevel_factor_start = max(off / total, 0.0)
        rod.data.bevel_factor_end = min((off + RODL) / total, 1.0)
        rod.data.keyframe_insert("bevel_factor_start", frame=fr)
        rod.data.keyframe_insert("bevel_factor_end", frame=fr)

# ---- свет, камера ----
bpy.ops.object.light_add(type='SUN', location=(80, -60, 130))
bpy.context.object.data.energy = 4
bpy.context.object.rotation_euler = (math.radians(32), math.radians(10), 0)
w = bpy.data.worlds.new("W")
w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.92, 0.92, 0.92, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 0.75
sc.world = w
bpy.ops.object.camera_add(location=(105, -160, 150))
cam = bpy.context.object
direction = mathutils.Vector((115, 5, 2)) - cam.location
cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 40
sc.camera = cam
sc.frame_set(18)

sc.render.resolution_x, sc.render.resolution_y = 1400, 900
sc.render.filepath = r"C:\App\gitar\2-0\manual\img\_flex_demo.png"
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=r"C:\App\gitar\2-0\Пруток_демо.blend")
print("FLEX OK")
