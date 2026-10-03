# -*- coding: utf-8 -*-
r"""Картинки к «Т. Инструкция по сборке: магнитное русло (проба)» — с настоящих STL стола 86.
Запуск: blender -b -P 2-0\magnit\render_sborka_magnit.py  -> wiki/img/mag_sb_*.png"""
import math
import os
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(os.path.dirname(HERE), "Print", "Print")
IMG = os.path.join(os.path.dirname(os.path.dirname(HERE)), "wiki", "img")
CW, NC, CH, LEG, WIN = 6.5, 8, 20.9, 2.45, 16.0
PHASE = ["A", "B", "B-", "A", "B", "A-", "A", "B"]       # фаза и направление катушек 1..8


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = 'METRIC'
    sc.unit_settings.scale_length = 0.001
    sc.render.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
    sc.render.resolution_x, sc.render.resolution_y = 1000, 640
    sc.view_settings.view_transform = "Standard"
    w = bpy.data.worlds.new("w"); sc.world = w
    w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (0.62, 0.65, 0.69, 1)
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
    sun.data.energy = 3.5
    sun.rotation_euler = (math.radians(35), math.radians(10), math.radians(40))
    sc.collection.objects.link(sun)
    return sc


def mat(name, rgba, alpha=1.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rgba
    if alpha < 1:
        b.inputs["Alpha"].default_value = alpha
        try:
            m.surface_render_method = 'BLENDED'
        except Exception:
            pass
    return m


def stl(fname, m, loc=(0, 0, 0), rot=(0, 0, 0)):
    bpy.ops.wm.stl_import(filepath=os.path.join(P, fname + ".stl"))
    ob = bpy.context.selected_objects[0]
    ob.data.materials.clear(); ob.data.materials.append(m)
    ob.location = loc; ob.rotation_euler = rot
    return ob


def box(x0, x1, y0, y1, z0, z1, m):
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), rotation=(0, 0, 0))
    ob = bpy.context.object
    ob.scale = (x1 - x0, y1 - y0, z1 - z0)
    ob.data.materials.append(m)
    return ob


def text(s, loc, size=4.0, m=None, rot=(math.radians(90), 0, 0)):
    bpy.ops.object.text_add(location=loc, rotation=rot)
    t = bpy.context.object
    t.data.body = s
    t.data.size = size
    t.data.align_x = 'CENTER'
    t.data.extrude = 0.2
    t.data.materials.append(m or mat("текст", (0.05, 0.05, 0.05, 1)))
    return t


def cyl(x, y, z0, z1, r, m):
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=r, depth=z1 - z0, location=(x, y, (z0 + z1) / 2), rotation=(0, 0, 0))
    ob = bpy.context.object
    ob.data.materials.append(m)
    return ob


def coil_xz(x0, y0, y1, z0, m):
    """Одна катушка стоймя в плоскости XZ (как в рамке): рамка из 4 брусков."""
    box(x0, x0 + LEG, y0, y1, z0, z0 + CH, m)
    box(x0 + CW - LEG, x0 + CW, y0, y1, z0, z0 + CH, m)
    box(x0 + LEG, x0 + CW - LEG, y0, y1, z0, z0 + LEG, m)
    box(x0 + LEG, x0 + CW - LEG, y0, y1, z0 + CH - LEG, z0 + CH, m)


def coil_xy(cx, cy, z0, z1, m):
    """Одна катушка лёжа (в оправке): окно по Y."""
    box(cx - CW / 2, cx - CW / 2 + LEG, cy - CH / 2, cy + CH / 2, z0, z1, m)
    box(cx + CW / 2 - LEG, cx + CW / 2, cy - CH / 2, cy + CH / 2, z0, z1, m)
    box(cx - CW / 2 + LEG, cx + CW / 2 - LEG, cy - CH / 2, cy - CH / 2 + LEG, z0, z1, m)
    box(cx - CW / 2 + LEG, cx + CW / 2 - LEG, cy + CH / 2 - LEG, cy + CH / 2, z0, z1, m)


def shot(sc, name, cam_loc, target, lens=35):
    tgt = bpy.data.objects.new("t", None); sc.collection.objects.link(tgt); tgt.location = target
    c = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(c)
    c.data.lens = lens; c.data.clip_start = 1; c.location = cam_loc
    tc = c.constraints.new('TRACK_TO'); tc.target = tgt; tc.track_axis = 'TRACK_NEGATIVE_Z'; tc.up_axis = 'UP_Y'
    sc.camera = c
    sc.render.filepath = os.path.join(IMG, name)
    bpy.ops.render.render(write_still=True)


