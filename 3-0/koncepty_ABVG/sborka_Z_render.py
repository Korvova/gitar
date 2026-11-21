# -*- coding: utf-8 -*-
# Картинки шагов сборки модуля З. Серое — уже собрано, оранжевое — ставим сейчас (раздвинуто, стрелка — куда).
import bpy, os, math
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "19.70_pechat_okantovka8_Z")
A = os.path.join(D, "asm_sborka"); OUTD = os.path.join(D, "sborka")
YM, YG, AF = 15.5, 7.5, 2.5 * math.pi * 0.8
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.unit_settings.scale_length = 0.001; sc.unit_settings.length_unit = 'MILLIMETERS'
sc.render.engine = 'BLENDER_WORKBENCH'; sc.display.shading.color_type = 'MATERIAL'; sc.display.shading.show_cavity = True
sc.render.resolution_x, sc.render.resolution_y = 1100, 800
w = bpy.data.worlds.new("w"); w.color = (0.93, 0.93, 0.92); sc.world = w
OBJ = {}
def load(n, key=None, loc=(0, 0, 0)):
    bpy.ops.wm.stl_import(filepath=os.path.join(A, n + ".stl")); o = bpy.context.selected_objects[0]
    o.name = key or n; o["base_loc"] = loc; o.location = loc; m = bpy.data.materials.new(o.name); o.data.materials.append(m); OBJ[o.name] = o; return o
for n in ("okantovka", "knopki", "pol", "motor", "posts", "sens", "noga_prav", "noga_lev", "brusok", "polzun", "rack", "beam", "telezhka"):
    load(n)
load("flo", "flo1", (-AF, YG, 0)); load("flo", "flo2", (AF, YG, 0)); load("plat", "plat", (0, YM, 0)); load("gm", "gm", (0, YM, 0))
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam; cam.data.clip_start = 1
tg = bpy.data.objects.new("t", None); sc.collection.objects.link(tg)
k = cam.constraints.new('TRACK_TO'); k.target = tg; k.track_axis = 'TRACK_NEGATIVE_Z'; k.up_axis = 'UP_Y'
GREY, NEW, DARK = (.72, .73, .76, 1), (1.0, .55, .1, 1), (.15, .15, .17, 1)
def step(fname, done, new, cam_loc=(75, -95, 75), target=(0, 3, 10)):
    for n, o in OBJ.items():
        if n in done:
            o.hide_render = False; o.location = o["base_loc"]
            o.data.materials[0].diffuse_color = DARK if n == "motor" else GREY
        elif n in new:
            o.hide_render = False; b = o["base_loc"]; d = new[n]; o.location = (b[0] + d[0], b[1] + d[1], b[2] + d[2])
            o.data.materials[0].diffuse_color = NEW
        else:
            o.hide_render = True
    cam.location = cam_loc; tg.location = target
    sc.render.filepath = os.path.join(OUTD, fname); bpy.ops.render.render(write_still=True)
UP = lambda h: (0, 0, h)
step("1_okantovka_knopki.png", [], {"okantovka": (0, 0, 0), "knopki": UP(8)}, (60, -80, 70), (0, 0, 3))
step("2_motor_stojki_49E.png", ["pol"], {"motor": UP(12), "posts": UP(10), "sens": UP(10)})
step("3_nogi_balki.png", ["pol", "motor", "posts", "sens"], {"noga_prav": (10, 0, 0), "noga_lev": (-10, 0, 0)}, (85, -75, 40), (0, -2, 12))
step("4_brusok_polzun_shesterni.png", ["pol", "motor", "posts", "sens", "noga_prav", "noga_lev"],
     {"brusok": UP(6), "polzun": UP(12), "flo1": UP(18), "flo2": UP(18)})
step("5_rejka_rotor.png", ["pol", "motor", "posts", "sens", "noga_prav", "noga_lev", "brusok", "polzun", "flo1", "flo2"],
     {"rack": UP(10), "plat": UP(8), "gm": UP(14)})
step("6_balka_telezhka.png", ["pol", "motor", "posts", "sens", "noga_prav", "noga_lev", "brusok", "polzun", "flo1", "flo2", "rack", "plat", "gm"],
     {"beam": UP(6), "telezhka": (30, 0, 6)})
done_all = [n for n in OBJ if n not in ("okantovka", "knopki")]
step("7_v_okantovku.png", ["okantovka", "knopki"], {n: UP(12) for n in done_all}, (80, -100, 80), (0, 0, 12))
step("8_gotovo.png", list(OBJ), {}, (75, -95, 75), (0, 3, 10))
print("готово")
