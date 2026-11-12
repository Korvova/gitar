import bpy, os
D = os.path.join(os.path.expanduser("~"), "Documents", "App", "mcp-blender-cloude", "gitar_teleskop_v4")
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.unit_settings.scale_length = 0.001; sc.unit_settings.length_unit = 'MILLIMETERS'
def imp(path, name, c, loc=(0, 0, 0)):
    bpy.ops.wm.stl_import(filepath=path); o = bpy.context.selected_objects[0]; o.name = name; o.location = loc
    m = bpy.data.materials.new(name); m.diffuse_color = c; o.data.materials.append(m); return o
K = os.path.join(D, "kaseta_stl")
imp(os.path.join(K, "asm_tray.stl"), "Лоток", (.45, .48, .52, 1))
imp(os.path.join(K, "asm_lid.stl"), "Крышка кассеты", (.62, .65, .7, 1))
imp(os.path.join(K, "asm_caps.stl"), "Крышки", (.9, .9, .85, 1))
imp(os.path.join(K, "asm_plate.stl"), "Пластина вместо платы", (.2, .5, .2, 1))
imp(os.path.join(K, "asm_btns.stl"), "Кнопки", (.9, .15, .15, 1))
imp(os.path.join(D, "asm", "cart.stl"), "Тележка v4 (на струне 4.4)", (.1, .35, .9, .6), (4.4, 0, 0))
tg = bpy.data.objects.new("ц", None); sc.collection.objects.link(tg); tg.location = (0, 17, 18)
c = bpy.data.objects.new("Камера", bpy.data.cameras.new("Камера")); sc.collection.objects.link(c); c.location = (45, -40, 55)
k = c.constraints.new('TRACK_TO'); k.target = tg; k.track_axis = 'TRACK_NEGATIVE_Z'; k.up_axis = 'UP_Y'; sc.camera = c
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(D, "kaseta_proba.blend")); print("saved")
