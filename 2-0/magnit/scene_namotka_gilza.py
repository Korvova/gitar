# -*- coding: utf-8 -*-
r"""Как мотать гильзу бегунка (стол 87): гильза надета на ось для намотки (квадрат + шестигранник под
шуруповёрт), отсеки мотаются по очереди 1 → 2 → 3 → 4, все в одну сторону; начало и конец каждого отсека
выходят через прорезь щёчки вниз (хвосты по 10 см). Потом: A = 1 + 3 наоборот, B = 2 + 4 наоборот.
В анимации провод каждого отсека «нарастает» по очереди; ось с гильзой медленно вращается.
Запуск: blender -b -P 2-0\magnit\scene_namotka_gilza.py
"""
import math
import os
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(os.path.dirname(HERE), "Print", "Print")
OUT = os.path.join(HERE, "Как_мотать_гильзу.blend")
HOLE, CORE_W, FL, PITCH, NSEC, OUTER = 6.0, 0.6, 0.6, 4.0, 4, 13.0
BOB_L = NSEC * PITCH + FL
SQ_W = HOLE - 0.15
D, NX, NL = 0.34, 9, 5                        # провод, витков в ряду (3.4 мм), слоёв
FRAMES = 360

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


def stl(fname, name, m, loc=(0, 0, 0), parent=None):
    bpy.ops.wm.stl_import(filepath=os.path.join(P, fname + ".stl"))
    ob = bpy.context.selected_objects[0]
    ob.name = name
    ob.data.materials.clear(); ob.data.materials.append(m)
    ob.location = loc
    if parent:
        ob.parent = parent
    return ob


ZC = SQ_W / 2                                  # ось вращения
rot = bpy.data.objects.new("ось с гильзой (вращается)", None); sc.collection.objects.link(rot)
rot.location = (0, 0, ZC)
os_ = stl("sz_os_namotki", "ось для намотки (в шуруповёрт за шестигранник)", mat("ось", (0.45, 0.47, 0.5, 1)), loc=(0, 0, -ZC), parent=rot)
gil = stl("sz_katushka", "гильза", mat("гильза", (0.45, 0.65, 0.95, 1), 0.6), loc=(BOB_L / 2 + 1, 0, 0), parent=rot)
C_CU = mat("медь", (0.90, 0.40, 0.12, 1), metal=0.3)
r0 = HOLE / 2 + CORE_W                         # поверхность сердечника
for k in range(NSEC):
    x0 = 1 + FL + k * PITCH + D / 2            # начало отсека по X (в системе вращающейся оси)
    pts = [(x0, 0.3, -r0 - 8), (x0, 0.3, -r0 - 0.2)]          # начало «н» — из прорези вниз
    for L in range(NL):
        h = r0 + D / 2 + L * D
        for i in range(NX):
            j = i if L % 2 == 0 else NX - 1 - i
            x = x0 + j * D
            for (y, z) in ((h, -h), (h, h), (-h, h), (-h, -h)):
                pts.append((x, y, z))
    last = pts[-1]
    pts += [(last[0], -0.3, -h - 0.2), (last[0], -0.3, -r0 - 8)]   # конец «к» — тоже вниз
    cu = bpy.data.curves.new("отсек %d" % (k + 1), "CURVE")
    cu.dimensions = '3D'; cu.bevel_depth = D / 2 * 0.9; cu.bevel_resolution = 1
    sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
    for p_, (x, y, z) in zip(sp.points, pts):
        p_.co = (x, y, z, 1)
    cu.materials.append(C_CU)
    ob = bpy.data.objects.new("отсек %d (%s)" % (k + 1, "A" if k % 2 == 0 else "B"), cu)
    sc.collection.objects.link(ob)
    ob.parent = rot
    f0, f1 = 20 + k * 80, 20 + k * 80 + 70
    cu.bevel_factor_end = 0.0; cu.keyframe_insert("bevel_factor_end", frame=1); cu.keyframe_insert("bevel_factor_end", frame=f0)
    cu.bevel_factor_end = 1.0; cu.keyframe_insert("bevel_factor_end", frame=f1)
    bpy.ops.object.text_add(location=(x0 + 1.5, 0, -r0 - 11), rotation=(math.radians(90), 0, 0))
    t = bpy.context.object; t.data.body = "%d%s" % (k + 1, "A" if k % 2 == 0 else "B"); t.data.size = 2.2; t.data.align_x = 'CENTER'
    t.data.materials.append(mat("текст", (0.05, 0.05, 0.05, 1)))
# лёгкое вращение оси — видно, что мотает шуруповёрт
for f in (1, FRAMES):
    rot.rotation_euler = (math.radians(0 if f == 1 else 720), 0, 0)
    rot.keyframe_insert("rotation_euler", frame=f)
for fc in rot.animation_data.action.fcurves if rot.animation_data and hasattr(rot.animation_data.action, "fcurves") else []:
    for kp in fc.keyframe_points:
        kp.interpolation = 'LINEAR'

t = bpy.data.objects.new("t", None); sc.collection.objects.link(t); t.location = (12, 0, 0)
cam = bpy.data.objects.new("Камера", bpy.data.cameras.new("Камера")); sc.collection.objects.link(cam)
cam.data.lens = 45; cam.data.clip_start = 1; cam.location = (30, -55, 35)
tc = cam.constraints.new('TRACK_TO'); tc.target = t; tc.track_axis = 'TRACK_NEGATIVE_Z'; tc.up_axis = 'UP_Y'
sc.camera = cam
sun = bpy.data.objects.new("Солнце", bpy.data.lights.new("Солнце", "SUN"))
sun.data.energy = 3.5
sun.rotation_euler = (math.radians(35), math.radians(10), math.radians(40))
sc.collection.objects.link(sun)
sc.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("saved", OUT)
