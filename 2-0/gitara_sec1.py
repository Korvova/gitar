# -*- coding: utf-8 -*-
"""ГИТАРА: СЕКЦИЯ-1 (верх грифа, зона четырёх тележек) — v0.

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
CARTS_Y = [18, 34, 50, 66]    # центры тележек (лады 1-4)
AXES_Y = [y + 52 for y in CARTS_Y]
LANE_X = 10                    # центр дорожки лент (диск кривошипа в деке)
FIT_D = 5.2                    # ПЛОТНАЯ посадка Ø5 стада/штыря: отверстия плеча, кольца спицы, паза тележки
                               # (было Ø6 = люфт 0.5 -> −5 мм хода; подобрать по купону gs1_kupon: 5.0/5.1/5.2/5.3)
def cols_for(k):
    """Колонны плиты k (живут в полости этажа k): вне сектора маха СВОЕГО
    плеча [ax-60, ax+6] и вне прорезей штырей нижних этажей."""
    bad = [(AXES_Y[k] - 60, AXES_Y[k] + 6)]
    bad += [(CARTS_Y[j] - 5, CARTS_Y[j] + 9) for j in range(k)]
    out = []
    for y in range(5, 156, 10):
        if all(not (lo <= y <= hi) for lo, hi in bad):
            if not out or y - out[-1] >= 30:
                out.append(y)
    return out
TIE = [(23.5, 6), (-23.5, 6), (23.5, 80), (-23.5, 80), (23.5, 150), (-23.5, 150)]

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
    """Дуговая прорезь под штырь плеча: X ±24.5 (было 23.5: оси штыря Ø5 не хватало запаса на 40 мм хода — физика 09.09), Y yc-3.5..yc+7.5."""
    return BB(-24.5, 24.5, yc - 3.5, yc + 7.5, z0, z1)


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
# тележки-пальцы стоят вплотную (шаг 16): ОДИН общий канал, борта внешние
deck += BB(-26, 26, CARTS_Y[0] - 10.35, CARTS_Y[0] - 7.35, DECK_T, DECK_T + RAIL_H)
deck += BB(-26, 26, CARTS_Y[3] + 7.35, CARTS_Y[3] + 10.35, DECK_T, DECK_T + RAIL_H)
deck = tie_boss(deck, 0, DECK_T)
deck = tie_holes(deck, 0, DECK_T + RAIL_H)
# ладовые валики (мензура 650) на свободном юге палубы — имитация грифа
import math as _m
for n in range(1, 9):
    Ln = 650.0 * (1 - 2 ** (-n / 12))
    if 85 <= Ln <= 155:
        deck += Pos(0, Ln, DECK_T) * Rot(0, 90, 0) * Cylinder(1.2, 48)

# ---------------- плечи (4 шт, разная высота штыря) ----------------
arms = []
for k in range(4):
    a = Pos(0, 0, 0.8) * Cylinder(5, 1.6)                # диск оси
    a += BB(-2.5, 2.5, -52, 0, 0, 1.6)                   # длинное к тележке (юг->север)
    a += Pos(0, -52, 0.8) * Cylinder(3.5, 1.6)           # пад типа
    a += BB(0, LANE_X, -2.5, 2.5, 0, 1.6)                # короткое к жёлобу
    a += Pos(LANE_X, 0, 0.8) * Cylinder(4, 1.6)          # пад угла-1
    a -= Pos(0, 0, 0.8) * Cylinder(FIT_D / 2, 1.8)       # дырка оси: плотно на стад Ø5 (FIT_D)
    a += Pos(LANE_X, 0, 2.5) * Cylinder(2.5, 1.8)        # стад угла-1 (спица)
    pin_h = (Z_DECK + DECK_T + 4) - (Z_FLOOR[k] + 0.2 + 1.6)
    a += Pos(0, -52, 1.6 + pin_h / 2) * Cylinder(2.5, pin_h)   # штырь в вилку
    arms.append(a)

# ---------------- тележка (4 шт одинаковые) ----------------
cart = BB(-6, 6, -7, 7, 0, CART_H)
cart -= BB(-(FIT_D + 0.1) / 2, (FIT_D + 0.1) / 2, -7.1, 3, -0.1, CART_H + 0.1)   # вилка: паз под штырь Ø5 плотно (FIT_D+0.1), открыт на юг
carts = cart

# ---------------- спицы-ленты: головы с кольцом и ступенькой ---------------
spicas = []
for k in range(4):
    ln = 182 - AXES_Y[k]                   # конец на мир 178 (поза = ось-4)
    s = BB(-4, 4, 16, ln, 0, 1.6)                        # тело ленты на полу
    s += BB(-4, 4, 16, 20, 0, 3.4)                       # соединитель тело-ступень
    s += BB(-4, 4, 7, 20, 1.8, 3.4)                      # ступень (мимо стада: y>=7)
    s += Pos(0, 4, 2.6) * Cylinder(5.5, 1.6)             # голова-кольцо (приподнята)
    s -= Pos(0, 4, 2.6) * Cylinder(FIT_D / 2, 1.8)       # на стад угла-1: плотно (FIT_D)
    # стык-защёлка (идея юзера): нижний язык 0.8 со штырьком вверх + дыркой,
    # верхний язык соседки — с дыркой + штырьком вниз: взаимный замок без
    # крепежа. Штырёк вверх высокий (торчит 1.6 над лентой) — потолок щели
    # не даёт стыку разойтись. Стык живёт на переходе секций (160..178).
    s -= BB(-4.1, 4.1, ln - 18, ln + 0.1, 0.8, 1.7)
    s += Pos(0, ln - 11.5, 2.0) * Cylinder(1.5, 2.4)     # штырёк вверх Ø3
    s -= Pos(0, ln - 6.5, 0.4) * Cylinder(1.75, 1.0)     # дырка под штырёк соседки
    spicas.append(s)

# ---------------- купон посадок: Ø5 стад (плотно) и Ø6 под MR63 (запрессовка) --------
kupon = BB(0, 60, 0, 22, 0, 3)
for i, d in enumerate((5.0, 5.1, 5.2, 5.3)):                 # ряд под стад Ø5
    kupon -= Pos(7 + i * 12, 6, 1.5) * Cylinder(d / 2, 3.2)
for i, d in enumerate((5.8, 5.9, 6.0, 6.1)):                 # ряд под подшипник MR63 (нар. Ø6)
    kupon -= Pos(7 + i * 12, 16, 1.5) * Cylinder(d / 2, 3.2)
# щуп: стад Ø5 на шайбе-ручке Ø12 — отдельная деталь, как стад на плите (печатный в печатное)
kupon_stud = Pos(0, 0, 1) * Cylinder(6, 2) + Pos(0, 0, 2 + 1.8) * Cylinder(2.5, 3.6)
for i in range(4):                                            # риски-метки: 1..4 = порядок размеров
    for j in range(i + 1):
        kupon -= BB(3 + i * 12 + j * 2, 4 + i * 12 + j * 2, 20.5, 22.1, 2.4, 3.1)

parts = [("gs1_p0_base", p0), ("gs1_p4_deck", deck), ("gs1_cart", carts),
         ("gs1_kupon", kupon), ("gs1_kupon_stud", kupon_stud)]
parts += [(f"gs1_p{k}_mid", mids[k - 1]) for k in (1, 2, 3)]
parts += [(f"gs1_arm{k}", arms[k]) for k in range(4)]
parts += [(f"gs1_spica{k}", spicas[k]) for k in range(4)]
for name, part in parts:
    p = part if isinstance(part, Part) else Part() + part
    export_stl(p, rf"{OUT}\{name}.stl")
    print(f"{name}: volume={p.volume:.0f} mm3, solids={len(p.solids())}")
print("export done")

# ================= ЧИСЛЕННАЯ ПРОВЕРКА СБОРКИ =================
from clearance import Assembly

SRC = OUT
asm = Assembly()
asm.add("p0", SRC + r"\gs1_p0_base.stl")
for k in (1, 2, 3):
    asm.add(f"p{k}", SRC + rf"\gs1_p{k}_mid.stl", loc=(0, 0, Z_FLOOR[k] - FLOOR))
asm.add("deck", SRC + r"\gs1_p4_deck.stl", loc=(0, 0, Z_DECK))
pairs_touch = [("p0", "p1"), ("p1", "p2"), ("p2", "p3"), ("p3", "deck")]
pairs_clear = []
for k in range(4):
    for phi, tag in ((0, "n"), (22.6, "p"), (-22.6, "m")):
        nm = f"arm{k}{tag}"
        asm.add(nm, SRC + rf"\gs1_arm{k}.stl",
                loc=(0, AXES_Y[k], Z_FLOOR[k] + 0.2), rz=phi)
        up = f"p{k + 1}" if k < 3 else "deck"
        pairs_clear += [(nm, up, 0.15)]                  # плечо/штырь vs плита выше
        pairs_clear += [(nm, f"p{k}" if k else "p0", 0.05)]  # vs своя плита: стад в дырке сидит плотно (FIT_D), радиальный зазор 0.1
    pairs_clear += [(f"sp{k}", f"p{k}" if k else "p0", 0.1)]     # спица vs своя плита: стенки, колонны, южный проход
    asm.add(f"sp{k}", SRC + rf"\gs1_spica{k}.stl",
            loc=(LANE_X, AXES_Y[k] - 4, Z_FLOOR[k] + 0.2))
    up = f"p{k + 1}" if k < 3 else "deck"
    pairs_clear += [(f"sp{k}", up, 0.15)]
    asm.add(f"cart{k}", SRC + r"\gs1_cart.stl", loc=(0, CARTS_Y[k], Z_DECK + DECK_T))
    pairs_touch += [(f"cart{k}", "deck")]
asm.check(clearances=pairs_clear,
          touching=pairs_touch + [(f"arm{k}n", f"sp{k}") for k in range(4)],
          verbose=False)
