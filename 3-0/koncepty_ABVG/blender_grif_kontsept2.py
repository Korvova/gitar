# Сцена концепта грифа: открыть ряд 4 модулей (19.69) и поставить его на гриф 19.72 — блок едет по ладам вместе с хвостом и палкой.
# Запуск: blender -b ../19.69_ryad4_okantovka8/ryad4_okantovka8.blend -P blender_grif_kontsept.py
import bpy, os
D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "19.73_grif_kontsept2"); A_ = os.path.join(D, "asm")
sc = bpy.context.scene
top = [o for o in bpy.data.objects if o.parent is None and o.type != 'CAMERA']
blk = bpy.data.objects.new("БЛОК (едет по ладам)", None); sc.collection.objects.link(blk); blk.empty_display_type = 'ARROWS'; blk.empty_display_size = 40
C = {"osnovanie": (.32, .22, .14, 1), "risunok": (.85, .85, .8, 1), "guby_bloka": (.25, .45, .75, 1), "korobka_plat": (.55, .57, .6, 1), "plata": (.1, .55, .25, 1),
     "tolkatel": (.9, .5, .15, 1), "provoda": (.8, .1, .1, 1), "kryshka_jubka": (.2, .2, .22, 1)}
NM = {"osnovanie": "основание грифа (плита со скосами)", "risunok": "рисунок: струны и лады", "guby_bloka": "губы блока на скосах", "korobka_plat": "коробка с платами",
      "plata": "плата", "tolkatel": "толкатель (к мотору в деке)", "provoda": "провода в толкателе", "kryshka_jubka": "крышка-юбка блока"}
for n, col in C.items():
    bpy.ops.wm.stl_import(filepath=os.path.join(A_, n + ".stl")); o = bpy.context.selected_objects[0]; o.name = NM[n]
    m = bpy.data.materials.new(n); m.diffuse_color = col; o.data.materials.append(m)
    if n not in ("osnovanie", "risunok"): top.append(o)
bpy.context.view_layer.update()
for o in top:
    mw = o.matrix_world.copy(); o.parent = blk; o.matrix_world = mw
for f, y in ((1, -150.0), (120, 100.0), (240, -150.0)):
    blk.location.y = y; blk.keyframe_insert("location", index=1, frame=f)
cam = bpy.data.objects.get("Камера")
if cam:
    cam.constraints.clear(); cam.location = (260, -260, 200); cam.rotation_euler = (1.05, 0, 0.785); cam.data.clip_start = 1; cam.data.clip_end = 5000
sc.frame_set(60); bpy.ops.wm.save_as_mainfile(filepath=os.path.join(D, "grif_kontsept2.blend")); print("saved", len(top))
