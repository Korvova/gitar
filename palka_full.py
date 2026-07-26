# -*- coding: utf-8 -*-
"""ПОЛНЫЙ МАКЕТ: 4 станции на механизме юзера (палка-треугольник), слоями.
Запуск: blender -b -P palka_full.py
- 4 ОДИНАКОВЫХ механизма (плечо 85, серьга 3, кривошип R4.7), оси на деке;
- слои снизу вверх: станция 1..4 (веера не пересекают чужие пальцы);
- спицы у борта друг над другом, кривошипы на моторах на высоте слоя;
- ход каждой тележки ~40 мм, фазы кривошипов разные (едут независимо).
"""
import bpy, math, mathutils

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.fps = 24
sc.frame_start, sc.frame_end = 1, 240

S = [35.0, 51.0, 67.0, 83.0]          # тележки у ГОЛОВЫ грифа
MOT = [640.0, 690.0, 740.0, 790.0]    # кривошипы моторов в ДЕКЕ
RA, R1, LL, RC = 65.0, 21.2, 4.0, 6.5  # классика 52: серьга 4, плечо 65
PY = -1.6
YSP = -22.8                            # коридор спиц у борта (гриф +-26)


def mat(name, rgba):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = rgba
    return m

M_BASE = mat("base", (0.62, 0.62, 0.62, 1))
M_CART = mat("cart", (0.8, 0.8, 0.82, 1))
M_RED = mat("red", (0.8, 0.15, 0.1, 1))
M_GOLD = mat("gold", (0.75, 0.6, 0.25, 1))
COLS = [mat("c1", (0.20, 0.35, 0.80, 1)), mat("c2", (0.20, 0.60, 0.80, 1)),
        mat("c3", (0.20, 0.75, 0.45, 1)), mat("c4", (0.80, 0.55, 0.20, 1))]


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
    verts, n = [], 20
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


# ---- ГИТАРА-КЛАССИКА: гриф 600x52 + дека ----
box("Head", -70, 0, -30, 30, 0, 1.0, M_BASE)                       # головка
box("Neck", 0, 600, -26, 26, 0, 1.0, M_BASE)
box("BortN", 0, 600, 24.5, 26, 1.0, 10.0, M_BASE)
box("BortS", 0, 600, -26, -24.5, 1.0, 10.0, M_BASE)
box("Deck", 600, 1050, -185, 185, 0, 1.0, M_BASE)                  # корпус

stations = []
for k in range(4):
    zlo = 1.3 + 1.5 * k                      # слой станции (снизу вверх)
    zhi = zlo + 1.0
    xc = S[k]
    px = xc + RA                             # ось на деке/стыке
    col = COLS[k]
    piv = bpy.data.objects.new("Pivot%d" % (k + 1), None)
    piv.location = (px, PY, 0)
    sc.collection.objects.link(piv)
    sector("Sec%d" % (k + 1), 11.0, 180, 270, zlo, zhi, col, piv)
    box("A1_%d" % (k + 1), px - 1.6, px + 1.6, PY - R1 - 1.6, PY, zlo, zhi, col, parent=piv)
    cyl("C1_%d" % (k + 1), px, PY - R1, zhi, zhi + 0.9, 1.1, M_RED, parent=piv)
    box("Arm%d" % (k + 1), px - RA - 1.2, px, PY - 1.6, PY + 1.6, zlo, zhi, col, parent=piv)
    cyl("Tip%d" % (k + 1), px - RA, PY, zhi, zhi + 0.9, 1.1, M_RED, parent=piv)
    cyl("Post%d" % (k + 1), px, PY, 1.0, zhi + 0.8, 0.9, M_BASE)
    # тележка: стакан вверху, палец вниз до своего слоя
    cart = box("Cart%d" % (k + 1), xc - 7.1, xc + 7.1, -8, 8, 10.5, 17.5, M_CART)
    cyl("Pin%d" % (k + 1), xc, 0, zhi, 10.6, 1.0, M_RED, parent=cart)
    # кривошип на моторе, на высоте слоя
    crank = bpy.data.objects.new("Crank%d" % (k + 1), None)
    crank.location = (MOT[k], YSP, 0)
    sc.collection.objects.link(crank)
    cyl("CrD%d" % (k + 1), MOT[k], YSP, zlo, zhi, 7.0, M_GOLD, parent=crank)
    cyl("CrP%d" % (k + 1), MOT[k] - RC, YSP, zhi, zhi + 0.9, 1.0, M_RED, parent=crank)
    # спица и серьга
    bpy.ops.mesh.primitive_cube_add()
    sp_ = bpy.context.object
    sp_.name = "Sp%d" % (k + 1)
    sp_.data.materials.append(M_RED)
    bpy.ops.mesh.primitive_cube_add()
    lk = bpy.context.object
    lk.name = "Lk%d" % (k + 1)
    lk.data.materials.append(col)
    stations.append(dict(piv=piv, cart=cart, crank=crank, sp=sp_, lk=lk,
                         px=px, xc=xc, mot=MOT[k], z=(zlo + zhi) / 2, zhi=zhi))


