# -*- coding: utf-8 -*-
"""ДЕМО v5 — bell crank СТРОГО по фото юзера.
Запуск: blender -b -P palka_demo.py
- у южного КРАЯ вперёд-назад ходит ПАЛКА-спица (её гоняет кривошип мотора);
- палка приколота к УГЛУ-1 треугольника;
- треугольник (с полукруглым основанием) крутится вокруг ЦЕНТРАЛЬНОГО угла
  (Pivot, неподвижная ось);
- УГОЛ-3 (длинное плечо) толкает тележку ПЕРПЕНДИКУЛЯРНО (палец в прорези);
- ход тележки +-20 (40 мм) при качании треугольника ~+-28°.
"""
import bpy, math, mathutils

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.fps = 24
sc.frame_start, sc.frame_end = 1, 120

XC = 17.0                 # дорожка тележки (запад)
PX, PY = 55.0, 0.0        # ось треугольника (центральный угол)
R1 = 18.0                 # плечо к углу-1 (вниз, к палке у края)
LA = PX - XC              # плечо к тележке = 38 (запад)
CX, CY = 95.0, -17.0      # кривошип у мотора (восток)
RC = 8.4                  # радиус кривошипа
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
    verts, n = [], 30
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


# ---- пол + борта ----
box("Slab", 0, 112, -25, 25, 0, 1.0, M_BASE)
box("WallN", 0, 112, 23.2, 25, 1.0, 4.5, M_BASE)
box("WallS", 0, 112, -25, -23.2, 1.0, 4.5, M_BASE)

# ---- тележка + палец ----
cart = box("Cart", XC - 8, XC + 8, -7, 7, 5.0, 12.0, M_CART)
cyl("CartPin", XC, 0, 1.4, 5.2, 1.1, M_CART, parent=cart)

# ---- ТРЕУГОЛЬНИК на оси (центральный угол = Pivot) ----
piv = bpy.data.objects.new("Pivot", None)
piv.location = (PX, PY, 0)
sc.collection.objects.link(piv)
# полукруглое основание между плечами (юго-запад)
sector("Base", R1, -180, -90, 1.3, 2.3, M_BLUE, piv)
# плечо к углу-1 (вниз)
box("Arm1", PX - 1.6, PX + 1.6, PY - R1 - 1.6, PY, 1.3, 2.3, M_BLUE, parent=piv)
cyl("Corner1", PX, PY - R1, 2.3, 3.6, 1.3, M_RED, parent=piv)      # шарнир палки
# плечо-3 к тележке (запад) с прорезью под палец
box("Arm3", PX - 30, PX + 2, PY - 1.6, PY + 1.6, 1.3, 2.3, M_BLUE, parent=piv)
box("Arm3RailN", PX - 45.5, PX - 30, PY + 1.6, PY + 4.2, 1.3, 2.3, M_BLUE, parent=piv)
box("Arm3RailS", PX - 45.5, PX - 30, PY - 4.2, PY - 1.6, 1.3, 2.3, M_BLUE, parent=piv)
box("Arm3Cap", PX - 47, PX - 45.5, PY - 4.2, PY + 4.2, 1.3, 2.3, M_BLUE, parent=piv)
cyl("AxisPost", PX, PY, 1.0, 3.4, 1.0, M_BASE)

# ---- кривошип мотора (восток) ----
crank = bpy.data.objects.new("Crank", None)
crank.location = (CX, CY, 0)
sc.collection.objects.link(crank)
cyl("CrankDisc", CX, CY, 1.3, 2.5, 10.0, M_GOLD, parent=crank)
cyl("CrankPin", CX - RC, CY, 2.5, 3.8, 1.0, M_RED, parent=crank)

# ---- ПАЛКА у края (спица): от кривошипа к углу-1, ходит вперёд-назад ----
bpy.ops.mesh.primitive_cube_add()
spica = bpy.context.object
spica.name = "Palka"
spica.data.materials.append(M_RED)

# ---- кинематика ----
def corner1(phi):
    return mathutils.Vector((PX + R1 * math.sin(phi), PY - R1 * math.cos(phi)))


def crank_pin(th):
    return mathutils.Vector((CX + RC * math.cos(th), CY + RC * math.sin(th)))


L_SP = (crank_pin(math.pi) - corner1(0.0)).length


def solve_phi(th):
    pc = crank_pin(th)
    lo, hi = math.radians(-42), math.radians(42)
    f = lambda p: (corner1(p) - pc).length - L_SP
    flo = f(lo)
    for _ in range(60):
        mid = (lo + hi) / 2
        if (f(mid) > 0) == (flo > 0):
            lo, flo = mid, f(mid)
        else:
            hi = mid
    return (lo + hi) / 2


for fr in range(1, 121):
    th = math.pi + 2 * math.pi * (fr - 1) / 120.0
    phi = solve_phi(th)
    piv.rotation_euler = (0, 0, phi)
    piv.keyframe_insert("rotation_euler", frame=fr)
    cy_ = PY - LA * math.tan(phi)               # палец в прорези плеча-3
    cart.location = (XC, cy_, 8.5)
    cart.keyframe_insert("location", frame=fr)
    crank.rotation_euler = (0, 0, th - math.pi)
    crank.keyframe_insert("rotation_euler", frame=fr)
    c1, pc = corner1(phi), crank_pin(th)
    mid = (c1 + pc) / 2
    spica.location = (mid.x, mid.y, ZS + 1.2)
    spica.scale = ((pc - c1).length / 2 + 1.5, 1.0, 0.5)
    spica.rotation_euler = (0, 0, math.atan2(pc.y - c1.y, pc.x - c1.x))
    spica.keyframe_insert("location", frame=fr)
    spica.keyframe_insert("scale", frame=fr)
    spica.keyframe_insert("rotation_euler", frame=fr)

# ---- свет, камера ----
bpy.ops.object.light_add(type='SUN', location=(40, -40, 90))
bpy.context.object.data.energy = 4
bpy.context.object.rotation_euler = (math.radians(30), math.radians(12), 0)
w = bpy.data.worlds.new("W")
w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.9, 0.9, 0.9, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 0.7
sc.world = w
bpy.ops.object.camera_add(location=(35, -62, 70))
cam = bpy.context.object
direction = mathutils.Vector((55, -2, 2)) - cam.location
cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 42
sc.camera = cam
sc.frame_set(12)

sc.render.resolution_x, sc.render.resolution_y = 1400, 900
sc.render.filepath = r"C:\App\gitar\2-0\manual\img\_palka_demo5.png"
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=r"C:\App\gitar\2-0\Палка_демо.blend")
print("PALKA5 OK")
