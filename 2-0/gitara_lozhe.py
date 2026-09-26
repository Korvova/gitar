# -*- coding: utf-8 -*-
"""ГИТАРА: тележка с ложем для пальца, 4 шт одинаковые.

VER = "v2" (по умолчанию) — под секцию-1 v2: шаг тележек 26/25/24, тележка 12 x 18, закрытый паз,
ложе 24 x 22. VER = "v0" — под напечатанную секцию-1 v0 (шаг 16, ложе 24 x 15), стол 69.

v0: низ — та же тележка секции-1: 12 x 14 x 6, вилка Ø5.2 открыта на юг, садится на штырь
плеча так же, как старая (старую просто вынуть). Сверху — ложе для кончика пальца:
пластина 24 x 15 над бортами канала, бортики по концам хода (толкают палец в обе
стороны) и низкие бортики вдоль (палец не соскальзывает к соседу).
Ширина 15 при шаге тележек 16 — между соседними ложами 1 мм (исходная постановка).
Пластина шире тележки опирается на скосы 45° — печать без поддержек, низом на стол.

Запуск: .venv-b123d\\Scripts\\python gitara_lozhe.py
"""
import os
from build123d import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "Print", "Print")

import sys
VER = sys.argv[1] if len(sys.argv) > 1 else "v2"
FIT_D = 5.1
CART_H = 6
LOZHE_X, LOZHE_Y = (24.0, 22.0) if VER == "v2" else (24.0, 15.0)   # ложе: вдоль хода x ширина
CART_HY = 9 if VER == "v2" else 7
SUF = "_v2" if VER == "v2" else ""
PLATE_T = 1.6
RIM_T, RIM_H = 1.6, 5.0              # бортики по концам хода
LIP_T, LIP_H = 0.8, 1.5              # бортики вдоль


def BB(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))


def _unused_gusset(sign):
    """Скос 45° от стенки тележки (x = ±6, низ) до края пластины (x = ±12, верх тележки)."""
    tri = Polygon((6 * sign, 0), (6 * sign, CART_H), (12 * sign, CART_H), align=None)
    g = extrude(Plane.XZ * tri, amount=CART_HY, both=True)
    return g


def build(last=False):
    """Тележка с ложем. v2 — по центру штыря. v0 — по центру прорези палубы (она y -3.5..+7.5
    от штыря), чтобы опираться на палубу с обеих сторон; last — крайняя южная (тележка 3):
    за ней бортик канала, низ укорочен до 7.0, а верх ступенькой ложится на бортик (z 4)."""
    if VER == "v2":
        yc, y0, y1, y1lo = 0.0, -CART_HY, CART_HY, CART_HY
    else:
        yc = 2.0
        y0, y1 = yc - LOZHE_Y / 2, yc + LOZHE_Y / 2          # -5.5 .. 9.5
        y1lo = 7.0 if last else y1
    c = BB(-6, 6, y0, y1lo, 0, CART_H)
    if y1lo < y1:
        c += BB(-6, 6, y1lo, y1, 4.0, CART_H)             # ступенька на бортик канала
    for sgn in (1, -1):
        tri = Polygon((6 * sgn, 0), (6 * sgn, CART_H), (12 * sgn, CART_H), align=None)
        g = extrude(Plane.XZ * tri, amount=(y1lo - y0) / 2, both=True)
        c += Pos(0, (y0 + y1lo) / 2, 0) * g
    if VER == "v2":
        c -= BB(-(FIT_D + 0.1) / 2, (FIT_D + 0.1) / 2, -2.9, 6.9, -0.1, CART_H + 0.1)   # паз, как у gs1_cart_v2
    else:
        # замеры владельца 26.09: прорезь 10.5 (в модели 11), штырь 4.9. Полозья в прорезь держат
        # тележку по Y; штырь — в сквозном по Y канале 5.3 (ведёт по X, по Y гуляет на 4 мм);
        # полозья вплотную к штырю — на ходу ±20 не упираются в концы прорези (±24.5)
        SLOT_Y, PIN_CH, RUN_H = 10.0, 5.3, 2.9
        c -= BB(-PIN_CH / 2, PIN_CH / 2, y0 - 0.1, y1 + 0.1, -0.1, 4.5)   # канал штыря, мост над ним
        for sx in (1, -1):
            c += BB(sx * PIN_CH / 2, sx * 4.4, yc - SLOT_Y / 2, yc + SLOT_Y / 2, -RUN_H, 0)
    hx = LOZHE_X / 2
    z0, z1 = CART_H, CART_H + PLATE_T
    c += BB(-hx, hx, y0 if VER != "v2" else -LOZHE_Y / 2, y1 if VER != "v2" else LOZHE_Y / 2, z0, z1)
    ya, yb = (y0, y1) if VER != "v2" else (-LOZHE_Y / 2, LOZHE_Y / 2)
    c += BB(-hx, -hx + RIM_T, ya, yb, z1, z1 + RIM_H)
    c += BB(hx - RIM_T, hx, ya, yb, z1, z1 + RIM_H)
    c += BB(-hx + RIM_T, hx - RIM_T, ya, ya + LIP_T, z1, z1 + LIP_H)
    c += BB(-hx + RIM_T, hx - RIM_T, yb - LIP_T, yb, z1, z1 + LIP_H)
    part = Part() + c
    bb = part.bounding_box()
    print("ложе %s%s: %.1f x %.1f x %.1f, volume %.0f mm3, solids %d" %
          (VER, " крайнее" if last else "", bb.size.X, bb.size.Y, bb.size.Z, part.volume, len(part.solids())))
    return part


