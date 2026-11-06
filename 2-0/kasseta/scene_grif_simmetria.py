# Симметрия: скосы ±12.1 зеркально, окна сбоку y 4.7...12.1 и y -12.1...-4.7. Спинка рейки толще: основание до 11.25, верх до 11.85.
# Задний рельс узкий, как спинка рейки: скос только наружу, внутренняя грань y -9.5, упор вплотную к ней. Заглушки нет, заднее окно уже.
# Идея владельца: рейка и ласточкин хвост — одно целое. У спинки рейки скос, за него цепляется передняя лапа; отдельного переднего рельса нет.
# Сзади один рельс со скосом наружу. Два встречных скоса держат тележку.
# Сбоку у кубика два чистых окна: заднее y -13.7...-7.1 (рельс, упор), переднее y 4.7...13.7 (рейка, рельс). Лапы ±14.1, за юбкой.
# Идея владельца: мотор перевёрнут. Неподвижная часть с пайкой вверху, приклеена к крышке кубика; провода от пайки сразу
# в центральную трубку и вниз. Крутящийся торец корпуса смотрит вниз, на нём фланец с полой шестернёй. Лапы держатся
# от крышки через стенки и юбку кубика. Щель 3 мм под осью шестерни.
# Идея владельца: один паз в платформе вместо рейки и прорези. На стенке паза зубья, шестерня утоплена в паз,
# рядом вниз идут провода, по бокам только ласточкины хвосты. Дно паза 0.5 мм держит платформу целой, концы паза открыты.
# Эскиз: ширина снова 52 мм. Неподвижного бортика нет, низ закрыт самой тележкой: кубик идёт почти до платформы.
# Лапы и плашки снова ±14.7, как в 19.38. Рейка с крышкой из 19.41.
# Эскиз внешнего вида (не утверждён): механика 19.38, но низ спрятан в неподвижную ванночку с бортиком 4 мм,
# тележка сверху — закрытый кубик, который выезжает над бортиком. Лапы и плашки укорочены до ±7.
# Итоговая схема 06.11 (19.38): основание грифа 2.5 + щель под провода 2 + платформа 2 + лыжи и шестерня 4 + мотор 12.2
# + зазор 0.3 + крышка = дно ложа 1.5 = 24.5 мм. Шпилька М3 без головки сквозь трубку мотора, шестерня m1 z12 на выходе.
# 4 тележки с шагом 30 на общей платформе, платформа ездит вдоль неподвижного основания. Провода: вниз в прорезь, плоская
# катящаяся петля в щели, шина вдоль грифа. Датчика положения нет. Оси: X поперёк, Y вдоль, Z вверх; 0 — верх платформы.
import bpy, bmesh, math, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Гриф_симметрия.blend")
PITCH = 30.0
HALF_Y = 14.7                       # тележка вдоль грифа ±14.7
HALF_X = 14.7
R_M = 13.9                          # мотор Ø27.8
Z_G0, Z_G1 = -1.3, 3.8               # шестерня, рейка
Z_RK = 0.8                          # верх рейки (над ней проходит перемычка)
Z_R = 2.4                           # верх рельсов
Z_P0, Z_P1 = 2.6, 3.7               # плашки под дном мотора (над рельсами)
Z_M0, Z_M1 = 4.0, 16.2              # мотор 12.2
Z_BASE = 5.8                        # неподвижное дно мотора до этой высоты
Z_T0, Z_T1 = 16.2, 17.7             # крышка с дыркой под головку винта
Z_L2 = 21.5                         # верх бортов ложа; дно ложа = крышка # ложе: низ, дно, верх бортиков
R_PITCH, ZT = 6.0, 12               # шестерня m1 z12
TRAVEL = 22.0
LOW_X = 14.7                         # нижний этаж тележки ±7: на краю хода 22 + 7 = 29
TUB_IN, TUB_OUT = 26.0, 26.0        # бортик ванночки
TUB_TOP = 3.95                      # верх бортика
Z_SHELL = 4.1                       # низ кубика
R_CUT = 14.1                        # полость под мотор Ø27.8 (зазор 0.2, стенка 0.6)
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
M_FLOOR = mat("дно ванночки (матовое чёрное)", (0.035, 0.035, 0.04, 1))
M_RAIL = mat("рельсы (чёрные)", (0.05, 0.05, 0.055, 1))
M_RACK = mat("рейка (чёрная)", (0.05, 0.05, 0.055, 1))
M_PLAT = mat("низ тележки (цвет кубика)", (0.86, 0.83, 0.77, 1))
M_FRAME = mat("стойки и крышка", (0.95, 0.55, 0.15, 1), 0.55)
M_LZ = mat("кубик тележки", (0.86, 0.83, 0.77, 1))
M_TUB = mat("ванночка, бортик", (0.2, 0.2, 0.22, 1))
M_STAT = mat("дно мотора (стоит)", (0.3, 0.3, 0.34, 1))
M_CAN = mat("корпус мотора (крутится)", (0.1, 0.1, 0.12, 1))
M_MARK = mat("метка на корпусе", (0.95, 0.95, 0.95, 1))
M_GEAR = mat("шестерня", (0.06, 0.06, 0.065, 1))
M_SCR = mat("винты, пайка", (0.2, 0.2, 0.22, 1))
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

