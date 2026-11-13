import bpy, os, math
D = os.path.join(os.path.expanduser("~"), "Documents", "App", "mcp-blender-cloude", "gitar_full_v5")
A, S, RF, RM, YM, FR = 2.5 * math.pi * 0.8, 11.0, 4.8, 4.4, 15.5, 240
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.unit_settings.scale_length = 0.001; sc.unit_settings.length_unit = 'MILLIMETERS'; sc.frame_end = FR
L = {"base": ("Основание", (.55, .58, .62, 1)), "beam": ("Брусок", (.7, .72, .76, 1)), "motor": ("Макет мотора", (.1, .1, .12, 1)),
     "slider": ("Ползун", (.2, .65, .3, 1)), "pin_m": ("Шестерня мотора", (.85, .2, .1, 1)),
     "tray": ("Лоток моста", (.62, .65, .7, 1)), "lid": ("Крышка лотка", (.75, .77, .8, 1)), "tape": ("Лента TPU", (.12, .12, .25, 1)),
     "pcb": ("Плата", (.15, .5, .2, 1)), "btns": ("Кнопки", (.9, .15, .15, 1)), "res": ("Резисторы", (.85, .7, .4, 1)),
     "cart": ("Тележка с рейкой", (.1, .35, .9, 1)), "cover": ("Накладка тележки", (.8, .82, .85, 1)), "pads": ("Подушки TPU", (.1, .1, .4, 1)), "coins_b": ("Вибромоторы под мостом", (.05, .05, .05, 1))}
ob = {}
def imp(f, n, c):
    bpy.ops.wm.stl_import(filepath=os.path.join(D, "asm", f + ".stl")); o = bpy.context.selected_objects[0]; o.name = n
    m = bpy.data.materials.new(n); m.diffuse_color = c; o.data.materials.append(m); return o
for f, (n, c) in L.items(): ob[f] = imp(f, n, c)
f1, f2 = imp("flo", "Плавающая шестерня 1", (1, .5, .05, 1)), imp("flo", "Плавающая шестерня 2", (1, .5, .05, 1))
for f in range(1, FR + 1):
    s = S * math.sin(2 * math.pi * (f - 1) / FR)
    for o in (ob["slider"],): o.location.x = s; o.keyframe_insert("location", index=0, frame=f)
    for o in (ob["cart"], ob["cover"]): o.location.x = 2 * s; o.keyframe_insert("location", index=0, frame=f)
    for o, x in ((f1, s - A), (f2, s + A)):
        o.location = (x, 0, 0); o.rotation_euler[2] = -s / RF; o.keyframe_insert("location", frame=f); o.keyframe_insert("rotation_euler", index=2, frame=f)
    ob["pin_m"].location = (0, YM, 0); ob["pin_m"].rotation_euler[2] = s / RM
    ob["pin_m"].keyframe_insert("rotation_euler", index=2, frame=f); ob["pin_m"].keyframe_insert("location", frame=f)
tg = bpy.data.objects.new("ц", None); sc.collection.objects.link(tg); tg.location = (0, 12, 16)
cam = bpy.data.objects.new("Камера", bpy.data.cameras.new("Камера")); sc.collection.objects.link(cam); cam.location = (80, -95, 90); cam.data.clip_start = 1
k = cam.constraints.new('TRACK_TO'); k.target = tg; k.track_axis = 'TRACK_NEGATIVE_Z'; k.up_axis = 'UP_Y'; sc.camera = cam
sc.frame_set(61); bpy.ops.wm.save_as_mainfile(filepath=os.path.join(D, "full_v5.blend")); print("saved")
