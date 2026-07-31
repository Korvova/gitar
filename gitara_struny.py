# -*- coding: utf-8 -*-
"""ГИТАРА: СТРУНЫ — насадка над розеткой (концепт, конструкция юзера).
6 рычагов-«струн»: печатный рычаг 2×10×100 Г-образно вставлен лопаткой в
джойстиковый потенциометр ALPS 10 кОм (ось+подшипник+датчик), второй конец
через СМЕННУЮ пружину-гармошку к стойке рамы. Щипок вбок → угол оси → ADC.
Рама сидит на крышке wn вокруг розетки (центр y=665), 4 винта М3.
⚠ РАЗМЕРЫ ПОТЕНЦИОМЕТРА — типовые, УТОЧНИТЬ ПО ЗАМЕРУ когда приедут:
POT_W/L/H (корпус), CROSS_* (крест шлица), высота креста.
Запуск: .venv-b123d\\Scripts\\python gitara_struny.py
"""
from build123d import *

OUT = r"C:\App\gitar\2-0\Print\Print"

ROZ_Y = 665.0                          # центр розетки (мир)
N_STR = 6
PITCH = 12.0                           # шаг струн по x
SX = [(i - (N_STR - 1) / 2) * PITCH for i in range(N_STR)]   # -30..30

# --- потенциометр ALPS (джойстиковый, запчасть PS4) ---
# корпус 13x10x4 по данным продавца (юзер); ротор и прорезь — TODO замерить!
# Официальный чертёж стика: docs/ALPS_RKJXV_datasheet.pdf — VR-модуль:
# ширина 12.45 (с ушками), тело 10.8, корпус ~2.9 + ротор; ПИНЫ ШАГ 2.5;
# рабочий угол ~±23 град (стик 46 max); ресурс 2 млн циклов
POT_W, POT_L, POT_H = 10.0, 13.0, 4.0  # корпус (x, y=сторона пинов, высота)
ROT_D, ROT_H = 8.6, 2.0                # белый РОТОР-диск сверху корпуса
BLADE_W, BLADE_T = 2.8, 0.85           # по ЗАМЕРУ юзера: прорезь 3x1, сквозная
PODIUM = 4.0                           # подиум ряда: полость под замок-болтик
AXIS_H = PODIUM + POT_H + ROT_H        # верх ротора над рамой

# --- струна ---
STR_L = 100.0                          # длина рычага
STR_T, STR_H = 2.0, 10.0               # сечение
STR_Z = AXIS_H                         # низ балки = верх ротора

POT_Y = ROZ_Y - 42                     # ряд потенциометров (север накладки)
POST_Y = POT_Y + 117.5                 # центр СЪЁМНЫХ столбиков гармошек

def BB(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(
        abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))

# ================== РАМА (на крышке вокруг розетки) ==================
RX = 48
rama = BB(-RX, RX, POT_Y - 16, POST_Y + 10, 0, 3)
rama -= BB(-RX + 10, RX - 10, POT_Y + 10, POST_Y - 14, -0.1, 3.1)  # окно
# блок-ПОДИУМ с гнёздами-стаканами: потенциометр сидит по плечи, под ним
# сквозное окно — лопатка струны выходит вниз, там поперечный болтик-замок
rama += BB(-42, 42, POT_Y - 8, POT_Y + 8, 3, 3 + PODIUM + POT_H)
for sx in SX:
    rama -= BB(sx - POT_W / 2, sx + POT_W / 2,           # карман корпуса
               POT_Y - POT_L / 2, POT_Y + POT_L / 2,
               3 + PODIUM - 0.1, 3 + PODIUM + POT_H + 0.1)
    rama -= BB(sx - 6, sx + 6, POT_Y - 4, POT_Y + 4,     # окно замка (насквозь)
               -0.1, 3 + PODIUM + 0.1)
    rama -= BB(sx - 4, sx + 4, POT_Y + POT_L / 2 - 1, POT_Y + POT_L / 2 + 3.5,
               -0.1, 3 + PODIUM + POT_H + 0.2)   # проём ПИНОВ: на юг (к розетке)
                                                 # и насквозь вниз — провода в окно
for kx, ky in ((-38.6, POT_Y), (38.6, POT_Y)):           # каналы прижим-планки
    rama -= Pos(kx, ky, 3 + PODIUM + POT_H - 2) * Cylinder(0.9, 4.2)
# столбики гармошек — СЪЁМНЫЕ (юзер): гармошка прикручивается к столбику
# на столе, узел ставится на раму 2 винтами М2 сверху; в раме — каналы
for sx in SX:
    for dy in (-6, 6):
        rama -= Pos(sx + 2.2, POST_Y + dy, 1.6) * Cylinder(0.9, 2.9)
# крепёж к крышке: 4 × М3 по углам (Ø3.2; в крышке — слепые каналы Ø2.6)
FRAME_SCREWS = [(sx, sy) for sx in (-RX + 5, RX - 5)
                for sy in (POT_Y - 12, POST_Y + 4)]   # север — мимо подиума
