# -*- coding: utf-8 -*-
# ФИЗИКА стенда: rigid body + hinge-шарниры + мотор на кривошипе
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
    "ptest_serga_v2": mat("se", (0.2, 0.7, 0.35, 1)),
    "ptest_crank_r65_v2": mat("cr", (0.8, 0.68, 0.2, 1)),
    "ptest_cart_v2": mat("ca", (0.88, 0.88, 0.9, 1)),
    "ptest_plug_v2": mat("plug", (0.6, 0.4, 0.7, 1)),
}
POS = {
    "ptest_plate_v2": ((0, 0, 0), 0),
    "ptest_triangle_v2": ((95, -2, 5.0), 0),
    "ptest_spica_v2": ((91.0, -23.25, 6.6), 0.72),
    "ptest_serga_v2": ((30, -6, 6.6), 90),
    "ptest_crank_r65_v2": ((229, -15, 5.2), -90),
    "ptest_cart_v2": ((30, 6, 5.0), 0),
    "ptest_plug_v2": ((229, -15, 3.05), 0),
}

OBJ = {}
for name, (loc, rz) in POS.items():
    before = set(bpy.data.objects)
    bpy.ops.wm.stl_import(filepath=SRC + "\\" + name + ".stl")
    ob = (set(bpy.data.objects) - before).pop()
    ob.name = name
    ob.data.materials.append(COL[name])
    ob.location = loc
    ob.rotation_euler = (0, 0, math.radians(rz))
    OBJ[name] = ob

# ---- rigid body мир ----
bpy.ops.rigidbody.world_add()
sc.rigidbody_world.substeps_per_frame = 150
sc.rigidbody_world.solver_iterations = 200
sc.frame_start, sc.frame_end = 1, 500
sc.rigidbody_world.point_cache.frame_end = 500


def set_rb(ob, typ, slot):
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.ops.rigidbody.object_add()
    ob.rigid_body.type = typ
    ob.rigid_body.mass = 0.05
    ob.rigid_body.collision_shape = 'CONVEX_HULL'
    cols = [False] * 20
    cols[slot] = True
    ob.rigid_body.collision_collections = cols   # каждый в своём слое: столкновений нет
    ob.rigid_body.use_deactivation = False       # НЕ ЗАСЫПАТЬ (кинематик не будит)
    ob.select_set(False)

set_rb(OBJ["ptest_plate_v2"], 'PASSIVE', 19)
import os
STEP = int(os.environ.get("PSTEP", "5"))        # 1=вал .. 6=вся цепь
CHAIN = ["ptest_crank_r65_v2", "ptest_spica_v2",
         "ptest_triangle_v2", "ptest_serga_v2", "ptest_cart_v2"][:STEP]
for i, n in enumerate(CHAIN):
    set_rb(OBJ[n], 'ACTIVE', i)
# КРИВОШИП — КИНЕМАТИЧЕСКИЙ (анимированный): крутится гарантированно
ck = OBJ["ptest_crank_r65_v2"]
ck.rigid_body.kinematic = True
for fr in range(1, 501):
    a = 0 if fr <= 40 else (fr - 40) * 1.5      # 40 кадров покоя, потом 1.5°/кадр
    ck.rotation_euler = (0, 0, math.radians(-90 + a))
    ck.keyframe_insert("rotation_euler", frame=fr)


def joint(name, x, y, z, typ, a, b):
    e = bpy.data.objects.new(name, None)
    e.empty_display_size = 3
    e.location = (x, y, z)
    sc.collection.objects.link(e)
    bpy.context.view_layer.objects.active = e
    e.select_set(True)
    bpy.ops.rigidbody.constraint_add()
    c = e.rigid_body_constraint
    c.type = typ
    c.object1 = a
    c.object2 = b
    c.disable_collisions = True
    e.select_set(False)
    return c


P = OBJ["ptest_plate_v2"]
if STEP >= 2:
    joint("j_pin", 229.4, -21.5, 9.0, 'HINGE', OBJ["ptest_crank_r65_v2"], OBJ["ptest_spica_v2"])
if STEP >= 3:
    joint("j_c1", 95, -23.2, 7.4, 'HINGE', OBJ["ptest_spica_v2"], OBJ["ptest_triangle_v2"])
    joint("j_axis", 95, -2, 5.8, 'HINGE', P, OBJ["ptest_triangle_v2"])
if STEP >= 4:
    joint("j_tip", 30, -2, 7.4, 'HINGE', OBJ["ptest_triangle_v2"], OBJ["ptest_serga_v2"])
if STEP >= 5:
    joint("j_cart_pin", 30, 6, 7.4, 'HINGE', OBJ["ptest_serga_v2"], OBJ["ptest_cart_v2"])
    cs = joint("j_cart_slider", 30, 6, 9, 'GENERIC', P, OBJ["ptest_cart_v2"])
    cs.use_limit_lin_x = True
    cs.limit_lin_x_lower = 0
    cs.limit_lin_x_upper = 0
    cs.use_limit_lin_z = True
    cs.limit_lin_z_lower = 0
    cs.limit_lin_z_upper = 0
    cs.use_limit_lin_y = True
    cs.limit_lin_y_lower = -22
    cs.limit_lin_y_upper = 22
    for ax in ('x', 'y', 'z'):
        setattr(cs, 'use_limit_ang_' + ax, True)
        setattr(cs, 'limit_ang_' + ax + '_lower', 0)
        setattr(cs, 'limit_ang_' + ax + '_upper', 0)

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
