# Сцена: блок «тележка = мотор» на 2 пальца + вторая половина (тот же блок, повёрнут на 180°) = 4 пальца. Запуск: blender -b -P blender_telezhka_motor.py
import bpy, os, math
H = os.path.dirname(os.path.abspath(__file__)); A = os.path.join(H, "asm")
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.unit_settings.scale_length = 0.001; sc.unit_settings.length_unit = 'MILLIMETERS'
LANE, S, ZP, Y_LO = map(float, open(os.path.join(A, "params.txt")).read().split())
COL = [(.25, .45, .85, 1), (.2, .65, .35, 1), (.85, .5, .2, 1), (.6, .3, .75, 1)]
def imp(n, name, col, parent):
    bpy.ops.wm.stl_import(filepath=os.path.join(A, n + ".stl")); o = bpy.context.selected_objects[0]; o.name = name
    m = bpy.data.materials.new(name); m.diffuse_color = col; o.data.materials.append(m); o.parent = parent; return o
for half in (0, 1):
    R = bpy.data.objects.new("блок %d (пальцы %d-%d)" % (half + 1, 2 * half + 1, 2 * half + 2), None); sc.collection.objects.link(R)
    if half: R.location = (0, 2 * Y_LO, 0); R.rotation_euler.z = math.pi
    imp("base", "основание %d" % (half + 1), (.6, .62, .66, 1), R)
    for k in range(2):
        n = 2 * half + (k if half == 0 else 1 - k) + 1                         # номер пальца вдоль грифа
        yc = -LANE * k
        E = bpy.data.objects.new("тележка пальца %d" % n, None); sc.collection.objects.link(E); E.parent = R
        imp("cart%d" % (k + 1), "тележка %d: шапка + ножки-полоз" % n, COL[n - 1], E)
        imp("key%d" % (k + 1), "клавиша %d" % n, (.95, .95, .97, 1), E)
        imp("btn%d" % (k + 1), "кнопка %d" % n, (.9, .15, .15, 1), E)
        mo = imp("motor", "мотор GB1806 %d" % n, (.12, .12, .14, 1), E); mo.location = (0, yc, 0)
        pn = imp("pin", "шестерня %d" % n, (.95, .8, .2, 1), E); pn.location = (0, yc, 0)
        for f in range(1, 241, 3):
            s = S * math.sin(2 * math.pi * ((f - 1) / 120 + 0.27 * n))
            E.location.x = s; E.keyframe_insert("location", index=0, frame=f)
            pn.rotation_euler.z = -s / ZP; pn.keyframe_insert("rotation_euler", index=2, frame=f)
sc.frame_start, sc.frame_end = 1, 240; sc.frame_set(1)
tg = bpy.data.objects.new("ц", None); sc.collection.objects.link(tg); tg.location = (0, Y_LO, 12)
cam = bpy.data.objects.new("Камера", bpy.data.cameras.new("Камера")); sc.collection.objects.link(cam); cam.location = (150, -140, 120); cam.data.clip_start = 1
k_ = cam.constraints.new('TRACK_TO'); k_.target = tg; k_.track_axis = 'TRACK_NEGATIVE_Z'; k_.up_axis = 'UP_Y'; sc.camera = cam
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(H, "telezhka_motor.blend")); print("saved")
