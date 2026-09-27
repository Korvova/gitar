# -*- coding: utf-8 -*-
"""Окно: стенд v2 с шатуном в движении по физике MuJoCo (trace_mini2.json из dump_trace_mini2.py).

Настоящие детали стенда (STL), движение — из симуляции: мотор тянет кривошип, палец давит на ложе
3 Н против хода, трение в шарнирах. На экране — угол кривошипа, ложе, момент мотора.
Клавиши: 1 — мотор 0.2 Н·м (крутит), 2 — мотор 0.05 Н·м (срывается под пальцем), пробел — пауза.
Запуск: .venv-b123d\\Scripts\\python view_mini2.py
"""
import json
import math
import os
import time

import numpy as np
import pyvista as pv

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "Print", "Print")
TR = json.load(open(os.path.join(HERE, "trace_mini2.json")))
CART_Y, MY, R_CR, RS, LB = 16.0, 80.0, 10.0, 18.0, 32.51
AX = CART_Y + LB
Z_ARM, Z_LINK, Z_DECK, DECK_T, RUN = 3.2, 5.0, 21.0, 3.0, 2.9


def mesh(name):
    return pv.read(os.path.join(P, name + ".stl"))


def mat(x, y, z, rz):
    c, s = math.cos(rz), math.sin(rz)
    m = np.eye(4)
    m[:2, :2] = [[c, -s], [s, c]]
    m[:3, 3] = (x, y, z)
    return m


pl = pv.Plotter(window_size=(1100, 800), title="Стенд одного пальца v2 — физика MuJoCo")
pl.set_background("#9aa3ad")
pl.add_mesh(mesh("mini2_base"), color="#dddde2", opacity=0.25)
deck = pl.add_mesh(mesh("mini2_deck"), color="#e8dfcf", opacity=0.18)
deck.user_matrix = mat(0, 0, Z_DECK, 0)
mot = pl.add_mesh(mesh("gdk_motor0_model"), color="#40454c", opacity=0.6)
mot.user_matrix = mat(0, MY, -4.0, 0)
sp = pl.add_mesh(mesh("gdk_spacer0_x2"), color="#40454c", opacity=0.6)
sp.user_matrix = mat(0, MY, 0, 0)
crank = pl.add_mesh(mesh("mini2_crank"), color="#d9612e")
arm = pl.add_mesh(mesh("mini2_arm"), color="#3f73cc")
link = pl.add_mesh(mesh("mini2_shatun"), color="#40b35a")
lozhe = pl.add_mesh(mesh("gs1_lozhe_v3"), color="#f2b84b")
txt = pl.add_text("", position="upper_left", font_size=12, color="black")
pl.add_text("1 — мотор 0.2 Н·м   2 — мотор 0.05 Н·м   пробел — пауза", position="lower_left", font_size=10, color="black")
pl.camera_position = [(60, -40, 170), (0, 55, 8), (0, 0, 1)]

state = {"key": "strong", "i": 0, "pause": False}
pl.add_key_event("1", lambda: state.update(key="strong", i=0))
pl.add_key_event("2", lambda: state.update(key="weak", i=0))
pl.add_key_event("space", lambda: state.update(pause=not state["pause"]))

pl.show(interactive_update=True, auto_close=False)
while True:
    run = TR[state["key"]]
    tr = run["trace"]
    t, c, a, f = tr[state["i"]]
    cx, cy = R_CR * math.cos(c), MY + R_CR * math.sin(c)          # палец кривошипа
    sx, sy = RS * math.cos(a), AX + RS * math.sin(a)             # стад плеча
    crank.user_matrix = mat(0, MY, 0, c)
    arm.user_matrix = mat(0, AX, Z_ARM, a)
    link.user_matrix = mat(cx, cy, Z_LINK, math.atan2(-(sx - cx), sy - cy))
    lozhe.user_matrix = mat(LB * math.sin(a), CART_Y, Z_DECK + DECK_T - RUN, 0)
    txt.SetText(2, "мотор до %.2f Н·м, палец %.0f Н против хода\nвремя %.2f с   кривошип %6.0f°\nложе %+5.1f мм   момент мотора %.3f Н·м%s"
                % (run["t_lim"], run["force"], t, math.degrees(c), LB * math.sin(a), abs(f),
                   "   — СРЫВ: мотор не тянет" if run["t_lim"] < 0.1 and abs(f) >= run["t_lim"] * 0.99 else ""))
    pl.update()
    if pl.render_window is None or getattr(pl, "_closed", False):
        break
    if not state["pause"]:
        state["i"] = (state["i"] + 1) % len(tr)
    time.sleep(0.005)
