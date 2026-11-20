# -*- coding: utf-8 -*-
"""Модуль на качающейся платформе внутри окантовки (20.11, владелец).
- окантовка (неподвижная): по бокам 2.5 мм, на торцах 3 мм, верх вровень с полом платформы — высота модуля не растёт;
- платформа: пол ±22.2 со всем модулем (мотор, столбы, брусок, рейки, телескоп); сзади 2 язычка-продолжения пола входят в пазы окантовки — ось качания;
- клик: на окантовке в вырезах углов платформы стоят кнопки Ø6.4×5 в «вазах» (стенки + щель под провода), сверху на шток давит Г-навес платформы;
- столбы к центру: стойки бруска — столб внутри платформы, верх «Г» к краю (снизу скос 45°, печать без поддержек), стойки рейки и колонны — просто внутрь.
Запуск: MOD=P|Z python modul_okantovka.py → ../19.66_okantovka_P|Z/asm; сцена — DIR=19.66_okantovka_P blender -b -P blender_klavisha.py -- P"""
import os, sys, math
os.environ["KLAV"] = "2"; os.environ["OKANT"] = "1"
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from build123d import *
import ryad_V4d as R, datchiki_bok as DB
Z, V, K, T = R.Z, R.V, R.K, R.T
BB, CZ, HALF, YM, S, A, RF, RM, L1, L2, Z_FL = T.BB, T.CZ, T.HALF, T.YM, T.S, T.A, T.RF, T.RM, T.L1, T.L2, T.Z_FL
MOD = os.environ.get("MOD", "P")
OUT = os.path.join(os.path.dirname(HERE), "19.66_okantovka_%s" % MOD); os.makedirs(os.path.join(OUT, "asm"), exist_ok=True)
RW, RE, G = 2.5, 3.0, 0.3                                                         # окантовка: бок / торец / щель
XP = HALF - RW - G                                                                # полуширина платформы 22.2
BTN_D, BTN_H, BTN_HP = Z.BTN_D, Z.BTN_H, Z.BTN_HP                                 # кнопка Ø6.4 × (3.5 + шток 1.5)
RH = BTN_D / 2 + 0.15 + 0.9                                                       # ваза: гнездо Ø6.7, стенка 0.9
XB = HALF - RH                                                                    # центр кнопки по X (ваза у самого края)
Z_AW = Z_FL + BTN_H + BTN_HP                                                      # низ навеса = верх штока
TRAVEL = 0.3

def iv(a, b):
    ba, bb_ = a.bounding_box(), b.bounding_box()
    if ba.min.X > bb_.max.X or bb_.min.X > ba.max.X or ba.min.Y > bb_.max.Y or bb_.min.Y > ba.max.Y or ba.min.Z > bb_.max.Z or bb_.min.Z > ba.max.Z:
        return 0.0
    try:
        r = a & b; return 0.0 if r is None else r.volume
    except Exception:
        return 0.0

def prof_y(pts, y0, y1):                                                          # профиль (x, z) вытянуть вдоль Y
    return extrude(make_face(Polyline(*[(x, y0, z) for x, z in pts + [pts[0]]])), y1 - y0, dir=(0, 1, 0))

def motor_mount(b):
    for ang in (45, 135, 225, 315):
        for r_ in (5.6, 6.1, 6.6):
            b -= CZ(1.3, -1, Z_FL + 1, r_ * math.cos(math.radians(ang)), YM + r_ * math.sin(math.radians(ang)))
    b -= BB(-5.5, 5.5, YM + 6.0, YM + 12.5, -1, Z_FL + 1)
    b -= CZ(5.0, Z_FL - 0.25, Z_FL + 1, 0, YM) + CZ(2.0, -1, Z_FL + 1, 0, YM)
    return b

# ---------- платформа ----------
if MOD == "P":
    base = R.base_P - DB.slots_p[0] - DB.slots_p[1]
    parts = {"rack": R.fix_P_body, "legs": R.legs_P, "posts": DB.posts_p, "sens": DB.sens_p}
    cart, YB_LIST = R.cart_H, (21.0,)                                       # спереди места нет (стойки бруска, колонны) — кнопки за колоннами, ось держит язычки в пазах
else:
    base = Z.base - DB.slots_z[0] - DB.slots_z[1]
    parts = {"rack": V.fix_o, "beam": Z.beam_body, "legs": Z.legs, "posts": DB.posts_z, "sens": DB.sens_z}
    cart, YB_LIST = Z.cart, (-14.0,)
    base += BB(-XP, XP, -19.4, -14.3, 0, Z_FL)                                   # хвост З длиннее: место под вазы за колоннами
base = motor_mount(base)
# старые стойки у края (x 23.7..25) — убрать
for sx in (-1, 1):
    base -= BB(*sorted((sx * 23.6, sx * 25.1)), -30, 40, Z_FL - 0.01, L2[0] + 0.01)
