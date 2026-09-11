# -*- coding: utf-8 -*-
"""Картинки для «Т. Инструкция по сборке»: этап А секции-1 (P0 + P1 + P4, плечи 0/1,
спицы 0/1, две тележки). Рендер с настоящих STL из 2-0/Print/Print (pyvista offscreen).

Запуск: .venv-b123d\\Scripts\\python 2-0\\render_sborka_a.py  ->  wiki/img/sborka_a_*.png
Позиции деталей — из gitara_sec1.py (проверка сборки): плиты в мировых координатах,
плечо/спица/тележка моделируются в нуле и ставятся на место.
"""
import os, math
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
LANE_X = 10
Z_FLOOR = [3, 8.4, 13.8, 19.2]
FLOOR = 1.6
Z_DECK_A = Z_FLOOR[1] + 3.8          # этап А: палуба прямо на стенках P1 (=12.2)
DECK_T = 3
TIE = [(23.5, 6), (-23.5, 6), (23.5, 80), (-23.5, 80), (23.5, 150), (-23.5, 150)]

C = {"plate": "#c9c4bb", "new_plate": "#9aa7b8", "arm": "#3f74c9", "spica": "#d9612f",
     "cart": "#f2efe6", "ghost": "#d8d4cc", "screw": "#c8102e", "pin": "#1d9a5b"}


def load(name, loc=(0, 0, 0), rz=0.0):
    m = trimesh.load(os.path.join(SRC, name + ".stl"))
    if rz:
        m.apply_transform(trimesh.transformations.rotation_matrix(math.radians(rz), [0, 0, 1]))
    m.apply_translation(loc)
    return pv.wrap(m)


def scene(parts, path, view="iso", labels=(), screws=False, size=(1600, 1100), zoom=1.0, focus=None):
    """parts: [(mesh, color, opacity)] ; labels: [(xyz, text)]"""
    p = pv.Plotter(off_screen=True, window_size=size)
    p.set_background("white")
    for mesh, color, op in parts:
        p.add_mesh(mesh, color=color, opacity=op, smooth_shading=False, show_edges=False,
                   specular=0.15, ambient=0.35, diffuse=0.7)
        if view == "top" and op >= 0.9:
            p.add_mesh(mesh.extract_feature_edges(feature_angle=40), color="#7a7570", line_width=1, opacity=0.9)
    if screws:
        pts = np.array([(x, y, Z_DECK_A + DECK_T + 0.5) for x, y in TIE], float)
        p.add_mesh(pv.PolyData(pts).glyph(geom=pv.Cylinder(radius=1.6, height=2.0, direction=(0, 0, 1)), scale=False),
                   color=C["screw"])
    if labels:
        pts = np.array([l[0] for l in labels], float)
        p.add_points(pv.PolyData(pts), color="black", point_size=11, render_points_as_spheres=True)
    p.add_light(pv.Light(position=(-200, -300, 500), intensity=0.9))
    p.add_light(pv.Light(position=(300, 100, 300), intensity=0.5))
    if view == "iso":
        p.camera_position = [(-170, -150, 150), (0, 85, 10), (0, 0, 1)]
        if focus is not None:
            f = np.array(focus, float); p.camera_position = [tuple(f + np.array((-190, -200, 190))), tuple(f), (0, 0, 1)]
    elif view == "iso2":
        p.camera_position = [(170, -170, 140), (0, 85, 10), (0, 0, 1)]
    elif view == "top":
        p.camera_position = [(0, 85, 400), (0, 85, 0), (0, 1, 0)]
    elif view == "south":
        p.camera_position = [(0, -260, 120), (0, 60, 8), (0, 0, 1)]
    if focus is not None:
        p.camera.focal_point = focus
    p.camera.zoom(zoom)
    if labels:
        p.render()
        ren = p.renderer
        for (xyz, text) in labels:
            ren.SetWorldPoint(float(xyz[0]), float(xyz[1]), float(xyz[2]), 1.0)
            ren.WorldToDisplay()
            dx, dy, _ = ren.GetDisplayPoint()
            p.add_text(text, position=(dx + 12, dy + 8), font_size=13, color="black",
                       font_file="C:/Windows/Fonts/arial.ttf", viewport=False, shadow=False)
    p.screenshot(path)
    p.close()
    print("saved", os.path.basename(path))


# ---- детали ----
p0 = load("gs1_p0_base")
p1 = load("gs1_p1_mid", (0, 0, Z_FLOOR[1] - FLOOR))
deck = load("gs1_p4_deck", (0, 0, Z_DECK_A))
arm = [load("gs1_arm%d" % k, (0, AXES_Y[k], Z_FLOOR[k] + 0.2)) for k in (0, 1)]
spica = [load("gs1_spica%d" % k, (LANE_X, AXES_Y[k] - 4, Z_FLOOR[k] + 0.2)) for k in (0, 1)]
carts = [load("gs1_cart", (0, CARTS_Y[k], Z_DECK_A + DECK_T), rz=180) for k in (0, 1)]   # вилкой на север

# 0. Обзор деталей этапа А, разложены на столе
lay = [("gs1_p0_base", (0, 0, 0), 0, C["plate"], "P0 дно (полка на юг)"),
       ("gs1_p1_mid", (70, 0, 0), 0, C["plate"], "P1 межэтажка"),
       ("gs1_p4_deck", (140, 0, 0), 0, C["plate"], "P4 палуба"),
       ("gs1_arm0", (-45, 60, 0), 0, C["arm"], "плечо 0 (штырь длиннее)"),
       ("gs1_arm1", (-70, 60, 0), 0, C["arm"], "плечо 1"),
       ("gs1_spica0", (-95, 0, 0), 0, C["spica"], "спица 0"),
       ("gs1_spica1", (-113, 0, 0), 0, C["spica"], "спица 1 (короче)"),
       ("gs1_cart", (-45, 130, 0), 0, C["cart"], "тележка ×2"),
       ("gs1_cart", (-70, 130, 0), 0, C["cart"], None)]
