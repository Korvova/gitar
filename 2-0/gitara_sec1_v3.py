# -*- coding: utf-8 -*-
"""ГИТАРА: СЕКЦИЯ-1 v3 (27.09.2026) — рычаг ×2 вместо ×5.2.

Отличия от v2: плечо 36 : 18 (было 52 : 10). Лента ходит ±11 мм (было ±4.2) на те же ±22 пальца —
люфт ленты, стадов и шестерни мотора на пальце умножается на 2, а не на 5.2.
Короткое плечо больше 18 не влезает: кольцо стада подходит к стенке x 24.
  * оси плеч на CARTS_Y + 36; мах плеча ±37.7°;
  * штырь на махе уходит к оси на 36·(1 − cos) = 7.5 мм — прорези плит и палубы до yc + 10.7,
    ложе v3 с длинной дыркой и длинными полозьями (ложе — здесь же, внизу);
  * стад на коротком плече уходит по X на 3.8 мм — голова спицы с ПРОРЕЗЬЮ вдоль X (по Y плотно),
    лента больше не гнётся вбок; от головы «колено» к жёлобу x 6..14;
  * винт стяжки (23.5, 120) убран — там ходит голова спицы этажа 3; стопку держат остальные пять.
В деке к этому — кривошипы R15 рычажком (gitara_deka.py, DEKA_X2=1).
Файлы — с суффиксом _v3. Запуск: .venv-b123d\\Scripts\\python gitara_sec1_v3.py

Было v2 (26.09.2026) — тележки на шаге V позиции 26/25/24 мм.

Отличия от v0 (gitara_sec1.py, напечатана и собрана): v0 ставила тележки вплотную
с шагом 16 — это расстояние между пальцами у XII лада, пальцам тесно (владелец 26.09).
v2: CARTS_Y 16/42/67/91 (лады 5-8 при мензуре 650), тележка 12 x 18, у каждой своё
русло (бортики между тележками), паз под штырь закрыт с обеих сторон и длиннее — штырь
гуляет по Y на 4 мм в крайних положениях и тележку больше не толкает. Средняя стяжка
уехала с y=80 (там теперь ходят тележки) на y=120. Файлы — с суффиксом _v2.

Было v0:

Координаты: Y вдоль грифа (0 = порожек, растёт к деке), X поперёк (0 центр,
гриф ±26), Z вверх (0 = низ секции).

ЭТАЖНАЯ СТОПКА (каждая плита-«лоток» печатается плашмя, сборка стопкой):
  P0  дно 0..3, стенки-борта до 6.8; стад оси плеча-0 прямо на дне
  P1..P3 межэтажки: тело 1.6 + стенки 3.8 вверх; каждая несёт стад своей оси
  P4  палуба: тело 3 + борта каналов тележек 4
Полость этажа 3.8 = плечо 1.6 + 0.2 + кольцо спицы 1.6 + 0.4 (потолок прижимает
всё сверху — вертикальные замки не нужны, урок стенда).

МЕХАНИЗМ (по каналу): плечо-треугольник B=52 (вдоль Y) + A=16 (поперёк, к
жёлобу спиц x=16), качается ±22.6° -> тип метёт X ±20 = ход тележки 40.
Штырь с типа идёт ВВЕРХ сквозь дуговые прорези верхних плит в вилку тележки.
Спицы-ленты 8×1.6 всех этажей бегут друг над другом в жёлобе x 6..14 (центр LANE_X=10).

Тележки на ладах 1-4 (Y: 18, 54, 87, 118), оси плеч на Y+52.
Стяжка стопки: М3 сквозь стенки (x=±25; y 12/120/228), в дне самонарез Ø2.6.
Запуск: .venv-b123d\\Scripts\\python gitara_sec1.py
"""
from build123d import *
import math as _m

OUT = r"C:\App\gitar\2-0\Print\Print"

