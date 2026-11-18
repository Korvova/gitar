# Концепт Г: мотор лёжа, 4 модуля подряд с шагом 24 — тележки прямо под пальцами. Пробел — анимация (разные фазы).
import bpy, os, math
D = os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.unit_settings.scale_length = 0.001; sc.unit_settings.length_unit = 'MILLIMETERS'; sc.frame_end = 240
ZC, ZG, RF, RM = map(float, open(os.path.join(D, "asm_D", "params.txt")).read().split())
A, S = 2.5 * math.pi * 0.8, 11.0
C = {"base": (.55, .58, .62, 1), "beam": (.7, .72, .76, 1), "motor": (.1, .1, .12, 1), "plat": (.6, .25, .7, 1), "pin": (.85, .2, .1, 1),
     "slider": (.2, .65, .3, 1), "flo": (1, .5, .05, 1), "cart": (.1, .35, .9, 1)}
mesh = {}
for n, c in C.items():
    bpy.ops.wm.stl_import(filepath=os.path.join(D, "asm_D", n + ".stl")); o = bpy.context.selected_objects[0]
    m = bpy.data.materials.new(n); m.diffuse_color = c; o.data.materials.append(m); mesh[n] = o.data; bpy.data.objects.remove(o)
pm = bpy.data.materials.new("палец"); pm.diffuse_color = (.2, .6, 1, .55)
for i in range(4):
    e = bpy.data.objects.new("Модуль %d" % (i + 1), None); sc.collection.objects.link(e); e.location.y = 24.0 * i
    ob = {}
    for n in C:
        for k in ((0, 1) if n == "flo" else (0,)):
            o = bpy.data.objects.new("%s %d" % (n, i + 1), mesh[n]); sc.collection.objects.link(o); o.parent = e; ob[(n, k)] = o
    ob[("pin", 0)].location.z = ZC
    for f in range(1, 241, 3):
        s = S * math.sin(2 * math.pi * ((f - 1) / 240 + 0.2 * i))
        ob[("slider", 0)].location.x = s; ob[("slider", 0)].keyframe_insert("location", index=0, frame=f)
        ob[("cart", 0)].location.x = 2 * s; ob[("cart", 0)].keyframe_insert("location", index=0, frame=f)
        for k, x in ((0, s - A), (1, s + A)):
            o = ob[("flo", k)]; o.location = (x, 0, ZG); o.rotation_euler[1] = s / RF
            o.keyframe_insert("location", frame=f); o.keyframe_insert("rotation_euler", index=1, frame=f)
        ob[("pin", 0)].rotation_euler[1] = s / RM; ob[("pin", 0)].keyframe_insert("rotation_euler", index=1, frame=f)
    bpy.ops.mesh.primitive_cylinder_add(radius=5, depth=0.6, location=(0, 24.0 * i + 11.6, 33.0)); p = bpy.context.object; p.name = "Палец %d" % (i + 1); p.data.materials.append(pm); p.parent = None
tg = bpy.data.objects.new("ц", None); sc.collection.objects.link(tg); tg.location = (0, 45, 15)
cam = bpy.data.objects.new("Камера", bpy.data.cameras.new("Камера")); sc.collection.objects.link(cam); cam.location = (110, -60, 90); cam.data.clip_start = 1
c = cam.constraints.new('TRACK_TO'); c.target = tg; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'; sc.camera = cam
sc.frame_set(30); bpy.ops.wm.save_as_mainfile(filepath=os.path.join(D, "koncept_D_bokom.blend")); print("saved")
