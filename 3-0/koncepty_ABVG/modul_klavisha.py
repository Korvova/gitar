# -*- coding: utf-8 -*-
"""Модуль-клавиша (19.11, владелец): весь модуль качается на оси, клик — кнопкой на раме под полом.
Тележка больше не должна проседать относительно шестерён: жмёшь где угодно — наклоняется весь модуль (мотор, шестерни, тележка).
- «Т»-ножка вклеивается в стакан (не ездит), стакан без дна — кнопка стоит на раме, «Т» лежит на штоке;
- рама: плита 1.2 под модулем (зазор 0.5), у одного края — упор-ребро (ось качания) и два крючка над полом модуля;
- П: ось сзади (за мотором), кнопки посередине, площадка спереди над шестернями — рычаг жмёт кнопки сильнее пальца;
- З: ось тоже сзади за мотором, кнопки под хвостом (спереди) прямо под площадкой.
Запуск: MOD=P python modul_klavisha.py → ../19.65_klavisha_P (STL + asm), сцена — blender_modul.py с DIR=19.65_klavisha_P."""
import os, sys, math
os.environ["KLAV"] = "1"
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from build123d import *
import ryad_V4d as R, datchiki_bok as DB
Z, V, K, T = R.Z, R.V, R.K, R.T
BB, CZ, HALF = T.BB, T.CZ, T.HALF
MOD = os.environ.get("MOD", "P")
OUT = os.path.join(os.path.dirname(HERE), "19.65_klavisha_%s" % MOD)
os.makedirs(os.path.join(OUT, "asm"), exist_ok=True)
GAP, FR = Z.GAP, 1.2
TRAVEL = 0.35                                                                     # ход у кнопок при нажатии (кнопке хватает ~0.25)

def motor_mount(b):
    for ang in (45, 135, 225, 315):
        for r_ in (5.6, 6.1, 6.6):
            b -= CZ(1.3, -1, T.Z_FL + 1, r_ * math.cos(math.radians(ang)), T.YM + r_ * math.sin(math.radians(ang)))
    b -= BB(-5.5, 5.5, T.YM + 6.0, T.YM + 12.5, -1, T.Z_FL + 1)
    b -= CZ(5.0, T.Z_FL - 0.25, T.Z_FL + 1, 0, T.YM) + CZ(2.0, -1, T.Z_FL + 1, 0, T.YM)
    return b

if MOD == "P":
    base = motor_mount(R.base_P - DB.slots_p[0] - DB.slots_p[1])
    rigid = {"base": base, "rack": R.fix_P_body, "legs": R.legs_P, "posts": DB.posts_p}
    asm = {"cart": R.cart_H, "btns": R.btns_P, "sens": DB.sens_p}
    Y_BTN, X_BTN, HINGE_BACK = R.YCP, R.XCP, True
else:
    base = motor_mount(Z.base - DB.slots_z[0] - DB.slots_z[1])
    rigid = {"base": base, "rack": V.fix_o, "beam": Z.beam_body, "legs": Z.legs, "posts": DB.posts_z}
    asm = {"cart": Z.cart, "btns": Z.btns, "sens": DB.sens_z}
    Y_BTN, X_BTN, HINGE_BACK = Z.Y_BC, Z.XCB, True                                 # хвост З — спереди (y<0), ось сзади за мотором

for sx in (-1, 1):                                                               # окно в полу под кнопкой (кнопка стоит на раме)
    base -= CZ(Z.R_P, -1, T.Z_FL + 0.1, sx * X_BTN, Y_BTN)
rigid["base"] = base
bb = base.bounding_box(); Y0, Y1 = bb.min.Y, bb.max.Y
sg = 1 if HINGE_BACK else -1                                                      # куда смотрит край с осью
YE = Y1 if HINGE_BACK else Y0                                                     # край модуля с осью
Y_PIV = YE - sg * 2.0                                                             # линия качания (ребро под полом)

def iv(a, b):
    r = a & b; return 0.0 if r is None else r.volume

# рама: плита + ребро-ось под полом у края + 2 крючка над полом (свободное место по X ищем перебором)
frame = BB(-HALF, HALF, *sorted((Y0, YE + sg * 2.4)), -GAP - FR, -GAP)
rib = Part()
for sx in (-1, 1):
    rib += T.prof_x([(Y_PIV - 1.2, -GAP - 0.01), (Y_PIV + 1.2, -GAP - 0.01), (Y_PIV + 0.15, 0), (Y_PIV - 0.15, 0)], *sorted((sx * 14, sx * 23.5)))   # ребро-ось: узкая грань, модуль качается на ней
frame += rib
frame -= BB(-HALF - 1, HALF + 1, *sorted((Y0 - 1, Y_BTN - 4.6)), -GAP - 0.4, -GAP + 0.01)   # перед кнопками рама ниже на 0.4: край модуля опускается больше, упор после щелчка
mod_all = Part() + list(rigid.values())
hooks, hook_x = Part(), []
for sx in (-1, 1):
    for xc in [sx * v for v in (21.0, 19.0, 17.0, 15.0, 13.0, 11.0, 9.0)]:
        post = BB(xc - 2, xc + 2, *sorted((YE + sg * 0.2, YE + sg * 2.2)), -GAP - 0.01, T.Z_FL + 0.2 + 1.2)
        tong = BB(xc - 2, xc + 2, *sorted((YE - sg * 1.5, YE + sg * 0.21)), T.Z_FL + 0.2, T.Z_FL + 0.2 + 1.2)
        h = post + tong
        if iv(h, mod_all) < 1e-3:
            hooks += h; hook_x.append(xc); break
frame += hooks

# поза «нажато»: модуль поворачивается вокруг линии качания так, что у кнопок опускается на TRAVEL
ang = math.degrees(TRAVEL / abs(Y_BTN - Y_PIV)) * (1 if HINGE_BACK else -1)
def pressed(p):
    return Pos(0, Y_PIV, 0) * Rot(ang, 0, 0) * Pos(0, -Y_PIV, 0) * p
bad = 0
for n, p in rigid.items():
    for nm, pose in (("покой", p), ("нажато", pressed(p))):
        v = iv(pose, frame)
        if v > 0.01: bad += 1; print("  %s × рама (%s) %.3f" % (n, nm, v))
    v = iv(p, asm["btns"])
    if v > 0.01: bad += 1; print("  %s × кнопки (покой) %.3f" % (n, v))
dz = [pressed(Pos(x, Y_BTN, 0) * Box(0.01, 0.01, 0.01)).center().Z for x in (0,)]
print("модуль-клавиша %s: %s | ось на y=%.1f (%s), кнопки y=%.1f, крючки x=%s, наклон %.2f°, ход у кнопок %.2f, высота +%.1f (рама+зазор)" % (
    MOD, "ЧИСТО" if not bad else "%d проблем" % bad, Y_PIV, "сзади" if HINGE_BACK else "спереди", Y_BTN, hook_x, abs(ang), -dz[0], GAP + FR))

asm.update(rigid); asm["frame"] = frame
asm.update({"slider": K.sl, "flo": K.flo0, "brusok": K.beam, "gm": K.gm, "plat": DB.plat, "mags": DB.mags, "motor": K.motor})
for n, p in asm.items():
    export_stl(Part() + p, os.path.join(OUT, "asm", n + ".stl"), tolerance=0.02, angular_tolerance=0.2)
open(os.path.join(OUT, "asm", "params.txt"), "w").write("%f %f %f %f %f" % (T.YM, K.Y_G, T.A, T.RF, T.RM))
open(os.path.join(OUT, "asm", "klav.txt"), "w").write("%f %f" % (Y_PIV, ang))
