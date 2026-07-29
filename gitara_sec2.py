# -*- coding: utf-8 -*-
"""ГИТАРА: СЕКЦИЯ-2 (средняя часть грифа) — РАЗБОРНАЯ (v2, идея юзера).
Вместо литого моноблока — слои:
  дно (карман под стопку + стенки-направляющие + стыки-нахлёсты)
  4 ОДИНАКОВЫЕ П-рейки: подошва 1.6 + бортики 3.8; лента лежит в рейке,
    подошва следующей рейки = потолок предыдущего этажа (шаг 5.4 = секции-1)
  крышка с язычком (потолок верхней ленты), 4 винта М3 в торцы стенок дна
Разборка: 4 винта -> стопка снимается, любая лента достаётся.
Все детали плоские, печать без поддержек и мостов.
Запуск: .venv-b123d\\Scripts\\python gitara_sec2.py
"""
from build123d import *

OUT = r"C:\App\gitar\2-0\Print\Print"
L = 240
Z_FLOOR = [3, 8.4, 13.8, 19.2]         # уровни лент = этажам секции-1
JX = (-21, -9, 5, 21)                  # болты стыков секций (доступ для гаек)


def BB(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(
        abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))

# ---------------- дно ----------------
base = BB(-26, 26, 0, L, 0, 3)
base += BB(7, 10, 0, L, 3, 23)                      # стенки-направляющие стопки
base += BB(22, 25, 0, L, 3, 23)
base -= BB(9.8, 22.2, -0.1, L + 0.1, 1.4, 23.1)     # карман стопки + прорезь
# стык СЕВЕР: верхняя полка (ложится на нижнюю полку секции-1)
base -= BB(-26.1, 26.1, -0.1, 18, -0.1, 1.5)
for hx in JX:
    base -= Pos(hx, 9, 2.25) * Cylinder(1.6, 1.7)
# стык ЮГ: нижняя полка
base += BB(-26, 26, L, L + 18, 0, 1.5)
for hx in JX:
    base -= Pos(hx, L + 9, 0.75) * Cylinder(1.6, 1.7)
# рёбра жёсткости свободной (западной) зоны
for yr in (60, 120, 180):
    base += BB(-24, 5, yr - 2, yr + 2, 3, 8)
# отверстия М3 в торцах стенок под винты крышки (самонарез, Ø2.6)
for wx in (8.5, 23.5):
    for wy in (12, 228):
        base -= Pos(wx, wy, 17) * Cylinder(1.3, 12.2)

# ---------------- П-рейка (4 шт одинаковые) ----------------
tray = BB(10.2, 21.8, 0, L, 0, 1.6)                 # подошва (лента едет по ней)
tray += BB(10.2, 11.4, 0, L, 1.6, 5.4)              # бортики = распорки стопки
tray += BB(20.6, 21.8, 0, L, 1.6, 5.4)

# ---------------- крышка ----------------
lid = BB(7, 25, 0, L, 0, 1.6)
lid += BB(11.5, 20.5, -0.0, L, -2.0, 0)             # язычок-потолок верхней ленты
for wx in (8.5, 23.5):
    for wy in (12, 228):
        lid -= Pos(wx, wy, 0.8) * Cylinder(1.6, 1.8)

parts = [("gs2_base", base), ("gs2_tray", tray), ("gs2_lid", lid)]
for name, part in parts:
    p = part if isinstance(part, Part) else Part() + part
    export_stl(p, rf"{OUT}\{name}.stl")
    print(f"{name}: volume={p.volume:.0f} mm3, solids={len(p.solids())}")

band = BB(-4, 4, -10, L + 10, 0, 1.6)
export_stl(Part() + band, rf"{OUT}\gs2_band_test.stl")
print("export done")

# -------- численная проверка: стопка, ленты в рейках, крышка --------
from clearance import Assembly

asm = Assembly()
asm.add("base", rf"{OUT}\gs2_base.stl")
clear = []
touch = []
for k, zf in enumerate(Z_FLOOR):
    asm.add(f"tray{k}", rf"{OUT}\gs2_tray.stl", loc=(0, 0, zf - 1.6))
    asm.add(f"band{k}", rf"{OUT}\gs2_band_test.stl", loc=(16, 0, zf + 0.05))
    clear.append((f"band{k}", f"tray{k}", 0.0))
    touch.append((f"tray{k}", "base"))
    if k:
        touch.append((f"tray{k}", f"tray{k - 1}"))
        clear.append((f"band{k - 1}", f"tray{k}", 0.15))
asm.add("lid", rf"{OUT}\gs2_lid.stl", loc=(0, 0, 23))
touch += [("lid", "base"), ("lid", "tray3")]
clear += [("band3", "lid", 0.15)]
asm.check(clearances=clear, touching=touch, verbose=True)