def corner1(px, phi):
    return mathutils.Vector((px + R1 * math.sin(phi), PY - R1 * math.cos(phi)))


def tipf(px, phi):
    return mathutils.Vector((px - RA * math.cos(phi), PY - RA * math.sin(phi)))


def crank_pin(mx, th):
    return mathutils.Vector((mx - RC * math.cos(th), YSP + RC * math.sin(th)))


def solve_phi(px, mx, Lsp, th):
    pc = crank_pin(mx, th)
    lo, hi = math.radians(-16), math.radians(16)
    f = lambda p: (corner1(px, p) - pc).length - Lsp
    flo = f(lo)
    for _ in range(50):
        mid = (lo + hi) / 2
        if (f(mid) > 0) == (flo > 0):
            lo, flo = mid, f(mid)
        else:
            hi = mid
    return (lo + hi) / 2


for st in stations:
    st['L'] = (crank_pin(st['mot'], math.pi / 2) - corner1(st['px'], 0.0)).length

for fr in range(1, 241):
    for k, st in enumerate(stations):
        th = 2 * math.pi * (fr - 1) / 240.0 * (2 + 0.5 * k) + k * 1.3
        phi = solve_phi(st['px'], st['mot'], st['L'], th)
        st['piv'].rotation_euler = (0, 0, phi)
        st['piv'].keyframe_insert("rotation_euler", frame=fr)
        tp = tipf(st['px'], phi)
        dxx = st['xc'] - tp.x
        cy_ = tp.y + math.sqrt(max(LL * LL - dxx * dxx, 0.04))
        st['cart'].location = (st['xc'], cy_, 14.0)
        st['cart'].keyframe_insert("location", frame=fr)
        pin = mathutils.Vector((st['xc'], cy_))
        mid = (tp + pin) / 2
        st['lk'].location = (mid.x, mid.y, st['zhi'] + 0.45)
        st['lk'].scale = ((pin - tp).length / 2 + 0.9, 0.7, 0.35)
        st['lk'].rotation_euler = (0, 0, math.atan2(pin.y - tp.y, pin.x - tp.x))
        st['lk'].keyframe_insert("location", frame=fr)
        st['lk'].keyframe_insert("scale", frame=fr)
        st['lk'].keyframe_insert("rotation_euler", frame=fr)
        st['crank'].rotation_euler = (0, 0, th)
        st['crank'].keyframe_insert("rotation_euler", frame=fr)
        c1 = corner1(st['px'], phi)
        pc = crank_pin(st['mot'], th)
        mid = (c1 + pc) / 2
        st['sp'].location = (mid.x, mid.y, st['zhi'] + 0.45)
        st['sp'].scale = ((pc - c1).length / 2 + 1.2, 0.8, 0.35)
        st['sp'].rotation_euler = (0, 0, math.atan2(pc.y - c1.y, pc.x - c1.x))
        st['sp'].keyframe_insert("location", frame=fr)
        st['sp'].keyframe_insert("scale", frame=fr)
        st['sp'].keyframe_insert("rotation_euler", frame=fr)

# ---- свет, камера ----
bpy.ops.object.light_add(type='SUN', location=(80, -60, 130))
bpy.context.object.data.energy = 4
bpy.context.object.rotation_euler = (math.radians(30), math.radians(12), 0)
w = bpy.data.worlds.new("W")
w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.9, 0.9, 0.9, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 0.7
sc.world = w
bpy.ops.object.camera_add(location=(350, -560, 520))
cam = bpy.context.object
direction = mathutils.Vector((430, 0, 3)) - cam.location
cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 28
sc.camera = cam
sc.frame_set(30)

sc.render.resolution_x, sc.render.resolution_y = 1400, 900
sc.render.filepath = r"C:\App\gitar\2-0\manual\img\_palka_guitar.png"
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=r"C:\App\gitar\2-0\Гитара_палка.blend")
print("FULL OK")
