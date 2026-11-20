# -*- coding: utf-8 -*-
"""Ряд из 4 (З1 П1 ‖ П2 З2) модулей в окантовке 8 — и пара З1+П1 (окантовка 8) на месте в ряду: шаг площадок PITCH (по умолчанию 17), оба развёрнуты, хвост З над задней частью П.
Общая окантовка (бока на всю длину + торцы) + вазы и кнопки обоих. Проверка: детали З × детали П в покое и когда нажат один из них.
Запуск: python para_ryad8.py → ../19.68_para_ryad8/asm (детали модулей в своих координатах + общая окантовка), сцена — blender_para8.py с PARA=ryad."""
import os, sys, math, importlib
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from build123d import *
OUT = os.path.join(os.path.dirname(HERE), "19.69_ryad4_okantovka8"); os.makedirs(os.path.join(OUT, "asm"), exist_ok=True)
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
TY = ["Z" if t == "З" else "P" for t in R.TYPE]
def place(i, p):
    return R.place(i, p)
def pressed(mod, p):
    d = M[mod]
    return Pos(0, d["ypiv"], d["zpiv"]) * Rot(d["ang"], 0, 0) * Pos(0, -d["ypiv"], -d["zpiv"]) * p
bad = 0
for i in range(3):                                                                # соседи: покой, нажат один из двух; ход тележек 0/середина/край
    a_, b_ = i, i + 1; ma, mb = TY[a_], TY[b_]
    for pa_, pb_ in ((False, False), (True, False), (False, True)):
        tag = "%d%s/%d%s %s" % (a_ + 1, ma, b_ + 1, mb, "покой" if not (pa_ or pb_) else ("нажат %d" % (a_ + 1) if pa_ else "нажат %d" % (b_ + 1)))
        As = {n: place(a_, pressed(ma, p) if pa_ else p) for n, p in M[ma]["platform"].items()}
        Bs = {n: place(b_, pressed(mb, p) if pb_ else p) for n, p in M[mb]["platform"].items()}
        for k in (0, 2, 4):
            As.update({("~%s%d" % (n, k)): place(a_, pressed(ma, q) if pa_ else q) for n, q in M[ma]["mov"][k].items()})
            Bs.update({("~%s%d" % (n, k)): place(b_, pressed(mb, q) if pb_ else q) for n, q in M[mb]["mov"][k].items()})
        for na, qa in As.items():
            for nb, qb in Bs.items():
                if na.startswith("~") and nb.startswith("~") and na[-1] != nb[-1] and False: pass
                v = iv(qa, qb)
                if v > 0.02: bad += 1; print("  %s: %s × %s %.2f" % (tag, na, nb, v))
# общая окантовка: бока на всю длину, торцы снаружи (у З), окно под пол каждого модуля, ямки под язычки, вазы
G, RW, XP = 0.3, 8.0, M["P"]["Q"].XP
fl = []
for i in range(4):
    m = TY[i]
    ys = sorted((place(i, Pos(0, M[m]["Y0p"], 0) * Box(0.01, 0.01, 0.01)).center().Y, place(i, Pos(0, M[m]["Y1p"], 0) * Box(0.01, 0.01, 0.01)).center().Y))
    fl.append(ys)
y_lo, y_hi = min(f[0] for f in fl) - G - RW, max(f[1] for f in fl) + G + RW
rim = BB(-HALF, HALF, y_lo, y_hi, 0, T.Z_FL)
for f in fl:
    rim -= BB(-XP - G, XP + G, f[0] - G, f[1] + G, -1, T.Z_FL + 1)
for i in range(4):
    m = TY[i]
    yt = place(i, Pos(0, M[m]["ypiv"], 0) * Box(0.01, 0.01, 0.01)).center().Y
    for sx in (-1, 1):
        rim -= BB(*sorted((sx * (XP + G - 0.01), sx * (XP + G + 2.2))), yt - 1.4, yt + 1.4, 0.75, T.Z_FL + 1)
    rim += place(i, M[m]["fx"]) & BB(-HALF, HALF, -300, 300, T.Z_FL + 0.01, 40)
fx_all = rim
print("полы модулей:", ["%.1f..%.1f" % tuple(f) for f in fl], "зазоры:", ["%.2f" % (fl[i + 1][0] - fl[i][1]) for i in range(3)])
for i in range(4):
    m = TY[i]
    for n, p in M[m]["platform"].items():
        for nm, pose in (("покой", p), ("нажато", pressed(m, p))):
            v = iv(place(i, pose), fx_all)
            if v > 0.02: bad += 1; print("  модуль %d %s × окантовка (%s) %.2f" % (i + 1, n, nm, v))
print("ряд З П ‖ П З в окантовке: %s | площадки %s, моторы %s, длина ряда %.1f" % ("ЧИСТО" if not bad else "%d проблем" % bad, R.PADC, ["%.1f" % c for c in R.CM], y_hi - y_lo))
for mod in ("Z", "P"):
    for n, p in M[mod]["platform"].items():
        export_stl(Part() + p, os.path.join(OUT, "asm", "%s_%s.stl" % (mod, n)), tolerance=0.02, angular_tolerance=0.2)
    export_stl(Part() + M[mod]["btns"], os.path.join(OUT, "asm", "%s_btns.stl" % mod), tolerance=0.02, angular_tolerance=0.2)
export_stl(fx_all, os.path.join(OUT, "asm", "frame_ryad.stl"), tolerance=0.02, angular_tolerance=0.2)
open(os.path.join(OUT, "asm", "ryad.txt"), "w").write(repr(dict(CM=R.CM, ROT=R.ROT, TY=TY, YM=YM)))
