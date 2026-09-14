# -*- coding: utf-8 -*-
"""ГИТАРА: СТЕНД ДАТЧИКА ПОЛОЖЕНИЯ — проверка гипотезы «49E видит ход ленты» до деки.

Две детали:
  * основание: пол, две направляющие, упоры по концам, встроенная стойка с карманом
    под 49E — та же геометрия, что у стойки в деке (магнит на ленте X=+2 от её оси,
    датчик на X 4.8..9 от оси ленты, центр датчика на высоте центра магнита, датчик
    сдвинут вдоль хода на +R_CR+0.5 от среднего положения магнита), шкала 0..10 мм;
  * палка: кусок ленты 8×1.6 длиной 50 с карманом под магнит Ø4×1.5 сверху, ручкой
    для пальца на южном конце и стрелкой-указателем на шкалу.
Палка ходит между упорами ровно на 2·R_CR = 9.6 мм, как лента в деке.

Запуск: .venv-b123d\\Scripts\\python gitara_hall_stend.py
  -> Print/Print/hall_stend_base_v1.stl, hall_stend_bar_v1.stl
"""
import os
from build123d import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "Print", "Print")

R_CR = 4.8                      # ход ленты в деке ±R_CR
TRAVEL = 2 * R_CR               # 9.6
BAND_W, BAND_T = 8.0, 1.6
BAR_L = 50.0
MAG_D, MAG_H = 4.0, 1.5
MAG_X = 2.0                     # магнит на ленте: +2 от оси (в деке X=12 при оси 10)
SENS_W, SENS_L, SENS_T = 3.0, 4.0, 1.5
POST_X0, POST_X1 = 4.8, 9.0     # стойка: как в деке (14.8..19 при оси 10)
POST_HY = 4.0
CLR = 0.3                       # зазор палки в направляющих
FLOOR = 2.0
RAIL_H = 2.6                    # направляющие чуть ниже верха ленты + магнит не задевают


def BB(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(
        abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))


# ---------- палка (координаты: ось ленты X=0, Y от 0 до BAR_L, низ Z=0) ----------
MAG_Y_BAR = 25.0                                    # магнит посередине палки
bar = BB(-BAND_W / 2, BAND_W / 2, 0, BAR_L, 0, BAND_T)
bar -= Pos(MAG_X, MAG_Y_BAR, BAND_T - 0.5) * Cylinder(MAG_D / 2 + 0.1, 1.2)   # карман 1.0 глубиной: магнит торчит на 0.5 + клей
bar += BB(-BAND_W / 2, BAND_W / 2, 0, 6, 0, 6.0)                              # ручка для пальца (южный конец)
bar += BB(-BAND_W / 2 - 2.0, -BAND_W / 2, BAR_L - 3, BAR_L, 0, 1.0)            # стрелка-указатель на шкалу (север, запад)

# ---------- основание ----------
# палка в среднем положении: Y от Y0 до Y0+BAR_L; ход ±R_CR → канал длиной BAR_L + TRAVEL
Y0 = 12.0 + R_CR                                    # южный торец палки в среднем положении
CH_Y0, CH_Y1 = Y0 - R_CR, Y0 + BAR_L + R_CR          # канал между упорами
BASE_X0, BASE_X1 = -14.0, 16.0
BASE_Y0, BASE_Y1 = CH_Y0 - 4.0, CH_Y1 + 4.0
base = BB(BASE_X0, BASE_X1, BASE_Y0, BASE_Y1, 0, FLOOR)
# направляющие: запад сплошная, восток с разрывом под стойку
base += BB(-BAND_W / 2 - CLR - 2.0, -BAND_W / 2 - CLR, CH_Y0, CH_Y1, FLOOR, FLOOR + RAIL_H)
MAG_Y0 = Y0 + MAG_Y_BAR                              # магнит в среднем положении (мир)
SENS_Y = MAG_Y0 + R_CR + 0.5                         # датчик, как в деке
east_rail = BB(BAND_W / 2 + CLR, BAND_W / 2 + CLR + 2.0, CH_Y0, CH_Y1, FLOOR, FLOOR + RAIL_H)
east_rail -= BB(BAND_W / 2, POST_X1 + 1, SENS_Y - POST_HY - 1.5, SENS_Y + POST_HY + 1.5, FLOOR - 0.1, FLOOR + RAIL_H + 0.1)
base += east_rail
# упоры по концам канала (стенки во всю ширину палки, выше ручки не надо — палка упирается торцом)
base += BB(-BAND_W / 2 - CLR - 2.0, BAND_W / 2 + CLR + 2.0, CH_Y0 - 3.0, CH_Y0, FLOOR, FLOOR + RAIL_H)
base += BB(-BAND_W / 2 - CLR - 2.0, BAND_W / 2 + CLR + 2.0, CH_Y1, CH_Y1 + 3.0, FLOOR, FLOOR + RAIL_H)
# стойка датчика: центр датчика на высоте центра магнита
MAG_Z0 = 0.5                                          # низ магнита над низом палки (карман 1.1 от верха)
mag_zc = FLOOR + MAG_Z0 + MAG_H / 2                   # центр магнита в мире (3.25)
top = mag_zc + SENS_T / 2
post = BB(POST_X0, POST_X1, SENS_Y - POST_HY, SENS_Y + POST_HY, FLOOR, top)
xc = (POST_X0 + POST_X1) / 2
post -= BB(xc - SENS_W / 2 - 0.1, xc + SENS_W / 2 + 0.1, SENS_Y - SENS_L / 2 - 0.1, SENS_Y + SENS_L / 2 + 0.1,
           top - SENS_T - 0.1, top + 0.1)                                    # карман под 49E плашмя
post -= BB(xc, POST_X1 + 0.1, SENS_Y - 2.0, SENS_Y + 2.0, top - SENS_T - 0.1, top + 0.1)   # щель под ножки на восток
base += post
base -= BB(POST_X1 - 1.2, BASE_X1 + 0.1, SENS_Y - 1.2, SENS_Y + 1.2, FLOOR - 1.0, top + 0.1)  # канавка проводов: по грани вниз и по полу к краю
# шкала 0..10 мм у западного рельса напротив стрелки палки: риска каждый мм, длинная каждые 5
for i in range(11):
    y = (Y0 - R_CR) + BAR_L - 1.5 + i                # стрелка палки на BAR_L-1.5 от её торца; нулевая риска = южный упор
    ln = 3.0 if i % 5 == 0 else 1.6
    base -= BB(-BAND_W / 2 - CLR - 2.0 - ln, -BAND_W / 2 - CLR - 2.0, y - 0.2, y + 0.2, FLOOR - 0.5, FLOOR + 0.1)
# подписи-точки: 0 и 10 (глухие лунки)
for i in (0, 10):
    y = (Y0 - R_CR) + BAR_L - 1.5 + i
    base -= Pos(-BAND_W / 2 - CLR - 2.0 - 4.5, y, FLOOR) * Cylinder(0.8 if i == 0 else 1.2, 1.0)

for name, part in (("hall_stend_base_v1", base), ("hall_stend_bar_v1", bar)):
    p = Part() + part
    export_stl(p, os.path.join(OUT, name + ".stl"))
    bb = p.bounding_box()
    print(f"{name}: volume={p.volume:.0f} mm3, solids={len(p.solids())}, "
          f"габарит {bb.size.X:.1f}×{bb.size.Y:.1f}×{bb.size.Z:.1f}")
print(f"ход палки {TRAVEL} мм; магнит в среднем положении Y={MAG_Y0:.1f}, датчик Y={SENS_Y:.1f} (сдвиг {R_CR + 0.5})")
print("export done")
