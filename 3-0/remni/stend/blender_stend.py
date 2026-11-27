# Сцена стенда одной ленты (ремень 3 мм). Запуск: blender -b -P blender_stend.py  → stend_remen.blend
import bpy, bmesh, os, math
H = os.path.dirname(os.path.abspath(__file__)); A = os.path.join(H, "asm")
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.unit_settings.scale_length = 0.001; sc.unit_settings.length_unit = 'MILLIMETERS'
W, XM, XC, RP, TB = 3.0, 13.0, 22.0, 2.54, 0.9
Z_D1, T_FL = 25.2, 0.6
Z0, Z1 = Z_D1 + T_FL, Z_D1 + T_FL + W


def mat(n, c):
    m = bpy.data.materials.new(n); m.diffuse_color = c; return m


def imp(n, name, c, parent=None):
    bpy.ops.wm.stl_import(filepath=os.path.join(A, n + ".stl")); o = bpy.context.selected_objects[0]; o.name = name
    o.data.materials.append(mat(name, c))
    if parent: o.parent = parent
    return o


def box(n, x0, x1, y0, y1, z0, z1, m, p=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)); o = bpy.context.object
    o.scale = (x1 - x0, y1 - y0, z1 - z0); bpy.ops.object.transform_apply(scale=True); o.name = n; o.data.materials.append(m)
    if p: o.parent = p; o.matrix_parent_inverse = p.matrix_world.inverted()
    return o


def arc(n, rc, t, x, a0, a1, m, seg=16):
    me = bpy.data.meshes.new(n); bm = bmesh.new(); ring = []
    for i in range(seg + 1):
        a = math.radians(a0 + (a1 - a0) * i / seg)
        for r in (rc, rc + t):
            for z in (Z0, Z1):
                ring.append(bm.verts.new((x + r * math.cos(a), r * math.sin(a), z)))
    for i in range(seg):
        q = [ring[4 * i + k] for k in range(4)]; w = [ring[4 * (i + 1) + k] for k in range(4)]
        for a_, b_ in ((0, 1), (1, 3), (3, 2), (2, 0)):
            bm.faces.new((q[a_], q[b_], w[b_], w[a_]))
    bm.to_mesh(me); o = bpy.data.objects.new(n, me); sc.collection.objects.link(o); o.data.materials.append(m); return o


imp("osnova", "основа (мотор крепится М2 через стакан)", (0.6, 0.62, 0.66, 1))
imp("paluba", "палуба на ножках (оси роликов — филамент 1.75)", (0.55, 0.6, 0.7, 1))
imp("motor", "мотор GB1806 со стаканом", (0.1, 0.1, 0.12, 1))
imp("relsa", "рельс тележки", (0.45, 0.48, 0.52, 1))
ved = imp("ved", "ведущий ролик на роторе", (0.95, 0.8, 0.2, 1))
rl = imp("rol_l", "концевой ролик (стол 126)", (0.85, 0.85, 0.87, 1)); rr = imp("rol_r", "концевой ролик (стол 126)", (0.85, 0.85, 0.87, 1))
for o in (ved, rl, rr):                                   # ось вращения — по центру ролика
    cx = XM if o is ved else (-XC if o is rl else XC)
    o.data.transform(__import__("mathutils").Matrix.Translation((-cx, 0, 0))); o.location.x = cx
M_B = mat("ремень TPU (схема)", (0.95, 0.75, 0.1, 1))
for sy in (-1, 1):
    box("ветвь ремня", -XC, XC, *sorted((sy * RP, sy * (RP + TB))), Z0, Z1, M_B)
arc("петля", RP, TB, XC, -90, 90, M_B); arc("петля", RP, TB, -XC, 90, 270, M_B)
cart = imp("tel", "тележка стенда", (0.25, 0.45, 0.85, 1))
for sx in (-1, 1):                                        # ушки-пилы на спинке верхней ветви — едут с тележкой
    g0 = 0.75 + 0.1
    box("ушко-пила", *sorted((sx * g0, sx * (g0 + 3.0))), RP + TB, RP + TB + 1.5, Z0, Z1, M_B, cart)
for f in range(1, 241, 3):
    s = 20.0 * math.sin(2 * math.pi * (f - 1) / 120)
    sc.frame_set(f)
    cart.location.x = s; cart.keyframe_insert("location", index=0, frame=f)
    for o in (ved, rl, rr):
        o.rotation_euler.z = -s / RP; o.keyframe_insert("rotation_euler", index=2, frame=f)
sc.frame_start, sc.frame_end = 1, 240; sc.frame_set(1)
tg = bpy.data.objects.new("ц", None); sc.collection.objects.link(tg); tg.location = (0, 0, 18)
cam = bpy.data.objects.new("Камера", bpy.data.cameras.new("Камера")); sc.collection.objects.link(cam); cam.location = (55, -75, 70); cam.data.clip_start = 1
k = cam.constraints.new('TRACK_TO'); k.target = tg; k.track_axis = 'TRACK_NEGATIVE_Z'; k.up_axis = 'UP_Y'; sc.camera = cam
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(H, "stend_remen.blend")); print("saved")
