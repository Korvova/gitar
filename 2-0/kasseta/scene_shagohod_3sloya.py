# Три слоя реек со сдвигом 120°: шаг зубьев sqrt(3)*E, ход плавнее, мёртвой точки нет. Заметка 19.44.
# Рейки в пределах грифа: тело ±24, с размахом ±2 ровно ±26. Этажи по 1.5 мм, дно тележки 2. Тележка на краю свисает, зубья берут часть гребёнки.
# -*- coding: utf-8 -*-
# Шагоход плашмя (идея владельца): мотор лежит, ось вертикальная. Две плоские рейки в два этажа ходят по кругу в горизонтальной
# плоскости в противофазе, зубья смотрят вбок (+Y) и по очереди входят в гребёнку тележки. Оси: X вдоль реек, Y поперёк, Z вверх,
# Z = 0 — верх мотора.
import bpy, bmesh, math, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Шагоход_3_слоя.blend")
E = 2.0; P = math.sqrt(3) * E; TRAVEL = 22.0; FR = 480
Y_BODY = 5.0; H_T = 2.8; Y_C = 8.3; T_C = 2.7
FA = (0.3, 1.8); FB = (2.1, 3.6); FC = (3.9, 5.4)        # этажи реек
ANG = TRAVEL / (3 * P) * 360.0
XI = 17.0

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.unit_settings.system = 'METRIC'; sc.unit_settings.scale_length = 0.001; sc.unit_settings.length_unit = 'MILLIMETERS'
sc.frame_start, sc.frame_end = 1, FR
def mat(n, c, a=1.0):
    m = bpy.data.materials.new(n); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]; b.inputs["Base Color"].default_value = c
    if a < 1:
        b.inputs["Alpha"].default_value = a
        try: m.surface_render_method = 'BLENDED'
        except Exception: pass
    m.diffuse_color = (c[0], c[1], c[2], a); return m
M_A = mat("рейка А", (0.72, 0.72, 0.74, 1)); M_B = mat("рейка Б", (0.36, 0.4, 0.55, 1))
M_C = mat("тележка: гребёнка", (0.6, 0.15, 0.65, 1)); M_TOP = mat("тележка: ложе (прозрачное)", (0.5, 0.85, 0.3, 1), 0.3)
M_D = mat("вал", (0.1, 0.15, 0.75, 1)); M_ECC = mat("эксцентрики", (0.15, 0.7, 0.2, 1))
M_MOT = mat("мотор плашмя", (0.1, 0.1, 0.25, 1)); M_G = mat("направляющие (стоят)", (0.55, 0.45, 0.3, 1), 0.6)
M_N = mat("края грифа ±26", (0.95, 0.25, 0.55, 1))
def box(name, x0, x1, y0, y1, z0, z1, m, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x0+x1)/2, (y0+y1)/2, (z0+z1)/2))
    o = bpy.context.object; o.name = name; o.scale = (x1-x0, y1-y0, z1-z0)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True); o.data.materials.append(m)
    if parent: o.parent = parent
    return o
def cyl(name, r, z0, z1, x, y, m, parent=None, v=48):
    bpy.ops.mesh.primitive_cylinder_add(vertices=v, radius=r, depth=z1-z0, location=(x, y, (z0+z1)/2))
    o = bpy.context.object; o.name = name
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True); o.data.materials.append(m)
    if parent: o.parent = parent
    return o
def empty(name, loc=(0, 0, 0)):
    e = bpy.data.objects.new(name, None); sc.collection.objects.link(e); e.location = loc; return e
def difference(o, cutters):
    for c_ in cutters:
        md = o.modifiers.new("вырез", 'BOOLEAN'); md.object = c_; md.operation = 'DIFFERENCE'; md.solver = 'EXACT'
    bpy.context.view_layer.objects.active = o
    for md in list(o.modifiers): bpy.ops.object.modifier_apply(modifier=md.name)
    for c_ in cutters: bpy.data.objects.remove(c_)

def rack(name, fl, m):
    R = empty(name); z0, z1 = fl
    B = box("тело рейки", -24, 24, -Y_BODY, Y_BODY, z0, z1, m)
    difference(B, [cyl("c", 4.15, z0-1, z1+1, x_, 0, m) for x_ in (0.0, XI)])
    B.parent = R; B["grp"] = name
    for k in range(-6, 7):
        t = box("зуб", k*P - 0.65, k*P + 0.65, Y_BODY - 0.01, Y_BODY + H_T, z0, z1, m, R); t["grp"] = name
    return R
RA = rack("РЕЙКА А", FA, M_A); RB = rack("РЕЙКА Б", FB, M_B); RC = rack("РЕЙКА В", FC, M_A)
S120, C120 = math.sin(math.radians(120)), math.cos(math.radians(120))

