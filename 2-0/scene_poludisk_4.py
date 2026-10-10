# -*- coding: utf-8 -*-
r"""Идея владельца 10.10: у каждого пальца ОДИН диск с мотором в деке и ПОЛУДИСК прямо у тележки на своём этаже;
планка соединяет пальцы обоих (спарник) — полудиск повторяет поворот диска в деке. Полудиск крутится полуоборотом
на сторону деки (палец ходит полукругом), штырь его пальца ведёт тележку поперёк ±20 (лапа тележки с прорезью
вдоль грифа). Планка держится за оба конца — вбок не гнётся, давление ученика уходит в ось полудиска.
Ближняя к деке тележка — верхний этаж. Запуск: blender -b -P scene_poludisk_4.py -> Полудиск_4_этажа.blend"""
import math
import os
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "Полудиск_4_этажа.blend")
R = 20.0
CARS = [("указательный", 60.0), ("средний", 86.0), ("безымянный", 111.0), ("мизинец", 135.0)]
MOT_Y = [-220.0, -160.0, -100.0, -40.0]
ZL = [-5.0, -11.0, -17.0, -23.0]                 # пол этажа
FRAMES = 200
OFF = 28.0                                       # 10.10: полудиск сдвинут от тележки к деке — штырь тележки неподвижен по y

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.unit_settings.system = "METRIC"
sc.unit_settings.scale_length = 0.001
sc.unit_settings.length_unit = "MILLIMETERS"
sc.frame_start, sc.frame_end = 1, FRAMES


def mat(name, rgba, alpha=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rgba
    b.inputs["Alpha"].default_value = alpha
    if alpha < 1:
        m.surface_render_method = "BLENDED"
    m.diffuse_color = (rgba[0], rgba[1], rgba[2], alpha)
    return m


def box(name, x0, x1, y0, y1, z0, z1, m, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    o = bpy.context.object
    o.name = name
    o.scale = (abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))
    o.data.materials.append(m)
    if parent:
        o.parent = parent
    return o


def cyl(name, x, y, z0, z1, r, m, parent=None, verts=32):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=z1 - z0, location=(x, y, (z0 + z1) / 2), vertices=verts)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(m)
    if parent:
        o.parent = parent
    return o


def half_disk(name, r, z0, z1, m, parent):
    """полудиск: половина круга на сторону −Y (к деке) + ступица"""
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=z1 - z0, location=(0, 0, (z0 + z1) / 2), vertices=48)
    o = bpy.context.object
    o.name = name
    bpy.ops.object.mode_set(mode="EDIT")
    import bmesh
    bm = bmesh.from_edit_mesh(o.data)
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, 0), plane_no=(0, 1, 0), clear_outer=True)
    bmesh.ops.holes_fill(bm, edges=bm.edges[:], sides=0)
    bmesh.update_edit_mesh(o.data)
    bpy.ops.object.mode_set(mode="OBJECT")
    o.data.materials.append(m)
    o.parent = parent
    return o


def empty(name, loc=(0, 0, 0)):
    e = bpy.data.objects.new(name, None)
    e.location = loc
    sc.collection.objects.link(e)
    return e


def label(text, loc, size=4.0):
    bpy.ops.object.text_add(location=loc, rotation=(math.radians(55), 0, 0))
    t = bpy.context.object
    t.data.body = text
    t.data.size = size
    t.data.align_x = "CENTER"
    t.data.materials.append(M_TXT)


M_TXT = mat("текст", (0.05, 0.05, 0.05, 1))
M_PL = mat("пол этажа (прозрачный)", (0.6, 0.5, 0.4, 1), 0.10)
M_MOT = mat("мотор", (0.25, 0.25, 0.28, 1))
M_AX = mat("ось и пальцы", (0.15, 0.15, 0.15, 1))
COLS = [(0.9, 0.3, 0.3, 1), (0.95, 0.65, 0.15, 1), (0.3, 0.7, 0.35, 1), (0.3, 0.5, 0.95, 1)]

box("накладка грифа", -25, 25, 0, 175, -1.5, 0, mat("накладка", (0.55, 0.38, 0.2, 1), 0.15))
for k, z in enumerate(ZL):
    box("пол этажа %d" % (k + 1), -25, 25, -250, 175, z - 1.0, z, M_PL)
label("ДЕКА: диск на моторе", (0, -150, 12), 5)
label("ГРИФ: полудиск у каждой тележки повторяет диск в деке", (0, 110, 18), 4)

