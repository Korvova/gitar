# -*- coding: utf-8 -*-
"""Картинки стенда датчика положения для «Т. Положение тележек»: детали, сборка, крайние положения."""
import os, sys
import numpy as np
import pyvista as pv
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "Print", "Print")
OUT = os.path.join(HERE, "..", "wiki", "img")
pv.OFF_SCREEN = True
sys.path.insert(0, HERE)
R_CR = 4.8; Y0 = 12.0 + R_CR; BAR_L = 50.0; MAG_Y_BAR = 25.0; FLOOR = 2.0; BAND_T = 1.6
MAG_X = 2.0; SENS_Y = Y0 + MAG_Y_BAR + R_CR + 0.5
C = {"base": "#cfcac1", "bar": "#d9612f", "mag": "#1d9a5b", "sens": "#3f74c9"}


def load(name, loc=(0, 0, 0)):
    m = trimesh.load(os.path.join(SRC, name + ".stl"), force="mesh"); m.apply_translation(loc); return pv.wrap(m)


def magnet(dy=0.0):
    c = pv.Cylinder(center=(MAG_X, Y0 + MAG_Y_BAR + dy, FLOOR + 0.5 + 0.75), direction=(0, 0, 1), radius=2.0, height=1.5)
    return c


def sensor():
    return pv.Cube(center=(6.9, SENS_Y, FLOOR + 1.25), x_length=3.0, y_length=4.0, z_length=1.5)


def scene(path, parts, cam, labels=(), size=(1600, 1000), edges=False, zoom=1.0):
    p = pv.Plotter(off_screen=True, window_size=size); p.set_background("white")
    for m, c, op in parts:
        p.add_mesh(m, color=c, opacity=op, smooth_shading=False, specular=0.15, ambient=0.35, diffuse=0.7)
        if edges:
            p.add_mesh(m.extract_feature_edges(feature_angle=40), color="#6f6a63", line_width=1.2)
    if labels:
        p.add_points(pv.PolyData(np.array([l[0] for l in labels], float)), color="black", point_size=10, render_points_as_spheres=True)
    p.add_light(pv.Light(position=(-200, -100, 400), intensity=0.9)); p.add_light(pv.Light(position=(200, 200, 300), intensity=0.5))
    p.camera_position = cam
    p.camera.zoom(zoom)
    if labels:
        p.render(); ren = p.renderer
        for xyz, text in labels:
            ren.SetWorldPoint(float(xyz[0]), float(xyz[1]), float(xyz[2]), 1.0); ren.WorldToDisplay()
            dx, dy, _ = ren.GetDisplayPoint()
            p.add_text(text, position=(dx + 12, dy + 8), font_size=13, color="black", font_file="C:/Windows/Fonts/arial.ttf", viewport=False, shadow=False)
    p.screenshot(path); p.close(); print("saved", os.path.basename(path))


base = load("hall_stend_base_v1")
# 1. детали рядом
scene(os.path.join(OUT, "hall_stend_1_detali.png"),
      [(base, C["base"], 1), (load("hall_stend_bar_v1", (30, 12, 0)), C["bar"], 1),
       (pv.Cylinder(center=(30, 70, 0.75), direction=(0, 0, 1), radius=2.0, height=1.5), C["mag"], 1),
       (pv.Cube(center=(30, 78, 0.75), x_length=3.0, y_length=4.0, z_length=1.5), C["sens"], 1)],
      [(-60, -50, 75), (10, 42, 0), (0, 0, 1)],
      [((0, 20, 5), "основание со стойкой"), ((6.9, SENS_Y, 5), "карман датчика"), ((30, 45, 2), "палка"),
       ((30, 70, 2), "магнит Ø4×1.5"), ((30, 78, 2), "датчик 49E")], zoom=1.5)
# 2. сборка в среднем положении
mid = [(base, C["base"], 1), (load("hall_stend_bar_v1", (0, Y0, FLOOR)), C["bar"], 1), (magnet(0), C["mag"], 1), (sensor(), C["sens"], 1)]
scene(os.path.join(OUT, "hall_stend_2_sborka.png"), mid, [(-60, -30, 60), (0, 42, 2), (0, 0, 1)], zoom=1.6,
      labels=[((MAG_X, Y0 + MAG_Y_BAR, 5), "магнит в кармане палки"), ((6.9, SENS_Y, 5), "датчик в кармане стойки"),
       ((0, Y0 + 3, 9), "ручка"), ((-7, Y0 + BAR_L - 1.5, 3), "стрелка и шкала")])
# 3. крайние положения: юг (0 мм) и север (9.6 мм)
for tag, dy in (("jug", -R_CR), ("sever", +R_CR)):
    parts = [(base, C["base"], 1), (load("hall_stend_bar_v1", (0, Y0 + dy, FLOOR)), C["bar"], 1), (magnet(dy), C["mag"], 1), (sensor(), C["sens"], 1)]
    scene(os.path.join(OUT, f"hall_stend_3_{tag}.png"), parts, [(0, 45, 110), (0, 45, 0), (0, 1, 0)], edges=True, zoom=1.0,
          labels=[((MAG_X, Y0 + MAG_Y_BAR + dy, 4), "магнит"), ((6.9, SENS_Y, 4), "датчик"),
           ((-8, Y0 + BAR_L - 1.5 + dy, 3), "стрелка: %s мм" % ("0" if dy < 0 else "9.6"))], size=(1000, 1400))
