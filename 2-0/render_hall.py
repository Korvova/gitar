# -*- coding: utf-8 -*-
"""Картинка: дека v3 со стойками датчиков Холла и магнитами на лентах (черновик)."""
import os, math, sys
import numpy as np
import pyvista as pv
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "Print", "Print")
OUT = os.path.join(HERE, "..", "wiki", "img")
os.makedirs(OUT, exist_ok=True)
pv.OFF_SCREEN = True
sys.argv = [sys.argv[0]]
Z_FLOOR = [3, 8.4, 13.8, 19.2]; LANE = 10; MY = [515, 565, 615, 678]; COMB_Y = (540, 590, 634)


def load(name, loc=(0, 0, 0)):
    m = trimesh.load(os.path.join(SRC, name + ".stl"), force="mesh")
    m.apply_translation(loc)
    return pv.wrap(m)


parts = [(load("gdk1_base_v3", (0, 480, 0)), "#cfcac1", 1.0), (load("gdk2_base_v3", (0, 640, 0)), "#cfcac1", 1.0)]
for i, yg in enumerate(COMB_Y):
    parts.append((load("gdk_comb_v3", (0, yg, 0)), "#a9a49b", 1.0))
for k in range(4):
    parts.append((load(f"gdk_tail{k}_v3", (LANE, 480, Z_FLOOR[k] + 0.05)), "#d9612f", 1.0))
    parts.append((load(f"gdk_crank{k}_v3", (0, MY[k], 0)), "#d8b23a", 1.0))
    parts.append((load(f"gdk_hall_post{k}_v1"), "#3f74c9", 1.0))
    parts.append((load(f"_hall_magnet{k}_model"), "#1d9a5b", 1.0))


def scene(path, cam, labels=(), size=(1600, 1000)):
    p = pv.Plotter(off_screen=True, window_size=size); p.set_background("white")
    for m, c, op in parts:
        p.add_mesh(m, color=c, opacity=op, smooth_shading=False, specular=0.15, ambient=0.35, diffuse=0.7)
    if labels:
        p.add_points(pv.PolyData(np.array([l[0] for l in labels], float)), color="black", point_size=10, render_points_as_spheres=True)
    p.add_light(pv.Light(position=(-200, 300, 500), intensity=0.9)); p.add_light(pv.Light(position=(300, 700, 300), intensity=0.5))
    p.camera_position = cam
    if labels:
        p.render(); ren = p.renderer
        for xyz, text in labels:
            ren.SetWorldPoint(float(xyz[0]), float(xyz[1]), float(xyz[2]), 1.0); ren.WorldToDisplay()
            dx, dy, _ = ren.GetDisplayPoint()
            p.add_text(text, position=(dx + 12, dy + 8), font_size=13, color="black", font_file="C:/Windows/Fonts/arial.ttf", viewport=False, shadow=False)
    p.screenshot(path); p.close(); print("saved", os.path.basename(path))


import json
P = json.load(open(os.path.join(HERE, "_hall_pos.json")))
MAG_Y, SENS_Y, SIDE = P["MAG_Y"], P["SENS_Y"], P["SIDE"]
labels = [((P["SIDE_MAGX"][str(SIDE[k])], MAG_Y[k], Z_FLOOR[k] + 4), f"магнит {k}") for k in range(4)]
labels += [((sum(P["SIDE_POST"][str(SIDE[k])]) / 2, SENS_Y[k], Z_FLOOR[k] + 4), f"датчик {k}") for k in range(4)]
scene(os.path.join(OUT, "hall_deka_1_iso.png"), [(-160, 470, 160), (0, 590, 10), (0, 0, 1)], labels)
scene(os.path.join(OUT, "hall_deka_2_etazh0.png"), [(-60, 470, 60), (8, 500, 6), (0, 0, 1)],
      [l for l in labels if l[1].endswith("0") or l[1].endswith("1")])
scene(os.path.join(OUT, "hall_deka_3_etazh3.png"), [(70, 600, 70), (6, 650, 18), (0, 0, 1)],
      [l for l in labels if l[1].endswith("3") or l[1].endswith("2")])