W, L = 52, 160                 # гриф: ширина, длина секции (3 x 160 = 480)
CARTS_Y = [16, 42, 67, 91]    # центры тележек: шаг V позиции 26/25/24 (v0: 18/34/50/66 вплотную)
CART_HY = 9                    # полуширина тележки по Y (v0: 7)
RAIL_W = 3                     # бортик русла
RAIL_GAP = 1.5                 # тележка — бортик
LB, RS = 36.0, 18.0            # плечо: длинное к тележке, короткое к спице (v2: 52 / 10)
PHI = _m.degrees(_m.asin(22 / LB))       # мах на ход пальца ±22: 37.7°
PIN_DY = LB * (1 - _m.cos(_m.radians(PHI)))   # штырь уходит к оси: 7.5
RIB = RS * _m.sin(_m.radians(PHI))       # ход ленты ±11
SLOT_Y1 = PIN_DY + 2.5 + 0.7             # прорезь штыря: до yc + 10.7
AXES_Y = [y + LB for y in CARTS_Y]
LANE_X = 10                    # центр дорожки лент (диск кривошипа в деке)
FIT_D = 5.1                    # ПЛОТНАЯ посадка Ø5 стада/штыря: отверстия плеча, кольца спицы, паза тележки
                               # (было Ø6 = люфт 0.5 -> −5 мм хода; подобрать по купону gs1_kupon: 5.0/5.1/5.2/5.3)
def cols_for(k):
    """Колонны плиты k (живут в полости этажа k): вне сектора маха СВОЕГО
    плеча [ax-60, ax+6] и вне прорезей штырей нижних этажей."""
    bad = [(CARTS_Y[k] - 6, AXES_Y[k] + 6)]                      # мах длинного плеча (колонны на x −16)
    bad += [(CARTS_Y[j] - 8, CARTS_Y[j] + SLOT_Y1 + 5) for j in range(k)]
    out = []
    for y in range(5, 156, 10):
        if all(not (lo <= y <= hi) for lo, hi in bad):
            if not out or y - out[-1] >= 30:
                out.append(y)
    return out
TIE = [(23.5, 6), (-23.5, 6), (-23.5, 120), (23.5, 150), (-23.5, 150)]   # v3: (23.5, 120) убран — там голова спицы 3

FLOOR = 1.6                    # плита межэтажки
CAV = 3.8                      # полость этажа
STEP = FLOOR + CAV             # шаг этажа 5.4
Z_FLOOR = [3, 8.4, 13.8, 19.2]         # верх пола каждого этажа
Z_DECK = 23                    # низ палубы
DECK_T = 3
RAIL_H = 4                     # борта каналов тележек
CART_H = 6


def BB(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(
        abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))


def slot_cut(yc, z0, z1):
    """Прорезь под штырь плеча: X ±24.5, Y yc-3.5..yc+10.7 (v3: штырь на махе уходит к оси на 7.5)."""
    return BB(-24.5, 24.5, yc - 3.5, yc + SLOT_Y1, z0, z1)


def walls(z0, z1, south_open=True):
    """Стенки лотка по периметру; юг открыт под выход лент жёлоба."""
    w = BB(-26, -24, 0, L, z0, z1) + BB(24, 26, 0, L, z0, z1)
    w += BB(-24, 24, 0, 2, z0, z1)
    if south_open:
        w += BB(-24, 4, L - 2, L, z0, z1) + BB(16, 24, L - 2, L, z0, z1)   # проход x 4..16 под жёлоб 6..14 (был 10..22 от старого жёлоба 11..21 — спица упиралась в стенку, найдено рендером 11.09)
    else:
        w += BB(-24, 24, L - 2, L, z0, z1)
    return w


def columns(z0, z1, ys):
    c = Part()
    for y in ys:
        c += Pos(-16, y, (z0 + z1) / 2) * Cylinder(4, z1 - z0)
    return c


def tie_boss(part, z0, z1):
    """Приливы-бобышки на стенках у точек стяжки (Ø3.2 в стенку 2 не влезает)."""
    for x, y in TIE:
        s = 1 if x > 0 else -1
        part += BB(s * 21, s * 26, y - 4, y + 4, z0, z1)
    return part


def tie_holes(part, z0, z1, r=1.6):
    for x, y in TIE:
        part -= Pos(x, y, (z0 + z1) / 2) * Cylinder(r, (z1 - z0) + 0.2)
    return part


