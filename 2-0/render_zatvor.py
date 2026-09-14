# -*- coding: utf-8 -*-
"""Картинки «затвора» под большим пальцем для «Т. Перемещение по грифу рукой»."""
import os, math, sys
import numpy as np
import pyvista as pv
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "Print", "Print")
OUT = os.path.join(HERE, "..", "wiki", "img")
pv.OFF_SCREEN = True
sys.path.insert(0, HERE)
WIN_YC, TRAVEL = 46.0, 6.0
CARTS_Y = [18, 34, 50, 66]; Z_FLOOR = [3, 8.4, 13.8, 19.2]; Z_DECK = 23
C = {"plate": "#d6d1c8", "cart": "#f2efe6", "zp": "#3f74c9", "sl": "#d9612f", "fsr": "#c8102e",
     "mag": "#1d9a5b", "sens": "#222222", "mot": "#1d9a5b", "spr": "#888888"}


def load(name, loc=(0, 0, 0), rz=0.0):
    m = trimesh.load(os.path.join(SRC, name + ".stl"), force="mesh")
    if rz:
        m.apply_transform(trimesh.transformations.rotation_matrix(math.radians(rz), [0, 0, 1]))
    m.apply_translation(loc); return pv.wrap(m)


def stack():
    s = [(load("gs1_p0_base"), C["plate"], 1), (load("gs1_p4_deck", (0, 0, Z_DECK)), C["plate"], 1)]
    for k in (1, 2, 3):
        s.append((load(f"gs1_p{k}_mid", (0, 0, Z_FLOOR[k] - 1.6)), C["plate"], 1))
    for k in range(4):
        s.append((load("gs1_cart", (0, CARTS_Y[k], Z_DECK + 3), rz=180), C["cart"], 1))
    return s


def slide_parts(dy=0.0):
    parts = [(load("zatvor_slide_v0", (0, WIN_YC + dy, 0)), C["sl"], 1)]
    parts.append((pv.Cylinder(center=(10.0, WIN_YC + dy, -2.5), direction=(1, 0, 0), radius=2.0, height=2.0), C["mag"], 1))
    for d in (-13, 0, 13):
        parts.append((pv.Cylinder(center=(0, WIN_YC + dy + d, -3.8), direction=(0, 0, 1), radius=5.0, height=3.0), C["mot"], 1))
    return parts


def fixed_parts():
    parts = [(load("zatvor_plate_v0"), C["zp"], 1)]
    for yw in (20.0, 72.0):
        parts.append((pv.Cylinder(center=(0, yw, -2.5), direction=(0, 1, 0), radius=6.35, height=0.3), C["fsr"], 1))
        for sx in (-7.5, 7.5):
            parts.append((pv.Cylinder(center=(sx, yw + (6 if yw < 46 else -6), -2.5), direction=(0, 1, 0), radius=1.9, height=8.0), C["spr"], 1))
    parts.append((pv.Cube(center=(15.4, 52.5, -2.9), x_length=1.5, y_length=4.0, z_length=3.0), C["sens"], 1))
    return parts


def scene(path, parts, cam, labels=(), size=(1600, 1000), zoom=1.0, edges=False):
    p = pv.Plotter(off_screen=True, window_size=size); p.set_background("white")
    for m, c, op in parts:
        p.add_mesh(m, color=c, opacity=op, smooth_shading=False, specular=0.15, ambient=0.35, diffuse=0.7)
        if edges:
            p.add_mesh(m.extract_feature_edges(feature_angle=40), color="#6f6a63", line_width=1.2)
    if labels:
        p.add_points(pv.PolyData(np.array([l[0] for l in labels], float)), color="black", point_size=10, render_points_as_spheres=True)
    p.add_light(pv.Light(position=(-200, -200, -400), intensity=0.8)); p.add_light(pv.Light(position=(200, 300, 300), intensity=0.6))
    p.camera_position = cam; p.camera.zoom(zoom)
    if labels:
        p.render(); ren = p.renderer
        for xyz, text in labels:
            ren.SetWorldPoint(float(xyz[0]), float(xyz[1]), float(xyz[2]), 1.0); ren.WorldToDisplay()
            dx, dy, _ = ren.GetDisplayPoint()
            p.add_text(text, position=(dx + 12, dy + 8), font_size=13, color="black", font_file="C:/Windows/Fonts/arial.ttf", viewport=False, shadow=False)
    p.screenshot(path); p.close(); print("saved", os.path.basename(path))


# 1. снизу: гриф перевёрнут, затвор под большим пальцем
allp = stack() + fixed_parts() + slide_parts(0)
scene(os.path.join(OUT, "zatvor_1_snizu.png"), allp, [(120, -120, -170), (0, 60, -3), (0, 0, -1)],
      [((0, 46, -6), "затвор под большим пальцем"), ((0, 20, -6), "FSR у порожка"), ((0, 72, -6), "FSR у деки"),
       ((15.4, 52.5, -6), "49E сбоку"), ((-23.5, 80, -6), "винт стяжки М3"), ((0, 120, -6), "пластина 5 мм")], zoom=1.3)
# 2. детали отдельно
det = [(load("zatvor_plate_v0"), C["zp"], 1), (load("zatvor_slide_v0", (45, 46, 0)), C["sl"], 1)]
scene(os.path.join(OUT, "zatvor_2_detali.png"), det, [(80, -110, -150), (10, 70, -3), (0, 0, -1)],
      [((0, 46, -6), "окно с пазами, гнёзда пружин, ниши FSR, карман 49E"), ((45, 46, -6), "затвор: язычки, пятачки, магнит, моторы")], zoom=1.4)
# 3. три положения затвора, вид снизу ортогонально
for tag, dy in (("porozhek", -TRAVEL), ("centr", 0.0), ("deka", +TRAVEL)):
    parts = [(load("zatvor_plate_v0"), C["zp"], 1)] + fixed_parts()[1:] + slide_parts(dy)
    scene(os.path.join(OUT, f"zatvor_3_{tag}.png"), parts, [(0, 46, -160), (0, 46, 0), (0, 1, 0)],
          [((11, 46 + dy, -6), "магнит"), ((15.4, 52.5, -6), "49E"), ((0, 20, -6), "FSR"), ((0, 72, -6), "FSR"),
           ((0, 46 + dy, -8), {"porozhek": "к порожку −6", "centr": "центр", "deka": "к деке +6"}[tag])],
          size=(900, 1000), zoom=1.15, edges=True)