for fx, fy in FRAME_SCREWS:
    rama -= Pos(fx, fy, 1.5) * Cylinder(1.6, 3.2)

# ============ ПРИЖИМ-ПЛАНКА ряда потенциометров (не вылетят) ============
klamp = BB(-45, 45, POT_Y - 8, POT_Y + 8, 0, 1.5)   # садится на верх стаканов
for sx in SX:
    klamp -= Pos(sx, POT_Y, 0.75) * Cylinder(ROT_D / 2 + 0.5, 1.7)  # окна роторов
for kx in (-38.6, 38.6):
    klamp -= Pos(kx, POT_Y, 0.75) * Cylinder(1.1, 1.7)              # винты М2

# ================== СТРУНА (рычаг, 6 одинаковых) ==================
# лок: ось ротора в (0,0), z0 = верх ротора; рычаг на юг (+y).
# ПЕЧАТЬ ЛЁЖА на западном боку (x=-1) — ничего не выступает вниз,
# все дырки при печати вертикальные, поддержек ноль (юзер)
struna = BB(-STR_T / 2, STR_T / 2, -2, STR_L - 8, 0, STR_H)   # тело
struna += Pos(0, 0, 1) * Cylinder(3.1, 2)                     # башмак над ротором
# лопатка НАСКВОЗЬ ротора и корпуса, ДЛИННОЙ стороной вдоль струны;
# ниже корпуса — дырка Ø1.6: болтик М2 поперёк = замок (юзер)
struna += BB(-BLADE_T / 2, BLADE_T / 2, -BLADE_W / 2, BLADE_W / 2,
             -(ROT_H + POT_H + 3), 0.1)
struna -= (Pos(0, 0, -(ROT_H + POT_H + 1.7)) * Rot(0, 90, 0) *
           Cylinder(0.85, 3))    # Ø1.7: ШПЛИНТ из филамента 1.75 (лопатка узкая,
                                 # болтик не помещается; вертикаль держит гармошка)
# юг: просто ДЫРОЧКА в теле (юзер) — винт М2 сквозь лапку гармошки + гайка
struna -= (Pos(0, STR_L - 12, 3) * Rot(0, 90, 0) * Cylinder(1.1, 3))

# ================== ГАРМОШКА (пружина, сменный расходник) =============
# лок: (0,0) = дырка северной лапки; призма высотой 6 — печать стоя без
# поддержек. Лапки вертикальные, винты М2 вбок; юг — буквой Г к столбику.
def make_garm(t):
    """t — толщина стенки зигзага (жёсткость пружины)"""
    h = t / 2
    g = BB(-2.6, -1.0, -4, 4, 0, 6)                   # северная лапка
    g -= Pos(-1.8, 0, 3) * Rot(0, 90, 0) * Cylinder(1.1, 2)
    g += BB(-1.0, 0.6, 4.2, 5.0, 0, 6)                # перемычка ЗА концом тела
    g += BB(-2.6, -1.0, 4, 5.0, 0, 6)
    yy = 5.0
    for i in range(3):                                 # колена зигзага
        dx = 4 if i % 2 == 0 else -4
        g += BB(min(0, dx) - h, max(0, dx) + h, yy, yy + 2 * h, 0, 6)
        g += BB(dx - h, dx + h, yy + 2 * h, yy + 3.8 - 2 * h, 0, 6)
        g += BB(min(0, dx) - h, max(0, dx) + h, yy + 3.8 - 2 * h, yy + 3.8, 0, 6)
        yy += 3.8
    g += BB(-0.6, 0.6, yy, 17.2, 0, 6)                # полоса до обхода
    g += BB(-3.5, 0.6, 16.4, 17.2, 0, 6)              # поперечина на запад
    g += BB(-3.5, -2.3, 16.4, 34, 0, 6)               # обход столбика сбоку
    g += BB(-3.5, 7, 32.5, 34, 0, 6)   # плечо ЗА столбиком (юзер): винт снаружи
    g -= Pos(2.2, 33.25, 3) * Rot(90, 0, 0) * Cylinder(0.8, 3.2)
    return g

garm = make_garm(0.8)
garm_soft = make_garm(0.6)                             # помягче — на подбор

# ============ СТОЛБИК гармошки (съёмный, 6 шт) ============
# лок: (0,0) = центр тела; подошва вдоль y, 2 дырки М2 (винты сверху)
stolb = BB(-4, 4, -8, 8, 0, 3)                        # подошва-фланец
stolb += BB(-4, 4, -3, 3, 3, 17.5)                    # тело
for dy in (-6, 6):
    stolb -= Pos(0, dy, 1.5) * Cylinder(1.1, 3.2)
stolb -= (Pos(0, 0, 13.5) * Rot(90, 0, 0) *
          Cylinder(1.1, 6.4))       # канал СКВОЗНОЙ: винт М2х10 заходит С ЮГА

