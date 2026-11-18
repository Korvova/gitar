# -*- coding: utf-8 -*-
# Раскладка платформы на 4 пальца (эскиз, 18.11): 1 — по идее владельца: по краям мотор боком (концепт Г), в середине два мотора плашмя
# спиной к спине; 2 — наоборот: в середине два концепта Г, по краям моторы плашмя лицом к середине.
# Синие площадки — где должны быть пальцы (шаг 24); полупрозрачные полосы — нижний слой тележки от её рейки до площадки.
# Механизм не проверялся на пересечения — это раскладка по размерам. Запуск: blender -b -P blender_raskladka4.py
import bpy, os, math
D = os.path.dirname(os.path.abspath(__file__))
P2 = os.path.join(D, "asm"); PG = os.path.join(D, "..", "koncepty_ABVG", "asm_D")
A, YM = 2.5 * math.pi * 0.8, 15.5
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.unit_settings.scale_length = 0.001; sc.unit_settings.length_unit = 'MILLIMETERS'
mats = {}
def mat(n, c):
    if n not in mats:
        m = bpy.data.materials.new(n); m.diffuse_color = c; mats[n] = m
    return mats[n]
meshes = {}
def mesh(path):
    if path not in meshes:
        bpy.ops.wm.stl_import(filepath=path); o = bpy.context.selected_objects[0]; meshes[path] = o.data; bpy.data.objects.remove(o)
    return meshes[path]
def part(parent, path, name, col, loc=(0, 0, 0)):
    o = bpy.data.objects.new(name, mesh(path)); sc.collection.objects.link(o); o.parent = parent; o.location = loc
    o.data.materials.clear() if False else None
    o.active_material = mat(name.split(" ")[0], col); return o
def module(kind, x0, y0, rot, tag):
    e = bpy.data.objects.new("Модуль %s %s" % (kind, tag), None); sc.collection.objects.link(e)
    e.location = (x0, y0, 0); e.rotation_euler.z = math.pi if rot else 0
    G, Dk = (.6, .62, .66, 1), (.45, .47, .5, 1)
    if kind == "плашмя":
        for f, n, c in (("base", "основание", G), ("rack", "рейка", Dk), ("beam", "брусок", (.7, .72, .76, 1)), ("motor", "мотор", (.12, .12, .14, 1)),
                        ("hall", "49E", (.2, .2, .55, 1)), ("slider", "ползун", (.2, .55, .3, 1))):
            part(e, os.path.join(P2, f + ".stl"), n + " " + tag, c)
        part(e, os.path.join(P2, "jacket.stl"), "колпак " + tag, (.85, .3, .15, 1), (0, YM, 0))
        part(e, os.path.join(P2, "pin_m.stl"), "шестерня " + tag, (.85, .2, .1, 1), (0, YM, 0))
        for dx in (-A, A):
            part(e, os.path.join(P2, "flo.stl"), "плавающая " + tag, (1, .6, .1, 1), (dx, 0, 0))
    else:
        for f, n, c in (("base", "основание", G), ("beam", "брусок", (.7, .72, .76, 1)), ("motor", "мотор", (.12, .12, .14, 1)),
                        ("plat", "платформа", (.6, .25, .7, 1)), ("slider", "ползун", (.2, .55, .3, 1))):
            part(e, os.path.join(PG, f + ".stl"), n + " " + tag, c)
        part(e, os.path.join(PG, "pin.stl"), "шестерня " + tag, (.85, .2, .1, 1), (0, 0, 15.0))
        for dx in (-A, A):
            part(e, os.path.join(PG, "flo.stl"), "плавающая " + tag, (1, .6, .1, 1), (dx, 0, 21.3))
    return e
def box(n, x0, x1, y0, y1, z0, z1, col):
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)); o = bpy.context.object
    o.name = n; o.scale = (abs(x1 - x0), abs(y1 - y0), abs(z1 - z0)); o.active_material = mat(n.split(" ")[0], col); return o
PAD = (.15, .45, .95, 1); ARM = (.35, .6, 1.0, .35)
def pad(x0, yc, zt, y_from, tag):
    box("Площадка " + tag, x0 - 10, x0 + 10, yc - 7.5, yc + 7.5, zt - 1.6, zt, PAD)
    a, b = sorted((y_from, yc))
    if b - a > 1:
        box("Нижний_слой " + tag, x0 - 10, x0 + 10, a, b, zt - 3.6, zt - 1.6, ARM)
# ---------- раскладка 1: Г по краям, плашмя спиной к спине в середине ----------
X1 = -45.0
module("плашмя", X1, -35.1, False, "1-2"); module("плашмя", X1, 35.1, True, "1-3")
module("Г", X1, -67.9, False, "1-1"); module("Г", X1, 67.9, True, "1-4")
pad(X1, -12, 29.7, -41.2, "1-2"); pad(X1, 12, 29.7, 41.2, "1-3")
pad(X1, -36, 31.4, -56.3, "1-1"); pad(X1, 36, 31.4, 56.3, "1-4")
# ---------- раскладка 2: Г в середине, плашмя по краям лицом к середине ----------
X2 = 45.0
module("Г", X2, -23.4, False, "2-2"); module("Г", X2, 23.4, True, "2-3")
module("плашмя", X2, -33.0, True, "2-1"); module("плашмя", X2, 33.0, False, "2-4")
pad(X2, -12, 31.4, -11.8, "2-2"); pad(X2, 12, 31.4, 11.8, "2-3")
pad(X2, -36, 29.7, -34.4, "2-1"); pad(X2, 36, 29.7, 34.4, "2-4")
for x, t in ((X1, "1: Г по краям"), (X2, "2: Г в середине")):
    bpy.ops.object.text_add(location=(x - 20, -85, 0)); tx = bpy.context.object; tx.data.body = t; tx.data.size = 6
    tx.active_material = mat("текст", (.9, .1, .1, 1))
cam = bpy.data.objects.new("Камера", bpy.data.cameras.new("Камера")); sc.collection.objects.link(cam); cam.location = (170, -170, 170); cam.data.clip_start = 1
tg = bpy.data.objects.new("ц", None); sc.collection.objects.link(tg); tg.location = (0, 0, 10)
k = cam.constraints.new('TRACK_TO'); k.target = tg; k.track_axis = 'TRACK_NEGATIVE_Z'; k.up_axis = 'UP_Y'; sc.camera = cam
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(D, "raskladka_4_paltsa.blend")); print("saved")
