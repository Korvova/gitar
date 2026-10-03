# -*- coding: utf-8 -*-
r"""Концепт «храповик» (идея владельца 03.10): два толкателя дёргаются туда-сюда, собачки по зубчатой
рейке тележки превращают каждый рывок в один шаг — левый толкатель двигает только влево, правый только вправо.
  * рейка под тележкой: два ряда пилообразных зубьев с шагом 8.8 (шаг струн) — у левого и правого
    толкателя зубья смотрят в разные стороны;
  * толкатель = соленоид (серый) с ползуном (синий) и собачкой на шарнире: на рабочем ходе собачка
    в зубе и тянет рейку, на обратном — поднимается и проскальзывает по скосу;
  * фиксатор (жёлтый шарик на пружине) держит тележку между рывками без тока.
Анимация: 5 рывков влево (струна 6 → 1), 5 рывков вправо. Фигуры условные.
Запуск: blender -b -P 2-0\magnit\scene_hrapovik_idea.py
"""
import math
import os
import bmesh
import bpy

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Идея_храповик.blend")
P = 8.8                           # шаг зуба = шаг струн
NT = 11                           # зубьев в ряду
ST = 12                           # кадров на рывок
ZR = 4.0                          # верх рейки (основание зубьев)
TH = 3.0                          # высота зуба

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.unit_settings.system = 'METRIC'
sc.unit_settings.scale_length = 0.001
sc.unit_settings.length_unit = 'MILLIMETERS'
sc.frame_start, sc.frame_end = 1, 10 * ST + 1


def mat(name, rgba, alpha=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rgba
    if alpha < 1:
        b.inputs["Alpha"].default_value = alpha
        try:
            m.surface_render_method = 'BLENDED'
        except Exception:
            pass
    m.diffuse_color = (rgba[0], rgba[1], rgba[2], alpha)
    return m


def box(name, x0, x1, y0, y1, z0, z1, m, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), rotation=(0, 0, 0))
    ob = bpy.context.object
    ob.name = name
    ob.scale = (x1 - x0, y1 - y0, z1 - z0)
    ob.data.materials.append(m)
    if parent:
        ob.parent = parent
    return ob


