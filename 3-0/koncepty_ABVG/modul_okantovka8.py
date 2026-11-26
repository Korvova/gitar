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
if os.environ.get("GB") == "1":
    Z_RF = 17.83                                                                  # торец ротора GB1806 = низ прежней шестерни → всё над мотором без изменений
    Z_CAP0 = Z_RF - 20.5                                                          # низ заводского стакана с платой AS5600 (мотор 13 + стакан 7.5)
    _gm0 = K.gm
    GB_GEAR = (_gm0 & BB(-20, 20, -20, 20, 19.23, 40)) + CZ(4.0, Z_RF, 19.24)     # шестерня: зубья прежние + фланец Ø8 (не шире зубьев — печать без нависаний) прямо на ротор
    for _a in (0, 90, 180, 270):                                                  # 4 штыря Ø1.9 в резьбовые М2 ротора (Ø6) — центруют и передают момент, капля клея
        GB_GEAR += CZ(0.95, Z_RF - 1.5, Z_RF + 0.01, 3 * math.cos(math.radians(_a)), 3 * math.sin(math.radians(_a)))
    K.gm = GB_GEAR
    DB.plat = CZ(4.0, Z_RF, 19.24)                                                # «платформы ротора» больше нет — только фланец шестерни
    K.motor = CZ(11.0, Z_RF - 13.0, Z_RF, 0, YM) + CZ(11.0, Z_CAP0, Z_RF - 12.99, 0, YM)
MOD = os.environ.get("MOD", "P")
PV = os.environ.get("PV", "2") if MOD == "P" else ""                              # П: 2 — кнопка под держателем рейки (24.11), 3 — плечи как у З: кнопка спереди справа, слева ножка в паз (24.11, владелец)
GB = os.environ.get("GB") == "1"                                                # 25.11 (владелец): мотор GB1806 (Ø22, датчик AS5600 в заводском стакане снизу) вместо 2204 + магнитов + 49E
TAG = MOD + ("3" if PV == "3" else "") + ("GB" if GB else "")
OUT = os.path.join(os.path.dirname(HERE), "19.67_okantovka8_%s" % TAG); os.makedirs(os.path.join(OUT, "asm"), exist_ok=True)
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
P3 = MOD == "P" and PV == "3"
FEET = 5.6 if GB else (1.5 if P3 else 0.0)                                                         # 24.11 (владелец, после пробы П3): окантовка на 1.5 выше стола — низ пола упирался в стол (запас был 0.5)
LR = P3 and os.environ.get("LR") == "1"                                                   # 24.11 вечер (владелец, после печати П3): качание СЛЕВА НАПРАВО — ось вдоль Y по левому краю, кнопка справа
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
base = (base - CZ(12.55, -10, 40, 0, YM)) if GB else motor_mount(base)        # GB: в полу сквозное Ø25.1 — снизу вклеивается чашка со стаканом мотора
parts = {"rack": V.fix_o}
if MOD == "Z":                                                                    # балка З на сплошной стенке до пола (тележка низ балки не трогает) — колонн нет
    parts.update({"beam": Z.beam_body - BB(-30, 30, -40, 40, -1, L2[0])})
    base -= BB(-30, 30, -40, YM - 16.1, -1, 40)                                    # 20.11 (владелец): платформа З — в диаметр мотора, хвоста нет
    cart, YB = Z.cart, Z.Y_BC                                                     # кнопки под балкой (владелец)
