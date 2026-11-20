# -*- coding: utf-8 -*-
"""Модуль на качающейся платформе, окантовка 8 мм со всех сторон (20.11, владелец).
- окантовка (неподвижная) 8 мм, верх вровень с полом платформы (высота +0); кнопки Ø6.4 в вазах целиком на окантовке;
- платформа ±16.7: всё внутрь. Стойки бруска — столб внутри, верх «Г» к краю (скос 45° снизу);
  опоры неподвижной рейки — отдельные «Г»-кронштейны (столб сзади, где мотор уже, плечо вперёд под концы рейки);
  колонны балки З — внутрь; стойки 49E уже и повёрнуты (углы перебором: внутри платформы, без касаний, квадратура 22.5°+45°·k);
- Г-навесы платформы над штоками кнопок; сзади язычки пола в пазах окантовки — ось качания; низ пола поднят на ход переднего края.
Запуск: MOD=P|Z python modul_okantovka8.py → ../19.67_okantovka8_P|Z/asm; сцена — DIR=19.67_okantovka8_%s BLEND=okantovka8_%s EXAG=1 blender -b -P blender_klavisha.py -- P"""
import os, sys, math
os.environ["KLAV"] = "2"; os.environ["OKANT"] = "8"
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from build123d import *
import ryad_V4d as R, datchiki_bok as DB
Z, V, K, T = R.Z, R.V, R.K, R.T
BB, CZ, HALF, YM, S, A, RF, RM, L1, L2, Z_FL = T.BB, T.CZ, T.HALF, T.YM, T.S, T.A, T.RF, T.RM, T.L1, T.L2, T.Z_FL
MOD = os.environ.get("MOD", "P")
OUT = os.path.join(os.path.dirname(HERE), "19.67_okantovka8_%s" % MOD); os.makedirs(os.path.join(OUT, "asm"), exist_ok=True)
RW, G = 8.0, 0.3
XP = HALF - RW - G                                                                # 16.7
X_C0 = XP - 4.0                                                                   # столбы у края платформы: x 12.7..16.7
BTN_D, BTN_H, BTN_HP = Z.BTN_D, Z.BTN_H, Z.BTN_HP
RH = BTN_D / 2 + 0.15 + 0.7                                                       # ваза: гнездо Ø6.7, стенка 0.7
XB = HALF - RH                                                                    # 20.95
Z_AW = Z_FL + BTN_H + BTN_HP
TRAVEL = 0.3
assert abs(Z.XCB - (XP - 2.0)) < 0.01, "OKANT=8 → колонны З на x=14.7"

def iv(a, b):
    ba, bb_ = a.bounding_box(), b.bounding_box()
    if ba.min.X > bb_.max.X or bb_.min.X > ba.max.X or ba.min.Y > bb_.max.Y or bb_.min.Y > ba.max.Y or ba.min.Z > bb_.max.Z or bb_.min.Z > ba.max.Z:
        return 0.0
    try:
        r = a & b; return 0.0 if r is None else r.volume
    except Exception:
        return 0.0

def prof_y(pts, y0, y1):
    return extrude(make_face(Polyline(*[(x, y0, z) for x, z in pts + [pts[0]]])), y1 - y0, dir=(0, 1, 0))

def motor_mount(b):
    for ang in (45, 135, 225, 315):
        for r_ in (5.6, 6.1, 6.6):
            b -= CZ(1.3, -1, Z_FL + 1, r_ * math.cos(math.radians(ang)), YM + r_ * math.sin(math.radians(ang)))
    b -= BB(-5.5, 5.5, YM + 6.0, YM + 12.5, -1, Z_FL + 1)
    b -= CZ(5.0, Z_FL - 0.25, Z_FL + 1, 0, YM) + CZ(2.0, -1, Z_FL + 1, 0, YM)
    return b

# ---------- платформа: основание без всего, что шире ±16.7 ----------
base = Z.base if MOD == "Z" else V.base_o
for sx in (-1, 1):
    base -= BB(*sorted((sx * XP, sx * 30)), -40, 50, -1, 40)
