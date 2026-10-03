# -*- coding: utf-8 -*-
r"""Сцена опыта «стержень + бегущая катушка» (стол 87) из настоящих STL: основа, 8 кассет с дисками
(красные/синие группы — направление N), заглушки, гильза с 4 отсеками медной намотки, ложе.
Кадры: 1–80 — кассеты по одной ложатся в стойки (уже склеенным стержнем), 80–110 — гильза надевается,
110–130 — ложе, дальше бегунок ездит ±22.
Запуск: blender -b -P 2-0\magnit\scene_sterzhen_proba.py
"""
import math
import os
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(os.path.dirname(HERE), "Print", "Print")
OUT = os.path.join(HERE, "Стержень_проба_стол87.blend")
SQ, POLE, NG, PLUG, Z_AX = 5.6, 8.0, 8, 6.0, 9.0
PITCH, FL, NSEC, OUTER, HOLE, CORE_W = 4.0, 0.6, 4, 13.0, 6.0, 0.6
BOB_L = NSEC * PITCH + FL
FRAMES = 300

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.unit_settings.system = 'METRIC'
sc.unit_settings.scale_length = 0.001
sc.frame_start, sc.frame_end = 1, FRAMES


def mat(name, rgba, alpha=1.0, metal=0.0):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rgba
    b.inputs["Metallic"].default_value = metal
    if alpha < 1:
        b.inputs["Alpha"].default_value = alpha
        try:
            m.surface_render_method = 'BLENDED'
        except Exception:
            pass
    return m


def stl(fname, name, m, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    bpy.ops.wm.stl_import(filepath=os.path.join(P, fname + ".stl"))
    ob = bpy.context.selected_objects[0]
    ob.name = name
    ob.data.materials.clear(); ob.data.materials.append(m)
    ob.location = loc; ob.rotation_euler = rot
    if parent:
        ob.parent = parent
    return ob


def key(ob, f0, f1, start, end):
    ob.location = start; ob.keyframe_insert("location", frame=1); ob.keyframe_insert("location", frame=f0)
    ob.location = end; ob.keyframe_insert("location", frame=f1)


PLA = mat("печать", (0.93, 0.93, 0.95, 1))
C_K = mat("кассета (полупрозрачная)", (0.93, 0.93, 0.95, 1), 0.35)
C_N, C_S = mat("диски N→", (0.85, 0.15, 0.15, 1), metal=0.4), mat("диски ←N", (0.15, 0.30, 0.85, 1), metal=0.4)
C_CU = mat("медь", (0.90, 0.40, 0.12, 1), metal=0.3)
C_BOB = mat("гильза", (0.45, 0.65, 0.95, 1))
C_LZ = mat("ложе", (0.95, 0.72, 0.30, 1))

stl("sz_osnova", "основа", PLA)
# стержень: кассеты лежат вдоль X (STL кассеты — вдоль Z), внутри диски
for g in range(NG):
    x0 = -NG * POLE / 2 + g * POLE
    e = bpy.data.objects.new("кассета %d" % (g + 1), None); sc.collection.objects.link(e)
    k = stl("sz_kasseta", "кассета %d: корпус" % (g + 1), C_K, rot=(0, math.radians(90 if g % 2 == 0 else -90), 0), parent=e)
    k.location = (0 if g % 2 == 0 else POLE, 0, 0)
    for d in range(4):
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=1.98, depth=1.9, location=(d * 2 + 1, 0, 0), rotation=(0, math.radians(90), 0))
        dd = bpy.context.object; dd.name = "диск 4×2"; dd.data.materials.append(C_N if g % 2 == 0 else C_S); dd.parent = e
    key(e, 5 + g * 8, 12 + g * 8, (x0, 0, Z_AX + 40), (x0, 0, Z_AX))
for s in (1, -1):
    z = stl("sz_zaglushka", "заглушка", PLA, rot=(0, math.radians(90), 0))
    xz = (NG * POLE / 2) if s > 0 else (-NG * POLE / 2 - PLUG)
    key(z, 70, 80, (xz, 0, Z_AX + 30), (xz, 0, Z_AX))
# бегунок: гильза + намотка + ложе
bg = bpy.data.objects.new("бегунок (едет)", None); sc.collection.objects.link(bg)
stl("sz_katushka", "гильза: 4 отсека", C_BOB, parent=bg)
for k in range(NSEC):
    x0 = -BOB_L / 2 + FL + k * PITCH + 0.05
    x1 = x0 + PITCH - FL - 0.1
    r_in, r_out = HOLE / 2 + CORE_W + 0.05, OUTER / 2 - 0.4
    for (y0, y1, z0, z1) in ((-r_out, r_out, r_in, r_out), (-r_out, r_out, -r_out, -r_in),
                             (-r_out, -r_in, -r_in, r_in), (r_in, r_out, -r_in, r_in)):     # квадратное кольцо витков
        bpy.ops.mesh.primitive_cube_add(size=1, location=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), rotation=(0, 0, 0))
        w = bpy.context.object
        w.name = "отсек %d: ~54 витка (%s)" % (k + 1, "A" if k % 2 == 0 else "B")
        w.scale = (x1 - x0, y1 - y0, z1 - z0)
        w.data.materials.append(C_CU)
        w.parent = bg
stl("sz_lozhe", "ложе", C_LZ, loc=(0, 0, OUTER / 2), parent=bg)
travel = NG * POLE / 2 - BOB_L / 2 - 1.0
key(bg, 85, 120, (-NG * POLE / 2 - PLUG - 30, 0, Z_AX), (0, 0, Z_AX))
for f in range(120, FRAMES + 1, 2):
    bg.location = (travel * math.sin(2 * math.pi * (f - 120) / (FRAMES - 120)), 0, Z_AX)
    bg.keyframe_insert("location", frame=f)

for name, loc, tgt, lens in (("Камера: 3/4", (55, -85, 55), (0, 0, 8), 35),
                             ("Камера: сбоку", (0, -120, 12), (0, 0, 10), 40)):
    t = bpy.data.objects.new(name + " цель", None); sc.collection.objects.link(t); t.location = tgt
    c = bpy.data.objects.new(name, bpy.data.cameras.new(name)); sc.collection.objects.link(c)
    c.data.lens = lens; c.data.clip_start = 1; c.location = loc
    tc = c.constraints.new('TRACK_TO'); tc.target = t; tc.track_axis = 'TRACK_NEGATIVE_Z'; tc.up_axis = 'UP_Y'
    if "3/4" in name:
        sc.camera = c
sun = bpy.data.objects.new("Солнце", bpy.data.lights.new("Солнце", "SUN"))
sun.data.energy = 3.5
sun.rotation_euler = (math.radians(35), math.radians(10), math.radians(40))
sc.collection.objects.link(sun)
sc.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("saved", OUT)