def prism_xz(name, pts, y0, y1, m, parent=None):
    """Призма из контура в плоскости XZ, толщина по Y."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    a = [bm.verts.new((x, y0, z)) for x, z in pts]
    b = [bm.verts.new((x, y1, z)) for x, z in pts]
    bm.faces.new(a)
    bm.faces.new(b[::-1])
    for i in range(len(pts)):
        j = (i + 1) % len(pts)
        bm.faces.new((a[i], a[j], b[j], b[i]))
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    sc.collection.objects.link(ob)
    ob.data.materials.append(m)
    if parent:
        ob.parent = parent
    return ob


def saw(direction):
    """Пила вдоль X: крутая сторона зуба смотрит в direction (+1 — вправо, её толкает собачка, идущая влево)."""
    x0, x1 = -NT * P / 2, NT * P / 2
    pts = [(x0, 0.0)]
    if direction < 0:
        for i in range(NT):
            pts += [(x0 + i * P, ZR + TH), (x0 + (i + 1) * P, ZR)]
    else:
        pts += [(x0, ZR)]
        for i in range(NT):
            pts += [(x0 + (i + 1) * P, ZR + TH), (x0 + (i + 1) * P, ZR)]
    pts += [(x1, 0.0)]
    return pts


C_CART = mat("тележка и рейка", (0.95, 0.72, 0.30, 1))
C_SOL = mat("соленоид", (0.45, 0.47, 0.50, 1))
C_ROD = mat("ползун", (0.25, 0.45, 0.80, 1))
C_PAWL = mat("собачка", (0.85, 0.20, 0.20, 1))
C_DET = mat("фиксатор", (0.95, 0.85, 0.15, 1))
C_BASE = mat("основа", (0.8, 0.8, 0.82, 1), 0.35)

box("основа русла", -40, 40, -14, 14, -2, 0, C_BASE)
cart = bpy.data.objects.new("тележка с рейкой (едет)", None)
sc.collection.objects.link(cart)
prism_xz("рейка «влево»", saw(+1), 2.0, 7.0, C_CART, cart)
prism_xz("рейка «вправо»", saw(-1), -7.0, -2.0, C_CART, cart)
box("ложе (условно)", -12, 12, -11, 11, 12, 14, C_CART, cart)
box("стойка", -2, 2, -1.5, 1.5, 4, 12, C_CART, cart)
# ряд лунок фиксатора — для вида
for i in range(NT):
    box("лунка фиксатора", -NT * P / 2 + i * P + P / 2 - 0.6, -NT * P / 2 + i * P + P / 2 + 0.6, 7.2, 9.0, 0, 0.6, C_DET, cart)


def pusher(name, y0, y1, side):
    """Соленоид сбоку, ползун тянется к центру, собачка на конце ползуна (шарнир)."""
    sol = box(f"{name}: соленоид", side * 30, side * 42, y0 - 1, y1 + 1, ZR + 4, ZR + 12, C_SOL)
    rod = bpy.data.objects.new(f"{name}: ползун", None)
    sc.collection.objects.link(rod)
    box(f"{name}: ползун", side * 6, side * 30, (y0 + y1) / 2 - 1, (y0 + y1) / 2 + 1, ZR + 7, ZR + 9, C_ROD, rod)
    hinge = bpy.data.objects.new(f"{name}: шарнир собачки", None)
    sc.collection.objects.link(hinge)
    hinge.parent = rod
    hinge.location = (side * 6, 0, ZR + 8)
    pts = [(0, 0.8), (side * 1.5, 0.8), (side * 1.5, -1.0), (0, -4.6)]
    prism_xz(f"{name}: собачка", pts if side > 0 else pts[::-1], y0, y1, C_PAWL, hinge)
    return rod, hinge


rodL, hingeL = pusher("толкатель «влево»", 2.0, 7.0, +1)        # стоит справа, тянет рейку влево
rodR, hingeR = pusher("толкатель «вправо»", -7.0, -2.0, -1)     # стоит слева, тянет вправо
det = bpy.data.objects.new("фиксатор: шарик на пружине", None)
sc.collection.objects.link(det)
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.2, location=(0, 8.1, 2.0))
ball = bpy.context.object
ball.name = "фиксатор: шарик"
ball.data.materials.append(C_DET)
box("фиксатор: корпус пружины", -2, 2, 6.5, 9.7, 3.4, 8, C_SOL)

# анимация: рывок = ход ползуна P к центру с опущенной собачкой (рейка едет), возврат с поднятой собачкой
x_cart = 2 * P + P / 2                                         # старт: струна 6
f = 1


def key(fr):
    for ob, prop in ((cart, "location"), (rodL, "location"), (rodR, "location"), (hingeL, "rotation_euler"),
                     (hingeR, "rotation_euler"), (ball, "location")):
        ob.keyframe_insert(prop, frame=fr)


for step in range(10):
    left = step < 5
    rod, hinge, side = (rodL, hingeL, +1) if left else (rodR, hingeR, -1)
    other = rodR if left else rodL
    other.location.x = 0
    # начало: ползун отведён, собачка опущена
    rod.location.x = 0; hinge.rotation_euler = (0, 0, 0); cart.location.x = x_cart; ball.location.z = 2.0
    key(f)
    # рабочий ход: ползун к центру на P, рейка с ним
    rod.location.x = -side * P; cart.location.x = x_cart - side * P; ball.location.z = 1.2
    key(f + ST // 2)
    x_cart -= side * P
    # возврат: собачка поднята, ползун назад, рейка стоит, шарик в лунке
    hinge.rotation_euler = (0, math.radians(side * 35), 0); rod.location.x = -side * P * 0.5; ball.location.z = 2.0
    key(f + ST * 3 // 4)
    rod.location.x = 0; hinge.rotation_euler = (0, 0, 0)
    key(f + ST - 1)
    f += ST


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


cam = camera("Камера: 3/4", (40, -110, 70), (0, 0, 6), 32)
camera("Камера: сбоку (видно зубья)", (0, -140, 8), (0, 0, 6), 35)
sc.camera = cam
sun = bpy.data.objects.new("Солнце", bpy.data.lights.new("Солнце", "SUN"))
sun.data.energy = 3
sun.rotation_euler = (math.radians(35), math.radians(10), math.radians(40))
sc.collection.objects.link(sun)
sc.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("saved", OUT)
