# -*- coding: utf-8 -*-
r"""Сцена-инструкция: сборка кассеты с макетом мотора по шагам (стол 106). Каждый шаг — 50 кадров: деталь подлетает
со стороны, откуда её ставят; подпись шага над кассетой; маркеры на шкале времени. В конце тележка ходит ±24.
Запуск: blender -b -P 2-0\kasseta\scene_kasseta_sborka.py
"""
import math
import os
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
P_STL = os.path.join(HERE, "..", "Print", "Print")
OUT = os.path.join(HERE, "Кассета_сборка.blend")
Y_PIN, Y_FLOAT = 16.5, 6.0
P = math.pi * 0.5
SP_FLOAT = 5 * P
Z_GEAR0 = 1.2 + 17.5 + 0.1
STEP = 50

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.unit_settings.system, sc.unit_settings.scale_length, sc.unit_settings.length_unit = 'METRIC', 0.001, 'MILLIMETERS'


def mat(name, rgba, alpha=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rgba
    if alpha < 1:
        b.inputs["Alpha"].default_value = alpha
        m.surface_render_method = 'BLENDED'
    m.diffuse_color = (rgba[0], rgba[1], rgba[2], alpha)
    return m


def stl(fname, name, m, loc):
    bpy.ops.wm.stl_import(filepath=os.path.join(P_STL, fname + ".stl"))
    ob = bpy.context.selected_objects[0]
    ob.name = name
    ob.data.materials.clear()
    ob.data.materials.append(m)
    ob.location = loc
    return ob


def rod(name, x, y, z0, z1, m, r=0.875):
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=r, depth=z1 - z0, location=(x, y, (z0 + z1) / 2))
    ob = bpy.context.object
    ob.name = name
    ob.data.materials.append(m)
    return ob


M_GREY = mat("основание", (0.80, 0.80, 0.84, 1), 0.55)
M_MK = mat("макет мотора", (0.25, 0.25, 0.28, 1))
M_ROD = mat("пруток 1.75", (0.95, 0.85, 0.20, 1))
steps = []          # (подпись, [(объект, откуда — смещение)])

stand = stl("kas_podstavka", "подставка", mat("подставка", (0.6, 0.45, 0.3, 1)), (0, 0, -8))
steps.append(("1. Подставка на стол", [(stand, (0, 0, -40))]))
base = stl("kas_osnovanie", "основание", M_GREY, (0, 0, 0))
steps.append(("2. Основание пока рядом — сначала собираем мотор (подставку ставим в конце)", [(base, (0, 0, 60))]))
body = stl("kas_maket_korpus", "макет мотора: корпус", M_MK, (0, Y_PIN, 1.2))
steps.append(("3. Корпус мотора задвинуть СБОКУ под стенку (сверху не пролезет). Штырьки снизу, если есть, срезать", [(body, (0, 45, 0))]))
pins = []
for a in (150, 210, 270, 330):
    pins.append(rod("пруток в дырку М2", 9 * math.cos(math.radians(a)), Y_PIN + 9 * math.sin(math.radians(a)), -0.6, 3.8, M_ROD))
steps.append(("4. Снизу сквозь дырки основания — кусочки прутка 1.75 в корпус, капля клея", [(p, (0, 0, -30)) for p in pins]))
axle = stl("kas_maket_os", "макет мотора: ось D5", M_MK, (0, Y_PIN, 18.7 - 23.7))
steps.append(("5. Ось — сверху сквозь корпус и окно основания", [(axle, (0, 0, 50))]))
boss = stl("kas_maket_vystup", "макет мотора: выступ", mat("выступ", (0.5, 0.5, 0.55, 1)), (0, Y_PIN, 15.2))
steps.append(("6. Выступ — сверху на ось (срезом к срезу), капля клея", [(boss, (0, 0, 40))]))
knob = stl("kas_maket_ruchka", "ручка", mat("ручка", (0.2, 0.4, 0.8, 1)), (0, Y_PIN, -5))
steps.append(("7. Ручка — снизу на ось, капля клея", [(knob, (0, 0, -30))]))
pin = stl("kas_shesternya_motora", "шестерня мотора Z18", mat("шестерня мотора", (0.95, 0.55, 0.20, 1)), (0, Y_PIN, Z_GEAR0))
steps.append(("8. Шестерня мотора — на 4 штырька выступа (дырками вниз)", [(pin, (0, 0, 35))]))
sld = stl("kas_polzun_fdm", "ползун", mat("ползун", (0.30, 0.55, 0.85, 1), 0.75), (0, 0, 0))
sub = [(sld, (-70, 0, 0))]
M_FL = mat("плавающие", (0.30, 0.70, 0.40, 1))
for i, x in enumerate((-SP_FLOAT / 2, SP_FLOAT / 2)):
    fo = stl("kas_plav_fdm", "плавающая Z12 %d" % (i + 1), M_FL, (x, Y_FLOAT, Z_GEAR0 + 0.1))
    ax = rod("пруток-ось плавающей", x, Y_FLOAT, Z_GEAR0 - 0.4, 23.5, M_ROD)
    sub += [(fo, (-70, 0, 0)), (ax, (-70, 0, 0))]
steps.append(("9. Заранее: в ползун снизу 2 прутка-оси, на них плавающие шестерни, капля клея на кончик. "
              "Ползун вдвинуть с края (−X), выступ — в паз стенки", sub))
