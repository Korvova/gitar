# Концепт: платформа с 4 тележками ездит вдоль грифа, её толкает зубчатая штанга из деки (мотор + шестерня в деке).
import bpy, math, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Гриф_платформа_толкатель.blend")
W, PL = 52.0, 110.0                   # ширина грифа, длина платформы
NECK_L = 470.0                        # гриф от порожка до деки
TRAVEL_Y = 290.0                      # ход платформы вдоль грифа (I..XII)
ST = [16, 42, 67, 91]
POCK, FLOOR, ZM, MD, MT, PR = 16.0, 2.0, 12.5, 20.0, 10.0, 3.0
TRAVEL_X = 22.0
FR = 240
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
M_NECK = mat("гриф (корыто)", (0.85, 0.78, 0.65, 1), 0.35)
M_DECK = mat("дека", (0.7, 0.55, 0.4, 1), 0.25)
M_PLAT = mat("платформа", (0.6, 0.8, 0.6, 1), 0.6)
M_RACK = mat("рейки", (0.55, 0.55, 0.6, 1))
M_MOT = mat("мотор", (0.12, 0.12, 0.14, 1))
M_GEAR = mat("шестерни", (0.85, 0.65, 0.2, 1))
M_CART = mat("тележка", (0.3, 0.55, 0.85, 1))
M_LZ = mat("ложе", (0.95, 0.72, 0.30, 1))
M_ROD = mat("штанга-толкатель", (0.85, 0.3, 0.25, 1))
def box(name, x0, x1, y0, y1, z0, z1, m, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x0+x1)/2, (y0+y1)/2, (z0+z1)/2))
    o = bpy.context.object; o.name = name; o.scale = (x1-x0, y1-y0, z1-z0)
    bpy.ops.object.transform_apply(scale=True); o.data.materials.append(m)
    if parent: o.parent = parent
    return o
def cyl(name, r, depth, loc, rot, m, parent=None, verts=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth, location=loc, rotation=rot)
    o = bpy.context.object; o.name = name; o.data.materials.append(m)
    if parent: o.parent = parent
    return o
def empty(name):
    e = bpy.data.objects.new(name, None); sc.collection.objects.link(e); return e
# ---- неподвижное: корыто грифа (дно + невысокие бортики-направляющие), дека с мотором ----
ZB = -4.0                                             # дно корыта под платформой
box("гриф: дно-корыто", -W/2, W/2, -5, NECK_L, ZB - 2, ZB, M_NECK)
for sx in (-1, 1):
    box("гриф: бортик-направляющая", sx*W/2 - (2 if sx > 0 else 0), sx*W/2 + (0 if sx > 0 else 2), -5, NECK_L, ZB, ZB + 5, M_NECK)
box("канал штанги", -7, 7, PL, NECK_L, ZB, ZB + 1, M_RACK)
box("дека (корпус, упрощённо)", -120, 120, NECK_L, NECK_L + 260, ZB - 60, ZB + 30, M_DECK)
YM = NECK_L + 60                                      # мотор толкателя в деке
cyl("мотор толкателя (в деке)", 18, 30, (0, YM, ZB - 20), (0, 0, 0), M_MOT)
pin = cyl("шестерня толкателя", 6, 8, (0, YM, ZB - 1), (0, 0, 0), M_GEAR, None, 12)
# ---- платформа: дно, рёбра между карманами, поперечные рейки, тележки ----
P = empty("ПЛАТФОРМА (едет вдоль грифа)")
box("платформа: дно", -W/2 + 2, W/2 - 2, 0, PL, ZB + 1, FLOOR, M_PLAT, P)
edges = [0]
for s in ST: edges += [s - POCK/2, s + POCK/2]
edges.append(PL)
for i in range(0, len(edges), 2):
    box("платформа: ребро", -W/2 + 2, W/2 - 2, edges[i], edges[i+1], FLOOR, 25.0, M_PLAT, P)
