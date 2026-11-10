# -*- coding: utf-8 -*-
# Одна дорожка: 3 датчика 49E боком, маркировкой вверх, ножки в сторону -X (тогда питание +Y, земля по центру, сигнал -Y), отверстия под пины, провода снизу без пересечений.
import bpy, os, math
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Датчики_боком_с_дырками.blend")
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.unit_settings.system = 'METRIC'; sc.unit_settings.scale_length = 0.001; sc.unit_settings.length_unit = 'MILLIMETERS'
def mat(n, c):
    m = bpy.data.materials.new(n); m.diffuse_color = c; return m
PL = mat("платформа", (0.3, 0.3, 0.33, 1)); SE = mat("датчик 49E", (0.08, 0.08, 0.09, 1)); MG = mat("магнит", (0.75, 0.75, 0.8, 1))
RED = mat("питание", (0.9, 0.1, 0.1, 1)); BLK = mat("земля", (0.02, 0.02, 0.02, 1)); LEG = mat("ножки", (0.8, 0.7, 0.3, 1)); OC = [mat("сигнал 1", (0.1, 0.6, 1, 1)), mat("сигнал 2", (0.1, 0.8, 0.2, 1)), mat("сигнал 3", (1, 0.75, 0.1, 1))]
def box(n, x0, x1, y0, y1, z0, z1, m):
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x0+x1)/2, (y0+y1)/2, (z0+z1)/2)); o = bpy.context.object; o.name = n; o.scale = (x1-x0, y1-y0, z1-z0)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True); o.data.materials.append(m); return o
def cyl(n, r, z0, z1, x, y, m):
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=r, depth=z1-z0, location=(x, y, (z0+z1)/2)); o = bpy.context.object; o.name = n; o.data.materials.append(m); return o
def wire(n, pts, m, r=0.2):
    cu = bpy.data.curves.new(n, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = r; cu.bevel_resolution = 2
    sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
    for p, q in zip(sp.points, pts): p.co = (*q, 1)
    o = bpy.data.objects.new(n, cu); sc.collection.objects.link(o); o.data.materials.append(m); return o
YC = -5.2; XS = (-8.8, 0.0, 8.8); PIN = 1.27; XH = 2.6; ZU = -3.95
P = box("платформа: дно паза 2 мм", -20, 20, -7.3, 3.0, -3.5, -1.5, PL)
Q = box("платформа за пазом", -20, 20, -13.5, -7.3, -3.5, 0, PL)
cut = [box("c", -24, 24, -1.5, 1.5, -4, -1, PL)]                    # щель проводов мотора
for x in XS:
    cut.append(box("c", x - 1.55, x + 1.55, YC - 2.1, YC + 2.1, -3.05, -1, PL))     # гнездо датчика, сверху открыто
    cut.append(box("c", x - XH - 0.55, x - 1.5, YC - 2.1, YC + 2.1, -2.9, -1, PL))  # канавка ножек
    for dy in (PIN, 0, -PIN): cut.append(cyl("c", 0.4, -4, -2, x - XH, YC + dy, PL))  # три отверстия
for c in cut:
    md = P.modifiers.new("v", 'BOOLEAN'); md.object = c; md.solver = 'EXACT'; md.operation = 'DIFFERENCE'
bpy.context.view_layer.objects.active = P
for md in list(P.modifiers): bpy.ops.object.modifier_apply(modifier=md.name)
for c in cut: bpy.data.objects.remove(c)
for i, x in enumerate(XS):
    box("датчик 49E (боком)", x - 1.5, x + 1.5, YC - 2.05, YC + 2.05, -3.0, -1.55, SE)
    for dy, m in ((PIN, RED), (0, BLK), (-PIN, OC[i])):
        wire("ножка", [(x - 1.5, YC + dy, -2.3), (x - XH, YC + dy, -2.3), (x - XH, YC + dy, ZU)], LEG, 0.16)
    wire("сигнал %d" % (i + 1), [(x - XH, YC - PIN, ZU), (x - XH, -9.0 - 0.55 * (2 - i), ZU), (20, -9.0 - 0.55 * (2 - i), ZU)], OC[i])
for mx, nm in ((-8.8, "магнит минус (тележка на x = +4.4)"), (17.6, "магнит плюс (тележка на x = +4.4)")):
    cyl(nm, 2.0, 0.72, 2.62, mx, YC, MG)
wire("питание, общий провод", [(XS[0] - XH, YC + PIN, ZU), (20, YC + PIN, ZU)], RED)
wire("земля, общий провод", [(XS[0] - XH, YC, ZU), (20, YC, ZU)], BLK)
tg = bpy.data.objects.new("ц", None); sc.collection.objects.link(tg); tg.location = (3, -6, -3)
def cam(n, loc):
    c = bpy.data.objects.new(n, bpy.data.cameras.new(n)); sc.collection.objects.link(c); c.location = loc; c.data.lens = 60; c.data.clip_start = 1
    k = c.constraints.new('TRACK_TO'); k.target = tg; k.track_axis = 'TRACK_NEGATIVE_Z'; k.up_axis = 'UP_Y'; return c
below = cam("Снизу", (10, -55, -75)); above = cam("Сверху", (10, -50, 70)); sc.camera = below
sun = bpy.data.objects.new("С", bpy.data.lights.new("С", "SUN")); sc.collection.objects.link(sun)
bpy.ops.wm.save_as_mainfile(filepath=OUT); print("saved")
sh = sc.display.shading; sc.render.engine = 'BLENDER_WORKBENCH'; sh.light = 'STUDIO'; sh.color_type = 'MATERIAL'; sh.show_cavity = True; sh.show_object_outline = True
sc.world = bpy.data.worlds.new("w"); sc.world.color = (0.9, 0.9, 0.9); sc.render.resolution_x, sc.render.resolution_y = 800, 500
sc.render.filepath = os.path.join(os.path.dirname(OUT), "_datchiki_snizu.png"); bpy.ops.render.render(write_still=True)