else:
    cart, YB = R.cart_H, (4.6 if PV == "3" else 13.9)                                                    # 24.11 (владелец): кнопка П — под держателем рейки (y 12.4..15.5), брусок спереди — просто направляющая
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
BRUSOK -= CZ(DB.plat.bounding_box().max.X + 0.5, L1[0] - 1, L1[0] + 0.6, 0, YM)       # 24.11 (владелец): брусок тёрся о верх ротора (зазор был 0.17) — выемка снизу 0.6 по кругу ротора → 0.77
DEEP = 0.6                                                                        # 24.11 (владелец, П): брусок со стойками, плечом и языком — ОДНА деталь, ставится сверху, низ стоек в гнёзда пола на клей
for sx in (-1, 1):                                                                # стойки бруска: под ним, не шире его (стенки паза ползуна проходят мимо)
    if MOD == "P" and PV == "3":
        pass                                                                      # П3 (владелец): передних стоек нет — брусок висит на «Г»-плечах от держателей рейки
    elif MOD == "P":
        BRUSOK += BB(*sorted((sx * X_C0, sx * XP)), K.BMY0 + 0.1, K.BMY1 - 0.1, Z_FL - DEEP, L1[0] + 0.01)
        base -= BB(*sorted((sx * (X_C0 - 0.15), sx * (XP + 0.15))), K.BMY0 - 0.05, K.BMY1 + 0.05, Z_FL - DEEP, Z_FL + 0.01)
    else:
        base += BB(*sorted((sx * X_C0, sx * XP)), K.BMY0 + 0.1, K.BMY1 - 0.1, Z_FL - 0.01, L1[0])
# навесы над кнопками: стенка у края платформы + плечо над штоком
ONE_BTN = True                                                             # 23.11 (владелец, после пробы): одна кнопка наверху сбоку, с другой стороны — язык в паз; ось сзади зажата
Z_B0 = 11.0 if P3 else 10.0                                                                        # низ кнопки на неподвижной стойке на окантовке (было на окантовке, z 2.5)
Z_AWH = 10.0 + BTN_H + BTN_HP                                                     # П3: гнездо кнопки на 1 мм выше (на печати подкладывал 1 мм — шток был утоплен), низ плеча прежний
Z_TNG, Z_SLOT = 12.0, 9.0                                                         # П: низ языка / дно паза — запас вниз 3.0 (ход 0.3), язык никогда не ложится на дно
if MOD == "P":
    # кнопка справа (+x): плечо от стойки бруска наружу, низ на 15.0 над штоком
    if PV == "3":                                                                 # П3: плечи заодно с бруском — справа над кнопкой, слева с ножкой в паз; сзади стенка-нога в пол + раскос под плечом
        # 24.11 (владелец): три детали — 2 плеча + брусок; плечо → столб рейки шипом сзади, брусок → плечо шипом сверху (пазы с зазором 0.1)
        Y_ARM1 = 12.3                                                             # плечо до 0.1 от столба рейки (столб с y 12.4)
        ARMS, TABS, KEYS = {}, [], []
        for sx in (-1, 1):
            a_ = BB(*sorted((sx * 14.5, sx * X_BR)), YB - 2.2, Y_ARM1, Z_AWH, L1[0] - 0.1)
            a_ += BB(*sorted((sx * 14.5, sx * X_BR)), K.BMY0 + 0.1, K.BMY1 - 0.1, Z_AWH, L1[0])                 # под бруском — до его низа (контакт для клея)
            tb = BB(*sorted((sx * 15.3, sx * 20.9)), Y_ARM1 - 0.01, 13.9, Z_AWH, 19.0); TABS.append(tb)       # шип в столб: 5.6 × 1.6 × 4
            ky = BB(*sorted((sx * 16.0, sx * 23.0)), 2.9, 4.1, L1[0] - 0.01, L1[0] + 0.8); KEYS.append(ky)    # шип в брусок: 7 × 1.2 × 0.8
            a_ += tb + ky
            if sx < 0:
                a_ -= BB(-(XB + 2.1), -(XP + G + 0.1), YB - 1.5, YB + 1.5, Z_AWH - 0.01, Z_AWH + 3.0)          # паз снизу под шип стойки окантовки
            ARMS["prav" if sx > 0 else "lev"] = a_
        for ky in KEYS:
            b_ = ky.bounding_box(); BRUSOK -= BB(b_.min.X - 0.1, b_.max.X + 0.1, b_.min.Y - 0.1, b_.max.Y + 0.1, L1[0] - 0.1, b_.max.Z + 0.1)
