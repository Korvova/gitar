# -*- coding: utf-8 -*-
import trimesh
import pyvista as pv

m = pv.wrap(trimesh.load(r"C:\app\Esp-gitar\base_v1.stl"))

clipped = m.clip(normal=(0, 0, 1), origin=(0, 0, 36))
pl = pv.Plotter(off_screen=True, window_size=(1500, 800))
pl.add_mesh(clipped, color="#9fb4c7", smooth_shading=False, show_edges=False)
pl.set_background("white")
pl.camera_position = "xy"
pl.camera.zoom(1.3)
pl.screenshot(r"C:\app\Esp-gitar\_proto_section_top.png")

pl2 = pv.Plotter(off_screen=True, window_size=(1200, 900))
pl2.add_mesh(m, color="#9fb4c7", smooth_shading=False)
pl2.set_background("white")
pl2.camera_position = [(120, -30, 60), (-30, 0, 20), (0, 0, 1)]
pl2.screenshot(r"C:\app\Esp-gitar\_proto_funnel.png")
print("ok")
