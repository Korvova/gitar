# -*- coding: utf-8 -*-
"""Схема подтверждённого формата датчика положения: магнит в кармане ленты,
49E плашмя ПОД лентой. Запуск: blender -b -P tools/render_hall_format.py"""
import bpy, math, os
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "wiki", "img")

def mat(n, rgba):
    m = bpy.data.materials.new(n); m.diffuse_color = rgba; return m
M = {"band": mat("band", (0.85, 0.35, 0.2, 1)), "mag": mat("mag", (0.85, 0.85, 0.9, 1)),
     "sens": mat("sens", (0.15, 0.15, 0.18, 1)), "post": mat("post", (0.72, 0.7, 0.66, 1)),
     "floor": mat("floor", (0.55, 0.55, 0.58, 1)), "arrow": mat("arrow", (0.2, 0.7, 0.3, 1))}

def box(name, x0, x1, y0, y1, z0, z1, m):
    bpy.ops.mesh.primitive_cube_add(size=1); ob = bpy.context.object
    ob.dimensions = (x1 - x0, y1 - y0, z1 - z0); ob.location = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    ob.name = name; ob.data.materials.append(M[m]); return ob
def cyl(name, x, y, z0, z1, r, m):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=z1 - z0, vertices=48); ob = bpy.context.object
    ob.location = (x, y, (z0 + z1) / 2); ob.name = name; ob.data.materials.append(M[m]); return ob

R_CR, OFF = 4.8, 5.3
ZF = 8.4                      # пример: этаж 1 (низ ленты на Z_FLOOR+0.05)
zb = ZF + 0.05
box("пол хребта", -14, 26, -30, 40, 0, 3, "floor")
box("лента 8x1.6", 6, 14, -30, 40, zb, zb + 1.6, "band")          # среднее положение
# магнит в кармане ленты: Ø4, карман 1.0, торчит 0.5
cyl("магнит", 10, 0, zb + 0.6, zb + 2.1, 2.0, "mag")
# датчик плашмя под лентой: верх на 1 мм ниже низа ленты, центр на +OFF по Y
st = zb - 1.0
cyl_ = box("49E", 8.5, 11.5, OFF - 2, OFF + 2, st - 1.5, st, "sens")
box("ножки", 9.0, 11.0, OFF + 2, OFF + 6, st - 1.2, st - 0.9, "sens")
# стойка с язычком под лентой (снаружи жёлоба, X 15..19) и язычок под датчиком
box("стойка", 15, 19, OFF - 4, OFF + 4, 3, st - 1.5 + 0.01, "post")
box("язычок", 8, 19, OFF - 3, OFF + 3, st - 2.7, st - 1.5, "post")
# стрелки хода ленты ±R_CR
for s in (-1, 1):
    box("ход", 9.6, 10.4, min(0, s * R_CR), max(0, s * R_CR), zb + 2.6, zb + 2.9, "arrow")
    bpy.ops.mesh.primitive_cone_add(radius1=0.9, depth=1.6, vertices=16); c = bpy.context.object
    c.location = (10, s * (R_CR + 0.8), zb + 2.75); c.rotation_euler = (math.radians(-90 * s), 0, 0)
    c.data.materials.append(M["arrow"])

def shot(path, d, scale_mul=1.05):
    lo, hi = Vector((-14, -12, 0)), Vector((26, 16, zb + 4))
    center = (lo + hi) / 2; size = hi - lo
    cd = bpy.data.cameras.new("c"); cd.type = 'ORTHO'; cam = bpy.data.objects.new("c", cd); sc.collection.objects.link(cam)
    cam.location = center + d.normalized() * 200; cam.rotation_euler = d.normalized().to_track_quat("Z", "Y").to_euler()
    cd.clip_start, cd.clip_end = 1, 1000; sc.camera = cam; bpy.context.view_layer.update()
    inv = cam.matrix_world.inverted(); xs, ys = [], []
    for i in range(8):
        p = inv @ Vector(((lo.x, hi.x)[i & 1], (lo.y, hi.y)[(i >> 1) & 1], (lo.z, hi.z)[(i >> 2) & 1])); xs.append(p.x); ys.append(p.y)
    sc.render.resolution_x, sc.render.resolution_y = 1400, 900
    cd.ortho_scale = max(max(xs) - min(xs), (max(ys) - min(ys)) * 1400 / 900) * scale_mul
    cam.location += cam.matrix_world.to_3x3() @ Vector(((max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2, 0))
    sc.render.engine = 'BLENDER_WORKBENCH'; sh = sc.display.shading
    sh.light, sh.color_type, sh.show_object_outline, sh.show_cavity = 'STUDIO', 'MATERIAL', True, True
    sc.render.image_settings.file_format = 'JPEG'; sc.render.image_settings.quality = 88
    sc.render.filepath = path; bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam); bpy.data.cameras.remove(cd)
os.makedirs(IMG, exist_ok=True)
shot(os.path.join(IMG, "hall_format_iso.jpg"), Vector((1, -1.1, 0.8)))
shot(os.path.join(IMG, "hall_format_side.jpg"), Vector((1, 0, 0.05)))
print("HALL FORMAT OK")
