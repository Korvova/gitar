# -*- coding: utf-8 -*-
"""
Прототип v8 "тележка на тросике": СБОРНЫЙ гриф (2 слоя) + крепление NEMA 14 в деке.

Схема: тележка ездит поперёк грифа в Т-пазу. Тросик (PE-оплётка 0.5) идёт
петлёй: барабан на валу NEMA 14 (круглый, Ø36.5, уши 2-M3 @ 43.85) ->
направляющий ролик -> боковой канал грифа -> угловой ролик Ø5 -> поперёк
грифа к КРЮЧКУ на конце основания тележки (узел). Второй конец зеркально.
Дорожки двух концов разнесены по X (31 и 39) -> крючки не встречают ролики
-> ход полные +-20 мм (40 мм). Габарит грифа 50 мм чистый, ничего не выпирает.

Гриф из двух печатных слоёв (задел под 4 этажа для 4 тележек):
  L1 низ z 0..6  - каналы/канавки/карманы роликов ОТКРЫТЫ СВЕРХУ (трос кладётся)
  L2 верх z 6..12 - Т-паз (полость + губки); накрывает каналы L1
Слои стянуты 4x M3 сверху + 2x M3 насквозь в деку.

Оси: X вдоль грифа (0..125 гриф, 100..200 дека), Y поперёк (+-25), Z вверх.
Трос в грифе на z~3.5, ручьи барабана z 2.5 и 4.5. Оси роликов - филамент 1.75.

Детали:
  neck_base_v8.stl  - слой L1 (печать как есть)
  neck_top_a_v8.stl - слой L2 передняя часть с губкой (печать ВВЕРХ НОГАМИ)
  neck_top_b_v8.stl - слой L2 задняя часть с губкой (печать ВВЕРХ НОГАМИ)
  carriage_v8.stl  - тележка с крючками (печать на боку или с поддержками)
  drum_v8.stl      - барабан на вал Ø2.5 (натяг + клей), 2 ручья
  roller_corner_v8.stl x2, roller_guide_v8.stl x2
  deck_v8.stl      - плита деки: колодец мотора, стойки, рельсы, ноги
Сборка: тележку в паз L2 сбоку -> ролики в карманы L1, оси-филамент ->
L2 на L1, 4x M3 -> гриф на деку, 2x M3 -> мотор в колодец -> барабан -> трос.
"""
from build123d import *

OUT = r"C:\app\Esp-gitar"


def BB(x0, x1, y0, y1, z0, z1):
    """Box по границам (не по центру), порядок границ любой."""
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(
        abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))


# ---------------- параметры ----------------
NECK_L, NECK_W = 125.0, 50.0
SPLIT_Z, NECK_T = 6.0, 12.0                     # шов слоёв z=6, верх грифа z=12
SLOT_X = 35.0                                   # центр Т-паза
LANE_A, LANE_B = 31.0, 39.0                     # дорожки концов троса (поперечные)
CH_Y, CH_W = 17.0, 3.5                          # боковые каналы: центр, ширина
RC = 2.5                                        # эфф. радиус углового ролика
ROLL_A = (LANE_A + RC, CH_Y + RC)               # угловой A (33.5, +19.5), трос с +Y
ROLL_B = (LANE_B + RC, -(CH_Y + RC))            # угловой B (41.5, -19.5), трос с -Y
POCKET_R = 4.75
PIN_R_PRESS = 0.85                              # отверстие под ось-филамент (натяг)
PIN_R_FREE = 0.975                              # бора ролика (свободно)
TRAVEL = 20.0                                   # ход тележки +-20

MOT_X = 160.0
MOT_HOLE_R = 18.7                               # колодец Ø37.4 (корпус Ø36.5)
EAR_CC = 43.85
GUIDE_X, GUIDE_Y = 131.0, 14.5                  # направляющие ролики в деке

DECK_SCREWS = [(112, 11), (112, -11)]           # гриф+L1 -> дека, M3 насквозь
STACK_SCREWS = [(15, 21.5), (15, -21.5), (55, 21.5), (55, -21.5)]  # L2 -> L1, M3

