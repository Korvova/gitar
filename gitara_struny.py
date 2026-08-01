# -*- coding: utf-8 -*-
"""ГИТАРА: СТРУНЫ — 6-струнная насадка над розеткой (ФИНАЛ, схема юзера).
Струна = плоская пластина 2x10x100 между ДВУМЯ пружинами-гармошками на
съёмных столбиках. Магнит Ø4.1x2.1 плашмя в ямке Г-обоймы на шплинте;
датчик AS5600L (только I2C!) на плате под магнитом, зазор ~2.7.
Компоновка «тройки лево-центр-право»: струны 2,5 — обойма БЕЗ хвоста
(плата под струной), 1,4 — хвост на север, 3,6 — хвост на юг: платы
тремя диагональными линиями, магниты разнесены 25+ мм.
Рама на 6 шайбах-проставках 4 мм над крышкой wn — под рамой ход проводам
(вниз в розетку). Всё печатается без поддержек.
Проверено железом: стенды столов 48/49/50, «работает как на гитаре».
Запуск: .venv-b123d\\Scripts\\python gitara_struny.py
"""
from build123d import *

OUT = r"C:\App\gitar\2-0\Print\Print"

ROZ_Y = 665.0                          # центр розетки (мир); рама лок (0,0)=он
N_STR = 6
PITCH = 12.0
SX = [(i - (N_STR - 1) / 2) * PITCH for i in range(N_STR)]   # -30..30
KIND = ["N", "C", "S", "N", "C", "S"]  # хвост: север/без/юг (тройки юзера)
POST_DY = 75.5                         # центры столбиков от центра струны
STR_L = 100.0
STR_T, STR_H = 2.0, 10.0
MAG_D, MAG_H = 4.1, 2.1                # магнит AS5600 (замер юзера)
TAIL_Y = 26.0                          # вынос магнита хвостом (подтверждён)


def BB(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(
        abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))

# ================== СТРУНА (плоская пластина, 6 шт) ==================
struna = BB(-1, 1, 0, 100, 0, 10)
for hy in (4, 96):                     # дырки гармошек у самых концов
    struna -= Pos(0, hy, 3) * Rot(0, 90, 0) * Cylinder(1.1, 3)
struna -= Pos(0, 50, 4.4) * Rot(0, 90, 0) * Cylinder(0.85, 3)   # шплинт обоймы
for vy in (24, 76):                    # вырезы снизу: проход над крышечкой
    struna -= BB(-1.1, 1.1, vy - 10, vy + 10, -0.1, 2.4)   # +3 на край (юзер)

# ================== ГАРМОШКА (пружина, 2 жёсткости) ==================
def make_garm(t):
    """t — толщина стенки зигзага (жёсткость)"""
    h = t / 2
    g = BB(-2.6, -1.0, -4, 4, 0, 6)                   # северная лапка
    g -= Pos(-1.8, 0, 3) * Rot(0, 90, 0) * Cylinder(1.1, 2)
    g += BB(-1.0, 0.6, 4.2, 5.0, 0, 6)
    g += BB(-2.6, -1.0, 4, 5.0, 0, 6)
    yy = 5.0
    for i in range(3):
        dx = 4 if i % 2 == 0 else -4
        g += BB(min(0, dx) - h, max(0, dx) + h, yy, yy + 2 * h, 0, 6)
        g += BB(dx - h, dx + h, yy + 2 * h, yy + 3.8 - 2 * h, 0, 6)
        g += BB(min(0, dx) - h, max(0, dx) + h, yy + 3.8 - 2 * h, yy + 3.8, 0, 6)
        yy += 3.8
    g += BB(-0.6, 0.6, yy, 17.2, 0, 6)
    g += BB(-3.5, 0.6, 16.4, 17.2, 0, 6)
    g += BB(-3.5, -2.3, 16.4, 34, 0, 6)               # обход столбика
    g += BB(-3.5, 7, 32.5, 34, 0, 6)                  # плечо ЗА столбиком
    g -= Pos(2.2, 33.25, 3) * Rot(90, 0, 0) * Cylinder(0.8, 3.2)
    return g

garm = make_garm(0.8)
garm_soft = make_garm(0.6)

# ================== СТОЛБИК (съёмный, 12 шт) ==================
stolb = BB(-4, 4, -8, 8, 0, 3)                        # подошва, 2 винта М2
stolb += BB(-4, 4, -3, 3, 3, 17.5)
for dy in (-6, 6):
    stolb -= Pos(0, dy, 1.5) * Cylinder(1.1, 3.2)
stolb -= Pos(0, 0, 13.5) * Rot(90, 0, 0) * Cylinder(1.1, 6.4)   # винт с торца

