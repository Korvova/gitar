# -*- coding: utf-8 -*-
"""ГИТАРА: ДЕКА (2 секции по 160, y 480..800) — моторный отсек.
Моторы NEMA17 лесенкой (шаг 60, my = 510/570/630/690), снизу дна, валы вверх.
Кривошип: ступица с D-отверстием (вал Ø5 с лыской) задаёт ВЫСОТУ диска —
каждый диск в СВОЁМ этаже; палец Ø5 ВНИЗ, короткий, в ВИЛКУ хвоста ленты
(кулиса #2: лента ходит строго вдоль жёлоба, поперечный ход пина ест вилка).
Ход ленты ±7 (пин r7) -> угол-1 ±6.15 -> тележка 40 мм.
Запуск: .venv-b123d\\Scripts\\python gitara_deka.py
"""
from build123d import *

OUT = r"C:\App\gitar\2-0\Print\Print"
L = 160
Z_FLOOR = [3, 8.4, 13.8, 19.2]
JX = (-21, -9, 5, 21)
LANE = 10
MY = [505, 555, 605, 668]              # моторы (Д1: три, Д2: один; не на стыке)
R_PIN = 4.3                            # кривошип: радиус пальца (ход ±3.8+люфт)
DK1_Y0, DK2_Y0 = 480, 640


def BB(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(
        abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))


def deka_base(sec_y0, motors, south_shelf, tumba_xy, lid_y, neck_mount=False):
    """Дно секции деки: колодцы NEMA17, стыки, стенки, ямки гребёнок."""
    b = BB(-26, 26, 0, L, 0, 3)
    b += BB(-26, -22, 0, L, 3, 23)                     # стенки как у секций грифа
    b += BB(22, 26, 0, L, 3, 23)
    # стык СЕВЕР (верхняя полка)
    b -= BB(-26.1, 26.1, -0.1, 18, -0.1, 1.5)
    for hx in JX:
        b -= Pos(hx, 9, 2.25) * Cylinder(1.3, 1.7)
    if south_shelf:
        b += BB(-26, 26, L, L + 18, 0, 1.5)
        for hx in JX:
            b -= Pos(hx, L + 9, 0.75) * Cylinder(1.6, 1.7)
    else:                                              # южный торец гитары
        b += BB(-26, 26, L - 2, L, 3, 23)
    for my in motors:                                  # колодцы NEMA17
        yl = my - sec_y0
        b -= Pos(LANE, yl, 1.5) * Cylinder(11.3, 3.2)          # пилот Ø22.6
        for sx in (-1, 1):
            for sy in (-1, 1):                                 # М3 по 31х31
                b -= Pos(LANE + sx * 15.5, yl + sy * 15.5, 1.5) * Cylinder(1.7, 3.2)
    # ямки гребёнок-поддержек лент (между моторами) и мостиков-прижимов вилок
    for yg in (m - sec_y0 + 30 for m in motors):
        for gx in (-4, 18):
            if 4 < yg < L - 4:
                b -= Pos(gx, yg, 1.5) * Cylinder(3.0, 3.2)
    # сетка Ø2.6 под стойки электроники (свободный запад)
    for ex in (-19, -11):
        for ey in range(25, L - 15, 35):
            b -= Pos(ex, ey, 1.5) * Cylinder(1.3, 3.2)
    # корпус: дырки Ø3.4 в дне — винты М3 сверху в тумбы дна корпуса
    for tx, ty in tumba_xy:
        b -= Pos(tx, ty, 1.5) * Cylinder(1.7, 3.2)
    # корпус: вертикальные каналы Ø2.6 в верх стенок — крышка корпуса
    for ty in lid_y:
        for sx in (-24, 24):
            b -= Pos(sx, ty, 18.2) * Cylinder(1.3, 10)
    if neck_mount:              # язык фретборда сек-3: стенки понижены до 20
        for x0, x1 in ((-26.1, -21.9), (21.9, 26.1)):   # (под бобышки крышки),
            b -= BB(x0, x1, -0.1, 30.5, 20, 23.1)       # каналы под винты языка
        for sx in (-24, 24):
            b -= Pos(sx, 10, 16.1) * Cylinder(1.3, 8.2)
    return b

# ---------------- кривошипы: ступица задаёт этаж ----------------
# вал NEMA17 торчит над дном ~20; диск этажа k: низ на Z_FLOOR[k]+1.8,
# пин вниз до Z_FLOOR[k]+0.1 (в вилку ленты 1.6)
cranks = []
for k in range(4):
    disk_z0 = Z_FLOOR[k] + 1.8
    c = Pos(0, 0, disk_z0 + 1.25) * Cylinder(7, 2.5)           # диск Ø14
    dcut = Cylinder(2.6, 3) - Pos(2.25, 0, disk_z0 + 1.25) * Box(1.4, 6, 3.2)
    c -= Pos(0, 0, disk_z0 + 1.25) * (Cylinder(2.6, 2.7) -
                                      Pos(2.25, 0, 0) * Box(1.4, 6, 2.9))
    c += Pos(R_PIN, 0, disk_z0 - 0.85) * Cylinder(2.5, 1.7)   # ПИН ВНИЗ в вилку
    cranks.append(c)
# втулки-подставки: надеваются на вал до упора, задают высоту диска
sleeves = []
for k in range(4):
    h = Z_FLOOR[k] + 1.8 - 3
    s = Pos(0, 0, 3 + h / 2) * Cylinder(5, h)
    s -= Pos(0, 0, 3 + h / 2) * Cylinder(2.7, h + 0.2)
    sleeves.append(s)

