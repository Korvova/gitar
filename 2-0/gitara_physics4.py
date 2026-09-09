# -*- coding: utf-8 -*-
"""ФИЗИКА ЧЕТЫРЁХ СТАНЦИЙ ГРИФА (Bullet): секция-1 + секции 2–3 + хребет.
Проверка цепочки кривошип → лента → плечо → штырь в вилке тележки для всех
четырёх этажей разом, до печати столов 31–36.

Рецепт стенда (palka_physics.py): неподвижное — MESH из STL (стабильно),
подвижное — COMPOUND из выпуклых примитивов по параметрам генераторов
(меш-меш у Bullet взрывается), узлы штырь-в-дырке — GENERIC-связки с люфтом
±0.5 при включённых контактах, кривошипы кинематические.
Упрощение: лента этажа (голова + 2 ext + хвост) — ОДНО жёсткое тело:
защёлки стыков считаем сцепленными, их высокие штырьки в модели есть.

Запуск:
  blender -b -P 2-0/gitara_physics4.py -- [south|north] [кадров]
    south — вилки тележек открыты на юг (как в инструкции grif.html),
    north — вилки развёрнуты на север (к оси плеча).
Пишет: 2-0/Гитара_физика4_<вариант>.blend (кэш запечён, пробел — смотреть),
       wiki/img/sim4_<вариант>_*.jpg, отчёт по ходу/дрейфу тележек в stdout.
"""
import sys, os, math, bpy
sys.stdout.reconfigure(line_buffering=True)
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
FORK = argv[0] if argv else "south"
LIVE = "live" in argv                 # ручная сцена: без ключей, без запекания
NOCARTS = "nocarts" in argv           # без тележек: штыри плеч ходят свободно
NFR = int(argv[1]) if len(argv) > 1 and argv[1].isdigit() else (100000 if LIVE else 440)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "2-0", "Print", "Print")
IMG = os.path.join(ROOT, "wiki", "img")

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene

# ---- параметры из gitara_sec1.py / gitara_deka.py ----
CARTS_Y = [18, 34, 50, 66]
AXES_Y = [y + 52 for y in CARTS_Y]
LANE = 10
Z_FLOOR = [3, 8.4, 13.8, 19.2]
Z_DECK, DECK_T = 23, 3
MY = [505, 555, 605, 668]
R_PIN = next((float(a[4:]) for a in argv if a.startswith('rpin')), 4.3)   # палец кривошипа
SLOTX = next((float(a[5:]) for a in argv if a.startswith('slotx')), 7.5)  # полуширина паза вилки ленты
COMB_Y = (535, 585, 635)
SETTLE = 40                      # кадров покоя перед движением
PERIOD = 200                     # кадров на цикл качания
AMP = math.radians(next((float(a[3:]) for a in argv if a.startswith("amp")), 62))   # сектор: amp80 в аргументах


def mat(name, rgba):
    m = bpy.data.materials.new(name)
    m.diffuse_color = rgba
    return m

M = {"static": mat("static", (0.75, 0.72, 0.68, 1)), "arm": mat("arm", (0.25, 0.45, 0.8, 1)),
     "band": mat("band", (0.85, 0.35, 0.2, 1)), "cart": mat("cart", (0.95, 0.95, 0.9, 1)),
     "crank": mat("crank", (0.85, 0.7, 0.2, 1)), "tray": mat("tray", (0.6, 0.62, 0.66, 1))}


def rb_common(ob):
    ob.rigid_body.friction = 0.2
    ob.rigid_body.restitution = 0.0
    ob.rigid_body.linear_damping = 0.9
    ob.rigid_body.angular_damping = 0.9
    ob.rigid_body.use_deactivation = False


def set_rb(ob, typ, shape):
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.ops.rigidbody.object_add()
    ob.rigid_body.type = typ
    ob.rigid_body.mass = 0.05
    ob.rigid_body.collision_shape = shape
    ob.rigid_body.mesh_source = 'BASE'
    rb_common(ob)
    ob.select_set(False)


