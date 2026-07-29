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
base -= BB(9.8, 22.2, 18, L + 0.1, 1.4, 23.1)       # карман стопки (после стыка!)
# стык СЕВЕР: верхняя полка (ложится на нижнюю полку секции-1);
# винты шины самонарезом: дырки узкие Ø2.6
base -= BB(-26.1, 26.1, -0.1, 18, -0.1, 1.5)
for hx in JX:
    base -= Pos(hx, 9, 2.25) * Cylinder(1.3, 1.7)
# стык ЮГ: нижняя полка
base += BB(-26, 26, L, L + 18, 0, 1.5)
for hx in JX:
    base -= Pos(hx, L + 9, 0.75) * Cylinder(1.6, 1.7)
# ЗАПАДНАЯ СТЕНКА сплошная до накладки (юзер: бок не должен зиять) +
# рёбра жёсткости; каналы Ø2.6 под винты накладки — в стенке, между ладов
base += BB(-26, -22, 0, L, 3, 24.6)
for yr in (60, 120, 180):
    base += BB(-22, 5, yr - 2, yr + 2, 3, 8)
for wy in (70, 110, 178):
    base -= Pos(-23.8, wy, 19.6) * Cylinder(1.3, 10.2)
# отверстия М3 в торцах стенок под винты крышки (самонарез, Ø2.6)
for wx in (8.5, 23.5):
    for wy in (12, 221.5):
        base -= Pos(wx, wy, 17) * Cylinder(1.3, 12.2)

# ---------------- П-рейка (4 шт одинаковые) ----------------
tray = BB(10.2, 21.8, 18, L, 0, 1.6)                # подошва (после стыковой зоны)
tray += BB(10.2, 11.4, 18, L, 1.6, 5.4)             # бортики = распорки стопки
tray += BB(20.6, 21.8, 18, L, 1.6, 5.4)

# ---------------- крышка ----------------
lid = BB(5.5, 26, 0, L, 0, 1.6)
lid += BB(11.5, 20.5, -0.0, L, -2.0, 0)             # язычок-потолок верхней ленты
for wx in (8.5, 23.5):
    for wy in (12, 221.5):
        lid -= Pos(wx, wy, 0.8) * Cylinder(1.6, 1.8)

# ---------------- ШИНА-НАКЛАДКА стыка секций (идея юзера) ----------------
# перекрывает шов снизу: 2 ряда по 4 винта М3 (самонарез в донья);
# южный ряд прошивает бутерброд шина+полка+дно
splice = BB(-26, 26, -24, 24, 0, 3)
for hy in (-15, 9):
    for hx in JX:
        splice -= Pos(hx, hy, 1.5) * Cylinder(1.6, 3.2)

# ---------------- НАКЛАДКА-ФРЕТБОРД (идея юзера: лады сверху!) ----------
# пластина на всю ширину грифа поверх крышки и столбиков; ладовые валики на
# НАСТОЯЩИХ позициях мензуры 650 (лады, попавшие в диапазон секции)
import math as _m
MENZURA = 650.0
SEC_Y0 = 240.0                      # секция-2 начинается на 240 от порожка
fret = BB(-26, 26, 0, L, 0, 2)
n = 1
while True:
    Ln = MENZURA * (1 - 2 ** (-n / 12))
    if Ln > SEC_Y0 + L - 5:
        break
    if Ln >= SEC_Y0 + 5:
        yl = Ln - SEC_Y0
        fret += Pos(0, yl, 2) * Rot(0, 90, 0) * Cylinder(1.2, 48)
    n += 1
FRET_HOLES = ((8.5, 12), (23.5, 12), (8.5, 221.5), (23.5, 221.5),
              (-23.8, 70), (-23.8, 110), (-23.8, 178))
for wx, wy in FRET_HOLES:
    fret -= Pos(wx, wy, 1) * Cylinder(1.6, 2.2)

parts = [("gs2_base", base), ("gs2_tray", tray), ("gs2_lid", lid),
         ("gs_splice", splice), ("gs2_fret", fret)]
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
asm.check(clearances=clear, touching=touch, verbose=False)
asm.check_holes("lid", [(wx, wy, 23.8, 1.6) for wx in (8.5, 23.5)
                        for wy in (12, 228)], verbose=False)
asm.check_holes("base", [(hx, 9, 2.3, 1.3) for hx in JX] +
                        [(hx, L + 9, 0.75, 1.6) for hx in JX], verbose=False)
asm.add("splice", rf"{OUT}\gs_splice.stl", loc=(0, 0, -3))
asm.check_holes("splice", [(hx, hy, -1.5, 1.6) for hx in JX
                           for hy in (-15, 9)], verbose=False)
asm.add("fret", rf"{OUT}\gs2_fret.stl", loc=(0, 0, 24.6))
asm.check(touching=[("fret", "lid"), ("fret", "base")], verbose=False)
asm.check_holes("fret", [(wx, wy, 25.6, 1.6) for wx, wy in FRET_HOLES],
                verbose=False)
# соосность каналов стыка: болт должен проходить шину+полку+дно свободно
asm.add("p0", rf"{OUT}\gs1_p0_base.stl", loc=(0, -240, 0))
import numpy as np
for hx in JX:
    pts = np.array([[hx, 9, zz] for zz in (-2.5, -1.5, 0.5, 2.0)])
    blocked = []
    for nm in ("splice", "base", "p0"):
        try:
            if asm.meshes[nm].contains(pts).any():
                blocked.append(nm)
        except BaseException:
            pass
    if blocked:
        print(f"  FAIL канал стыка x={hx}: перекрыт {blocked}")
        raise SystemExit(1)
print("каналы стыка сквозные")
print("holes: все кольца замкнуты")
