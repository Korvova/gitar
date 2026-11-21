# -*- coding: utf-8 -*-
# Детали модуля З в положении сборки — для инструкции (ножки балки отдельно, как на печати). Запуск: MOD=Z python sborka_Z_export.py
import os, sys
os.environ["MOD"] = "Z"
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from build123d import *
import modul_okantovka8 as Q
OUT = os.path.join(os.path.dirname(HERE), "19.70_pechat_okantovka8_Z", "asm_sborka"); os.makedirs(OUT, exist_ok=True)
BB = Q.BB
base = Q.platform["base"]
cut = Part() + [BB(*sorted((sx * Q.XP, sx * 30)), -40, 40, Q.Z_AW - 0.01, 40) for sx in (-1, 1)]
nav = base & cut
P = {"pol": base - cut, "noga_prav": Part() + [s for s in nav.solids() if s.center().X > 0], "noga_lev": Part() + [s for s in nav.solids() if s.center().X < 0]}
for k, v in Q.platform.items():
    if k != "base":
        P[k] = v
P.update({"okantovka": Q.fx, "knopki": Q.btns, "telezhka": Q.cart, "polzun": Q.SL, "flo": Q.K.flo0, "gm": Q.K.gm, "plat": Q.DB.plat, "mags": Q.DB.mags})
for n, p in P.items():
    export_stl(Part() + p, os.path.join(OUT, n + ".stl"), tolerance=0.02, angular_tolerance=0.2)
print("детали сборки:", sorted(P))
