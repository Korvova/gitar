# -*- coding: utf-8 -*-
"""Картинки для «Т. Гриф в деке»: хребет деки v2, моторы, гребёнки, хвосты лент и
кривошипы по шагам. Рендер с настоящих STL (pyvista offscreen).

Запуск: .venv-b123d\\Scripts\\python 2-0\\render_sborka_g.py  ->  wiki/img/deka_g_*.png
"""
import os
import math
import numpy as np
import pyvista as pv
import trimesh

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "2-0", "Print", "Print")
OUT = os.path.join(ROOT, "wiki", "img")
pv.OFF_SCREEN = True

Z_FLOOR = [3, 8.4, 13.8, 19.2]
MY = [515, 565, 615, 678]
COMB_Y = (540, 590, 634)
LANE = 10
EAR_SIGN = [1, 1, -1, 1]
EAR_R, EAR_A = 43.85 / 2, math.radians(56)

C = {"base": "#c9c4bb", "mot": "#3d4046", "crank": "#3f74c9", "tail": "#d9612f",
     "comb": "#5a9e61", "screw": "#c8102e", "empty": "#7a7570"}


def load(name, loc=(0, 0, 0), rz=0.0, flip=False):
    m = trimesh.load(os.path.join(SRC, name + ".stl"))
    if flip:
        m.apply_transform(trimesh.transformations.rotation_matrix(math.pi, [1, 0, 0]))
    if rz:
        m.apply_transform(trimesh.transformations.rotation_matrix(math.radians(rz), [0, 0, 1]))
    m.apply_translation(loc)
    return pv.wrap(m)


def dots(points, color, r=2.2, h=2.0):
    pts = np.array(points, float)
    return (pv.PolyData(pts).glyph(geom=pv.Cylinder(radius=r, height=h, direction=(0, 0, 1)),
                                   scale=False), color)


def scene(parts, name, cam, size=(1600, 1000)):
    p = pv.Plotter(off_screen=True, window_size=size)
    p.set_background("white")
    for mesh, color in parts:
        p.add_mesh(mesh, color=color, smooth_shading=False, specular=0.15, ambient=0.35, diffuse=0.7)
    p.add_light(pv.Light(position=(-300, 300, 600), intensity=0.9))
    p.add_light(pv.Light(position=(300, 900, 300), intensity=0.5))
    p.camera_position = cam
    p.screenshot(os.path.join(OUT, name))
    p.close()
    print("ok", name)


bases = [(load("gdk1_base_v2", (0, 480, 0)), C["base"]), (load("gdk2_base_v2", (0, 640, 0)), C["base"])]
motors = [(load(f"gdk_motor{k}_model", (0, MY[k], 0)), C["mot"]) for k in range(4)]
combs = [(load("gdk_comb", (0, yg, 0)), C["comb"]) for yg in COMB_Y]


def tail(k):
    return (load(f"gdk_tail{k}_v2", (LANE, 480, Z_FLOOR[k] + 0.05)), C["tail"])


def crank(k):
    return (load(f"gdk_crank{k}_v2", (0, MY[k], 0)), C["crank"])


TOP = [(-150, 470, 330), (5, 600, 5), (0, 0, 1)]
ZOOM0 = [(-70, 470, 110), (5, 515, 5), (0, 0, 1)]
BELOW = [(-170, 470, -200), (0, 600, -5), (0, 0, 1)]

# 1. детали на столе
lay = [(load("gdk1_base_v2", (-40, 0, 0)), C["base"]), (load("gdk2_base_v2", (40, 0, 0)), C["base"])]
lay += [(load(f"gdk_crank{k}_v2", (100 + k * 26, 20, 0), flip=True), C["crank"]) for k in range(4)]
lay += [(load(f"gdk_tail{k}_v2", (100 + k * 14, 50, 0)), C["tail"]) for k in range(4)]
lay += [(load("gdk_comb", (175 + i * 32, 10, 0)), C["comb"]) for i in range(3)]
lay += [(load(f"gdk_motor{k}_model", (-120, 20 + k * 45, 22)), C["mot"]) for k in range(4)]
scene(lay, "deka_g_1_detali.png", [(20, -260, 330), (20, 110, 0), (0, 0, 1)])

# 2. стык Д1 и Д2 снизу: три винта, среднее у жёлоба пустое
sc = [(x, 649, -1.2) for x in (-21, -9, 21)]
scene(bases + [dots(sc, C["screw"]), dots([(5, 649, -1.2)], C["empty"], r=1.0, h=0.6)],
      "deka_g_2_styk.png", [(-110, 560, -170), (0, 650, 0), (0, 0, 1)])

# 3. моторы снизу, винты ушей сверху
ears = []
for k, my in enumerate(MY):
    s = EAR_SIGN[k]
    dx, dy = EAR_R * math.sin(EAR_A), EAR_R * math.cos(EAR_A)
    ears += [(s * dx, my + dy, 3.8), (-s * dx, my - dy, 3.8)]
scene(bases + motors, "deka_g_3_motory.png", BELOW)
scene(bases + motors + [dots(ears, C["screw"], r=2.7, h=1.8)], "deka_g_3b_vinty.png", TOP)

# 4. гребёнки
scene(bases + motors + combs, "deka_g_4_grebenki.png", TOP)

# 5. этаж 0: хвост 0 и кривошип 0
scene(bases + motors + combs + [tail(0)], "deka_g_5a_hvost0.png", ZOOM0)
scene(bases + motors + combs + [tail(0), crank(0)], "deka_g_5b_krivoship0.png", ZOOM0)

# 6. все этажи
scene(bases + motors + combs + [tail(k) for k in range(4)] + [crank(k) for k in range(4)],
      "deka_g_6_vse.png", TOP)

# 7. проверка: кривошип 0 в крайних положениях — кончик ленты уезжает
for tag, th in (("minus", -38), ("plus", 38)):
    dy = 7.6 * math.sin(math.radians(th))
    t0 = (load("gdk_tail0_v2", (LANE, 480 + dy, Z_FLOOR[0] + 0.05)), C["tail"])
    c0 = (load("gdk_crank0_v2", (0, MY[0], 0), rz=th), C["crank"])
    scene(bases + motors + combs + [t0, c0], f"deka_g_7_{tag}.png",
          [(-40, 470, 150), (5, 500, 3), (0, 0, 1)])