def axis_stud(y_ax, z0):
    """Стад оси плеча Ø5: от пола почти до потолка (замок от слезания)."""
    return Pos(0, y_ax, z0 + 1.8) * Cylinder(2.5, 3.6)


# ---------------- P0: дно ----------------
p0 = BB(-26, 26, 0, L, 0, 3)
p0 += walls(3, 6.8)
p0 += columns(3, 6.8, cols_for(0))
p0 += axis_stud(AXES_Y[0], 3)
p0 = tie_boss(p0, 3, 6.8)
p0 = tie_holes(p0, 0, 6.8, r=1.3)
p0 += BB(-26, 26, 160, 178, 0, 1.5)
for hx in (-21, -9, 5, 21):
    p0 -= Pos(hx, 169, 0.75) * Cylinder(1.6, 1.7)     # сквозь полку (бутерброд)      # в дне Ø2.6 — М3 сам нарежет

# ---------------- P1..P3: межэтажки ----------------
mids = []
for k in (1, 2, 3):
    m = BB(-26, 26, 0, L, 0, FLOOR)
    for j in range(k):                          # прорези штырей нижних плеч
        m -= slot_cut(CARTS_Y[j], -0.1, FLOOR + 0.1)
    m += walls(FLOOR, FLOOR + CAV)
    m += columns(FLOOR, FLOOR + CAV, cols_for(k))
    m += axis_stud(AXES_Y[k], FLOOR)
    m = tie_boss(m, FLOOR, FLOOR + CAV)
    m = tie_holes(m, 0, FLOOR + CAV)
    mids.append(m)

# ---------------- P4: палуба с бортами каналов ----------------
deck = BB(-26, 26, 0, L, 0, DECK_T)
for yc in CARTS_Y:
    deck -= slot_cut(yc, -0.1, DECK_T + 0.1)
# у каждой тележки своё русло: бортики снаружи и между тележками
RAIL_Y = [CARTS_Y[0] - CART_HY - RAIL_GAP - RAIL_W / 2]
RAIL_Y += [(CARTS_Y[j] + CARTS_Y[j + 1]) / 2 for j in range(3)]
RAIL_Y += [CARTS_Y[3] + CART_HY + RAIL_GAP + RAIL_W / 2]
for ry in RAIL_Y:
    deck += BB(-26, 26, ry - RAIL_W / 2, ry + RAIL_W / 2, DECK_T, DECK_T + RAIL_H)
CH_END = RAIL_Y[-1] + RAIL_W / 2
deck = tie_boss(deck, 0, DECK_T)
deck = tie_holes(deck, 0, DECK_T + RAIL_H)
# ладовые валики (мензура 650) на свободном юге палубы — имитация грифа
import math as _m
for n in range(1, 9):
    Ln = 650.0 * (1 - 2 ** (-n / 12))
    if CH_END + 3 <= Ln <= 155:
        deck += Pos(0, Ln, DECK_T) * Rot(0, 90, 0) * Cylinder(1.2, 48)
# линии струн (владелец 26.09, для вида): как на фретбордах секций 2-3 — 6 полуцилиндров R0.6
# с шагом 8.8, только на свободной части палубы южнее тележек (в руслах тележки о них спотыкались бы);
# у винтов стяжки прерываются под головку
STRING_X = (-22.0, -13.2, -4.4, 4.4, 13.2, 22.0)
ys0, ys1 = CH_END + 1.5, L - 1
for sx in STRING_X:
    ridge = Pos(sx, (ys0 + ys1) / 2, DECK_T) * Rot(90, 0, 0) * Cylinder(0.6, ys1 - ys0)
    ridge -= BB(sx - 1, sx + 1, ys0 - 1, ys1 + 1, DECK_T - 0.7, DECK_T)     # только верхняя половина
    for tx, ty in TIE:
        if abs(tx - sx) < 3.6:
            ridge -= Pos(tx, ty, DECK_T) * Cylinder(3.6, 3)
    deck += ridge