# ============ болванка потенциометра (для сцены, НЕ печатать) ============
pot = BB(-POT_W / 2, POT_W / 2, -POT_L / 2, POT_L / 2, 0, POT_H)
pot += Pos(0, 0, POT_H + ROT_H / 2) * Cylinder(ROT_D / 2, ROT_H)   # ротор-диск
pot -= BB(-BLADE_T / 2 - 0.1, BLADE_T / 2 + 0.1, -BLADE_W / 2 - 0.1,
          BLADE_W / 2 + 0.1, -0.1, POT_H + ROT_H + 0.1)   # прорезь СКВОЗНАЯ (вдоль y)
for px in (-2.5, 0, 2.5):                                 # 3 ножки-пина (юг, вниз)
    pot += BB(px - 0.35, px + 0.35, POT_L / 2, POT_L / 2 + 2.5, 0.8, 1.4)
    pot += BB(px - 0.35, px + 0.35, POT_L / 2 + 1.9, POT_L / 2 + 2.5, -3.5, 1.4)

# ============ ТЕСТ-СТЕНД «одна струна» (юзер: примериться до партии) =====
tp = BB(-25, 25, -22, 132, 0, 3)                       # плита на стол
tp += BB(-18, 18, -8, 8, 3, 3 + PODIUM + POT_H)        # подиум одного гнезда
tp -= BB(-POT_W / 2, POT_W / 2, -POT_L / 2, POT_L / 2,
         3 + PODIUM - 0.1, 3 + PODIUM + POT_H + 0.1)   # карман корпуса
tp -= BB(-6, 6, -4, 4, -0.1, 3 + PODIUM + 0.1)         # окно замка (насквозь)
tp -= BB(-4, 4, POT_L / 2 - 1, POT_L / 2 + 3.5,
         -0.1, 3 + PODIUM + POT_H + 0.2)               # проём пинов
for kx in (-14, 14):                                   # каналы прижим-планки
    tp -= Pos(kx, 0, 3 + PODIUM + POT_H - 2) * Cylinder(0.9, 4.2)
for dy in (-6, 6):                                     # каналы столбика
    tp -= Pos(2.2, 117.5 + dy, 1.6) * Cylinder(0.9, 2.9)

tk = BB(-18, 18, -8, 8, 0, 1.5)                        # мини прижим-планка
tk -= Pos(0, 0, 0.75) * Cylinder(ROT_D / 2 + 0.5, 1.7)
for kx in (-14, 14):
    tk -= Pos(kx, 0, 0.75) * Cylinder(1.1, 1.7)

parts = [("gst_test_plate", tp), ("gst_test_klamp", tk),
         ("gst_garm_soft", garm_soft),
("gst_rama", rama), ("gst_struna", struna),
         ("gst_garm", garm), ("gst_klamp", klamp), ("gst_stolb", stolb),
         ("gst_pot_dummy", pot)]
for name, part in parts:
    p = part if isinstance(part, Part) else Part() + part
    export_stl(p, rf"{OUT}\{name}.stl")
    print(f"{name}: volume={p.volume:.0f} mm3, solids={len(p.solids())}")
print("export done")

# ================= ПРОВЕРКИ (концепт: рама на крышке, струны свободны) ===
from clearance import Assembly

asm = Assembly()
asm.add("top", rf"{OUT}\gk_top_wn.stl")
asm.add("rama", rf"{OUT}\gst_rama.stl", loc=(0, 0, 26))
asm.add("klamp", rf"{OUT}\gst_klamp.stl",
        loc=(0, 0, 26 + 3 + PODIUM + POT_H))
clear = []
touch = [("rama", "top"), ("klamp", "rama")]
for i, sx in enumerate(SX):
    asm.add(f"str{i}", rf"{OUT}\gst_struna.stl",
            loc=(sx, POT_Y, 26 + 3 + STR_Z))
    asm.add(f"g{i}", rf"{OUT}\gst_garm.stl",
            loc=(sx, POT_Y + STR_L - 12, 26 + 3 + STR_Z))
    clear.append((f"str{i}", "rama", 0.3))             # рычаг ничего не задевает
    clear.append((f"str{i}", "klamp", 0.2))            # и прижим-планку
    asm.add(f"st{i}", rf"{OUT}\gst_stolb.stl",
            loc=(sx + 2.2, POST_Y, 26 + 3))
    touch.append((f"g{i}", f"str{i}"))                 # лапка к боку прилива
    touch.append((f"g{i}", f"st{i}"))                  # лапка к столбику
    touch.append((f"st{i}", "rama"))                   # подошва на раме
    if i:
        clear.append((f"str{i}", f"str{i-1}", 4.0))    # соседки: место щипку
asm.check(clearances=clear, touching=touch, verbose=False)
asm.check_holes("rama", [(fx, fy, 27.5, 1.6) for fx, fy in FRAME_SCREWS],
                verbose=False)
print("струны: концепт чист")
