# Раскладка печатного набора (все STL папки ../19.70_pechat_okantovka8_<MOD>) в сетку с подписями. Запуск: blender -b -P blender_pechat_raskladka.py -- Z
import bpy, os, sys, math
MOD = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else "Z"
D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "19.70_pechat_okantovka8_%s" % MOD)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.unit_settings.scale_length = 0.001; sc.unit_settings.length_unit = 'MILLIMETERS'
files = sorted(f for f in os.listdir(D) if f.endswith(".stl"))
COLS, STEP = 5, 70.0
pal = [(.6, .62, .66, 1), (.85, .55, .2, 1), (.2, .6, .3, 1), (.15, .4, .9, 1), (.6, .25, .7, 1), (1, .55, .05, 1)]
for i, f in enumerate(files):
    bpy.ops.wm.stl_import(filepath=os.path.join(D, f)); o = bpy.context.selected_objects[0]; o.name = f[:-4]
    m = bpy.data.materials.new(f); m.diffuse_color = pal[i % len(pal)]; o.data.materials.append(m)
    cx, cy = (i % COLS) * STEP, -(i // COLS) * STEP
    o.location = (cx, cy, 0)
    n = 2 if "_x2" in f else 1
    t = bpy.data.curves.new(f, 'FONT'); t.body = f[:-4] + ("  ×2" if n == 2 else ""); t.size = 3.2
    to = bpy.data.objects.new("подпись " + f[:-4], t); sc.collection.objects.link(to); to.location = (cx - 28, cy - 30, 0)
    tm = bpy.data.materials.new("txt"); tm.diffuse_color = (0.95, 0.95, 0.95, 1); t.materials.append(tm)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(D, "raskladka_%s.blend" % MOD)); print("saved", len(files))
