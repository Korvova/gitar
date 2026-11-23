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
os.environ.setdefault("CM_H", "15.5")                                              # моторы П на ±15.5: ползуны П1/П2 не цепляют при наклоне (ряд 4 — проверено)
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from build123d import *
import ryad_V4d as R, datchiki_bok as DB
Z, V, K, T = R.Z, R.V, R.K, R.T
BB, CZ, HALF, YM, S, A, RF, RM, L1, L2, Z_FL = T.BB, T.CZ, T.HALF, T.YM, T.S, T.A, T.RF, T.RM, T.L1, T.L2, T.Z_FL
MOD = os.environ.get("MOD", "P")
OUT = os.path.join(os.path.dirname(HERE), "19.67_okantovka8_%s" % MOD); os.makedirs(os.path.join(OUT, "asm"), exist_ok=True)
for _f in os.listdir(os.path.join(OUT, "asm")):                                   # старые STL не должны попадать в сцену
    if _f.endswith(".stl"): os.remove(os.path.join(OUT, "asm", _f))
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
    base -= BB(-30, 30, -40, YM - 16.1, -1, 40)                                    # 20.11 (владелец): платформа З — в диаметр мотора, хвоста нет
    cart, YB = Z.cart, Z.Y_BC                                                     # кнопки под балкой (владелец)
else:
    cart, YB = R.cart_H, 4.6                                                      # вазы не выходят за край пола спереди — к П2 вплотную (владелец)
YBB = YB                                                                          # стойки кнопки/паза прямо под ножками; у З в ряду стойка стоит над ямкой оси соседа П и клеится после — её дно и есть крышка (владелец 23.11)
# 20.11 (владелец): брусок ПОД ползуном — паз ползуна открыт вниз, ползун лежит на бруске; брусок короткий (±16.7) на простых стойках
BM_H = T.Z_BM1 - T.Z_BM0                                                          # 1.95
SL = K.sl + BB(-K.SLX - 1, K.SLX + 1, K.BMY0 - K.C - 0.01, K.BMY1 + K.C + 0.01, T.Z_BM0 - K.C, L1[1])   # заделать старый паз сверху
SL -= BB(-K.SLX - 1, K.SLX + 1, K.BMY0 - K.C, K.BMY1 + K.C, L1[0] - 1, L1[0] + BM_H + K.C)             # паз снизу
SL = SL & BB(-K.SLX, K.SLX, -40, 40, -1, 40)
X_BR = 24.5                                                                       # брусок до конца хода ползуна (над окантовкой)
BRUSOK = BB(-X_BR, X_BR, K.BMY0, K.BMY1, L1[0], L1[0] + BM_H)
X_STOP = K.SLX + S + 0.2                                                           # 21.11 (владелец): упоры хода ползуна на концах бруска — шире паза,
for sx in (-1, 1):                                                                # стенки паза ползуна упираются в них при ходе ±11.2
    BRUSOK += BB(*sorted((sx * X_STOP, sx * X_BR)), K.BMY0 - 1.2, K.BMY1 + 1.2, L1[0], L1[0] + BM_H)
for sx in (-1, 1):                                                                # стойки бруска: под ним, не шире его (стенки паза ползуна проходят мимо)
    base += BB(*sorted((sx * X_C0, sx * XP)), K.BMY0 + 0.1, K.BMY1 - 0.1, Z_FL - 0.01, L1[0])
# навесы над кнопками: стенка у края платформы + плечо над штоком
ONE_BTN = True                                                             # 23.11 (владелец, после пробы): одна кнопка наверху сбоку, с другой стороны — язык в паз; ось сзади зажата
Z_B0 = 10.0                                                                        # низ кнопки на неподвижной стойке на окантовке (было на окантовке, z 2.5)
Z_AWH = Z_B0 + BTN_H + BTN_HP                                                     # низ плеча над кнопкой = верх штока (15.0)
if MOD == "P":
    # кнопка справа (+x): плечо от стойки бруска наружу, низ на 15.0 над штоком
    base += BB(X_C0, X_BR, YB - 2.2, YB + 2.2, Z_AWH, L1[0] - 0.1)
    base += BB(X_C0, X_BR, K.BMY0 + 0.1, K.BMY1 - 0.1, Z_AWH, L1[0])
    # слева (−x): язык от стойки бруска в вертикальный паз неподвижной стойки
    base += BB(-(XB + 1.6), -XP + 0.1, YB - 1.0, YB + 1.0, 12.0, L1[0] - 0.1)