# ---- ямка магнита: простая тугая Ø4.25; на хвосте сверху КРЫШЕЧКА на
# 2 болтиках М2 (решение юзера), в струне под неё вырез ------------------
def magnet_pocket(part, cx, cy):
    part -= Pos(cx, cy, -1.075) * Cylinder(2.125, 2.25)
    return part

# ============ Г-ОБОЙМА магнита (струны 2,5 — плата под струной) ========
# лок: z0 = НИЗ струны; ямка сдвинута от стенки — магнит кладётся сверху
sk = BB(-3.6, 3, -4, 4, -2.6, 0)
sk = magnet_pocket(sk, -1.1, 0)          # магнит накрыт самой струной
sk += BB(1.15, 3, -4, 4, 0, 6)                        # стенка Г
sk -= Pos(0, 0, 4.4) * Rot(0, 90, 0) * Cylinder(0.85, 8)   # шплинт
skoba = sk

# ============ Г-ОБОЙМА С ХВОСТОМ (струны 1,3,4,6) — вынос магнита ======
sk6 = BB(-3.6, 3, -4, 4, -2.6, 0)                     # дно (без ямки)
sk6 += BB(1.15, 3, -4, 4, 0, 6)
sk6 -= Pos(0, 0, 4.4) * Rot(0, 90, 0) * Cylinder(0.85, 8)
sk6 += BB(-3, 1, 4, TAIL_Y - 7, -2.6, 0)              # хвост 4x2.6
sk6 += BB(-4.6, 2.4, TAIL_Y - 7, TAIL_Y + 7, -2.6, 0)  # площадка магнита
sk6 = magnet_pocket(sk6, -1.1, TAIL_Y)
for wy in (TAIL_Y - 4.5, TAIL_Y + 4.5):                # каналы М2 крышечки
    sk6 -= Pos(-1.1, wy, -1.3) * Cylinder(0.9, 2.7)
skoba6 = sk6

# КРЫШЕЧКА магнита (юзер): плоская пластинка на 2 болтиках М2 поверх ямки
kryshka = BB(-3.4, 1.2, TAIL_Y - 7, TAIL_Y + 7, 0, 0.8)
for wy in (TAIL_Y - 4.5, TAIL_Y + 4.5):
    kryshka -= Pos(-1.1, wy, 0.4) * Cylinder(1.1, 1.0)

# ================== РАМА v3 (на крышке wn, вокруг розетки) =============
# лок: (0,0) = центр розетки; струны вдоль y (тела -50..50), шаг 12.
# Рама стоит на 6 шайбах 4 мм — под ней ход проводам к розетке.
RX, RY = 52, 95
rama = BB(-RX, RX, -RY, RY, 0, 3)
for i, sx in enumerate(SX):
    for sgn in (1, -1):                                # каналы 12 столбиков
        for dy in (-6, 6):
            rama -= Pos(sx + 2.2 * sgn, sgn * POST_DY + dy, 1.6) * \
                Cylinder(0.9, 2.9)
# подиумы плат AS5600 (лесенка по KIND) + карманы + СКВОЗНЫЕ прорези пинов
PCB = []                                               # (mx, my) центров чипов
for i, sx in enumerate(SX):
    k = KIND[i]
    mx = sx + (1.1 if k == "N" else -1.1)
    my = {"N": -TAIL_Y, "C": 0.0, "S": TAIL_Y}[k]
    PCB.append((mx, my))
    rama += BB(mx - 13.0, mx + 13.0, my - 13.0, my + 13.0, 3, 8.5)
    rama -= BB(mx - 11.8, mx + 11.8, my - 11.8, my + 11.8, 6.1, 8.6)  # карман
                                       # 23.6 — свободнее (юзер шлифовал 22.8)
    rama -= BB(mx - 7.5, mx - 3, my - 5.5, my + 5.5, -0.1, 6.2)  # пины: колодки
    rama -= BB(mx + 3, mx + 7.5, my - 5.5, my + 5.5, -0.1, 6.2)  # у чипа (фото)
    # крепление платы БЕЗ металла: 4 штырька Ø2.7 в штатные дырки Ø3 платы
    # (сетка 16x16, замер юзера); ДВА диагональных — с ЗАЩЁЛКОЙ-головкой
    # (конус с прорезью, как заводские клипсы плат — рисунок юзера)
    for px in (-8, 8):
        for py in (-8, 8):
            rama += Pos(mx + px, my + py, 7.1) * Cylinder(1.35, 2.0)
            if px * py < 0:                            # диагональ: защёлки
                snap = Pos(mx + px, my + py, 8.8) * Cone(1.8, 1.05, 1.4)
                snap -= BB(mx + px - 2, mx + px + 2,
                           my + py - 0.55, my + py + 0.55, 7.0, 9.6)
                head = Pos(mx + px, my + py, 8.5) * Cylinder(1.8, 0.8)
                head -= BB(mx + px - 2, mx + px + 2,
                           my + py - 0.55, my + py + 0.55, 7.0, 9.6)
                rama += snap + head
