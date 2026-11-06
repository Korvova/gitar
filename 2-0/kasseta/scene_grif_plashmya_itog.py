# Итоговая схема 06.11 (19.38): основание грифа 2.5 + щель под провода 2 + платформа 2 + лыжи и шестерня 4 + мотор 12.2
# + зазор 0.3 + крышка = дно ложа 1.5 = 24.5 мм. Шпилька М3 без головки сквозь трубку мотора, шестерня m1 z12 на выходе.
# 4 тележки с шагом 30 на общей платформе, платформа ездит вдоль неподвижного основания. Провода: вниз в прорезь, плоская
# катящаяся петля в щели, шина вдоль грифа. Датчика положения нет. Оси: X поперёк, Y вдоль, Z вверх; 0 — верх платформы.
import bpy, bmesh, math, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Гриф_плашмя_итог.blend")
PITCH = 30.0
HALF_Y = 14.7                       # тележка вдоль грифа ±14.7
HALF_X = 14.7
R_M = 13.9                          # мотор Ø27.8
Z_G0, Z_G1 = 0.3, 3.8               # шестерня, рейка
Z_RK = 2.4                          # верх рейки (над ней проходит перемычка)
Z_R = 2.4                           # верх рельсов
Z_P0, Z_P1 = 2.6, 4.0               # плашки под дном мотора (над рельсами)
Z_M0, Z_M1 = 4.0, 16.2              # мотор 12.2
Z_BASE = 5.8                        # неподвижное дно мотора до этой высоты
Z_T0, Z_T1 = 16.5, 18.0             # крышка с дыркой под головку винта
Z_L2 = 21.8                         # верх бортов ложа; дно ложа = крышка # ложе: низ, дно, верх бортиков
R_PITCH, ZT = 6.0, 12               # шестерня m1 z12
TRAVEL = 22.0
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
M_FLOOR = mat("дно грифа", (0.85, 0.72, 0.5, 1))
M_RAIL = mat("рельсы", (0.5, 0.5, 0.55, 1))
M_RACK = mat("рейка", (0.35, 0.55, 0.9, 1))
M_PLAT = mat("платформа", (0.3, 0.75, 0.45, 1))
M_FRAME = mat("стойки и крышка", (0.95, 0.55, 0.15, 1), 0.55)
M_LZ = mat("ложе", (0.95, 0.75, 0.35, 1))
M_STAT = mat("дно мотора (стоит)", (0.3, 0.3, 0.34, 1))
M_CAN = mat("корпус мотора (крутится)", (0.1, 0.1, 0.12, 1))
M_MARK = mat("метка на корпусе", (0.95, 0.95, 0.95, 1))
M_GEAR = mat("шестерня", (0.9, 0.2, 0.2, 1))
M_SCR = mat("винты", (0.75, 0.75, 0.78, 1))
M_WIRE = mat("провода", (0.05, 0.05, 0.05, 1))
M_STR = mat("струны", (0.95, 0.95, 0.95, 1))

def tag(o, g): o["grp"] = g; return o
def box(name, x0, x1, y0, y1, z0, z1, m, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x0+x1)/2, (y0+y1)/2, (z0+z1)/2))
    o = bpy.context.object; o.name = name; o.scale = (x1-x0, y1-y0, z1-z0)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True); o.data.materials.append(m)
    if parent: o.parent = parent
    return o
def cyl(name, r, z0, z1, x, y, m, parent=None, v=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=v, radius=r, depth=z1-z0, location=(x, y, (z0+z1)/2))
    o = bpy.context.object; o.name = name
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True); o.data.materials.append(m)
    if parent: o.parent = parent
    return o
def empty(name, parent=None, loc=(0, 0, 0)):
    e = bpy.data.objects.new(name, None); sc.collection.objects.link(e); e.location = loc
    if parent: e.parent = parent
    return e