stop = stl("kas_upor", "упор паза", mat("упор", (0.85, 0.2, 0.2, 1)), (-23.6, 22.6, 22.3))
steps.append(("10. Упор — в паз стенки за ползуном, капля клея (ползун больше не выпадет)", [(stop, (-15, 0, 10))]))
cart = stl("kas_telezhka", "тележка", mat("тележка", (0.85, 0.30, 0.30, 1)), (0, 0, 0))
steps.append(("11. Тележка — по ласточкину хвосту с края, выставить по центру", [(cart, (-70, 0, 0))]))
# 12: всё на подставку — двигаем собранную кассету (кроме подставки) сверху; делаем через пустышку-родителя
root = bpy.data.objects.new("кассета (вся)", None)
sc.collection.objects.link(root)
moving = [base, body, axle, boss, knob, pin, stop, cart] + pins + [o for o, _ in sub]
for o in moving:
    o.parent = root

# ---- анимация шагов ----
for k, (title, items) in enumerate(steps):
    f0, f1 = 1 + k * STEP, 1 + k * STEP + 35
    for ob, off in items:
        base_loc = tuple(ob.location)
        ob.location = (base_loc[0] + off[0], base_loc[1] + off[1], base_loc[2] + off[2])
        ob.keyframe_insert("location", frame=1)
        ob.keyframe_insert("location", frame=f0)
        ob.location = base_loc
        ob.keyframe_insert("location", frame=f1)
        # до своего шага деталь скрыта
        ob.hide_viewport = ob.hide_render = True
        ob.keyframe_insert("hide_viewport", frame=1)
        ob.keyframe_insert("hide_render", frame=1)
        ob.hide_viewport = ob.hide_render = False
        ob.keyframe_insert("hide_viewport", frame=f0)
        ob.keyframe_insert("hide_render", frame=f0)
    sc.timeline_markers.new(title.split(" ")[0] + " " + title.split(" ")[1], frame=f0)
    # подпись шага
    bpy.ops.object.text_add(location=(-30, -10, 45), rotation=(math.radians(60), 0, math.radians(20)))
    t = bpy.context.object
    t.data.body = title if len(title) < 70 else title[:68] + "…"
    t.data.size = 3.0
    t.name = "подпись " + str(k + 1)
    t.data.materials.append(mat("подпись", (0.1, 0.1, 0.1, 1)))
    for fr, hid in ((1, True), (f0, False), (f0 + STEP, True)):
        t.hide_viewport = t.hide_render = hid
        t.keyframe_insert("hide_viewport", frame=fr)
        t.keyframe_insert("hide_render", frame=fr)
# шаг 12: собранная кассета опускается на подставку (подставка уже стоит)
f12 = 1 + len(steps) * STEP
root.location = (0, 0, 30)
root.keyframe_insert("location", frame=1)
root.keyframe_insert("location", frame=f12)
root.location = (0, 0, 0)
root.keyframe_insert("location", frame=f12 + 35)
sc.timeline_markers.new("12. На подставку", frame=f12)
# шаг 13: крутим ручку — тележка ходит ±24
f13 = f12 + STEP
sc.timeline_markers.new("13. Крутим ручку", frame=f13)
FR = f13 + 160
for f in range(f13, FR + 1, 2):
    d = 24.0 * math.sin(2 * math.pi * (f - f13) / 158)
    s = d / 2
    a_f, a_p = -s / 3.0, s / 4.5
    sld.location = (s, 0, 0)
    cart.location = (d, 0, 0)
    for o in (sld, cart):
        o.keyframe_insert("location", frame=f)
    for o, rz in ((pin, -a_p), (boss, -a_p), (knob, -a_p), (axle, -a_p)):
        o.rotation_euler = (0, 0, rz)
        o.keyframe_insert("rotation_euler", index=2, frame=f)
    for (o, _), x in zip([it for it in sub if it[0].name.startswith("плавающая")], (-SP_FLOAT / 2, SP_FLOAT / 2)):
        o.location, o.rotation_euler = (x + s, Y_FLOAT, Z_GEAR0 + 0.1), (0, 0, -a_f)
        o.keyframe_insert("location", frame=f)
        o.keyframe_insert("rotation_euler", index=2, frame=f)
    for (o, _), x in zip([it for it in sub if it[0].name.startswith("пруток-ось")], (-SP_FLOAT / 2, SP_FLOAT / 2)):
        o.location = (x + s, Y_FLOAT, o.location[2])
        o.keyframe_insert("location", frame=f)
sc.frame_start, sc.frame_end = 1, FR

tgt = bpy.data.objects.new("цель", None)
sc.collection.objects.link(tgt)
tgt.location = (0, 12, 10)
cam = bpy.data.objects.new("Камера", bpy.data.cameras.new("Камера"))
sc.collection.objects.link(cam)
cam.data.clip_start, cam.data.clip_end, cam.data.lens = 1, 50000, 40
cam.location = (90, -110, 100)
tc = cam.constraints.new('TRACK_TO')
tc.target, tc.track_axis, tc.up_axis = tgt, 'TRACK_NEGATIVE_Z', 'UP_Y'
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
print("сборка кассеты: шагов %d, кадров %d" % (len(steps) + 2, FR))