# крепёж к крышке: 6 x М3 сквозь раму и шайбу-проставку
FRAME_SCREWS = [(sx, sy) for sx in (-46, 46) for sy in (-87, 0, 87)]
for fx, fy in FRAME_SCREWS:
    rama -= Pos(fx, fy, 1.5) * Cylinder(1.6, 3.2)

shayba = Pos(0, 0, 2) * Cylinder(5, 4)                 # проставка рамы 4 мм
shayba -= Pos(0, 0, 2) * Cylinder(1.7, 4.2)

# ============ вспомогательные (тест-стенд, подставки, ножки) ============
podstavka = BB(-12.4, 12.4, -12.4, 12.4, 0, 4.8)       # плата на столе
nozhka = Pos(0, 0, 6) * Cylinder(5, 12)                # ножка тест-плиты
nozhka += Pos(0, 0, 13.5) * Cylinder(1.95, 3)

tp2 = BB(-20, 20, -95, 95, 0, 3)                       # тест-плита 1 струны
for sy, sxs in ((-POST_DY, -2.2), (POST_DY, 2.2)):
    for dy in (-6, 6):
        tp2 -= Pos(sxs, sy + dy, 1.6) * Cylinder(0.9, 2.9)
tp2 += BB(-13.9, 11.7, -12.8, 12.8, 3, 7.8)
tp2 -= BB(-12.5, 10.3, -11.4, 11.4, 6.1, 7.9)
tp2 -= BB(-20.1, -10.1, -3, 3, 6.0, 7.9)
tp2 -= BB(-12.5, -4.6, -9, 9, -0.1, 6.2)
tp2 -= BB(2.4, 10.3, -9, 9, -0.1, 6.2)
for cx in (-15, 15):
    for cy in (-88, 88):
        tp2 -= Pos(cx, cy, 1.5) * Cylinder(2.1, 3.2)

parts = [("gst_rama6", rama), ("gst_shayba", shayba),
         ("gst_struna2", struna), ("gst_garm", garm),
         ("gst_garm_soft", garm_soft), ("gst_stolb", stolb),
         ("gst_skoba", skoba), ("gst_skoba6", skoba6),
         ("gst_kryshka_mag", kryshka),
         ("gst_podstavka", podstavka), ("gst_nozhka", nozhka),
         ("gst_test2_plate", tp2)]
for name, part in parts:
    p = part if isinstance(part, Part) else Part() + part
    export_stl(p, rf"{OUT}\{name}.stl")
    print(f"{name}: volume={p.volume:.0f} mm3, solids={len(p.solids())}")
print("export done")

# ================= ПРОВЕРКИ =================
from clearance import Assembly

asm = Assembly()
asm.add("rama", rf"{OUT}\gst_rama6.stl")
clear, touch = [], []
for i, sx in enumerate(SX):
    k = KIND[i]
    asm.add(f"str{i}", rf"{OUT}\gst_struna2.stl", loc=(sx, -50, 13.5))
    clear.append((f"str{i}", "rama", 0.3))
    if k == "C":
        asm.add(f"sk{i}", rf"{OUT}\gst_skoba.stl", loc=(sx, 0, 13.5))
    else:
        asm.add(f"sk{i}", rf"{OUT}\gst_skoba6.stl", loc=(sx, 0, 13.5),
                rz=(180 if k == "N" else 0))
    touch.append((f"sk{i}", f"str{i}"))
    clear.append((f"sk{i}", "rama", 0.5))              # хвост НАД подиумом
    for sgn, tag in ((1, "s"), (-1, "n")):
        asm.add(f"st{i}{tag}", rf"{OUT}\gst_stolb.stl",
                loc=(sx + 2.2 * sgn, sgn * POST_DY, 3),
                rz=(0 if sgn > 0 else 180))
        touch.append((f"st{i}{tag}", "rama"))
        asm.add(f"g{i}{tag}", rf"{OUT}\gst_garm.stl",
                loc=(sx, sgn * 46, 13.5), rz=(0 if sgn > 0 else 180))
        touch.append((f"g{i}{tag}", f"str{i}"))
        touch.append((f"g{i}{tag}", f"st{i}{tag}"))
asm.check(clearances=clear, touching=touch, verbose=False)
asm.check_holes("rama", [(fx, fy, 1.5, 1.6) for fx, fy in FRAME_SCREWS],
                verbose=False)
print("струны-6: рама чиста")
