# -*- coding: utf-8 -*-
"""ДЕМО v2 (схема юзера): ПАЛКА-СТРЕЛКА на неподвижной оси.
Запуск: blender -b -P palka_demo.py
- палка (пластина ~1 мм толщиной) верхним концом входит ПРОРЕЗЬЮ в палец
  на центре тележки; ЧУТЬ НИЖЕ ЦЕНТРА ПАЛКИ — неподвижная ось на полу;
- нижний конец качается влево-вправо как стрелка часов, его тянут ТРОСИКИ;
- плечи 26/19: тележка ходит +-20 (40 мм!), низ палки — только +-13,
  поэтому нити и ролики живут в своей зоне и тележка до них не доезжает.
"""
import bpy, math, mathutils

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.fps = 24
sc.frame_start, sc.frame_end = 1, 120

XC = 30.0                 # дорожка тележки (x)
XP = 56.0                 # неподвижная ось палки
L1 = XP - XC              # верхнее плечо (к тележке) = 26
L2 = 19.0                 # нижнее плечо (к тросикам)
RY = 14.0                 # линия нитей у роликов
ZS = 1.9                  # высота нитей


def mat(name, rgba):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = rgba
    return m

M_BASE = mat("base", (0.62, 0.62, 0.62, 1))
M_CART = mat("cart", (0.8, 0.8, 0.82, 1))
M_GOLD = mat("gold", (0.75, 0.6, 0.25, 1))
M_RED = mat("red", (0.8, 0.15, 0.1, 1))
M_BLADE = mat("blade", (0.25, 0.5, 0.85, 1))


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


def cable(name, pts):
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
    return ob


# ---- пол (тонкая плита, механика сверху для наглядности) + борта ----
box("Slab", 5, 100, -25, 25, 0, 1.0, M_BASE)
box("WallN", 5, 100, 23, 25, 1.0, 4.5, M_BASE)
box("WallS", 5, 100, -25, -23, 1.0, 4.5, M_BASE)

# ---- тележка (ездит по y) + палец вниз ----
cart = box("Cart", XC - 8, XC + 8, -7, 7, 5.0, 12.0, M_CART)
cyl("CartPin", XC, 0, 1.4, 5.2, 1.1, M_CART, parent=cart)

# ---- ПАЛКА-стрелка на неподвижной оси ----
piv = bpy.data.objects.new("PalkaPivot", None)
piv.location = (XP, 0, 0)
sc.collection.objects.link(piv)
# пластина: хвост к тележке С ПРОРЕЗЬЮ под палец, нос к тросикам
box("PalkaBody", XP - 25, XP + L2, -6, 6, 1.3, 2.3, M_BLADE, parent=piv)
box("PalkaRailN", XP - 35.5, XP - 25, 1.6, 6, 1.3, 2.3, M_BLADE, parent=piv)
box("PalkaRailS", XP - 35.5, XP - 25, -6, -1.6, 1.3, 2.3, M_BLADE, parent=piv)
box("PalkaCap", XP - 37, XP - 35.5, -6, 6, 1.3, 2.3, M_BLADE, parent=piv)
cyl("PalkaBoss", XP, 0, 1.3, 3.0, 2.2, M_BLADE, parent=piv)
box("PalkaTab", XP + L2 - 1.5, XP + L2 + 0.5, -1.5, 1.5, 1.3, 3.2, M_BLADE, parent=piv)
cyl("AxisPost", XP, 0, 1.0, 3.4, 1.0, M_BASE)                       # сама ось

# ---- ролики нитей + статичные части нитей (в свои каналы к мотору) ----
RXR = XP + L2 + 2.55
for sg, nm in ((1, 'A'), (-1, 'B')):
    cyl("Roll%s" % nm, RXR, sg * RY, 1.0, 3.6, 2.3, M_GOLD)
    cable("cab%s_stat" % nm, [(100, sg * RY, ZS), (RXR, sg * RY, ZS),
                              (RXR - 2.55, sg * (RY - 1.0), ZS)])

# ---- подвижные пролёты нитей: от носа палки к роликам ----
spans = {}
for sg, nm in ((1, 'A'), (-1, 'B')):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=1.0,
                                        location=(XP + L2, sg * 5, ZS))
    ob = bpy.context.object
    ob.name = "span%s" % nm
    ob.data.materials.append(M_RED)
    spans[sg] = ob

# ---- анимация ----
for fr in range(1, 121):
    t = 2 * math.pi * (fr - 1) / 120.0
    cy = 20.0 * math.sin(t)                     # ход тележки +-20 = 40 мм
    cart.location = (XC, cy, 8.5)
    cart.keyframe_insert("location", frame=fr)
    phi = math.atan2(cy, -L1) - math.pi         # палка следит за пальцем
    piv.rotation_euler = (0, 0, phi)
    piv.keyframe_insert("rotation_euler", frame=fr)
    tx = XP + L2 * math.cos(phi)                # нос палки
    ty = L2 * math.sin(phi)
    for sg, ob in spans.items():
        ex, ey = RXR - 2.55, sg * (RY - 1.0)    # сход нити с ролика
        mx, my = (tx + ex) / 2, (ty + ey) / 2
        ln = math.hypot(ex - tx, ey - ty)
        ob.location = (mx, my, ZS)
        ob.scale = (1, 1, max(ln, 0.5))
        ob.rotation_euler = (0, math.pi / 2, math.atan2(ey - ty, ex - tx))
        ob.keyframe_insert("location", frame=fr)
        ob.keyframe_insert("scale", frame=fr)
        ob.keyframe_insert("rotation_euler", frame=fr)

# ---- свет, камера ----
bpy.ops.object.light_add(type='SUN', location=(40, -40, 90))
bpy.context.object.data.energy = 4
bpy.context.object.rotation_euler = (math.radians(30), math.radians(12), 0)
w = bpy.data.worlds.new("W")
w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.9, 0.9, 0.9, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 0.7
sc.world = w
bpy.ops.object.camera_add(location=(50, -70, 75))
cam = bpy.context.object
direction = mathutils.Vector((52, 0, 2)) - cam.location
cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 42
sc.camera = cam
sc.frame_set(20)

sc.render.resolution_x, sc.render.resolution_y = 1400, 900
sc.render.filepath = r"C:\App\gitar\2-0\manual\img\_palka_demo.png"
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=r"C:\App\gitar\2-0\Палка_демо.blend")
print("PALKA OK")
