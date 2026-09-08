# -*- coding: utf-8 -*-
"""Концепт «спица-РЕЙКА -> двухъярусная шестерня -> рейка тележки», анимация.
Запуск: blender -b -P rack_concept.py
Кинематика: кривошип R9 (скотч-йок) двигает спицу по X на +-9; рейка спицы
крутит малый венец r4.5; большой венец r10 двигает поперечную рейку тележки
на +-20 (усиление 1:2.22, сила ~13 Н -> ~6 Н).
"""
import bpy, math, mathutils

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.fps = 24
sc.frame_start, sc.frame_end = 1, 120

MX = 160.0                  # мотор
R_CR = 9.0                  # кривошип
PX, PY = 35.0, -12.5        # ось шестерни
R_S, R_B = 4.5, 10.0        # венцы: малый (спица) / большой (тележка)
RACK_Y = PY - R_S           # линия рейки спицы (юг шестерни) = -17
CARTRACK_X = PX + R_B       # линия рейки тележки (восток шестерни) = 45
Z_SP0, Z_SP1 = 1.0, 2.5     # ярус спицы
Z_BG0, Z_BG1 = 3.6, 5.1     # ярус большого венца


def mat(name, rgba):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = rgba
    return m

M_BASE = mat("base", (0.6, 0.6, 0.6, 1))
M_CART = mat("cart", (0.8, 0.8, 0.82, 1))
M_GEAR = mat("gear", (0.25, 0.45, 0.8, 1))
M_ROD = mat("rod", (0.85, 0.2, 0.15, 1))
M_GOLD = mat("gold", (0.75, 0.6, 0.25, 1))
M_RACK = mat("rack", (0.2, 0.7, 0.3, 1))


def box(name, x0, x1, y0, y1, z0, z1, m, parent=None):
    bpy.ops.mesh.primitive_cube_add()
    ob = bpy.context.object
    ob.name = name
    ob.scale = ((x1 - x0) / 2, (y1 - y0) / 2, (z1 - z0) / 2)
    ob.location = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    ob.data.materials.append(m)
    if parent:
        ob.parent = parent
        ob.matrix_parent_inverse = parent.matrix_world.inverted()
    return ob


def cyl(name, x, y, z0, z1, r, m, parent=None):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=z1 - z0,
                                        location=(x, y, (z0 + z1) / 2))
    ob = bpy.context.object
    ob.name = name
    ob.data.materials.append(m)
    if parent:
        ob.parent = parent
        ob.matrix_parent_inverse = parent.matrix_world.inverted()
    return ob


def empty(name, x, y, z):
    e = bpy.data.objects.new(name, None)
    e.location = (x, y, z)
    sc.collection.objects.link(e)
    return e


PITCH = 3.6                 # шаг зубьев (крупно, для наглядности)

# ---- основание с открытым каналом спицы + окном шестерни ----
box("BaseS", 0, 220, -25, -19.6, 0, 3.5, M_BASE)                   # юг канала
box("BaseFloor", 0, 220, -19.6, -14.8, 0, 1.0, M_BASE)             # дно канала
box("BaseN_W", 0, 25, -14.8, 25, 0, 3.5, M_BASE)                   # север, запад окна
box("BaseN_E", 45, 220, -14.8, 25, 0, 3.5, M_BASE)                 # север, восток окна
box("BaseN_M", 25, 45, -4, 25, 0, 3.5, M_BASE)                     # север, за окном
box("BaseWin", 25, 45, -14.8, -4, 0, 1.0, M_BASE)                  # дно окна шестерни
box("GrooveMark", 43.5, 47.5, -4, 24, 3.45, 3.55, M_CART)
cyl("MotorWell", MX, 0, 3.5, 5.0, 18.0, M_BASE)
cyl("Gear", MX, 0, 5.0, 8.0, 3.0, M_GOLD)

# ---- кривошип (скотч-йок) ----
crank = empty("Crank", MX, 0.0, 0)
cyl("CrankDisc", MX, 0, 8.2, 9.7, 12.0, M_GEAR, parent=crank)
cyl("CrankPin", MX - R_CR, 0, 9.7, 12.6, 1.0, M_GEAR, parent=crank)

# ---- спица: стержень + рейка (зубья на север) + вилка скотч-йока ----
# нейтраль кадра 1: theta=pi -> спица в крайнем западе (dx=0)
sp = empty("SpicaE", 0, 0, 0)
box("SpicaRod", 14, MX - 6.8, RACK_Y - 2.4, RACK_Y - 0.9, Z_SP0, Z_SP1, M_ROD, parent=sp)
# зубья рейки спицы (шаг PITCH), покрывают зону контакта x~35 при dx 0..18
xt = 16.0
while xt < 40:
    box("SpT", xt, xt + PITCH * 0.45, RACK_Y - 0.9, RACK_Y + 0.9, Z_SP0, Z_SP1, M_ROD, parent=sp)
    xt += PITCH
