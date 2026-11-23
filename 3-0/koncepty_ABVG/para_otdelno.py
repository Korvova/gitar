# -*- coding: utf-8 -*-
"""Пара З1 + П1 на местах в ряду — неподвижные детали ОТДЕЛЬНЫМИ объектами (двигать руками в Blender):
общая окантовка с ямками оси, у каждого модуля стойка с кнопкой и стойка с пазом, крышки ям; платформы модулей в сборе.
Запуск: python para_otdelno.py → ../19.71_para_otdelno/*.stl, сцена — blender -b -P blender_para_otdelno.py"""
import os, sys, importlib
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from build123d import *
OUT = os.path.join(os.path.dirname(HERE), "19.71_para_otdelno"); os.makedirs(OUT, exist_ok=True)
for _f in os.listdir(OUT):
    if _f.endswith(".stl"): os.remove(os.path.join(OUT, _f))
M = {}
for mod in ("Z", "P"):
    os.environ["MOD"] = mod
    import modul_okantovka8 as Q
    if mod == "P": Q = importlib.reload(Q)
    M[mod] = dict(platform=dict(Q.platform), btns=Q.btns, pb=Q.PILLAR_BTN, pg=Q.PILLAR_GROOVE, lids=Q.lids, ypiv=Q.Y_PIV, Y0p=Q.Y0p, Y1p=Q.Y1p, Q=Q,
                  cart=Q.cart, mov=dict(Q.MOV[2]))
Q = M["P"]["Q"]; R, T, BB, HALF, XP, G, RW = Q.R, Q.T, Q.BB, Q.HALF, Q.XP, Q.G, Q.RW
IDX = {"Z": 0, "P": 1}
def place(mod, p): return R.place(IDX[mod], p)
def ywor(mod, y): return place(mod, Pos(0, y, 0) * Box(0.01, 0.01, 0.01)).center().Y
fl = {m: sorted((ywor(m, M[m]["Y0p"]), ywor(m, M[m]["Y1p"]))) for m in M}
y_lo = fl["Z"][0] - G - RW; y_hi = fl["P"][1] + G
rim = BB(-HALF, HALF, y_lo, y_hi, 0, T.Z_FL)
for m in M:
    rim -= BB(-XP - G, XP + G, fl[m][0] - G, fl[m][1] + G, -1, T.Z_FL + 1)
    yt = ywor(m, M[m]["ypiv"])
    for sx in (-1, 1):
        rim -= BB(*sorted((sx * (XP + G - 0.01), sx * (XP + G + 2.2))), yt - 1.4, yt + 1.4, 0.75, T.Z_FL + 1)
out = {"okantovka_obshaja": rim}
for m in M:
    nm = "Z" if m == "Z" else "P"
    out["%s_stojka_knopki" % nm] = place(m, M[m]["pb"])
    out["%s_stojka_paza" % nm] = place(m, M[m]["pg"])
    out["%s_kryshki_jam" % nm] = place(m, M[m]["lids"])
    out["%s_knopka" % nm] = place(m, M[m]["btns"])
    for n, p in M[m]["platform"].items():
        out["%s_%s" % (nm, n)] = place(m, p)
    for n, p in M[m]["mov"].items():
        out["%s_%s" % (nm, n)] = place(m, p)
for n, p in out.items():
    export_stl(Part() + p, os.path.join(OUT, n + ".stl"), tolerance=0.02, angular_tolerance=0.2)
print("готово:", len(out), "объектов →", OUT)