else:                                                                             # З (владелец): балка за платформой — ножки над окантовкой на кнопки + переходник к блоку стойки бруска
    for sx in (-1, 1):
        base += BB(*sorted((sx * X_C0, sx * X_BR)), K.BMY0 + 0.1, K.BMY1 - 0.1, Z_AW, L1[0])     # блок стойки бруска наружу
        base += BB(*sorted((sx * X_C0, sx * X_BR)), 1.15, 5.55, Z_AW, L1[0] - 0.1)
        lx = sorted((sx * (XB - 2.0), sx * (XB + 2.0)))
        base += BB(*lx, YB - 1.5, YB + 1.5, Z_AWH if sx > 0 else 12.0, L2[0])                 # ножка балки (23.11): справа низ давит на кнопку (15), слева входит в паз стойки (низ 12)
        base += BB(*lx, YB - 1.5, 5.0, Z_AWH, L1[0] - 0.1)                                     # переходник ножка — блок стойки бруска, сплошной (21.11), низ выше стоек окантовки
if MOD == "Z":                                                                    # З: сзади (внешний край ряда) пол длиннее на 3.5 — там стойки 49E; у П сзади сосед З
    base += BB(-XP, XP, 30.0, 34.0, 0, Z_FL)
D_PIV_Z = (34.0 - 2.0) - Z.Y_BC                                                   # З: от язычка до кнопки 37.9 — у З клик «прям хорошо»
if P3 and not LR and os.environ.get("LONG") == "1":                                                                 # 24.11 (владелец): П3 — зад платформы длиннее, чтобы язычок—кнопка было как у З
    base += BB(-XP, XP, base.bounding_box().max.Y - 1.0, YB + D_PIV_Z + 2.0, 0, Z_FL)
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
    yr0, yr1 = 12.4, V.fix_o.bounding_box().max.Y - 0.2                            # 24.11: держатель от y 12.4 — шестерня и тележка в крайних не задевают
    X_HI = 24.5                                                                   # держатель (владелец): вверху широкий — до конца рейки над окантовкой, внизу узкий на краю платформы, снаружи скос
    rk = V.fix_o                                                                  # 24.11 (владелец): рейка и держатели — ОДНА деталь, низ держателей в пазы пола (срез кольца мотора)
    for sx in (-1, 1):
        if PV == "3":                                                             # П3: держатель прежний — со скосом снаружи (кнопки под ним нет)
            rk += prof_y([(sx * (XP - RW_T), Z_FL - DEEP), (sx * XP, Z_FL - DEEP), (sx * XP, Z_FL), (sx * X_HI, L2[0]), (sx * (XP - RW_T), L2[0])], yr0, yr1)
        else:
            rk += prof_y([(sx * (XP - RW_T), Z_FL - DEEP), (sx * XP, Z_FL - DEEP), (sx * XP, Z_AWH), (sx * X_HI, Z_AWH), (sx * X_HI, L2[0]), (sx * (XP - RW_T), L2[0])], yr0, yr1)   # «Г»: стойка в паз пола + плоское плечо, низ плеча 15.0 = верх штока
        base -= BB(*sorted((sx * (XP - RW_T - 0.15), sx * (XP + 0.15))), yr0 - 0.15, yr1 + 0.15, Z_FL - DEEP, L2[0])
    if PV != "3":
        rk += BB(-(XB + 1.6), -(XP + G + 0.6), YB - 1.0, YB + 1.0, Z_TNG, Z_AWH + 0.01)    # слева под плечом — язык в паз стойки (зазор 0.5 по x и y, дно паза на 3 ниже)
    if PV == "3":                                                                 # П3 (владелец): балка отдельно, концы плеч вырезаны по столбам (булева) — клей, сама встаёт на место
        # 24.11 (владелец): держатели — отдельные детали (печать плашмя на задней грани: паз под шип плеча смотрит вверх),
        # сверху у держателя шип в паз снизу рейки; рейка печатается верхом на стол
        rk = V.fix_o; HOLD = {}
        for sx in (-1, 1):
            h_ = prof_y([(sx * (XP - RW_T), Z_FL - DEEP), (sx * XP, Z_FL - DEEP), (sx * XP, Z_FL), (sx * X_HI, L2[0]), (sx * (XP - RW_T), L2[0])], yr0, yr1)
            for tb in TABS:                                                       # паз под шип плеча
                b_ = tb.bounding_box(); h_ -= BB(b_.min.X - 0.1, b_.max.X + 0.1, 12.0, b_.max.Y + 0.1, b_.min.Z - 0.1, b_.max.Z + 0.1)
            tt = BB(*sorted((sx * 17.5, sx * 23.0)), 13.4, 14.7, L2[0] - 0.01, L2[0] + 1.0)              # шип в рейку 5.5 × 1.3 × 1 (за y 14.86 под рейкой бегает крюк тележки)
            h_ += tt; b_ = tt.bounding_box()
            rk -= BB(b_.min.X - 0.1, b_.max.X + 0.1, b_.min.Y - 0.1, b_.max.Y + 0.1, L2[0] - 0.1, b_.max.Z + 0.1)
            HOLD["prav" if sx > 0 else "lev"] = h_
        parts["holders"] = HOLD["prav"] + HOLD["lev"]
        parts["arms"] = ARMS["prav"] + ARMS["lev"]
    parts["rack"] = rk; print("  рейка+держатели: тел", len(rk.solids()))
    br_y = "скос"
