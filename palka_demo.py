# -*- coding: utf-8 -*-
"""ДЕМО (схема юзера): одна тележка, центральная ПАЛКА, трос тянет её конец.
Запуск: blender -b -P palka_demo.py
- палка привинчена к центру тележки (ось), нижний конец уходит в центральную
  канавку; к нему привязаны обе нити петли (A с борта +Y, B с борта -Y);
- ролики заворачивают нити из каналов в ОДНУ центральную дорожку x=35;
- ход +-18 в демо; ничего не выходит за борта.
"""
import bpy, math, mathutils

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.fps = 24
sc.frame_start, sc.frame_end = 1, 120

S = 35.0
CHY = 17.0
RX = S + 2.55            # ролики: западная касательная = дорожка x=35
ZA, ZB = 2.2, 3.0        # высоты нитей A и B на дорожке (друг над другом)


def mat(name, rgba):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = rgba
    return m

M_BASE = mat("base", (0.62, 0.62, 0.62, 1))
M_DARK = mat("dark", (0.35, 0.35, 0.35, 1))
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


# ---- пол с РЕАЛЬНО прорезанной канавкой и каналами ----
box("FloorW", 5, 32.2, -25, 25, 0, 3.5, M_BASE)                    # запад
box("FloorE1", 37.8, 70, -25, -18.75, 0, 3.5, M_BASE)              # восток: юг
box("FloorE2", 37.8, 70, -15.25, 15.25, 0, 3.5, M_BASE)            # восток: центр
box("FloorE3", 37.8, 70, 18.75, 25, 0, 3.5, M_BASE)                # восток: север
box("ChAfloor", 37.8, 70, 15.25, 18.75, 0, 0.5, M_DARK)            # дно канала A
box("ChBfloor", 37.8, 70, -18.75, -15.25, 0, 0.5, M_DARK)          # дно канала B
box("GrooveFloor", 32.2, 37.8, -21, 21, 0, 0.4, M_DARK)            # дно дорожки
box("GrooveCapN", 32.2, 37.8, 21, 25, 0, 3.5, M_BASE)
box("GrooveCapS", 32.2, 37.8, -25, -21, 0, 3.5, M_BASE)
# ролики (шейки-капстаны)
cyl("RollA", RX, CHY - 2.5, 0.4, 3.3, 2.3, M_GOLD)
cyl("RollB", RX, -(CHY - 2.5), 0.4, 3.3, 2.3, M_GOLD)

# ---- тележка + ПАЛКА к центру (ось видна как бобышка) ----
cart = box("Cart", S - 7.1, S + 7.1, -7, 7, 6.5, 13.5, M_CART)
cyl("Axis", S - 1.0, 0, 5.6, 6.6, 1.4, M_BLADE, parent=cart)        # ось-«винт»
box("Blade", S - 2.6, S - 0.2, -1.1, 1.1, 1.0, 6.4, M_BLADE, parent=cart)
box("BladeTab", S - 0.2, S + 0.15, -1.1, 1.1, 1.6, 3.4, M_BLADE, parent=cart)

# ---- нити: статичная часть (канал + обход ролика) ----
ptsA = [(70, CHY, 0.75), (RX, CHY, 0.75)]
for i in range(11):
    a = math.radians(90 + 9 * i)
    ptsA.append((RX + 2.55 * math.cos(a), CHY - 2.5 + 2.55 * math.sin(a),
                 0.75 + (ZA - 0.75) * i / 10.0))
cable("cabA_stat", ptsA)
ptsB = [(70, -CHY, 0.75), (RX, -CHY, 0.75)]
for i in range(11):
    a = math.radians(270 - 9 * i)
    ptsB.append((RX + 2.55 * math.cos(a), -(CHY - 2.5) + 2.55 * math.sin(a),
                 0.75 + (ZB - 0.75) * i / 10.0))
cable("cabB_stat", ptsB)

# ---- подвижные пролёты нитей (цилиндры до палки) ----
def span(name, z):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=1.0, location=(S, 0, z))
    ob = bpy.context.object
    ob.name = name
    ob.data.materials.append(M_RED)
    return ob

spanA = span("spanA", ZA)
spanB = span("spanB", ZB)

# ---- анимация: тележка ездит, пролёты следят за палкой ----
YA0, YB0 = CHY - 2.5, -(CHY - 2.5)          # точки схода нитей с роликов
for fr in range(1, 121):
    t = 2 * math.pi * (fr - 1) / 120.0
    cy = 18.0 * math.sin(t)
    cart.location = (S, cy, 10.0)
    cart.keyframe_insert("location", frame=fr)
    for ob, z, y0, tab in ((spanA, ZA, YA0, 1.1), (spanB, ZB, YB0, -1.1)):
        y1 = cy + tab
        ob.location = (S, (y0 + y1) / 2, z)
        ob.scale = (1, 1, max(abs(y1 - y0), 0.5))
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
bpy.ops.object.camera_add(location=(80, -48, 42))
cam = bpy.context.object
direction = mathutils.Vector((36, 2, 3)) - cam.location
cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 42
sc.camera = cam
sc.frame_set(15)

sc.render.resolution_x, sc.render.resolution_y = 1400, 900
sc.render.filepath = r"C:\App\gitar\2-0\manual\img\_palka_demo.png"
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=r"C:\App\gitar\2-0\Палка_демо.blend")
print("PALKA OK")
