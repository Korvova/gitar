# -*- coding: utf-8 -*-
"""Картинки ложа для пальца: деталь отдельно и 4 ложа на палубе секции-1.
Запуск: .venv-b123d\Scripts\python render_lozhe.py -> ../wiki/img/lozhe_*.png
"""
import os
import pyvista as pv
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "Print", "Print")
OUT = os.path.join(os.path.dirname(HERE), "wiki", "img")
pv.OFF_SCREEN = True


def load(name, loc=(0, 0, 0)):
    m = trimesh.load(os.path.join(SRC, name + ".stl"))
    m.apply_translation(loc)
    return pv.wrap(m)


def shot(parts, name, cam, size=(1400, 900)):
    p = pv.Plotter(off_screen=True, window_size=size)
    p.set_background("white")
    for mesh, color in parts:
        p.add_mesh(mesh, color=color, smooth_shading=False, specular=0.15, ambient=0.35, diffuse=0.7)
    p.add_light(pv.Light(position=(-200, -200, 400), intensity=0.9))
    p.camera_position = cam
    p.screenshot(os.path.join(OUT, name))
    p.close()
    print("ok", name)


import sys
V = sys.argv[1] if len(sys.argv) > 1 else "v2"
SUF, TAG = ("_v2", "_v2") if V == "v2" else ("", "_v0")
CY = (16, 42, 67, 91) if V == "v2" else (18, 34, 50, 66)
shot([(load("gs1_cart_lozhe" + SUF), "#3f74c9")], "lozhe" + TAG + "_detal.png", [(45, -55, 45), (0, 0, 5), (0, 0, 1)])
parts = [(load("gs1_p4_deck" + SUF, (0, 0, 23)), "#c9c4bb")]
for k, (y, x) in enumerate(zip(CY, (-20, 8, 20, -6))):
    parts.append((load("gs1_cart_lozhe" + SUF, (x, y, 26 if V == "v2" else 23.5)), ("#3f74c9", "#d9612f", "#5a9e61", "#b58a3c")[k]))
shot(parts, "lozhe" + TAG + "_na_grife.png", [(95, -70, 120), (0, 45, 28), (0, 0, 1)])
