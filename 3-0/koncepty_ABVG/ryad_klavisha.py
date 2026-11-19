# -*- coding: utf-8 -*-
"""Ряд из 4 модулей-клавиш (19.11, владелец): З1 П1 ‖ П2 З2, каждый модуль качается сам на своей оси, общая рама под рядом.
Полы соседей З/П раньше были общими (хвост З с кнопками заходит под задний край П) — теперь пол разрезан «пазлом»:
у З в зоне хвоста остаются два бока-рога со стаканами (|x| ≥ 15.7), у П — узкий хвост под мотором (|x| ≤ 15.4), щели 0.3.
Оси: у П — сзади, ребро под узким хвостом, крючки над кольцом мотора; у З — сзади, на внешнем краю ряда.
Запуск: python ryad_klavisha.py → ../19.65_klavisha_ryad/asm (детали модулей в своих координатах + рама ряда), сцена — blender_ryad_klavisha.py."""
import os, sys, math
os.environ["KLAV"] = "1"
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from build123d import *
import ryad_V4d as R, datchiki_bok as DB
Z, V, K, T = R.Z, R.V, R.K, R.T
BB, CZ, HALF, YM, S, A, RF, RM = T.BB, T.CZ, T.HALF, T.YM, T.S, T.A, T.RF, T.RM
OUT = os.path.join(os.path.dirname(HERE), "19.65_klavisha_ryad"); os.makedirs(os.path.join(OUT, "asm"), exist_ok=True)
GAP, FR, TRAVEL = Z.GAP, 1.2, 0.35
X_SPLIT, Y_SPLIT_Z, Y_SPLIT_P = 15.55, -11.75, 19.65                              # граница «пазла» (в своих координатах модуля)

def iv(a, b):
    ba, bb_ = a.bounding_box(), b.bounding_box()
    if ba.min.X > bb_.max.X or bb_.min.X > ba.max.X or ba.min.Y > bb_.max.Y or bb_.min.Y > ba.max.Y or ba.min.Z > bb_.max.Z or bb_.min.Z > ba.max.Z:
        return 0.0
    try:
        r = a & b; return 0.0 if r is None else r.volume
    except Exception:
        return 0.0

def motor_mount(b):
    for ang in (45, 135, 225, 315):
        for r_ in (5.6, 6.1, 6.6):
            b -= CZ(1.3, -1, T.Z_FL + 1, r_ * math.cos(math.radians(ang)), YM + r_ * math.sin(math.radians(ang)))
    b -= BB(-5.5, 5.5, YM + 6.0, YM + 12.5, -1, T.Z_FL + 1)
    b -= CZ(5.0, T.Z_FL - 0.25, T.Z_FL + 1, 0, YM) + CZ(2.0, -1, T.Z_FL + 1, 0, YM)
    return b