base = motor_mount(base)
parts = {"rack": V.fix_o}
if MOD == "Z":                                                                    # балка З на сплошной стенке до пола (тележка низ балки не трогает) — колонн нет
    parts.update({"beam": Z.beam_body - BB(-30, 30, -40, 40, -1, L2[0])})
    base += BB(-XP, XP, Z.Y_BC - 1.4, Z.Y_BC + 1.4, Z_FL - 0.6, L2[0])
    cart, YB = Z.cart, -10.0
else:
    cart, YB = R.cart_H, 3.35
# 20.11 (владелец): брусок ПОД ползуном — паз ползуна открыт вниз, ползун лежит на бруске; брусок короткий (±16.7) на простых стойках
BM_H = T.Z_BM1 - T.Z_BM0                                                          # 1.95
SL = K.sl + BB(-K.SLX - 1, K.SLX + 1, K.BMY0 - K.C - 0.01, K.BMY1 + K.C + 0.01, T.Z_BM0 - K.C, L1[1])   # заделать старый паз сверху
SL -= BB(-K.SLX - 1, K.SLX + 1, K.BMY0 - K.C, K.BMY1 + K.C, L1[0] - 1, L1[0] + BM_H + K.C)             # паз снизу
SL = SL & BB(-K.SLX, K.SLX, -40, 40, -1, 40)
BRUSOK = BB(-XP, XP, K.BMY0, K.BMY1, L1[0], L1[0] + BM_H)
for sx in (-1, 1):                                                                # стойки бруска: под ним, не шире его (стенки паза ползуна проходят мимо)
    base += BB(*sorted((sx * X_C0, sx * XP)), K.BMY0 + 0.1, K.BMY1 - 0.1, Z_FL - 0.01, L1[0])
# навесы над кнопками: стенка у края платформы + плечо над штоком
for sx in (-1, 1):
    base += BB(*sorted((sx * X_C0, sx * XP)), YB - 1.4, YB + 1.4, Z_FL - 0.01, Z_AW + 1.6)
    base += BB(*sorted((sx * X_C0, sx * (XB + 2.2))), YB - 2.2, YB + 2.2, Z_AW, Z_AW + 1.6)
base += BB(-XP, XP, 30.0, 34.0, 0, Z_FL)                                          # сзади пол длиннее на 3.5: там встают стойки 49E
Y0p, Y1p = base.bounding_box().min.Y, base.bounding_box().max.Y
moving_all = []
def moving(s):
    rf = math.degrees(s / RF)
    return {"slider": Pos(s, 0, 0) * SL, "flo1": Pos(s - A, K.Y_G, 0) * Rot(0, 0, rf) * K.flo0, "flo2": Pos(s + A, K.Y_G, 0) * Rot(0, 0, rf) * K.flo0,
            "cart": Pos(2 * s, 0, 0) * cart, "gm": Pos(0, YM, 0) * Rot(0, 0, math.degrees(s / RM)) * K.gm, "plat": Pos(0, YM, 0) * DB.plat}
MOV = [moving(s) for s in (-S, -S / 2, 0, S / 2, S)]
# неподвижная рейка — на стенках до пола вдоль края платформы (владелец), стенка длиннее рейки
RW_T = XP - 14.5                                                                 # стенка до 0.6 от колокола мотора (кольцо под мотор в этом месте срезано — владелец)
if MOD == "Z":                                                                    # З (владелец): рейка-«столик» — плита рейки удлинена назад, стенки — заодно с рейкой, низом в паз пола
    table = V.fix_o + BB(-XP, XP, V.fix_o.bounding_box().max.Y - 0.5, 24.0, L2[0], L2[1])
    for sx in (-1, 1):
        table += BB(*sorted((sx * (XP - RW_T), sx * XP)), 12.0, 24.0, Z_FL - 0.6, L2[0] + 0.01)
        base -= BB(*sorted((sx * (XP - RW_T - 0.15), sx * (XP + 0.15))), 11.85, 24.15, Z_FL - 0.6, Z_FL + 4.5)   # паз в полу + срез кольца
    parts["rack"] = table
    br_y = "столик"
