# -*- coding: utf-8 -*-
"""ДЕМО v3 (bell crank как на фото юзера): стрелка + ДИСК-ШКИВ на оси.
Запуск: blender -b -P palka_demo.py
- нижняя часть палки = диск r17 на неподвижной оси; НИТИ ЛОЖАТСЯ НА ЕГО
  ДУГУ по касательной (как лента на bell crank с фото): плечо постоянное,
  перекосов тяги нет, УГЛОВЫЕ РОЛИКИ НЕ НУЖНЫ — нить с канала сразу на диск;
- верхнее плечо (стрелка) двигает тележку через палец-прорезь;
- ход +-20 (40 мм), сила = F_нити * 17/26 ~ 5 Н.
"""
import bpy, math, mathutils

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.fps = 24
sc.frame_start, sc.frame_end = 1, 120

XC = 30.0                 # дорожка тележки
XP = 56.0                 # ось диска-стрелки
L1 = XP - XC              # плечо к тележке = 26
RD = 17.0                 # радиус диска = y каналов (нити по касательной!)
ZS = 1.8                  # высота нитей


def mat(name, rgba):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = rgba
    return m

M_BASE = mat("base", (0.62, 0.62, 0.62, 1))
M_CART = mat("cart", (0.8, 0.8, 0.82, 1))
M_RED = mat("red", (0.8, 0.15, 0.1, 1))
M_BLUE = mat("blue", (0.25, 0.5, 0.85, 1))


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


# ---- пол + борта ----
box("Slab", 5, 100, -25, 25, 0, 1.0, M_BASE)
box("WallN", 5, 100, 23.2, 25, 1.0, 4.5, M_BASE)
box("WallS", 5, 100, -25, -23.2, 1.0, 4.5, M_BASE)

# ---- тележка + палец ----
cart = box("Cart", XC - 8, XC + 8, -7, 7, 5.0, 12.0, M_CART)
cyl("CartPin", XC, 0, 1.4, 5.2, 1.1, M_CART, parent=cart)

# ---- СТРЕЛКА + ДИСК на неподвижной оси ----
piv = bpy.data.objects.new("Pivot", None)
piv.location = (XP, 0, 0)
sc.collection.objects.link(piv)
cyl("Disk", XP, 0, 1.3, 2.3, RD, M_BLUE, parent=piv)               # диск-шкив
# стрелка к тележке с прорезью под палец
box("ArmBody", XP - 25, XP - 8, -3, 3, 1.3, 2.3, M_BLUE, parent=piv)
box("ArmRailN", XP - 35.5, XP - 25, 1.6, 4.5, 1.3, 2.3, M_BLUE, parent=piv)
box("ArmRailS", XP - 35.5, XP - 25, -4.5, -1.6, 1.3, 2.3, M_BLUE, parent=piv)
box("ArmCap", XP - 37, XP - 35.5, -4.5, 4.5, 1.3, 2.3, M_BLUE, parent=piv)
cyl("AxisPost", XP, 0, 1.0, 3.2, 1.0, M_BASE)

# ---- нити: статичные каналы + НАМОТКА НА ДУГУ (едет с диском) ----
cable("chA", [(100, RD, ZS), (XP, RD, ZS)])                        # канал A (север)
cable("chB", [(100, -RD, ZS), (XP, -RD, ZS)])                      # канал B (юг)
for sg, nm in ((1, 'A'), (-1, 'B')):
    pts = []
    for i in range(23):                                            # дуга 110°
        a = math.radians(sg * (90 + 5 * i))
        pts.append((XP + RD * math.cos(a), RD * math.sin(a), ZS))
    cable("wrap%s" % nm, pts, parent=piv)
    # якорь нити на дуге
    a = math.radians(sg * 200)
    cyl("anch%s" % nm, XP + RD * math.cos(a), RD * math.sin(a),
        ZS - 0.5, ZS + 0.7, 0.7, M_RED, parent=piv)

# ---- анимация ----
for fr in range(1, 121):
    t = 2 * math.pi * (fr - 1) / 120.0
    cy = 20.0 * math.sin(t)                     # ход 40 мм
    cart.location = (XC, cy, 8.5)
    cart.keyframe_insert("location", frame=fr)
    phi = math.atan2(cy, -L1) - math.pi
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
bpy.ops.object.camera_add(location=(30, -55, 70))
cam = bpy.context.object
direction = mathutils.Vector((48, 0, 2)) - cam.location
cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 42
sc.camera = cam
sc.frame_set(20)

sc.render.resolution_x, sc.render.resolution_y = 1400, 900
sc.render.filepath = r"C:\App\gitar\2-0\manual\img\_palka_demo3.png"
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=r"C:\App\gitar\2-0\Палка_демо.blend")
print("PALKA3 OK")
