# -*- coding: utf-8 -*-
"""Один модуль на печать (19.11): MOD=P — модуль «П» (тележка над шестернями, клик через рейку с колоннами),
MOD=Z — модуль «З» (тележка за мотором на балке с колоннами). Всё из генераторов ряда 19.59–19.62, отдельно от ряда.
Запуск: MOD=P python pechat_modul.py  → папка ../19.63_modul_P_pechat (STL + asm + сцена)."""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from build123d import *
import ryad_V4d as R, datchiki_bok as DB
import trimesh
Z, V, K, T = R.Z, R.V, R.K, R.T
MOD = os.environ.get("MOD", "P")
OUT = os.path.join(os.path.dirname(HERE), "19.63_modul_%s_pechat" % MOD)
os.makedirs(os.path.join(OUT, "asm"), exist_ok=True)
if MOD == "P":
    base = R.base_P - DB.slots_p[0] - DB.slots_p[1]
    parts = [("01_osnovanie_P", base, 0, 1), ("02_rejka_s_kolonnami_P", R.fix_P, 180, 1), ("03_telezhka_P", R.cart_H, 180, 1)]
    post, n_post = DB.radial_post()[0], "10_stojka_49E_P_x2"
    asm = {"base": base, "rack": R.fix_P, "cart": R.cart_H, "btns": R.btns_P, "posts": DB.posts_p, "sens": DB.sens_p}
else:
    base = Z.base - DB.slots_z[0] - DB.slots_z[1]
    parts = [("01_osnovanie_Z", base, 0, 1), ("02_balka_s_kolonnami_Z", Z.beam, 180, 1), ("03_telezhka_Z", Z.cart, 180, 1), ("04_nepodvizhnaja_rejka_Z", V.fix_o, 180, 1)]
    post, n_post = None, "10_stojka_49E_Z_x2"
    asm = {"base": base, "rack": V.fix_o, "beam": Z.beam, "cart": Z.cart, "btns": Z.btns, "posts": DB.posts_z, "sens": DB.sens_z}
# крепёж мотора в дне (как в телескопе v3): 4 паза-ряда отверстий под винты на 45°, центр, окно под провода мотора
def motor_mount(b):
    for ang in (45, 135, 225, 315):
        for r_ in (5.6, 6.1, 6.6):
            b -= T.CZ(1.3, -1, T.Z_FL + 1, r_ * math.cos(math.radians(ang)), T.YM + r_ * math.sin(math.radians(ang)))
    b -= T.BB(-5.5, 5.5, T.YM + 6.0, T.YM + 12.5, -1, T.Z_FL + 1)                 # окно под провода мотора
    b -= T.CZ(5.0, T.Z_FL - 0.25, T.Z_FL + 1, 0, T.YM) + T.CZ(2.0, -1, T.Z_FL + 1, 0, T.YM)   # выемка под бобышку + центр
    return b
base = motor_mount(base)
parts[0] = (parts[0][0], base, parts[0][2], parts[0][3]); asm["base"] = base
if post is None:                                                                  # стойка З: одна из двух (вторая — зеркальная, печатать обе)
    post = DB.posts_z & T.BB(0, 60, -100, 100, -10, 60)                          # правая; вторую печатать такую же и ставить, повернув на 180°
parts += [("05_polzun", K.sl, 0, 1), ("06_shest_plav_x2", K.flo0, 0, 2), ("07_brusok", K.beam, 0, 1), ("08_shest_motora", K.gm, 180, 1),
          ("09_platforma_rotora_magnity", DB.plat, 0, 1), (n_post, post, 0, 2)]
asm.update({"slider": K.sl, "flo": K.flo0, "brusok": K.beam, "gm": K.gm, "plat": DB.plat, "mags": DB.mags, "motor": K.motor})
print("модуль %s → %s" % (MOD, OUT))
for n, p, rot, cnt in parts:
    p = Rot(rot, 0, 0) * (Part() + p); b = p.bounding_box(); p = Pos(-(b.min.X + b.max.X) / 2, -(b.min.Y + b.max.Y) / 2, -b.min.Z) * p
    f = os.path.join(OUT, n + ".stl"); export_stl(p, f, tolerance=0.01, angular_tolerance=0.1)
    m = trimesh.load(f); ov = float(m.area_faces[(m.face_normals[:, 2] < -0.72) & (m.triangles_center[:, 2] > 0.25)].sum())
    print("  %-32s ×%d  %5.1f × %5.1f × %4.1f  герм %s  нависание %.0f мм²" % (n, cnt, b.size.X, b.size.Y, b.size.Z, m.is_watertight, ov))
for n, p in asm.items():
    export_stl(Part() + p, os.path.join(OUT, "asm", n + ".stl"), tolerance=0.02, angular_tolerance=0.2)
open(os.path.join(OUT, "asm", "params.txt"), "w").write("%f %f %f %f %f" % (T.YM, K.Y_G, T.A, T.RF, T.RM))
