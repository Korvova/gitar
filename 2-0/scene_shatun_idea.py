# -*- coding: utf-8 -*-
"""Концепт «шатун вместо прорези» для стенда одного пальца (27.09.2026, вопрос владельца).

Лента (оранжевая) едет только вдоль грифа, стад на ней вверх. Плечо (синее) качается на оси.
Между стадом ленты и стадом плеча — шатун (зелёный) с двумя КРУГЛЫМИ дырками: ничего не скользит,
только повороты. Точка плеча идёт по дуге (сдвиг вбок до 3 мм) — это забирает наклон шатуна.
Слои снизу вверх: лента → плечо (на ступеньке оси) → шатун сверху. Потолок стенда поднимется на 1.8.
Кинематика: кривошип θ → лента u = 10·sin θ → шатун 16 → плечо φ (решается) → ложе x = 36·sin φ.
Дно, палуба, кривошип, проставка, мотор, ложе — из деталей стенда (gitara_mini1.py); середина скрыта.
Запуск: blender -b -P 2-0\\scene_shatun_idea.py
"""
import math
import os
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "Print", "Print")
OUT = os.path.join(HERE, "Идея_шатун_плечо.blend")
CART_Y, LB, RS, AX, MY, R_CR = 16, 36.0, 18.0, 52.0, 80.0, 10.0
XB, LK = 16.5, 16.0                       # стад ленты по X, длина шатуна (центр — центр)
Z_RIB, Z_ARM, Z_LINK = 3.15, 4.95, 6.75
Z_DECK, DECK_T, RUN = 21.0, 3.0, 2.9
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


def stl(fname, name, m, loc=(0, 0, 0)):
    bpy.ops.wm.stl_import(filepath=os.path.join(P, fname + ".stl"))
    ob = bpy.context.selected_objects[0]
    ob.name = name
    ob.data.materials.clear()
    ob.data.materials.append(m)
    ob.location = loc
    return ob


def box(name, x0, x1, y0, y1, z0, z1, m, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), rotation=(0, 0, 0))
    ob = bpy.context.object
    ob.name = name
    ob.scale = (x1 - x0, y1 - y0, z1 - z0)
    ob.data.materials.append(m)
    if parent:
        ob.parent = parent
    return ob


def cyl(name, x, y, r, z0, z1, m, parent=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=40, radius=r, depth=z1 - z0, location=(x, y, (z0 + z1) / 2), rotation=(0, 0, 0))
    ob = bpy.context.object
    ob.name = name
    ob.data.materials.append(m)
    if parent:
        ob.parent = parent
    return ob


def empty(name, loc):
    e = bpy.data.objects.new(name, None)
    sc.collection.objects.link(e)
    e.location = loc
    return e


C_GLASS = mat("корпус (прозрачный)", (0.8, 0.8, 0.82, 1), 0.12)
C_DECK = mat("палуба (прозрачная)", (0.85, 0.82, 0.76, 1), 0.25)
C_ARM = mat("плечо", (0.25, 0.45, 0.80, 1))
C_RIB = mat("лента", (0.85, 0.38, 0.18, 1))
C_LINK = mat("шатун", (0.25, 0.70, 0.35, 1))
C_HOLE = mat("дырка", (0.1, 0.1, 0.1, 1))
C_LZ = mat("ложе", (0.95, 0.72, 0.30, 1))
C_MOT = mat("мотор", (0.25, 0.27, 0.30, 1))

stl("mini1_base", "дно", C_GLASS)
stl("mini1_deck", "палуба", C_DECK, (0, 0, Z_DECK))
stl("gdk_spacer0_x2", "проставка", C_MOT, (0, MY, 0))
stl("gdk_motor0_model", "мотор", C_MOT, (0, MY, -4.0))
cr = stl("gdk_crank0_x2", "кривошип R10", C_ARM, (0, MY, 0))
lz = stl("gs1_lozhe_v3", "ложе", C_LZ, (0, CART_Y, Z_DECK + DECK_T - RUN))

# лента: пустышка в y = 0 (середина хода), детали — в мировых координатах при u = 0
YB0 = AX + math.sqrt(LK ** 2 - (RS - XB) ** 2)                     # стад ленты при φ = 0
rib = empty("лента (едет по Y)", (0, 0, 0))
box("лента: лапка стада", 6, XB + 4.5, YB0 - 4.5, YB0 + 4.5, Z_RIB, Z_RIB + 1.6, C_RIB, rib)
box("лента: тело", 6, 14, YB0 - 4.5, MY + 5.65, Z_RIB, Z_RIB + 1.6, C_RIB, rib)
cyl("лента: стад вверх", XB, YB0, 2.5, Z_RIB + 1.6, Z_LINK + 1.6, C_RIB, rib)
for x0, x1, y0, y1 in ((-14, 14, MY - 5.65, MY - 2.65), (-14, 14, MY + 2.65, MY + 5.65), (-14, -12.8, MY - 2.65, MY + 2.65)):
    box("лента: кулиса", x0, x1, y0, y1, Z_RIB, Z_RIB + 1.6, C_RIB, rib)