# ---------------- гриф: слой L1 (низ, каналы) ----------------
base_l = BB(0, NECK_L, -25, 25, 0, SPLIT_Z)
# боковые каналы, открыты сверху (накроет L2); от углового ролика до торца
base_l -= BB(ROLL_A[0], NECK_L, CH_Y - CH_W / 2, CH_Y + CH_W / 2, 2.5, SPLIT_Z + 0.1)
base_l -= BB(ROLL_B[0], NECK_L, -CH_Y - CH_W / 2, -CH_Y + CH_W / 2, 2.5, SPLIT_Z + 0.1)
# поперечные дорожки крючков/троса, во всю ширину
for lane in (LANE_A, LANE_B):
    base_l -= BB(lane - 1.5, lane + 1.5, -25, 25, 3, SPLIT_Z + 0.1)
# карманы угловых роликов + оси
for cx, cy in (ROLL_A, ROLL_B):
    base_l -= Pos(cx, cy, 3.6) * Cylinder(POCKET_R, 4.8 + 0.1)          # z 1.2..6+
    base_l -= Pos(cx, cy, 0.6) * Cylinder(PIN_R_PRESS, 1.3)             # ось, натяг
for sx, sy in DECK_SCREWS:
    base_l -= Pos(sx, sy, 3) * Cylinder(1.7, 6.2)                       # M3 насквозь
for sx, sy in STACK_SCREWS:
    base_l -= Pos(sx, sy, 3.5) * Cylinder(1.25, 5.2)                    # M3 самонарез, глухое

# ---------------- гриф: слой L2 (верх, Т-паз) — ДВЕ детали, паз сквозной ----------------
# передняя (к голове): тело до паза + своя губка
top_a = BB(0, 24, -25, 25, SPLIT_Z, NECK_T) + BB(24, 27, -25, 25, 9.7, NECK_T)
for sx, sy in STACK_SCREWS[:2]:                 # (15, +-21.5)
    top_a -= Pos(sx, sy, 9) * Cylinder(1.7, 6.2)
    top_a -= Pos(sx, sy, 10.6) * Cylinder(3.25, 3.0)                    # потай

# задняя (к деке): тело после паза + своя губка
top_b = BB(46, NECK_L, -25, 25, SPLIT_Z, NECK_T) + BB(43, 46, -25, 25, 9.7, NECK_T)
for sx, sy in STACK_SCREWS[2:]:                 # (55, +-21.5)
    top_b -= Pos(sx, sy, 9) * Cylinder(1.7, 6.2)
    top_b -= Pos(sx, sy, 10.6) * Cylinder(3.25, 3.0)
for sx, sy in DECK_SCREWS:
    top_b -= Pos(sx, sy, 9) * Cylinder(1.7, 6.2)
    top_b -= Pos(sx, sy, 10.6) * Cylinder(3.25, 3.0)

# ---------------- тележка ----------------
car = BB(24.4, 45.6, -12, 12, 6.2, 9.4)          # основание в полости
car += BB(27.5, 42.5, -12, 12, 9.4, 13)          # шея через горловину
car += BB(27.5, 42.5, -11, 11, 13, 25)           # стакан под палец
car -= BB(29.25, 40.75, -9, 9, 14.5, 25.1)       # внутр. 11.5 x 18
# крючки на концах: A на -Y (трос от ролика A с +Y), B на +Y (трос от B с -Y)
car += BB(LANE_A - 1.25, LANE_A + 1.25, -12, -9, 3.4, 6.2)
car += BB(LANE_B - 1.25, LANE_B + 1.25, 9, 12, 3.4, 6.2)
car -= Pos(LANE_A, -10.5, 4.3) * Rot(X=90) * Cylinder(0.8, 8)   # Ø1.6 под трос, узел снаружи
car -= Pos(LANE_B, 10.5, 4.3) * Rot(X=90) * Cylinder(0.8, 8)

# ---------------- барабан (в нуле, печать как есть) ----------------
drum = Pos(0, 0, (1.7 + 2.1) / 2) * Cylinder(7.5, 0.4)
drum += Pos(0, 0, 2.5) * Cylinder(5.0, 0.8)                   # ручей 1 (z=2.5)
drum += Pos(0, 0, 3.5) * Cylinder(7.5, 1.2)
drum += Pos(0, 0, 4.5) * Cylinder(5.0, 0.8)                   # ручей 2 (z=4.5)
drum += Pos(0, 0, 5.6) * Cylinder(7.5, 1.4)
drum = Pos(0, 0, -1.7) * drum                                 # низ на z=0
drum -= Pos(0, 0, 2.3) * Cylinder(1.175, 4.8)                 # бора Ø2.35 + клей
for s in (-1, 1):
    drum -= Pos(s * 6.2, 0, 2.3) * Cylinder(0.65, 4.8)        # узлы концов

