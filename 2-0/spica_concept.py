# -*- coding: utf-8 -*-
"""Концепт «спица + качалка» с АНИМАЦИЕЙ — отдельный файл, канал 1.
Запуск: blender -b -P spica_concept.py
Кинематика (вид сверху): кривошип R11.2 на моторе -> спица -> качалка
(ось в (20,0), плечо спицы 14 к -Y, кулисное плечо к +X) -> палец тележки
на x=35. Полный оборот кривошипа = тележка туда-обратно на +-20.
"""
import bpy, math, mathutils

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.fps = 24
sc.frame_start, sc.frame_end = 1, 120

PVT = (20.0, 0.0)          # ось качалки
R_ROD_ARM = 14.0           # плечо спицы (к -Y)
R_CART_X = 15.0            # от оси до дорожки пальца (x=35)
MX, MY = 160.0, 0.0        # мотор
R_CRANK = 11.2
Z_ARM0, Z_ARM1 = 14.8, 16.3
Z_ROD = 16.9


def mat(name, rgba):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = rgba
    return m

M_BASE = mat("base", (0.6, 0.6, 0.6, 1))
M_CART = mat("cart", (0.8, 0.8, 0.82, 1))
M_MECH = mat("mech", (0.25, 0.45, 0.8, 1))
M_ROD = mat("rod", (0.85, 0.2, 0.15, 1))
M_GOLD = mat("gold", (0.75, 0.6, 0.25, 1))


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


# ---- статика: настил (гриф этаж 1 + дека), метка канавки, мотор ----
box("Base", 0, 260, -25, 25, 0, 3.5, M_BASE)
box("GrooveMark", 27.9, 42.1, -22, 22, 3.45, 3.55, M_CART)
cyl("MotorWell", MX, MY, 3.5, 5.0, 18.0, M_BASE)
cyl("Gear", MX, MY, 5.0, 8.0, 3.0, M_GOLD)
cyl("GearShaft", MX, MY, 8.0, 14.0, 2.2, M_GOLD)     # удлинитель до высоты спицы

# ---- тележка + палец вверх (кулиса ходит над стаканом) ----
cart = box("Cart", 28, 42, -11, 11, 6, 13, M_CART)
cyl("CartPin", 35, 0, 13, 17.2, 1.0, M_MECH, parent=cart)

# ---- качалка: пустышка-ось + стойка + два плеча ----
bell = empty("BellCrank", PVT[0], PVT[1], 0)
cyl("PivotPost", PVT[0], PVT[1], 3.5, Z_ARM1, 1.8, M_MECH, parent=bell)
# кулисное плечо вдоль +X: рельсы кулисы (прорезь r13..27) + торец
box("ArmSolid", PVT[0] - 2, PVT[0] + 13, -1.8, 1.8, Z_ARM0, Z_ARM1, M_MECH, parent=bell)
box("ArmRailS", PVT[0] + 13, PVT[0] + 27, -1.8, -1.1, Z_ARM0, Z_ARM1, M_MECH, parent=bell)
box("ArmRailN", PVT[0] + 13, PVT[0] + 27, 1.1, 1.8, Z_ARM0, Z_ARM1, M_MECH, parent=bell)
box("ArmCap", PVT[0] + 27, PVT[0] + 28.5, -1.8, 1.8, Z_ARM0, Z_ARM1, M_MECH, parent=bell)
# плечо спицы вдоль -Y + палец вверх
box("ArmRod", PVT[0] - 1.5, PVT[0] + 1.5, -R_ROD_ARM - 1.5, 0, Z_ARM0, Z_ARM1, M_MECH, parent=bell)
cyl("ArmRodPin", PVT[0], -R_ROD_ARM, Z_ARM1, Z_ROD + 0.6, 1.0, M_MECH, parent=bell)

# ---- кривошип на моторе ----
crank = empty("Crank", MX, MY, 0)
cyl("CrankDisc", MX, MY, 14.0, 15.5, 13.0, M_MECH, parent=crank)
cyl("CrankPin", MX - R_CRANK, MY, 15.5, Z_ROD + 0.6, 1.0, M_MECH, parent=crank)

# ---- спица ----
bpy.ops.mesh.primitive_cylinder_add(radius=1.1, depth=1.0, location=(0, 0, Z_ROD))
rod = bpy.context.object
rod.name = "Spica"
rod.data.materials.append(M_ROD)
rod.rotation_mode = 'XYZ'

# ---- кинематика и запекание ----
P0 = mathutils.Vector((PVT[0], PVT[1]))
L_ROD = (mathutils.Vector((PVT[0], -R_ROD_ARM)) -
         mathutils.Vector((MX - R_CRANK, MY))).length


