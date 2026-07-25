# -*- coding: utf-8 -*-
"""Концепт «спица + качалка» (авиационная тяга) — ОТДЕЛЬНЫЙ файл, канал 1.
Запуск: blender -b -P spica_concept.py
Схема: кривошип на шестерне мотора -> спица вдоль коридора -> качалка с
кулисой на грифе -> палец тележки. Ход тележки +-20 при кривошипе R9.
"""
import bpy, math

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene


def mat(name, rgba):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = rgba
    return m

M_BASE = mat("base", (0.6, 0.6, 0.6, 1))
M_CART = mat("cart", (0.75, 0.75, 0.78, 1))
M_MECH = mat("mech", (0.25, 0.45, 0.8, 1))    # качалка+кривошип — синие
M_ROD = mat("rod", (0.85, 0.2, 0.15, 1))      # спица — красная
M_GOLD = mat("gold", (0.75, 0.6, 0.25, 1))


def add(obj, m):
    sc.collection.objects.link(obj)
    obj.data.materials.append(m)
    return obj


def box(name, x0, x1, y0, y1, z0, z1, m):
    me = bpy.data.meshes.new(name)
    bpy.ops.mesh.primitive_cube_add()
    ob = bpy.context.object
    ob.name = name
    ob.scale = ((x1 - x0) / 2, (y1 - y0) / 2, (z1 - z0) / 2)
    ob.location = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    ob.data.materials.append(m)
    return ob


def cyl(name, x, y, z0, z1, r, m):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=z1 - z0,
                                        location=(x, y, (z0 + z1) / 2))
    ob = bpy.context.object
    ob.name = name
    ob.data.materials.append(m)
    return ob


# ---- основание: кусок грифа (этаж 1) + дека одним настилом ----
box("Base", 0, 220, -25, 25, 0, 3.5, M_BASE)
# намёк на канавку тележки 1 (дорожки лап S+-4)
box("GrooveMark", 27.9, 42.1, -25, 21, 3.45, 3.55, M_CART)

# ---- тележка (упрощённый стакан) + палец вниз ----
box("Cart", 28, 42, -11, 11, 6, 13, M_CART)
cyl("CartPin", 35, 0, 3.8, 6.0, 1.0, M_MECH)

# ---- качалка: стойка + кулисное плечо (низ) + плечо спицы (верх) ----
PVX, PVY = 35.0, -21.0
cyl("Pivot", PVX, PVY, 3.5, 11.5, 1.8, M_MECH)
# кулисное плечо к тележке: сплошная часть, два рельса (кулиса), торец
box("ArmSolid", 33.2, 36.8, PVY - 2.0, -5, 4.0, 5.5, M_MECH)
box("ArmRailW", 33.2, 33.9, -5, 10, 4.0, 5.5, M_MECH)
box("ArmRailE", 36.1, 36.8, -5, 10, 4.0, 5.5, M_MECH)
box("ArmCap", 33.2, 36.8, 10, 11.4, 4.0, 5.5, M_MECH)
# плечо спицы (верхний этаж качалки) + палец вверх
box("ArmRod", PVX, 47.5, PVY - 1.0, PVY + 1.0, 9.7, 11.2, M_MECH)
cyl("ArmRodPin", 47.0, PVY, 11.2, 12.4, 1.0, M_MECH)

# ---- мотор: шестерня + кривошип-диск с пальцем ----
MX, MY = 160.0, 0.0
cyl("MotorTop", MX, MY, 3.5, 5.0, 18.0, M_BASE)      # фланец в колодце
cyl("Gear", MX, MY, 5.0, 7.5, 3.0, M_GOLD)
cyl("CrankDisc", MX, MY, 7.5, 9.0, 10.5, M_MECH)
# палец кривошипа: на радиусе 9 в сторону качалки
dx, dy = 47.0 - MX, PVY - MY
L = math.hypot(dx, dy)
px, py = MX + 9 * dx / L, MY + 9 * dy / L
cyl("CrankPin", px, py, 9.0, 12.4, 1.0, M_MECH)

# ---- спица: от пальца кривошипа к пальцу качалки ----
rx, ry, rz = (47.0 + px) / 2, (PVY + py) / 2, 11.8
rlen = math.hypot(px - 47.0, py - PVY)
bpy.ops.mesh.primitive_cylinder_add(radius=1.1, depth=rlen, location=(rx, ry, rz))
rod = bpy.context.object
rod.name = "Spica"
rod.rotation_euler = (0, math.pi / 2, math.atan2(py - PVY, px - 47.0))
rod.data.materials.append(M_ROD)
# наконечники спицы
for ex, ey in ((47.0, PVY), (px, py)):
    cyl("RodEnd", ex, ey, 11.3, 12.3, 1.6, M_ROD)

# ---- свет и камера ----
bpy.ops.object.light_add(type='SUN', location=(80, -60, 120))
bpy.context.object.data.energy = 4
bpy.context.object.rotation_euler = (math.radians(35), math.radians(15), 0)
w = bpy.data.worlds.new("W")
w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.9, 0.9, 0.9, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 0.7
sc.world = w
bpy.ops.object.camera_add(location=(150, -150, 120))
cam = bpy.context.object
import mathutils
direction = mathutils.Vector((95, -8, 5)) - cam.location
cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 45
sc.camera = cam

sc.render.resolution_x, sc.render.resolution_y = 1400, 900
sc.render.filepath = r"C:\App\gitar\2-0\manual\img\_spica_concept.png"
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=r"C:\App\gitar\2-0\Спица_концепт.blend")
print("SPICA OK")