def static_stl(name, stl, loc, matn="static"):
    before = set(bpy.data.objects)
    bpy.ops.wm.stl_import(filepath=os.path.join(SRC, stl + ".stl"))
    ob = (set(bpy.data.objects) - before).pop()
    ob.name = name
    ob.location = loc
    ob.data.materials.append(M[matn])
    set_rb(ob, 'PASSIVE', 'MESH')
    return ob

# ---- rigid body мир ----
bpy.ops.rigidbody.world_add()
sc.rigidbody_world.substeps_per_frame = 250
sc.rigidbody_world.solver_iterations = 250
sc.frame_start, sc.frame_end = 1, NFR
sc.rigidbody_world.point_cache.frame_end = NFR

# ---- НЕПОДВИЖНОЕ из STL ----
ST = {}
ST["p0"] = static_stl("П0_дно", "gs1_p0_base", (0, 0, 0))
for k in (1, 2, 3):
    ST[f"p{k}"] = static_stl(f"П{k}_межэтажка", f"gs1_p{k}_mid", (0, 0, Z_FLOOR[k] - 1.6))
ST["deck"] = static_stl("П4_палуба", "gs1_p4_deck", (0, 0, Z_DECK))
for tag, y0 in (("gs2", 160), ("gs3", 320)):
    ST[tag] = static_stl(f"{tag}_дно", f"{tag}_base", (0, y0, 0))
    ST[tag + "f"] = static_stl(f"{tag}_фретборд", f"{tag}_fret", (0, y0, Z_DECK))
    for k, zf in enumerate(Z_FLOOR):
        ST[f"{tag}t{k}"] = static_stl(f"{tag}_рейка{k}", "gs2_tray", (0, y0, zf - 1.6), "tray")
ST["dk1"] = static_stl("Д1_хребет", "gdk1_base", (0, 480, 0))
ST["dk2"] = static_stl("Д2_хребет", "gdk2_base", (0, 640, 0))
for i, yg in enumerate(COMB_Y):
    ST[f"comb{i}"] = static_stl(f"гребёнка{i}", "gdk_comb", (0, yg, 0))

# ---- ПОДВИЖНОЕ: compound из примитивов (мировые координаты) ----
CHILD = []


def _child(part, ob):
    ob.display_type = 'SOLID'
    ob.hide_render = False
    if part.data.materials:
        ob.data.materials.append(part.data.materials[0])
    ob.parent = part
    ob.matrix_parent_inverse = part.matrix_world.inverted()
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.ops.rigidbody.object_add()
    ob.rigid_body.type = 'ACTIVE'
    ob.rigid_body.use_margin = True
    ob.rigid_body.collision_margin = 0.01
    rb_common(ob)
    ob.select_set(False)
    CHILD.append(ob)


def c_box(part, x0, x1, y0, y1, z0, z1):
    bpy.ops.mesh.primitive_cube_add(size=1)
    ob = bpy.context.object
    ob.dimensions = (x1 - x0, y1 - y0, z1 - z0)
    ob.location = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    bpy.context.view_layer.update()
    _child(part, ob)
    ob.rigid_body.collision_shape = 'BOX'


def c_cyl(part, cx, cy, z0, z1, r):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=z1 - z0, vertices=24)
    ob = bpy.context.object
    ob.location = (cx, cy, (z0 + z1) / 2)
    bpy.context.view_layer.update()
    _child(part, ob)
    ob.rigid_body.collision_shape = 'CYLINDER'


def c_ring(part, cx, cy, z0, z1, rin, rout):
    rc = (rin + rout) / 2
    w = 2 * rc * math.tan(math.pi / 8) + 0.2
    for k in range(8):
        a = k * math.pi / 4
        bpy.ops.mesh.primitive_cube_add(size=1)
        ob = bpy.context.object
        ob.dimensions = (rout - rin, w, z1 - z0)
        ob.location = (cx + rc * math.cos(a), cy + rc * math.sin(a), (z0 + z1) / 2)
        ob.rotation_euler = (0, 0, a)
        bpy.context.view_layer.update()
        _child(part, ob)
        ob.rigid_body.collision_shape = 'BOX'


