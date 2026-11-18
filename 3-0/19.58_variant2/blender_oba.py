# -*- coding: utf-8 -*-
# Вариант 2 (слева) и вариант 2Б (справа) в одной сцене, анимация сохраняется. Запуск: blender -b -P blender_oba.py
import bpy, os
D = os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.unit_settings.scale_length = 0.001; sc.unit_settings.length_unit = 'MILLIMETERS'; sc.frame_end = 240
for fn, dx, tag in (("variant2.blend", -35.0, "в2"), ("variant2b.blend", 35.0, "в2Б")):
    with bpy.data.libraries.load(os.path.join(D, fn), link=False) as (src, dst):
        dst.objects = [n for n in src.objects if n not in ("Камера", "ц")]
    root = bpy.data.objects.new("Вариант " + tag, None); sc.collection.objects.link(root); root.location.x = dx
    for o in dst.objects:
        if o is None:
            continue
        sc.collection.objects.link(o); o.name = tag + ": " + o.name; o.parent = root
cam = bpy.data.objects.new("Камера", bpy.data.cameras.new("Камера")); sc.collection.objects.link(cam); cam.location = (40, -160, 120); cam.data.clip_start = 1
tg = bpy.data.objects.new("ц", None); sc.collection.objects.link(tg); tg.location = (0, 0, 12)
k = cam.constraints.new('TRACK_TO'); k.target = tg; k.track_axis = 'TRACK_NEGATIVE_Z'; k.up_axis = 'UP_Y'; sc.camera = cam
sc.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(D, "variant2_i_2b.blend")); print("saved")
