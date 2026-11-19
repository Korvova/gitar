# -*- coding: utf-8 -*-
# Ряд из пар: З1 П1 | П2 З2 (З — тележка за мотором на балке, П — тележка на половине мотора). Пробел — анимация.
import bpy, os, math
D = os.path.dirname(os.path.abspath(__file__)); P = os.path.join(D, "asm_V4d")
v = list(map(float, open(os.path.join(P, "params.txt")).read().split())); CM, YM, YG = v[:4], v[4], v[5]
ROT = [True, True, False, False]; TYPE = ["З", "П", "П", "З"]
A, RF, RM, S, FR = 2.5 * math.pi * 0.8, 4.8, 4.4, 11.0, 240
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.unit_settings.scale_length = 0.001; sc.unit_settings.length_unit = 'MILLIMETERS'; sc.frame_end = FR
C = {"base_row": (.6, .62, .66, 1), "fix": (.45, .48, .52, 1), "fix_p": (.45, .48, .52, 1), "beam_k": (.7, .72, .76, 1), "beam_z": (.35, .37, .4, 1), "motor": (.12, .12, .14, 1),
     "slider": (.2, .6, .3, 1), "flo": (1, .55, .05, 1), "cart_z": (.15, .45, .95, 1), "cart_h": (.1, .35, .85, 1), "gm": (.85, .2, .1, 1), "plat": (.6, .25, .7, 1)}
mesh = {}
def get(n):
    if n not in mesh:
        bpy.ops.wm.stl_import(filepath=os.path.join(P, n + ".stl")); o = bpy.context.selected_objects[0]; mesh[n] = o.data; bpy.data.objects.remove(o)
        m = bpy.data.materials.new(n); m.diffuse_color = C[n]; mesh[n].materials.append(m)
    return mesh[n]
def obj(n, name, parent=None, loc=(0, 0, 0)):
    o = bpy.data.objects.new(name, get(n)); sc.collection.objects.link(o); o.parent = parent; o.location = loc; return o
obj("base_row", "Основание ряда")
for i in range(4):
    e = bpy.data.objects.new("Модуль %d (%s)" % (i + 1, TYPE[i]), None); sc.collection.objects.link(e)
    e.location = (0, CM[i], 0); e.rotation_euler.z = math.pi if ROT[i] else 0
    for n in (("fix",) if TYPE[i] == "З" else ("fix_p",)) + ("beam_k", "motor") + (("beam_z",) if TYPE[i] == "З" else ()):
        obj(n, "%s %d" % (n, i + 1), e, (0, -YM, 0))
    pl = obj("plat", "платформа %d" % (i + 1), e); g = obj("gm", "шестерня мотора %d" % (i + 1), e)
    sl = obj("slider", "ползун %d" % (i + 1), e, (0, -YM, 0)); f1 = obj("flo", "плав %d.1" % (i + 1), e); f2 = obj("flo", "плав %d.2" % (i + 1), e)
    ct = obj("cart_z" if TYPE[i] == "З" else "cart_h", "тележка %d" % (i + 1), e, (0, -YM, 0))
    for f in range(1, FR + 1, 2):
        s = S * math.sin(2 * math.pi * ((f - 1) / FR * (1 + i % 2) + 0.17 * i))
        sl.location.x = s; sl.keyframe_insert("location", index=0, frame=f)
        ct.location.x = 2 * s; ct.keyframe_insert("location", index=0, frame=f)
        for o, x in ((f1, s - A), (f2, s + A)):
            o.location = (x, YG - YM, 0); o.rotation_euler.z = s / RF; o.keyframe_insert("location", frame=f); o.keyframe_insert("rotation_euler", index=2, frame=f)
        for o in (g, pl):
            o.rotation_euler.z = s / RM; o.keyframe_insert("rotation_euler", index=2, frame=f)
tg = bpy.data.objects.new("ц", None); sc.collection.objects.link(tg); tg.location = (0, 0, 12)
cam = bpy.data.objects.new("Камера", bpy.data.cameras.new("Камера")); sc.collection.objects.link(cam); cam.location = (160, -120, 140); cam.data.clip_start = 1
k = cam.constraints.new('TRACK_TO'); k.target = tg; k.track_axis = 'TRACK_NEGATIVE_Z'; k.up_axis = 'UP_Y'; sc.camera = cam
sc.frame_set(1); bpy.ops.wm.save_as_mainfile(filepath=os.path.join(D, "ryad_V4d.blend")); print("saved")
