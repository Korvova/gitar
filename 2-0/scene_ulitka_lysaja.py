# Идея владельца 05.11, вариант 3: шестерня-улитка. В каждом слое шестерня, у которой половина круга с зубьями,
# дальше зубья плавно уменьшаются и круг «лысеет» (меньший радиус). Рейка лежит СВЕРХУ, штырёк у неё прямо
# на спине — вверх в дырку тележки. Пока под рейкой зубья — рейка поднята, штырёк в тележке, тележка едет.
# Когда под рейку приходит лысый участок — рейка опускается (пружинка/вес), штырёк выходит из тележки,
# рейка стоит. Слой Б устроен зеркально: он подхватывает тележку во второй половине хода.
import bpy, bmesh, math, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Идея_улитка_лысая_шестерня.blend")
RG, Z = 9.0, 18                      # m1 z18
TRAVEL, D = 24.0, 3.0                # ход ±24; зона передачи |x| < D
RB = 5.6                             # радиус лысого участка
DROP = (RG - 1.0) - RB               # на сколько опускается рейка (2.4)
FR = 300

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
M_G = mat("шестерни-улитки", (0.95, 0.8, 0.3, 1)); M_A = mat("рейка А (левая половина)", (0.3, 0.55, 0.9, 1))
M_B = mat("рейка Б (правая половина)", (0.3, 0.75, 0.4, 1)); M_CART = mat("тележка", (0.95, 0.55, 0.15, 1), 0.55)
M_PIN = mat("штырьки", (0.1, 0.1, 0.1, 1)); M_MOT = mat("мотор (неподвижен)", (0.15, 0.15, 0.17, 1))
M_NECK = mat("края грифа ±26", (0.9, 0.2, 0.6, 1))

def box(name, x0, x1, y0, y1, z0, z1, m, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x0+x1)/2, (y0+y1)/2, (z0+z1)/2))
    o = bpy.context.object; o.name = name; o.scale = (x1-x0, y1-y0, z1-z0)
    bpy.ops.object.transform_apply(scale=True); o.data.materials.append(m)
    if parent: o.parent = parent
    return o
def empty(name, parent=None):
    e = bpy.data.objects.new(name, None); sc.collection.objects.link(e)
    if parent: e.parent = parent
    return e
def prism_xz(name, pts, y0, y1, m, parent=None):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    a = [bm.verts.new((x, y0, z)) for x, z in pts]; b = [bm.verts.new((x, y1, z)) for x, z in pts]
    bm.faces.new(a); bm.faces.new(b[::-1]); n = len(pts)
    for i in range(n):
        j = (i + 1) % n; bm.faces.new((a[i], a[j], b[j], b[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); sc.collection.objects.link(o); o.data.materials.append(m)
    if parent: o.parent = parent
    return o

def smooth(u): u = min(max(u, 0.0), 1.0); return u*u*(3 - 2*u)
def lift_A(x): return 1.0 - smooth(x / D)        # 1 — зубья (рейка поднята), 0 — лысо (рейка опущена)
def lift_B(x): return 1.0 - smooth(-x / D)
# касание сверху (90°); верх шестерни идёт в +X при повороте phi > 0 → phi = x / RG; местный угол = мировой + phi
def x_of_local(a):
    phi = (a - 0.5*math.pi + math.pi) % (2*math.pi) - math.pi
    return phi * RG
def snail_gear(lift):
    pts = []; ra, rf = RG + 1.0, RG - 1.25; w = 2*math.pi/Z
    for k in range(Z):
        t = w*k - w/2
        for i in range(12):
            f = i / 12.0
            r = rf if (f < 0.18 or f >= 0.82) else (ra if 0.3 <= f < 0.7 else rf + (ra - rf) * ((f - 0.18) / 0.12 if f < 0.3 else (0.82 - f) / 0.12))
            a = t + f*w
            L = lift(max(-TRAVEL - 3, min(TRAVEL + 3, x_of_local(a))))
            rr = RB + (r - RB) * L                       # к лысому участку зубья плавно «садятся» на круг RB
            pts.append((rr*math.cos(a), rr*math.sin(a)))
    return pts

GA, GB = (-8.0, -4.0), (-3.0, 1.0)                     # два слоя рядом
# ---- неподвижное ----
bpy.ops.mesh.primitive_cylinder_add(vertices=40, radius=13.9, depth=12.2, location=(0, 10.2, 0), rotation=(math.pi/2, 0, 0))
o = bpy.context.object; o.name = "мотор 2204 (неподвижен)"; o.data.materials.append(M_MOT)
for sx in (-1, 1):
    box("край грифа", sx*26 - 0.3, sx*26 + 0.3, -12, 6, -12, 24, M_NECK)
# ---- одна деталь на моторе: 2 шестерни-улитки + фланец ----
SH = empty("ВАЛ МОТОРА")
parts = [prism_xz("a", snail_gear(lift_A), *GA, M_G), prism_xz("b", snail_gear(lift_B), *GB, M_G)]
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=RB - 0.2, depth=1.2, location=(0, -3.5, 0), rotation=(math.pi/2, 0, 0)); parts.append(bpy.context.object)
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=7.5, depth=3.1, location=(0, 2.55, 0), rotation=(math.pi/2, 0, 0)); parts.append(bpy.context.object)
for o in parts[2:]: o.data.materials.append(M_G)
bpy.ops.object.select_all(action='DESELECT')
for o in parts: o.select_set(True)
bpy.context.view_layer.objects.active = parts[0]; bpy.ops.object.join()
o = bpy.context.object; o.name = "ОДНА ДЕТАЛЬ: 2 шестерни-улитки (лысые наполовину) + фланец"; o.parent = SH