def rod_pin(beta):
    return mathutils.Vector((PVT[0] + R_ROD_ARM * math.sin(beta),
                             -R_ROD_ARM * math.cos(beta)))


def crank_pin(theta):
    return mathutils.Vector((MX + R_CRANK * math.cos(theta),
                             MY + R_CRANK * math.sin(theta)))


def solve_beta(theta):
    pc = crank_pin(theta)
    lo, hi = math.radians(-75), math.radians(75)
    f = lambda b: (rod_pin(b) - pc).length - L_ROD
    flo = f(lo)
    for _ in range(60):
        mid = (lo + hi) / 2
        if (f(mid) > 0) == (flo > 0):
            lo, flo = mid, f(mid)
        else:
            hi = mid
    return (lo + hi) / 2


for fr in range(1, 121):
    theta = math.pi + 2 * math.pi * (fr - 1) / 120.0
    beta = solve_beta(theta)
    crank.rotation_euler = (0, 0, theta - math.pi)
    crank.keyframe_insert("rotation_euler", frame=fr)
    bell.rotation_euler = (0, 0, beta)
    bell.keyframe_insert("rotation_euler", frame=fr)
    cy = R_CART_X * math.tan(beta)
    cart.location = (35, cy, 9.5)
    cart.keyframe_insert("location", frame=fr)
    pb, pc = rod_pin(beta), crank_pin(theta)
    mid = (pb + pc) / 2
    rod.location = (mid.x, mid.y, Z_ROD)
    rod.scale = (1, 1, (pc - pb).length)
    rod.rotation_euler = (0, math.pi / 2, math.atan2(pc.y - pb.y, pc.x - pb.x))
    rod.keyframe_insert("location", frame=fr)
    rod.keyframe_insert("scale", frame=fr)
    rod.keyframe_insert("rotation_euler", frame=fr)

# ================= СТАНЦИЯ 2: та же качалка, но СЕРЬГА вместо кулисы ======
# Качалка: ось (63,0), кулисного плеча нет — плечо R22 с пальцем на конце.
# Серьга L9 (звено с 2 шарнирами) соединяет палец плеча с пальцем тележки
# на дорожке x=85. Скольжения нет вообще — только вращение в шарнирах.
P2 = (61.0, 0.0)
R_ARM2 = 28.0
L_SER = 8.0
LANE2 = 85.0
M2X, M2Y = 210.0, 0.0
R_CRANK2 = 8.5
BETA_MIN = -math.radians(54)                 # плечо при тележке на -20 (кривошип в θ=π)

box("GrooveMark2", 77.9, 92.1, -22, 22, 3.45, 3.55, M_CART)
cyl("Motor2Well", M2X, M2Y, 3.5, 5.0, 18.0, M_BASE)
cyl("Gear2", M2X, M2Y, 5.0, 8.0, 3.0, M_GOLD)
cyl("Gear2Shaft", M2X, M2Y, 8.0, 14.0, 2.2, M_GOLD)

cart2 = box("Cart2", 78, 92, -11, 11, 6, 13, M_CART)
cyl("Cart2Pin", LANE2, 0, 13, 17.2, 1.0, M_MECH, parent=cart2)

bell2 = empty("BellCrank2", P2[0], P2[1], 0)
cyl("Pivot2Post", P2[0], P2[1], 3.5, Z_ARM1, 1.8, M_MECH, parent=bell2)
# плечо к тележке: БЕЗ прорези, на конце палец вверх (шарнир серьги)
box("Arm2", P2[0] - 2, P2[0] + R_ARM2 + 1.5, -1.8, 1.8, Z_ARM0, Z_ARM1, M_MECH, parent=bell2)
cyl("Arm2Pin", P2[0] + R_ARM2, 0, Z_ARM1, Z_ROD + 0.6, 1.0, M_MECH, parent=bell2)
# плечо спицы вдоль -Y
box("Arm2Rod", P2[0] - 1.5, P2[0] + 1.5, -R_ROD_ARM - 1.5, 0, Z_ARM0, Z_ARM1, M_MECH, parent=bell2)
cyl("Arm2RodPin", P2[0], -R_ROD_ARM, Z_ARM1, Z_ROD + 0.6, 1.0, M_MECH, parent=bell2)

crank2 = empty("Crank2", M2X, M2Y, 0)
cyl("Crank2Disc", M2X, M2Y, 14.0, 15.5, 13.0, M_MECH, parent=crank2)
cyl("Crank2Pin", M2X - R_CRANK2, M2Y, 15.5, Z_ROD + 0.6, 1.0, M_MECH, parent=crank2)