PLA = (0.93, 0.93, 0.95, 1)
C_COIL = (0.95, 0.55, 0.15, 1)
C_A, C_B = (0.95, 0.55, 0.15, 1), (0.25, 0.70, 0.35, 1)
C_N, C_S = (0.85, 0.15, 0.15, 1), (0.15, 0.30, 0.85, 1)
C_FE = (0.45, 0.47, 0.50, 1)
C_BLUE = (0.25, 0.45, 0.80, 1)

# ---- 0: что напечатать ----
sc = reset()
stl("mag_osnova", mat("основа", PLA), loc=(0, 0, 10))
stl("mag_ramka", mat("рамка", PLA), loc=(0, 45, 1.5), rot=(math.radians(90), 0, 0))
stl("mag_skoba", mat("скоба", PLA), loc=(70, 0, 0.15))
for i, x in enumerate((-70, -50)):
    stl("mag_opravka_a", mat("оправка", C_BLUE), loc=(x, 0, 0))
    stl("mag_opravka_b", mat("оправка", C_BLUE), loc=(x, -45, 0))
text("86", (0, -40, 0.1), 7, rot=(0, 0, 0))
shot(sc, "mag_sb_0_detali.png", (0, -150, 170), (0, 0, 0), 30)

# ---- 1: оправка ----
sc = reset()
stl("mag_opravka_a", mat("оправка", C_BLUE))
stl("mag_opravka_b", mat("оправка b", (0.45, 0.65, 0.95, 1)), loc=(0, 0, 14))
shot(sc, "mag_sb_1_opravka.png", (45, -55, 55), (0, 0, 8), 40)

# ---- 2: намотка ----
sc = reset()
stl("mag_opravka_a", mat("оправка", C_BLUE))
coil_xy(0, 0, 2.5, 5.5, mat("медь", C_COIL))
b = stl("mag_opravka_b", mat("оправка b", (0.45, 0.65, 0.95, 1), 0.35), loc=(0, 0, 5.5))
shot(sc, "mag_sb_2_namotka.png", (35, -45, 50), (0, 0, 3), 45)

# ---- 3: катушки в рамку ----
sc = reset()
stl("mag_ramka", mat("рамка", PLA))
for k in range(NC):
    ph = PHASE[k]
    m = mat("фаза " + ph, C_A if ph[0] == "A" else C_B)
    coil_xz(-26 + k * CW, -1.5, 1.5, 0, m)
    text(f"{k + 1}\n{ph.replace('-', '−')}", (-26 + k * CW + CW / 2, -1.7, 24.5), 3.0)
shot(sc, "mag_sb_3_katushki.png", (0, -95, 25), (0, 0, 10), 40)

# ---- 4: рамка в основу ----
sc = reset()
stl("mag_osnova", mat("основа", PLA))
stl("mag_ramka", mat("рамка", PLA), loc=(0, 0, 12))
stl("mag_katushki_proverka", mat("медь", C_COIL), loc=(0, 0, 12))
shot(sc, "mag_sb_4_osnova.png", (70, -90, 60), (0, 0, 8), 35)

# ---- 5: магниты и сталь в скобу (снизу) ----
sc = reset()
stl("mag_skoba", mat("скоба", PLA, 0.5))
YM0, YM1, Z0 = 2.0, 7.0, 0.45
for s in (1, -1):
    for p in range(3):
        n_face = (p % 2 == 0) == (s > 0)                    # грань к щели: N или S
        y0, y1 = sorted((s * YM0, s * YM1))
        box(-15 + p * 10 + 0.3, -5 + p * 10 - 0.3, y0, y1, Z0 - 28, Z0 - 8, mat("N" if n_face else "S", C_N if n_face else C_S))
        text("N" if n_face else "S", (-10 + p * 10, s * 1.2, Z0 - 31), 3.0, rot=(0, 0, 0))
    y0, y1 = sorted((s * YM1, s * (YM1 + 1.5)))
    box(-15, 15, y0, y1, Z0 - 55, Z0 - 35, mat("сталь", C_FE))
shot(sc, "mag_sb_5_magnity.png", (60, -80, -10), (0, 0, -20), 32)

# ---- 6: скоба на рельс ----
sc = reset()
stl("mag_osnova", mat("основа", PLA))
stl("mag_ramka", mat("рамка", PLA))
stl("mag_katushki_proverka", mat("медь", C_COIL))
for f, z in (("mag_skoba", 10), ("mag_magnity_proverka", 10), ("mag_stal_proverka", 10)):
    stl(f, mat(f, PLA if f == "mag_skoba" else (C_N if "magn" in f else C_FE), 0.45 if f == "mag_skoba" else 1.0), loc=(8, 0, z))
shot(sc, "mag_sb_6_skoba.png", (75, -95, 70), (0, 0, 12), 35)
print("ok")