def rounded_box(name, x0, x1, y0, y1, z0, z1, r, m):
    o = box(name, x0, x1, y0, y1, z0, z1, m)
    bm = bmesh.new(); bm.from_mesh(o.data)
    ed = [e for e in bm.edges if not (abs(e.verts[0].co.z - z0) < 1e-6 and abs(e.verts[1].co.z - z0) < 1e-6)]
    bmesh.ops.bevel(bm, geom=ed, offset=r, segments=4, profile=0.5, affect='EDGES')
    bm.to_mesh(o.data); bm.free(); return o

HOLE_R = 6.0                         # отверстия дна мотора на Ø12 (оценка по фото)
RY = 12.0                            # оси рельсов ±12

def build_fixed(y0):
    # рейка: зубья к шестерне (−Y), стоит неподвижно на дне грифа
    tag(box("паз: задняя стенка с зубьями", -TUB_IN, TUB_IN, y0 + 7.25, y0 + 9.0, -1.5, Z_RK, M_RACK), "fix")
    k = -10
    while k <= 9:
        xc = k * math.pi + math.pi / 2
        if abs(xc) < 25.5:
            tag(box("рейка: зуб", xc - 0.62, xc + 0.62, y0 + 5.0, y0 + 7.25, -1.5, Z_RK, M_RACK), "fix")
        k += 1
    tag(prism_x("рейка: спинка со скосом", [(y0 + 7.25, 0), (y0 + 11.25, 0), (y0 + 11.85, 2.4), (y0 + 7.25, 2.4)], -TUB_IN, TUB_IN, M_RACK), "fix")
    tag(box("рейка: крышка над зубьями", -TUB_IN, TUB_IN, y0 + 5.0, y0 + 7.25, 1.0, 2.4, M_RACK), "fix")
    # задний рельс: скос только наружу (−Y)
    tag(prism_x("рельс", [(y0 - 11.25, 0), (y0 - 9.5, 0), (y0 - 9.5, Z_R), (y0 - 11.85, Z_R)], -TUB_IN, TUB_IN, M_RAIL), "fix")

