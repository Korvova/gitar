# -*- coding: utf-8 -*-
"""Идея владельца 27.09 (вариант А): один палец двигает барабан прямо на валу мотора.

Мотор Ø36 лежит в голове грифа, вал вдоль грифа. На валу барабан Ø60 длиной 30 — он утоплен
в гриф у порожка, над фретбордом выступает дугой. В барабане у края дырка под кончик пальца.
Барабан поворачивается ±47° — дырка идёт по дуге поперёк грифа со струны 6 на струну 1.
Никаких лент, плеч и штырей: мотор ведёт палец напрямую.

Координаты: Y вдоль грифа (0 — порожек, голова в минусе), X поперёк, Z вверх (0 — ось барабана).
Запуск: "C:\\Program Files\\Blender Foundation\\Blender 5.1\\blender.exe" -b -P 2-0\\scene_baraban_idea.py
"""
import math
import os
import bpy

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Идея_барабан_палец.blend")
R, DRUM_L, HOLE_D = 30.0, 30.0, 18.0
NECK_W, NECK_TOP, NECK_BOT = 52.0, 10.0, -10.0     # фретборд на 20 мм ниже верха барабана
SWING = 47.0
FRAMES = 120
STRING_X = (-22.0, -13.2, -4.4, 4.4, 13.2, 22.0)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.unit_settings.system = 'METRIC'
sc.unit_settings.scale_length = 0.001
sc.unit_settings.length_unit = 'MILLIMETERS'
sc.frame_start, sc.frame_end = 1, FRAMES


def mat(name, rgba):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = rgba
    m.diffuse_color = rgba
    return m


def box(name, x0, x1, y0, y1, z0, z1, m):
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    ob = bpy.context.object
    ob.name = name
    ob.scale = (x1 - x0, y1 - y0, z1 - z0)
    bpy.ops.object.transform_apply(scale=True)
    ob.data.materials.append(m)
    return ob


def cyl_y(name, r, y0, y1, m, x=0.0, z=0.0, verts=96):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=y1 - y0,
                                        location=(x, (y0 + y1) / 2, z), rotation=(math.radians(90), 0, 0))
    ob = bpy.context.object
    ob.name = name
    if m:
        ob.data.materials.append(m)
    return ob


def boolean(target, cutter, op="DIFFERENCE"):
    mod = target.modifiers.new("b", "BOOLEAN")
    mod.operation = op
    mod.object = cutter
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)


C_NECK = mat("гриф", (0.85, 0.78, 0.66, 1))
C_FRET = mat("фретборд", (0.45, 0.30, 0.20, 1))
C_STR = mat("струны", (0.85, 0.85, 0.88, 1))
C_DRUM = mat("барабан", (0.25, 0.45, 0.80, 1))
C_MOT = mat("мотор", (0.25, 0.27, 0.30, 1))
C_FING = mat("палец", (0.95, 0.72, 0.60, 1))

# гриф: голова (y -70..-5) и сам гриф (y 0..220), у порожка вырез под барабан
neck = box("гриф", -NECK_W / 2, NECK_W / 2, -5, 220, NECK_BOT, NECK_TOP - 3, C_NECK)
fret = box("фретборд", -NECK_W / 2, NECK_W / 2, -5, 220, NECK_TOP - 3, NECK_TOP, C_FRET)
for ob in (neck, fret):
    boolean(ob, cyl_y("вырез", R + 1.0, 4.0, 6.0 + DRUM_L + 2, None))
head = box("голова грифа", -NECK_W / 2 - 4, NECK_W / 2 + 4, -75, -5, -24, NECK_TOP - 3, C_NECK)
boolean(head, cyl_y("вырез_мотор", 19, -70, -4, None))
# струны
for i, sx in enumerate(STRING_X):
    cyl_y("струна_%d" % (6 - i), 0.5 if i > 2 else 0.8, -5, 220, C_STR, x=sx, z=NECK_TOP + 1.2, verts=12)
    # лады
for k in range(1, 7):
    Ln = 650.0 * (1 - 2 ** (-k / 12))
    box("лад_%d" % k, -NECK_W / 2, NECK_W / 2, Ln - 0.8, Ln + 0.8, NECK_TOP, NECK_TOP + 1.2, C_STR)

# мотор лёжа в голове, вал вдоль грифа к барабану
cyl_y("мотор Ø36", 18, -64, -42, C_MOT)
cyl_y("вал", 3, -42, 6, C_MOT, verts=24)

# барабан с дыркой под палец: дырка сверху, радиально
drum = cyl_y("барабан Ø60", R, 6, 6 + DRUM_L, C_DRUM)
bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=HOLE_D / 2, depth=24, location=(0, 6 + DRUM_L / 2, R - 8), rotation=(0, 0, 0))   # rotation явно: оператор помнит прошлый поворот
boolean(drum, bpy.context.object)
finger = cyl_y("палец", 8, 6 + DRUM_L / 2 - 60, 6 + DRUM_L / 2 + 40, C_FING, verts=32)
finger.rotation_euler = (0, 0, 0)
finger.location = (0, 6 + DRUM_L / 2, R - 2)
finger.rotation_euler = (math.radians(0), 0, 0)
# палец: цилиндр вдоль Z из дырки вверх (как кончик пальца, вставленный сверху)
bpy.data.objects.remove(finger, do_unlink=True)
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=7.5, depth=40, location=(0, 6 + DRUM_L / 2, R - 12 + 20), rotation=(0, 0, 0))
finger = bpy.context.object
finger.name = "кончик пальца"
finger.data.materials.append(C_FING)
bpy.context.view_layer.update()            # иначе matrix_world барабана ещё единичная, и палец встаёт боком
bpy.ops.object.select_all(action='DESELECT')
finger.select_set(True)
drum.select_set(True)
bpy.context.view_layer.objects.active = drum
bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

# ось вращения барабана = ось Y (x=0, z=0): барабан уже стоит на ней
drum.rotation_mode = 'XYZ'
for f in range(1, FRAMES + 1, 2):
    th = SWING * math.sin(2 * math.pi * (f - 1) / (FRAMES - 1))
    drum.rotation_euler = (math.radians(90), math.radians(th), 0)   # 90° по X — ось барабана вдоль грифа, th — поворот вокруг неё
    drum.keyframe_insert("rotation_euler", frame=f)

labels = []

cam = bpy.data.objects.new("Камера", bpy.data.cameras.new("Камера"))
sc.collection.objects.link(cam)
cam.data.clip_start, cam.data.clip_end = 1, 10000
cam.location = (160, -120, 150)
cam.rotation_euler = (math.radians(55), 0, math.radians(52))
sc.camera = cam
for t in labels:
    c = t.constraints.new('TRACK_TO')
    c.target = cam
    c.track_axis = 'TRACK_Z'
    c.up_axis = 'UP_Y'
sun = bpy.data.objects.new("Солнце", bpy.data.lights.new("Солнце", "SUN"))
sun.data.energy = 3
sun.rotation_euler = (math.radians(40), math.radians(20), math.radians(30))
sc.collection.objects.link(sun)
sc.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("saved", OUT)