else:                                                                             # З (владелец): балка за платформой — ножки над окантовкой на кнопки + переходник к блоку стойки бруска
    for sx in (-1, 1):
        base += BB(*sorted((sx * X_C0, sx * X_BR)), K.BMY0 + 0.1, K.BMY1 - 0.1, Z_AW, L1[0])     # блок стойки бруска наружу
        base += BB(*sorted((sx * X_C0, sx * X_BR)), 1.15, 5.55, Z_AW, L1[0] - 0.1)
        lx = sorted((sx * (XB - 2.0), sx * (XB + 2.0)))
        base += BB(*lx, YB - 1.5, YB + 1.5, Z_AWH if sx > 0 else 12.0, L2[0])                 # ножка балки (23.11): справа низ давит на кнопку (15), слева входит в паз стойки (низ 12)
        base += BB(*lx, YB - 1.5, 5.0, Z_AWH, L1[0] - 0.1)                                     # переходник ножка — блок стойки бруска, сплошной (21.11), низ выше стоек окантовки
if MOD == "Z":                                                                    # З: сзади (внешний край ряда) пол длиннее на 3.5 — там стойки 49E; у П сзади сосед З
    base += BB(-XP, XP, 30.0, 34.0, 0, Z_FL)
Y0p, Y1p = base.bounding_box().min.Y, base.bounding_box().max.Y
Y0ALL = Y0p                                                                       # самая передняя точка платформы (с ножками З)
if MOD == "Z":
    Y0p = YM - 16.1                                                               # край пола
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
        table += BB(*sorted((sx * (XP - RW_T), sx * XP)), 12.0, 19.0, Z_FL - 0.6, L2[0] + 0.01)          # стенки короче — задние углы свободны под стойки 49E
        base -= BB(*sorted((sx * (XP - RW_T - 0.15), sx * (XP + 0.15))), 11.85, 19.15, Z_FL - 0.6, Z_FL + 4.5)   # паз в полу + срез кольца
    parts["rack"] = table
    br_y = "столик"
else:                                                                             # П (владелец): по спинке рейки бегает тележка — под концом рейки только скос-распорка до пола
    yr0, yr1 = 12.0, V.fix_o.bounding_box().max.Y - 0.2
    X_HI = 24.5                                                                   # держатель (владелец): вверху широкий — до конца рейки над окантовкой, внизу узкий на краю платформы, снаружи скос
    for sx in (-1, 1):
        base += prof_y([(sx * (XP - RW_T), Z_FL - 0.01), (sx * XP, Z_FL - 0.01), (sx * X_HI, L2[0]), (sx * (XP - RW_T), L2[0])], yr0, yr1)
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
pair, best = None, -1                                                             # пара с квадратурой, разнесённая как можно дальше (по углам, владелец)
for a1 in sorted(ok):
    for a2 in sorted(ok):
        d = (a2 - a1) % 360
        if a2 <= a1 or abs((d % 45) - 22.5) > 0.01: continue
        sep = min(d, 360 - d)
        if sep > best and iv(ok[a1][0], ok[a2][0]) < 0.01:
            pair, best = (a1, a2), sep
print("стойки 49E: подходящие углы", sorted(ok), "→ пара", pair)
if pair:
    parts["posts"] = ok[pair[0]][0] + ok[pair[1]][0]
    parts["sens"] = DB.rotm(pair[0], SE0) + DB.rotm(pair[1], SE0)
    base = base - ok[pair[0]][1] - ok[pair[1]][1]

# ---------- язычки-ось, подъём низа пола ----------
YT = Y1p - 2.0                                                                    # язычки-ось ВБОК в боковую окантовку (в ряду сзади сосед)
for sx in (-1, 1):
    base += BB(*sorted((sx * (XP - 0.5), sx * (XP + G + 2.0))), YT - 1.25, YT + 1.25, 0.8, 2.0)
Y_PIV, Z_PIV = YT, 1.4
DROP = TRAVEL * (Y_PIV - Y0ALL) / (Y_PIV - YBB)
Z_LIFT = round(DROP + 0.2, 2)
base -= BB(-30, 30, -40, 60, -1, Z_LIFT)
platform = {"base": base, **parts, "brusok": BRUSOK, "motor": K.motor}

# ---------- окантовка 8 мм + вазы + кнопки ----------
# у П спереди окантовки нет (там П2)
rim = BB(-HALF, HALF, min(Y0p, YBB - RH) - G - (0 if MOD == "P" else RW), Y1p + G + RW, 0, Z_FL) - BB(-XP - G, XP + G, Y0p - G, Y1p + G, -1, Z_FL + 1)
for sx in (-1, 1):
    rim -= BB(*sorted((sx * (XP + G - 0.01), sx * (XP + G + 2.2))), YT - 1.4, YT + 1.4, 0.75, Z_FL + 1)   # ямка под язычок, открыта сверху — платформа просто кладётся (владелец)