bpy.ops.mesh.primitive_cylinder_add(radius=1.1, depth=1.0, location=(0, 0, Z_ROD))
rod2 = bpy.context.object
rod2.name = "Spica2"
rod2.data.materials.append(M_ROD)
# серьга — зелёная, чтобы бросалась в глаза
M_SER = mat("serga", (0.2, 0.7, 0.3, 1))
bpy.ops.mesh.primitive_cylinder_add(radius=1.0, depth=1.0, location=(0, 0, Z_ROD))
serga = bpy.context.object
serga.name = "Serga"
serga.data.materials.append(M_SER)


def rod_pin2(beta):
    return mathutils.Vector((P2[0] + R_ROD_ARM * math.sin(beta),
                             -R_ROD_ARM * math.cos(beta)))


def crank_pin2(theta):
    return mathutils.Vector((M2X + R_CRANK2 * math.cos(theta),
                             M2Y + R_CRANK2 * math.sin(theta)))


pb0 = rod_pin2(BETA_MIN)
L_ROD2 = (pb0 - crank_pin2(math.pi)).length


def solve_beta2(theta):
    pc = crank_pin2(theta)
    lo, hi = BETA_MIN - math.radians(8), BETA_MIN + math.radians(95)
    f = lambda b: (rod_pin2(b) - pc).length - L_ROD2
    flo = f(lo)
    for _ in range(60):
        m_ = (lo + hi) / 2
        if (f(m_) > 0) == (flo > 0):
            lo, flo = m_, f(m_)
        else:
            hi = m_
    return (lo + hi) / 2


for fr in range(1, 121):
    theta = math.pi + 2 * math.pi * (fr - 1) / 120.0
    beta = solve_beta2(theta)
    crank2.rotation_euler = (0, 0, theta - math.pi)
    crank2.keyframe_insert("rotation_euler", frame=fr)
    bell2.rotation_euler = (0, 0, beta)
    bell2.keyframe_insert("rotation_euler", frame=fr)
    # палец плеча (плечо построено вдоль +X, пустышка повёрнута на beta)
    tip = mathutils.Vector((P2[0] + R_ARM2 * math.cos(beta),
                            R_ARM2 * math.sin(beta)))
    dx = LANE2 - tip.x
    arg = max(L_SER * L_SER - dx * dx, 0.01)
    yc = tip.y + math.sqrt(arg)
    cart2.location = (LANE2, yc, 9.5)
    cart2.keyframe_insert("location", frame=fr)
    # серьга между пальцем плеча и пальцем тележки
    cpin = mathutils.Vector((LANE2, yc))
    mid = (tip + cpin) / 2
    serga.location = (mid.x, mid.y, Z_ROD)
    serga.scale = (1, 1, max((cpin - tip).length, 0.5))
    serga.rotation_euler = (0, math.pi / 2, math.atan2(cpin.y - tip.y, cpin.x - tip.x))
    serga.keyframe_insert("location", frame=fr)
    serga.keyframe_insert("scale", frame=fr)
    serga.keyframe_insert("rotation_euler", frame=fr)
    # спица 2
    pb, pc = rod_pin2(beta), crank_pin2(theta)
    mid = (pb + pc) / 2
    rod2.location = (mid.x, mid.y, Z_ROD)
    rod2.scale = (1, 1, (pc - pb).length)
    rod2.rotation_euler = (0, math.pi / 2, math.atan2(pc.y - pb.y, pc.x - pb.x))
    rod2.keyframe_insert("location", frame=fr)
    rod2.keyframe_insert("scale", frame=fr)
    rod2.keyframe_insert("rotation_euler", frame=fr)

# ---- свет, мир, камера ----
bpy.ops.object.light_add(type='SUN', location=(80, -60, 120))
bpy.context.object.data.energy = 4
bpy.context.object.rotation_euler = (math.radians(35), math.radians(15), 0)
w = bpy.data.worlds.new("W")
w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.9, 0.9, 0.9, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 0.7
sc.world = w
bpy.ops.object.camera_add(location=(120, -130, 110))
cam = bpy.context.object
direction = mathutils.Vector((85, -5, 8)) - cam.location
cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 45
sc.camera = cam
sc.frame_set(1)

sc.render.resolution_x, sc.render.resolution_y = 1400, 900
sc.render.filepath = r"C:\App\gitar\2-0\manual\img\_spica_concept.png"
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=r"C:\App\gitar\2-0\Спица_концепт.blend")
print("SPICA OK")