# ---------------- плечи (4 шт, разная высота штыря): 36 : 18 ----------------
PIN_TOP = Z_DECK + DECK_T + 1.8          # штырь не выше дна ложа v3 (дно 26..28): в дырке дна и между полозьями
arms = []
for k in range(4):
    a = Pos(0, 0, 0.8) * Cylinder(5, 1.6)                # диск оси
    a += BB(-2.5, 2.5, -LB, 0, 0, 1.6)                   # длинное к тележке
    a += Pos(0, -LB, 0.8) * Cylinder(3.5, 1.6)           # пад штыря
    a += BB(0, RS, -2.5, 2.5, 0, 1.6)                    # короткое к спице
    a += Pos(RS, 0, 0.8) * Cylinder(4, 1.6)              # пад стада
    a -= Pos(0, 0, 0.8) * Cylinder(FIT_D / 2, 1.8)       # дырка оси: плотно на стад Ø5 (FIT_D)
    a += Pos(RS, 0, 2.5) * Cylinder(2.5, 1.8)            # стад спицы
    pin_h = PIN_TOP - (Z_FLOOR[k] + 0.2 + 1.6)
    a += Pos(0, -LB, 1.6 + pin_h / 2) * Cylinder(2.5, pin_h)   # штырь в ложе
    arms.append(a)

# ---------------- спицы v3: голова с прорезью вдоль X, колено к жёлобу ---------------
# система спицы: (0, 0) — ось плеча при ленте в середине; спица только едет по Y
SX0 = RS * _m.cos(_m.radians(PHI)) - FIT_D / 2 - 0.2      # прорезь: стад ходит по X 14.2 .. 18
SX1 = RS + FIT_D / 2 + 0.2
HEAD_HY = FIT_D / 2 + 2.2
JX0, JX1 = LANE_X - 4, LANE_X + 4                         # жёлоб x 6..14
spicas = []
for k in range(4):
    end = 178 - AXES_Y[k]                                 # конец на мир 178, как в v2
    s = BB(SX0 - 2.2, SX1 + 2.2, -HEAD_HY, HEAD_HY, 1.8, 3.4)   # голова над плечом
    s += BB(JX0, JX1, 3, 15, 1.8, 3.4)                    # колено к жёлобу (мимо прорези: y ≥ 3)
    s += BB(JX0, JX1, 11, 15, 0, 3.4)                     # соединитель вниз (дальше от диска оси)
    s += BB(JX0, JX1, 11, end, 0, 1.6)                    # тело ленты на полу
    s -= BB(SX0, SX1, -(FIT_D + 0.02) / 2, (FIT_D + 0.02) / 2, 1.7, 3.5)   # прорезь: по Y плотно, по X гуляет
    # стык-защёлка на переходе секций (160..178), как в v2
    s -= BB(JX0 - 0.1, JX1 + 0.1, end - 18, end + 0.1, 0.8, 1.7)
    s += Pos(LANE_X, end - 11.5, 2.0) * Cylinder(1.5, 2.4)
    s -= Pos(LANE_X, end - 6.5, 0.4) * Cylinder(1.75, 1.0)
    spicas.append(s)

# ---------------- ложе v3 (плоское, как gitara_lozhe.py build_flat v2) ----------------
# штырь ходит к оси на 7.5: дырка в дне и полозья длиннее (v2: дырка −2.8..6.8, полозья −3..7)
LZ_HX, LZ_Y0, LZ_Y1, LZ_T, RUN = 12.0, -10.2, 10.2, 2.0, 2.9
RIM_T, RIM_H, LIP_T, LIP_H = 1.6, 5.0, 0.8, 1.5
PIN_CH = 5.3
lz = BB(-LZ_HX, LZ_HX, LZ_Y0, LZ_Y1, 0, LZ_T)
lz -= BB(-PIN_CH / 2, PIN_CH / 2, -2.8, LZ_Y1 + 0.1, -0.1, LZ_T + 0.1)     # дырка под штырь (открыта к деке, сверху её перекрывает бортик)
lz += BB(-LZ_HX, -LZ_HX + RIM_T, LZ_Y0, LZ_Y1, LZ_T, LZ_T + RIM_H)
lz += BB(LZ_HX - RIM_T, LZ_HX, LZ_Y0, LZ_Y1, LZ_T, LZ_T + RIM_H)
lz += BB(-LZ_HX + RIM_T, LZ_HX - RIM_T, LZ_Y0, LZ_Y0 + LIP_T, LZ_T, LZ_T + LIP_H)
lz += BB(-LZ_HX + RIM_T, LZ_HX - RIM_T, LZ_Y1 - LIP_T, LZ_Y1, LZ_T, LZ_T + LIP_H)
for sx in (1, -1):
    lz += BB(sx * PIN_CH / 2, sx * 4.4, -3.0, LZ_Y1, -RUN, 0)             # полозья в прорезь палубы
