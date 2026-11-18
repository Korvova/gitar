# -*- coding: utf-8 -*-
# Пара: модули А и Б на общем основании, тележки на шаге 24, ходят независимо. Пробел — анимация. Запуск: blender -b -P blender_para.py
import bpy, os, math
D0 = os.path.dirname(os.path.abspath(__file__)); P = os.path.join(D0, "asm_para")
D = float(open(os.path.join(P, "D.txt")).read())
RF, RM, A, YM, S, FR = 4.8, 4.4, 2.5 * math.pi * 0.8, 15.5, 11.0, 240
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.unit_settings.scale_length = 0.001; sc.unit_settings.length_unit = 'MILLIMETERS'; sc.frame_end = FR
def imp(f, name, col, loc=(0, 0, 0)):
    bpy.ops.wm.stl_import(filepath=os.path.join(P, f + ".stl")); o = bpy.context.selected_objects[0]; o.name = name
    m = bpy.data.materials.new(name); m.diffuse_color = col; o.data.materials.append(m); o.location = loc; return o
GR, DK = (.6, .62, .66, 1), (.45, .47, .5, 1)
imp("base", "Основание пары", GR)
for f, n, c in (("rackA", "Рейка А", DK), ("rackB", "Рейка Б", DK), ("beamA", "Брусок А", (.7, .72, .76, 1)), ("beamB", "Брусок Б", (.7, .72, .76, 1)),
                ("motorA", "Мотор А", (.12, .12, .14, 1)), ("motorB", "Мотор Б", (.12, .12, .14, 1)), ("hallA", "49E А", (.2, .2, .55, 1)), ("hallB", "49E Б", (.2, .2, .55, 1)),
                ("per", "Перекладина под тележкой Б", DK)):
    imp(f, n, c)
mods = []
for tag, y0, cartf, ph, k in (("А", 0.0, "cartA", 0.0, 1), ("Б", D, "cartB", 0.3, 2)):
    jk = imp("jacket", "Колпак " + tag, (.85, .3, .15, 1), (0, YM + y0, 0)); pm = imp("pin_m", "Шестерня мотора " + tag, (.85, .2, .1, 1), (0, YM + y0, 0))
    sl = imp("slider", "Ползун " + tag, (.2, .55, .3, 1), (0, y0, 0)); f1 = imp("flo", "Плавающая " + tag + "1", (1, .6, .1, 1), (0, y0, 0))
    f2 = imp("flo", "Плавающая " + tag + "2", (1, .6, .1, 1), (0, y0, 0)); ct = imp(cartf, "Тележка " + tag, (.15, .4, .9, 1), (0, y0, 0))
    mods.append((jk, pm, sl, f1, f2, ct, ph, k))
for fr in range(1, FR + 1):
    t = (fr - 1) / (FR - 1)
    for jk, pm, sl, f1, f2, ct, ph, k in mods:
        s = S * math.sin(2 * math.pi * (k * t + ph))
        sl.location.x = s; sl.keyframe_insert("location", index=0, frame=fr)
        for o, dx in ((f1, -A), (f2, A)):
            o.location.x = s + dx; o.rotation_euler.z = s / RF
            o.keyframe_insert("location", index=0, frame=fr); o.keyframe_insert("rotation_euler", index=2, frame=fr)
        for o in (pm, jk):
            o.rotation_euler.z = s / RM; o.keyframe_insert("rotation_euler", index=2, frame=fr)
        ct.location.x = 2 * s; ct.keyframe_insert("location", index=0, frame=fr)
cam = bpy.data.objects.new("Камера", bpy.data.cameras.new("Камера")); sc.collection.objects.link(cam); cam.location = (110, -90, 110); cam.data.clip_start = 1
tg = bpy.data.objects.new("ц", None); sc.collection.objects.link(tg); tg.location = (0, D / 2, 12)
kk = cam.constraints.new('TRACK_TO'); kk.target = tg; kk.track_axis = 'TRACK_NEGATIVE_Z'; kk.up_axis = 'UP_Y'; sc.camera = cam
sc.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(D0, "para.blend")); print("saved")
