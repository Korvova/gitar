# -*- coding: utf-8 -*-
"""Концепт «винт поперёк грифа» для верхнего этажа (обсуждение 27.09).

Мотор лёжа в деке, вал вдоль грифа → стальной пруток крутится вдоль грифа в этаже →
у края грифа коническая пара 1:1 поворачивает вращение на 90° → ходовой винт поперёк грифа
(шаг 8, как TR8x8 в принтерах) → гайка в тележке → стойка сквозь прорезь палубы → ложе пальца.
Один оборот = 8 мм, 45 мм = 5.6 оборота. Винт неподвижен вдоль себя — ничего не выезжает.

Узкое место: коническая пара на конце винта. Винт + гайка на ход 45 мм занимают всю ширину 52 —
пара встаёт снаружи края грифа коробочкой ~10 мм (со стороны 6-й струны). Если спрятать пару внутрь грифа — ход только ~38.
Расстояние до деки укорочено. Запуск: blender -b -P 2-0\\scene_vint_idea.py
"""
import math
import os
import bpy

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Идея_винт_поперёк.blend")
LEAD = 8.0
Y_CART, Z_AX = 40.0, 20.0
SCREW_X = (-26.0, 26.0)
BEVEL_X = -31.0               # оси винта и прутка пересекаются здесь (снаружи края x = −26)
ROD_X = BEVEL_X
MOTOR_Y = 250.0
TRAVEL = 22.0                 # тележка ±22 мм
FRAMES = 120

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
    if alpha < 1:
        b.inputs["Alpha"].default_value = alpha
    m.diffuse_color = (rgba[0], rgba[1], rgba[2], alpha)
    return m


def add(obj_fn, name, m, **kw):
    obj_fn(**kw)
    ob = bpy.context.object
    ob.name = name
    ob.data.materials.append(m)
    return ob


def box(name, x0, x1, y0, y1, z0, z1, m):
    ob = add(bpy.ops.mesh.primitive_cube_add, name, m, size=1,
             location=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), rotation=(0, 0, 0))
    ob.scale = (x1 - x0, y1 - y0, z1 - z0)
    return ob


C_DECK = mat("палуба (прозрачная)", (0.85, 0.82, 0.76, 1), 0.18)
C_ROD = mat("пруток", (0.8, 0.8, 0.85, 1))
C_SCREW = mat("ходовой винт", (0.75, 0.7, 0.4, 1))
C_BEV = mat("коническая пара", (0.35, 0.62, 0.38, 1))
C_CART = mat("гайка и ложе", (0.95, 0.55, 0.25, 1))
C_MOT = mat("мотор", (0.25, 0.27, 0.30, 1))
C_BOX = mat("коробочка пары", (0.6, 0.6, 0.65, 1), 0.45)

box("палуба секции-1", -26, 26, 0, 160, 23, 26, C_DECK)
box("пол этажа", -26, 26, 0, 270, 15.5, 17, C_DECK)
box("прорезь в палубе (пометка)", -24.5, 24.5, Y_CART - 3, Y_CART + 3, 26, 26.2, C_BEV)
box("коробочка конической пары снаружи края", -36.5, -26, Y_CART - 7, Y_CART + 12, 15.5, 26, C_BOX)

# ходовой винт: цилиндр + «витки» (кольца с шагом LEAD) — чтобы было видно вращение
screw = add(bpy.ops.mesh.primitive_cylinder_add, "ходовой винт Ø6, шаг 8", C_SCREW, vertices=32, radius=3.0,
            depth=SCREW_X[1] - SCREW_X[0] + 4, location=(-2, Y_CART, Z_AX), rotation=(0, math.radians(90), 0))
bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)   # ось винта = X, крутим rotation X
bev1 = add(bpy.ops.mesh.primitive_cone_add, "коническая на винте", C_BEV, vertices=12, radius1=5, radius2=2.5,
           depth=4, location=(BEVEL_X + 4, Y_CART, Z_AX), rotation=(0, math.radians(-90), 0))
parts = [bev1]
x = SCREW_X[0] + 2
while x < SCREW_X[1] - 1:
    parts.append(add(bpy.ops.mesh.primitive_torus_add, "виток", C_SCREW, major_radius=3.0, minor_radius=0.6,
                     location=(x, Y_CART, Z_AX), rotation=(math.radians(12), math.radians(90), 0)))
    x += LEAD
# пруток вдоль грифа, коническая на нём и мотор лёжа в деке
rod = add(bpy.ops.mesh.primitive_cylinder_add, "пруток Ø3 (крутится)", C_ROD, vertices=16, radius=1.5,
          depth=MOTOR_Y - 11 - (Y_CART + 2), location=(ROD_X, (Y_CART + 2 + MOTOR_Y - 11) / 2, Z_AX),
          rotation=(math.radians(90), 0, 0))
bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)   # ось прутка = Y
bev2 = add(bpy.ops.mesh.primitive_cone_add, "коническая на прутке", C_BEV, vertices=12, radius1=5, radius2=2.5,
           depth=4, location=(ROD_X, Y_CART + 4, Z_AX), rotation=(math.radians(90), 0, 0))
add(bpy.ops.mesh.primitive_cylinder_add, "мотор Ø36 лёжа, вал вдоль грифа", C_MOT, vertices=48, radius=18.25,
    depth=22, location=(ROD_X + 5, MOTOR_Y, Z_AX), rotation=(math.radians(90), 0, 0))
bpy.context.view_layer.update()
for ch, par in [(p, screw) for p in parts] + [(bev2, rod)]:
    ch.parent = par
    ch.matrix_parent_inverse = par.matrix_world.inverted()

# тележка: гайка на винте + стойка сквозь прорезь + ложе над палубой
cart = box("гайка", -4, 4, Y_CART - 5, Y_CART + 5, Z_AX - 4.5, Z_AX + 4.5, C_CART)
post = box("стойка сквозь прорезь", -2, 2, Y_CART - 2, Y_CART + 2, Z_AX + 4.5, 27, C_CART)
bed = box("ложе пальца", -12, 12, Y_CART - 10, Y_CART + 10, 27, 29, C_CART)
rims = [box("бортик", rx, rx + 1.6, Y_CART - 10, Y_CART + 10, 29, 34, C_CART) for rx in (-12, 10.4)]
bpy.context.view_layer.update()
for ob in [post, bed] + rims:
    ob.parent = cart
    ob.matrix_parent_inverse = cart.matrix_world.inverted()

# анимация: тележка ±22 мм; винт, конические и пруток — на тот же угол (пара 1:1)
for f in range(1, FRAMES + 1, 2):
    xc = TRAVEL * math.sin(2 * math.pi * (f - 1) / (FRAMES - 1))
    turns = xc / LEAD
    ang = 2 * math.pi * turns
    cart.location = (xc, Y_CART, Z_AX)
    cart.keyframe_insert("location", frame=f)
    screw.rotation_euler = (ang, 0, 0)
    screw.keyframe_insert("rotation_euler", frame=f)
    rod.rotation_euler = (0, -ang, 0)
    rod.keyframe_insert("rotation_euler", frame=f)


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


cam = camera("Камера: секция-1 крупно", (85, -55, 95), (-3, 50, 20), 38)
camera("Камера: общий вид", (150, -40, 150), (-5, 120, 15), 30)
sc.camera = cam
sun = bpy.data.objects.new("Солнце", bpy.data.lights.new("Солнце", "SUN"))
sun.data.energy = 3
sun.rotation_euler = (math.radians(40), math.radians(20), math.radians(30))
sc.collection.objects.link(sun)
sc.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("saved", OUT)
