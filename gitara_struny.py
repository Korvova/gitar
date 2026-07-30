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

# --- потенциометр ALPS (джойстиковый, запчасть PS4) --- TODO: замерить!
POT_W, POT_L, POT_H = 9.7, 11.2, 4.5   # корпус (x, y, высота)
CROSS_D, CROSS_T = 4.4, 1.3            # крест шлица: размах и толщина лопасти
CROSS_H = 3.0                          # глубина креста
AXIS_H = 7.0                           # верх оси-втулки над рамой (корпус+крест)

# --- струна ---
STR_L = 100.0                          # длина рычага
STR_T, STR_H = 2.0, 10.0               # сечение
STR_Z = AXIS_H + 1.0                   # низ балки над рамой

POT_Y = ROZ_Y - 42                     # ряд потенциометров (север накладки)
POST_Y = POT_Y + STR_L + 12            # стойки гармошек (юг)


def BB(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(
        abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))

# ================== РАМА (на крышке вокруг розетки) ==================
RX = 48
rama = BB(-RX, RX, POT_Y - 12, POST_Y + 10, 0, 3)
rama -= BB(-RX + 10, RX - 10, POT_Y + 10, POST_Y - 14, -0.1, 3.1)  # окно
# посадочные лунки-маркеры потенциометров (позиционирование корпуса) + провода
for sx in SX:
    rama -= BB(sx - POT_W / 2, sx + POT_W / 2,
               POT_Y - POT_L / 2, POT_Y + POT_L / 2, 2.6, 3.1)
    rama -= BB(sx - 2, sx + 2, POT_Y - POT_L / 2 - 3, POT_Y - POT_L / 2,
               -0.1, 3.1)                              # щель проводов вниз
# стойки гармошек: колонна с вертикальным пазом (гармошка вставляется сверху)
for sx in SX:
    rama += BB(sx - 4, sx + 4, POST_Y - 4, POST_Y + 4, 3, STR_Z + STR_H)
    rama -= BB(sx - 0.7, sx + 0.7, POST_Y - 4.1, POST_Y - 1,
               STR_Z + 1, STR_Z + STR_H + 0.1)
# крепёж к крышке: 4 × М3 по углам (Ø3.2; в крышке — слепые каналы Ø2.6)
FRAME_SCREWS = [(sx, sy) for sx in (-RX + 5, RX - 5)
                for sy in (POT_Y - 6, POST_Y + 4)]
for fx, fy in FRAME_SCREWS:
    rama -= Pos(fx, fy, 1.5) * Cylinder(1.6, 3.2)

# ================== СТРУНА (рычаг, 6 одинаковых) ==================
# лок: ось потенциометра в (0,0), рычаг на юг (+y)
struna = BB(-STR_T / 2, STR_T / 2, -2, STR_L - 8, 0, STR_H)   # тело
struna += Pos(0, 0, -1.5) * Cylinder(3.2, 3)                  # башмак над осью
# крест-лопатки ВНИЗ в шлиц потенциометра (TODO: замер!)
struna += BB(-CROSS_D / 2, CROSS_D / 2, -CROSS_T / 2, CROSS_T / 2,
             -CROSS_H - 3, -1.5)
struna += BB(-CROSS_T / 2, CROSS_T / 2, -CROSS_D / 2, CROSS_D / 2,
             -CROSS_H - 3, -1.5)
# юг: паз под язык гармошки (сменная!)
struna -= BB(-0.7, 0.7, STR_L - 12, STR_L - 8.1, 1, STR_H + 0.1)

# ================== ГАРМОШКА (пружина, сменный расходник) =============
# полоска 0.8, высота 6, зигзаг 4 колена в плоскости качания; языки по концам
g = BB(-0.6, 0.6, 0, 3.5, 0, 6)                       # северный язык (в струну)
yy = 3.5
for i in range(4):                                     # колена зигзага
    dx = 4 if i % 2 == 0 else -4
    g += BB(min(0, dx) - 0.4, max(0, dx) + 0.4, yy, yy + 0.8, 0, 6)
    g += BB(dx - 0.4, dx + 0.4, yy + 0.8, yy + 3.2, 0, 6)
    g += BB(min(0, dx) - 0.4, max(0, dx) + 0.4, yy + 3.2, yy + 4.0, 0, 6)
    yy += 4.0
g += BB(-0.6, 0.6, yy, yy + 3.5, 0, 6)                # южный язык (в стойку)
garm = g

# ============ болванка потенциометра (для сцены, НЕ печатать) ============
pot = BB(-POT_W / 2, POT_W / 2, -POT_L / 2, POT_L / 2, 0, POT_H)
pot += Pos(0, 0, POT_H + (AXIS_H - POT_H) / 2) * Cylinder(3.4, AXIS_H - POT_H)
pot -= BB(-CROSS_D / 2, CROSS_D / 2, -CROSS_T / 2, CROSS_T / 2,
          POT_H, AXIS_H + 0.1)
pot -= BB(-CROSS_T / 2, CROSS_T / 2, -CROSS_D / 2, CROSS_D / 2,
          POT_H, AXIS_H + 0.1)

parts = [("gst_rama", rama), ("gst_struna", struna),
         ("gst_garm", garm), ("gst_pot_dummy", pot)]
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
clear, touch = [], [("rama", "top")]
for i, sx in enumerate(SX):
    asm.add(f"str{i}", rf"{OUT}\gst_struna.stl",
            loc=(sx, POT_Y, 26 + 3 + STR_Z))
    clear.append((f"str{i}", "rama", 0.3))             # рычаг ничего не задевает
    if i:
        clear.append((f"str{i}", f"str{i-1}", 4.0))    # соседки: место щипку
asm.check(clearances=clear, touching=touch, verbose=False)
asm.check_holes("rama", [(fx, fy, 27.5, 1.6) for fx, fy in FRAME_SCREWS],
                verbose=False)
print("струны: концепт чист")
