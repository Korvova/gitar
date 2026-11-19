# Ряд из 4 модулей-клавиш (папка ../19.65_klavisha_ryad): тележки ездят, модули по очереди «нажимаются» (наклон ×4 для наглядности).
# Запуск: blender -b -P blender_ryad_klavisha.py
import bpy, os, math, ast
D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "19.65_klavisha_ryad"); A_ = os.path.join(D, "asm")
P = ast.literal_eval(open(os.path.join(A_, "params.txt")).read()); S = 11.0
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.unit_settings.scale_length = 0.001; sc.unit_settings.length_unit = 'MILLIMETERS'; sc.frame_end = 240
C = {"frame": (.35, .3, .25, 1), "base": (.6, .62, .66, 1), "rack": (.45, .48, .52, 1), "beam": (.4, .42, .46, 1), "legs": (.55, .57, .6, 1), "cart": (.15, .4, .9, 1),
     "btns": (.9, .15, .15, 1), "posts": (.78, .78, .72, 1), "sens": (.05, .05, .3, 1), "slider": (.2, .6, .3, 1), "flo": (1, .55, .05, 1), "brusok": (.7, .72, .76, 1),
     "gm": (.85, .2, .1, 1), "plat": (.6, .25, .7, 1), "mags": (.9, .9, .95, 1), "motor": (.12, .12, .14, 1)}
mats = {}
def mat(n):
    if n not in mats:
        m = bpy.data.materials.new(n); m.diffuse_color = C[n]; mats[n] = m
    return mats[n]
meshes = {}
def obj(file, key, name, parent=None, loc=(0, 0, 0)):
    if file not in meshes:
        bpy.ops.wm.stl_import(filepath=os.path.join(A_, file + ".stl")); o = bpy.context.selected_objects[0]; meshes[file] = o.data
        bpy.data.objects.remove(o)
    o = bpy.data.objects.new(name, meshes[file]); sc.collection.objects.link(o)
    if not o.data.materials: o.data.materials.append(mat(key))
    o.parent = parent; o.location = loc; return o
def empty(name, parent=None, loc=(0, 0, 0), rz=0.0):
    e = bpy.data.objects.new(name, None); sc.collection.objects.link(e); e.parent = parent; e.location = loc; e.rotation_euler[2] = rz; e.empty_display_size = 5; return e
obj("frame", "frame", "рама ряда")
for i in range(4):
    t = P["TYPE"][i]; nm = "модуль %d %s" % (i + 1, "П" if t == "P" else "З"); yp, ang = P["piv"][t], P["ang"][t]
    E = empty(nm, loc=(0, P["CM"][i], 0), rz=math.pi if P["ROT"][i] else 0.0)
    F = empty(nm + " (центр)", E, (0, -P["YM"], 0))
    obj("%s_btns" % t, "btns", nm + " кнопки", F)
    Pv = empty(nm + " ось качания", F, (0, yp, 0)); Pv.empty_display_type = 'ARROWS'
    rig = ["base", "rack", "legs", "posts", "sens", "brusok", "motor"] + (["beam"] if t == "Z" else [])
    for k in rig:
        obj("%s_%s" % (t, k), k, "%s %s" % (nm, k), Pv, (0, -yp, 0))
    sl = obj("slider", "slider", nm + " ползун", Pv); ca = obj("%s_cart" % t, "cart", nm + " тележка", Pv)
    f1 = obj("flo", "flo", nm + " плав.1", Pv); f2 = obj("flo", "flo", nm + " плав.2", Pv)
    rot = [obj(n, n, "%s %s" % (nm, n), Pv) for n in ("gm", "plat", "mags")]
    ph0 = i * 0.25
    for f in range(1, 241, 2):
        s = S * math.sin(2 * math.pi * ((f - 1) / 240 + ph0))
        sl.location = (s, -yp, 0); ca.location = (2 * s, -yp, 0)
        for o in (sl, ca): o.keyframe_insert("location", frame=f)
        for o, x in ((f1, s - P["A"]), (f2, s + P["A"])):
            o.location = (x, P["YG"] - yp, 0); o.rotation_euler[2] = s / P["RF"]; o.keyframe_insert("location", frame=f); o.keyframe_insert("rotation_euler", index=2, frame=f)
        for o in rot:
            o.location = (0, P["YM"] - yp, 0); o.rotation_euler[2] = s / P["RM"]; o.keyframe_insert("location", frame=f); o.keyframe_insert("rotation_euler", index=2, frame=f)
    for f in range(1, 241):
        ph = (f - 1 - i * 10) % 40
        Pv.rotation_euler[0] = math.radians(ang * 4 * (1.0 if 0 <= ph < 12 else 0.0)); Pv.keyframe_insert("rotation_euler", index=0, frame=f)
tg = bpy.data.objects.new("ц", None); sc.collection.objects.link(tg); tg.location = (0, 0, 10)
cam = bpy.data.objects.new("Камера", bpy.data.cameras.new("Камера")); sc.collection.objects.link(cam); cam.location = (150, -110, 110); cam.data.clip_start = 1
k = cam.constraints.new('TRACK_TO'); k.target = tg; k.track_axis = 'TRACK_NEGATIVE_Z'; k.up_axis = 'UP_Y'; sc.camera = cam
sc.frame_set(1); bpy.ops.wm.save_as_mainfile(filepath=os.path.join(D, "klavisha_ryad.blend")); print("saved")