def body(name, origin, matn, mass=0.05):
    """Пустой родитель-тело с origin в указанной точке (центр масс)."""
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    sc.collection.objects.link(ob)
    ob.location = origin
    bpy.context.view_layer.update()
    set_rb(ob, 'ACTIVE', 'COMPOUND')
    ob.rigid_body.mass = mass
    ob.data.materials.append(M[matn])
    return ob

ARM, BAND, CART, CRANK = [], [], [], []
for k in range(4):
    zA = Z_FLOOR[k] + 0.2               # низ плеча и ленты на этаже k
    ay = AXES_Y[k]
    # --- плечо-кулиса ---
    a = body(f"плечо{k}", (0, ay - 26, zA + 0.8), "arm")
    c_ring(a, 0, ay, zA, zA + 1.6, 3.0, 5.0)                      # диск оси (дырка Ø6)
    c_box(a, -2.5, 2.5, ay - 52, ay - 3, zA, zA + 1.6)            # длинное плечо
    c_cyl(a, 0, ay - 52, zA, zA + 1.6, 3.5)                        # пад типа
    c_box(a, 5, LANE - 4, ay - 2.5, ay + 2.5, zA, zA + 1.6)        # короткое плечо
    c_cyl(a, LANE, ay, zA, zA + 1.6, 4.0)                          # пад угла-1
    c_cyl(a, LANE, ay, zA + 1.6, zA + 3.4, 2.5)                    # стад под кольцо ленты
    pin_h = (Z_DECK + DECK_T + 4) - (zA + 1.6)
    c_cyl(a, 0, ay - 52, zA + 1.6, zA + 1.6 + pin_h, 2.5)          # штырь в вилку тележки
    ARM.append(a)
    # --- лента этажа целиком: кольцо + ступень + тело + штырьки защёлок + вилка ---
    yEnd = MY[k] + 10
    b = body(f"лента{k}", (LANE, (ay + yEnd) / 2, zA + 0.8), "band", mass=0.08)
    c_ring(b, LANE, ay, zA + 1.8, zA + 3.4, 3.0, 5.5)              # кольцо на стаде
    c_box(b, LANE - 4, LANE + 4, ay + 3, ay + 16, zA + 1.8, zA + 3.4)   # ступень
    c_box(b, LANE - 4, LANE + 4, ay + 12, ay + 16, zA, zA + 3.4)   # соединитель
    c_box(b, LANE - 4, LANE + 4, ay + 12, MY[k] - 6, zA, zA + 1.6)  # тело до вилки
    for yp in (166.5, 326.5, 486.5):                               # высокие штырьки стыков
        c_cyl(b, LANE, yp, zA + 0.8, zA + 3.2, 1.5)
    c_box(b, LANE - SLOTX - 2, LANE - SLOTX, MY[k] - 6, MY[k] + 10, zA, zA + 1.6)   # вилка: щёки
    c_box(b, LANE + SLOTX, LANE + SLOTX + 2, MY[k] - 6, MY[k] + 10, zA, zA + 1.6)
    c_box(b, LANE - SLOTX, LANE + SLOTX, MY[k] - 6, MY[k] - 3, zA, zA + 1.6)    # юг паза
    c_box(b, LANE - SLOTX, LANE + SLOTX, MY[k] + 3, MY[k] + 10, zA, zA + 1.6)   # север паза
    BAND.append(b)
    # --- тележка: 12×14×6 с вилкой (паз 6 по X, глубина: юг 7.1 / север 3) ---
    cy = CARTS_Y[k]
    zc = Z_DECK + DECK_T + 0.15          # зазор к палубе: ноль = взрыв
    if NOCARTS:
        CART.append(None)
        dz0 = Z_FLOOR[k] + 1.8 + 0.25
        r = body(f"кривошип{k}", (LANE, MY[k], dz0 + 1.25), "crank")
        c_cyl(r, LANE, MY[k], dz0, dz0 + 2.5, 7.0)
        c_cyl(r, LANE + R_PIN, MY[k], dz0 - 1.7, dz0, 2.5)
        r.rigid_body.kinematic = True
        CRANK.append(r)
        continue
    c = body(f"тележка{k}", (0, cy, zc + 3), "cart", mass=0.05)
    sgn = 1 if FORK == "south" else -1        # север = вилка развёрнута на 180°
    c_box(c, -6, -3, cy - 7, cy + 7, zc, zc + 6)
    c_box(c, 3, 6, cy - 7, cy + 7, zc, zc + 6)
    if sgn == 1:
        c_box(c, -3, 3, cy + 3, cy + 7, zc, zc + 6)      # закрытый торец на севере
    else:
        c_box(c, -3, 3, cy - 7, cy - 3, zc, zc + 6)      # закрытый торец на юге
    CART.append(c)
    # --- кривошип (кинематический) ---
    dz0 = Z_FLOOR[k] + 1.8 + 0.25         # диск над лентой с зазором
    r = body(f"кривошип{k}", (LANE, MY[k], dz0 + 1.25), "crank")
    c_cyl(r, LANE, MY[k], dz0, dz0 + 2.5, 7.0)
    c_cyl(r, LANE + R_PIN, MY[k], dz0 - 1.7, dz0, 2.5)             # палец вниз в вилку
    r.rigid_body.kinematic = True
    CRANK.append(r)