fingers = []
for k, (name, cy) in enumerate(CARS):
    m = mat(name, COLS[k])
    z, ym = ZL[k], MOT_Y[k]
    box("%s: мотор" % name, -17.5, 17.5, ym - 17.5, ym + 17.5, -60, -36, M_MOT)
    cyl("%s: вал" % name, 0, ym, -36, z + 0.2, 2.5, M_MOT)
    dd = empty("%s: диск в деке" % name, (0, ym, z + 0.2))
    cyl("диск", 0, 0, 0, 1.8, R + 3.5, m, dd)
    cyl("палец", R, 0, 1.8, 4.0, 2.5, M_AX, dd)
    # полудиск у тележки: ось на полу своего этажа под тележкой
    yh = cy - OFF                                                                 # ось полудиска — со стороны деки от тележки
    cyl("%s: ось полудиска (на полу этажа)" % name, 0, yh, z, z + 2.2, 2.5, M_AX)
    hd = empty("%s: полудиск" % name, (0, yh, z + 0.2))
    half_disk("полудиск", R + 3.5, 0, 1.8, m, hd)
    cyl("палец полудиска (короткий, в лапу)", 0, -R, 1.8, 5.6, 2.5, M_AX, hd)   # палец на −Y (θ=270° локально)
    # планка между пальцами (над дисками)
    bar = empty("%s: планка-спарник (этаж %d)" % (name, k + 1))
    box("планка", -3, 3, 0, yh - ym, 0, 1.6, m, bar)
    # тележка: ложе + лапа с прорезью вдоль грифа на высоте пола над этажом
    car = empty("%s: тележка" % name, (0, cy, 0))
    box("дно ложа", -11, 11, -7, 7, 0.5, 2.5, m, car)
    z_lapa = z + 0.2 + 1.8 + 2.2 + 0.3                                           # над планкой своего этажа
    box("штырь тележки (неподвижен по y)", -2.5, 2.5, -2.5, 2.5, z_lapa, 0.5, m, car)
    y0, y1 = -OFF - R - 4, 3                                                      # лапа к деке, прорезь вдоль грифа
    for sx in (1, -1):
        box("лапа: бок", sx * 2.8 - (0 if sx > 0 else 2.2), sx * 2.8 + (2.2 if sx > 0 else 0), y0, y1, z_lapa, z_lapa + 1.6, m, car)
    box("лапа: торец", -5, 5, y0, y0 + 1.5, z_lapa, z_lapa + 1.6, m, car)
    for s in (1, -1):
        box("бортик", s * 11 - (1.6 if s > 0 else 0), s * 11 + (0 if s > 0 else 1.6), -7, 7, 2.5, 7.5, m, car)
    label(name, (-40, cy, 4), 3.5)
    fingers.append((dd, hd, bar, car, ym, cy, z))

# полуоборот на сторону деки: угол пальца θ от 180° до 360° (палец на −Y), поперёк x = R·cosθ
for f in range(1, FRAMES + 1):
    th = math.pi + math.pi * (1 - math.cos(2 * math.pi * (f - 1) / (FRAMES - 1))) / 2
    x, dy = R * math.cos(th), R * math.sin(th)
    for dd, hd, bar, car, ym, cy, z in fingers:
        dd.rotation_euler = (0, 0, th)
        dd.keyframe_insert("rotation_euler", index=2, frame=f)
        hd.rotation_euler = (0, 0, th + math.pi / 2)                       # палец полудиска локально на −Y
        hd.keyframe_insert("rotation_euler", index=2, frame=f)
        bar.location = (x, ym + dy, z + 2.2)        # палец диска в деке: (x, ym + dy); палец полудиска: (x, yh + dy)
        bar.keyframe_insert("location", frame=f)
        car.location.x = x
        car.keyframe_insert("location", index=0, frame=f)

tgt = empty("цель", (0, -30, -15))
cam = bpy.data.objects.new("Камера", bpy.data.cameras.new("Камера"))
sc.collection.objects.link(cam)
cam.data.clip_start, cam.data.clip_end, cam.data.lens = 1, 50000, 28
cam.location = (300, -260, 300)
tc = cam.constraints.new("TRACK_TO")
tc.target, tc.track_axis, tc.up_axis = tgt, "TRACK_NEGATIVE_Z", "UP_Y"
sc.camera = cam
w = bpy.data.worlds.new("мир")
w.color = (0.92, 0.92, 0.9)
sc.world = w
sun = bpy.data.objects.new("Солнце", bpy.data.lights.new("Солнце", "SUN"))
sun.data.energy = 3
sun.rotation_euler = (math.radians(30), math.radians(15), math.radians(30))
sc.collection.objects.link(sun)
sc.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("saved", OUT)
