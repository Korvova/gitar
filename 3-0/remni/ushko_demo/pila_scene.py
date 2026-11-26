# Анимация (26.11): два ушка-«пилы» на спинке ремня 2 мм, зуб тележки между ними. Ремень бежит по петле на роликах ±22,
# тележка ездит ±21. На краю хода наружное ушко заходит на ролик и загибается вместе с ремнём; толкающая грань
# у зуба остаётся на прямом участке; скат не достаёт до стенки корпуса (гриф 53, стенка с x = 25.7).
# Запуск: blender -b -P pila_scene.py
import bpy, bmesh, math, os
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.unit_settings.scale_length = 0.001; sc.unit_settings.length_unit = 'MILLIMETERS'
HERE = r"C:\App\gitar\3-0\remni\ushko_demo"
XC, R, TB, H, WT, W = 22.0, 2.5, 0.9, 0.7, 0.9, 2.0
LOOP = 4 * XC + 2 * math.pi * R; N = 39; P = LOOP / N
S = 21.0
T_W, G = 1.5, 0.1                      # зуб тележки вдоль хода, зазор
LL, HP, NSL = 3.0, 1.5, 6              # ушко: длина вдоль ремня, вынос у толкающей грани, ломтиков
WALL_X = 26.5 - 0.8


def mat(n, c):
    m = bpy.data.materials.new(n); m.diffuse_color = c; return m


M_B, M_L, M_C, M_R, M_W = mat("ремень", (0.95, 0.75, 0.2, 1)), mat("ушки", (0.95, 0.45, 0.1, 1)), mat("тележка", (0.2, 0.4, 0.9, 1)), mat("ролик", (0.8, 0.8, 0.82, 1)), mat("стенка", (0.5, 0.5, 0.55, 1))


def mesh_obj(name, verts, faces, m):
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update()
    o = bpy.data.objects.new(name, me); sc.collection.objects.link(o); o.data.materials.append(m); return o


def prism(name, poly, z0, z1, m):                     # призма из многоугольника (x, y) по z
    n = len(poly)
    v = [(x, y, z0) for x, y in poly] + [(x, y, z1) for x, y in poly]
    f = [list(range(n))[::-1], list(range(n, 2 * n))] + [[i, (i + 1) % n, n + (i + 1) % n, n + i] for i in range(n)]
    return mesh_obj(name, v, f, m)


def path_pt(s):
    s %= LOOP
    if s < 2 * XC: return (-XC + s, R)
    s -= 2 * XC
    if s < math.pi * R: a = math.pi / 2 - s / R; return (XC + R * math.cos(a), R * math.sin(a))
    s -= math.pi * R
    if s < 2 * XC: return (XC - s, -R)
    s -= 2 * XC; a = -math.pi / 2 - s / R; return (-XC + R * math.cos(a), R * math.sin(a))


# путь по внутренней стороне спинки (по часовой: верх слева направо)
cu = bpy.data.curves.new("путь ремня", 'CURVE'); cu.dimensions = '3D'; cu.use_path = True
sp = cu.splines.new('POLY'); K = 800; sp.points.add(K - 1)
for i in range(K):
    x, y = path_pt(LOOP * i / K); sp.points[i].co = (x, y, 0, 1)
sp.use_cyclic_u = True
PATH = bpy.data.objects.new("путь ремня", cu); sc.collection.objects.link(PATH); PATH.hide_render = True; PATH.hide_set(True)

# спинка ремня — неподвижная (при движении выглядит так же)
band = []
def ring(r0, r1, cx, a0, a1, nm):
    pts = [(cx + r1 * math.cos(math.radians(a0 + (a1 - a0) * k / 24)), r1 * math.sin(math.radians(a0 + (a1 - a0) * k / 24))) for k in range(25)]
    pts += [(cx + r0 * math.cos(math.radians(a1 - (a1 - a0) * k / 24)), r0 * math.sin(math.radians(a1 - (a1 - a0) * k / 24))) for k in range(25)]
    prism(nm, pts, 0, W, M_B)
ring(R, R + TB, XC, -90, 90, "спинка: дуга справа"); ring(R, R + TB, -XC, 90, 270, "спинка: дуга слева")
prism("спинка: верхняя ветвь", [(-XC, R), (XC, R), (XC, R + TB), (-XC, R + TB)], 0, W, M_B)
prism("спинка: нижняя ветвь", [(-XC, -R - TB), (XC, -R - TB), (XC, -R), (-XC, -R)], 0, W, M_B)

movers = []                                            # (объект, позиция на петле при s = 0)
def follower(obj, s0):
    c = obj.constraints.new('FOLLOW_PATH'); c.target = PATH; c.use_fixed_location = True; c.use_curve_follow = True
    c.forward_axis = 'FORWARD_X'; c.up_axis = 'UP_Z'; movers.append((c, s0))