# ---- узлы: GENERIC-люфты (контакты остаются) ----
PLAY = next((float(a[4:]) for a in argv if a.startswith('play')), 0.5)   # люфт узлов Ø5/Ø6 = ±0.5
def slop(name, x, y, z, a, b, zlo, zhi, lin=None):
    lin = PLAY if lin is None else lin
    e = bpy.data.objects.new(name, None)
    e.empty_display_size = 3
    e.location = (x, y, z)
    sc.collection.objects.link(e)
    bpy.context.view_layer.objects.active = e
    e.select_set(True)
    bpy.ops.rigidbody.constraint_add()
    c = e.rigid_body_constraint
    c.type = 'GENERIC'
    c.object1, c.object2 = a, b
    c.disable_collisions = False
    for ax in ('x', 'y'):
        setattr(c, 'use_limit_lin_' + ax, True)
        setattr(c, 'limit_lin_' + ax + '_lower', -lin)
        setattr(c, 'limit_lin_' + ax + '_upper', lin)
    c.use_limit_lin_z = True
    c.limit_lin_z_lower, c.limit_lin_z_upper = zlo, zhi
    for ax in ('x', 'y'):
        setattr(c, 'use_limit_ang_' + ax, True)
        setattr(c, 'limit_ang_' + ax + '_lower', -math.radians(5))
        setattr(c, 'limit_ang_' + ax + '_upper', math.radians(5))
    c.use_limit_ang_z = False
    e.select_set(False)
    return c