# скотч-йок: колонна от стержня вверх + рамка, пин кривошипа ходит в щели
box("YokeCol", MX - 11.2, MX - 6.8, RACK_Y - 2.4, -15.0, Z_SP0, 12.4, M_ROD, parent=sp)
box("YokeRailW", MX - 11.2, MX - 10.1, -14.0, 13.0, 10.0, 12.4, M_ROD, parent=sp)
box("YokeRailE", MX - 7.9, MX - 6.8, -14.0, 13.0, 10.0, 12.4, M_ROD, parent=sp)
box("YokeCapN", MX - 11.2, MX - 6.8, 13.0, 14.1, 10.0, 12.4, M_ROD, parent=sp)

# ---- двухъярусная шестерня ----
pin = empty("PinionE", PX, PY, 0)
cyl("PinPost", PX, PY, 0.3, 6.0, 1.0, M_BASE, parent=pin)
cyl("PinS", PX, PY, Z_SP0, Z_SP1, R_S - 0.9, M_GEAR, parent=pin)
cyl("PinB", PX, PY, Z_BG0, Z_BG1, R_B - 0.9, M_GEAR, parent=pin)
nS = max(6, int(2 * math.pi * R_S / PITCH))
for k in range(nS):
    a = 2 * math.pi * k / nS
    bpy.ops.mesh.primitive_cube_add()
    t = bpy.context.object
    t.name = "PinSt%d" % k
    t.scale = (0.9, PITCH * 0.22, (Z_SP1 - Z_SP0) / 2)
    t.location = (PX + (R_S - 0.5) * math.cos(a), PY + (R_S - 0.5) * math.sin(a), (Z_SP0 + Z_SP1) / 2)
    t.rotation_euler = (0, 0, a)
    t.data.materials.append(M_GEAR)
    t.parent = pin
    t.matrix_parent_inverse = pin.matrix_world.inverted()
nB = int(2 * math.pi * R_B / PITCH)
for k in range(nB):
    a = 2 * math.pi * k / nB
    bpy.ops.mesh.primitive_cube_add()
    t = bpy.context.object
    t.name = "PinBt%d" % k
    t.scale = (0.9, PITCH * 0.22, (Z_BG1 - Z_BG0) / 2)
    t.location = (PX + (R_B - 0.5) * math.cos(a), PY + (R_B - 0.5) * math.sin(a), (Z_BG0 + Z_BG1) / 2)
    t.rotation_euler = (0, 0, a)
    t.data.materials.append(M_GEAR)
    t.parent = pin
    t.matrix_parent_inverse = pin.matrix_world.inverted()

# ---- тележка + подвес + поперечная рейка (зубья на запад) ----
cart = box("Cart", 28, 42, -11, 11, 6, 13, M_CART)
box("Hanger", 42, 47.4, -11, 11, 5.2, 6.5, M_CART, parent=cart)
box("HangerLeg", 45.9, 47.4, -11, 11, Z_BG0, 5.2, M_CART, parent=cart)
box("CartRack", 45.9, 47.4, -23, 23, Z_BG0, Z_BG1, M_RACK, parent=cart)
yt = -23.0
while yt < 23:
    box("CrT", 44.1, 45.9, yt, yt + PITCH * 0.45, Z_BG0, Z_BG1, M_RACK, parent=cart)
    yt += PITCH

# ---- анимация ----
for fr in range(1, 121):
    theta = math.pi + 2 * math.pi * (fr - 1) / 120.0
    dx = R_CR * math.cos(theta) + R_CR      # 0..18, нейтраль кадра 1 = 0
    crank.rotation_euler = (0, 0, theta - math.pi)
    crank.keyframe_insert("rotation_euler", frame=fr)
    sp.location = (dx, 0, 0)
    sp.keyframe_insert("location", frame=fr)
    pin.rotation_euler = (0, 0, dx / R_S)
    pin.keyframe_insert("rotation_euler", frame=fr)
    cart.location = (35, dx * R_B / R_S - 20.0, 9.5)
    cart.keyframe_insert("location", frame=fr)

# ---- свет, мир, камера ----
bpy.ops.object.light_add(type='SUN', location=(80, -60, 120))
bpy.context.object.data.energy = 4
bpy.context.object.rotation_euler = (math.radians(35), math.radians(15), 0)
w = bpy.data.worlds.new("W")
w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.9, 0.9, 0.9, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 0.7
sc.world = w
bpy.ops.object.camera_add(location=(135, -145, 115))
cam = bpy.context.object
direction = mathutils.Vector((95, -8, 5)) - cam.location
cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 45
sc.camera = cam
sc.frame_set(1)

sc.render.resolution_x, sc.render.resolution_y = 1400, 900
sc.render.filepath = r"C:\App\gitar\2-0\manual\img\_rack_concept.png"
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=r"C:\App\gitar\2-0\Спица_рейка.blend")
print("RACK OK")