# ---------------- ролики (в нуле) ----------------
def roller(h_bot_fl, h_core, h_top_fl, r_core=2.3, r_fl=3.25):
    r = Pos(0, 0, h_bot_fl / 2) * Cylinder(r_fl, h_bot_fl)
    r += Pos(0, 0, h_bot_fl + h_core / 2) * Cylinder(r_core, h_core)
    r += Pos(0, 0, h_bot_fl + h_core + h_top_fl / 2) * Cylinder(r_fl, h_top_fl)
    h = h_bot_fl + h_core + h_top_fl
    r -= Pos(0, 0, h / 2) * Cylinder(PIN_R_FREE, h + 0.2)
    return r

roller_corner = roller(1.2, 1.8, 1.5)                 # h 4.5, ручей на z троса ~3.5
roller_guide = roller(0.6, 4.4, 0.6, r_fl=3.5)        # h 5.6, ловит уровни 2.5/4.5

# ---------------- плита деки ----------------
deck = BB(100, 200, -30, 30, -3, 0)
for sx0, sx1 in ((100, 112), (188, 200)):             # ноги (мотор висит вниз на 22)
    for s in (-1, 1):
        deck += BB(sx0, sx1, s * 18, s * 30, -29, -3)
for s in (-1, 1):
    deck += BB(100, 126, s * 25.2, s * 28.2, 0, 8)    # рельсы по бортам грифа
    deck += BB(125.4, 129.4, s * 5, s * 10, 0, 8)     # упоры торца (тросы на Y~15-17)

deck -= Pos(MOT_X, 0, -1.5) * Cylinder(MOT_HOLE_R, 3.2)          # мотор падает сверху
deck -= BB(154, 166, -24, -16, -3.1, 0.1)                        # вырез под разъём ZH-4AW
for s in (-1, 1):
    deck -= Pos(MOT_X + s * EAR_CC / 2, 0, -1.5) * Cylinder(1.25, 3.2)    # M3 ушек
    deck -= Pos(GUIDE_X, s * GUIDE_Y, -1.5) * Cylinder(PIN_R_PRESS, 3.2)  # оси направляющих
for sx, sy in DECK_SCREWS:
    deck -= Pos(sx, sy, -1.5) * Cylinder(1.25, 3.2)                       # M3 грифа

# ---------------- мок мотора (только для рендера) ----------------
mot = Pos(MOT_X, 0, -11) * Cylinder(18.25, 22)
mot += BB(MOT_X - 25.9, MOT_X + 25.9, -4.5, 4.5, 0, 1.5)
for s in (-1, 1):
    mot += Pos(MOT_X + s * EAR_CC / 2, 0, 0.75) * Cylinder(3.5, 1.5)
    mot -= Pos(MOT_X + s * EAR_CC / 2, 0, 0.75) * Cylinder(1.6, 1.7)
mot += Pos(MOT_X, 0, 0.75) * Cylinder(8, 1.5)                    # пилот Ø16
mot += Pos(MOT_X, 0, 3) * Cylinder(1.25, 6)                      # вал Ø2.5
mot += BB(154.75, 165.25, -21.5, -17.5, -22, -14)                # бугор разъёма

# ---------------- экспорт ----------------
parts = [("neck_base_v8", base_l), ("neck_top_a_v8", top_a), ("neck_top_b_v8", top_b),
         ("carriage_v8", car), ("drum_v8", drum), ("roller_corner_v8", roller_corner),
         ("roller_guide_v8", roller_guide), ("deck_v8", deck), ("_mock_nema14", mot)]
for name, part in parts:
    p = part if isinstance(part, Part) else Part() + part
    export_stl(p, rf"{OUT}\{name}.stl")
    print(f"{name}: volume={p.volume:.0f} mm3, solids={len(p.solids())}")

# ---------------- проверка + рендер ----------------
import numpy as np
import trimesh
import pyvista as pv

meshes = {}
for name, _ in parts:
    m = trimesh.load(rf"{OUT}\{name}.stl")
    print(f"{name}: watertight={m.is_watertight}, bodies={m.body_count}")
    meshes[name] = m


def placed(name, dx=0, dy=0, dz=0):
    m = meshes[name].copy()
    m.apply_translation([dx, dy, dz])
    return pv.wrap(m)


# тросики (визуально, тележка в центре)
cabA = np.array([(158, 5.4, 4.5), (133.2, 13.2, 4.5), (128.5, 16.6, 4.2), (125, 17, 3.9),
                 (37, 17, 3.5), (34.4, 17.3, 3.5), (31.6, 18.9, 3.5), (31, 19.5, 3.6),
                 (31, -10.5, 4.3)])