for k in range(4):
    zA = Z_FLOOR[k] + 0.2
    ay = AXES_Y[k]
    plate = ST["p0"] if k == 0 else ST[f"p{k}"]
    slop(f"j_ось{k}", 0, ay, zA + 0.8, plate, ARM[k], -0.1, 0.3)
    slop(f"j_кольцо{k}", LANE, ay, zA + 2.6, ARM[k], BAND[k], -0.1, 1.6)
    p = slop(f"j_палец{k}", LANE + R_PIN, MY[k], Z_FLOOR[k] + 0.9, BAND[k], CRANK[k], -2.5, 0.5)
    p.limit_lin_x_lower, p.limit_lin_x_upper = -(SLOTX - 2), SLOTX - 2   # паз вилки ленты минус палец
    p.limit_lin_y_lower, p.limit_lin_y_upper = -0.6, 0.6      # ширина паза 6 минус палец 5
    if NOCARTS:
        continue
    s = slop(f"j_вилка{k}", 0, CARTS_Y[k], Z_DECK + DECK_T + 3, CART[k], ARM[k], -6.0, 0.5)
    s.limit_lin_x_lower, s.limit_lin_x_upper = -0.6, 0.6      # паз тележки 6 минус штырь 5
    if FORK == "south":            # паз открыт на юг: на север стенка (+3 минус штырь)
        s.limit_lin_y_lower, s.limit_lin_y_upper = -7.0, 0.5
    else:                          # паз открыт на север: щёки держат до края тележки
        s.limit_lin_y_lower, s.limit_lin_y_upper = -0.5, 7.0
    ch = slop(f"j_канал{k}", 0, CARTS_Y[k], Z_DECK + DECK_T + 3, ST["deck"], CART[k], -0.2, 0.6)
    ch.limit_lin_x_lower, ch.limit_lin_x_upper = -25, 25       # ход тележки
    ch.limit_lin_y_lower, ch.limit_lin_y_upper = -4, 4         # слабина канала
    for ax in ('x', 'y'):
        setattr(ch, 'limit_ang_' + ax + '_lower', -math.radians(3))
        setattr(ch, 'limit_ang_' + ax + '_upper', math.radians(3))

if LIVE:
    # ручная сцена: кривошипы в нуле, крутит аддон gitar_stend4_addon.py
    # (N-панель «Стенд»), физика считается вживую при проигрывании
    sc.rigidbody_world.substeps_per_frame = 120
    sc.rigidbody_world.solver_iterations = 120
    sc.render.fps = 30
    for r in CRANK:
        r.rotation_euler = (0, 0, 0)
    bpy.ops.object.select_all(action='DESELECT')
    tag = FORK + ("_r%.1f" % R_PIN if R_PIN != 4.3 else "") + ("_bezteleg" if NOCARTS else "")
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, "2-0", "Гитара_физика4_ручная_%s.blend" % tag))
    print("PHYS4 LIVE OK", FORK)
    sys.exit(0)