M = {}
for typ in ("П", "З"):
    if typ == "П":
        base = motor_mount(R.base_P - DB.slots_p[0] - DB.slots_p[1])
        xb, yb = R.XCP, R.YCP
        for sx in (-1, 1):
            base -= BB(*sorted((sx * (X_SPLIT - 0.15), sx * 30)), Y_SPLIT_P + 0.15, 60, -1, T.Z_FL + 0.01)   # узкий хвост
        rig = {"base": base, "rack": R.fix_P_body, "legs": R.legs_P, "posts": DB.posts_p, "sens": DB.sens_p}
        cart = R.cart_H
    else:
        base = motor_mount(Z.base - DB.slots_z[0] - DB.slots_z[1])
        xb, yb = Z.XCB, Z.Y_BC
        base -= BB(-HALF - 1, HALF + 1, -60, Y_SPLIT_Z - 0.15, -1, T.Z_FL + 0.01)                        # дальше рогов пола нет (там стаканы П)
        base -= BB(-(X_SPLIT + 0.15), X_SPLIT + 0.15, -60, -0.9, -1, T.Z_FL + 0.01)                       # рога: середина хвоста — пол П
        # стойки 49E соседа П стоят у края рогов — вырез в рогах вокруг них (зазор 0.5)
        Lz = Pos(0, R.CM[0], 0) * Rot(0, 0, 180) * Pos(0, -YM, 0); Lp = Pos(0, R.CM[1], 0) * Rot(0, 0, 180) * Pos(0, -YM, 0)
        for pst in DB.posts_p.solids():
            b_ = pst.bounding_box()
            base -= (Lz.inverse() * Lp) * BB(b_.min.X - 0.5, b_.max.X + 0.5, b_.min.Y - 0.5, b_.max.Y + 0.5, -1, T.Z_FL + 0.01)
        rig = {"base": base, "rack": V.fix_o, "beam": Z.beam_body, "legs": Z.legs, "posts": DB.posts_z, "sens": DB.sens_z}
        cart = Z.cart
    for sx in (-1, 1):
        rig["base"] = rig["base"] - CZ(Z.R_P, -1, T.Z_FL + 0.1, sx * xb, yb)                     # окно под кнопку
    rig.update({"brusok": K.beam, "motor": K.motor})
    btns = Part() + [CZ(Z.BTN_D / 2, Z.Z_B0, Z.Z_B0 + Z.BTN_H, sx * xb, yb) + CZ(Z.BTN_DP / 2, Z.Z_B0 + Z.BTN_H - 0.01, Z.Z_BTOP, sx * xb, yb) for sx in (-1, 1)]
    Y1 = rig["base"].bounding_box().max.Y
    y_piv = Y1 - 2.0
    allr = Part() + list(rig.values())
    fr, hx = Part(), []
    if typ == "З":                                                               # З: крючки за задним краем (внешний край ряда)
        for sx in (-1, 1):
            for xc in [sx * v for v in (21.0, 19.0, 17.0, 13.0)]:
                h = BB(xc - 2, xc + 2, Y1 + 0.2, Y1 + 2.2, -GAP - 0.01, T.Z_FL + 1.4) + BB(xc - 2, xc + 2, Y1 - 1.5, Y1 + 0.21, T.Z_FL + 0.2, T.Z_FL + 1.4)
                if iv(h, allr) < 1e-3:
                    fr += h; hx.append(xc); break
        rib_x = [(14.0, 23.5)]
    else:                                                                        # П: за краем — пол соседа З, поэтому крючок в вырезе у края пола
        for sx in (-1, 1):
            for xc in [sx * v for v in (13.5, 12.5, 11.5, 10.5, 9.0, 7.5, 6.0, 4.5)]:
                notch = BB(xc - 1.5, xc + 1.5, Y1 - 1.9, Y1 + 1, -1, T.Z_FL + 0.01)
                h = BB(xc - 1.2, xc + 1.2, Y1 - 1.6, Y1 - 0.2, -GAP - 0.01, T.Z_FL + 1.4) + BB(xc - 1.2, xc + 1.2, Y1 - 3.2, Y1 - 1.59, T.Z_FL + 0.2, T.Z_FL + 1.4)
                if iv(h, allr - notch) < 1e-3:
                    rig["base"] = rig["base"] - notch; fr += h; hx.append(xc); break
        rib_x = [(1.5, min(abs(x) for x in hx) - 1.8 if hx else 13.5)]
    for sx in (-1, 1):                                                           # ребро-ось под полом: узкая грань, модуль качается на ней
        for x0, x1 in rib_x:
            fr += T.prof_x([(y_piv - 1.2, -GAP - 0.01), (y_piv + 1.2, -GAP - 0.01), (y_piv + 0.15, 0), (y_piv - 0.15, 0)], *sorted((sx * x0, sx * x1)))
    ang = math.degrees(TRAVEL / abs(yb - y_piv))
    rec = BB(-HALF - 1, HALF + 1, -80, yb - 4.6, -GAP - 0.4, -GAP + 0.01)           # перед кнопками рама ниже (упор после щелчка)
    M[typ] = dict(rig=rig, cart=cart, btns=btns, y_piv=y_piv, ang=ang, fr=fr, rec=rec, hx=hx, Y1=Y1, yb=yb)
    print("модуль %s: ось y=%.1f, кнопки y=%.1f, наклон %.2f°, крючки %s" % (typ, y_piv, yb, ang, hx))

