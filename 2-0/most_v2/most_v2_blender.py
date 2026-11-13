import bpy, os
D = os.path.dirname(os.path.abspath(__file__))   # папка скрипта (рядом asm/)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.unit_settings.scale_length = 0.001; sc.unit_settings.length_unit = 'MILLIMETERS'
for f, n, c in (("tray", "Лоток (стенки = рельсы)", (.55, .58, .62, 1)), ("lid", "Крышка лотка", (.7, .72, .76, 1)), ("plungers", "Лента TPU", (.12, .12, .25, 1)),
                ("pcb", "Плата / пластина 1.6", (.15, .5, .2, 1)), ("btns", "Кнопки 5.2×5.2", (.9, .15, .15, 1)), ("res", "Резисторы 1 кОм", (.85, .7, .4, 1)),
                ("cart", "Тележка с П-язычком (струна 4.4)", (.1, .35, .9, .7)), ("cover", "Накладка тележки", (.75, .77, .8, 1)), ("coin", "Вибромотор-таблетка", (.05, .05, .05, 1))):
    bpy.ops.wm.stl_import(filepath=os.path.join(D, "asm", f + ".stl")); o = bpy.context.selected_objects[0]; o.name = n
    m = bpy.data.materials.new(n); m.diffuse_color = c; o.data.materials.append(m)
tg = bpy.data.objects.new("ц", None); sc.collection.objects.link(tg); tg.location = (2, 0, 5)
cam = bpy.data.objects.new("Камера", bpy.data.cameras.new("Камера")); sc.collection.objects.link(cam); cam.location = (50, -55, 45)
k = cam.constraints.new('TRACK_TO'); k.target = tg; k.track_axis = 'TRACK_NEGATIVE_Z'; k.up_axis = 'UP_Y'; sc.camera = cam
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(D, "most_v2.blend")); print("saved")
