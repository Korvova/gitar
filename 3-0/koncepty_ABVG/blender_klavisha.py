# Модуль-клавиша (папка ../19.65_klavisha_*): сборка + ход тележки + наклон модуля на оси (наклон в сцене ×4 для наглядности). Запуск: blender -b -P blender_klavisha.py -- P
import bpy, os, sys, math
MOD = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else "P"
D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), os.environ.get("DIR", "19.65_klavisha_%s") % MOD if "%s" in os.environ.get("DIR", "19.65_klavisha_%s") else os.environ["DIR"]); A_ = os.path.join(D, "asm")
YM, YG, A, RF, RM = map(float, open(os.path.join(A_, "params.txt")).read().split()); S = 11.0
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.unit_settings.scale_length = 0.001; sc.unit_settings.length_unit = 'MILLIMETERS'; sc.frame_end = 240
C = {"frame": (.35, .3, .25, 1), "rack_br": (.5, .45, .4, 1), "base": (.6, .62, .66, 1), "rack": (.45, .48, .52, 1), "beam": (.4, .42, .46, 1), "legs": (.55, .57, .6, 1), "cart": (.15, .4, .9, 1), "btns": (.9, .15, .15, 1),
     "posts": (.78, .78, .72, 1), "sens": (.05, .05, .3, 1), "slider": (.2, .6, .3, 1), "flo": (1, .55, .05, 1), "brusok": (.7, .72, .76, 1),
     "gm": (.85, .2, .1, 1), "plat": (.6, .25, .7, 1), "mags": (.9, .9, .95, 1), "motor": (.12, .12, .14, 1)}
ob = {}
def put(n, name):
    bpy.ops.wm.stl_import(filepath=os.path.join(A_, n + ".stl")); o = bpy.context.selected_objects[0]; o.name = name
    m = bpy.data.materials.new(name); m.diffuse_color = C[n]; o.data.materials.append(m); return o
for n in C:
    if not os.path.exists(os.path.join(A_, n + ".stl")): continue
    if n == "flo":
        ob["f1"] = put(n, "плавающая шестерня 1"); ob["f2"] = put(n, "плавающая шестерня 2")
    else:
        ob[n] = put(n, n)
for n in ("gm", "plat", "mags"):
    ob[n].location.y = YM
for f in range(1, 241, 2):
    s = S * math.sin(2 * math.pi * (f - 1) / 240)
    ob["slider"].location.x = s; ob["slider"].keyframe_insert("location", index=0, frame=f)
    ob["cart"].location.x = 2 * s; ob["cart"].keyframe_insert("location", index=0, frame=f)
    for k, x in (("f1", s - A), ("f2", s + A)):
        ob[k].location = (x, YG, 0); ob[k].rotation_euler[2] = s / RF; ob[k].keyframe_insert("location", frame=f); ob[k].keyframe_insert("rotation_euler", index=2, frame=f)
    for n in ("gm", "plat", "mags"):
        ob[n].rotation_euler[2] = s / RM; ob[n].keyframe_insert("rotation_euler", index=2, frame=f)
tg = bpy.data.objects.new("ц", None); sc.collection.objects.link(tg); tg.location = (0, 12, 12)
cam = bpy.data.objects.new("Камера", bpy.data.cameras.new("Камера")); sc.collection.objects.link(cam); cam.location = (80, -70, 75); cam.data.clip_start = 1
k = cam.constraints.new('TRACK_TO'); k.target = tg; k.track_axis = 'TRACK_NEGATIVE_Z'; k.up_axis = 'UP_Y'; sc.camera = cam
kv = list(map(float, open(os.path.join(A_, "klav.txt")).read().split())); Y_PIV, ANG = kv[0], kv[1]; Z_PIV = kv[2] if len(kv) > 2 else 0.0
piv = bpy.data.objects.new("ось качания", None); sc.collection.objects.link(piv); piv.location = (0, Y_PIV, Z_PIV); piv.empty_display_type = 'ARROWS'; piv.empty_display_size = 30; bpy.context.view_layer.update()
for n, o in list(ob.items()):
    if n in ("frame", "btns"): continue
    o.parent = piv; o.matrix_parent_inverse = piv.matrix_world.inverted()
for f in range(1, 241):
    ph = (f - 1) % 40
    k = 1.0 if 8 <= ph < 22 else 0.0                                                # нажатие каждые 40 кадров
    piv.rotation_euler[0] = math.radians(ANG * float(os.environ.get("EXAG", "4")) * k); piv.keyframe_insert("rotation_euler", index=0, frame=f)
sc.frame_set(1); bpy.ops.wm.save_as_mainfile(filepath=os.path.join(D, os.environ.get("BLEND", "klavisha_%s") % MOD + ".blend")); print("saved")