vases, btns, lids = Part(), Part(), Part()
if ONE_BTN:
    # справа: стойка на окантовке, наверху ваза с кнопкой (две щели по бокам для выводов + канавка вниз по стойке)
    st = BB(XB - RH, XB + RH, YBB - RH, YBB + RH, Z_FL - 0.01, Z_B0)
    for sy in (-1, 1):                                                            # канавки для проводов вниз по стойке с обеих сторон (шире: 2.2 × 1.5)
        st -= BB(XB - 1.1, XB + 1.1, *sorted((YBB + sy * (RH + 1), YBB + sy * (RH - 1.5))), Z_FL - 1, Z_B0 + 10)   # сквозной проход: щель вазы сразу переходит в канавку по стойке, без перемычки (владелец)
    v_ = CZ(RH, Z_B0 - 0.01, Z_B0 + BTN_H + 0.5, XB, YBB) - CZ(BTN_D / 2 + 0.15, Z_B0, Z_B0 + 10, XB, YBB)
    v_ -= BB(XB - 1.1, XB + 1.1, YBB - RH - 1, YBB + RH + 1, Z_B0, Z_B0 + 10)                      # щели для выводов 2.2
    vases += st + v_
    PILLAR_BTN = st + v_                                                          # отдельно — для сцены «двигать руками»
    btns += CZ(BTN_D / 2, Z_B0, Z_B0 + BTN_H, XB, YBB) + CZ(Z.BTN_DP / 2, Z_B0 + BTN_H - 0.01, Z_AWH, XB, YBB)
    # слева: стойка с вертикальным пазом под язык (ход вниз 2 мм, сверху паз открыт)
    if MOD == "P":
        gs = BB(-(XB + RH), -(XP + G + 0.2), YB - 3.0, YB + 3.0, Z_FL - 0.01, L1[0] - 0.4)
        gs -= BB(-(XB + 1.8), -(XP + G + 0.1), YB - 1.5, YB + 1.5, 10.0, L1[0])
    else:                                                                         # З: в паз входит сама ножка балки (4×3), верх стойки под переходником
        gs = BB(-(XB + RH), -(XP + G + 0.2), YBB - RH, YBB + RH, Z_FL - 0.01, Z_AWH - 0.5)
        gs -= BB(-(XB + 2.5), -(XB - 2.5), YBB - 2.0, YBB + 2.0, 10.0, Z_AWH)                    # зазор 0.5: при наклоне верх языка уходит вбок на ~0.25
    vases += gs
    PILLAR_GROOVE = gs
    if MOD == "Z":                                                                # З: стойки отдельные, на клей — снизу пробка 0.4 в гнездо окантовки (сама встаёт на место; над язычком соседа П остаётся 0.1)
        for q in (PILLAR_BTN, PILLAR_GROOVE):
            b_ = q.bounding_box()
            plug = BB(b_.min.X + 0.15, b_.max.X - 0.15, b_.min.Y + 0.15, b_.max.Y - 0.15, Z_FL - 0.4, Z_FL + 0.01)
            rim -= BB(b_.min.X + 0.05, b_.max.X - 0.05, b_.min.Y + 0.05, b_.max.Y - 0.05, Z_FL - 0.4, Z_FL + 0.01)
            vases += plug
        PILLAR_BTN = PILLAR_BTN + BB(PILLAR_BTN.bounding_box().min.X + 0.15, PILLAR_BTN.bounding_box().max.X - 0.15, PILLAR_BTN.bounding_box().min.Y + 0.15, PILLAR_BTN.bounding_box().max.Y - 0.15, Z_FL - 0.4, Z_FL + 0.01)
        PILLAR_GROOVE = PILLAR_GROOVE + BB(PILLAR_GROOVE.bounding_box().min.X + 0.15, PILLAR_GROOVE.bounding_box().max.X - 0.15, PILLAR_GROOVE.bounding_box().min.Y + 0.15, PILLAR_GROOVE.bounding_box().max.Y - 0.15, Z_FL - 0.4, Z_FL + 0.01)
    # ось сзади зажата: крышки на ямки язычков (кладутся после платформы, на клей)
    for sx in (-1, 1):
        lids += BB(*sorted((sx * (XP + G + 0.1), sx * (XP + G + 2.1))), YT - 1.3, YT + 1.3, 2.1, Z_FL) + BB(*sorted((sx * (XP + G + 0.1), sx * (XP + G + 3.2))), YT - 2.0, YT + 2.0, Z_FL - 0.01, Z_FL + 0.8)   # пробка в ямку + шляпка на окантовку (клей)
else:
    for sx in (-1, 1):
        v_ = CZ(RH, Z_FL - 0.01, Z_FL + BTN_H + 0.5, sx * XB, YB) - CZ(BTN_D / 2 + 0.15, Z_FL, Z_FL + 10, sx * XB, YB)
        v_ -= BB(sx * XB - 0.7, sx * XB + 0.7, YB - RH - 1, YB + RH + 1, Z_FL, Z_FL + 10)             # две щели для выводов — по бокам, вдоль окантовки (владелец)
        vases += v_
        btns += CZ(BTN_D / 2, Z_FL, Z_FL + BTN_H, sx * XB, YB) + CZ(Z.BTN_DP / 2, Z_FL + BTN_H - 0.01, Z_AW, sx * XB, YB)
fx = rim + vases + lids

# ---------- проверка ----------
ang = math.degrees(TRAVEL / abs(Y_PIV - YBB))
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
