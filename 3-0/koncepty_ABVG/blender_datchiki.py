# Ряд 19.59 + датчики сбоку: стойки с 49E по бокам каждого мотора, магниты по кромке платформы ротора.
import bpy, os, json, math
D = os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.open_mainfile(filepath=os.path.join(D, "ryad_V4d.blend"))
P = json.load(open(os.path.join(D, "asm_dat", "place.json")))
sc = bpy.context.scene
for o in list(bpy.data.objects):                                                 # штатная платформа без гнёзд — заменяем платформой с магнитами
    if o.name.startswith("платформа "):
        bpy.data.objects.remove(o)
C = {"posts": (.75, .75, .7, 1), "sens": (.05, .05, .3, 1), "posts_p": (.75, .75, .7, 1), "sens_p": (.05, .05, .3, 1), "mags": (.9, .9, .95, 1), "plat_mag": (.75, .35, .85, 1)}
mesh = {}
for n, c in C.items():
    bpy.ops.wm.stl_import(filepath=os.path.join(D, "asm_dat", n + ".stl")); o = bpy.context.selected_objects[0]
    m = bpy.data.materials.new("дат_" + n); m.diffuse_color = c; o.data.materials.append(m); mesh[n] = o.data; bpy.data.objects.remove(o)
names = {"posts": "Стойки 49E", "sens": "49E", "posts_p": "Стойки 49E", "sens_p": "49E", "mags": "Магниты платформы", "plat_mag": "Платформа с магнитами"}
for i, (cm, rot) in enumerate(zip(P["CM"], P["ROT"])):
    e = bpy.data.objects.new("Датчики модуля %d" % (i + 1), None); sc.collection.objects.link(e)
    e.location.y = cm; e.rotation_euler[2] = math.pi if rot else 0
    for n in C:
        if (n in ("posts", "sens") and i in (1, 2)) or (n in ("posts_p", "sens_p") and i in (0, 3)): continue
        o = bpy.data.objects.new("%s %d" % (names[n], i + 1), mesh[n]); sc.collection.objects.link(o); o.parent = e
        o.location.y = -P["YM"] + (P["YM"] if n in ("mags", "plat_mag") else 0)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(D, "ryad_V4d_datchiki.blend")); print("saved")
