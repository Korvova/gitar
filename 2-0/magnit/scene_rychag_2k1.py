# -*- coding: utf-8 -*-
r"""Один палец (08.10): линейный привод в деке (ход ±44) → рычаг 2:1 в деке (плечи 60 : 30) → лента по этажу
(ход ±22, сила ×2) → «крюк» 1:1 у тележки (плечи 30 : 30) → тележка ±22 поперёк грифа.
Запуск: blender -b -P scene_rychag_2k1.py -> Рычаг_2к1_один_палец.blend"""
import math
import os
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "Рычаг_2к1_один_палец.blend")

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.unit_settings.system = "METRIC"
sc.unit_settings.scale_length = 0.001
sc.unit_settings.length_unit = "MILLIMETERS"


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


M_NECK = mat("гриф", (0.55, 0.38, 0.2, 1), 0.15)
M_DECK = mat("дека", (0.7, 0.6, 0.45, 1), 0.12)
M_ROD = mat("стержень", (0.55, 0.75, 0.95, 1))
M_N = mat("магнит N", (0.85, 0.2, 0.2, 1))
M_S = mat("магнит S", (0.2, 0.35, 0.85, 1))
M_W = mat("шайба", (0.6, 0.6, 0.6, 1))
M_CU = mat("катушка", (0.85, 0.42, 0.15, 1))
M_LEV = mat("рычаг", (0.25, 0.25, 0.25, 1))
M_RIB = mat("лента", (0.95, 0.5, 0.2, 1))
M_CAR = mat("тележка", (0.95, 0.85, 0.3, 1))
M_TXT = mat("текст", (0.05, 0.05, 0.05, 1))


def box(name, x0, x1, y0, y1, z0, z1, m, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    o = bpy.context.object
    o.name = name
    o.scale = (abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))
    o.data.materials.append(m)
    if parent:
        o.parent = parent
    return o


def bar(name, p0, p1, w, t, m, parent=None):
    dx, dy, dz = (p1[i] - p0[i] for i in range(3))
    L = math.sqrt(dx * dx + dy * dy + dz * dz)
    bpy.ops.mesh.primitive_cube_add(size=1, location=tuple((p0[i] + p1[i]) / 2 for i in range(3)))
    o = bpy.context.object
    o.name = name
    o.scale = (w, L, t)
    o.rotation_euler = (math.atan2(dz, math.hypot(dx, dy)), 0, -math.atan2(dx, dy))
    o.data.materials.append(m)
    if parent:
        o.parent = parent
    return o


def cyl(name, loc, r, depth, m, rot=(0, 0, 0), parent=None):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, location=loc, rotation=rot, vertices=32)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(m)
    if parent:
        o.parent = parent
    return o


def label(text, loc, size=7.0):
    bpy.ops.object.text_add(location=loc, rotation=(math.radians(50), 0, 0))
    t = bpy.context.object
    t.data.body = text
    t.data.size = size
    t.data.align_x = "CENTER"
    t.data.materials.append(M_TXT)


def empty(name, loc=(0, 0, 0)):
    e = bpy.data.objects.new(name, None)
    e.location = loc
    sc.collection.objects.link(e)
    return e


box("Гриф 50 мм", -25, 25, 0, 260, -20, 0, M_NECK)
box("Дека", -105, 60, -200, 0, -62, 0, M_DECK)

# ---- привод: стержень 8 полюсов по 3 диска 15×5 + 7 шайб (~128 мм магнитов), ход катушки ±44 ----
QX, QY, ZL = -20.0, -80.0, -20.0          # ось рычага 2:1 в деке, высота рычагов в деке
XA, ZA = QX - 60.0, -35.0                 # ось привода (под концом длинного плеча)
rod_l = 8 * 15 + 7 * 1.2
y0 = QY - rod_l / 2
box("стержень привода (неподвижно)", XA - 8.5, XA + 8.5, y0 - 6, y0 + rod_l + 6, ZA - 8.5, ZA - 6.5, M_ROD)
for s in (1, -1):
    box("стенка бруса", XA + s * 7.7 - (0.8 if s > 0 else 0), XA + s * 7.7 + (0 if s > 0 else 0.8),
        y0 - 6, y0 + rod_l + 6, ZA - 8.5, ZA + 8.5, M_ROD)
y = y0
for g in range(8):
    cyl("магниты %d" % (g + 1), (XA, y + 7.5, ZA), 7.5, 15, M_N if g % 2 == 0 else M_S, rot=(math.pi / 2, 0, 0))
    y += 15
    if g < 7:
        cyl("шайба М5", (XA, y + 0.6, ZA), 7.5, 1.2, M_W, rot=(math.pi / 2, 0, 0))
        y += 1.2
for yy in (y0 - 6, y0 + rod_l + 6):
    box("стойка стержня", XA - 11, XA + 11, yy - 3, yy + 3, -62, ZA + 9, M_DECK)