X_ST0 = XP - 2.5                                                                  # столб у края платформы: x 19.7..22.2
Z_ARM0, Z_ARM1 = L1[0] - 2.1, L1[0] - 0.1                                         # плечо «Г» под ползуном
stands = Part()
for sx in (-1, 1):
    # стойка бруска: столб внутри → плечо наружу под ползуном → верх с пазом на старом месте (23.7..25), скос 45° под плечом
    col = BB(*sorted((sx * X_ST0, sx * XP)), 0.5, 6.2, Z_FL - 0.01, Z_ARM1)
    arm = BB(*sorted((sx * X_ST0, sx * HALF)), 0.5, 6.2, Z_ARM0, Z_ARM1)
    top = BB(*sorted((sx * 23.7, sx * HALF)), 0.5, 6.2, Z_ARM1 - 0.01, L2[0])
    ch = prof_y([(sx * XP, Z_ARM0 - (HALF - XP)), (sx * HALF, Z_ARM0 + 0.01), (sx * XP, Z_ARM0 + 0.01)], 0.5, 6.2)
    st = col + arm + top + ch
    st -= BB(*sorted((sx * 23.6, sx * 25.1)), K.BMY0 - 0.1, K.BMY1 + 0.1, T.Z_BM0 - 0.05, L2[0] + 1)   # паз под конец бруска
    stands += st
    if MOD == "Z":                                                               # стойка неподвижной рейки З — просто внутрь
        stands += BB(*sorted((sx * X_ST0, sx * XP)), 12.0, 14.7, Z_FL - 0.01, L2[0])
base += stands
# пол — не шире платформы, вырезы в углах под вазы, язычки-ось сзади
Y0p, Y1p = base.bounding_box().min.Y, base.bounding_box().max.Y
for sx in (-1, 1):
    base -= BB(*sorted((sx * XP, sx * 30)), -40, 50, -1, Z_FL + 0.01)
notch = Part() + [BB(*sorted((sx * (XB - RH - G), sx * 30)), yb - RH - G, yb + RH + G, -1, Z_AW - 0.5) for sx in (-1, 1) for yb in YB_LIST]
base -= notch
platform = {"base": base, **parts, "brusok": K.beam, "motor": K.motor}
allp = Part() + list(platform.values())
# навес «Г» над кнопкой: стенка на полу рядом с вырезом (со стороны оси) + плечо над штоком
awn = Part()
for sx in (-1, 1):
    for yb in YB_LIST:
        for side in (1, -1):
            y_w0, y_w1 = sorted((yb + side * (RH + G + 0.2), yb + side * (RH + G + 2.0)))
            wall = BB(*sorted((sx * (XB - RH - G + 0.2), sx * XP)), y_w0, y_w1, Z_FL - 0.01, Z_AW + 1.6)
            arm_ = BB(*sorted((sx * (XB - 2.2), sx * (XB + 2.2))), *sorted((yb, yb + side * (RH + G + 2.0))), Z_AW, Z_AW + 1.6)
            arm_ += BB(*sorted((sx * (XB - 2.2), sx * (XB + 2.2))), yb - 2.2, yb + 2.2, Z_AW, Z_AW + 1.6)
            a_ = wall + arm_
            if y_w0 >= Y0p and y_w1 <= Y1p and iv(a_, allp - base) < 1e-3:
                awn += a_; break
platform["base"] = base + awn
# язычки сзади: продолжение пола, входят в пазы окантовки (опора и держат от подъёма — ось качания)
tabs, tab_x = Part(), (-12.0, 12.0)
for xc in tab_x:
    tabs += BB(xc - 2, xc + 2, Y1p - 0.5, Y1p + G + 2.0, 0.8, 2.0)
platform["base"] = platform["base"] + tabs

# низ пола поднят: при нажатии передний край опускается сильнее, чем у кнопок, — не выходит ниже окантовки (под ней дно грифа)
Y_PIV, Z_PIV = Y1p + G + 1.0, 1.4
DROP = TRAVEL * (Y_PIV - Y0p) / (Y_PIV - YB_LIST[0])
Z_LIFT = round(DROP + 0.2, 2)
platform["base"] = platform["base"] - BB(-30, 30, -40, 60, -1, Z_LIFT)

# ---------- окантовка + вазы + кнопки ----------
rim = BB(-HALF, HALF, Y0p - G - RE, Y1p + G + RE, 0, Z_FL)
opening = BB(-XP - G, XP + G, Y0p - G, Y1p + G, -1, Z_FL + 1)
for sx in (-1, 1):
    for yb in YB_LIST:
        opening -= BB(*sorted((sx * (XB - RH), sx * 30)), yb - RH, yb + RH, -2, Z_FL + 2)   # остров под вазу