def build_cart(y0, phase):
    C = empty("ТЕЛЕЖКА шаг %d" % y0, None, (0, y0, 0))
    # ---- нижний этаж ±7, он ходит внутри ванночки ----
    PB = box("плашка задняя", -LOW_X, LOW_X, -HALF_Y, -5.0, Z_P0, Z_P1, M_PLAT)
    difference(PB, [cyl("c", 8.0, Z_P0 - 1, Z_P1 + 1, 0, 0, M_PLAT, None, 48)]); PB.parent = C; tag(PB, "frame")
    tag(box("плашка передняя (за рейкой)", -LOW_X, LOW_X, 9.3, HALF_Y, Z_P0, Z_P1, M_PLAT, C), "frame")
    for sy in (-1, 1):
        ya, yb = sorted((sy * R_CUT, sy * HALF_Y))
        tag(box("язычок: низ к кубику", -LOW_X, LOW_X, ya, yb, Z_P1, Z_SHELL + 0.1, M_PLAT, C), "frame")
    tag(box("перемычка над рейкой", 8.0, 10.6, -5.0, 9.3, Z_P0, Z_P1, M_PLAT, C), "frame")
    for sx in (-1, 1):
        xa, xb = sorted((sx * 2.05, sx * 3.0))
        tag(box("щёчка упора (скользит с лапой)", xa, xb, -9.3, -7.45, 0.3, Z_P0, M_RAIL, C), "frame")
        tag(box("щёчка: верх до шейки шестерни", xa, xb, -7.45, -4.9, 1.0, 2.4, M_RAIL, C), "frame")
    yc = -RY
    tag(prism_x("лапа задняя", [(-12.1, Z_P0), (-HALF_Y, Z_P0), (-HALF_Y, 0.3), (-11.525, 0.3)], -R_CUT, R_CUT, M_RAIL, C), "frame")
    tag(prism_x("лапа передняя (за спинкой рейки)", [(11.525, 0.3), (HALF_Y, 0.3), (HALF_Y, Z_P0), (12.1, Z_P0)], -R_CUT, R_CUT, M_RAIL, C), "frame")
    # ---- закрытый кубик: скруглён сверху и по вертикальным рёбрам, снизу плоский ----
    # боковая юбка: закрывает шестерню и плашки сбоку; проёмы — под рейку (y 4.7…9.2) и у лап (они сами закрывают низ)
    for sx in (-1, 1):
        xa, xb = sorted((sx * R_CUT, sx * HALF_X))
        tag(box("юбка: верх", xa, xb, -HALF_Y, HALF_Y, Z_P0, Z_SHELL + 0.1, M_PLAT, C), "frame")
        tag(box("юбка: задняя стенка", xa, xb, -HALF_Y, -12.1, 0.3, Z_P0, M_PLAT, C), "frame")
        tag(box("юбка: передняя стенка", xa, xb, 12.1, HALF_Y, 0.3, Z_P0, M_PLAT, C), "frame")
        tag(box("юбка: у шестерни", xa, xb, -4.7, 4.7, 0.3, Z_P0, M_PLAT, C), "frame")
    SH = rounded_box("КУБИК", -HALF_X, HALF_X, -HALF_Y, HALF_Y, Z_SHELL, Z_T1, 1.0, M_LZ)
    difference(SH, [cyl("c", R_CUT, Z_SHELL - 1, Z_T0, 0, 0, M_LZ, None, 96),
                    box("c", -5.5, 5.5, -12.5, -6.0, Z_T0 - 0.2, 17.0, M_LZ),
                    box("c", -1.2, 1.2, -9.0, 1.0, Z_T0 - 0.2, 17.0, M_LZ),
                    cyl("c", 5.0, Z_T0 - 0.2, Z_T0 + 0.3, 0, 0, M_LZ, None, 48)]); SH.parent = C; tag(SH, "frame")
    for sx in (-1, 1):
        xa, xb = sorted((sx*10.5, sx*12))
        B = rounded_box("ложе: борт", xa, xb, -12.5, 12.5, Z_T1 - 0.05, Z_L2, 0.5, M_LZ); B.parent = C; tag(B, "frame")
    # ---- неподвижное дно мотора, пайка, провода ----
    tag(cyl("дно мотора (стоит, приклеено к крышке)", R_M, Z_M1 - 1.8, Z_M1, 0, 0, M_STAT, C, 64), "stat")
    for xw in (-3.2, 0.0, 3.2):
        tag(box("пайка", xw - 0.7, xw + 0.7, -11.5, -9.2, Z_M1, Z_M1 + 0.7, M_SCR, C), "wire")
        d = xw / 3.2 * 0.5
        wire("провод", [(xw, -10.0, Z_M1 + 0.5), (d, -7.0, Z_M1 + 0.5), (d * 0.45, -1.5, Z_M1 + 0.5), (d * 0.45, -d * 0.2, Z_M1 + 0.35), (d * 0.45, -d * 0.2, -3.1)], C)
    # ---- то, что крутится: корпус, винт М3 × 16, ступица, шестерня ----
    Ro = empty("ВРАЩАЕТСЯ: корпус + винт + шестерня", C)
    tag(cyl("корпус мотора", R_M, Z_M0, Z_M1 - 1.9, 0, 0, M_CAN, Ro, 64), "rot")
    tag(box("метка на корпусе", -0.8, 0.8, R_M - 0.05, R_M + 0.15, Z_M0 + 1, Z_M1 - 3, M_MARK, Ro), "rot")
    TB = cyl("трубка самого мотора Ø3 внутри", 2.2, Z_M0, Z_M1, 0, 0, M_SCR, None, 32)
    difference(TB, [cyl("c", 1.5, Z_M0 - 1, Z_M1 + 1, 0, 0, M_SCR, None, 32)]); TB.parent = Ro; tag(TB, "rot")
    FL_ = cyl("фланец шестерни (клей на торец корпуса, М2 если есть резьба)", 7.5, Z_P0, Z_M0 - 0.02, 0, 0, M_GEAR, None, 48)
    difference(FL_, [cyl("c", 1.6, Z_P0 - 1, Z_M0 + 1, 0, 0, M_GEAR, None, 32)] + [cyl("c", 1.05, Z_P0 - 1, Z_M0 + 1, 6*math.cos(a_), 6*math.sin(a_), M_GEAR, None, 16) for a_ in (0.785, 2.356, 3.927, 5.498)]); FL_.parent = Ro; tag(FL_, "rot")
    GU = cyl("шестерня: шейка Ø9.4 мимо крышки рейки", 4.7, Z_RK, Z_P0, 0, 0, M_GEAR, None, 32)
    difference(GU, [cyl("c", 1.6, Z_RK - 1, Z_P0 + 1, 0, 0, M_GEAR, None, 32)]); GU.parent = Ro; tag(GU, "rot")
    GZ = prism_xy("шестерня m1 z12", gear_pts(), Z_G0, Z_RK, M_GEAR)
    difference(GZ, [cyl("c", 1.6, Z_G0 - 1, Z_RK + 1, 0, 0, M_GEAR, None, 32)]); GZ.parent = Ro; tag(GZ, "rot")
    return C, Ro, phase

