# -*- coding: utf-8 -*-
"""Сцена телескопа v3: детали из asm/, 240 кадров, тележка −22 → +22 → −22. Запуск: blender -b -P blender_v3.py (или Run Script)."""
import bpy, os, math
D = os.path.join(os.path.expanduser("~"), "Documents", "App", "mcp-blender-cloude", "gitar_teleskop_v3")
A, S, RF, RM, YM, FR = 2.5 * math.pi * 0.8, 11.0, 4.8, 4.4, 15.5, 240
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.unit_settings.system = 'METRIC'; sc.unit_settings.scale_length = 0.001; sc.unit_settings.length_unit = 'MILLIMETERS'
sc.frame_start, sc.frame_end = 1, FR
COL = {"base": (.55, .58, .62, 1), "most": (.45, .48, .52, 1), "motor": (.1, .1, .12, 1), "pins": (.95, .95, .95, 1), "slider": (.2, .65, .3, 1),
       "strap": (.15, .5, .25, 1), "cart": (.1, .35, .9, 1), "flo": (1, .5, .05, 1), "pin_m": (.85, .2, .1, 1), "beam": (.7, .72, .76, 1)}
NAMES = {"base": "Основание", "most": "Мост", "motor": "Макет мотора", "pins": "Упоры (филамент)", "slider": "Ползун", "strap": "Планка осей",
         "cart": "Тележка", "flo": "Плавающая шестерня", "pin_m": "Шестерня мотора", "beam": "Брусок ползуна"}
ob = {}
def imp(n, name=None):
    bpy.ops.wm.stl_import(filepath=os.path.join(D, "asm", n + ".stl"))
    o = bpy.context.selected_objects[0]; o.name = name or NAMES[n]
    m = bpy.data.materials.new(o.name); m.diffuse_color = COL[n]; o.data.materials.append(m); return o
for n in ("base", "beam", "most", "motor", "slider", "strap", "cart", "pin_m"):
    ob[n] = imp(n)
f1, f2 = imp("flo", "Плавающая шестерня 1"), imp("flo", "Плавающая шестерня 2")
for f in range(1, FR + 1):
    s = S * math.sin(2 * math.pi * (f - 1) / FR)
    for o in (ob["slider"], ob["strap"]):
        o.location.x = s; o.keyframe_insert("location", index=0, frame=f)
    ob["cart"].location.x = 2 * s; ob["cart"].keyframe_insert("location", index=0, frame=f)
    for o, x in ((f1, s - A), (f2, s + A)):
        o.location = (x, 0, 0); o.rotation_euler[2] = -s / RF
        o.keyframe_insert("location", frame=f); o.keyframe_insert("rotation_euler", index=2, frame=f)
    ob["pin_m"].location = (0, YM, 0); ob["pin_m"].rotation_euler[2] = s / RM
    ob["pin_m"].keyframe_insert("rotation_euler", index=2, frame=f); ob["pin_m"].keyframe_insert("location", frame=f)
tg = bpy.data.objects.new("цель", None); sc.collection.objects.link(tg); tg.location = (0, 8, 12)
c = bpy.data.objects.new("Камера", bpy.data.cameras.new("Камера")); sc.collection.objects.link(c)
c.location = (75, -95, 95); c.data.clip_start = 1
k = c.constraints.new('TRACK_TO'); k.target = tg; k.track_axis = 'TRACK_NEGATIVE_Z'; k.up_axis = 'UP_Y'; sc.camera = c
sun = bpy.data.objects.new("Солнце", bpy.data.lights.new("Солнце", "SUN")); sun.data.energy = 3; sc.collection.objects.link(sun)
sc.frame_set(61)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(D, "teleskop_v3.blend")); print("saved")
sh = sc.display.shading; sc.render.engine = 'BLENDER_WORKBENCH'; sh.light = 'STUDIO'; sh.color_type = 'MATERIAL'; sh.show_cavity = True; sh.show_object_outline = True
sc.world = bpy.data.worlds.new("w"); sc.world.color = (0.92, 0.92, 0.92); sc.render.resolution_x, sc.render.resolution_y = 900, 600
sc.render.filepath = os.path.join(D, "teleskop_v3_vid.png"); bpy.ops.render.render(write_still=True)
