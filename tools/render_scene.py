# -*- coding: utf-8 -*-
"""Рендер .blend-сцены проекта в PNG для вики — без открытия Blender руками.

Запуск (из корня репозитория):
    "C:\\Program Files\\Blender Foundation\\Blender 5.1\\blender.exe" -b 2-0\\Гитара_корпус.blend
        -P tools\\render_scene.py -- wiki\\img\\korpus.png [iso|top|front] [кадр]

Движок Workbench: цвета из материалов сцены (секции покрашены по-разному),
контур, полости; камера ортографическая, сама вписывает все видимые объекты.
"""
import os
import sys
import math
import re
import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
out = os.path.abspath(argv[0]) if argv else os.path.abspath("render.png")
view = argv[1] if len(argv) > 1 else "iso"
frame = int(argv[2]) if len(argv) > 2 and argv[2].isdigit() else None
# объекты-декорации (пол, стол, плоскости) в кадр не вписываем
EXCLUDE = re.compile(r"^(Plane|Floor|Ground|Пол|Стол|Плоскость)", re.I)

sc = bpy.context.scene
if frame is not None:
    sc.frame_set(frame)

# --- габариты всех видимых мешей (мировые координаты) ---
lo = Vector((1e9, 1e9, 1e9))
hi = Vector((-1e9, -1e9, -1e9))
n = 0
for ob in sc.objects:
    if ob.type != "MESH" or ob.hide_render or ob.hide_viewport:
        continue
    if EXCLUDE.match(ob.name):
        ob.hide_render = True
        continue
    for c in ob.bound_box:
        w = ob.matrix_world @ Vector(c)
        lo = Vector(map(min, lo, w))
        hi = Vector(map(max, hi, w))
    n += 1
if n == 0:
    sys.exit("В сцене нет видимых мешей")
center = (lo + hi) / 2
size = hi - lo
diag = size.length

# --- камера ---
dirs = {
    "iso": Vector((1.0, -1.2, 0.9)),
    "top": Vector((0.0, -0.001, 1.0)),
    "front": Vector((0.0, -1.0, 0.25)),
    "side": Vector((1.0, 0.0, 0.25)),
}
d = dirs.get(view, dirs["iso"]).normalized()
cam_data = bpy.data.cameras.new("wiki_cam")
cam_data.type = "ORTHO"
cam = bpy.data.objects.new("wiki_cam", cam_data)
sc.collection.objects.link(cam)
cam.location = center + d * (diag * 2)
cam.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
cam_data.clip_start = 1
cam_data.clip_end = diag * 10
sc.camera = cam
bpy.context.view_layer.update()        # иначе matrix_world камеры устаревшая

# точное вписывание: проекция углов бокса на оси камеры
inv = cam.matrix_world.inverted()
xs, ys = [], []
for i in range(8):
    c = Vector(((lo.x, hi.x)[i & 1], (lo.y, hi.y)[(i >> 1) & 1], (lo.z, hi.z)[(i >> 2) & 1]))
    p = inv @ c
    xs.append(p.x)
    ys.append(p.y)
w, h = max(xs) - min(xs), max(ys) - min(ys)
sc.render.resolution_x = 1600
sc.render.resolution_y = 1100
aspect = sc.render.resolution_x / sc.render.resolution_y
cam_data.ortho_scale = max(w, h * aspect) * 1.06
# сдвиг камеры в центр проекции
cam.location += cam.matrix_world.to_3x3() @ Vector(((max(xs) + min(xs)) / 2,
                                                      (max(ys) + min(ys)) / 2, 0))

# --- Workbench ---
sc.render.engine = "BLENDER_WORKBENCH"
sh = sc.display.shading
sh.light = "STUDIO"
sh.color_type = "MATERIAL" if any(ob.material_slots for ob in sc.objects
                                  if ob.type == "MESH") else "RANDOM"
sh.show_object_outline = True
sh.show_cavity = True
sh.show_shadows = False
sc.display.render_aa = "8"
sc.render.film_transparent = False
if sc.world is None:
    sc.world = bpy.data.worlds.new("wiki_world")
sc.world.color = (0.96, 0.96, 0.97)
if out.lower().endswith((".jpg", ".jpeg")):
    sc.render.image_settings.file_format = "JPEG"
    sc.render.image_settings.quality = 88
else:
    sc.render.image_settings.file_format = "PNG"
sc.render.filepath = out
bpy.ops.render.render(write_still=True)
big = sorted(((ob.dimensions.length, ob.name) for ob in sc.objects
              if ob.type == "MESH"), reverse=True)[:4]
print("RENDER OK:", out, "объектов:", n, "габарит мм:",
      tuple(round(v, 1) for v in size), "| крупнейшие:", [b[1] for b in big])
