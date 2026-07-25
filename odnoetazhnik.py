# -*- coding: utf-8 -*-
"""ОДНОЭТАЖНИК (v15-концепт): все 4 тележки на одном этаже.
Запуск: blender -b -P odnoetazhnik.py
- гриф = 3 детали: ПОЛ (вся механика), проставка, полка (показаны срезом у головы);
- каналы на своих Y (17/18.5/20/21.5), пересечения канавок — П-тоннели вкладышей;
- 8 одинаковых роликов, плавники все = типоразмер этажа 1;
- дека: 4 ОДИНАКОВЫХ диска Ø27 на одной высоте, БЕЗ подставок моторов;
- направляющие сдвинуты к центру: y = 13.25/13.25/14.0/17.75 (зазоры >=4.75).
"""
import bpy, math, mathutils

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene

S = [35.0, 51.0, 67.0, 83.0]
CHY = [17.0, 18.5, 20.0, 21.5]
MOT = [160.0, 206.0, 252.0, 298.0]
GX = [m - 29.0 for m in MOT]
GY = [13.25, 13.25, 14.0, 17.75]     # сдвинуты от chy-3.75 ради зазоров


def mat(name, rgba):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = rgba
    return m

M_BASE = mat("base", (0.62, 0.62, 0.62, 1))
M_DARK = mat("dark", (0.35, 0.35, 0.35, 1))
M_CART = mat("cart", (0.8, 0.8, 0.82, 1))
M_GOLD = mat("gold", (0.75, 0.6, 0.25, 1))
M_RED = mat("red", (0.8, 0.15, 0.1, 1))
M_DISK = mat("disk", (0.45, 0.55, 0.75, 1))


def box(name, x0, x1, y0, y1, z0, z1, m):
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


def cable(name, pts):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = 0.25
    sp = cu.splines.new('POLY')
    sp.points.add(len(pts) - 1)
    for p, (x, y, z) in zip(sp.points, pts):
        p.co = (x, y, z, 1)
    ob = bpy.data.objects.new(name, cu)
    ob.data.materials.append(M_RED)
    sc.collection.objects.link(ob)
    return ob


# ================= ГРИФ: пол с механикой всех 4 станций =================
box("Floor", 0, 125, -25, 25, 0, 3.5, M_BASE)
for k in range(4):
    s, chy = S[k], CHY[k]
    la, lb = s - 4, s + 4
    pax, pay = la + 2.5, chy - 2.5
    pbx, pby = lb + 2.5, -(chy - 2.5)
    # канавки (тёмные врезки сверху)
    box("GrA%d" % (k + 1), la - 3, la + 3, -25, 21, 3.4, 3.52, M_DARK)
    box("GrB%d" % (k + 1), lb - 3, lb + 3, -21, 25, 3.4, 3.52, M_DARK)
    # каналы к деке
    box("ChA%d" % (k + 1), pax, 125, chy - 1.75, chy + 1.75, 3.4, 3.5, M_DARK)
    box("ChB%d" % (k + 1), pbx, 125, -chy - 1.75, -chy + 1.75, 3.4, 3.5, M_DARK)
    # угловые ролики (8 одинаковых, одна высота)
    cyl("CornA%d" % (k + 1), pax, pay, 0.4, 3.3, 3.0, M_GOLD)
    cyl("CornB%d" % (k + 1), pbx, pby, 0.4, 3.3, 3.0, M_GOLD)
    # тележка: стакан + 2 ноги-плавника (ВСЕ одинаковые = типоразмер этажа 1)
    box("Cart%d" % (k + 1), s - 7.1, s + 7.1, -11, 11, 16.2, 23.2, M_CART)
    box("FinA%d" % (k + 1), la - 1.25, la + 1.25, -13.2, -10.9, 1.8, 16.4, M_CART)
    box("FinB%d" % (k + 1), lb - 1.25, lb + 1.25, 10.9, 13.2, 1.8, 16.4, M_CART)
    # нити: канал -> ролик (обход со стороны края) -> дорожка -> пятка
    r = 2.55
    z0, z1, zh = 0.75, 2.1, 3.2
    ptsA = [(122, chy, z0), (pax, chy, z0)]
    for i in range(11):
        a = math.radians(90 + 9 * i)
        t = i / 10.0
        ptsA.append((pax + r * math.cos(a), pay + r * math.sin(a),
                     z0 + (z1 - z0) * t))
    ptsA += [(la, -9.5, z1), (la, -10.5, zh), (la, -12.9, zh)]
    cable("cabA%d" % (k + 1), ptsA)
    ptsB = [(122, -chy, z0), (pbx, -chy, z0)]
    for i in range(11):
        a = math.radians(270 - 9 * i)
        t = i / 10.0
        ptsB.append((pbx + r * math.cos(a), pby + r * math.sin(a),
                     z0 + (z1 - z0) * t))
    ptsB += [(lb, 9.5, z1), (lb, 10.5, zh), (lb, 12.9, zh)]
    cable("cabB%d" % (k + 1), ptsB)

# срез стопки у головы грифа: проставка + полка (остальное открыто для обзора)
box("RiserCut", 0, 16, -25, 25, 3.5, 14, M_BASE)
box("ShelfCut", 0, 16, -25, 25, 14, 16, M_BASE)

# ================= ДЕКА: 4 одинаковых диска, без подставок =================
box("Deck", 125, 320, -30, 30, -1, 0, M_BASE)
for k in range(4):
    mx = MOT[k]
    cyl("Motor%d" % (k + 1), mx, 0, -1, 0.5, 18.0, M_DARK)
    d = cyl("Disk%d" % (k + 1), mx, 0, 0.5, 5.5, 13.5, M_DISK)
    cyl("DiskCap%d" % (k + 1), mx, 0, 5.5, 6.3, 9.0, M_DISK)
    # направляющие (одна высота, y сдвинуты)
    for sg in (1, -1):
        cyl("G%d%s" % (k + 1, 'P' if sg > 0 else 'M'),
            GX[k], sg * GY[k], 0, 2.8, 3.5, M_GOLD)
    # нити по деке: диск -> направляющий -> кромка грифа (обе стороны)
    for sg in (1, -1):
        chy = CHY[k]
        gy = sg * GY[k]
        cable("deck%d%s" % (k + 1, 'P' if sg > 0 else 'M'),
              [(mx, sg * 12.0, 0.75),
               (GX[k] + 3.0, gy + sg * 3.75, 0.75),
               (GX[k] - 3.0, gy + sg * 3.75, 0.75),
               (125.5, sg * chy, 0.75)])

# ================= свет, камера =================
bpy.ops.object.light_add(type='SUN', location=(80, -60, 120))
bpy.context.object.data.energy = 4
bpy.context.object.rotation_euler = (math.radians(35), math.radians(15), 0)
w = bpy.data.worlds.new("W")
w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.9, 0.9, 0.9, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 0.7
sc.world = w
bpy.ops.object.camera_add(location=(60, -150, 130))
cam = bpy.context.object
direction = mathutils.Vector((120, 0, 2)) - cam.location
cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 40
sc.camera = cam

sc.render.resolution_x, sc.render.resolution_y = 1400, 900
sc.render.filepath = r"C:\App\gitar\2-0\manual\img\_odnoetazhnik.png"
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=r"C:\App\gitar\2-0\Одноэтажник.blend")
print("ODNO OK")