stat0 = Part() + [base, K.motor] + ([BRUSOK] if BRUSOK else []) + list(parts.values())

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
for k in range(0 if GB else 144):
    a = 2.5 * k
    p, sl = DB.rotm(a, P0), DB.rotm(a, SL0)
    b_ = p.bounding_box()
    if b_.min.X < -XP + 0.05 or b_.max.X > XP - 0.05 or b_.min.Y < Y0p + 0.05 or b_.max.Y > Y1p - 0.05: continue
    if iv(p, Part() + [base - sl, K.motor] + ([BRUSOK] if BRUSOK else []) + [v for n, v in parts.items()]) > 0.01: continue
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
if LR:                                                                            # П3: два язычка ВЛЕВО (спереди и сзади) — ось вдоль Y; справа язычка нет, правый край висит на штоке
    Y_TABS = (YB + 5.4, YT)                                                       # передний — сразу за стойкой с шипом (она стоит над y YB±3)
    for yt in Y_TABS:
        base += BB(-(XP + G + 2.0), -(XP - 0.5), yt - 1.25, yt + 1.25, 0.8, 2.0)
    X_PIV, Z_PIV = -(XP + G + 1.0), 1.4
    Y_PIV = YT
    DROP = TRAVEL * (XP - X_PIV) / (XB - X_PIV)                                    # правый край пола опускается сильнее всего
else:
    Y_TABS = (YT,)
    for sx in (-1, 1):
        base += BB(*sorted((sx * (XP - 0.5), sx * (XP + G + 2.0))), YT - 1.25, YT + 1.25, 0.8, 2.0)
    Y_PIV, Z_PIV = YT, 1.4
    DROP = TRAVEL * (Y_PIV - Y0ALL) / (Y_PIV - YBB)