# ---- кривошипы: покой, потом качание сектором со сдвигом фаз ----
for k, r in enumerate(CRANK):
    # каждая станция стартует из нуля, со сдвигом на четверть периода —
    # без стартового преднатяга, но все четыре едут одновременно
    for fr in range(1, NFR + 1):
        t = max(0, fr - SETTLE - k * PERIOD // 4)
        r.rotation_euler = (0, 0, AMP * math.sin(2 * math.pi * t / PERIOD))
        r.keyframe_insert("rotation_euler", frame=fr)

# ---- запекание и отчёт ----
bpy.ops.ptcache.bake_all(bake=True)
rep = {k: {"x": [], "y": [], "yaw": [], "bz": [], "az": []} for k in range(4)}
for fr in range(SETTLE, NFR + 1):
    sc.frame_set(fr)
    for k in range(4):
        if NOCARTS:
            tip = ARM[k].matrix_world @ Vector((0, -26, 0))   # штырь = конец плеча
            m = ARM[k].matrix_world
            rep[k]["x"].append(tip.x)
            rep[k]["y"].append(tip.y - CARTS_Y[k])
        else:
            m = CART[k].matrix_world
            rep[k]["x"].append(m.translation.x)
            rep[k]["y"].append(m.translation.y - CARTS_Y[k])
        ax = m.to_3x3().col[0]
        rep[k]["yaw"].append(math.degrees(math.atan2(ax.y, ax.x)))
        rep[k].setdefault("tilt", []).append(math.degrees(math.acos(max(-1, min(1, m.to_3x3().col[2].z)))))
        rep[k]["bz"].append(BAND[k].matrix_world.translation.z - (Z_FLOOR[k] + 1.0))
        rep[k]["az"].append(ARM[k].matrix_world.translation.z - (Z_FLOOR[k] + 1.0))
print("=" * 70)
print("ОТЧЁТ вилки=%s, сектор ±%.0f°, палец r%.1f, паз ленты ±%.1f, люфт ±%.2f, кадров %d" % (FORK, math.degrees(AMP), R_PIN, SLOTX, PLAY, NFR))
print(("ШТЫРЬ" if NOCARTS else "ТЕЛЕЖКА") + ": ст  ход X мм (min..max)  дрейф/дуга Y мм  yaw° max  наклон° max  лента dz  плечо dz")
for k in range(4):
    R = rep[k]
    print("%d   %6.1f .. %5.1f  = %4.1f   %5.1f .. %4.1f   %5.1f   %5.1f   %+.2f/%+.2f  %+.2f/%+.2f" % (
        k, min(R["x"]), max(R["x"]), max(R["x"]) - min(R["x"]), min(R["y"]), max(R["y"]),
        max(abs(v) for v in R["yaw"]), max(R["tilt"]), min(R["bz"]), max(R["bz"]), min(R["az"]), max(R["az"])))
    # траектория станции по кадрам — видно, где ломается
    for fr_i in range(0, len(R["x"]), 25):
        print("      кадр %3d: x=%6.1f y=%5.1f yaw=%5.1f tilt=%5.1f" % (
            SETTLE + fr_i, R["x"][fr_i], R["y"][fr_i], R["yaw"][fr_i], R["tilt"][fr_i]))
print("=" * 70)

# ---- картинки: общий вид сверху и крупно зона тележек ----
def shot(path, lo, hi, fr, view="top"):
    sc.frame_set(fr)
    center, size = (lo + hi) / 2, hi - lo
    d = {"top": Vector((0, -0.001, 1)), "iso": Vector((1, -1.2, 0.9))}[view].normalized()
    cd = bpy.data.cameras.new("cam"); cd.type = 'ORTHO'
    cam = bpy.data.objects.new("cam", cd); sc.collection.objects.link(cam)
    cam.location = center + d * (size.length * 2)
    cam.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    cd.clip_start, cd.clip_end = 1, size.length * 10
    sc.camera = cam
    bpy.context.view_layer.update()
    inv = cam.matrix_world.inverted()
    xs, ys = [], []
    for i in range(8):
        c = Vector(((lo.x, hi.x)[i & 1], (lo.y, hi.y)[(i >> 1) & 1], (lo.z, hi.z)[(i >> 2) & 1]))
        p = inv @ c; xs.append(p.x); ys.append(p.y)
    sc.render.resolution_x, sc.render.resolution_y = 1600, 1000
    cd.ortho_scale = max(max(xs) - min(xs), (max(ys) - min(ys)) * 1.6) * 1.05
    cam.location += cam.matrix_world.to_3x3() @ Vector(((max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2, 0))
    sc.render.engine = 'BLENDER_WORKBENCH'
    sh = sc.display.shading
    sh.light, sh.color_type, sh.show_object_outline, sh.show_cavity = 'STUDIO', 'MATERIAL', True, True
    sc.render.image_settings.file_format = 'JPEG'; sc.render.image_settings.quality = 88
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam); bpy.data.cameras.remove(cd)

os.makedirs(IMG, exist_ok=True)
ST["deck"].hide_render = True                 # палубу и фретборды снимаем — видно механику
ST["gs2f"].hide_render = True; ST["gs3f"].hide_render = True
shot(os.path.join(IMG, "sim4_%s_top.jpg" % FORK), Vector((-30, 0, 0)), Vector((30, 150, 30)), SETTLE + PERIOD // 4 + 3 * PERIOD // 4)
shot(os.path.join(IMG, "sim4_%s_carts.jpg" % FORK), Vector((-30, 0, 0)), Vector((30, 150, 32)), SETTLE + PERIOD // 4, "iso")
shot(os.path.join(IMG, "sim4_%s_deka.jpg" % FORK), Vector((-30, 480, 0)), Vector((30, 690, 30)), SETTLE + PERIOD // 4, "iso")
ST["deck"].hide_render = False; ST["gs2f"].hide_render = False; ST["gs3f"].hide_render = False

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, "2-0", "Гитара_физика4_%s.blend" % (FORK + ("_bezteleg" if NOCARTS else ""))))
print("PHYS4 OK", FORK)
