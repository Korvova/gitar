# Модуль в сборе отдельными печатными деталями, БЕЗ анимации — двигать руками. Запуск: blender -b -P blender_ruchnaya.py -- P|Z
import bpy, os, sys
MOD = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else "P"
D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "19.70_pechat_okantovka8_%s" % MOD); S_ = os.path.join(D, "sborka")
C = {"01": (.35, .3, .25, 1), "02": (.6, .62, .66, 1), "03a": (.85, .55, .2, 1), "03b": (.75, .45, .15, 1), "03c": (.4, .42, .46, 1), "04": (.45, .48, .52, 1),
     "05": (.7, .72, .76, 1), "06": (.2, .6, .3, 1), "07": (1, .55, .05, 1), "08": (.85, .2, .1, 1), "09": (.6, .25, .7, 1), "10": (.78, .78, .72, 1),
     "11": (.15, .4, .9, 1), "12": (.12, .12, .14, 1), "13": (.95, .85, .3, 1), "14": (.85, .55, .2, 1), "15": (.75, .45, .15, 1),
     "k1": (.9, .15, .15, 1), "k2": (.9, .9, .95, 1), "k3": (.05, .05, .3, 1)}
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.unit_settings.scale_length = 0.001; sc.unit_settings.length_unit = 'MILLIMETERS'
for f in sorted(os.listdir(S_)):
    if not f.endswith(".stl"): continue
    bpy.ops.wm.stl_import(filepath=os.path.join(S_, f)); o = bpy.context.selected_objects[0]; o.name = f[:-4]
    m = bpy.data.materials.new(f); m.diffuse_color = C.get(f.split("_")[0], (.6, .6, .6, 1)); o.data.materials.append(m)
    bpy.context.view_layer.objects.active = o; bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')   # точка вращения — центр детали
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(D, os.environ.get("NAME", "ruchnaya_%s") % MOD + ".blend")); print("saved")
