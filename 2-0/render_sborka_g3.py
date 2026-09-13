# -*- coding: utf-8 -*-
"""Картинки для «Т. Гриф в деке» (дека v3, полный оборот кривошипа): хребет,
моторы, проставка мотора 0, кривошипы, ленты-хвосты, гребёнки «Е» — по шагам.
Рендер с настоящих STL (pyvista offscreen).

Запуск: .venv-b123d\\Scripts\\python 2-0\\render_sborka_g3.py  ->  wiki/img/deka3_*.png
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
FLANGE_Z = [-4.0, 0.0, 0.0, 0.0]
COMB_Y = (540, 590, 634)
LANE, R_CR = 10, 4.8
EAR_SIGN = [1, 1, -1, 1]
EAR_R, EAR_A = 43.85 / 2, math.radians(56)

C = {"base": "#c9c4bb", "mot": "#3d4046", "crank": "#3f74c9", "tail": "#d9612f",
     "comb": "#5a9e61", "spacer": "#b58a3c", "screw": "#c8102e", "empty": "#7a7570"}


def load(name, loc=(0, 0, 0), rz=0.0, rx=0.0):
    m = trimesh.load(os.path.join(SRC, name + ".stl"))
    if rx:
        m.apply_transform(trimesh.transformations.rotation_matrix(math.radians(rx), [1, 0, 0]))
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


bases = [(load("gdk1_base_v3", (0, 480, 0)), C["base"]), (load("gdk2_base_v3", (0, 640, 0)), C["base"])]
spacer = (load("gdk_spacer0_v3", (0, MY[0], 0)), C["spacer"])
motors = [(load(f"gdk_motor{k}_model", (0, MY[k], FLANGE_Z[k])), C["mot"]) for k in range(4)]
combs = [(load("gdk_comb_v3", (0, yg, 0)), C["comb"]) for yg in COMB_Y]


def crank(k, a=0.0):
    return (load(f"gdk_crank{k}_v3", (0, MY[k], 0), rz=a), C["crank"])


def tail(k, a=0.0):
    return (load(f"gdk_tail{k}_v3", (LANE, 480 + R_CR * math.sin(math.radians(a)), Z_FLOOR[k] + 0.05)), C["tail"])


TOP = [(-150, 470, 330), (5, 600, 5), (0, 0, 1)]
ZOOM0 = [(-70, 470, 110), (5, 515, 2), (0, 0, 1)]
BELOW = [(-170, 470, -200), (0, 600, -5), (0, 0, 1)]
COMBS_CAM = [(90, 520, 120), (5, 590, 8), (0, 0, 1)]

# 1. детали
lay = [(load("gdk1_base_v3", (-40, 0, 0)), C["base"]), (load("gdk2_base_v3", (40, 0, 0)), C["base"])]
lay += [(load(f"gdk_crank{k}_v3", (100 + k * 24, 20, 0), rx=180), C["crank"]) for k in range(4)]
lay += [(load(f"gdk_tail{k}_v3", (100 + k * 22, 50, 0)), C["tail"]) for k in range(4)]
lay += [(load("gdk_comb_v3", (205 + i * 22, 10, 0)), C["comb"]) for i in range(3)]
lay += [(load("gdk_comb_key_v3", (215 + i * 22, 60, 0)), C["spacer"]) for i in range(3)]
lay += [(load("gdk_spacer0_v3", (-120, 205, 4)), C["spacer"])]
lay += [(load(f"gdk_motor{k}_model", (-120, 20 + k * 45, 22)), C["mot"]) for k in range(4)]
scene(lay, "deka3_1_detali.png", [(20, -260, 330), (20, 110, 0), (0, 0, 1)])

# 2. стык Д1 и Д2
sc = [(x, 649, -1.2) for x in (-21, -9, 21)]
scene(bases + [dots(sc, C["screw"]), dots([(5, 649, -1.2)], C["empty"], r=1.0, h=0.6)],
      "deka3_2_styk.png", [(-110, 560, -170), (0, 650, 0), (0, 0, 1)])

# 3. моторы снизу (мотор 0 на проставке), винты сверху
ears = []
for k, my in enumerate(MY):
    s = EAR_SIGN[k]
    dx, dy = EAR_R * math.sin(EAR_A), EAR_R * math.cos(EAR_A)
    ears += [(s * dx, my + dy, 3.8), (-s * dx, my - dy, 3.8)]
scene(bases + [spacer] + motors, "deka3_3_motory.png", BELOW)
scene(bases + [spacer] + motors + [dots(ears, C["screw"], r=2.7, h=1.8)], "deka3_3b_vinty.png", TOP)

# 4. кривошип 0 на шестерёнку, 5. лента 0 прорезью на палец
scene(bases + [spacer] + motors + [crank(0)], "deka3_4_krivoship0.png", ZOOM0)
scene(bases + [spacer] + motors + [crank(0), tail(0)], "deka3_5_lenta0.png", ZOOM0)

# 6. все этажи без гребёнок
scene(bases + [spacer] + motors + [crank(k) for k in range(4)] + [tail(k) for k in range(4)],
      "deka3_6_etazhi.png", TOP)

# 7. гребёнки: поставить западнее ленты, задвинуть на 4.5 мм, вставить фиксатор
everything = bases + [spacer] + motors + [crank(k) for k in range(4)] + [tail(k) for k in range(4)]
combs_w = [(load("gdk_comb_v3", (-4.5, yg, 0)), C["comb"]) for yg in COMB_Y]
keys = [(load("gdk_comb_key_v3", (0, yg, 0)), C["spacer"]) for yg in COMB_Y]
CAM7 = [(-110, 520, 110), (0, 590, 6), (0, 0, 1)]
scene(everything + combs_w, "deka3_7a_grebenki_postavit.png", CAM7)
scene(everything + combs + keys, "deka3_7b_grebenki_zadvinut.png", CAM7)

# 8. проверка: кривошип 0 на 90° и 270° — кончик ленты в крайних положениях
for tag, a in (("a", 90), ("b", 270)):
    scene(bases + [spacer] + motors + [crank(0, a), tail(0, a)], f"deka3_8_{tag}.png",
          [(-40, 470, 150), (5, 500, 3), (0, 0, 1)])