Z_LIFT = round(DROP + 0.2, 2)
base -= BB(-30, 30, -40, 60, -1, Z_LIFT)
if GB:                                                                            # чашка: стакан мотора стоит на её дне (винты М2 снизу в потай), губа клеится под пол
    Z_CUP0 = Z_CAP0 - 1.6
    CUP = CZ(12.45, Z_CUP0, Z_LIFT, 0, YM) - CZ(11.25, Z_CAP0, Z_LIFT + 1, 0, YM)
    CUP += Pos(0, YM, Z_LIFT - 1.35) * Cone(12.45, 13.8, 1.35, align=(Align.CENTER, Align.CENTER, Align.MIN)) - CZ(11.25, Z_LIFT - 2, Z_LIFT + 1, 0, YM)
    for _a in range(0, 360, 60):                                                  # 6 отверстий М2 на Ø18 (у мотора 6, стакан берёт 4 из них) + потай под головку
        _x, _y = 9 * math.cos(math.radians(_a)), YM + 9 * math.sin(math.radians(_a))
        CUP -= CZ(1.1, Z_CUP0 - 1, Z_CAP0 + 0.1, _x, _y) + CZ(1.95, Z_CUP0 - 1, Z_CUP0 + 1.0, _x, _y)
    CUP -= CZ(2.5, Z_CUP0 - 1, Z_CAP0 + 0.1, 0, YM)                                # центр — посмотреть/продуть
    CUP -= BB(-14, -9, YM - 3.5, YM + 3.5, Z_CAP0 + 2.5, Z_LIFT + 1)                # прорезь в стенке под провода стакана (стакан повернуть щелью сюда)
    parts["stakan"] = CUP
platform = {"base": base, **parts, "motor": K.motor}
if BRUSOK: platform["brusok"] = BRUSOK

# ---------- окантовка 8 мм + вазы + кнопки ----------
# у П спереди окантовки нет (там П2)
rim = BB(-HALF, HALF, min(Y0p, YBB - RH) - G - (0 if MOD == "P" else RW), Y1p + G + RW, -FEET, Z_FL) - BB(-XP - G, XP + G, Y0p - G, Y1p + G, -FEET - 1, Z_FL + 1)
for sx, yt in ([(-1, y_) for y_ in Y_TABS] if LR else [(-1, YT), (1, YT)]):
    rim -= BB(*sorted((sx * (XP + G - 0.01), sx * (XP + G + 2.2))), yt - 1.4, yt + 1.4, 0.75, Z_FL + 1)   # ямка под язычок, открыта сверху — платформа просто кладётся (владелец)
vases, btns, lids = Part(), Part(), Part()
if ONE_BTN:
    # справа: стойка на окантовке, наверху ваза с кнопкой (две щели по бокам для выводов + канавка вниз по стойке)
    st = BB(XB - RH, XB + RH, YBB - RH, YBB + RH, Z_FL - 0.01, Z_B0)
    for sy in (-1, 1):                                                            # канавки для проводов вниз по стойке с обеих сторон (шире: 2.2 × 1.5)
        st -= BB(XB - 1.1, XB + 1.1, *sorted((YBB + sy * (RH + 1), YBB + sy * (RH - 1.5))), Z_FL - 1, Z_B0 + 10)   # сквозной проход: щель вазы сразу переходит в канавку по стойке, без перемычки (владелец)
    v_ = CZ(RH, Z_B0 - 0.01, min(Z_B0 + BTN_H + 0.5, Z_AWH - (1.5 if P3 else 0.6)), XB, YBB) - CZ(BTN_D / 2 + 0.15, Z_B0, Z_B0 + 10, XB, YBB)   # П3: гнездо выше на 1 — край вазы не выше 0.6 под плечом
    v_ -= BB(XB - 1.1, XB + 1.1, YBB - RH - 1, YBB + RH + 1, Z_B0, Z_B0 + 10)                      # щели для выводов 2.2
    vases += st + v_
    PILLAR_BTN = st + v_                                                          # отдельно — для сцены «двигать руками»
    btns += CZ(BTN_D / 2, Z_B0, Z_B0 + BTN_H, XB, YBB) + CZ(Z.BTN_DP / 2, Z_B0 + BTN_H - 0.01, Z_AWH, XB, YBB)
    # слева: стойка с вертикальным пазом под язык (ход вниз 2 мм, сверху паз открыт)
    if MOD == "P":
        Z_GS = Z_AWH - (1.8 if P3 else 0.8)                                       # П3: верх стойки и шип ниже на 1.0/1.5 — ход упирается только в кнопку
        gs = BB(-(XB + RH), -(XP + G + 0.2), YB - 3.0, YB + 3.0, Z_FL - 0.01, Z_GS)       # верх под плечом держателя (ход 0.3 + запас)
        if PV == "3":                                                             # шип вверх в паз левого плеча: зазоры 0.5 по x/y, сверху 0.6 (ход 0.3)
            gs += BB(-(XB + 1.6), -(XP + G + 0.6), YB - 0.8, YB + 0.4, Z_GS - 0.01, Z_AWH + 0.9)   # тоньше по y: при наклоне задняя стенка паза плеча идёт вперёд
        else:
            gs -= BB(-(XB + 2.1), -(XP + G + 0.1), YB - 1.5, YB + 1.5, Z_SLOT, L1[0])           # паз: по x зазор 0.5 до торца языка, по y 0.5, дно на 3 ниже языка
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
    for sx, yt in ([(-1, y_) for y_ in Y_TABS] if LR else [(-1, YT), (1, YT)]):
        lids += BB(*sorted((sx * (XP + G + 0.1), sx * (XP + G + 2.1))), yt - 1.3, yt + 1.3, 2.1, Z_FL) + BB(*sorted((sx * (XP + G + 0.1), sx * (XP + G + 3.2))), yt - 2.0, yt + 2.0, Z_FL - 0.01, Z_FL + 0.8)   # пробка в ямку + шляпка на окантовку (клей)