# плечо: пустышка на оси
arm = empty("плечо (качается)", (0, AX, 0))
cyl("плечо: диск оси", 0, 0, 5, Z_ARM, Z_ARM + 1.6, C_ARM, arm)
box("плечо: длинное", -2.5, 2.5, -LB, 0, Z_ARM, Z_ARM + 1.6, C_ARM, arm)
cyl("плечо: пад штыря", 0, -LB, 3.5, Z_ARM, Z_ARM + 1.6, C_ARM, arm)
cyl("плечо: штырь в ложе", 0, -LB, 2.5, Z_ARM + 1.6, Z_DECK + DECK_T + 1.8, C_ARM, arm)
box("плечо: короткое", 0, RS, -2.5, 2.5, Z_ARM, Z_ARM + 1.6, C_ARM, arm)
cyl("плечо: пад стада", RS, 0, 4, Z_ARM, Z_ARM + 1.6, C_ARM, arm)
cyl("плечо: стад вверх", RS, 0, 2.5, Z_ARM + 1.6, Z_LINK + 1.6, C_ARM, arm)

# шатун: пустышка в стаде ленты, смотрит на стад плеча (локальная ось +Y)
link = empty("шатун (две круглые дырки)", (0, 0, 0))
cyl("шатун: у ленты", 0, 0, 4.2, Z_LINK, Z_LINK + 1.6, C_LINK, link)
cyl("шатун: у плеча", 0, -LK, 4.2, Z_LINK, Z_LINK + 1.6, C_LINK, link)
box("шатун: планка", -2.8, 2.8, -LK, 0, Z_LINK, Z_LINK + 1.6, C_LINK, link)
for y in (0, -LK):
    cyl("шатун: дырка", 0, y, 2.6, Z_LINK + 1.55, Z_LINK + 1.65, C_HOLE, link)


def solve_phi(yb):
    """Угол плеча, при котором стад плеча на расстоянии LK от стада ленты (XB, yb)."""
    lo, hi = math.radians(-60), math.radians(60)
    f = lambda p: AX + RS * math.sin(p) + math.sqrt(LK ** 2 - (RS * math.cos(p) - XB) ** 2) - yb
    for _ in range(60):
        mid = (lo + hi) / 2
        if f(lo) * f(mid) <= 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


worst = 0
for f in range(1, FRAMES + 1, 2):
    th = 2 * math.pi * 2 * (f - 1) / (FRAMES - 1)                  # 2 полных оборота
    u = R_CR * math.sin(th)
    yb = YB0 + u
    phi = solve_phi(yb)
    ax_, ay_ = RS * math.cos(phi), AX + RS * math.sin(phi)         # стад плеча
    cr.rotation_euler = (0, 0, th)
    cr.keyframe_insert("rotation_euler", frame=f)
    rib.location = (0, u, 0)
    rib.keyframe_insert("location", frame=f)
    arm.rotation_euler = (0, 0, phi)
    arm.keyframe_insert("rotation_euler", frame=f)
    link.location = (XB, yb, 0)
    link.rotation_euler = (0, 0, math.atan2(ax_ - XB, -(ay_ - yb)))    # локальная −Y шатуна смотрит на стад плеча
    link.keyframe_insert("location", frame=f)
    link.keyframe_insert("rotation_euler", frame=f)
    lz.location.x = LB * math.sin(phi)
    lz.keyframe_insert("location", index=0, frame=f)
    worst = max(worst, abs(LB * math.sin(phi)))
print("ложе ±%.1f" % worst)


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


cam = camera("Камера: шатун крупно", (15, 60, 120), (8, 62, 6), 45)
camera("Камера: сбоку", (120, 20, 70), (5, 62, 6), 40)
sc.camera = cam
sun = bpy.data.objects.new("Солнце", bpy.data.lights.new("Солнце", "SUN"))
sun.data.energy = 3
sun.rotation_euler = (math.radians(30), math.radians(15), math.radians(30))
sc.collection.objects.link(sun)
sc.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("saved", OUT)
