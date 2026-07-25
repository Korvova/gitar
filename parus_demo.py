# -*- coding: utf-8 -*-
"""ДЕМО «ПАРУС»: жёсткая центральная пластина + ПЕРЕКРЁСТНАЯ привязка нитей.
Запуск: blender -b -P parus_demo.py
- парус: пластина от центра тележки вниз, вдоль хода, полудлина 4.5;
- нить A (тянет на север, ролик у СЕВЕРНОГО борта) привязана к ЮЖНОМУ концу
  паруса; нить B — к СЕВЕРНОМУ (крест-накрест), высоты 2.1 / 2.9;
- поэтому при ходе +-20 точка привязки не доезжает до своего ролика 5 мм;
- ноль шарниров, ноль прорезей: нечему люфтить и закусывать.
"""
import bpy, math, mathutils

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.fps = 24
sc.frame_start, sc.frame_end = 1, 120

XL = 35.0                 # дорожка (лента паруса и нитей)
RY = 20.5                 # ролики у бортов
RX = XL + 2.55
HP = 4.5                  # полудлина паруса
ZA, ZB = 2.1, 2.9         # высоты нитей


def mat(name, rgba):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = rgba
    return m

M_BASE = mat("base", (0.62, 0.62, 0.62, 1))
M_CART = mat("cart", (0.8, 0.8, 0.82, 1))
M_GOLD = mat("gold", (0.75, 0.6, 0.25, 1))
M_RED = mat("red", (0.8, 0.15, 0.1, 1))
M_SAIL = mat("sail", (0.25, 0.5, 0.85, 1))


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


# ---- пол + борта ----
box("Slab", 5, 80, -25, 25, 0, 1.0, M_BASE)
box("WallN", 5, 80, 23.2, 25, 1.0, 4.5, M_BASE)
box("WallS", 5, 80, -25, -23.2, 1.0, 4.5, M_BASE)

# ---- тележка + ПАРУС (жёсткая пластина, без осей и прорезей) ----
cart = box("Cart", XL - 8, XL + 8, -7, 7, 5.0, 12.0, M_CART)
box("Sail", XL - 1.9, XL - 0.5, -HP, HP, 1.2, 5.2, M_SAIL, parent=cart)  # западнее дорожки, мимо роликов

# ---- ролики у бортов + статичные части нитей (каналы к мотору) ----
for sg, nm in ((1, 'A'), (-1, 'B')):
    cyl("Roll%s" % nm, RX, sg * RY, 1.0, 3.6, 2.3, M_GOLD)
    cable("cab%s_stat" % nm, [(80, sg * 23.0, 0.75), (RX + 1.5, sg * 23.0, 0.75),
                              (RX, sg * (RY + 2.55), 0.9),
                              (XL, sg * RY, ZA if sg > 0 else ZB)])

# ---- подвижные пролёты: КРЕСТ-НАКРЕСТ к концам паруса ----
spans = {}
for sg, nm in ((1, 'A'), (-1, 'B')):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=1.0,
                                        location=(XL, 0, ZA if sg > 0 else ZB))
    ob = bpy.context.object
    ob.name = "span%s" % nm
    ob.data.materials.append(M_RED)
    spans[sg] = ob

# ---- анимация ----
for fr in range(1, 121):
    t = 2 * math.pi * (fr - 1) / 120.0
    cy = 20.0 * math.sin(t)                     # ход 40 мм
    cart.location = (XL, cy, 8.5)
    cart.keyframe_insert("location", frame=fr)
    for sg, ob in spans.items():
        z = ZA if sg > 0 else ZB
        y_roll = sg * RY                        # сход нити со своего ролика
        y_tie = cy - sg * HP                    # КРЕСТ: A к югу паруса, B к северу
        ob.location = (XL - 0.35, (y_roll + y_tie) / 2, z)
        ob.scale = (1, 1, max(abs(y_roll - y_tie), 0.5))
        ob.rotation_euler = (math.pi / 2, 0, 0)
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
bpy.ops.object.camera_add(location=(18, -38, 78))
cam = bpy.context.object
direction = mathutils.Vector((40, 1, 1)) - cam.location
cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 42
sc.camera = cam
sc.frame_set(20)

sc.render.resolution_x, sc.render.resolution_y = 1400, 900
sc.render.filepath = r"C:\App\gitar\2-0\manual\img\_parus_demo.png"
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=r"C:\App\gitar\2-0\Парус_демо.blend")
print("PARUS OK")
