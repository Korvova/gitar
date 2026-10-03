# -*- coding: utf-8 -*-
r"""Как мотать плоскую катушку на оправке (стол 86) — анимация провода виток за витком.
Оправка лежит щёчкой вниз, сердечник 1.6 × 16 торчит вверх, прижимная щёчка (полупрозрачная) сверху,
между щёчками щель 3 мм. Провод (медный) входит через прорезь прижимной щёчки — это «н», начало,
дальше витки ложатся вокруг сердечника: первый слой — 8 витков рядом поперёк щели (по высоте 3 мм),
второй слой поверх — обратно, и так 5 слоёв ≈ 40 витков; конец «к» уходит наружу.
Анимация: провод «нарастает» (bevel end), 240 кадров.
Запуск: blender -b -P 2-0\magnit\scene_namotka.py
"""
import math
import os
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(os.path.dirname(HERE), "Print", "Print")
OUT = os.path.join(HERE, "Как_мотать_катушку.blend")
WX, WY = 1.6, 16.0                # сердечник (окно катушки)
Z0, GAPZ = 2.5, 3.0               # верх щёчки, щель
D = 0.34                          # провод с лаком
NZ = int(GAPZ // D)               # витков в слое поперёк щели: 8
NL = 5                            # слоёв
FRAMES = 240

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.unit_settings.system = 'METRIC'
sc.unit_settings.scale_length = 0.001
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


def stl(fname, m, loc=(0, 0, 0)):
    bpy.ops.wm.stl_import(filepath=os.path.join(P, fname + ".stl"))
    ob = bpy.context.selected_objects[0]
    ob.data.materials.clear(); ob.data.materials.append(m)
    ob.location = loc
    return ob


stl("mag_opravka_a", mat("оправка: щёчка с сердечником", (0.25, 0.45, 0.80, 1)))
pb = stl("mag_opravka_b", mat("прижимная щёчка", (0.45, 0.65, 0.95, 1), 0.3), loc=(0, 0, Z0 + GAPZ))
pb.hide_render = True                      # на картинке без неё — видно витки; в Blender включить глазком

# путь провода: прямоугольные витки вокруг сердечника; слой за слоем наружу, в слое — поперёк щели
pts = []
# начало «н»: сверху через прорезь прижимной щёчки вниз к сердечнику
x_slot = WX / 2 + 0.3
pts += [(x_slot, WY / 2 + 6, Z0 + GAPZ + 6), (x_slot, WY / 2 - 0.5, Z0 + GAPZ + 2.5), (x_slot, WY / 2 - 0.5, Z0 + D / 2)]
for L in range(NL):
    r = D / 2 + L * D                                   # отступ слоя от сердечника
    hx, hy = WX / 2 + r, WY / 2 + r
    for i in range(NZ):
        k = i if L % 2 == 0 else NZ - 1 - i             # слой туда, следующий обратно
        z = Z0 + D / 2 + k * D
        z1 = Z0 + D / 2 + (k + (1 if L % 2 == 0 else -1)) * D if i < NZ - 1 else z
        for j, (x, y) in enumerate(((hx, hy), (-hx, hy), (-hx, -hy), (hx, -hy))):
            pts.append((x, y, z + (z1 - z) * (j + 1) / 5))
        pts.append((hx, hy, z1))
# конец «к»: наружу вверх
last = pts[-1]
pts += [(last[0] + 3, last[1] + 3, last[2]), (last[0] + 8, last[1] + 8, last[2] + 4)]

cu = bpy.data.curves.new("провод", "CURVE")
cu.dimensions = '3D'
cu.bevel_depth = D / 2 * 0.9
cu.bevel_resolution = 2
sp = cu.splines.new('POLY')
sp.points.add(len(pts) - 1)
for p_, (x, y, z) in zip(sp.points, pts):
    p_.co = (x, y, z, 1)
wire = bpy.data.objects.new("провод ПЭТВ-2 0.3", cu)
sc.collection.objects.link(wire)
wire.data.materials.append(mat("медь", (0.90, 0.40, 0.12, 1), metal=0.3))
cu.bevel_factor_end = 0.0
cu.keyframe_insert("bevel_factor_end", frame=1)
cu.bevel_factor_end = 1.0
cu.keyframe_insert("bevel_factor_end", frame=FRAMES - 20)


# подписи «н» и «к» (латиницей шрифт есть всегда; кириллицу пишем как есть — у Blender шрифт с ней)
def label(s, loc):
    bpy.ops.object.text_add(location=loc, rotation=(math.radians(60), 0, math.radians(30)))
    t = bpy.context.object
    t.data.body = s; t.data.size = 2.5; t.data.align_x = 'CENTER'
    t.data.materials.append(mat("текст", (0.05, 0.05, 0.05, 1)))


label("н", (x_slot + 1.5, WY / 2 + 6.5, Z0 + GAPZ + 7))
label("к", (last[0] + 8.5, last[1] + 9, last[2] + 5))

tgt = bpy.data.objects.new("t", None); sc.collection.objects.link(tgt); tgt.location = (1.5, 2, 4)
cam = bpy.data.objects.new("Камера", bpy.data.cameras.new("Камера")); sc.collection.objects.link(cam)
cam.data.lens = 60; cam.data.clip_start = 1; cam.location = (24, -26, 34)
tc = cam.constraints.new('TRACK_TO'); tc.target = tgt; tc.track_axis = 'TRACK_NEGATIVE_Z'; tc.up_axis = 'UP_Y'
sc.camera = cam
sun = bpy.data.objects.new("Солнце", bpy.data.lights.new("Солнце", "SUN"))
sun.data.energy = 3.5
sun.rotation_euler = (math.radians(35), math.radians(10), math.radians(40))
sc.collection.objects.link(sun)
sc.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("saved", OUT, "витков", NZ * NL)