# ---------------- гребёнка поддержки лент (между моторами) ----------------
comb = BB(-6, 21.9, -2, 2, 3, 22.5)
for zf in Z_FLOOR:
    comb -= BB(5.4, 14.6, -2.1, 2.1, zf - 0.15, zf + 1.95)    # щели лент
comb += Pos(-4, 0, 1.6) * Cylinder(2.85, 2.8)                 # штыри в ямки дна
comb += Pos(18, 0, 1.6) * Cylinder(2.85, 2.8)

# ------------- сегменты лент: ЗАЩЁЛКИ-нахлёсты на ПЕРЕХОДАХ секций ---------
# голова сек-1 (до 178) + ext (160..338) + ext (320..498) + хвост (480..my).
# Каждый стык: нижний язык 0.8 (штырёк вверх Ø3 высокий + дырка) + верхний
# язык 0.8 (дырка + штырёк вниз) — взаимная защёлка без крепежа (идея юзера).
# Позиции штырьков T+6.5 / T+11.5 — при ходе ±3.8 не выходят из перехода.
def lap_top(seg, y0):
    """верхний язык на СЕВЕРНОМ конце (ложится на нижний язык предыдущего)"""
    seg -= BB(-4.1, 4.1, y0 - 0.1, y0 + 18, -0.1, 0.8)
    seg -= Pos(0, y0 + 6.5, 1.2) * Cylinder(1.75, 1.0)   # дырка: высокий штырёк
    seg += Pos(0, y0 + 11.5, 0.4) * Cylinder(1.5, 0.8)   # штырёк вниз (заподлицо)
    return seg


def lap_bot(seg, y1):
    """нижний язык на ЮЖНОМ конце"""
    seg -= BB(-4.1, 4.1, y1 - 18, y1 + 0.1, 0.8, 1.7)
    seg += Pos(0, y1 - 11.5, 2.0) * Cylinder(1.5, 2.4)   # штырёк вверх (высокий)
    seg -= Pos(0, y1 - 6.5, 0.4) * Cylinder(1.75, 1.0)   # дырка: штырёк вниз
    return seg

ext = lap_bot(lap_top(BB(-4, 4, 0, 178, 0, 1.6), 0), 178)   # 2 шт на этаж

tails = []
for k in range(4):
    ln = MY[k] - 480 + 10                              # мир 480..my+10
    t = lap_top(BB(-4, 4, 0, ln, 0, 1.6), 0)
    t += BB(-9.5, 9.5, ln - 16, ln, 0, 1.6)            # площадка вилки поперёк
    t -= BB(-7.5, 7.5, ln - 13, ln - 7, -0.1, 1.7)     # ВИЛКА: паз 6 по центру my
    tails.append(t)

# тумбы корпуса (лок): винты сверху сквозь дно; каналы крышки в верх стенок
TUMBA1 = [(-15, 45), (-15, 105), (-15, 150), (20, 65), (20, 115)]
TUMBA2 = [(-15, 45), (-15, 110), (20, 60), (20, 120)]
parts = [("gdk1_base", deka_base(DK1_Y0, [505, 555, 605], True,
                                 TUMBA1, (40, 100, 135), neck_mount=True)),
         ("gdk2_base", deka_base(DK2_Y0, [668], False, TUMBA2, (75, 120))),
         ("gdk_comb", comb), ("gdk_ext", ext)]
parts += [(f"gdk_crank{k}", cranks[k]) for k in range(4)]
parts += [(f"gdk_sleeve{k}", sleeves[k]) for k in range(4)]
parts += [(f"gdk_tail{k}", tails[k]) for k in range(4)]
for name, part in parts:
    p = part if isinstance(part, Part) else Part() + part
    export_stl(p, rf"{OUT}\{name}.stl")
    print(f"{name}: volume={p.volume:.0f} mm3, solids={len(p.solids())}")
print("export done")

# ================= ПРОВЕРКИ =================
from clearance import Assembly

asm = Assembly()
asm.add("dk1", rf"{OUT}\gdk1_base.stl", loc=(0, DK1_Y0, 0))
asm.add("dk2", rf"{OUT}\gdk2_base.stl", loc=(0, DK2_Y0, 0))
clear, touch = [], [("dk1", "dk2")]
for k in range(4):
    dk = "dk1" if MY[k] < DK2_Y0 else "dk2"
    asm.add(f"cr{k}", rf"{OUT}\gdk_crank{k}.stl", loc=(LANE, MY[k], 0))
    clear.append((f"cr{k}", dk, 0.3))                  # диск/ступица над дном
    asm.add(f"tl{k}", rf"{OUT}\gdk_tail{k}.stl",
            loc=(LANE, 480, Z_FLOOR[k] + 0.05))
    clear.append((f"tl{k}", f"cr{k}", 0.0))
    for j in range(k):                                 # чужие ленты мимо дисков
        clear.append((f"tl{k}", f"cr{j}", 0.5))
# стык-3 (переход сек3/дека): защёлка ext+хвост этажа 0 — языки в контакте,
# штырьки в дырках (глубина 0 = попали)
asm.add("ex0", rf"{OUT}\gdk_ext.stl", loc=(LANE, 320, Z_FLOOR[0] + 0.05))
touch.append(("tl0", "ex0"))
COMB_Y = (535, 585, 635)
for i, yg in enumerate(COMB_Y):
    dk = "dk1" if yg < DK2_Y0 else "dk2"
    asm.add(f"comb{i}", rf"{OUT}\gdk_comb.stl", loc=(0, yg, 0))
    touch.append((f"comb{i}", dk))
    for k in range(4):
        if MY[k] - 12 > yg:                     # лента k доходит до этой гребёнки
            clear.append((f"tl{k}", f"comb{i}", 0.1))
asm.check(clearances=clear, touching=touch, verbose=False)
print("дека: каркас чист")
