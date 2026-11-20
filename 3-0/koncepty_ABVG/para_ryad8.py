# -*- coding: utf-8 -*-
"""Пара З1 + П1 (окантовка 8) на месте в ряду: шаг площадок PITCH (по умолчанию 17), оба развёрнуты, хвост З над задней частью П.
Общая окантовка (бока на всю длину + торцы) + вазы и кнопки обоих. Проверка: детали З × детали П в покое и когда нажат один из них.
Запуск: python para_ryad8.py → ../19.68_para_ryad8/asm (детали модулей в своих координатах + общая окантовка), сцена — blender_para8.py с PARA=ryad."""
import os, sys, math, importlib
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from build123d import *
OUT = os.path.join(os.path.dirname(HERE), "19.68_para_ryad8"); os.makedirs(os.path.join(OUT, "asm"), exist_ok=True)
for _f in os.listdir(os.path.join(OUT, "asm")):
    if _f.endswith(".stl"): os.remove(os.path.join(OUT, "asm", _f))
M = {}
for mod in ("Z", "P"):
    os.environ["MOD"] = mod
    import modul_okantovka8 as Q
    if mod == "P": Q = importlib.reload(Q)
    M[mod] = dict(platform=dict(Q.platform), mov=[dict(m) for m in Q.MOV], btns=Q.btns, fx=Q.fx, ypiv=Q.Y_PIV, zpiv=Q.Z_PIV, ang=Q.ang, YB=Q.YB, Y0p=Q.Y0p, Y1p=Q.Y1p, Q=Q)
R, T = M["P"]["Q"].R, M["P"]["Q"].T
BB, HALF, YM = T.BB, T.HALF, T.YM
iv = M["P"]["Q"].iv
CY = {"Z": R.CM[0] + YM, "P": R.CM[1] + YM}                                       # центр поворота модуля (ось мотора) в ряду
def place(mod, p):
    return Pos(0, CY[mod], 0) * Rot(0, 0, 180) * p
def pressed(mod, p):
    d = M[mod]
    return Pos(0, d["ypiv"], d["zpiv"]) * Rot(d["ang"], 0, 0) * Pos(0, -d["ypiv"], -d["zpiv"]) * p

bad = 0
pairs = []
for pz in (False, True):
    for pp in (False, True):
        if pz and pp: continue
        Zs = {n: place("Z", pressed("Z", p) if pz else p) for n, p in M["Z"]["platform"].items()}
        Ps = {n: place("P", pressed("P", p) if pp else p) for n, p in M["P"]["platform"].items()}
        tag = "нажат З" if pz else ("нажат П" if pp else "покой")
        for a, pa in Zs.items():
            for b, pb in Ps.items():
                v = iv(pa, pb)
                if v > 0.02: bad += 1; print("  %s: З %s × П %s %.2f" % (tag, a, b, v))
        for k in (0, 2, 4):                                                      # тележки/ползуны в крайних и средней позиции
            for j in (0, 2, 4):
                for a, pa in M["Z"]["mov"][k].items():
                    pa_w = place("Z", pressed("Z", pa) if pz else pa)
                    for b, pb in {**Ps, **{("~" + n): place("P", pressed("P", q) if pp else q) for n, q in M["P"]["mov"][j].items()}}.items():
                        v = iv(pa_w, pb)
                        if v > 0.02: bad += 1; print("  %s: З(ход %d) %s × П %s %.2f" % (tag, k, a, b, v))
                for b, pb in M["P"]["mov"][j].items():
                    pb_w = place("P", pressed("P", pb) if pp else pb)
                    for a, pa in Zs.items():
                        v = iv(pb_w, pa)
                        if v > 0.02: bad += 1; print("  %s: П(ход %d) %s × З %s %.2f" % (tag, j, b, a, v))
# общая окантовка: бока на всю длину, торцы снаружи; пол каждого модуля — своё окно
yz0, yz1 = CY["Z"] - M["Z"]["Y1p"], CY["Z"] - M["Z"]["Y0p"]
yp0, yp1 = CY["P"] - M["P"]["Y1p"], CY["P"] - M["P"]["Y0p"]
G, RW, XP = 0.3, 8.0, M["P"]["Q"].XP
y_lo, y_hi = min(yz0, yp0) - G - RW, max(yz1, yp1) + G + RW
rim = BB(-HALF, HALF, y_lo, y_hi, 0, T.Z_FL)
for a_, b_ in ((yz0, yz1), (yp0, yp1)):
    rim -= BB(-XP - G, XP + G, a_ - G, b_ + G, -1, T.Z_FL + 1)
print("пол З: y %.1f..%.1f, пол П: y %.1f..%.1f, зазор между полами %.2f (нужно ≥0.3)" % (yz0, yz1, yp0, yp1, max(yp0 - yz1, yz0 - yp1)))
for mod in ("Z", "P"):
    v_ = place(mod, M[mod]["fx"]) & BB(-HALF, HALF, -200, 200, T.Z_FL + 0.01, 40)   # вазы своего модуля (без своей окантовки)
    rim += v_
for mod in ("Z", "P"):                                                            # пазы под боковые язычки-оси
    yt = CY[mod] - M[mod]["ypiv"]
    for sx in (-1, 1):
        rim -= BB(*sorted((sx * (XP + G - 0.01), sx * (XP + G + 2.2))), yt - 1.4, yt + 1.4, 0.7, 2.1)
fx_all = rim
for mod in ("Z", "P"):
    for n, p in M[mod]["platform"].items():
        for nm, pose in (("покой", p), ("нажато", pressed(mod, p))):
            v = iv(place(mod, pose), fx_all)
            if v > 0.02: bad += 1; print("  %s %s × общая окантовка (%s) %.2f" % (mod, n, nm, v))
padZ = CY["Z"] - R.C_Z; padP = CY["P"] - R.C_H
print("пара З+П в ряду: %s | шаг площадок %.1f, длина пары %.1f" % ("ЧИСТО" if not bad else "%d проблем" % bad, padP - padZ, y_hi - y_lo))
for mod in ("Z", "P"):
    for n, p in M[mod]["platform"].items():
        export_stl(Part() + p, os.path.join(OUT, "asm", "%s_%s.stl" % (mod, n)), tolerance=0.02, angular_tolerance=0.2)
    export_stl(Part() + M[mod]["btns"], os.path.join(OUT, "asm", "%s_btns.stl" % mod), tolerance=0.02, angular_tolerance=0.2)
export_stl(fx_all, os.path.join(OUT, "asm", "frame_pair.stl"), tolerance=0.02, angular_tolerance=0.2)
open(os.path.join(OUT, "asm", "pair.txt"), "w").write("%f %f" % (CY["Z"], CY["P"]))