for i in range(N):                                     # зубья внутрь петли (локально −y)
    o = prism("зуб ремня", [(-WT / 2, -H), (WT / 2, -H), (WT / 2, 0.02), (-WT / 2, 0.02)], 0, W, M_B); follower(o, (i + 0.5) * P)

S_CART = 2 * XC / 2                                    # центр тележки на петле при s = 0 (x = 0 на верхней ветви)
d = LL / NSL
for side in (-1, 1):                                   # ушки-пилы: грань к зубу вертикальная, скат наружу
    for k in range(NSL):
        u0, u1 = T_W / 2 + G + k * d, T_W / 2 + G + (k + 1) * d
        h0, h1 = HP * (1 - k / NSL) , HP * (1 - (k + 1) / NSL) + 0.05
        c_ = (u0 + u1) / 2
        poly = [(-d / 2 - 0.01, TB - 0.02), (d / 2 + 0.01, TB - 0.02), (d / 2 + 0.01, TB + h1), (-d / 2 - 0.01, TB + h0)]
        if side < 0: poly = [(-x, y) for x, y in poly][::-1]
        o = prism("ушко-пила %s, ломтик %d" % ("левое" if side < 0 else "правое", k + 1), poly, 0, W, M_L)
        follower(o, S_CART + side * c_)

# тележка: зуб между ушками + пластина в прорези + площадка 8.5 × 10; хвост зуба под крышкой (держит от подъёма)
YB = R + TB
cart = bpy.data.objects.new("тележка", None); sc.collection.objects.link(cart)
for nm, poly, z0, z1 in (("зуб тележки между ушками", [(-T_W / 2, YB + G), (T_W / 2, YB + G), (T_W / 2, YB + HP + G + 1.0), (-T_W / 2, YB + HP + G + 1.0)], 0.0, W + 0.15),
                         ("пластина в прорези", [(-3, YB - 0.0), (3, YB), (3, YB + 1.4), (-3, YB + 1.4)], W + 0.1, W + 1.25),
                         ("площадка пальца 8.5 × 10", [(-4.25, -5), (4.25, -5), (4.25, 5), (-4.25, 5)], W + 1.2, W + 2.4)):
    prism(nm, poly, z0, z1, M_C).parent = cart

for x in (-XC, XC, 13.0):                              # концевые ролики и ведущий (упрощённо, по дну зубьев)
    bpy.ops.mesh.primitive_cylinder_add(radius=R - H, depth=W + 0.1, location=(x, 0, W / 2)); o = bpy.context.object
    o.name = "ролик (упрощённо)"; o.data.materials.append(M_R)
for sx in (-1, 1):
    prism("стенка корпуса 0.8 (гриф 53)", [(sx * WALL_X, -8), (sx * 26.5, -8), (sx * 26.5, 9), (sx * WALL_X, 9)][:: sx], -0.5, W + 1.0, M_W)

# анимация: s = 21·sin
F = 240
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'CONSTANT'   # factor перескакивает 1 → 0 — без промежуточных кадров
for f in range(1, F + 1):
    s = S * math.sin(2 * math.pi * (f - 1) / F)
    cart.location.x = s; cart.keyframe_insert("location", index=0, frame=f)
    for c, s0 in movers:
        c.offset_factor = ((s0 + s) / LOOP) % 1.0; c.keyframe_insert("offset_factor", frame=f)
sc.frame_start, sc.frame_end = 1, F

# проверка: максимальный x ушек на краю хода и зазор до стенки
dg = bpy.context.evaluated_depsgraph_get()
for f in (61, 181):
    sc.frame_set(f); dg.update()
    mx = max(abs((o.matrix_world @ v.co).x) for o in bpy.data.objects if o.name.startswith("ушко") for v in o.data.vertices)
    print("кадр %d (тележка %+.1f): ушки до |x| = %.2f, стенка %.2f, зазор %.2f" % (f, cart.location.x, mx, WALL_X, WALL_X - mx))
sc.frame_set(1)
for o in cart.children:                                  # площадку и пластину скрыть (видно ушки сверху); показать — Alt+H
    if not o.name.startswith("зуб"): o.hide_set(True)
for scr in bpy.data.screens:
    for ar in scr.areas:
        for sp_ in ar.spaces:
            if sp_.type == 'VIEW_3D':
                sp_.shading.type = 'SOLID'; sp_.shading.color_type = 'MATERIAL'; sp_.clip_start = 0.1; sp_.clip_end = 1000
                r3 = sp_.region_3d; r3.view_location = (14, 1, 1); r3.view_distance = 38; r3.view_rotation = (0.97, 0.22, 0.03, 0.08)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "pila_demo.blend")); print("saved")