def build_flat(last=False):
    """v0 «плоское» (идея владельца 26.09): без тележки и скосов — ложе лежит прямо на палубе,
    снизу два полоза в прорезь, в дне продолговатая дырка под штырь (штырь гуляет по Y на 4 мм,
    торчит над дном ложа ~2 мм — для пробы допустимо). Печать вверх ногами: бортиками на стол,
    дно ложа мостом между бортиками, полозья сверху."""
    yc, PIN_CH, SLOT_Y, T = 2.0, 5.3, 10.0, 2.0
    y0, y1 = yc - LOZHE_Y / 2, yc + LOZHE_Y / 2
    if VER == "v2":                         # v2: ложе в своём русле между бортиками (самое узкое ±10.5)
        y0, y1 = -10.2, 10.2
    if last:
        y1 = 7.0                                  # тележка 3: южнее — бортик канала (y +7.35)
    hx = LOZHE_X / 2
    c = BB(-hx, hx, y0, y1, 0, T)
    c -= BB(-PIN_CH / 2, PIN_CH / 2, -2.8, 6.8, -0.1, T + 0.1)           # дырка под штырь
    c += BB(-hx, -hx + RIM_T, y0, y1, T, T + RIM_H)
    c += BB(hx - RIM_T, hx, y0, y1, T, T + RIM_H)
    c += BB(-hx + RIM_T, hx - RIM_T, y0, y0 + LIP_T, T, T + LIP_H)
    c += BB(-hx + RIM_T, hx - RIM_T, y1 - LIP_T, y1, T, T + LIP_H)
    for sx in (1, -1):
        c += BB(sx * PIN_CH / 2, sx * 4.4, yc - SLOT_Y / 2, yc + SLOT_Y / 2, -RUN, 0)
    part = Part() + c
    print("ложе " + VER + " плоское%s: volume" % (" крайнее" if last else "") + " %.0f mm3, solids %d" % (part.volume, len(part.solids())))
    return part


RUN = 2.9
names = []
if VER == "v2":
    export_stl(Pos(0, 0, RUN) * build_flat(), os.path.join(OUT, "gs1_cart_lozhe_v2_plosk.stl"))
if VER != "v2":
    export_stl(Pos(0, 0, RUN) * build_flat(), os.path.join(OUT, "gs1_cart_lozhe_plosk.stl"))
    export_stl(Pos(0, 0, RUN) * build_flat(True), os.path.join(OUT, "gs1_cart_lozhe_plosk_kraj.stl"))
for last in ((False,) if VER == "v2" else (False, True)):
    part = build(last)
    nm = "gs1_cart_lozhe" + SUF + ("_kraj" if last else "")
    if VER != "v2":
        part = Pos(0, 0, RUN) * part          # низ полозьев — на стол
    export_stl(part, os.path.join(OUT, nm + ".stl"))
    names.append(nm)

# ================= ПРОВЕРКА: 4 ложа на палубе секции-1, крайние положения =================
from clearance import Assembly

CARTS_Y = [16, 42, 67, 91] if VER == "v2" else [18, 34, 50, 66]
Z_DECK, DECK_T = 23, 3
pairs_clear, pairs_touch = [], []
asm = Assembly()
asm.add("deck", os.path.join(OUT, "gs1_p4_deck" + SUF + ".stl"), loc=(0, 0, Z_DECK))
for case, xs in (("A", (20, -20, 20, -20)), ("B", (-20, 20, -20, 20)), ("C", (0, 0, 0, 0))):
    for k in range(4):
        nm = "c%s%d" % (case, k)
        stl = names[1] if (VER != "v2" and k == 3) else names[0]
        asm.add(nm, os.path.join(OUT, stl + ".stl"), loc=(xs[k], CARTS_Y[k], Z_DECK + DECK_T - (0 if VER == "v2" else RUN)))
        pairs_touch.append((nm, "deck"))
        if k:
            pairs_clear.append(("c%s%d" % (case, k - 1), nm, 0.9))
if VER == "v2":                          # плоское ложе v2 в своих руслах, крайние положения
    for k in range(4):
        for x in (-20, 0, 20):
            nm = "g%d_%d" % (k, x)
            asm.add(nm, os.path.join(OUT, "gs1_cart_lozhe_v2_plosk.stl"), loc=(x, CARTS_Y[k], Z_DECK + DECK_T - RUN))
            pairs_touch.append((nm, "deck"))
if VER != "v2":                          # плоское ложе на тележках 0-2 в крайних положениях
    for k in range(4):
        for x in (-20, 0, 20):
            nm = "f%d_%d" % (k, x)
            stl = "gs1_cart_lozhe_plosk_kraj.stl" if k == 3 else "gs1_cart_lozhe_plosk.stl"
            asm.add(nm, os.path.join(OUT, stl), loc=(x, CARTS_Y[k], Z_DECK + DECK_T - RUN))
            pairs_touch.append((nm, "deck"))
asm.check(clearances=pairs_clear, touching=pairs_touch, verbose=False)