rim -= opening
for pst in parts["posts"].solids():                                               # стойки 49E, свисающие за край платформы, — вырез в окантовке
    b_ = pst.bounding_box(); rim -= BB(b_.min.X - 0.4, b_.max.X + 0.4, b_.min.Y - 0.4, b_.max.Y + 0.4, -1, Z_FL + 1)
for xc in tab_x:
    rim -= BB(xc - 2.3, xc + 2.3, Y1p + G - 0.01, Y1p + G + 2.2, 0.7, 2.1)          # паз под язычок (зазор 0.1)
vases, btns = Part(), Part()
for sx in (-1, 1):
    for yb in YB_LIST:
        v_ = CZ(RH, Z_FL - 0.01, Z_FL + BTN_H + 0.5, sx * XB, yb) - CZ(BTN_D / 2 + 0.15, Z_FL, Z_FL + 10, sx * XB, yb)
        v_ -= BB(*sorted((sx * XB, sx * 30)), yb - 0.7, yb + 0.7, Z_FL, Z_FL + 10)                       # щель для проводов (наружу)
        vases += v_
        btns += CZ(BTN_D / 2, Z_FL, Z_FL + BTN_H, sx * XB, yb) + CZ(Z.BTN_DP / 2, Z_FL + BTN_H - 0.01, Z_AW, sx * XB, yb)
fixed = {"frame": rim + vases}

# ---------- проверка: покой / нажато (поворот вокруг кромки окантовки под язычками) ----------
ang = math.degrees(TRAVEL / abs(Y_PIV - YB_LIST[0]))
def pressed(p):
    return Pos(0, Y_PIV, Z_PIV) * Rot(ang, 0, 0) * Pos(0, -Y_PIV, -Z_PIV) * p
def moving(s):
    rf = math.degrees(s / RF)
    return {"slider": Pos(s, 0, 0) * K.sl, "flo1": Pos(s - A, K.Y_G, 0) * Rot(0, 0, rf) * K.flo0, "flo2": Pos(s + A, K.Y_G, 0) * Rot(0, 0, rf) * K.flo0,
            "cart": Pos(2 * s, 0, 0) * cart, "gm": Pos(0, YM, 0) * Rot(0, 0, math.degrees(s / RM)) * K.gm, "plat": Pos(0, YM, 0) * DB.plat}
bad = 0
fx = fixed["frame"]
for nm, pose in (("покой", lambda p: p), ("нажато", pressed)):
    for n, p in platform.items():
        v = iv(pose(p), fx)
        if v > 0.02: bad += 1; print("  %s × окантовка (%s) %.3f" % (n, nm, v))
    for s in (-S, 0, S):
        for n, p in moving(s).items():
            v = iv(pose(p), fx) + iv(pose(p), btns)
            if v > 0.02: bad += 1; print("  %s s=%+.0f × окантовка/кнопки (%s) %.3f" % (n, s, nm, v))
    v = iv(pose(platform["base"]), btns)
    print("  навесы × штоки (%s): %.2f мм³ (%s)" % (nm, v, "должно быть ~0" if nm == "покой" else "шток нажат"))
    if nm == "покой" and v > 0.02: bad += 1
for n in platform:
    if n == "base": continue
    v = iv(platform[n], btns)
    if v > 0.02: bad += 1; print("  %s × кнопки %.3f" % (n, v))
zmin = pressed(platform["base"]).bounding_box().min.Z
if zmin < 0.05: bad += 1; print("  платформа ниже окантовки при нажатии: z=%.2f" % zmin)
print("  низ пола поднят на %.2f (пол %.2f), при нажатии низ платформы z=%.2f" % (Z_LIFT, Z_FL - Z_LIFT, zmin))
print("модуль %s на платформе в окантовке: %s | платформа ±%.1f, кнопки x=±%.2f y=%s, язычки x=%s, навесы %d, наклон %.2f°, высота +0" % (
    MOD, "ЧИСТО" if not bad else "%d проблем" % bad, XP, XB, YB_LIST, tab_x, len(awn.solids()), ang))

asm = {**platform, **fixed, "btns": btns, "cart": cart, "slider": K.sl, "flo": K.flo0, "gm": K.gm, "plat": DB.plat, "mags": DB.mags}
for n, p in asm.items():
    export_stl(Part() + p, os.path.join(OUT, "asm", n + ".stl"), tolerance=0.02, angular_tolerance=0.2)
open(os.path.join(OUT, "asm", "params.txt"), "w").write("%f %f %f %f %f" % (YM, K.Y_G, A, RF, RM))
open(os.path.join(OUT, "asm", "klav.txt"), "w").write("%f %f %f" % (Y_PIV, ang, Z_PIV))
