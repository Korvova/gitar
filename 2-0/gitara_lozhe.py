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


def gusset(sign):
    """Скос 45° от стенки тележки (x = ±6, низ) до края пластины (x = ±12, верх тележки)."""
    tri = Polygon((6 * sign, 0), (6 * sign, CART_H), (12 * sign, CART_H), align=None)
    g = extrude(Plane.XZ * tri, amount=CART_HY, both=True)
    return g


cart = BB(-6, 6, -CART_HY, CART_HY, 0, CART_H)
cart += gusset(1)
cart += gusset(-1)
if VER == "v2":
    cart -= BB(-(FIT_D + 0.1) / 2, (FIT_D + 0.1) / 2, -2.9, 6.9, -0.1, CART_H + 0.1)   # паз, как у gs1_cart_v2
else:
    # v0, по замерам владельца 26.09: прорезь палубы напечаталась 10.5 (в модели 11), штырь 4.9.
    # Тележка стоит на палубе, снизу два полоза уходят в прорезь палубы и держат тележку по Y
    # (ширина 10.0). Штырь — в сквозном по Y канале 5.3: по X ведёт тележку, по Y гуляет свободно
    # (в крайних положениях плеча штырь уходит на юг на 4 мм). Полозья — вплотную к штырю, чтобы
    # на ходу ±20 не упереться в концы прорези (±24.5).
    SLOT_Y, PIN_CH, RUN_H = 10.0, 5.3, 2.5
    cart -= BB(-PIN_CH / 2, PIN_CH / 2, -CART_HY - 0.1, CART_HY + 0.1, -0.1, 4.5)       # канал штыря, мост над ним
    for sx in (1, -1):
        cart += BB(sx * PIN_CH / 2, sx * 4.4, 2 - SLOT_Y / 2, 2 + SLOT_Y / 2, -RUN_H, 0)  # полоз в прорезь (она y -3.5..+7.5 от центра тележки)
z0 = CART_H
hx, hy = LOZHE_X / 2, LOZHE_Y / 2
cart += BB(-hx, hx, -hy, hy, z0, z0 + PLATE_T)
z1 = z0 + PLATE_T
cart += BB(-hx, -hx + RIM_T, -hy, hy, z1, z1 + RIM_H)
cart += BB(hx - RIM_T, hx, -hy, hy, z1, z1 + RIM_H)
cart += BB(-hx + RIM_T, hx - RIM_T, -hy, -hy + LIP_T, z1, z1 + LIP_H)
cart += BB(-hx + RIM_T, hx - RIM_T, hy - LIP_T, hy, z1, z1 + LIP_H)

part = Part() + cart
bb = part.bounding_box()
print("gs1_cart_lozhe" + SUF + ": %.1f x %.1f x %.1f, volume %.0f mm3, solids %d" %
      (bb.size.X, bb.size.Y, bb.size.Z, part.volume, len(part.solids())))
assert abs(bb.min.Y + hy) < 0.01 and abs(bb.max.Y - hy) < 0.01, "скосы вылезли по Y"
if VER != "v2":
    part = Pos(0, 0, 2.5) * part          # низ полозьев — на стол
export_stl(part, os.path.join(OUT, "gs1_cart_lozhe" + SUF + ".stl"))

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
        asm.add(nm, os.path.join(OUT, "gs1_cart_lozhe" + SUF + ".stl"), loc=(xs[k], CARTS_Y[k], Z_DECK + DECK_T - (0 if VER == "v2" else 2.5)))
        pairs_touch.append((nm, "deck"))
        if k:
            pairs_clear.append(("c%s%d" % (case, k - 1), nm, 0.9))
asm.check(clearances=pairs_clear, touching=pairs_touch, verbose=False)
