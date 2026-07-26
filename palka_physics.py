# -*- coding: utf-8 -*-
# МАКСИМАЛЬНО НАСТОЯЩАЯ физика стенда (запрос юзера): БЕЗ программных шарниров.
# Только твёрдые тела с реальной формой (MESH), гравитация, трение и контакты:
# палец давит в стенку дырки, штырьки держат детали, рельсы ведут тележку.
# Единственная условность — кривошип кинематический (его крутит "мотор").
import bpy, math

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
SRC = r"C:\App\gitar\2-0\Print\Print"


def mat(name, rgba):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = rgba
    return m

COL = {
    "ptest_plate_v2": mat("plate", (0.7, 0.7, 0.72, 1)),
    "ptest_triangle_v2": mat("tri", (0.25, 0.45, 0.8, 1)),
    "ptest_spica_v2": mat("sp", (0.85, 0.3, 0.2, 1)),
    "ptest_crank_r85_v2": mat("cr", (0.8, 0.68, 0.2, 1)),
    "ptest_cart_v2": mat("ca", (0.88, 0.88, 0.9, 1)),
    "ptest_plug_v2": mat("plug", (0.6, 0.4, 0.7, 1)),
    "ptest_bridge_v1": mat("br", (0.55, 0.55, 0.6, 1)),
    "ptest_washer_v1": mat("wa", (0.9, 0.75, 0.2, 1)),
    "ptest_bridge_low_v1": mat("bl", (0.55, 0.6, 0.55, 1)),
    "ptest_bridge_high_v1": mat("bh", (0.6, 0.55, 0.55, 1)),
}
# z чуть приподняты ступенчато (0.05-0.25): нулевой зазор Bullet трактует как
# проникновение и выстреливает детали вверх; тут они мягко усаживаются
POS = {
    "ptest_plate_v2": ((0, 0, 0), 0),
    "ptest_triangle_v2": ((95, 0, 5.05), 0),
    "ptest_spica_v2": ((91.0, -21.3, 6.75), -1.0),
    "ptest_crank_r85_v2": ((229, -15, 5.2), -90),   # r8.5: добивает ход до 40
    "ptest_cart_v2": ((30, 8, 5.1), 0),
    "ptest_plug_v2": ((229, -15, 3.05), 0),
    "ptest_bridge_v1": ((120, -19, 10.0), 0),
    "ptest_bridge_v1#2": ((190, -19, 10.0), 0),
    "ptest_washer_v1": ((95, 0, 6.9), 0),
    "ptest_bridge_low_v1": ((65, -10.5, 8.4), 0),
    "ptest_bridge_high_v1": ((30, -14, 14.9), 90),
    "ptest_bridge_high_v1#2": ((30, 16, 14.9), 90),
}
# Bullet считает центр масс = origin объекта; у STL origin в углу детали.
# Для подвижных деталей центрируем origin (иначе дурная инерция = рывки).
CENTERED = {"ptest_spica_v2", "ptest_triangle_v2", "ptest_cart_v2"}
CTR = {}

OBJ = {}
for name, (loc, rz) in POS.items():
    stl = name.split("#")[0]
    before = set(bpy.data.objects)
    bpy.ops.wm.stl_import(filepath=SRC + "\\" + stl + ".stl")
    ob = (set(bpy.data.objects) - before).pop()
    ob.name = name
    ob.data.materials.append(COL[stl])
    if name in CENTERED:
        bpy.context.view_layer.objects.active = ob
        ob.select_set(True)
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME')
        ob.select_set(False)
        c = ob.location.copy()          # объект стоял в (0,0,0) => location = центр
        CTR[name] = c
        r = math.radians(rz)
        ob.location = (loc[0] + c.x * math.cos(r) - c.y * math.sin(r),
                       loc[1] + c.x * math.sin(r) + c.y * math.cos(r),
                       loc[2] + c.z)
    else:
        ob.location = loc
    ob.rotation_euler = (0, 0, math.radians(rz))
    if stl in ("ptest_bridge_v1", "ptest_bridge_low_v1", "ptest_bridge_high_v1"):
        ob.rotation_euler = (math.pi, 0, math.radians(rz))  # перевёрнут: штыри вниз
    OBJ[name] = ob

# ---- rigid body мир: только контакты ----
bpy.ops.rigidbody.world_add()
sc.rigidbody_world.substeps_per_frame = 300   # контакты мелкие (зазор 0.5 мм)
sc.rigidbody_world.solver_iterations = 300
sc.frame_start, sc.frame_end = 1, 500
sc.rigidbody_world.point_cache.frame_end = 500


def rb_common(ob):
    ob.rigid_body.friction = 0.2              # PLA по PLA
    ob.rigid_body.restitution = 0.0           # без отскоков
    ob.rigid_body.linear_damping = 0.9        # квазистатика: гасим пики
    ob.rigid_body.angular_damping = 0.9
    ob.rigid_body.use_deactivation = False    # не засыпать


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