cabB = np.array([(158, -5.4, 2.5), (133.2, -13.2, 2.5), (128.5, -16.6, 2.8), (125, -17, 3.2),
                 (45, -17, 3.5), (42.4, -17.3, 3.5), (39.6, -18.9, 3.5), (39, -19.5, 3.6),
                 (39, 10.5, 4.3)])


def add_cables(pl):
    for pts, col in ((cabA, "#d94f2a"), (cabB, "#2a6bd9")):
        pl.add_mesh(pv.lines_from_points(pts).tube(radius=0.3), color=col)


def scene(pl, ghost_car=True):
    pl.add_mesh(placed("deck_v8"), color="#9fb4c7", smooth_shading=False)
    pl.add_mesh(placed("_mock_nema14"), color="#555a60", smooth_shading=False)
    pl.add_mesh(placed("neck_base_v8"), color="#b09b82", smooth_shading=False)
    pl.add_mesh(placed("neck_top_a_v8"), color="#c7b49f", smooth_shading=False)
    pl.add_mesh(placed("neck_top_b_v8"), color="#cfbfa8", smooth_shading=False)
    pl.add_mesh(placed("carriage_v8"), color="#4fae8a", smooth_shading=False)
    if ghost_car:
        g = meshes["carriage_v8"].copy()
        g.apply_translation([0, TRAVEL, 0])
        pl.add_mesh(pv.wrap(g), color="#4fae8a", opacity=0.3, smooth_shading=False)
    pl.add_mesh(placed("drum_v8", MOT_X, 0, 1.7), color="#8a7fd4", smooth_shading=False)
    pl.add_mesh(placed("roller_corner_v8", *ROLL_A, 1.2), color="#d4a24f", smooth_shading=False)
    pl.add_mesh(placed("roller_corner_v8", *ROLL_B, 1.2), color="#d4a24f", smooth_shading=False)
    for s in (-1, 1):
        pl.add_mesh(placed("roller_guide_v8", GUIDE_X, s * GUIDE_Y, 0.1),
                    color="#d4a24f", smooth_shading=False)
    add_cables(pl)
    pl.set_background("white")


pl = pv.Plotter(off_screen=True, window_size=(1600, 1000))
scene(pl)
pl.camera_position = "iso"
pl.camera.zoom(1.3)
pl.screenshot(rf"{OUT}\_v8_asm_iso.png")

pl = pv.Plotter(off_screen=True, window_size=(1600, 1000))
scene(pl)
pl.camera_position = "xy"
pl.camera.zoom(1.35)
pl.screenshot(rf"{OUT}\_v8_asm_top.png")

# слой L1 без крышки: видно каналы, дорожки, ролики, тросы
pl = pv.Plotter(off_screen=True, window_size=(1500, 1000))
pl.add_mesh(placed("neck_base_v8"), color="#b09b82", smooth_shading=False)
pl.add_mesh(placed("carriage_v8"), color="#4fae8a", smooth_shading=False, opacity=0.5)
pl.add_mesh(placed("roller_corner_v8", *ROLL_A, 1.2), color="#d4a24f", smooth_shading=False)
pl.add_mesh(placed("roller_corner_v8", *ROLL_B, 1.2), color="#d4a24f", smooth_shading=False)
add_cables(pl)
pl.set_background("white")
pl.camera_position = [(90, -60, 80), (45, 0, 5), (0, 0, 1)]
pl.screenshot(rf"{OUT}\_v8_layer1_closeup.png")

# сетка деталей
pl = pv.Plotter(off_screen=True, shape=(3, 3), window_size=(1800, 1400))
grid = [("neck_base_v8", "L1 base"), ("neck_top_a_v8", "L2 top A"), ("neck_top_b_v8", "L2 top B"),
        ("carriage_v8", "carriage"), ("deck_v8", "deck"), ("drum_v8", "drum"),
        ("roller_corner_v8", "roller corner x2"), ("roller_guide_v8", "roller guide x2"),
        ("_mock_nema14", "NEMA14 mock")]
for i, (name, title) in enumerate(grid):
    pl.subplot(i // 3, i % 3)
    pl.add_mesh(pv.wrap(meshes[name]), color="#c7b49f", smooth_shading=False)
    pl.add_text(title, font_size=11)
    pl.set_background("white")
    pl.camera_position = "iso"
pl.screenshot(rf"{OUT}\_v8_parts.png")
print("renders done")
