# -*- coding: utf-8 -*-
# Концепт В в ряд ×4 (шаг 30), площадки 15 мм со сдвигом ±3/±9 — пальцы на шаге 24. Пробел — анимация, тележки ходят независимо.
import bpy, os, math
D = os.path.dirname(os.path.abspath(__file__)); P = os.path.join(D, "asm_V4")
v = list(map(float, open(os.path.join(P, "params.txt")).read().split())); YS, YM, YG = v[:4], v[4], v[5]
A, RF, RM, S, FR = 2.5 * math.pi * 0.8, 4.8, 4.4, 11.0, 240
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.unit_settings.scale_length = 0.001; sc.unit_settings.length_unit = 'MILLIMETERS'; sc.frame_end = FR
C = {"base_row": (.6, .62, .66, 1), "fix": (.45, .48, .52, 1), "beam": (.7, .72, .76, 1), "most": (.62, .65, .7, 1), "motor": (.12, .12, .14, 1),
     "slider": (.2, .6, .3, 1), "flo": (1, .55, .05, 1), "cart": (.1, .35, .9, 1), "gm": (.85, .2, .1, 1), "plat": (.6, .25, .7, 1), "pad": (.35, .65, 1, 1)}
mesh = {}
def get(n):
    if n not in mesh:
        bpy.ops.wm.stl_import(filepath=os.path.join(P, n + ".stl")); o = bpy.context.selected_objects[0]; mesh[n] = o.data; bpy.data.objects.remove(o)
        m = bpy.data.materials.new(n); m.diffuse_color = C.get(n, C["pad"]); mesh[n].materials.append(m)
    return mesh[n]
def obj(n, name, loc=(0, 0, 0)):
    o = bpy.data.objects.new(name, get(n)); sc.collection.objects.link(o); o.location = loc; return o
obj("base_row", "Основание ряда")
for i, y in enumerate(YS):
    for n in ("fix", "beam", "most", "motor"):
        obj(n, "%s %d" % (n, i + 1), (0, y, 0))
    pl = obj("plat", "платформа %d" % (i + 1), (0, y + YM, 0)); g = obj("gm", "шестерня мотора %d" % (i + 1), (0, y + YM, 0))
    sl = obj("slider", "ползун %d" % (i + 1), (0, y, 0)); f1 = obj("flo", "плав %d.1" % (i + 1)); f2 = obj("flo", "плав %d.2" % (i + 1))
    ct = obj("cart", "тележка %d" % (i + 1), (0, y, 0)); pd = obj("pad%d" % i, "площадка %d" % (i + 1), (0, y, 0))
    for f in range(1, FR + 1, 2):
        s = S * math.sin(2 * math.pi * ((f - 1) / FR * (1 + i % 2) + 0.17 * i))
        sl.location.x = s; sl.keyframe_insert("location", index=0, frame=f)
        for o in (ct, pd):
            o.location.x = 2 * s; o.keyframe_insert("location", index=0, frame=f)
        for o, x in ((f1, s - A), (f2, s + A)):
            o.location = (x, y + YG, 0); o.rotation_euler.z = -s / RF; o.keyframe_insert("location", frame=f); o.keyframe_insert("rotation_euler", index=2, frame=f)
        for o in (g, pl):
            o.rotation_euler.z = s / RM; o.keyframe_insert("rotation_euler", index=2, frame=f)
tg = bpy.data.objects.new("ц", None); sc.collection.objects.link(tg); tg.location = (0, 0, 12)
cam = bpy.data.objects.new("Камера", bpy.data.cameras.new("Камера")); sc.collection.objects.link(cam); cam.location = (150, -110, 130); cam.data.clip_start = 1
k = cam.constraints.new('TRACK_TO'); k.target = tg; k.track_axis = 'TRACK_NEGATIVE_Z'; k.up_axis = 'UP_Y'; sc.camera = cam
sc.frame_set(1); bpy.ops.wm.save_as_mainfile(filepath=os.path.join(D, "ryad_V4.blend")); print("saved")
