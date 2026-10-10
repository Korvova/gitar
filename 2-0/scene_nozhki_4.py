# -*- coding: utf-8 -*-
r"""Идея 10.10 (владелец): 4 этажа «как стенд 95» — в деке мотор с кривошипом R14 (сектор), длинная спица по своему
этажу тянет/толкает «ножку» (плечо 36 : 18) у своей тележки; ножка качается в своём этаже на оси, стоящей на полу
этажа, и штырём ведёт тележку поперёк ±22. Ось ножки — со стороны деки от тележки, поэтому спица каждого пальца
кончается ДО своей тележки и чужие штыри не цепляет. Ближняя к деке тележка — верхний этаж.
Запуск: blender -b -P scene_nozhki_4.py -> Ножки_4_этажа.blend"""
import math
import os
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "Ножки_4_этажа.blend")
RC, RS, LB, TRAVEL = 14.0, 18.0, 36.0, 22.0
CARS = [("указательный", 60.0), ("средний", 86.0), ("безымянный", 111.0), ("мизинец", 135.0)]
MOT_Y = [-220.0, -160.0, -100.0, -40.0]          # мотор: дальше всех — верхний этаж
ZL = [-5.0, -11.0, -17.0, -23.0]                 # пол этажа (верх пластины)
FRAMES = 200

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


def bar(name, p0, p1, w, z0, t, m, parent=None):
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy)
    bpy.ops.mesh.primitive_cube_add(size=1, location=((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, z0 + t / 2))
    o = bpy.context.object
    o.name = name
    o.scale = (w, L, t)
    o.rotation_euler = (0, 0, -math.atan2(dx, dy))
    o.data.materials.append(m)
    if parent:
        o.parent = parent
    return o


def cyl(name, x, y, z0, z1, r, m, parent=None):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=z1 - z0, location=(x, y, (z0 + z1) / 2), vertices=24)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(m)
    if parent:
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
M_AX = mat("ось", (0.15, 0.15, 0.15, 1))
COLS = [(0.9, 0.3, 0.3, 1), (0.95, 0.65, 0.15, 1), (0.3, 0.7, 0.35, 1), (0.3, 0.5, 0.95, 1)]

box("накладка грифа", -25, 25, 0, 175, -1.5, 0, mat("накладка", (0.55, 0.38, 0.2, 1), 0.15))
for k, z in enumerate(ZL):
    box("пол этажа %d" % (k + 1), -25, 25, -250, 175, z - 1.0, z, M_PL)
label("ДЕКА: моторы с кривошипом R14", (0, -150, 12), 5)
label("ГРИФ: у каждой тележки своя «ножка» на своём этаже", (0, 110, 16), 4)


def solve(th, ym, p, lc):
    """угол ножки φ при угле кривошипа th: |стад − палец кривошипа| = lc; стад (RS·cosφ, p + RS·sinφ)"""
    cx, cy = RC * math.cos(th), ym + RC * math.sin(th)
    lo, hi = -1.3, 1.3
    def f(ph):
        return math.hypot(RS * math.cos(ph) - cx, p + RS * math.sin(ph) - cy) - lc
    for _ in range(70):
        m = (lo + hi) / 2
        if f(lo) * f(m) <= 0:
            hi = m
        else:
            lo = m
    return (lo + hi) / 2, (cx, cy)


fingers = []
for k, (name, cy) in enumerate(CARS):
    m = mat(name, COLS[k])
    z, ym, p = ZL[k], MOT_Y[k], cy - LB                      # ось ножки — за LB до тележки, со стороны деки
    lc = math.hypot(RS - RC, p - ym)
    # сектор кривошипа под ход ±22
    def x_at(thd):
        ph, _ = solve(math.radians(thd), ym, p, lc)
        return -LB * math.sin(ph)
    lo, hi = 0.0, 89.0
    for _ in range(50):
        mm = (lo + hi) / 2
        if abs(x_at(mm)) < TRAVEL:
            lo = mm
        else:
            hi = mm
    sec = lo
    # мотор и кривошип
    box("%s: мотор" % name, -17.5, 17.5, ym - 17.5, ym + 17.5, -60, -36, M_MOT)
    cyl("%s: вал" % name, 0, ym, -36, z + 0.2, 2.5, M_MOT)
    cr = empty("%s: кривошип R14" % name, (0, ym, z + 0.2))
    cyl("диск кривошипа", 0, 0, 0, 1.8, RC + 3.5, m, cr)
    cyl("палец кривошипа", RC, 0, 1.8, 5.2, 2.5, M_AX, cr)
    # ось ножки на полу своего этажа + ножка
    cyl("%s: ось ножки (на полу этажа)" % name, 0, p, z, z + 3.8, 2.5, M_AX)
    leg = empty("%s: ножка 36:18" % name, (0, p, z + 0.2))
    bar("короткое плечо 18", (0, 0), (RS, 0), 5, 0, 1.6, m, leg)
    bar("длинное плечо 36", (0, 0), (0, LB), 5, 0, 1.6, m, leg)
    cyl("стад под спицу", RS, 0, 1.6, 3.6, 2.5, M_AX, leg)
    cyl("штырь тележки", 0, LB, 1.6, -z + 0.5, 2.5, m, leg)
    # спица: от пальца кривошипа до стада ножки (над ножкой)
    sp = bar("%s: спица (этаж %d)" % (name, k + 1), (0, 0), (0, lc), 6, z + 2.0, 1.6, m)
    # тележка (ложе) над накладкой
    car = empty("%s: ложе" % name, (0, cy, 0))
    box("дно ложа", -11, 11, -7, 7, 0.5, 2.5, m, car)
    for s in (1, -1):
        box("бортик", s * 11 - (1.6 if s > 0 else 0), s * 11 + (0 if s > 0 else 1.6), -7, 7, 2.5, 7.5, m, car)
    label(name, (-40, cy, 4), 3.5)
    fingers.append((cr, leg, sp, car, ym, p, lc, sec, z))
    print("%s: этаж %d, спица %.0f мм, сектор кривошипа ±%.1f°" % (name, k + 1, lc, sec))

for f in range(1, FRAMES + 1):
    s = math.sin(2 * math.pi * (f - 1) / (FRAMES - 1))
    for cr, leg, sp, car, ym, p, lc, sec, z in fingers:
        th = math.radians(sec * s)
        ph, (cx, cy) = solve(th, ym, p, lc)
        cr.rotation_euler = (0, 0, th)
        cr.keyframe_insert("rotation_euler", index=2, frame=f)
        leg.rotation_euler = (0, 0, ph)
        leg.keyframe_insert("rotation_euler", index=2, frame=f)
        sx, sy = RS * math.cos(ph), p + RS * math.sin(ph)
        sp.location = ((cx + sx) / 2, (cy + sy) / 2, z + 2.0 + 0.8)
        sp.rotation_euler = (0, 0, -math.atan2(sx - cx, sy - cy))
        sp.keyframe_insert("location", frame=f)
        sp.keyframe_insert("rotation_euler", index=2, frame=f)
        car.location.x = -LB * math.sin(ph)
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