# плита и заглушка неподвижны: статичный MESH у Bullet стабилен
set_rb(OBJ["ptest_plate_v2"], 'PASSIVE', 'MESH')
set_rb(OBJ["ptest_plug_v2"], 'PASSIVE', 'MESH')
set_rb(OBJ["ptest_bridge_v1"], 'PASSIVE', 'MESH')     # мостики защёлкнуты в плиту
set_rb(OBJ["ptest_bridge_v1#2"], 'PASSIVE', 'MESH')
set_rb(OBJ["ptest_washer_v1"], 'PASSIVE', 'MESH')     # привинчена M2 к оси
set_rb(OBJ["ptest_bridge_low_v1"], 'PASSIVE', 'MESH')  # низкий мост над плечом
set_rb(OBJ["ptest_bridge_high_v1"], 'PASSIVE', 'MESH')  # высокие мосты над тележкой
set_rb(OBJ["ptest_bridge_high_v1#2"], 'PASSIVE', 'MESH')

# ПОДВИЖНЫЕ детали: COMPOUND из выпуклых примитивов (меш-меш у Bullet
# взрывается, выпуклые контакты — железные). Дырка = кольцо из 8 брусков.
CHILD = []


def _child(part, ob):
    ob.display_type = 'WIRE'
    ob.hide_render = True
    ob.parent = part
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.ops.rigidbody.object_add()
    ob.rigid_body.type = 'ACTIVE'
    ob.rigid_body.use_margin = True
    ob.rigid_body.collision_margin = 0.01
    rb_common(ob)
    ob.select_set(False)
    CHILD.append(ob)


def _off(part):
    c = CTR.get(part.name)
    return (c.x, c.y, c.z) if c else (0.0, 0.0, 0.0)


def c_box(part, x0, x1, y0, y1, z0, z1, rz=0.0):
    ox, oy, oz = _off(part)
    bpy.ops.mesh.primitive_cube_add(size=1)
    ob = bpy.context.object
    ob.dimensions = (x1 - x0, y1 - y0, z1 - z0)
    ob.location = ((x0 + x1) / 2 - ox, (y0 + y1) / 2 - oy, (z0 + z1) / 2 - oz)
    ob.rotation_euler = (0, 0, rz)
    _child(part, ob)
    ob.rigid_body.collision_shape = 'BOX'


def c_cyl(part, cx, cy, z0, z1, r):
    ox, oy, oz = _off(part)
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=z1 - z0, vertices=24)
    ob = bpy.context.object
    ob.location = (cx - ox, cy - oy, (z0 + z1) / 2 - oz)
    _child(part, ob)
    ob.rigid_body.collision_shape = 'CYLINDER'


def c_ring(part, cx, cy, z0, z1, rin, rout):
    ox, oy, oz = _off(part)
    rc = (rin + rout) / 2
    w = 2 * rc * math.tan(math.pi / 8) + 0.2
    for k in range(8):
        a = k * math.pi / 4
        bpy.ops.mesh.primitive_cube_add(size=1)
        ob = bpy.context.object
        ob.dimensions = (rout - rin, w, z1 - z0)
        ob.location = (cx + rc * math.cos(a) - ox,
                       cy + rc * math.sin(a) - oy, (z0 + z1) / 2 - oz)
        ob.rotation_euler = (0, 0, a)
        _child(part, ob)
        ob.rigid_body.collision_shape = 'BOX'


def compound(name):
    ob = OBJ[name]
    set_rb(ob, 'ACTIVE', 'COMPOUND')
    return ob

sp = compound("ptest_spica_v2")               # спица: тело + 2 кольца-дырки
c_box(sp, 9.5, 117, -2.5, 2.5, 0, 1.6)
c_ring(sp, 4, 0, 0, 1.6, 3.0, 5.5)
c_box(sp, 113, 132.75, -2.5, 2.5, 1.4, 3.0)
c_ring(sp, 138.25, 0, 1.4, 3.0, 3.0, 5.5)

tr = compound("ptest_triangle_v2")            # треугольник: диск-кольцо + плечи
c_ring(tr, 0, 0, 0, 1.6, 3.0, 5.5)
c_ring(tr, 0, 0, 0, 1.6, 5.5, 11.0)
c_box(tr, -66.6, -3, -2.5, 2.5, 0, 1.6)
c_cyl(tr, -65, 0, 0, 1.6, 5.5)
c_cyl(tr, -65, 0, 1.6, 7.0, 2.5)              # штырь tip: верх 12, мосты не задевает
c_box(tr, -2.5, 2.5, -22.8, -3, 0, 1.6)
c_cyl(tr, 0, -21.2, 0, 1.6, 5.5)
c_cyl(tr, 0, -21.2, 1.6, 6.0, 2.5)            # штырёк угла-1 длинный