S = empty("ВАЛ (крутит мотор)")
cyl("вал Ø3", 1.5, 0.0, 5.5, 0, 0, M_D, S, 24)
cyl("эксцентрик А", 4.0, FA[0], FA[1], 0, E, M_ECC, S)["grp"] = "ecc"
cyl("эксцентрик Б", 4.0, FB[0], FB[1], E*S120, E*C120, M_ECC, S)["grp"] = "ecc"
cyl("эксцентрик В", 4.0, FC[0], FC[1], -E*S120, E*C120, M_ECC, S)["grp"] = "ecc"
S2 = empty("ВТОРАЯ ОПОРА (крутится сама)", (XI, 0, 0))
cyl("ось Ø3", 1.5, -12.2, 5.5, 0, 0, M_D, S2, 24)
cyl("эксцентрик А", 4.0, FA[0], FA[1], 0, E, M_ECC, S2)["grp"] = "ecc"
cyl("эксцентрик Б", 4.0, FB[0], FB[1], E*S120, E*C120, M_ECC, S2)["grp"] = "ecc"
cyl("эксцентрик В", 4.0, FC[0], FC[1], -E*S120, E*C120, M_ECC, S2)["grp"] = "ecc"
cyl("мотор 2204 плашмя Ø27.8", 13.9, -12.2, 0, 0, 0, M_MOT, None, 64)
box("платформа (стоит на месте относительно мотора)", -26, 26, -15, 15, -12.4, -12.2, M_G)
for sy in (-1, 1):
    ya, yb = sorted((sy*12.2, sy*14.0))
    box("направляющая тележки", -26, 26, ya, yb, 0.3, 5.55, M_G)["grp"] = "fix"
    box("край грифа", -26.3, -25.9, ya, yb, -12.2, -11, M_N); box("край грифа", 25.9, 26.3, ya, yb, -12.2, -11, M_N)

C = empty("ТЕЛЕЖКА")
for k in range(-3, 3):
    xc = (k + 0.5) * P
    box("зуб гребёнки", xc - 0.8, xc + 0.8, Y_C, Y_C + T_C, FA[0], FC[1], M_C, C)["grp"] = "cart"
box("спинка гребёнки", -11, 11, Y_C + T_C, 12.0, FA[0], FC[1], M_C, C)["grp"] = "cart"
box("ложе: дно", -11, 11, -14, 14, 5.6, 7.6, M_TOP, C)["grp"] = "cart"
for sx in (-1, 1):
    xa, xb = sorted((sx*9.5, sx*11))
    box("ложе: борт", xa, xb, -12.5, 12.5, 7.6, 11.4, M_TOP, C)

def cart_x(th):
    n = math.floor((th + 60.0) / 120.0)
    return P * n + E * math.sin(math.radians(th - n * 120.0))
for f in range(1, FR + 1):
    t = (f - 1) / (FR - 1)
    th = ANG * math.sin(2 * math.pi * t); a = math.radians(th)
    S.rotation_euler = (0, 0, -a); S.keyframe_insert("rotation_euler", index=2, frame=f)
    S2.rotation_euler = (0, 0, -a); S2.keyframe_insert("rotation_euler", index=2, frame=f)
    xa, ya = E * math.sin(a), E * math.cos(a)
    for R_, ph in ((RA, 0.0), (RB, 120.0), (RC, 240.0)):
        b_ = a + math.radians(ph)
        R_.location = (E * math.sin(b_), E * math.cos(b_), 0); R_.keyframe_insert("location", frame=f)
    C.location.x = cart_x(th); C.keyframe_insert("location", index=0, frame=f)

def camera(n, loc, tgt, lens=50, ortho=None):
    tg = empty(n + " цель", tgt)
    c = bpy.data.objects.new(n, bpy.data.cameras.new(n)); sc.collection.objects.link(c)
    c.location = loc; c.data.lens = lens; c.data.clip_start = 1; c.data.clip_end = 3000
    if ortho: c.data.type = 'ORTHO'; c.data.ortho_scale = ortho
    k = c.constraints.new('TRACK_TO'); k.target = tg; k.track_axis = 'TRACK_NEGATIVE_Z'; k.up_axis = 'UP_Y'
    return c
sc.camera = camera("Камера: наискосок", (75, -100, 75), (0, 0, 0))
camera("Камера: сверху", (0, 0, 300), (0, 0, 0), ortho=90)
camera("Камера: край хода", (95, -80, 60), (14, 0, 0))
camera("Камера: с торца", (300, 0, -2), (0, 0, -2), ortho=50)
sun = bpy.data.objects.new("Солнце", bpy.data.lights.new("Солнце", "SUN")); sun.data.energy = 3
sun.rotation_euler = (math.radians(40), math.radians(10), math.radians(30)); sc.collection.objects.link(sun)
sc.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=OUT); print("saved", OUT)
