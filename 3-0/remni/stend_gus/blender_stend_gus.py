# Сборка стенда гусеницы для просмотра: blender -b -P blender_stend_gus.py
import bpy, os
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.unit_settings.scale_length = 0.001; sc.unit_settings.length_unit = 'MILLIMETERS'
HERE = r"C:\App\gitar\3-0\remni\stend_gus"
for f, n, c in (("osnova", "дно + кронштейн мотора + столбики", (0.65, 0.65, 0.68, 1)), ("klavisha", "стенка + язычок + крышка-клавиша", (0.8, 0.8, 0.84, 1)),
                ("motor", "мотор GB1806 лёжа (корпус крутится, стакан на кронштейне)", (0.08, 0.08, 0.09, 1)), ("ved", "ведущий ролик Ø10 на роторе", (0.95, 0.95, 0.97, 1)),
                ("svob", "свободный ролик Ø10 на болте М2", (0.55, 0.55, 0.6, 1)), ("tel", "тележка", (0.95, 0.8, 0.15, 1)), ("remen", "ремень TPU с ушками-пилами", (0.2, 0.3, 0.9, 1))):
    bpy.ops.wm.stl_import(filepath=os.path.join(HERE, "asm", f + ".stl"))
    o = bpy.context.selected_objects[0]; o.name = n
    m = bpy.data.materials.new(n); m.diffuse_color = c; o.data.materials.append(m)
for scr in bpy.data.screens:
    for ar in scr.areas:
        for sp in ar.spaces:
            if sp.type == 'VIEW_3D':
                sp.shading.type = 'SOLID'; sp.shading.color_type = 'MATERIAL'; sp.clip_start = 0.5; sp.clip_end = 2000
                r3 = sp.region_3d; r3.view_location = (3, -8, 12); r3.view_distance = 120; r3.view_rotation = (0.82, 0.45, 0.15, 0.31)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "stend_gus.blend")); print("saved")
