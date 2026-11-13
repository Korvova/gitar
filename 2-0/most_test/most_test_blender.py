import bpy, os
D = os.path.dirname(os.path.abspath(__file__))   # папка скрипта (рядом asm/)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.unit_settings.scale_length = 0.001; sc.unit_settings.length_unit = 'MILLIMETERS'
for f, z, c in (("корпус", 0, (.55, .58, .62, 1)), ("пластина", 0, (.15, .5, .2, 1)), ("кнопки", 0, (.9, .15, .15, 1)), ("крышка", 12, (.75, .77, .8, 1)),
                ("лента", 20, (.12, .12, .25, 1)), ("плёнка", 24, (.85, .85, .5, 1)), ("тележка", 28, (.1, .35, .9, 1))):
    bpy.ops.wm.stl_import(filepath=os.path.join(D, "asm", f + ".stl")); o = bpy.context.selected_objects[0]; o.name = f.capitalize()
    o.location.z = z; m = bpy.data.materials.new(f); m.diffuse_color = c; o.data.materials.append(m)   # разнесено по высоте; G Z 0 — собрать
tg = bpy.data.objects.new("ц", None); sc.collection.objects.link(tg); tg.location = (0, 0, 15)
cam = bpy.data.objects.new("Камера", bpy.data.cameras.new("Камера")); sc.collection.objects.link(cam); cam.location = (60, -70, 60); cam.data.clip_start = 1
k = cam.constraints.new('TRACK_TO'); k.target = tg; k.track_axis = 'TRACK_NEGATIVE_Z'; k.up_axis = 'UP_Y'; sc.camera = cam
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(D, "most_test.blend")); print("saved")
