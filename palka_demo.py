# -*- coding: utf-8 -*-
"""ДЕМО v4 (bell crank точно по фото юзера): СЕКТОР с полукруглым основанием.
Запуск: blender -b -P palka_demo.py
- сектор («треугольник с полукруглым основанием») закреплён на оси (Pivot);
- НИТИ-ленты приходят по касательной к дуге основания (y=+-17, из каналов)
  и закреплены якорями на концах дуги: одна тянет — сектор поворачивается,
  другая возвращает;
- длинное плечо сектора давит ПЕРПЕНДИКУЛЯРНО — палец тележки в прорези;
- ход +-20 (40 мм) при повороте сектора +-32°.
"""
import bpy, math, mathutils

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.fps = 24
sc.frame_start, sc.frame_end = 1, 120

XC = 22.0                 # дорожка тележки
XP = 60.0                 # ось сектора (Pivot)
LA = XP - XC              # плечо к тележке = 38
RD = 17.0                 # радиус дуги основания = y каналов
ZS = 1.8


def mat(name, rgba):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = rgba
    return m

M_BASE = mat("base", (0.62, 0.62, 0.62, 1))
M_CART = mat("cart", (0.8, 0.8, 0.82, 1))
M_RED = mat("red", (0.8, 0.15, 0.1, 1))
M_BLUE = mat("blue", (0.2, 0.3, 0.75, 1))


def box(name, x0, x1, y0, y1, z0, z1, m, parent=None):
    bpy.ops.mesh.primitive_cube_add()
    ob = bpy.context.object
    ob.name = name
    ob.scale = ((x1 - x0) / 2, (y1 - y0) / 2, (z1 - z0) / 2)
    ob.location = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    ob.data.materials.append(m)
    if parent:
        ob.parent = parent
        ob.matrix_parent_inverse = parent.matrix_world.inverted()
    return ob


def cyl(name, x, y, z0, z1, r, m, parent=None):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=z1 - z0,
                                        location=(x, y, (z0 + z1) / 2))
    ob = bpy.context.object
    ob.name = name
    ob.data.materials.append(m)
    if parent:
        ob.parent = parent
        ob.matrix_parent_inverse = parent.matrix_world.inverted()
    return ob


def cable(name, pts, parent=None):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = 0.25
    spl = cu.splines.new('POLY')
    spl.points.add(len(pts) - 1)
    for p, (x, y, z) in zip(spl.points, pts):
        p.co = (x, y, z, 1)
    ob = bpy.data.objects.new(name, cu)
    ob.data.materials.append(M_RED)
    sc.collection.objects.link(ob)
    if parent:
        ob.parent = parent
        ob.matrix_parent_inverse = parent.matrix_world.inverted()
    return ob


def sector(name, x, y, r, a0_deg, a1_deg, z0, z1, m, parent=None):
    """Сектор-«пирог» вокруг (x,y) от a0 до a1 (градусы)."""
    verts, n = [], 36
    pts2 = [(0.0, 0.0)]
    for i in range(n + 1):
        a = math.radians(a0_deg + (a1_deg - a0_deg) * i / n)
        pts2.append((r * math.cos(a), r * math.sin(a)))
    for px, py in pts2:
        verts.append((px, py, z0))
    for px, py in pts2:
        verts.append((px, py, z1))
    m_ = len(pts2)
    faces = []
    for i in range(1, m_ - 1):                  # крышки веером из центра
        faces.append([0, i + 1, i])
        faces.append([m_, m_ + i, m_ + i + 1])
    for i in range(m_):                          # боковые стенки
        j = (i + 1) % m_
        faces.append([i, j, m_ + j, m_ + i])
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    ob = bpy.data.objects.new(name, me)
    ob.data.materials.append(m)
    sc.collection.objects.link(ob)
    if parent:
        ob.parent = parent          # вершины уже локальные вокруг оси
        ob.location = (0, 0, 0)
    else:
        ob.location = (x, y, 0)
    return ob


# ---- пол + борта ----
box("Slab", 0, 100, -25, 25, 0, 1.0, M_BASE)
box("WallN", 0, 100, 23.2, 25, 1.0, 4.5, M_BASE)
box("WallS", 0, 100, -25, -23.2, 1.0, 4.5, M_BASE)

# ---- тележка + палец ----
cart = box("Cart", XC - 8, XC + 8, -7, 7, 5.0, 12.0, M_CART)
cyl("CartPin", XC, 0, 1.4, 5.2, 1.1, M_CART, parent=cart)

# ---- СЕКТОР на оси: полукруглое основание (восток) + плечо к тележке ----
piv = bpy.data.objects.new("Pivot", None)
piv.location = (XP, 0, 0)
sc.collection.objects.link(piv)
sector("Sector", XP, 0, RD, -128, 128, 1.3, 2.3, M_BLUE, parent=piv)
# длинное плечо с прорезью под палец тележки
box("ArmBody", XP - 26, XP + 2, -3, 3, 1.3, 2.3, M_BLUE, parent=piv)
box("ArmRailN", XP - 45.5, XP - 26, 1.6, 4.5, 1.3, 2.3, M_BLUE, parent=piv)
box("ArmRailS", XP - 45.5, XP - 26, -4.5, -1.6, 1.3, 2.3, M_BLUE, parent=piv)
box("ArmCap", XP - 47, XP - 45.5, -4.5, 4.5, 1.3, 2.3, M_BLUE, parent=piv)
cyl("AxisPost", XP, 0, 1.0, 3.2, 1.0, M_BASE)

# ---- нити-ленты: каналы по касательной + намотка на дугу + якоря ----
cable("chA", [(100, RD, ZS), (XP, RD, ZS)])
cable("chB", [(100, -RD, ZS), (XP, -RD, ZS)])
for sg, nm in ((1, 'A'), (-1, 'B')):
    pts = []
    for i in range(9):                          # намотка 40° от полюса к якорю
        a = math.radians(sg * (90 + 5 * i))
        pts.append((XP + RD * math.cos(a), RD * math.sin(a), ZS))
    cable("wrap%s" % nm, pts, parent=piv)
    a = math.radians(sg * 126)
    cyl("anch%s" % nm, XP + RD * math.cos(a), RD * math.sin(a),
        ZS - 0.5, ZS + 0.7, 0.7, M_RED, parent=piv)

# ---- анимация ----
for fr in range(1, 121):
    t = 2 * math.pi * (fr - 1) / 120.0
    cy = 20.0 * math.sin(t)                     # ход 40 мм
    cart.location = (XC, cy, 8.5)
    cart.keyframe_insert("location", frame=fr)
    phi = math.atan2(cy, -LA) - math.pi         # сектор следит за пальцем
    piv.rotation_euler = (0, 0, phi)
    piv.keyframe_insert("rotation_euler", frame=fr)

# ---- свет, камера ----
bpy.ops.object.light_add(type='SUN', location=(40, -40, 90))
bpy.context.object.data.energy = 4
bpy.context.object.rotation_euler = (math.radians(30), math.radians(12), 0)
w = bpy.data.worlds.new("W")
w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.9, 0.9, 0.9, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 0.7
sc.world = w
bpy.ops.object.camera_add(location=(30, -58, 68))
cam = bpy.context.object
direction = mathutils.Vector((50, 0, 2)) - cam.location
cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 42
sc.camera = cam
sc.frame_set(12)

sc.render.resolution_x, sc.render.resolution_y = 1400, 900
sc.render.filepath = r"C:\App\gitar\2-0\manual\img\_palka_demo4.png"
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=r"C:\App\gitar\2-0\Палка_демо.blend")
print("PALKA4 OK")
