# -*- coding: utf-8 -*-
r"""Идея 08.10: «перевёрнутый» привод — катушка неподвижно в грифе (влезает в 50 мм), стержень с магнитами едет
вместе с РАМКОЙ: стойки на концах стержня + планка над катушкой, на планке ложе пальца. Анимация ±22 мм (6 струн).
Запуск: blender -b -P scene_ramka_idea.py  ->  Рамка_стержень_едет.blend"""
import math
import os
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "Рамка_стержень_едет.blend")

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


M_PINK = mat("пластик_катушки", (0.95, 0.55, 0.7, 1))
M_CU = mat("медь", (0.85, 0.42, 0.15, 1))
M_ROD = mat("стержень", (0.55, 0.75, 0.95, 1))
M_N = mat("магнит_N", (0.85, 0.2, 0.2, 1))
M_S = mat("магнит_S", (0.2, 0.35, 0.85, 1))
M_W = mat("шайба", (0.6, 0.6, 0.6, 1))
M_FR = mat("рамка", (0.3, 0.75, 0.35, 1))
M_PAD = mat("ложе", (0.95, 0.8, 0.2, 1))
M_NECK = mat("гриф", (0.55, 0.38, 0.2, 1), 0.18)
M_BASE = mat("крепление", (0.4, 0.4, 0.4, 1))


def box(name, x0, x1, y0, y1, z0, z1, m, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    o = bpy.context.object
    o.name = name
    o.scale = (abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))
    o.data.materials.append(m)
    if parent:
        o.parent = parent
    return o


def cyl_x(name, x0, x1, r, m, parent=None):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=abs(x1 - x0), location=((x0 + x1) / 2, 0, 0),
                                        rotation=(0, math.pi / 2, 0), vertices=32)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(m)
    if parent:
        o.parent = parent
    return o


def label(text, loc, size=4.0, rot=(math.radians(60), 0, 0)):
    bpy.ops.object.text_add(location=loc, rotation=rot)
    t = bpy.context.object
    t.data.body = text
    t.data.size = size
    t.data.align_x = "CENTER"
    t.data.materials.append(mat("текст_" + text[:6], (0.05, 0.05, 0.05, 1)))
    return t


# ---- гриф: полоса 50 мм поперёк (X), прозрачная ----
box("Гриф 50 мм", -25, 25, -32, 32, -17, -15, M_NECK)
for s in (1, -1):
    box("край грифа", s * 25 - 0.4, s * 25 + 0.4, -32, 32, -17, 22, M_NECK)
label("гриф 50 мм — в него влезает только катушка", (0, -48, -16), 3.2)

# ---- катушка: неподвижно, держится снизу за пол грифа ----
BOB, OUT_C = 33.2, 26.0
coil = bpy.data.objects.new("КАТУШКА (неподвижно)", None)
sc.collection.objects.link(coil)
for k in range(5):
    x = -BOB / 2 + k * 8.1
    box("щёчка", x, x + 0.8, -OUT_C / 2, OUT_C / 2, -OUT_C / 2, OUT_C / 2, M_PINK, coil)
for k in range(4):
    x = -BOB / 2 + 0.8 + k * 8.1
    box("обмотка %d" % (k + 1), x + 0.2, x + 7.1, -12.3, 12.3, -12.3, 12.3, M_CU, coil)
box("крепление катушки к полу", -12, 12, -10, 10, -15, -13, M_BASE, coil)
label("катушка — стоит на месте", (0, -30, -15), 3.2)

# ---- стержень + рамка: едут вместе ----
mov = bpy.data.objects.new("СТЕРЖЕНЬ + РАМКА (едут)", None)
sc.collection.objects.link(mov)
ROD_T, ROD_L, SQ = 92.2, 80.2, 17.0
box("стержень (брус)", -ROD_T / 2, ROD_T / 2, -SQ / 2, SQ / 2, -SQ / 2, -6.5, M_ROD, mov)
for s in (1, -1):
    box("стенка бруса", -ROD_T / 2, ROD_T / 2, s * 7.7, s * 8.5, -SQ / 2, SQ / 2, M_ROD, mov)
    box("конец стержня", s * ROD_L / 2, s * ROD_T / 2, -SQ / 2, SQ / 2, -SQ / 2, SQ / 2, M_ROD, mov)
x = -ROD_L / 2 + 0.2
for g in range(5):
    cyl_x("магниты %d (%s)" % (g + 1, "N→" if g % 2 == 0 else "←N"), x, x + 15, 7.5, M_N if g % 2 == 0 else M_S, mov)
    x += 15
    if g < 4:
        cyl_x("шайба М5", x, x + 1.2, 7.5, M_W, mov)
        x += 1.2
PL_Z0, PL_Z1 = OUT_C / 2 + 1.0, OUT_C / 2 + 3.5
for s in (1, -1):
    box("стойка рамки", s * ROD_T / 2 - (6 if s > 0 else 0), s * ROD_T / 2 + (0 if s > 0 else 6), -SQ / 2, SQ / 2,
        -SQ / 2, PL_Z1, M_FR, mov)
box("планка рамки над катушкой", -ROD_T / 2, ROD_T / 2, -8, 8, PL_Z0, PL_Z1, M_FR, mov)
box("ложе пальца", -10, 10, -10, 10, PL_Z1, PL_Z1 + 2, M_PAD, mov)
for s in (1, -1):
    box("бортик ложа", s * 10 - (1.5 if s > 0 else 0), s * 10 + (0 if s > 0 else 1.5), -10, 10, PL_Z1 + 2, PL_Z1 + 7, M_PAD, mov)
label("стержень + рамка + ложе — едут ±22 мм", (0, 0, 40), 3.2)

# ---- анимация: 1-я струна → 6-я → 1-я ----
sc.frame_start, sc.frame_end = 1, 160
for f, xx in ((1, 0), (40, 22), (80, -22), (120, 22), (160, 0)):
    mov.location.x = xx
    mov.keyframe_insert("location", index=0, frame=f)

# ---- свет и камера ----
bpy.ops.object.light_add(type="SUN", location=(0, 0, 200), rotation=(math.radians(35), math.radians(20), 0))
bpy.context.object.data.energy = 3.5
bpy.ops.object.camera_add(location=(40, -120, 165), rotation=(math.radians(38), 0, math.radians(18)))
cam = bpy.context.object
cam.data.clip_start, cam.data.clip_end = 1, 5000
sc.camera = cam
w = bpy.data.worlds.new("мир")
w.color = (0.92, 0.92, 0.9)
sc.world = w
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("сохранено", OUT)