parts, labels = [], []
for name, loc, rz, col, lab in lay:
    m = load(name, loc, rz)
    parts.append((m, col, 1.0))
    if lab:
        b = m.bounds
        labels.append((((b[0] + b[1]) / 2, (b[2] + b[3]) / 2, b[4] + 3), lab))   # подпись у основания, не у верха штыря
scene(parts, os.path.join(OUT, "sborka_a_0_detali_v2.png"), view="iso", labels=labels, zoom=0.85,
      focus=(-10, 90, 0))

# 1. P0 + плечо 0
scene([(p0, C["plate"], 1), (arm[0], C["arm"], 1)],
      os.path.join(OUT, "sborka_a_1_plecho0_v2.png"), view="iso",
      labels=[((0, AXES_Y[0], 8), "ось плеча: стад P0"), ((0, CARTS_Y[0], 32), "штырь вверх"),
              ((LANE_X, AXES_Y[0], 8), "стад под спицу"), ((0, 172, 4), "полка на юг")], zoom=1.3)

# 2. + спица 0
scene([(p0, C["plate"], 1), (arm[0], C["arm"], 1), (spica[0], C["spica"], 1)],
      os.path.join(OUT, "sborka_a_2_spica0_v2.png"), view="iso",
      labels=[((LANE_X, AXES_Y[0], 8), "кольцо на стад"), ((LANE_X, 120, 8), "тело в жёлоб"),
              ((LANE_X, 178, 6), "хвост наружу")], zoom=1.3)

# 3. + P1, плечо 1, спица 1
scene([(p0, C["ghost"], 1), (arm[0], C["arm"], 0.35), (spica[0], C["spica"], 0.35),
       (p1, C["new_plate"], 0.55), (arm[1], C["arm"], 1), (spica[1], C["spica"], 1)],
      os.path.join(OUT, "sborka_a_3_p1_v2.png"), view="iso",
      labels=[((0, CARTS_Y[0] + 2, 14), "штырь плеча 0 в прорезь P1"), ((0, AXES_Y[1], 13), "плечо 1 на стад P1"),
              ((LANE_X, 130, 13), "спица 1")], zoom=1.3)

# 4. + палуба и тележки
scene([(p0, C["ghost"], 1), (arm[0], C["arm"], 0.35), (spica[0], C["spica"], 0.35), (p1, C["ghost"], 0.5),
       (arm[1], C["arm"], 0.35), (spica[1], C["spica"], 0.35),
       (deck, C["new_plate"], 0.5), (carts[0], C["cart"], 1), (carts[1], C["cart"], 1)],
      os.path.join(OUT, "sborka_a_4_paluba_v2.png"), view="iso",
      labels=[((0, CARTS_Y[0], 24), "тележка 0 вилкой на север"), ((0, CARTS_Y[1], 24), "тележка 1"),
              ((0, 120, 18), "палуба P4 ладами вверх")], zoom=1.3)

# 5. Винты: 6 × М3 сверху через приливы
scene([(p0, C["plate"], 1), (p1, C["plate"], 1), (deck, C["plate"], 1),
       (carts[0], C["cart"], 1), (carts[1], C["cart"], 1), (arm[0], C["arm"], 1), (arm[1], C["arm"], 1)],
      os.path.join(OUT, "sborka_a_5_vinty_v2.png"), view="iso", screws=True,
      labels=[((x, y, 17), "М3×20") for x, y in TIE], zoom=1.3)

# 6. Проверка: спицу тянем за хвост — плечо ±22°, тележка ходит ±20
def arm_at(k, phi):
    a = load("gs1_arm%d" % k, (0, 0, 0), rz=phi)
    a.translate((0, AXES_Y[k], Z_FLOOR[k] + 0.2), inplace=True)
    return a
def spica_at(k, dy):
    return load("gs1_spica%d" % k, (LANE_X, AXES_Y[k] - 4 + dy, Z_FLOOR[k] + 0.2))
def cart_at(k, dx):
    return load("gs1_cart", (dx, CARTS_Y[k], Z_DECK_A + DECK_T), rz=180)
phi = 22.6
dy = LANE_X * math.sin(math.radians(phi))
dx = 52 * math.sin(math.radians(phi))
parts = [(p0, C["ghost"], 1), (p1, C["ghost"], 0.4), (deck, C["ghost"], 0.35)]
for sgn, op in ((1, 1.0), (-1, 0.35)):
    parts += [(arm_at(0, sgn * phi), C["arm"], op), (spica_at(0, sgn * dy), C["spica"], op), (cart_at(0, -sgn * dx), C["cart"], op)]
parts += [(arm_at(1, 0), C["arm"], 0.25), (spica_at(1, 0), C["spica"], 0.25), (cart_at(1, 0), C["cart"], 0.25)]
scene(parts, os.path.join(OUT, "sborka_a_6_proverka_v2.png"), view="top",
      labels=[((LANE_X, 190, 6), "хвост спицы: ±4 мм"), ((-dx, CARTS_Y[0], 24), "тележка: ±20 мм"),
              ((0, AXES_Y[0], 8), "плечо ±22°")], zoom=1.25, focus=(0, 90, 10))
print("done")