def prism_xy(name, pts, z0, z1, m, parent=None):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    a = [bm.verts.new((x, y, z0)) for x, y in pts]; b = [bm.verts.new((x, y, z1)) for x, y in pts]
    bm.faces.new(a); bm.faces.new(b[::-1]); n = len(pts)
    for i in range(n):
        j = (i + 1) % n; bm.faces.new((a[i], a[j], b[j], b[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); sc.collection.objects.link(o); o.data.materials.append(m)
    if parent: o.parent = parent
    return o
def prism_x(name, pts_yz, x0, x1, m, parent=None):
    # контур в плоскости YZ, вытянут вдоль X
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    a = [bm.verts.new((x0, y, z)) for y, z in pts_yz]; b = [bm.verts.new((x1, y, z)) for y, z in pts_yz]
    bm.faces.new(a); bm.faces.new(b[::-1]); n = len(pts_yz)
    for i in range(n):
        j = (i + 1) % n; bm.faces.new((a[i], a[j], b[j], b[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); sc.collection.objects.link(o); o.data.materials.append(m)
    if parent: o.parent = parent
    return o
def gear_pts():
    pts = []; ra, rf = R_PITCH + 1.0, R_PITCH - 1.25; w = 2*math.pi/ZT
    for k in range(ZT):
        t = w*k - w/2                    # зуб точно на угле w*k, в том числе на 90° (в сторону рейки)
        for f, r in ((0.0, rf), (0.18, rf), (0.30, ra), (0.70, ra), (0.82, rf)):
            pts.append((r*math.cos(t + f*w), r*math.sin(t + f*w)))
    return pts
def wire(name, pts, parent):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.25; cu.bevel_resolution = 1
    sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
    for p, q in zip(sp.points, pts): p.co = (q[0], q[1], q[2], 1)
    o = bpy.data.objects.new(name, cu); sc.collection.objects.link(o); o.data.materials.append(M_WIRE)
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o
    bpy.ops.object.convert(target='MESH'); o = bpy.context.object; o.parent = parent; tag(o, "wire"); return o
def difference(o, cutters):
    for c_ in cutters:
        md = o.modifiers.new("вырез", 'BOOLEAN'); md.object = c_; md.operation = 'DIFFERENCE'; md.solver = 'EXACT'
    bpy.context.view_layer.objects.active = o
    for md in list(o.modifiers): bpy.ops.object.modifier_apply(modifier=md.name)
    for c_ in cutters: bpy.data.objects.remove(c_)

HOLE_R = 6.0                         # отверстия дна мотора на Ø12 (оценка по фото)
RY = 12.0                            # оси рельсов ±12

def build_fixed(y0):
    # рейка: зубья к шестерне (−Y), стоит неподвижно на дне грифа
    tag(box("рейка: тело", -26, 26, y0 + 7.25, y0 + 9.0, Z_G0, Z_RK, M_RACK), "fix")
    k = -9
    while k <= 9:
        xc = k * math.pi + math.pi / 2
        if abs(xc) < 25.5:
            tag(box("рейка: зуб", xc - 0.62, xc + 0.62, y0 + 5.0, y0 + 7.25, Z_G0, Z_RK, M_RACK), "fix")
        k += 1
    tag(box("рейка: опора", -26, 26, y0 + 7.25, y0 + 9.0, 0, Z_G0, M_RACK), "fix")
    # рельсы — ласточкин хвост (низ уже, верх шире)
    for sy in (-1, 1):
        yc = y0 + sy * RY
        tag(prism_x("рельс", [(yc - 0.9, 0), (yc + 0.9, 0), (yc + 1.5, Z_R), (yc - 1.5, Z_R)], -26, 26, M_RAIL), "fix")

def build_cart(y0, phase):
    C = empty("ТЕЛЕЖКА шаг %d" % y0, None, (0, y0, 0))
    # ---- две плашки под дном мотора: задняя с вырезом под шестерню, передняя за рейкой ----
    PB = box("плашка задняя", -HALF_X, HALF_X, -HALF_Y, -5.0, Z_P0, Z_P1, M_PLAT)
    difference(PB, [cyl("c", 7.5, Z_P0 - 1, Z_P1 + 1, 0, 0, M_PLAT, None, 48), box("c", -4.5, 4.5, -13.0, -7.0, Z_P0 - 1, Z_P1 + 1, M_PLAT)]); PB.parent = C; tag(PB, "frame")
    tag(box("плашка передняя (за рейкой)", -HALF_X, HALF_X, 9.3, HALF_Y, Z_P0, Z_P1, M_PLAT, C), "frame")
    tag(box("перемычка над рейкой", 8.0, 10.6, -5.0, 9.3, Z_P0, Z_P1, M_PLAT, C), "frame")
    for sx in (-1, 1):
        xa, xb = sorted((sx * 2.05, sx * 3.0))
        tag(box("щёчка упора (скользит с лапой)", xa, xb, -9.3, -7.45, 0.3, Z_P0, M_PLAT, C), "frame")
    # лапы — ласточкин хвост, охватывают рельс
    for sy in (-1, 1):
        yc = sy * RY
        for s_ in (-1, 1):
            pts = [(yc + s_*1.7, Z_P0), (yc + s_*2.7, Z_P0), (yc + s_*2.7, 0.3), (yc + s_*1.1, 0.3)]
            if s_ > 0 and sy > 0: pts = [(yc + 1.7, Z_P0), (HALF_Y, Z_P0), (HALF_Y, 0.3), (yc + 1.1, 0.3)]
            if s_ < 0 and sy < 0: pts = [(yc - 1.7, Z_P0), (-HALF_Y, Z_P0), (-HALF_Y, 0.3), (yc - 1.1, 0.3)]
            tag(prism_x("лапа", pts, -HALF_X, HALF_X, M_PLAT, C), "frame")
    # ---- стойки, крышка, ложе ----
    for sx in (-1, 1):
        for sy in (-1, 1):
            xa, xb = sorted((sx*10.6, sx*HALF_X)); ya, yb = sorted((sy*10.6, sy*HALF_Y))
            tag(box("стойка", xa, xb, ya, yb, Z_P0, Z_T0, M_FRAME, C), "frame")
    tag(box("крышка = дно ложа", -HALF_X, HALF_X, -HALF_Y, HALF_Y, Z_T0, Z_T1, M_LZ, C), "frame")
    for sx in (-1, 1):
        xa, xb = sorted((sx*10.5, sx*12))
        tag(box("ложе: борт", xa, xb, -12.5, 12.5, Z_T1, Z_L2, M_LZ, C), "frame")
    # ---- неподвижное дно мотора, пайка, провода ----
    tag(cyl("дно мотора (стоит, с проводами)", R_M, Z_M0, Z_BASE, 0, 0, M_STAT, C, 64), "stat")
    for xw in (-2.5, 0.0, 2.5):
        tag(box("пайка", xw - 0.7, xw + 0.7, -11.5, -9.2, Z_M0 - 0.8, Z_M0, M_SCR, C), "wire")
        xs = xw * 0.3
        wire("провод", [(xw, -10.5, Z_M0 - 0.5), (xw * 0.85, -9.0, Z_M0 - 0.7), (xs, -8.2, Z_M0 - 1.5), (xs, -8.2, -3.1)], C)
    # ---- то, что крутится: корпус, винт М3 × 16, ступица, шестерня ----
    Ro = empty("ВРАЩАЕТСЯ: корпус + винт + шестерня", C)
    tag(cyl("корпус мотора", R_M, Z_BASE + 0.1, Z_M1, 0, 0, M_CAN, Ro, 64), "rot")
    tag(box("метка на корпусе", -0.8, 0.8, R_M - 0.05, R_M + 0.15, Z_BASE + 1, Z_M1 - 1, M_MARK, Ro), "rot")
    tag(box("метка сверху", -0.6, 0.6, 5, R_M - 1, Z_M1, Z_M1 + 0.1, M_MARK, Ro), "rot")
    tag(cyl("шпилька М3 без головки", 1.5, Z_M1 - 16.0, Z_M1, 0, 0, M_SCR, Ro, 16), "rot")
    tag(cyl("ступица Ø4.4 (буртик — только во внутреннее кольцо)", 2.2, Z_G1, Z_M0 - 0.02, 0, 0, M_GEAR, Ro, 24), "rot")
    tag(prism_xy("шестерня m1 z12", gear_pts(), Z_G0, Z_G1, M_GEAR, Ro), "rot")
    return C, Ro, phase

# ---- дно грифа и струны ----
NC = 4; YS = [PITCH * k for k in range(NC)]
Y0, Y1 = -16.0, YS[-1] + 16.0
M_BASE = mat("основание грифа 2.5 (стоит)", (0.72, 0.6, 0.42, 1))
M_SIDE = mat("бортики щели (стоят)", (0.55, 0.45, 0.3, 1))
tag(box("основание грифа 2.5", -26, 26, Y0 - 45, Y1 + 90, -6.5, -4.0, M_BASE), "base")
for sx in (-1, 1):
    xa, xb = sorted((sx*25.0, sx*26.0))
    tag(box("бортик щели 2 мм (платформа скользит по нему)", xa, xb, Y0 - 45, Y1 + 90, -4.0, -2.0, M_SIDE), "base")
Pl = empty("ПЛАТФОРМА (едет вдоль грифа)")
FL = box("платформа 2 мм", -26, 26, Y0, Y1, -2, 0, M_FLOOR); tag(FL, "fix")
difference(FL, [box("c", -24.2, 24.2, y_ - 9.15, y_ - 7.25, -3, 1, M_FLOOR) for y_ in YS])
M_STOP = mat("упоры", (0.9, 0.9, 0.2, 1))
for y_ in YS:
    for sx in (-1, 1):
        xa, xb = sorted((sx * 25.05, sx * 26.0))
        tag(box("упор", xa, xb, y_ - 9.25, y_ - 7.3, 0, 2.5, M_STOP), "fix")
carts = []
for i, y0 in enumerate(YS):
    build_fixed(y0)
    carts.append(build_cart(y0, 0.25 * i))

# плоские катящиеся петли проводов в щели: подвижная ветвь от тележки, полукруг, неподвижная ветвь, шина вдоль грифа
M_RIB = mat("шлейф проводов (тонкие)", (0.95, 0.55, 0.1, 1))
RIB_Z0, RIB_Z1 = -3.6, -3.1
def half_band(name, r0, r1, z0, z1, m, n=16):
    me = bpy.data.meshes.new(name); bm = bmesh.new(); rings = []
    for k in range(n + 1):
        a = -math.pi/2 + math.pi * k / n; c, q = math.cos(a), math.sin(a)
        rings.append([bm.verts.new((r*c, r*q, z)) for r in (r0, r1) for z in (z0, z1)])
    for k in range(n):
        a, b = rings[k], rings[k+1]
        for u, v in ((0, 1), (2, 3), (0, 2), (1, 3)):
            bm.faces.new((a[u], a[v], b[v], b[u]))
    for q in (rings[0], rings[-1]): bm.faces.new((q[0], q[1], q[3], q[2]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); sc.collection.objects.link(o); o.data.materials.append(m); return o
loops = []
for i, y0 in enumerate(YS):
    ya, yb = y0 - 8.2, y0 - 3.2; xf = -0.5 - 2.0 * i
    mv = box("петля: ветвь от тележки", -1, 0, ya - 0.8, ya + 0.8, RIB_Z0, RIB_Z1, M_RIB)
    fx = box("петля: неподвижная ветвь", -1, 0, yb - 0.8, yb + 0.8, RIB_Z0, RIB_Z1, M_RIB)
    bd = half_band("петля: изгиб", 1.7, 3.3, RIB_Z0, RIB_Z1, M_RIB)
    loops.append((mv, fx, bd, ya, yb, xf))
    tag(box("шина вдоль грифа", xf - 0.8, xf + 0.8, yb - 0.8, Y1 + 40, -3.95, -3.7, M_RIB), "bus")
    for o in (mv, fx, bd): tag(o, "rib")
for o in list(sc.objects):
    if o.parent is None and o.get("grp") != "base" and o != Pl:
        o.parent = Pl
for f in range(1, FR + 1):
    t = (f - 1) / (FR - 1)
    Pl.location.y = 25.0 * math.sin(2 * math.pi * t); Pl.keyframe_insert("location", index=1, frame=f)
    for (C, Ro, ph), (mv, fx, bd, ya, yb, xf) in zip(carts, loops):
        x = TRAVEL * math.sin(4 * math.pi * (t + ph))
        C.location.x = x; C.keyframe_insert("location", index=0, frame=f)
        Ro.rotation_euler = (0, 0, x / R_PITCH); Ro.keyframe_insert("rotation_euler", index=2, frame=f)
        xa = x - 0.5
        xb = (21.9 + xa) / 2.0
        mv.location.x = xb; mv.scale.x = max(xb - xa, 0.01); mv.keyframe_insert("location", index=0, frame=f); mv.keyframe_insert("scale", index=0, frame=f)
        fx.location.x = xb; fx.scale.x = max(xb - xf, 0.01); fx.keyframe_insert("location", index=0, frame=f); fx.keyframe_insert("scale", index=0, frame=f)
        bd.location = (xb, (ya + yb) / 2.0, 0); bd.keyframe_insert("location", frame=f)

def camera(n, loc, tgt, lens=50, ortho=None):
    tg = empty(n + " цель", None, tgt)
    c = bpy.data.objects.new(n, bpy.data.cameras.new(n)); sc.collection.objects.link(c)
    c.location = loc; c.data.lens = lens; c.data.clip_start = 1; c.data.clip_end = 3000
    if ortho: c.data.type = 'ORTHO'; c.data.ortho_scale = ortho
    k = c.constraints.new('TRACK_TO'); k.target = tg; k.track_axis = 'TRACK_NEGATIVE_Z'; k.up_axis = 'UP_Y'
    return c
sc.camera = camera("Камера: наискосок", (120, -110, 95), (0, 45, 5))
camera("Камера: сбоку вдоль рейки", (-300, 45, 8), (0, 45, 8), ortho=150)
camera("Камера: сверху", (0, 45, 300), (0, 45, 0), ortho=170)
camera("Камера: торец", (0, -300, 8), (0, 0, 8), ortho=70)
sun = bpy.data.objects.new("Солнце", bpy.data.lights.new("Солнце", "SUN")); sun.data.energy = 3
sun.rotation_euler = (math.radians(40), math.radians(10), math.radians(30)); sc.collection.objects.link(sun)
sc.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=OUT); print("saved", OUT)