carts = []
for i, s in enumerate(ST):
    y_m0, y_m1, y_g0, y_g1 = s - 7.5, s + 2.5, s + 3.0, s + 6.0
    box("рейка тележки %d" % i, -W/2 + 2, W/2 - 2, y_g0 - 0.3, y_g1 + 0.3, FLOOR, ZM - PR - 0.6, M_RACK, P)
    e = empty("тележка %d" % i); e.parent = P
    cyl("мотор %d" % i, MD/2, MT, (0, (y_m0+y_m1)/2, ZM), (math.pi/2, 0, 0), M_MOT, e, 40)
    g = cyl("шестерня %d" % i, PR + 0.5, 3, (0, (y_g0+y_g1)/2, ZM), (math.pi/2, 0, 0), M_GEAR, e, 12)
    box("крыша %d" % i, -11, 11, s - POCK/2 - 1, s + POCK/2 + 1, 22.2, 24.8, M_CART, e)
    box("ложе %d" % i, -11, 11, s - 7.5, s + 7.5, 24.8, 26.3, M_LZ, e)
    for sx in (-1, 1):
        box("борт ложа", sx*11 - (1.5 if sx > 0 else 0), sx*11 + (0 if sx > 0 else 1.5), s - 7.5, s + 7.5, 26.3, 31.0, M_LZ, e)
    carts.append((e, g))
# ---- штанга-толкатель: от южного края платформы к деке, зубья снизу ----
ROD_L = TRAVEL_Y + (YM - PL) + 40
R = empty("ШТАНГА-ТОЛКАТЕЛЬ"); R.parent = P
box("штанга 10×6", -5, 5, PL, PL + ROD_L, ZB + 1.2, ZB + 7.2, M_ROD, R)
k = 0.0
while k < ROD_L:
    box("зуб штанги", -5, 5, PL + k, PL + k + 0.9, ZB + 0.2, ZB + 1.2, M_ROD, R); k += 3.14
# ---- анимация: платформа I → XII → I, тележки «паучком», шестерни крутятся ----
for f in range(1, FR + 1):
    t = (f - 1) / (FR - 1)
    py = TRAVEL_Y * 0.5 * (1 - math.cos(2 * math.pi * t))
    P.location.y = py; P.keyframe_insert("location", index=1, frame=f)
    pin.rotation_euler = (0, 0, -py / 6.0); pin.keyframe_insert("rotation_euler", frame=f)
    for i, (e, g) in enumerate(carts):
        x = TRAVEL_X * math.sin(2 * math.pi * (4 * t + i * 0.25))
        e.location.x = x; e.keyframe_insert("location", index=0, frame=f)
        g.rotation_euler = (math.pi/2, -x / PR, 0); g.keyframe_insert("rotation_euler", frame=f)
def camera(n, loc, tgt, lens=35):
    tg = empty(n + " цель"); tg.location = tgt
    c = bpy.data.objects.new(n, bpy.data.cameras.new(n)); sc.collection.objects.link(c)
    c.location = loc; c.data.lens = lens; c.data.clip_start = 1; c.data.clip_end = 10000
    kk = c.constraints.new('TRACK_TO'); kk.target = tg; kk.track_axis = 'TRACK_NEGATIVE_Z'; kk.up_axis = 'UP_Y'
    return c
sc.camera = camera("Камера: наискосок", (330, 40, 260), (0, 300, 0))
camera("Камера: сверху", (0, 330, 900), (0, 330, 0))
camera("Камера: сбоку", (520, 330, 20), (0, 330, 0), 30)
sun = bpy.data.objects.new("Солнце", bpy.data.lights.new("Солнце", "SUN")); sun.data.energy = 3
sun.rotation_euler = (math.radians(30), math.radians(15), math.radians(30)); sc.collection.objects.link(sun)
sc.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=OUT); print("saved", OUT)
