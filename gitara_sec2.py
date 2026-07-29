# -*- coding: utf-8 -*-
"""ГИТАРА: СЕКЦИЯ-2 (средняя часть грифа) — МОНОБЛОК, одна деталь.
Дно 3 мм + башня-жёлоб (x 8..24) с 4 горизонтальными щелями-этажами под
спицы-ленты 8×1.6 (щели 8.8×2.0, уровни = этажам секции-1, мосты 8.8 мм —
печать плашмя без поддержек). Остальная ширина дна свободна: резерв под
боковые рычажки и LED-канал (по карте продукта).
Стыки: север — ВЕРХНЯЯ полка нахлёста (к южной нижней полке секции-1),
юг — нижняя полка (к секции-3/деке). 4×М3 на каждом стыке.
Запуск: .venv-b123d\\Scripts\\python gitara_sec2.py
"""
from build123d import *

OUT = r"C:\App\gitar\2-0\Print\Print"
L = 240
Z_FLOOR = [3, 8.4, 13.8, 19.2]         # уровни этажей (как в секции-1)


def BB(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(
        abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))

sec = BB(-26, 26, 0, L, 0, 3)                       # дно
sec += BB(8, 24, 0, L, 3, 22)                       # башня жёлоба
for zf in Z_FLOOR:
    sec -= BB(11.5, 20.5, -0.1, L + 0.1, zf - 0.1, zf + 2.1)   # щели-этажи
# стык СЕВЕР: верхняя полка (ложится на нижнюю полку секции-1)
sec -= BB(-26.1, 26.1, -0.1, 18, -0.1, 1.5)
for hx in (-20, -7, 7, 20):
    sec -= Pos(hx, 9, 2.25) * Cylinder(1.6, 1.7)
# стык ЮГ: нижняя полка
sec += BB(-26, 26, L, L + 18, 0, 1.5)
for hx in (-20, -7, 7, 20):
    sec -= Pos(hx, L + 9, 0.75) * Cylinder(1.6, 1.7)
# рёбра жёсткости дна по свободной стороне
for yr in (60, 120, 180):
    sec += BB(-24, 6, yr - 2, yr + 2, 3, 8)

p = Part() + sec
export_stl(p, rf"{OUT}\gs2_mono.stl")
print(f"gs2_mono: volume={p.volume:.0f} mm3, solids={len(p.solids())}")

# лента-заглушка для проверки прохода щелей
band = BB(-4, 4, -10, L + 10, 0, 1.6)
pb = Part() + band
export_stl(pb, rf"{OUT}\gs2_band_test.stl")
print("export done")

# -------- численная проверка: лента в каждой щели + стык с секцией-1 -------
from clearance import Assembly

asm = Assembly()
asm.add("mono", rf"{OUT}\gs2_mono.stl")
asm.add("sec1_base", rf"{OUT}\gs1_p0_base.stl", loc=(0, -240, 0))  # секция-1 севернее
clear = []
for k, zf in enumerate(Z_FLOOR):
    asm.add(f"band{k}", rf"{OUT}\gs2_band_test.stl", loc=(16, 0, zf + 0.2))
    clear.append((f"band{k}", "mono", 0.15))
asm.check(clearances=clear, touching=[("mono", "sec1_base")], verbose=True)