else:                                                                             # П (владелец): по спинке рейки бегает тележка — под концом рейки только скос-распорка до пола
    yr0, yr1 = 12.0, V.fix_o.bounding_box().max.Y - 0.2
    for sx in (-1, 1):
        x0_, x1_ = sorted((sx * (XP - RW_T), sx * XP))
        brace = Pos(x0_, 0, 0) * Rot(90, 90, 0) * extrude(make_face(Polyline((yr0, L2[0]), (yr1, L2[0]), (yr1, Z_FL - 0.01), (yr1 - 1.5, Z_FL - 0.01), (yr0, L2[0]))), x1_ - x0_, dir=(0, 0, 1))
        base += brace
    br_y = "скос"
stat0 = Part() + [base, K.motor, BRUSOK] + list(parts.values())

# ---------- стойки 49E: уже (5.4) и мельче (3.6), углы перебором ----------
PD, PW = 3.6, 5.4
X_IN = DB.X_IN
def post0():
    p = BB(X_IN, X_IN + PD, YM - PW / 2, YM + PW / 2, Z_FL - 1.0, DB.Z_TOP)
    p -= BB(X_IN - 0.05, X_IN + DB.SEN_T + 0.1, YM - DB.SEN_W / 2 - 0.1, YM + DB.SEN_W / 2 + 0.1, DB.Z_MC - DB.SEN_H / 2 - 0.1, DB.Z_TOP + 1)
    p -= BB(X_IN + 0.5, X_IN + PD + 1, YM - 1.5, YM + 1.5, DB.Z_TOP - 1.0, DB.Z_TOP + 1)
    for k in (-1, 0, 1):
        p -= BB(X_IN + PD - 0.7, X_IN + PD + 0.5, YM + k * 1.27 - 0.4, YM + k * 1.27 + 0.4, Z_FL + 0.5, DB.Z_TOP + 1)
    sl = BB(X_IN - 0.15, X_IN + PD + 0.15, YM - PW / 2 - 0.15, YM + PW / 2 + 0.15, Z_FL - 1.05, Z_FL + 4.2)
    se = BB(X_IN, X_IN + DB.SEN_T, YM - DB.SEN_W / 2, YM + DB.SEN_W / 2, DB.Z_MC - DB.SEN_H / 2, DB.Z_MC + DB.SEN_H / 2)
    return p, sl, se
P0, SL0, SE0 = post0()
ok = {}
for k in range(144):
    a = 2.5 * k
    p, sl = DB.rotm(a, P0), DB.rotm(a, SL0)
    b_ = p.bounding_box()
    if b_.min.X < -XP + 0.05 or b_.max.X > XP - 0.05 or b_.min.Y < Y0p + 0.05 or b_.max.Y > Y1p - 0.05: continue
    if iv(p, Part() + [base - sl, K.motor, BRUSOK] + [v for n, v in parts.items()]) > 0.01: continue
    if any(iv(p, m) > 0.01 for mv in MOV for m in mv.values()): continue
    ok[a] = (p, sl)
pair = None
for a1 in sorted(ok):
    for a2 in sorted(ok):
        d = (a2 - a1) % 360
        if a2 <= a1 or abs((d % 45) - 22.5) > 0.01: continue
        if iv(ok[a1][0], ok[a2][0]) > 0.01: continue
        pair = (a1, a2); break
    if pair: break
print("стойки 49E: подходящие углы", sorted(ok), "→ пара", pair)
if pair:
    parts["posts"] = ok[pair[0]][0] + ok[pair[1]][0]
    parts["sens"] = DB.rotm(pair[0], SE0) + DB.rotm(pair[1], SE0)
    base = base - ok[pair[0]][1] - ok[pair[1]][1]

# ---------- язычки-ось, подъём низа пола ----------
tab_x = (-8.0, 8.0)
for xc in tab_x:
    base += BB(xc - 2, xc + 2, Y1p - 0.5, Y1p + G + 2.0, 0.8, 2.0)