else:
    for sx in (-1, 1):
        v_ = CZ(RH, Z_FL - 0.01, Z_FL + BTN_H + 0.5, sx * XB, YB) - CZ(BTN_D / 2 + 0.15, Z_FL, Z_FL + 10, sx * XB, YB)
        v_ -= BB(sx * XB - 0.7, sx * XB + 0.7, YB - RH - 1, YB + RH + 1, Z_FL, Z_FL + 10)             # две щели для выводов — по бокам, вдоль окантовки (владелец)
        vases += v_
        btns += CZ(BTN_D / 2, Z_FL, Z_FL + BTN_H, sx * XB, YB) + CZ(Z.BTN_DP / 2, Z_FL + BTN_H - 0.01, Z_AW, sx * XB, YB)
fx = rim + vases + lids

# ---------- проверка ----------
if LR:
    ang = math.degrees(TRAVEL / (XB - X_PIV))
    def pressed(p):
        return Pos(X_PIV, 0, Z_PIV) * Rot(0, ang, 0) * Pos(-X_PIV, 0, -Z_PIV) * p
else:
    ang = math.degrees(TRAVEL / abs(Y_PIV - YBB))
    def pressed(p):
        return Pos(0, Y_PIV, Z_PIV) * Rot(ang, 0, 0) * Pos(0, -Y_PIV, -Z_PIV) * p
bad = 0
for nm, pose in (("покой", lambda p: p), ("нажато", pressed)):
    for n, p in platform.items():
        v = iv(pose(p), fx)
        if v > 0.02: bad += 1; print("  %s × окантовка (%s) %.3f" % (n, nm, v))
        if n not in ((("arms",) if PV == "3" else ("rack",)) if MOD == "P" else ("base",)):                   # кто давит на шток: у П — плечо держателя рейки, у З — ножка на платформе
            v = iv(pose(p), btns)
            if v > 0.02: bad += 1; print("  %s × кнопки (%s) %.3f" % (n, nm, v))
    for mv in MOV:
        for n, p in mv.items():
            v = iv(pose(p), fx) + iv(pose(p), btns)
            if v > 0.02: bad += 1; print("  %s × окантовка/кнопки (%s) %.3f" % (n, nm, v))
    v = iv(pose(Part() + [platform[k] for k in ("base", "brusok", "rack", "arms") if k in platform]), btns)
    print("  навесы × штоки (%s): %.2f мм³" % (nm, v))
    if nm == "покой" and v > 0.02: bad += 1
