# -*- coding: utf-8 -*-
# Наглядно: обе тележки 15 мм, площадки на шаге 24 → модуль Б приходится придвинуть, колпаки моторов пересекаются (красное).
import bpy, os, math
D0 = os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.open_mainfile(filepath=os.path.join(D0, "para.blend"))
sc = bpy.context.scene
D_OLD = float(open(os.path.join(D0, "asm_para", "D.txt")).read())
Z0, Z1 = 26.1, 29.7
A0, A1 = -9.7, 5.3                        # тележка А 15 мм: от крюка на передней стенке
B1 = -4.85; B0 = B1 - 15.0                 # тележка Б 15 мм: должна доставать до своей рейки (y −4.85)
D_NEW = 24.0 + (A0 + A1) / 2 - (B0 + B1) / 2
dy = D_NEW - D_OLD
for o in list(sc.objects):
    if o.name.startswith("Основание") or o.name.startswith("Тележка"):
        o.hide_set(True); o.hide_render = True
    elif "Б" in o.name.split(" ")[-1] or o.name.endswith(" Б") or "Б1" in o.name or "Б2" in o.name or o.name.startswith("Перекладина"):
        o.location.y += dy
def mat(n, c, a=1.0):
    m = bpy.data.materials.new(n); m.diffuse_color = (c[0], c[1], c[2], a); return m
def box(n, x0, x1, y0, y1, z0, z1, m):
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)); o = bpy.context.object
    o.name = n; o.scale = (x1 - x0, y1 - y0, z1 - z0); o.data.materials.append(m); return o
mb = mat("тележка 15", (.15, .4, .9), 1)
box("Тележка А 15 мм", -10, 10, A0, A1, Z0, Z1, mb)
box("Тележка Б 15 мм", -10, 10, B0 + D_NEW, B1 + D_NEW, Z0, Z1, mb)
ja, jb = bpy.data.objects["Колпак А"], bpy.data.objects["Колпак Б"]
bpy.context.view_layer.update()
cp = ja.copy(); cp.data = ja.data.copy(); sc.collection.objects.link(cp); cp.name = "ПЕРЕСЕЧЕНИЕ колпаков"
md = cp.modifiers.new("x", 'BOOLEAN'); md.operation = 'INTERSECT'; md.object = jb; md.solver = 'EXACT'
cp.data.materials.clear(); cp.data.materials.append(mat("пересечение", (1, 0, 0), 1))
for o in (ja, jb):
    o.data.materials[0].diffuse_color = (.85, .3, .15, .45)
bpy.ops.object.text_add(location=(-24, 10, 35)); t = bpy.context.object
t.data.body = "Тележки 15 мм, шаг 24: колпаки залезают друг в друга на %.1f мм" % (38.0 - D_NEW); t.data.size = 3.2
t.data.materials.append(mat("текст", (0.9, 0.1, 0.1), 1)); t.rotation_euler = (math.radians(60), 0, 0)
sc.frame_set(1)
cam = bpy.data.objects["Камера"]; cam.location = (110, -70, 120)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(D0, "pokaz_15mm.blend"))
s = sc; s.render.engine = 'BLENDER_WORKBENCH'; s.display.shading.color_type = 'MATERIAL'; s.render.resolution_x = 1000; s.render.resolution_y = 700
s.render.filepath = os.path.join(D0, "pokaz_15mm.png"); bpy.ops.render.render(write_still=True)
print("D_NEW %.2f overlap %.2f" % (D_NEW, 38.0 - D_NEW))
