# Ряд с датчиками + клик модулей «З»: балка с колоннами (одна деталь) на кнопках Ø6 в стаканах.
import bpy, os, json, math
D = os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.open_mainfile(filepath=os.path.join(D, "ryad_V4d_datchiki.blend"))
P = json.load(open(os.path.join(D, "asm_dat", "place.json")))
sc = bpy.context.scene
C = {"btns": (.9, .15, .15, 1)}
N = {"beam_col": "Балка с колоннами", "cups": "Стаканы кнопок", "btns": "Кнопки Ø6"}
mesh = {}
for n, c in C.items():
    bpy.ops.wm.stl_import(filepath=os.path.join(D, "asm_kn", n + ".stl")); o = bpy.context.selected_objects[0]
    m = bpy.data.materials.new("кн_" + n); m.diffuse_color = c; o.data.materials.append(m); mesh[n] = o.data; bpy.data.objects.remove(o)
for i in (0, 3):
    e = bpy.data.objects.new("Клик модуля %d (З)" % (i + 1), None); sc.collection.objects.link(e)
    e.location.y = P["CM"][i]; e.rotation_euler[2] = math.pi if P["ROT"][i] else 0
    for n in C:
        o = bpy.data.objects.new("%s %d" % (N[n], i + 1), mesh[n]); sc.collection.objects.link(o); o.parent = e; o.location.y = -P["YM"]
bpy.ops.wm.stl_import(filepath=os.path.join(D, "asm_V4d", "btns_p.stl")); bp = bpy.context.selected_objects[0]; bpm = bp.data; bpy.data.objects.remove(bp)
mb = bpy.data.materials.new("кн_п"); mb.diffuse_color = (.9, .15, .15, 1); bpm.materials.append(mb)
for i in (1, 2):
    e = bpy.data.objects.new("Клик модуля %d (П)" % (i + 1), None); sc.collection.objects.link(e)
    e.location.y = P["CM"][i]; e.rotation_euler[2] = math.pi if P["ROT"][i] else 0
    o = bpy.data.objects.new("Кнопки Ø6 %d" % (i + 1), bpm); sc.collection.objects.link(o); o.parent = e; o.location.y = -P["YM"]
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(D, "ryad_V4d_knopki.blend")); print("saved")