lozhe = Pos(0, 0, RUN) * lz                                                # низ полозьев — z 0

parts = [("gs1_p0_base", p0), ("gs1_p4_deck", deck), ("gs1_lozhe", lozhe)]
parts += [(f"gs1_p{k}_mid", mids[k - 1]) for k in (1, 2, 3)]
parts += [(f"gs1_arm{k}", arms[k]) for k in range(4)]
parts += [(f"gs1_spica{k}", spicas[k]) for k in range(4)]
for name, part in parts:
    p = part if isinstance(part, Part) else Part() + part
    export_stl(p, rf"{OUT}\{name}_v3.stl")
    print(f"{name}: volume={p.volume:.0f} mm3, solids={len(p.solids())}")
print("export done")

# ================= ЧИСЛЕННАЯ ПРОВЕРКА СБОРКИ =================
# мах проверяем на ход ложа ±20 (как v2: на ±22 полозья ложа упираются в концы прорези ±24.5)
from clearance import Assembly

SRC = OUT
PHI_CHK = _m.degrees(_m.asin(20 / LB))
asm = Assembly()
asm.add("p0", SRC + r"\gs1_p0_base_v3.stl")
for k in (1, 2, 3):
    asm.add(f"p{k}", SRC + rf"\gs1_p{k}_mid_v3.stl", loc=(0, 0, Z_FLOOR[k] - FLOOR))
asm.add("deck", SRC + r"\gs1_p4_deck_v3.stl", loc=(0, 0, Z_DECK))
pairs_touch = [("p0", "p1"), ("p1", "p2"), ("p2", "p3"), ("p3", "deck")]
pairs_clear = []
for k in range(4):
    own = f"p{k}" if k else "p0"
    up = f"p{k + 1}" if k < 3 else "deck"
    for phi in (-PHI_CHK, -PHI_CHK / 2, 0, PHI_CHK / 2, PHI_CHK):
        t = _m.radians(phi)
        tag = "%d_%+.0f" % (k, phi)
        an, sn, ln_ = "arm" + tag, "sp" + tag, "lz" + tag
        asm.add(an, SRC + rf"\gs1_arm{k}_v3.stl", loc=(0, AXES_Y[k], Z_FLOOR[k] + 0.2), rz=phi)
        asm.add(sn, SRC + rf"\gs1_spica{k}_v3.stl", loc=(0, AXES_Y[k] + RS * _m.sin(t), Z_FLOOR[k] + 0.2))
        asm.add(ln_, SRC + r"\gs1_lozhe_v3.stl", loc=(LB * _m.sin(t), CARTS_Y[k], Z_DECK + DECK_T - RUN))
        pairs_clear += [(an, up, 0.15), (an, own, 0.01), (sn, own, 0.1), (sn, up, 0.15), (an, ln_, 0.0)]
        pairs_clear += [(an, f"p{u}", 0.15) for u in range(k + 2, 4)] + ([(an, "deck", 0.15)] if k < 3 else [])   # штырь сквозь все плиты выше
        pairs_touch += [(an, sn), (ln_, "deck")]
        for j in range(k):                                  # чужие штыри нижних этажей проходят сквозь этот этаж
            pairs_clear += [(an, "arm%d_%+.0f" % (j, phi), 0.3), (sn, "arm%d_%+.0f" % (j, phi), 0.3)]
        if k:                                               # соседние ложа в разные стороны
            pairs_clear += [(ln_, "lz%d_%+.0f" % (k - 1, -phi), 0.5)]
asm.check(clearances=pairs_clear, touching=pairs_touch, verbose=False)
print("рычаг ×%.2f: мах ±%.1f° (±%.1f° на ложе ±20), лента ±%.2f, штырь к оси %.1f" % (LB / RS, PHI, PHI_CHK, RIB, PIN_DY))