coil = empty("катушка привода (едет ±44)", (XA, QY, ZA))
box("катушка", -13, 13, -16.6, 16.6, -13, 13, M_CU, coil)
box("кулиса на катушке (поперечная прорезь)", -2, 22, -3, 3, 13, ZL - ZA - 2, M_LEV, coil)
label("привод в деке: ход 88 мм", (XA, QY - 75, 10))

# ---- рычаг 2:1 в деке: длинное плечо 60 к катушке, короткое 30 к ленте ----
lev = empty("рычаг 2:1 (дека)", (QX, QY, ZL))
bar("длинное плечо 60", (0, 0, 0), (-60, 0, 0), 5, 3, M_LEV, lev)
bar("короткое плечо 30", (0, 0, 0), (30, 0, 0), 5, 3, M_LEV, lev)
cyl("ось рычага 2:1", (QX, QY, (ZL - 62) / 2), 3, ZL + 62 + 3, M_LEV)
label("рычаг 2:1 — сила ×2", (QX, QY + 25, 10))

# ---- лента: от короткого плеча по деке, подъём на этаж, по грифу к «крюку» ----
LANE, ZF, YCAR, L1 = 10.0, -8.0, 200.0, 30.0
PY = YCAR + L1
rib = empty("лента (едет ±22)")
bar("лента в деке", (LANE, QY, ZL), (LANE, -30, ZL), 8, 2, M_RIB, rib)
bar("лента: подъём на этаж", (LANE, -30, ZL), (LANE, -5, ZF), 8, 2, M_RIB, rib)
bar("лента по этажу грифа", (LANE, -5, ZF), (LANE, PY, ZF), 8, 2, M_RIB, rib)
box("прорезь ленты у рычага 2:1", -2, LANE + 4, QY - 3, QY + 3, ZL - 1, ZL + 1, M_RIB, rib)
box("прорезь ленты у крюка", -2, LANE + 4, PY - 3, PY + 3, ZF - 1, ZF + 1, M_RIB, rib)
label("лента по этажу: ход 44 мм, сила ×2", (60, 100, 10))

# ---- «крюк» 1:1 у тележки ----
PX = LANE - L1
hook = empty("крюк 1:1", (PX, PY, ZF))
bar("плечо к ленте 30", (0, 0, 0), (L1, 0, 0), 4, 2, M_LEV, hook)
bar("плечо к тележке 30", (0, 0, 0), (0, -L1, 0), 4, 2, M_LEV, hook)
cyl("ось крюка", (PX, PY, ZF), 2.5, 4, M_LEV)
car = empty("тележка", (PX, YCAR, 0))
box("палубка", -9 + 20, 9 + 20, -7, 7, 0, 3, M_CAR, car)
for s in (1, -1):
    box("бортик", 20 + s * 9 - (2 if s > 0 else 0), 20 + s * 9 + (0 if s > 0 else 2), -7, 7, 3, 10, M_CAR, car)
bar("штырь крюка в тележку", (0, 0, ZF), (0, 0, 0), 2.5, 2.5, M_LEV, car)
label("крюк 1:1 — тележка 44 мм поперёк", (0, PY + 15, 15))

# ---- анимация: лента s = 22·sin; рычаг 2:1 θ = asin(s/30); катушка −2s; крюк θ2 = asin(s/30); тележка +s ----
sc.frame_start, sc.frame_end = 1, 160
for f in range(1, 161, 2):
    s = 22.0 * math.sin(2 * math.pi * (f - 1) / 160)
    th = math.asin(s / 30.0)
    lev.rotation_euler.z = th
    lev.keyframe_insert("rotation_euler", index=2, frame=f)
    rib.location.y = s
    rib.keyframe_insert("location", index=1, frame=f)
    coil.location.y = QY - 60 * math.sin(th)
    coil.keyframe_insert("location", index=1, frame=f)
    hook.rotation_euler.z = th
    hook.keyframe_insert("rotation_euler", index=2, frame=f)
    car.location.x = PX + L1 * math.sin(th)
    car.keyframe_insert("location", index=0, frame=f)

bpy.ops.object.light_add(type="SUN", location=(0, 0, 300), rotation=(math.radians(30), math.radians(15), 0))
bpy.context.object.data.energy = 3.5
bpy.ops.object.camera_add(location=(200, -300, 280))
cam = bpy.context.object
tgt = empty("цель камеры", (-20, 20, -20))
c = cam.constraints.new("TRACK_TO")
c.target = tgt
c.track_axis, c.up_axis = "TRACK_NEGATIVE_Z", "UP_Y"
cam.data.lens = 35
cam.data.clip_start, cam.data.clip_end = 1, 50000
sc.camera = cam
w = bpy.data.worlds.new("мир")
w.color = (0.92, 0.92, 0.9)
sc.world = w
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("сохранено", OUT)