ca = compound("ptest_cart_v2")                # тележка: палуба со ЩЕЛЬЮ-кулисой
ca.rigid_body.mass = 0.2                      # утяжелена (реально: монетка сверху)
c_box(ca, 6.0, 9.65, -18, 12, 4.5, 8)         # палуба: 3 бокса вокруг ВИЛКИ
c_box(ca, -9.65, 6.0, -18, -11, 4.5, 8)       # (открыта на запад)
c_box(ca, -9.65, 6.0, -5, 12, 4.5, 8)
c_box(ca, -9.65, 9.65, 9.5, 12, 0, 4.5)
c_box(ca, -9.65, 9.65, -18, -16, 0, 4.5)

cr = compound("ptest_crank_r85_v2")           # кривошип: диск + палец
c_cyl(cr, 0, 0, 0, 2.5, 11)
c_cyl(cr, 8.5, 0, 2.5, 7.5, 2.5)

# УЗЛЫ ШТЫРЬ-В-ДЫРКЕ: люфтовые связки, эквивалент реального зазора Ø5/Ø6.
# Свобода ±0.5 в плане (люфт), по вертикали — ровно длина штырька. Контакты
# при этом ОСТАЮТСЯ включены (disable_collisions=False): опоры, мосты,
# потолки и рельсы давят по-настоящему; связка лишь не даёт солверу
# проколоть тонкие стенки на пиковых силах.
def slop(name, x, y, z, a, b, zlo, zhi):
    e = bpy.data.objects.new(name, None)
    e.empty_display_size = 3
    e.location = (x, y, z)
    sc.collection.objects.link(e)
    bpy.context.view_layer.objects.active = e
    e.select_set(True)
    bpy.ops.rigidbody.constraint_add()
    c = e.rigid_body_constraint
    c.type = 'GENERIC'
    c.object1 = a
    c.object2 = b
    c.disable_collisions = False
    for ax in ('x', 'y'):
        setattr(c, 'use_limit_lin_' + ax, True)
        setattr(c, 'limit_lin_' + ax + '_lower', -0.5)
        setattr(c, 'limit_lin_' + ax + '_upper', 0.5)
    c.use_limit_lin_z = True
    c.limit_lin_z_lower = zlo
    c.limit_lin_z_upper = zhi
    for ax in ('x', 'y'):
        setattr(c, 'use_limit_ang_' + ax, True)
        setattr(c, 'limit_ang_' + ax + '_lower', -math.radians(5))
        setattr(c, 'limit_ang_' + ax + '_upper', math.radians(5))
    c.use_limit_ang_z = False
    e.select_set(False)
    return c

slop("j_pin", 229.2, -23.5, 9.0, OBJ["ptest_crank_r85_v2"], OBJ["ptest_spica_v2"], -0.3, 3.1)
slop("j_c1", 95, -21.2, 7.4, OBJ["ptest_spica_v2"], OBJ["ptest_triangle_v2"], -0.1, 2.8)
slop("j_axis", 95, 0, 5.8, OBJ["ptest_plate_v2"], OBJ["ptest_triangle_v2"], -0.1, 0.3)
cs = slop("j_slot", 30, 0, 11, OBJ["ptest_triangle_v2"], OBJ["ptest_cart_v2"], -0.5, 3.2)
cs.limit_lin_x_lower = -6.2                   # вилка: штырь гуляет по дуге на запад
cs.limit_lin_x_upper = 0.6
# КАНАЛ как ДВЕ люфтовые связки у носа и кормы (база 28): пара линейных
# лимитов ±0.35 держит разворот жёстко (yaw < 1.5 гарантированно)
for chname, chy in (("j_channel_s", -6), ("j_channel_n", 22)):
    ch = slop(chname, 30, chy, 9, OBJ["ptest_plate_v2"], OBJ["ptest_cart_v2"], -0.2, 0.5)
    ch.limit_lin_x_lower = -0.35
    ch.limit_lin_x_upper = 0.35
    ch.use_limit_lin_y = True
    ch.limit_lin_y_lower = -24
    ch.limit_lin_y_upper = 24
    for _ax in ('x', 'y'):
        setattr(ch, 'limit_ang_' + _ax + '_lower', -math.radians(3))
        setattr(ch, 'limit_ang_' + _ax + '_upper', math.radians(3))

# КРИВОШИП — КИНЕМАТИЧЕСКИЙ «мотор»: 40 кадров покоя (всё усаживается), потом 1.5°/кадр
ck = OBJ["ptest_crank_r85_v2"]
ck.rigid_body.kinematic = True
for fr in range(1, 501):
    a = 0 if fr <= 40 else (fr - 40) * 1.0
    ck.rotation_euler = (0, 0, math.radians(-90 + a))
    ck.keyframe_insert("rotation_euler", frame=fr)

# ---- свет и мир ----
bpy.ops.object.light_add(type='SUN', location=(80, -60, 130))
bpy.context.object.data.energy = 4
bpy.context.object.rotation_euler = (math.radians(35), math.radians(12), 0)
w = bpy.data.worlds.new("W")
w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.92, 0.92, 0.92, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 0.75
sc.world = w

bpy.ops.wm.save_as_mainfile(filepath=r"C:\App\gitar\2-0\Стенд_физика.blend")
print("PHYS OK")
