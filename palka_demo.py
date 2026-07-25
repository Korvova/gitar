# -*- coding: utf-8 -*-
"""ДЕМО v7 — bell crank как на фото, КОМПАКТНО, без привязки к размерам.
Запуск: blender -b -P palka_demo.py
- спица вдоль края (кривошип) -> шарнир в углу-1 (низ треугольника);
- ось в центральном углу; сектор-основание между плечами;
- угол-3 (восток) через шарнир-серьгу толкает тележку ВБОК; тележка рядом.
"""
import bpy, math, mathutils

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.fps = 24
sc.frame_start, sc.frame_end = 1, 120

PX, PY = 45.0, -6.0       # ось (центральный угол)
R1 = 11.0                 # плечо вниз, к спице у края
R3 = 20.0                 # плечо на восток, к шарниру тележки
LL = 8.0                  # серьга от угла-3 к пальцу тележки
XCART = PX + R3           # тележка прямо над углом-3
CX, CY = 92.0, PY - R1    # кривошип
RC = 4.6                  # радиус кривошипа (кач +-25°)
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
M_GREEN = mat("green", (0.2, 0.65, 0.3, 1))


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


# ---- основание ----
box("Slab", 0, 108, -26, 26, 0, 1.0, M_BASE)

# ---- тележка (ездит вбок, по Y) + палец вниз ----
cart = box("Cart", XCART - 7, XCART + 7, -5, 5, 5.0, 11.0, M_CART)
cyl("CartPin", XCART, 0, 2.4, 5.2, 1.0, M_RED, parent=cart)

# ---- ТРЕУГОЛЬНИК: ось в центральном углу ----
piv = bpy.data.objects.new("Pivot", None)
piv.location = (PX, PY, 0)
sc.collection.objects.link(piv)
sector("Base", 11.0, -90, 0, 1.3, 2.3, M_BLUE, piv)                # основание-дуга
box("Arm1", PX - 1.6, PX + 1.6, PY - R1 - 1.6, PY, 1.3, 2.3, M_BLUE, parent=piv)
cyl("Corner1", PX, PY - R1, 2.3, 3.6, 1.2, M_RED, parent=piv)      # шарнир спицы
box("Arm3", PX, PX + R3 + 1.6, PY - 1.6, PY + 1.6, 1.3, 2.3, M_BLUE, parent=piv)
cyl("Corner3", PX + R3, PY, 2.3, 3.6, 1.2, M_RED, parent=piv)      # шарнир серьги
cyl("AxisPost", PX, PY, 1.0, 3.4, 1.0, M_BASE)

# ---- кривошип ----
crank = bpy.data.objects.new("Crank", None)
crank.location = (CX, CY, 0)
sc.collection.objects.link(crank)
cyl("CrankDisc", CX, CY, 1.3, 2.5, 8.0, M_GOLD, parent=crank)
cyl("CrankPin", CX - RC, CY, 2.5, 3.8, 1.0, M_RED, parent=crank)

# ---- спица и серьга (динамические) ----
bpy.ops.mesh.primitive_cube_add()
spica = bpy.context.object
spica.name = "Palka"
spica.data.materials.append(M_RED)
bpy.ops.mesh.primitive_cube_add()
link = bpy.context.object
link.name = "Serga"
link.data.materials.append(M_GREEN)

# ---- кинематика ----
def corner1(phi):
    return mathutils.Vector((PX + R1 * math.sin(phi), PY - R1 * math.cos(phi)))


def corner3(phi):
    return mathutils.Vector((PX + R3 * math.cos(phi), PY + R3 * math.sin(phi)))


def crank_pin(th):
    return mathutils.Vector((CX + RC * math.cos(th), CY + RC * math.sin(th)))


L_SP = (crank_pin(math.pi) - corner1(0.0)).length


def solve_phi(th):
    pc = crank_pin(th)
    lo, hi = math.radians(-30), math.radians(30)
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
    c3 = corner3(phi)
    dxx = XCART - c3.x
    cy_ = c3.y + math.sqrt(max(LL * LL - dxx * dxx, 0.25))
    cart.location = (XCART, cy_, 8.0)
    cart.keyframe_insert("location", frame=fr)
    pin = mathutils.Vector((XCART, cy_))
    mid = (c3 + pin) / 2
    link.location = (mid.x, mid.y, ZS + 1.4)
    link.scale = ((pin - c3).length / 2 + 1.1, 0.8, 0.4)
    link.rotation_euler = (0, 0, math.atan2(pin.y - c3.y, pin.x - c3.x))
    link.keyframe_insert("location", frame=fr)
    link.keyframe_insert("scale", frame=fr)
    link.keyframe_insert("rotation_euler", frame=fr)
    crank.rotation_euler = (0, 0, th - math.pi)
    crank.keyframe_insert("rotation_euler", frame=fr)
    c1, pc = corner1(phi), crank_pin(th)
    mid = (c1 + pc) / 2
    spica.location = (mid.x, mid.y, ZS + 1.2)
    spica.scale = ((pc - c1).length / 2 + 1.4, 1.0, 0.5)
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
bpy.ops.object.camera_add(location=(48, -52, 62))
cam = bpy.context.object
direction = mathutils.Vector((55, -2, 2)) - cam.location
cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 45
sc.camera = cam
sc.frame_set(16)

sc.render.resolution_x, sc.render.resolution_y = 1400, 900
sc.render.filepath = r"C:\App\gitar\2-0\manual\img\_palka_demo7.png"
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=r"C:\App\gitar\2-0\Палка_демо.blend")
print("PALKA7 OK")
