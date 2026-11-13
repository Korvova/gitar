# 4 модуля v5 вдоль струн: повёрнут/прямой/повёрнут/прямой (вплотную), пальцы шаг 24 — синие маркеры
import bpy, os, math
D = os.path.join(os.path.expanduser("~"), "Documents", "App", "mcp-blender-cloude", "gitar_full_v5")
A, S, RF, RM, YM, FR = 2.5 * math.pi * 0.8, 11.0, 4.8, 4.4, 15.5, 240
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.unit_settings.scale_length = 0.001; sc.unit_settings.length_unit = 'MILLIMETERS'; sc.frame_end = FR
L = {"base": (.55, .58, .62, 1), "beam": (.7, .72, .76, 1), "motor": (.1, .1, .12, 1), "slider": (.2, .65, .3, 1),
     "pin_m": (.85, .2, .1, 1), "tray": (.62, .65, .7, 1), "lid": (.75, .77, .8, 1), "tape": (.12, .12, .25, 1), "pcb": (.15, .5, .2, 1),
     "btns": (.9, .15, .15, 1), "res": (.85, .7, .4, 1), "cart": (.1, .35, .9, 1), "cover": (.8, .82, .85, 1), "pads": (.1, .1, .4, 1), "coins_b": (.05, .05, .05, 1), "flo": (1, .5, .05, 1)}
mesh = {}
for f, c in L.items():
    bpy.ops.wm.stl_import(filepath=os.path.join(D, "asm", f + ".stl")); o = bpy.context.selected_objects[0]
    m = bpy.data.materials.new(f); m.diffuse_color = c; o.data.materials.append(m); mesh[f] = o.data; bpy.data.objects.remove(o)
OFF = [(8.5, False, 0), (48.1, False, 0), (110.3, True, 0), (149.9, True, 0)]   # (Y, повёрнут, удлинитель)       # смещение по Y, повёрнут на 180
FING = [43.2 + 24 * i for i in range(4)]
pm = bpy.data.materials.new("палец"); pm.diffuse_color = (.2, .6, 1, .5)
for i, (oy, rot, ext) in enumerate(OFF):
    e = bpy.data.objects.new("Модуль %d%s" % (i + 1, " (повёрнут)" if rot else ""), None); sc.collection.objects.link(e)
    e.location = (0, oy, 0); e.rotation_euler[2] = math.pi if rot else 0
    ob = {}
    for f in L:
        if (f in ('cart', 'cover', 'coin')) == bool(ext) and f in ('cart', 'cover', 'coin', 'cart_e', 'cover_e', 'coin_e'): continue
        if f in ('cart_e', 'cover_e', 'coin_e') and not ext: continue
        for k in ((1, 2) if f == "flo" else (1,)):
            o = bpy.data.objects.new("%s %d.%d" % (f, i + 1, k), mesh[f]); sc.collection.objects.link(o); o.parent = e; ob[(f, k)] = o
    ph = i * 0.17
    for fr in range(1, FR + 1, 2):
        s = S * math.sin(2 * math.pi * ((fr - 1) / FR + ph))
        for f in ("slider",): ob[(f, 1)].location.x = s; ob[(f, 1)].keyframe_insert("location", index=0, frame=fr)
        for f in ("cart", "cover"): ob[(f, 1)].location.x = 2 * s; ob[(f, 1)].keyframe_insert("location", index=0, frame=fr)
        for k, x in ((1, s - A), (2, s + A)):
            o = ob[("flo", k)]; o.location.x = x; o.rotation_euler[2] = -s / RF
            o.keyframe_insert("location", index=0, frame=fr); o.keyframe_insert("rotation_euler", index=2, frame=fr)
        ob[("pin_m", 1)].location.y = YM; ob[("pin_m", 1)].rotation_euler[2] = s / RM; ob[("pin_m", 1)].keyframe_insert("rotation_euler", index=2, frame=fr)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, FING[i], 31.5)); p = bpy.context.object
    p.name = "Палец %d (шаг 24, ложе на месте%s)" % (i + 1, FING[i] - (oy + (-18 if rot else 18))); p.scale = (14, 14, 2); p.data.materials.append(pm)
tg = bpy.data.objects.new("ц", None); sc.collection.objects.link(tg); tg.location = (0, 80, 15)
cam = bpy.data.objects.new("Камера", bpy.data.cameras.new("Камера")); sc.collection.objects.link(cam); cam.location = (150, -60, 140); cam.data.clip_start = 1
k = cam.constraints.new('TRACK_TO'); k.target = tg; k.track_axis = 'TRACK_NEGATIVE_Z'; k.up_axis = 'UP_Y'; sc.camera = cam
sc.frame_set(40); bpy.ops.wm.save_as_mainfile(filepath=os.path.join(D, "full_v5_x4.blend")); print("saved")
