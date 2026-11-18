# Концепт В (справа, компактный ~32 мм) рядом с текущим А (слева, 43.6). Анимация хода у В.
import bpy, os, math
D = os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.unit_settings.scale_length = 0.001; sc.unit_settings.length_unit = 'MILLIMETERS'; sc.frame_end = 240
YM, A, RF, RM, S, YG = 15.5, 2.5 * math.pi * 0.8, 4.8, 4.4, 11.0, 7.5
C = {"base": (.55, .58, .62, 1), "beam": (.7, .72, .76, 1), "fix": (.45, .48, .52, 1), "slider": (.2, .65, .3, 1), "flo": (1, .5, .05, 1),
     "cart": (.1, .35, .9, 1), "most": (.62, .65, .7, 1), "plat": (.6, .25, .7, 1), "gm": (.85, .2, .1, 1), "motor": (.1, .1, .12, 1),
     "pin_m": (.85, .2, .1, 1), "jacket": (.6, .25, .7, 1)}
def put(folder, n, x0, name):
    bpy.ops.wm.stl_import(filepath=os.path.join(D, folder, n + ".stl")); o = bpy.context.selected_objects[0]; o.name = name
    m = bpy.data.materials.new(name); m.diffuse_color = C[n]; o.data.materials.append(m); o.location.x = x0; return o
for n in ("base", "beam", "slider", "cart", "most", "motor"):
    put("asm", n, -40, "А · " + n)
for n in ("pin_m", "jacket"):
    o = put("asm", n, -40, "А · " + n); o.location.y = YM
for k in (-A, A):
    put("asm", "flo", -40 + k, "А · шестерня")
ob = {n: put("asm_C", n, 40, "В · " + n) for n in ("base", "beam", "fix", "slider", "cart", "most", "motor", "plat", "gm")}
ob["plat"].location.y = YM; ob["gm"].location.y = YM
f1, f2 = put("asm_C", "flo", 40, "В · шестерня 1"), put("asm_C", "flo", 40, "В · шестерня 2")
for f in range(1, 241, 2):
    s = S * math.sin(2 * math.pi * (f - 1) / 240)
    ob["slider"].location.x = 40 + s; ob["slider"].keyframe_insert("location", index=0, frame=f)
    ob["cart"].location.x = 40 + 2 * s; ob["cart"].keyframe_insert("location", index=0, frame=f)
    for o, x in ((f1, s - A), (f2, s + A)):
        o.location = (40 + x, YG, 0); o.rotation_euler[2] = -s / RF; o.keyframe_insert("location", frame=f); o.keyframe_insert("rotation_euler", index=2, frame=f)
    for o in (ob["gm"], ob["plat"]):
        o.rotation_euler[2] = s / RM; o.keyframe_insert("rotation_euler", index=2, frame=f)
tg = bpy.data.objects.new("ц", None); sc.collection.objects.link(tg); tg.location = (0, 12, 15)
cam = bpy.data.objects.new("Камера", bpy.data.cameras.new("Камера")); sc.collection.objects.link(cam); cam.location = (60, -150, 120); cam.data.clip_start = 1
c = cam.constraints.new('TRACK_TO'); c.target = tg; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'; sc.camera = cam
sc.frame_set(40); bpy.ops.wm.save_as_mainfile(filepath=os.path.join(D, "koncept_C.blend")); print("saved")