# ---- рейки сверху, штырёк на спине ----
ZB0, ZB1 = RG + 1.25, RG + 4.0
P = math.pi
racks = {}
for key, (g, m, sgn) in {"А": (GA, M_A, 1), "Б": (GB, M_B, -1)}.items():
    R = empty("рейка %s" % key)
    x0, x1 = (-D - 1.0, TRAVEL + 1.0) if sgn > 0 else (-TRAVEL - 1.0, D + 1.0)
    box("тело рейки", x0, x1, g[0], g[1], ZB0, ZB1, m, R)
    k = math.floor(x0 / P)
    while k * P <= x1:
        xc = k * P + P/2
        if x0 + 0.6 < xc < x1 - 0.6:
            box("зуб", xc - 0.62, xc + 0.62, g[0], g[1], RG - 1.0, ZB0, m, R)
        k += 1
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=1.2, depth=2.5, location=(0, (g[0] + g[1]) / 2, ZB1 + 1.25))
    o = bpy.context.object; o.name = "штырёк на спине рейки %s" % key; o.data.materials.append(M_PIN); o.parent = R
    racks[key] = R

# ---- тележка прямо над рейками, снизу две дырки под штырьки ----
ZC0 = ZB1 + 0.5
C = empty("ТЕЛЕЖКА (едет ±24)")
box("тележка", -10, 10, -10, 3, ZC0, ZC0 + 5, M_CART, C)
box("ложе", -10, 10, -10, 3, ZC0 + 5, ZC0 + 6, M_CART, C)

# ---- анимация ----
for f in range(1, FR + 1):
    t = (f - 1) / (FR - 1)
    x = -TRAVEL * math.sin(2*math.pi*t)
    SH.rotation_euler = (0, x / RG, 0); SH.keyframe_insert("rotation_euler", frame=f)
    C.location.x = x; C.keyframe_insert("location", index=0, frame=f)
    for R, xx, L in ((racks["А"], min(x, D), lift_A(x)), (racks["Б"], max(x, -D), lift_B(x))):
        R.location = (xx, 0, -DROP * (1 - L)); R.keyframe_insert("location", frame=f)

def camera(n, loc, tgt, lens=50):
    tg = empty(n + " цель"); tg.location = tgt
    c = bpy.data.objects.new(n, bpy.data.cameras.new(n)); sc.collection.objects.link(c)
    c.location = loc; c.data.lens = lens; c.data.clip_start = 1
    k = c.constraints.new('TRACK_TO'); k.target = tg; k.track_axis = 'TRACK_NEGATIVE_Z'; k.up_axis = 'UP_Y'
    return c
sc.camera = camera("Камера: наискосок", (75, -120, 70), (0, 0, 5))
camera("Камера: спереди (слой А)", (0, -170, 5), (0, 0, 5))
sun = bpy.data.objects.new("Солнце", bpy.data.lights.new("Солнце", "SUN")); sun.data.energy = 3
sun.rotation_euler = (math.radians(40), math.radians(10), math.radians(30)); sc.collection.objects.link(sun)
sc.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=OUT); print("saved", OUT)