Y_PIV, Z_PIV = Y1p + G + 1.0, 1.4
DROP = TRAVEL * (Y_PIV - Y0p) / (Y_PIV - YB)
Z_LIFT = round(DROP + 0.2, 2)
base -= BB(-30, 30, -40, 60, -1, Z_LIFT)
platform = {"base": base, **parts, "brusok": BRUSOK, "motor": K.motor}

# ---------- окантовка 8 мм + вазы + кнопки ----------
rim = BB(-HALF, HALF, Y0p - G - RW, Y1p + G + RW, 0, Z_FL) - BB(-XP - G, XP + G, Y0p - G, Y1p + G, -1, Z_FL + 1)
for xc in tab_x:
    rim -= BB(xc - 2.3, xc + 2.3, Y1p + G - 0.01, Y1p + G + 2.2, 0.7, 2.1)
vases, btns = Part(), Part()
for sx in (-1, 1):
    v_ = CZ(RH, Z_FL - 0.01, Z_FL + BTN_H + 0.5, sx * XB, YB) - CZ(BTN_D / 2 + 0.15, Z_FL, Z_FL + 10, sx * XB, YB)
    v_ -= BB(*sorted((sx * XB, sx * 30)), YB - 0.7, YB + 0.7, Z_FL, Z_FL + 10)                       # щель для проводов (наружу)
    vases += v_
    btns += CZ(BTN_D / 2, Z_FL, Z_FL + BTN_H, sx * XB, YB) + CZ(Z.BTN_DP / 2, Z_FL + BTN_H - 0.01, Z_AW, sx * XB, YB)
fx = rim + vases

# ---------- проверка ----------
ang = math.degrees(TRAVEL / abs(Y_PIV - YB))
def pressed(p):
    return Pos(0, Y_PIV, Z_PIV) * Rot(ang, 0, 0) * Pos(0, -Y_PIV, -Z_PIV) * p
bad = 0
for nm, pose in (("покой", lambda p: p), ("нажато", pressed)):
    for n, p in platform.items():
        v = iv(pose(p), fx)
        if v > 0.02: bad += 1; print("  %s × окантовка (%s) %.3f" % (n, nm, v))
        if n != "base":
            v = iv(pose(p), btns)
            if v > 0.02: bad += 1; print("  %s × кнопки (%s) %.3f" % (n, nm, v))
    for mv in MOV:
        for n, p in mv.items():
            v = iv(pose(p), fx) + iv(pose(p), btns)
            if v > 0.02: bad += 1; print("  %s × окантовка/кнопки (%s) %.3f" % (n, nm, v))
    v = iv(pose(platform["base"]), btns)
    print("  навесы × штоки (%s): %.2f мм³" % (nm, v))
    if nm == "покой" and v > 0.02: bad += 1
for n, p in parts.items():                                                       # детали платформы между собой
    for n2, p2 in parts.items():
        if n < n2 and not {n, n2} <= {"rack", "rack_br"}:
            v = iv(p, p2)
            if v > 0.02: bad += 1; print("  %s × %s %.3f" % (n, n2, v))
zmin = pressed(platform["base"]).bounding_box().min.Z
if zmin < 0.05: bad += 1
print("модуль %s, окантовка 8: %s | платформа ±%.1f, кнопки x=±%.2f y=%.2f, стойки 49E %s, кронштейны y=%s, низ пола +%.2f, наклон %.2f°" % (
    MOD, "ЧИСТО" if not bad else "%d проблем" % bad, XP, XB, YB, pair, br_y, Z_LIFT, ang))
asm = {**platform, "frame": fx, "btns": btns, "cart": cart, "slider": SL, "flo": K.flo0, "gm": K.gm, "plat": DB.plat, "mags": DB.mags}
for n, p in asm.items():
    export_stl(Part() + p, os.path.join(OUT, "asm", n + ".stl"), tolerance=0.02, angular_tolerance=0.2)
open(os.path.join(OUT, "asm", "params.txt"), "w").write("%f %f %f %f %f" % (YM, K.Y_G, A, RF, RM))
open(os.path.join(OUT, "asm", "klav.txt"), "w").write("%f %f %f" % (Y_PIV, ang, Z_PIV))
