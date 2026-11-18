# -*- coding: utf-8 -*-
# Один модуль концепта В: тележка целиком за краем своего мотора, на балке. Пробел — анимация.
import bpy, os, math
D = os.path.dirname(os.path.abspath(__file__)); P = os.path.join(D, "asm_zm")
YM, YG, A, RF, RM, S, FR = 15.5, 7.5, 2.5 * math.pi * 0.8, 4.8, 4.4, 11.0, 240
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.unit_settings.scale_length = 0.001; sc.unit_settings.length_unit = 'MILLIMETERS'; sc.frame_end = FR
C = {"base": (.6, .62, .66, 1), "fix": (.45, .48, .52, 1), "beam_k": (.7, .72, .76, 1), "beam": (.35, .37, .4, 1), "motor": (.12, .12, .14, 1),
     "slider": (.2, .6, .3, 1), "flo": (1, .55, .05, 1), "cart": (.15, .45, .95, 1), "gm": (.85, .2, .1, 1), "plat": (.6, .25, .7, 1)}
def imp(n, name, loc=(0, 0, 0)):
    bpy.ops.wm.stl_import(filepath=os.path.join(P, n + ".stl")); o = bpy.context.selected_objects[0]; o.name = name
    m = bpy.data.materials.new(name); m.diffuse_color = C[n]; o.data.materials.append(m); o.location = loc; return o
for n, t in (("base", "основание"), ("fix", "неподвижная рейка"), ("beam_k", "брусок ползуна"), ("beam", "балка за мотором"), ("motor", "мотор")):
    imp(n, t)
pl = imp("plat", "платформа ротора", (0, YM, 0)); g = imp("gm", "шестерня мотора", (0, YM, 0)); sl = imp("slider", "ползун")
f1 = imp("flo", "плавающая 1"); f2 = imp("flo", "плавающая 2"); ct = imp("cart", "тележка")
for f in range(1, FR + 1, 2):
    s = S * math.sin(2 * math.pi * (f - 1) / FR)
    sl.location.x = s; sl.keyframe_insert("location", index=0, frame=f)
    ct.location.x = 2 * s; ct.keyframe_insert("location", index=0, frame=f)
    for o, x in ((f1, s - A), (f2, s + A)):
        o.location = (x, YG, 0); o.rotation_euler.z = s / RF; o.keyframe_insert("location", frame=f); o.keyframe_insert("rotation_euler", index=2, frame=f)
    for o in (g, pl):
        o.rotation_euler.z = s / RM; o.keyframe_insert("rotation_euler", index=2, frame=f)
tg = bpy.data.objects.new("ц", None); sc.collection.objects.link(tg); tg.location = (0, 8, 15)
cam = bpy.data.objects.new("Камера", bpy.data.cameras.new("Камера")); sc.collection.objects.link(cam); cam.location = (90, -80, 70); cam.data.clip_start = 1
k = cam.constraints.new('TRACK_TO'); k.target = tg; k.track_axis = 'TRACK_NEGATIVE_Z'; k.up_axis = 'UP_Y'; sc.camera = cam
sc.frame_set(1); bpy.ops.wm.save_as_mainfile(filepath=os.path.join(D, "modul_za_motorom.blend")); print("saved")
