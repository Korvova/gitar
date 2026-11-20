# Пара З + П в окантовке 8 мм рядом (как в ряду: оба развёрнуты, хвост З к задней части П), окантовки касаются.
# Запуск: blender -b -P blender_para8.py
import bpy, os, math
R0 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.unit_settings.scale_length = 0.001; sc.unit_settings.length_unit = 'MILLIMETERS'; sc.frame_end = 240
C = {"frame": (.35, .3, .25, 1), "base": (.6, .62, .66, 1), "rack": (.45, .48, .52, 1), "beam": (.4, .42, .46, 1), "cart": (.15, .4, .9, 1), "btns": (.9, .15, .15, 1),
     "posts": (.78, .78, .72, 1), "sens": (.05, .05, .3, 1), "slider": (.2, .6, .3, 1), "flo": (1, .55, .05, 1), "brusok": (.7, .72, .76, 1),
     "gm": (.85, .2, .1, 1), "plat": (.6, .25, .7, 1), "mags": (.9, .9, .95, 1), "motor": (.12, .12, .14, 1)}
def put(A_, n, name, parent):
    bpy.ops.wm.stl_import(filepath=os.path.join(A_, n + ".stl")); o = bpy.context.selected_objects[0]; o.name = name
    m = bpy.data.materials.new(name); m.diffuse_color = C[n]; o.data.materials.append(m); o.parent = parent; return o
def module(mod, cy, phase):
    A_ = os.path.join(R0, "19.67_okantovka8_%s" % mod, "asm")
    YM, YG, A, RF, RM = map(float, open(os.path.join(A_, "params.txt")).read().split())
    yp, ang, zp = map(float, open(os.path.join(A_, "klav.txt")).read().split())
    nm = "З" if mod == "Z" else "П"
    E = bpy.data.objects.new("модуль " + nm, None); sc.collection.objects.link(E); E.location = (0, cy, 0); E.rotation_euler[2] = math.pi
    Pv = bpy.data.objects.new(nm + " ось качания", None); sc.collection.objects.link(Pv); Pv.parent = E; Pv.location = (0, yp, zp)
    ob = {}
    for n in C:
        if not os.path.exists(os.path.join(A_, n + ".stl")): continue
        if n == "flo":
            for k in (1, 2):
                o = put(A_, n, "%s плав.%d" % (nm, k), Pv); ob["f%d" % k] = o
            continue
        o = put(A_, n, "%s %s" % (nm, n), E if n in ("frame", "btns") else Pv); ob[n] = o
    for n, o in ob.items():
        if o.parent == Pv: o.location = (0, -yp, -zp)
    for f in range(1, 241, 2):
        s = 11.0 * math.sin(2 * math.pi * ((f - 1) / 240 + phase))
        for n, x in (("slider", s), ("cart", 2 * s)):
            ob[n].location = (x, -yp, -zp); ob[n].keyframe_insert("location", frame=f)
        for k, x in (("f1", s - A), ("f2", s + A)):
            ob[k].location = (x, YG - yp, -zp); ob[k].rotation_euler[2] = s / RF; ob[k].keyframe_insert("location", frame=f); ob[k].keyframe_insert("rotation_euler", index=2, frame=f)
        for n in ("gm", "plat", "mags"):
            ob[n].location = (0, YM - yp, -zp); ob[n].rotation_euler[2] = s / RM; ob[n].keyframe_insert("location", frame=f); ob[n].keyframe_insert("rotation_euler", index=2, frame=f)
    for f in range(1, 241):
        ph = (f - 1 + int(phase * 80)) % 40
        Pv.rotation_euler[0] = math.radians(ang * (1.0 if 8 <= ph < 22 else 0.0)); Pv.keyframe_insert("rotation_euler", index=0, frame=f)
    bpy.context.view_layer.update()
    fb = [ob["frame"].matrix_world @ v.co for v in ob["frame"].data.vertices]
    return min(v.y for v in fb), max(v.y for v in fb)
z0, z1 = module("Z", 0.0, 0.0)
# П: сначала в 0, узнать размер, потом сдвинуть, чтобы окантовки касались
import mathutils
p0, p1 = module("P", 0.0, 0.5)
E = bpy.data.objects["модуль П"]; E.location.y = z1 - p0
print("PARA: З y %.1f..%.1f, П y %.1f..%.1f, сдвиг П %.1f, длина пары %.1f" % (z0, z1, p0 + E.location.y, p1 + E.location.y, E.location.y, p1 + E.location.y - z0))
tg = bpy.data.objects.new("ц", None); sc.collection.objects.link(tg); tg.location = (0, (z0 + p1 + E.location.y) / 2, 10)
cam = bpy.data.objects.new("Камера", bpy.data.cameras.new("Камера")); sc.collection.objects.link(cam); cam.location = (130, -40, 90); cam.data.clip_start = 1
k = cam.constraints.new('TRACK_TO'); k.target = tg; k.track_axis = 'TRACK_NEGATIVE_Z'; k.up_axis = 'UP_Y'; sc.camera = cam
sc.frame_set(1); bpy.ops.wm.save_as_mainfile(filepath=os.path.join(R0, "19.67_okantovka8_P", "para8_ZP.blend")); print("saved")