# ---- дно грифа и струны ----
NC = 4; YS = [PITCH * k for k in range(NC)]
Y0, Y1 = -16.0, YS[-1] + 16.0
M_BASE = mat("основание грифа 2.5 (стоит)", (0.5, 0.33, 0.18, 1))
M_SIDE = mat("бортики щели (стоят)", (0.36, 0.23, 0.12, 1))
tag(box("основание грифа 2.5", -26, 26, Y0 - 45, Y1 + 90, -6.5, -4.0, M_BASE), "base")
for sx in (-1, 1):
    xa, xb = sorted((sx*25.0, sx*26.0))
    tag(box("бортик щели 2 мм (платформа скользит по нему)", xa, xb, Y0 - 45, Y1 + 90, -4.0, -2.0, M_SIDE), "base")
Pl = empty("ПЛАТФОРМА (едет вдоль грифа)")
FL = box("платформа 2 мм", -TUB_OUT, TUB_OUT, Y0, Y1, -2, 0, M_FLOOR); tag(FL, "fix")
difference(FL, [box("c", -24.2, 24.2, y_ - 1.5, y_ + 1.5, -3, 1, M_FLOOR) for y_ in YS] + [box("c", -30, 30, y_ - 7.3, y_ + 7.25, -1.5, 1, M_FLOOR) for y_ in YS])
M_STOP = mat("упоры (чёрные)", (0.07, 0.07, 0.08, 1))
for y_ in YS:
    for sx in (-1, 1):
        xa, xb = sorted((sx * 25.05, sx * 26.0))
        tag(box("упор", xa, xb, y_ - 9.5, y_ - 7.3, 0, 2.5, M_STOP), "fix")
carts = []
for i, y0 in enumerate(YS):
    build_fixed(y0)
    carts.append(build_cart(y0, 0.09 * i))

# плоские катящиеся петли проводов в щели: подвижная ветвь от тележки, полукруг, неподвижная ветвь, шина вдоль грифа
M_RIB = mat("шлейф проводов (чёрный)", (0.03, 0.03, 0.035, 1))
tag(box("чёрная плёнка на основании", -25, 25, Y0 - 45, Y1 + 90, -4.0, -3.97, M_RIB), "base")
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
    ya, yb = y0, y0 + 5.0; xf = -0.5 - 2.0 * i
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
    pass  # платформа стоит, ходят только тележки
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
camera("Камера: торец", (0, -300, 8), (0, 0, 8), ortho=95)
camera("Камера: близко", (70, -55, 55), (5, 30, 2))
sun = bpy.data.objects.new("Солнце", bpy.data.lights.new("Солнце", "SUN")); sun.data.energy = 3
sun.rotation_euler = (math.radians(40), math.radians(10), math.radians(30)); sc.collection.objects.link(sun)
sc.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=OUT); print("saved", OUT)
