# -*- coding: utf-8 -*-
r"""Сцена: проба магнитного русла (стол 86) — сборка по шагам и ход скобы. Детали — настоящие STL.
Кадры:   1–40   оправка: прижимная щёчка опускается и защёлкивается (рядом с русл ом)
        40–80   рамка опускается в основу
        80–200  8 катушек (провод, как с оправки, выводы «н»/«к» вниз) по одной переезжают с оправки в окно рамки
       200–240  в скобу снизу входят сталь и магниты
       240–280  скоба опускается на рельс (верхнюю планку рамки)
       280–420  скоба ездит ±22 (струна 6 → 1 → 6)
Запуск: blender -b -P 2-0\magnit\scene_magnit_proba.py
"""
import math
import os
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(os.path.dirname(HERE), "Print", "Print")
OUT = os.path.join(HERE, "Магнит_проба_стол86.blend")
FRAMES = 420

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.unit_settings.system = 'METRIC'
sc.unit_settings.scale_length = 0.001
sc.unit_settings.length_unit = 'MILLIMETERS'
sc.frame_start, sc.frame_end = 1, FRAMES


def mat(name, rgba, alpha=1.0, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rgba
    b.inputs["Metallic"].default_value = metal
    if alpha < 1:
        b.inputs["Alpha"].default_value = alpha
        try:
            m.surface_render_method = 'BLENDED'
        except Exception:
            pass
    return m


def stl(fname, name, m, loc=(0, 0, 0), parent=None):
    bpy.ops.wm.stl_import(filepath=os.path.join(P, fname + ".stl"))
    ob = bpy.context.selected_objects[0]
    ob.name = name
    ob.data.materials.clear()
    ob.data.materials.append(m)
    ob.location = loc
    if parent:
        ob.parent = parent
    return ob


def fly(ob, f0, f1, start, end):
    """Деталь стоит в start до кадра f0, к кадру f1 приходит в end."""
    ob.location = start
    ob.keyframe_insert("location", frame=1)
    ob.keyframe_insert("location", frame=f0)
    ob.location = end
    ob.keyframe_insert("location", frame=f1)


PLA = (0.93, 0.93, 0.95, 1)
osn = stl("mag_osnova", "основа", mat("основа", PLA))
ram = stl("mag_ramka", "рамка катушек", mat("рамка", PLA, 0.75))
fly(ram, 40, 80, (0, 0, 40), (0, 0, 0))

# катушка из провода — как получается на оправке (scene_namotka.py): окно 1.6 × 16, 5 слоёв по 8 витков,
# толщина 3; в своей системе лежит как в оправке (окно вдоль Y, толщина по Z от −1.5 до +1.5), выводы — к +Y
WX, WY, D, NZ, NL = 1.6, 16.0, 0.34, 8, 5
pts = [(WX / 2 + 0.3, WY / 2 + 6, -1.5 + D / 2), (WX / 2 + 0.3, WY / 2 - 0.5, -1.5 + D / 2)]
for L in range(NL):
    r = D / 2 + L * D
    hx, hy = WX / 2 + r, WY / 2 + r
    for i in range(NZ):
        k = i if L % 2 == 0 else NZ - 1 - i
        z = -1.5 + D / 2 + k * D
        for (x, y) in ((hx, hy), (-hx, hy), (-hx, -hy), (hx, -hy)):
            pts.append((x, y, z))
        pts.append((hx, hy, z))
pts.append((pts[-1][0] - 1.0, WY / 2 + 6, pts[-1][2]))
cu = bpy.data.curves.new("катушка", "CURVE")
cu.dimensions = '3D'; cu.bevel_depth = D / 2 * 0.9; cu.bevel_resolution = 1
sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
for p_, (x, y, z) in zip(sp.points, pts):
    p_.co = (x, y, z, 1)
copper = mat("медь", (0.90, 0.40, 0.12, 1), metal=0.3)
cu.materials.append(copper)
JIG = (-75, 0, -7 + 2.5 + 1.5)                  # где катушка лежит в оправке
CW, Z_ACT = 6.5, 2.45 + 8.0
for k in range(8):
    ob = bpy.data.objects.new("катушка %d" % (k + 1), cu)
    sc.collection.objects.link(ob)
    f0 = 80 + k * 15
    ob.location = JIG; ob.rotation_euler = (0, 0, 0); ob.scale = (0.001, 0.001, 0.001)
    ob.keyframe_insert("location", frame=1); ob.keyframe_insert("rotation_euler", frame=1); ob.keyframe_insert("scale", frame=1)
    ob.keyframe_insert("location", frame=f0 - 1); ob.keyframe_insert("scale", frame=f0 - 1)
    ob.scale = (1, 1, 1); ob.keyframe_insert("scale", frame=f0); ob.keyframe_insert("location", frame=f0); ob.keyframe_insert("rotation_euler", frame=f0)
    ob.location = (-26 + k * CW + CW / 2, 0, Z_ACT); ob.rotation_euler = (math.radians(-90), 0, 0)   # стоймя, выводы вниз
    ob.keyframe_insert("location", frame=f0 + 14); ob.keyframe_insert("rotation_euler", frame=f0 + 14)

sk = bpy.data.objects.new("скоба (едет)", None)
sc.collection.objects.link(sk)
skb = stl("mag_skoba", "U-скоба с ложем", mat("скоба", PLA, 0.4), parent=sk)
mag = stl("mag_magnity_proverka", "магниты 20×10×5 N52", mat("магниты", (0.85, 0.15, 0.15, 1), metal=0.4), parent=sk)
stal = stl("mag_stal_proverka", "стальные пластинки 1.5", mat("сталь", (0.45, 0.47, 0.5, 1), metal=0.6), parent=sk)
fly(stal, 200, 220, (70, 0, -40), (0, 0, 0))
fly(mag, 215, 240, (70, 25, -40), (0, 0, 0))
fly(sk, 240, 280, (0, 0, 45), (0, 0, 0))
for f in range(280, FRAMES + 1, 2):
    sk.location = (22 * math.sin(2 * math.pi * (f - 280) / (FRAMES - 280)), 0, 0)
    sk.keyframe_insert("location", frame=f)

# оправка рядом: щёчка с сердечником и защёлками, прижимная опускается до щелчка
opa = stl("mag_opravka_a", "оправка: щёчка с сердечником и защёлками", mat("оправка", (0.25, 0.45, 0.80, 1)), loc=(-75, 0, -7))
opb = stl("mag_opravka_b", "оправка: прижимная щёчка", mat("оправка b", (0.45, 0.65, 0.95, 1)))
fly(opb, 5, 40, (-75, 0, -7 + 5.5 + 15), (-75, 0, -7 + 5.5))


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


cam = camera("Камера: всё", (60, -150, 95), (-25, 0, 8), 30)
camera("Камера: русло крупно", (80, -110, 80), (0, 0, 10), 32)
camera("Камера: торец", (110, 0, 12), (0, 0, 12), 45)
sc.camera = cam
sun = bpy.data.objects.new("Солнце", bpy.data.lights.new("Солнце", "SUN"))
sun.data.energy = 3
sun.rotation_euler = (math.radians(35), math.radians(10), math.radians(40))
sc.collection.objects.link(sun)
sc.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("saved", OUT)
