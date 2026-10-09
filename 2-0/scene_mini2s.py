# -*- coding: utf-8 -*-
r"""Сцена: стенд с мотором, кривошип R14 качается сектором +51.3° / −52.4° (gitara_mini2_sektor.py, столы 95/96):
мотор → кривошип R14 → шатун 95 → плечо 36 : 18 → ложе ±22. Дно, середина и палуба прозрачные. Пробел — анимация.
Запуск: blender -b -P 2-0\scene_mini2s.py
"""
import math
import os
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "Print", "Print")
OUT = os.path.join(HERE, "Стенд_мотор_сектор.blend")
CART_Y, LB, AX, MY, R, RS, LC = 16, 36.0, 52.0, 147.0, 14.0, 18.0, 95.08
Z_ARM, Z_LINK, Z_CEIL, Z_DECK, DECK_T, RUN = 3.2, 5.0, 8.3, 21.0, 3.0, 2.9
SEC_P, SEC_M = 51.3, 52.4
FRAMES = 240

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.unit_settings.system = 'METRIC'
sc.unit_settings.scale_length = 0.001
sc.unit_settings.length_unit = 'MILLIMETERS'
sc.frame_start, sc.frame_end = 1, FRAMES


def mat(name, rgba, alpha=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rgba
    if alpha < 1:
        b.inputs["Alpha"].default_value = alpha
        try:
            m.surface_render_method = 'BLENDED'
        except Exception:
            pass
    m.diffuse_color = (rgba[0], rgba[1], rgba[2], alpha)
    return m


def stl(fname, name, m, loc=(0, 0, 0), rz=0.0):
    bpy.ops.wm.stl_import(filepath=os.path.join(P, fname + ".stl"))
    ob = bpy.context.selected_objects[0]
    ob.name = name
    ob.data.materials.clear()
    ob.data.materials.append(m)
    ob.location = loc
    ob.rotation_euler = (0, 0, math.radians(rz))
    return ob


def rocker(th):
    cx, cy = R * math.cos(th), MY + R * math.sin(th)
    dx, dy = cx, cy - AX
    d = math.hypot(dx, dy)
    a = (RS ** 2 - LC ** 2 + d ** 2) / (2 * d)
    h = math.sqrt(max(RS ** 2 - a ** 2, 0))
    px, py = a * dx / d, a * dy / d
    cands = [(px + h * dy / d, py - h * dx / d), (px - h * dy / d, py + h * dx / d)]
    sx, sy = max(cands, key=lambda q: q[0])
    return math.atan2(sy, sx), (cx, cy), (sx, AX + sy)


C_GLASS = mat("середина (прозрачная)", (0.8, 0.8, 0.82, 1), 0.15)
C_DECK = mat("палуба (прозрачная)", (0.85, 0.82, 0.76, 1), 0.25)
C_BASE = mat("дно", (0.80, 0.80, 0.84, 1), 0.35)
C_MOT = mat("мотор", (0.25, 0.25, 0.28, 1))
C_SP = mat("проставка", (0.6, 0.6, 0.62, 1))
C_CR = mat("кривошип R14", (0.85, 0.35, 0.35, 1))
C_SH = mat("шатун 95", (0.30, 0.70, 0.40, 1))
C_ARM = mat("плечо 36:18", (0.25, 0.45, 0.80, 1))
C_LZ = mat("ложе", (0.95, 0.72, 0.30, 1))

stl("mini2s_base", "дно", C_BASE)
stl("mini2s_mid", "середина", C_GLASS, (0, 0, Z_CEIL))
stl("mini2s_deck", "палуба", C_DECK, (0, 0, Z_DECK))
stl("gdk_spacer0_x2", "проставка (со стенда 82)", C_SP, (0, MY, 0))
stl("gdk_motor0_model", "мотор", C_MOT, (0, MY, -4.0))
cr = stl("mini2s_crank", "кривошип R14", C_CR, (0, MY, 0))
sh = stl("mini2s_shatun", "шатун 95", C_SH, (0, 0, Z_LINK))
arm = stl("mini2s_arm", "плечо 36:18", C_ARM, (0, AX, Z_ARM))
lz = stl("mini2s_lozhe", "ложе ±22", C_LZ, (0, CART_Y, Z_DECK + DECK_T - RUN))

for f in range(1, FRAMES + 1):
    s = math.sin(2 * math.pi * 2 * (f - 1) / (FRAMES - 1))           # 2 качания за ролик
    thd = s * (SEC_P if s > 0 else SEC_M)
    phi, (cx, cy), (sx, sy) = rocker(math.radians(thd))
    cr.rotation_euler = (0, 0, math.radians(thd))
    cr.keyframe_insert("rotation_euler", index=2, frame=f)
    sh.location = (cx, cy, Z_LINK)
    sh.rotation_euler = (0, 0, math.atan2(-(sx - cx), sy - cy))
    sh.keyframe_insert("location", frame=f)
    sh.keyframe_insert("rotation_euler", index=2, frame=f)
    arm.rotation_euler = (0, 0, phi)
    arm.keyframe_insert("rotation_euler", index=2, frame=f)
    lz.location.x = LB * math.sin(phi)
    lz.keyframe_insert("location", index=0, frame=f)


def camera(name, loc, target, lens):
    tgt = bpy.data.objects.new(name + " цель", None)
    sc.collection.objects.link(tgt)
    tgt.location = target
    c = bpy.data.objects.new(name, bpy.data.cameras.new(name))
    sc.collection.objects.link(c)
    c.data.clip_start, c.data.clip_end = 1, 50000
    c.data.lens = lens
    c.location = loc
    tc = c.constraints.new('TRACK_TO')
    tc.target = tgt
    tc.track_axis = 'TRACK_NEGATIVE_Z'
    tc.up_axis = 'UP_Y'
    return c


cam = camera("Камера: сверху", (0, 85, 330), (0, 85, 0), 35)
camera("Камера: сбоку", (170, -60, 150), (0, 85, 5), 35)
sc.camera = cam
sun = bpy.data.objects.new("Солнце", bpy.data.lights.new("Солнце", "SUN"))
sun.data.energy = 3
sun.rotation_euler = (math.radians(30), math.radians(15), math.radians(30))
sc.collection.objects.link(sun)
for scr in bpy.data.screens:
    for area in scr.areas:
        if area.type == 'VIEW_3D':
            for sp in area.spaces:
                if sp.type == 'VIEW_3D':
                    sp.clip_start, sp.clip_end, sp.lens = 1, 50000, 250
sc.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("saved", OUT)
