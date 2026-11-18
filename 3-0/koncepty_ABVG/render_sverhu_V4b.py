import bpy, os
s = bpy.context.scene
keep = ("мотор", "площадка", "шестерня мотора", "платформа")
for o in s.objects:
    if o.type == 'MESH':
        o.hide_render = not any(o.name.startswith(k) for k in keep)
for o in s.objects:
    if o.type == 'MESH' and o.name.startswith("мотор"):
        o.active_material = bpy.data.materials.get("motor")
        o.active_material.diffuse_color = (.1, .25, .8, 1)
    if o.type == 'MESH' and o.name.startswith("площадка"):
        for m in o.data.materials: m.diffuse_color = (.7, .7, .7, 1)
    if o.type == 'MESH' and o.name.startswith("шестерня"):
        for m in o.data.materials: m.diffuse_color = (0, 0, 0, 1)
cam = bpy.data.objects["Камера"]; cam.constraints.clear(); cam.location = (0, 0, 300); cam.rotation_euler = (0, 0, 1.5708)
cam.data.type = 'ORTHO'; cam.data.ortho_scale = 140
s.render.engine = 'BLENDER_WORKBENCH'; s.display.shading.color_type = 'MATERIAL'; s.render.resolution_x = 1200; s.render.resolution_y = 500
s.frame_set(1)
for o in s.objects:
    if o.animation_data: o.animation_data_clear()
    if o.name.startswith(("площадка", "тележка", "ползун")): o.location.x = 0
s.render.filepath = os.path.join(os.path.dirname(bpy.data.filepath), "ryad_V4b_sverhu.png"); bpy.ops.render.render(write_still=True)
