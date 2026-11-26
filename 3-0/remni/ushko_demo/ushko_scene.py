import bpy, os
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.unit_settings.scale_length = 0.001; sc.unit_settings.length_unit = 'MILLIMETERS'
HERE = os.path.dirname(os.path.abspath(bpy.data.filepath or __file__)) if False else r"C:\App\gitar\3-0\remni\ushko_demo"
def imp(f, name, rgba):
    bpy.ops.wm.stl_import(filepath=os.path.join(HERE, f + ".stl"))
    o = bpy.context.selected_objects[0]; o.name = name
    m = bpy.data.materials.new(name); m.diffuse_color = rgba; o.data.materials.append(m); return o
imp("belt", "ремень 3 мм с ушком на спинке", (0.95, 0.75, 0.2, 1))
imp("rollers", "ролики (упрощённо): концевые и ведущий в центре петли", (0.8, 0.8, 0.82, 1))
c = imp("cart", "тележка: площадка + пластина в прорези + кармашек на ушко", (0.2, 0.4, 0.9, 1))
cv = imp("cover", "крышка с прорезью (полупрозрачная)", (0.7, 0.7, 0.75, 0.25))
for f, z in ((1, 7.0), (25, 7.0), (60, 0.0), (120, 0.0)):
    sc.frame_set(f); c.location.z = z; c.keyframe_insert("location", index=2, frame=f)
sc.frame_start, sc.frame_end = 1, 120; sc.frame_set(1)
for scr in bpy.data.screens:
    for ar in scr.areas:
        for sp in ar.spaces:
            if sp.type == 'VIEW_3D':
                sp.shading.type = 'SOLID'; sp.shading.color_type = 'MATERIAL'; sp.clip_start = 0.1; sp.clip_end = 1000
                r3 = sp.region_3d; r3.view_location = (0, 2, 2); r3.view_distance = 40; r3.view_rotation = (0.82, 0.45, 0.17, 0.31)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "ushko_demo.blend")); print("saved")
