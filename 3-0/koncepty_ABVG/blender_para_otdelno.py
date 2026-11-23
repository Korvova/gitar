# Пара З1+П1 на местах в ряду, все детали отдельными объектами (неподвижные — можно двигать). Запуск: blender -b -P blender_para_otdelno.py
import bpy, os
D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "19.71_para_otdelno")
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.unit_settings.scale_length = 0.001; sc.unit_settings.length_unit = 'MILLIMETERS'
COL = {"okantovka": (.35, .3, .25, 1), "stojka_knopki": (.85, .55, .2, 1), "stojka_paza": (.2, .65, .6, 1), "kryshki": (.9, .8, .2, 1), "knopka": (.9, .15, .15, 1),
       "base": (.6, .62, .66, 1), "rack": (.45, .48, .52, 1), "beam": (.4, .42, .46, 1), "posts": (.78, .78, .72, 1), "sens": (.05, .05, .3, 1), "brusok": (.7, .72, .76, 1),
       "motor": (.12, .12, .14, 1), "slider": (.2, .6, .3, 1), "flo1": (1, .55, .05, 1), "flo2": (1, .55, .05, 1), "cart": (.15, .4, .9, 1), "gm": (.85, .2, .1, 1), "plat": (.6, .25, .7, 1)}
NAMES = {"okantovka_obshaja": "окантовка общая", "stojka_knopki": "стойка с кнопкой", "stojka_paza": "стойка с пазом", "kryshki_jam": "крышки ям оси", "knopka": "кнопка"}
for f in sorted(os.listdir(D)):
    if not f.endswith(".stl"): continue
    n = f[:-4]
    bpy.ops.wm.stl_import(filepath=os.path.join(D, f)); o = bpy.context.selected_objects[0]
    key = next((k for k in COL if k in n), "base")
    mod = "З " if n.startswith("Z_") else ("П " if n.startswith("P_") else "")
    o.name = mod + NAMES.get(n[2:] if mod else n, n[2:] if mod else n)
    m = bpy.data.materials.new(o.name); m.diffuse_color = COL[key]; o.data.materials.append(m)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(D, "para_otdelno.blend")); print("saved")
