# -*- coding: utf-8 -*-
"""Картинки для «Т. Инструкция по сборке: гриф с моторами», этап В: секции 2 и 3
пристыкованы к собранной секции-1, рейки и ленты по этажам, планки-потолки,
фретборды. Рендер с настоящих STL из 2-0/Print/Print (pyvista offscreen).

Запуск: .venv-b123d\\Scripts\\python 2-0\\render_sborka_v.py  ->  wiki/img/sborka_v_*.png
Позиции — из проверок сборки gitara_sec1.py / gitara_sec2.py / gitara_deka.py.
"""
import os
import math
import numpy as np
import pyvista as pv
import trimesh

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "2-0", "Print", "Print")
OUT = os.path.join(ROOT, "wiki", "img")
os.makedirs(OUT, exist_ok=True)
pv.OFF_SCREEN = True

CARTS_Y = [18, 34, 50, 66]
AXES_Y = [y + 52 for y in CARTS_Y]
LANE = 10
Z_FLOOR = [3, 8.4, 13.8, 19.2]
FLOOR = 1.6
Z_DECK, DECK_T = 23, 3
SEC_Y = (160, 320)
JX = (-21, -9, 5, 21)

C = {"sec1": "#d8d4cc", "base": "#c9c4bb", "tray": "#9aa7b8", "band": "#d9612f",
     "spica": "#e39a6f", "cap": "#3f74c9", "fret": "#f2efe6", "screw": "#c8102e",
     "noscrew": "#7a7570"}


def load(name, loc=(0, 0, 0), rz=0.0):
    m = trimesh.load(os.path.join(SRC, name + ".stl"))
    if rz:
        m.apply_transform(trimesh.transformations.rotation_matrix(math.radians(rz), [0, 0, 1]))
    m.apply_translation(loc)
    return pv.wrap(m)


def dots(points, color, r=1.9, h=3.0):
    pts = np.array(points, float)
    return (pv.PolyData(pts).glyph(geom=pv.Cylinder(radius=r, height=h, direction=(0, 0, 1)),
                                   scale=False), color, 1.0)


def scene(parts, path, cam, size=(1700, 1000)):
    p = pv.Plotter(off_screen=True, window_size=size)
    p.set_background("white")
    for mesh, color, op in parts:
        p.add_mesh(mesh, color=color, opacity=op, smooth_shading=False,
                   specular=0.15, ambient=0.35, diffuse=0.7)
    p.add_light(pv.Light(position=(-300, -200, 600), intensity=0.9))
    p.add_light(pv.Light(position=(300, 400, 300), intensity=0.5))
    p.camera_position = cam
    p.screenshot(path)
    p.close()
    print("ok", os.path.basename(path))


# ---- секция-1 в сборе (результат инструкции этапов А и Б) ----
sec1 = [(load("gs1_p0_base"), C["sec1"], 1.0)]
sec1 += [(load(f"gs1_p{k}_mid", (0, 0, Z_FLOOR[k] - FLOOR)), C["sec1"], 1.0) for k in (1, 2, 3)]
sec1 += [(load("gs1_p4_deck", (0, 0, Z_DECK)), C["sec1"], 1.0)]
sec1 += [(load("gs1_cart", (0, CARTS_Y[k], Z_DECK + DECK_T), rz=180), C["fret"], 1.0) for k in range(4)]
spicas = [(load(f"gs1_spica{k}", (LANE, AXES_Y[k] - 4, Z_FLOOR[k] + 0.2)), C["spica"], 1.0)
          for k in range(4)]

bases = [(load("gs2_base", (0, 160, 0)), C["base"], 1.0),
         (load("gs3_base", (0, 320, 0)), C["base"], 1.0)]


def trays(floors):
    return [(load("gs2_tray", (0, y0, Z_FLOOR[k] - 1.6)), C["tray"], 1.0)
            for y0 in SEC_Y for k in floors]


def bands(floors):
    return [(load("gdk_ext", (LANE, y0, Z_FLOOR[k] + 0.05)), C["band"], 1.0)
            for y0 in SEC_Y for k in floors]


caps = [(load("gs2_cap", (0, y0, 21.0)), C["cap"], 1.0) for y0 in SEC_Y]
frets = [(load("gs2_fret", (0, 160, 23)), C["fret"], 1.0),
         (load("gs3_fret", (0, 320, 23)), C["fret"], 1.0)]

ISO = [(-230, 40, 520), (5, 250, 8), (0, 0, 1)]
JOINT = [(-15, 120, 230), (10, 205, 3), (0, 1, 0)]

# шаг В0: детали этапа на столе (раскладка)
lay = [(load("gs2_base", (-70, 0, 0)), C["base"], 1.0), (load("gs3_base", (0, 0, 0)), C["base"], 1.0)]
lay += [(load("gs2_tray", (60 + i * 16, 0, 0)), C["tray"], 1.0) for i in range(8)]
lay += [(load("gs2_fret", (-150, 0, 0)), C["fret"], 1.0), (load("gs3_fret", (-215, 0, 0)), C["fret"], 1.0)]
lay += [(load("gs2_cap", (180 + i * 14, 0, 0)), C["cap"], 1.0) for i in range(2)]
lay += [(load("gdk_ext", (230 + i * 12, 0, 0)), C["band"], 1.0) for i in range(8)]
scene(lay, os.path.join(OUT, "sborka_v_0_detali.png"),
      [(40, -330, 330), (40, 95, 0), (0, 0, 1)])

# шаг В1: стыки секций снизу — 3 винта на стык, у жёлоба (X=+5) без винта
sc = [(x, y, -1.8) for y in (169, 329) for x in JX if x != 5]
no = [(5, y, -1.8) for y in (169, 329)]
scene(sec1 + bases + [dots(sc, C["screw"]), dots(no, C["noscrew"], r=0.9, h=1.0)],
      os.path.join(OUT, "sborka_v_1_styki.png"),
      [(-200, 60, -230), (0, 250, 5), (0, 0, 1)])

# шаг В2: этаж 0 — рейки в обе секции, две ленты-продолжения на хвост спицы-0
scene(sec1 + spicas[:1] + bases + trays([0]) + bands([0]),
      os.path.join(OUT, "sborka_v_2_etazh0.png"), JOINT)

# шаг В3: этажи 1–3 так же, на верхнюю ленту — планка-потолок
scene(sec1 + spicas + bases + trays(range(4)) + bands(range(4)) + caps,
      os.path.join(OUT, "sborka_v_3_etazhi.png"), ISO)

# шаг В4: фретборды — пеньки планок в дырки, 7 винтов М3×10 на секцию
fx = []
for y0, wy in ((160, (12, 148)), (320, (12, 148))):
    fx += [(x, y0 + w, 26.5) for x in (2.5, 17.7) for w in wy]
    fx += [(-23.8, y0 + w, 26.5) for w in (40, 85, 130)]
scene(sec1 + bases + trays(range(4)) + frets + [dots(fx, C["screw"])],
      os.path.join(OUT, "sborka_v_4_fretbordy.png"), ISO)
