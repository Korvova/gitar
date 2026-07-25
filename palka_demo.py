# -*- coding: utf-8 -*-
"""ДЕМО v9 — ДВА толкателя от одного вала (хитрость юзера).
Запуск: blender -b -P palka_demo.py
- два одинаковых механизма (спица -> треугольник -> плечо) рядом,
  их наконечники сидят в ОКНЕ тележки и давят в противоположные стенки:
  один толкает вбок туда, другой — обратно;
- ходят в унисон (фазы согласованы на валу), тележка зажата без зазора,
  наружу за тележку ничего не торчит;
- обе спицы — к одному кривошипу на валу мотора.
"""
import bpy, math, mathutils

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.fps = 24
sc.frame_start, sc.frame_end = 1, 120

RA = 28.0                 # плечо
R1 = 10.0                 # плечо к спице
DY = 2.8                  # смещение осей пары от центра (полузазор окна)
P1 = mathutils.Vector((46.0, +DY))     # ось толкателя, давящего на СЕВЕР
P2 = mathutils.Vector((46.0, -DY))     # ось толкателя, давящего на ЮГ
XT = 46.0 + RA            # линия наконечников (окно тележки)
CX, CY = 100.0, -10.0     # кривошип на валу
RC = 4.4
ZS = 1.8


def mat(name, rgba):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = rgba
    return m

M_BASE = mat("base", (0.62, 0.62, 0.62, 1))
M_CART = mat("cart", (0.8, 0.8, 0.82, 1))
M_RED = mat("red", (0.8, 0.15, 0.1, 1))
M_BLUE = mat("blue", (0.2, 0.3, 0.75, 1))
M_CYAN = mat("cyan", (0.2, 0.6, 0.8, 1))
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


def sector(name, r, a0_deg, a1_deg, z0, z1, m, parent):
    verts, n = [], 24
    pts2 = [(0.0, 0.0)]
    for i in range(n + 1):
        a = math.radians(a0_deg + (a1_deg - a0_deg) * i / n)
        pts2.append((r * math.cos(a), r * math.sin(a)))
    for px, py in pts2:
        verts.append((px, py, z0))
    for px, py in pts2:
        verts.append((px, py, z1))
    m_ = len(pts2)
    faces = []
    for i in range(1, m_ - 1):
        faces.append([0, i + 1, i])
        faces.append([m_, m_ + i, m_ + i + 1])
    for i in range(m_):
        j = (i + 1) % m_
        faces.append([i, j, m_ + j, m_ + i])
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    ob = bpy.data.objects.new(name, me)
    ob.data.materials.append(m)
    sc.collection.objects.link(ob)
    ob.parent = parent
    ob.location = (0, 0, 0)
    return ob


# ---- основание ----
box("Slab", 0, 116, -26, 26, 0, 1.0, M_BASE)

# ---- два толкателя (одинаковые, рядом) ----
pivots = []
for idx, (P, mcol) in enumerate(((P1, M_BLUE), (P2, M_CYAN))):
    zlo = 2.45 - 1.15 * idx                    # пара стопкой: синий выше, голубой ниже
    zhi = zlo + 1.0
    piv = bpy.data.objects.new("Pivot%d" % (idx + 1), None)
    piv.location = (P.x, P.y, 0)
    sc.collection.objects.link(piv)
    sector("Base%d" % (idx + 1), 8.0, -90, 0, zlo, zhi, mcol, piv)
    box("Arm1_%d" % (idx + 1), P.x - 1.5, P.x + 1.5, P.y - R1 - 1.5, P.y,
        zlo, zhi, mcol, parent=piv)
    cyl("C1_%d" % (idx + 1), P.x, P.y - R1, zhi, zhi + 1.1, 1.1, M_RED, parent=piv)
    box("ArmUp%d" % (idx + 1), P.x, P.x + RA + 1.2, P.y - 1.5, P.y + 1.5,
        zlo, zhi, mcol, parent=piv)
    cyl("Tip%d" % (idx + 1), P.x + RA, P.y, zhi, 5.0, 1.2, M_RED, parent=piv)
    cyl("Post%d" % (idx + 1), P.x, P.y, 1.0, zhi + 0.9, 0.9, M_BASE)
    pivots.append(piv)

