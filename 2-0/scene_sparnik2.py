# -*- coding: utf-8 -*-
r"""Сцена: макет «второй диск у тележки» (gitara_sparnik2.py, стол 100). Было: стенд «спарник» (gitara_sparnik.py, стол 99) — мотор крутит диск R20, свободный диск повторяет,
планка ходит параллельно, Т-тележка в пересечении прорезей (мостик поперёк, планка вдоль) ходит поперёк ±20.
Дно и мостик прозрачные. Пробел — анимация (2 оборота). Запуск: blender -b -P 2-0\scene_sparnik.py"""
import math
import os
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "Print", "Print")
OUT = os.path.join(HERE, "Макет_диск_у_тележки.blend")
MY, YI, R, D = 147.0, 27.0, 20.0, 120.0
YC = YI + D / 2
Z_D0, Z_BAR, Z_DK0, D0, Z_SL0 = 3.3, 5.9, 8.0, -2.2, 10.3
FRAMES = 240

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
        try:
            m.surface_render_method = 'BLENDED'
        except Exception:
            pass
    m.diffuse_color = (rgba[0], rgba[1], rgba[2], alpha)
    return m


def stl(fname, name, m, loc=(0, 0, 0)):
    bpy.ops.wm.stl_import(filepath=os.path.join(P, fname + ".stl"))
    ob = bpy.context.selected_objects[0]
    ob.name = name
    ob.data.materials.clear()
    ob.data.materials.append(m)
    ob.location = loc
    return ob


stl("spar2_base", "дно", mat("дно", (0.8, 0.8, 0.84, 1), 0.35))
stl("gdk_spacer0_x2", "проставка", mat("проставка", (0.6, 0.6, 0.62, 1)), (0, MY, 0))
stl("gdk_motor0_model", "мотор", mat("мотор", (0.25, 0.25, 0.28, 1)), (0, MY, -4.0))
hub = stl("spar_stupica", "ступица мотора", mat("ступица", (0.6, 0.25, 0.25, 1)), (0, MY, D0))
dm = stl("spar_disk_motor", "диск на моторе", mat("диск мотора", (0.85, 0.35, 0.35, 1)), (0, MY, Z_D0))
di = stl("spar2_disk", "второй диск (у тележки)", mat("второй диск", (0.85, 0.55, 0.55, 1)), (0, YI, Z_D0))
bar = stl("spar2_planka", "планка", mat("планка", (0.30, 0.70, 0.40, 1)), (R, YI, Z_BAR))
stl("spar2_most", "мостик с окном", mat("мостик", (0.85, 0.82, 0.76, 1), 0.3), (0, YI, Z_DK0))
tl = stl("spar2_salazki", "салазки-тележка", mat("тележка", (0.95, 0.72, 0.30, 1)), (R, YI, Z_SL0))

for f in range(1, FRAMES + 1):
    th = 2 * math.pi * 2 * (f - 1) / (FRAMES - 1)
    for ob in (hub, dm, di):
        ob.rotation_euler = (0, 0, th)
        ob.keyframe_insert("rotation_euler", index=2, frame=f)
    bar.location = (R * math.cos(th), YI + R * math.sin(th), Z_BAR)
    bar.keyframe_insert("location", frame=f)
    tl.location.x = R * math.cos(th)                 # салазки только поперёк
    tl.keyframe_insert("location", index=0, frame=f)

tgt = bpy.data.objects.new("цель", None)
sc.collection.objects.link(tgt)
tgt.location = (0, 70, 0)
cam = bpy.data.objects.new("Камера", bpy.data.cameras.new("Камера"))
sc.collection.objects.link(cam)
cam.data.clip_start, cam.data.clip_end, cam.data.lens = 1, 50000, 35
cam.location = (120, -40, 200)
tc = cam.constraints.new('TRACK_TO')
tc.target, tc.track_axis, tc.up_axis = tgt, 'TRACK_NEGATIVE_Z', 'UP_Y'
sc.camera = cam
sun = bpy.data.objects.new("Солнце", bpy.data.lights.new("Солнце", "SUN"))
sun.data.energy = 3
sun.rotation_euler = (math.radians(30), math.radians(15), math.radians(30))
sc.collection.objects.link(sun)
sc.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("saved", OUT)
