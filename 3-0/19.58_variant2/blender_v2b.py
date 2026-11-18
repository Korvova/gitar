# -*- coding: utf-8 -*-
# Сцена варианта 2Б (стойка спереди): пробел — анимация, тележка ±22 спереди над шестернями. Запуск: blender -b -P blender_v2.py
import bpy, os, math
D = os.path.dirname(os.path.abspath(__file__))
RF, RM, A, YM, S = 4.8, 4.4, 2.5 * math.pi * 0.8, 15.5, 11.0
FR = 240
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.unit_settings.scale_length = 0.001; sc.unit_settings.length_unit = 'MILLIMETERS'; sc.frame_end = FR
def imp(f, name, col, loc=(0, 0, 0)):
    bpy.ops.wm.stl_import(filepath=os.path.join(D, "asm_b", f + ".stl")); o = bpy.context.selected_objects[0]; o.name = name
    m = bpy.data.materials.new(name); m.diffuse_color = col; o.data.materials.append(m); o.location = loc; return o
imp("base", "Основание", (.6, .62, .66, 1)); imp("rack", "Рейка неподвижная", (.45, .47, .5, 1)); imp("beam", "Брусок", (.7, .72, .76, 1))
imp("motor", "Мотор", (.12, .12, .14, 1)); imp("hall", "49E", (.2, .2, .55, 1)); imp("stojka", "Стойка", (.55, .57, .6, 1)); imp("perekladina", "Перекладина", (.4, .42, .45, 1))
jk = imp("jacket", "Колпак ротора", (.85, .3, .15, 1), (0, YM, 0)); pm = imp("pin_m", "Шестерня мотора", (.85, .2, .1, 1), (0, YM, 0))
sl = imp("slider", "Ползун", (.2, .55, .3, 1)); f1 = imp("flo", "Плавающая 1", (1, .6, .1, 1)); f2 = imp("flo", "Плавающая 2", (1, .6, .1, 1))
ct = imp("cart", "Тележка", (.15, .4, .9, 1))
for fr in range(1, FR + 1):
    s = S * math.sin(2 * math.pi * (fr - 1) / (FR - 1))
    sl.location.x = s; sl.keyframe_insert("location", index=0, frame=fr)
    for o, dx in ((f1, -A), (f2, A)):
        o.location.x = s + dx; o.rotation_euler.z = s / RF
        o.keyframe_insert("location", index=0, frame=fr); o.keyframe_insert("rotation_euler", index=2, frame=fr)
    for o in (pm, jk):
        o.rotation_euler.z = s / RM; o.keyframe_insert("rotation_euler", index=2, frame=fr)
    ct.location.x = 2 * s; ct.keyframe_insert("location", index=0, frame=fr)
cam = bpy.data.objects.new("Камера", bpy.data.cameras.new("Камера")); sc.collection.objects.link(cam); cam.location = (70, -90, 75); cam.data.clip_start = 1
tg = bpy.data.objects.new("ц", None); sc.collection.objects.link(tg); tg.location = (0, 8, 15)
k = cam.constraints.new('TRACK_TO'); k.target = tg; k.track_axis = 'TRACK_NEGATIVE_Z'; k.up_axis = 'UP_Y'; sc.camera = cam
sc.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(D, "variant2b.blend")); print("saved")
