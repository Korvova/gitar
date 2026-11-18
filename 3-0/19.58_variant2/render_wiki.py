import bpy, os
s = bpy.context.scene; s.render.engine = 'BLENDER_WORKBENCH'; s.display.shading.color_type = 'MATERIAL'
s.render.resolution_x = 1100; s.render.resolution_y = 750; s.frame_set(1)
cam = bpy.data.objects['Камера']
out = os.path.join(os.path.dirname(bpy.data.filepath), "..", "..", "wiki", "img")
for nm, loc in (("para_dva_palca", (110, -90, 110)), ("para_sverhu", (0, 19, 190)), ("para_sboku", (170, 19, 30))):
    cam.location = loc; s.render.filepath = os.path.abspath(os.path.join(out, nm + ".png")); bpy.ops.render.render(write_still=True)
print("ok")
