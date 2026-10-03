# -*- coding: utf-8 -*-
r"""Концепт опыта «магнитный стержень + бегущая катушка» (03.10) из дисков владельца Ø4 × 2.
Стержень: группы по 4 диска (полюс 8 мм) навстречу N-S-N-S, 8 групп = 64 мм, в термоусадке Ø5,
заглушки на концах, держится на двух стойках. Бегунок: печатная гильза (внутри Ø5.2), 4 отсека по 4 мм,
в каждом ~70 витков провода 0.3 (медные), снаружи Ø14; сверху площадка (ложе). Фазы: A = 1 + 3 наоборот,
B = 2 + 4 наоборот — к нашей плате вместо мотора. Анимация: бегунок шагает от края до края.
Запуск: blender -b -P 2-0\magnit\scene_sterzhen_idea.py
"""
import math
import os
import bpy

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Идея_стержень_катушка.blend")
D_M, T_M, GRP, NG = 4.0, 2.0, 4, 8        # диск, группа, групп
POLE = T_M * GRP                           # 8
ROD_L = POLE * NG                          # 64
SEC_W, NSEC = POLE / 2, 4                  # отсек = четверть периода (16)
FR = 0.6                                   # перегородка
BOB_L = NSEC * SEC_W + (NSEC + 1) * FR
R_IN, R_OUT = 2.6, 7.0
FRAMES = 240

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


def cyl_x(name, r, x0, x1, m, parent=None, verts=40, y=0.0, z=0.0):
    """Цилиндр вдоль X."""
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=x1 - x0, location=((x0 + x1) / 2, y, z),
                                        rotation=(0, math.radians(90), 0))
    ob = bpy.context.object
    ob.name = name
    ob.data.materials.append(m)
    if parent:
        ob.parent = parent
    return ob


def tube_x(name, r0, r1, x0, x1, m, parent=None):
    o = cyl_x(name, r1, x0, x1, m, parent)
    cut = cyl_x("вырез", r0, x0 - 1, x1 + 1, m)
    mod = o.modifiers.new("b", "BOOLEAN"); mod.operation = "DIFFERENCE"; mod.object = cut
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cut, do_unlink=True)
    return o


def box(name, x0, x1, y0, y1, z0, z1, m, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), rotation=(0, 0, 0))
    ob = bpy.context.object
    ob.name = name
    ob.scale = (x1 - x0, y1 - y0, z1 - z0)
    ob.data.materials.append(m)
    if parent:
        ob.parent = parent
    return ob


C_N, C_S = mat("группа N→", (0.85, 0.15, 0.15, 1), metal=0.5), mat("группа ←N", (0.15, 0.30, 0.85, 1), metal=0.5)
C_SHR = mat("термоусадка (прозрачная)", (0.1, 0.1, 0.1, 1), 0.25)
C_PR = mat("печать", (0.93, 0.93, 0.95, 1))
C_BOB = mat("гильза бегунка", (0.45, 0.65, 0.95, 1), 0.55)
C_CU = mat("медь", (0.90, 0.40, 0.12, 1), metal=0.3)
C_LZ = mat("ложе", (0.95, 0.72, 0.30, 1))

ZR = 12.0                                   # ось стержня над основой
# стержень: 8 групп по 4 диска, цвет — куда смотрит N (соседние навстречу)
for g in range(NG):
    x0 = -ROD_L / 2 + g * POLE
    for d in range(GRP):
        cyl_x("диск 4×2", D_M / 2 - 0.02, x0 + d * T_M + 0.05, x0 + (d + 1) * T_M - 0.05, C_N if g % 2 == 0 else C_S, z=ZR, verts=24)
cyl_x("термоусадка Ø5", 2.5, -ROD_L / 2 - 1, ROD_L / 2 + 1, C_SHR, z=ZR)
for s in (1, -1):
    cyl_x("заглушка", 2.6, s * ROD_L / 2 + (0 if s > 0 else -3), s * ROD_L / 2 + (3 if s > 0 else 0), C_PR, z=ZR)
# основа и стойки
box("основа", -45, 45, -12, 12, 0, 2, C_PR)
for s in (1, -1):
    box("стойка", s * (ROD_L / 2 + 3), s * (ROD_L / 2 + 3) + s * 4, -5, 5, 2, ZR + 4, C_PR)

# бегунок
bg = bpy.data.objects.new("бегунок (едет)", None)
sc.collection.objects.link(bg)
tube_x("гильза: трубка Ø5.2", R_IN, R_IN + 0.6, -BOB_L / 2, BOB_L / 2, C_BOB, bg)
for k in range(NSEC + 1):
    x = -BOB_L / 2 + k * (SEC_W + FR)
    tube_x("гильза: перегородка", R_IN, R_OUT + 0.6, x, x + FR, C_BOB, bg)
for k in range(NSEC):
    x0 = -BOB_L / 2 + FR + k * (SEC_W + FR)
    tube_x("отсек %d: ~70 витков (%s)" % (k + 1, "A" if k % 2 == 0 else "B"), R_IN + 0.6, R_OUT, x0 + 0.05, x0 + SEC_W - 0.05, C_CU, bg)
box("площадка-ложе", -12, 12, -10, 10, R_OUT + 0.6, R_OUT + 2.6, C_LZ, bg)
for s in (1, -1):
    box("бортик ложа", s * 12 - (1.6 if s > 0 else 0), s * 12 + (0 if s > 0 else 1.6), -10, 10, R_OUT + 2.6, R_OUT + 7.6, C_LZ, bg)
box("стойка ложа", -BOB_L / 2, BOB_L / 2, -3, 3, R_OUT, R_OUT + 0.6, C_BOB, bg)
bg.location = (0, 0, ZR)
travel = ROD_L / 2 - BOB_L / 2 - 2
for f in range(1, FRAMES + 1, 2):
    x = travel * math.sin(2 * math.pi * (f - 1) / (FRAMES - 1))
    bg.location = (x, 0, ZR)
    bg.keyframe_insert("location", frame=f)

for name, loc, tgt, lens in (("Камера: 3/4", (55, -85, 55), (0, 0, 10), 35),
                             ("Камера: сбоку (видно группы магнитов)", (0, -120, 14), (0, 0, 12), 40)):
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
print("saved", OUT, "ход бегунка ±%.0f мм" % travel)
