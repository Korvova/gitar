# -*- coding: utf-8 -*-
r"""Концепт пробного магнитного русла (03.10) под магниты 15 × 10 × 5 N52 — как 15.3–15.5 на вики.
Вид поперёк грифа: неподвижная пластина из 8 плоских катушек (оранжевые — фаза A, зелёные — B),
её обнимает U-скоба: по 3 магнита с каждой стороны (красный — N к пластине, синий — S),
снаружи стальные пластины, сверху мостик, стойка сквозь прорезь палубы и ложе.
Скоба ездит ±22 мм (струна 6 → 1). Фигуры условные — только чтобы увидеть устройство.
Запуск: blender -b -P 2-0\magnit\scene_ruslo_proba.py
"""
import math
import os
import bpy

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Магнитное_русло_проба.blend")
FRAMES = 120
NC, CW, WIN = 8, 6.5, 1.6            # катушки: 8 штук по 6.5, окно 1.6
TC = 3.0                             # толщина пластины катушек
Z0, H, END = 1.0, 15.0, 2.0          # дно, активная высота, лобовые части
MZ = Z0 + END + H / 2                # центр магнитов по высоте
G, MT = 4.0, 5.0                     # щель, толщина магнита
PHASE = "AbBAbaAb"                   # из lane_2phase.py: A+ b=B+ a=A− B=B−

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


def box(name, x0, x1, y0, y1, z0, z1, m, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), rotation=(0, 0, 0))
    ob = bpy.context.object
    ob.name = name
    ob.scale = (x1 - x0, y1 - y0, z1 - z0)
    ob.data.materials.append(m)
    if parent:
        ob.parent = parent
    return ob


C_BASE = mat("основа русла", (0.8, 0.8, 0.82, 1), 0.35)
C_DECK = mat("палуба (прозрачная)", (0.85, 0.82, 0.76, 1), 0.2)
C_A = mat("катушка фаза A", (0.95, 0.55, 0.15, 1))
C_B = mat("катушка фаза B", (0.25, 0.70, 0.35, 1))
C_N = mat("магнит N", (0.85, 0.15, 0.15, 1))
C_S = mat("магнит S", (0.15, 0.30, 0.85, 1))
C_FE = mat("сталь", (0.45, 0.47, 0.50, 1))
C_PR = mat("печать скобы", (0.95, 0.95, 0.95, 1), 0.55)
C_LZ = mat("ложе", (0.95, 0.72, 0.30, 1))

# основа русла и стенки по концам (ширина грифа 52)
box("основа русла", -28, 28, -12, 12, 0, Z0, C_BASE)
for s in (-1, 1):
    box("стенка", s * 26, s * 28, -12, 12, Z0, 21, C_BASE)
# пластина катушек: 8 рамок (две ветви + лобовые части)
for k in range(NC):
    x0 = -26 + k * CW
    m = C_A if PHASE[k] in "Aa" else C_B
    leg = (CW - WIN) / 2
    for a, b in ((x0, x0 + leg), (x0 + CW - leg, x0 + CW)):
        box("катушка %d (%s): ветвь" % (k + 1, PHASE[k]), a, b, -TC / 2, TC / 2, Z0, Z0 + 2 * END + H, m)
    box("катушка %d: лобовая низ" % (k + 1), x0, x0 + CW, -TC / 2, TC / 2, Z0, Z0 + END, m)
    box("катушка %d: лобовая верх" % (k + 1), x0, x0 + CW, -TC / 2, TC / 2, Z0 + END + H, Z0 + 2 * END + H, m)
# палуба со щелью под стойку скобы
ZD = Z0 + 2 * END + H + 2.0
box("палуба: сторона грифа", -26, 26, -12, -2, ZD, ZD + 1.5, C_DECK)
box("палуба: сторона деки", -26, 26, 2, 12, ZD, ZD + 1.5, C_DECK)

# скоба: пустышка, всё остальное — дети
sk = bpy.data.objects.new("скоба с магнитами (едет)", None)
sc.collection.objects.link(sk)
for side in (-1, 1):
    y0 = side * G / 2
    y1 = side * (G / 2 + MT)
    for p in range(3):
        n_up = (p % 2 == 0) == (side < 0)                 # напротив друг друга — разные полюса
        box("магнит 15×10×5", -15 + p * 10, -5 + p * 10, min(y0, y1), max(y0, y1), MZ - H / 2, MZ + H / 2,
            C_N if n_up else C_S, sk)
    ys0 = side * (G / 2 + MT)
    ys1 = side * (G / 2 + MT + 1.2)
    box("стальная пластина 30×17×1.2", -15, 15, min(ys0, ys1), max(ys0, ys1), MZ - 8.5, MZ + 8.5, C_FE, sk)
    yw0 = side * (G / 2 + MT + 1.2)
    yw1 = side * (G / 2 + MT + 2.4)
    box("стенка скобы (печать)", -15, 15, min(yw0, yw1), max(yw0, yw1), MZ - 9, Z0 + 2 * END + H + 1.7, C_PR, sk)
box("мостик над пластиной", -15, 15, -(G / 2 + MT + 2.4), G / 2 + MT + 2.4, Z0 + 2 * END + H + 0.5, Z0 + 2 * END + H + 1.7, C_PR, sk)
box("стойка сквозь прорезь", -3, 3, -1.5, 1.5, Z0 + 2 * END + H + 1.7, ZD + 1.8, C_PR, sk)
box("ложе 24×22", -12, 12, -11, 11, ZD + 1.8, ZD + 3.8, C_LZ, sk)
for s in (-1, 1):
    box("бортик ложа", s * 12 - (1.6 if s > 0 else 0), s * 12 + (0 if s > 0 else 1.6), -11, 11, ZD + 3.8, ZD + 8.8, C_LZ, sk)

for f in range(1, FRAMES + 1, 2):
    sk.location = (22 * math.sin(2 * math.pi * (f - 1) / (FRAMES - 1)), 0, 0)
    sk.keyframe_insert("location", frame=f)


def camera(name, loc, target, lens):
    tgt = bpy.data.objects.new(name + " цель", None)
    sc.collection.objects.link(tgt)
    tgt.location = target
    c = bpy.data.objects.new(name, bpy.data.cameras.new(name))
    sc.collection.objects.link(c)
    c.data.clip_start, c.data.clip_end = 1, 10000
    c.data.lens = lens
    c.location = loc
    tc = c.constraints.new('TRACK_TO')
    tc.target = tgt
    tc.track_axis = 'TRACK_NEGATIVE_Z'
    tc.up_axis = 'UP_Y'
    return c


cam = camera("Камера: 3/4", (70, -90, 70), (0, 0, 10), 35)
camera("Камера: торец (видно U-скобу)", (90, 0, 12), (0, 0, 11), 40)
sc.camera = cam
sun = bpy.data.objects.new("Солнце", bpy.data.lights.new("Солнце", "SUN"))
sun.data.energy = 3
sun.rotation_euler = (math.radians(35), math.radians(10), math.radians(40))
sc.collection.objects.link(sun)
sc.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("saved", OUT)