place = R.place
TY = R.TYPE
def pressed_local(typ, p):
    yp, a = M[typ]["y_piv"], M[typ]["ang"]
    return Pos(0, yp, 0) * Rot(a, 0, 0) * Pos(0, -yp, 0) * p

# рама ряда: плита + рёбра/крючки модулей − выемки перед кнопками
ys = [place(i, M[TY[i]]["rig"]["base"]).bounding_box() for i in range(4)]
frame = BB(-HALF, HALF, min(b.min.Y for b in ys) - 2.4, max(b.max.Y for b in ys) + 2.4, -GAP - FR, -GAP)
for i in range(4):
    frame -= place(i, M[TY[i]]["rec"])
for i in range(4):
    frame += place(i, M[TY[i]]["fr"])

def moving(typ, s):
    rf = math.degrees(s / RF)
    return {"slider": Pos(s, 0, 0) * K.sl, "flo1": Pos(s - A, K.Y_G, 0) * Rot(0, 0, rf) * K.flo0, "flo2": Pos(s + A, K.Y_G, 0) * Rot(0, 0, rf) * K.flo0,
            "cart": Pos(2 * s, 0, 0) * M[typ]["cart"], "gm": Pos(0, YM, 0) * Rot(0, 0, math.degrees(s / RM)) * K.gm}

if __name__ == "__main__":
    bad = 0
    def rep(msg, v):
        global bad
        if v > 0.05: bad += 1; print("  " + msg + " %.2f" % v)
    for i in range(4):
        t = TY[i]
        for n, p in M[t]["rig"].items():
            rep("модуль %d %s × рама (покой)" % (i + 1, n), iv(place(i, p), frame))
            rep("модуль %d %s × рама (нажато)" % (i + 1, n), iv(place(i, pressed_local(t, p)), frame))
    for i in range(3):                                                               # соседи: один нажат, другой в покое, тележки в крайних/средних
        for a_, b_ in ((i, i + 1), (i + 1, i)):
            ta, tb = TY[a_], TY[b_]
            for s in (-S, 0, S):
                A_ = {**M[ta]["rig"], **moving(ta, s)}
                B_ = {**M[tb]["rig"], **moving(tb, -s)}
                for na, pa in A_.items():
                    pa_w = place(a_, pressed_local(ta, pa))
                    for nb, pb in B_.items():
                        rep("нажат %d (s=%+.0f) %s × покой %d %s" % (a_ + 1, s, na, b_ + 1, nb), iv(pa_w, place(b_, pb)))
    print("ряд модулей-клавиш: %s" % ("ЧИСТО" if not bad else "%d проблем" % bad))
    for t, key in (("П", "P"), ("З", "Z")):
        for n, p in {**M[t]["rig"], "cart": M[t]["cart"], "btns": M[t]["btns"]}.items():
            export_stl(Part() + p, os.path.join(OUT, "asm", "%s_%s.stl" % (key, n)), tolerance=0.02, angular_tolerance=0.2)
    for n, p in (("slider", K.sl), ("flo", K.flo0), ("gm", K.gm), ("plat", DB.plat), ("mags", DB.mags)):
        export_stl(Part() + p, os.path.join(OUT, "asm", "%s.stl" % n), tolerance=0.02, angular_tolerance=0.2)
    export_stl(frame, os.path.join(OUT, "asm", "frame.stl"), tolerance=0.02, angular_tolerance=0.2)
    open(os.path.join(OUT, "asm", "params.txt"), "w").write(repr(dict(CM=R.CM, ROT=R.ROT, TYPE=["P" if t == "П" else "Z" for t in TY], YM=YM, YG=K.Y_G, A=A, RF=RF, RM=RM,
        piv={("P" if t == "П" else "Z"): M[t]["y_piv"] for t in M}, ang={("P" if t == "П" else "Z"): M[t]["ang"] for t in M})))
    print("asm готово:", OUT)
