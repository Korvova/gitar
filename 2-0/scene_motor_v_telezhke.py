# Концепт: гриф 52×25 с 4 поперечными карманами, в каждом тележка с гимбал-мотором Ø20×10 (вал вдоль грифа),
# шестерня m0.5 z12 (Ø6) на валу катится по рейке на дне кармана. Бока и верх карманов открыты.
import bpy, math, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Гриф_4_тележки_моторы.blend")
W, LEN = 52.0, 110.0
ST = [16, 42, 67, 91]                 # станции пальцев (V позиция), шаг 26/25/24
POCK = 16.0                           # карман вдоль грифа
FLOOR = 2.0
ZM = 12.5                             # ось мотора
MD, MT = 20.0, 10.0                   # мотор Ø20 × 10
PR = 3.0                              # шестерня: делительный радиус (m0.5 z12)
TRAVEL = 22.0
FR = 140

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

M_NECK = mat("гриф", (0.85, 0.78, 0.65, 1), 0.55)
M_RACK = mat("рейка", (0.55, 0.55, 0.6, 1))
M_MOT = mat("мотор Ø20", (0.12, 0.12, 0.14, 1))
M_GEAR = mat("шестерня Ø6", (0.85, 0.65, 0.2, 1))
M_CART = mat("тележка", (0.3, 0.55, 0.85, 1))
M_LZ = mat("ложе", (0.95, 0.72, 0.30, 1))

def box(name, x0, x1, y0, y1, z0, z1, m, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x0+x1)/2, (y0+y1)/2, (z0+z1)/2))
    o = bpy.context.object; o.name = name; o.scale = (x1-x0, y1-y0, z1-z0)
    bpy.ops.object.transform_apply(scale=True); o.data.materials.append(m)
    if parent: o.parent = parent
    return o

def cyl_y(name, r, y0, y1, x, z, m, parent=None, verts=48):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=y1-y0, location=(x, (y0+y1)/2, z), rotation=(math.pi/2, 0, 0))
    o = bpy.context.object; o.name = name; o.data.materials.append(m)
    if parent: o.parent = parent
    return o

# ---- гриф: дно + рёбра между карманами ----
box("гриф: дно", -W/2, W/2, 0, LEN, 0, FLOOR, M_NECK)
edges = [0]
for s in ST: edges += [s - POCK/2, s + POCK/2]
edges.append(LEN)
for i in range(0, len(edges), 2):
    box("гриф: ребро %d" % (i//2), -W/2, W/2, edges[i], edges[i+1], FLOOR, 25.0, M_NECK)
for i, s in enumerate(ST):                       # полки-направляющие тележки в рёбрах (паз сверху)
    for sy in (-1, 1):
        y0, y1 = sorted((s + sy*POCK/2, s + sy*(POCK/2 + 1.2)))
        box("паз тележки %d" % i, -W/2, W/2, y0, y1, 21.0, 22.0, M_RACK)

carts = []
for i, s in enumerate(ST):
    # мотор: Y s-8 .. s+2, вал и шестерня Y s+2.3 .. s+5.3, рейка под шестерней
    y_m0, y_m1 = s - 7.5, s + 2.5
    y_g0, y_g1 = s + 3.0, s + 6.0
    rk = box("рейка %d" % i, -W/2, W/2, y_g0 - 0.3, y_g1 + 0.3, FLOOR, ZM - PR - 0.6, M_RACK)
    for k in range(-26, 27):                      # зубья рейки, шаг π·m ≈ 1.57
        x = k * math.pi * 0.5
        if abs(x) < W/2 - 0.5:
            t = box("зуб", x - 0.35, x + 0.35, y_g0 - 0.3, y_g1 + 0.3, ZM - PR - 0.6, ZM - PR + 0.5, M_RACK)
            t.parent = rk
    # тележка — пустышка, от неё всё остальное
    e = bpy.data.objects.new("тележка %d (палец %s)" % (i, ["указательный", "средний", "безымянный", "мизинец"][i]), None)
    sc.collection.objects.link(e); e.location = (0, 0, 0)
    cyl_y("мотор %d" % i, MD/2, y_m0, y_m1, 0, ZM, M_MOT, e)
    cyl_y("вал %d" % i, 1.5, y_m1, y_g1 + 0.5, 0, ZM, M_RACK, e, 16)
    g = cyl_y("шестерня %d" % i, PR + 0.5, y_g0, y_g1, 0, ZM, M_GEAR, e, 12)   # 12 граней — видно вращение
    box("стенка за мотором %d" % i, -11, 11, y_m0 - 1.5, y_m0, ZM - 6, 24.8, M_CART, e)
    box("крыша %d" % i, -11, 11, s - POCK/2 - 1.0, s + POCK/2 + 1.0, 22.2, 24.8, M_CART, e)  # заходит лапками в пазы рёбер
    lz = box("ложе %d" % i, -11, 11, s - 7.5, s + 7.5, 24.8, 26.3, M_LZ, e)
    for sx in (-1, 1):
        box("борт ложа", sx*11 - (1.5 if sx > 0 else 0), sx*11 + (0 if sx > 0 else 1.5), s - 7.5, s + 7.5, 26.3, 31.0, M_LZ, e)
    carts.append((e, g))

# ---- анимация: «паучок» — каждая тележка своим ритмом ----
for f in range(1, FR + 1):
    t = (f - 1) / (FR - 1)
    for i, (e, g) in enumerate(carts):
        x = TRAVEL * math.sin(2 * math.pi * (2 * t + i * 0.25))
        e.location.x = x; e.keyframe_insert("location", index=0, frame=f)
        g.rotation_euler = (math.pi/2, -x / PR, 0); g.keyframe_insert("rotation_euler", frame=f)

def camera(n, loc, tgt, lens=35):
    t = bpy.data.objects.new(n + " цель", None); sc.collection.objects.link(t); t.location = tgt
    c = bpy.data.objects.new(n, bpy.data.cameras.new(n)); sc.collection.objects.link(c)
    c.location = loc; c.data.lens = lens; c.data.clip_start = 1
    k = c.constraints.new('TRACK_TO'); k.target = t; k.track_axis = 'TRACK_NEGATIVE_Z'; k.up_axis = 'UP_Y'
    return c
sc.camera = camera("Камера: наискосок", (150, -70, 120), (0, 55, 10))
camera("Камера: сверху", (0, 55, 260), (0, 55, 0))
camera("Камера: с торца", (0, -160, 15), (0, 55, 15), 50)
sun = bpy.data.objects.new("Солнце", bpy.data.lights.new("Солнце", "SUN")); sun.data.energy = 3
sun.rotation_euler = (math.radians(30), math.radians(15), math.radians(30)); sc.collection.objects.link(sun)
sc.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=OUT); print("saved", OUT)