for n, p in parts.items():                                                       # детали платформы между собой
    for n2, p2 in parts.items():
        if n < n2 and not {n, n2} <= {"rack", "rack_br"}:
            v = iv(p, p2)
            if v > 0.02: bad += 1; print("  %s × %s %.3f" % (n, n2, v))
if MOD == "P":                                                                    # 24.11: брусок-блок и рейка с держателями — отдельные детали: между собой, с полом и с подвижными
    trio = {"pol": platform["base"], "rejka": platform["rack"], **({"derzh": platform["holders"]} if "holders" in platform else {}), **({"brusok": platform["brusok"]} if "brusok" in platform else {}), **({"plechi": platform["arms"]} if "arms" in platform else {})}
    for a_ in trio:
        for b_ in trio:
            if a_ < b_:
                v = iv(trio[a_], trio[b_])
                if v > 0.02: bad += 1
                print("  ПРОВЕРКА %s × %s: %.3f" % (a_, b_, v))
    vm = sum(iv(p, trio[k]) for mv in MOV for n, p in mv.items() for k in ("brusok", "rejka", "plechi", "derzh") if k in trio)
    if vm > 0.05: bad += 1
    print("  ПРОВЕРКА подвижные (ползун, шестерни, тележка) × брусок/рейка: %.3f" % vm)
    print("  ротор верх %.2f — брусок низ над ним %.2f → зазор %.2f" % (DB.plat.bounding_box().max.Z, L1[0] + 0.6, L1[0] + 0.6 - DB.plat.bounding_box().max.Z))
    print("  язык/шип: %s; плечо низ %.1f = верх штока %.1f; кнопка y %.1f; балка тел %s" % ("шип вверх до %.1f, паз в плече до %.1f (запас 2.1)" % (Z_AWH + 0.9, Z_AWH + 3.0) if PV == "3" else "низ %.1f, дно паза %.1f" % (Z_TNG, Z_SLOT), Z_AWH, Z_AWH, YB, "%d, плечи %s" % (len(BRUSOK.solids()), [len(a_.solids()) for a_ in ARMS.values()]) if PV == "3" else "-"))
    for s_ in (-S, S):
        for n, p in moving(s_).items():
            for k in [k_ for k_ in ("brusok", "rejka", "plechi", "derzh") if k_ in trio]:
                v = iv(p, trio[k])
                if v > 0.005: print("    касание s=%+.0f %s × %s %.3f" % (s_, n, k, v))
zmin = pressed(platform["base"]).bounding_box().min.Z
if zmin < -FEET + 0.05: bad += 1
print("модуль %s, окантовка 8: %s | платформа ±%.1f, кнопки x=±%.2f y=%.2f, стойки 49E %s, кронштейны y=%s, низ пола +%.2f, наклон %.2f°" % (
    MOD, ("ось вдоль Y слева x=%.1f, язычки y=%s, " % (X_PIV, [round(v_, 1) for v_ in Y_TABS]) if LR else "") + ("ЧИСТО" if not bad else "%d проблем" % bad), XP, XB, YB, pair, br_y, Z_LIFT, ang))
asm = {**platform, "frame": fx, "btns": btns, "cart": cart, "slider": SL, "flo": K.flo0, "gm": K.gm, **({} if GB else {"plat": DB.plat, "mags": DB.mags})}
for n, p in asm.items():
    export_stl(Part() + p, os.path.join(OUT, "asm", n + ".stl"), tolerance=0.02, angular_tolerance=0.2)
open(os.path.join(OUT, "asm", "params.txt"), "w").write("%f %f %f %f %f" % (YM, K.Y_G, A, RF, RM))
open(os.path.join(OUT, "asm", "klav.txt"), "w").write(("X %f %f %f" % (X_PIV, ang, Z_PIV)) if LR else ("%f %f %f" % (Y_PIV, ang, Z_PIV)))
