# А (слева): тележка по центру на мосту — как сейчас.  Б (справа): тележка спереди над шестернями, зубья внутрь.
import bpy, os, math
D = os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.unit_settings.scale_length = 0.001; sc.unit_settings.length_unit = 'MILLIMETERS'
YM, A = 15.5, 2.5 * math.pi * 0.8
C = {"base": (.55, .58, .62, 1), "beam": (.7, .72, .76, 1), "motor": (.1, .1, .12, 1), "slider": (.2, .65, .3, 1), "flo": (1, .5, .05, 1),
     "pin_m": (.85, .2, .1, 1), "jacket": (.6, .25, .7, 1), "most": (.62, .65, .7, 1), "cart": (.1, .35, .9, 1),
     "baseB": (.55, .58, .62, 1), "fixB": (.45, .48, .52, 1), "cartB": (.1, .35, .9, 1), "padB": (.95, .95, .97, 1), "cap0": (.95, .95, .97, 1)}
def put(folder, n, x0, name):
    bpy.ops.wm.stl_import(filepath=os.path.join(D, folder, n + ".stl")); o = bpy.context.selected_objects[0]; o.name = name
    m = bpy.data.materials.new(name); m.diffuse_color = C[n]; o.data.materials.append(m); o.location.x += x0
    if n in ("pin_m", "jacket"): o.location.y = YM
    return o
for n in ("base", "beam", "motor", "slider", "pin_m", "jacket", "most", "cart", "cap0"):
    put("asm", n, -35, "А · " + n)
for k in (-A, A):
    put("asm", "flo", -35 + k, "А · шестерня")
for n in ("baseB", "fixB", "cartB", "padB"):
    put("asm_B", n, 35, "Б · " + n)
for n in ("beam", "motor", "slider", "pin_m", "jacket"):
    put("asm", n, 35, "Б · " + n)
for k in (-A, A):
    put("asm", "flo", 35 + k, "Б · шестерня")
pm = bpy.data.materials.new("палец"); pm.diffuse_color = (.2, .6, 1, .55)
for x, y, t in ((-35, 12.5, "А"), (35, -10.1, "Б")):
    bpy.ops.mesh.primitive_cylinder_add(radius=6, depth=1, location=(x, y, 31.5)); p = bpy.context.object; p.name = "Палец " + t; p.data.materials.append(pm)
tg = bpy.data.objects.new("ц", None); sc.collection.objects.link(tg); tg.location = (0, 10, 15)
cam = bpy.data.objects.new("Камера", bpy.data.cameras.new("Камера")); sc.collection.objects.link(cam); cam.location = (40, -150, 110); cam.data.clip_start = 1
c = cam.constraints.new('TRACK_TO'); c.target = tg; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'; sc.camera = cam
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(D, "varianty_AB.blend")); print("saved")