# ---- тележка с ОКНОМ: стенки, в которые давят наконечники ----
cart = box("CartN", XT - 8, XT + 8, 4.0, 8.0, 2.4, 5.0, M_CART)     # северная стенка
box("CartS", XT - 8, XT + 8, -8.0, -4.0, 2.4, 5.0, M_CART, parent=cart)
box("CartTop", XT - 8, XT + 8, -8.0, 8.0, 5.0, 9.5, M_CART, parent=cart)

# ---- кривошип на валу ----
crank = bpy.data.objects.new("Crank", None)
crank.location = (CX, CY, 0)
sc.collection.objects.link(crank)
cyl("CrankDisc", CX, CY, 1.3, 2.5, 7.5, M_GOLD, parent=crank)
cyl("CrankPin", CX, CY - RC, 2.5, 3.8, 1.0, M_RED, parent=crank)

# ---- спицы (динамические) ----
spicas = []
for idx in (1, 2):
    bpy.ops.mesh.primitive_cube_add()
    sp_ = bpy.context.object
    sp_.name = "Palka%d" % idx
    sp_.data.materials.append(M_RED)
    spicas.append(sp_)

# ---- кинематика ----
def corner1(P, phi):
    return mathutils.Vector((P.x + R1 * math.sin(phi), P.y - R1 * math.cos(phi)))


def crank_pin(th):
    return mathutils.Vector((CX + RC * math.sin(th), CY - RC * math.cos(th)))


L1_SP = (crank_pin(0.0) - corner1(P1, 0.0)).length
L2_SP = (crank_pin(0.0) - corner1(P2, 0.0)).length


def solve_phi(th):
    pc = crank_pin(th)
    lo, hi = math.radians(-28), math.radians(28)
    f = lambda p: (corner1(P1, p) - pc).length - L1_SP
    flo = f(lo)
    for _ in range(60):
        mid = (lo + hi) / 2
        if (f(mid) > 0) == (flo > 0):
            lo, flo = mid, f(mid)
        else:
            hi = mid
    return (lo + hi) / 2


for fr in range(1, 121):
    th = 2 * math.pi * (fr - 1) / 120.0
    phi = solve_phi(th)
    for piv in pivots:
        piv.rotation_euler = (0, 0, phi)
        piv.keyframe_insert("rotation_euler", frame=fr)
    # наконечник 1 давит в северную стенку окна: тележка следует
    tip1y = P1.y + RA * math.sin(phi)
    cy_ = tip1y + 1.2 - 4.0                      # стенка окна на +4 от центра
    cart.location = (XT, 6.0 + cy_, 3.7)         # центр CartN при смещении cy_
    cart.keyframe_insert("location", frame=fr)
    crank.rotation_euler = (0, 0, th)
    crank.keyframe_insert("rotation_euler", frame=fr)
    pc = crank_pin(th)
    for idx, (P, sp_) in enumerate(zip((P1, P2), spicas)):
        c1 = corner1(P, phi)
        mid = (c1 + pc) / 2
        sp_.location = (mid.x, mid.y, 4.0 - 1.15 * idx)
        sp_.scale = ((pc - c1).length / 2 + 1.2, 0.8, 0.35)
        sp_.rotation_euler = (0, 0, math.atan2(pc.y - c1.y, pc.x - c1.x))
        sp_.keyframe_insert("location", frame=fr)
        sp_.keyframe_insert("scale", frame=fr)
        sp_.keyframe_insert("rotation_euler", frame=fr)

# ---- свет, камера ----
bpy.ops.object.light_add(type='SUN', location=(40, -40, 90))
bpy.context.object.data.energy = 4
bpy.context.object.rotation_euler = (math.radians(30), math.radians(12), 0)
w = bpy.data.worlds.new("W")
w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.9, 0.9, 0.9, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 0.7
sc.world = w
bpy.ops.object.camera_add(location=(50, -55, 65))
cam = bpy.context.object
direction = mathutils.Vector((60, 0, 2)) - cam.location
cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 45
sc.camera = cam
sc.frame_set(16)

sc.render.resolution_x, sc.render.resolution_y = 1400, 900
sc.render.filepath = r"C:\App\gitar\2-0\manual\img\_palka_demo9.png"
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=r"C:\App\gitar\2-0\Палка_демо.blend")
print("PALKA9 OK")
