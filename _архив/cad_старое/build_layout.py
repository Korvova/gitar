# Полная плоская схема тренажёра: 4 дорожки поперёк грифа + 4 мотора в деке,
# ленты-петли с разводкой каналами вдоль грифа (2 дорожки выходят влево, 2 вправо).
# Блочная компоновка для утверждения. Размеры реальные.
import FreeCAD
from FreeCAD import Vector
import Part, math

doc = FreeCAD.newDocument("Trainer_layout")
def add(n, s):
    o = doc.addObject("Part::Feature", n); o.Shape = s; return o
def box(x, y, z, px, py, pz): return Part.makeBox(x, y, z, Vector(px, py, pz))
def cyl(r, h, px, py, pz): return Part.makeCylinder(r, h, Vector(px, py, pz))

R_PIN = 8.3        # шестерня ленты на моторе
R_ROLL = 4.0       # концевые и угловые ролики
LANE_P = 17.0      # шаг дорожек
TRAVEL_X0, TRAVEL_X1 = 5.0, 55.0
BELT_H = 15.0
Z0 = 2.0           # низ ленты над плитой

# --- плиты: гриф + дека ---
add("Plate_grif", box(96, 130, 2, -18, 0, 0))     # x -18..78 (каналы по бокам), y 0..130
add("Plate_deka", box(140, 120, 2, -40, 130, 0))

lanes_y = [30 + i * LANE_P for i in range(4)]     # 30,47,64,81
# выходы: дорожки 0,1 -> влево (x<0), 2,3 -> вправо (x>60)
side = [-1, -1, +1, +1]
chan_x = {0: (-6.0, -12.0), 1: (-3.0, -15.0), 2: (66.0, 72.0), 3: (63.0, 75.0)}
motors = {0: (-20.0, 165.0), 1: (-2.0, 200.0), 2: (80.0, 165.0), 3: (62.0, 200.0)}

report = []
for i, y0 in enumerate(lanes_y):
    ya = y0 + 3.0            # передняя ветка поперёк
    yb = y0 + 3.0 + 2 * R_ROLL + 0.7   # задняя ветка (вокруг концевого ролика)
    s = side[i]
    xe = TRAVEL_X0 - 2 if s > 0 else TRAVEL_X1 + 2   # конец с петлёй (противоположен выходу)
    x_exit = 60.0 if s > 0 else 0.0
    xa, xb = chan_x[i]
    mx, my = motors[i]

    # дорожка: рельс + тележка (блоки)
    add(f"Rail{i+1}", box(58, 2, 2, 1, y0 + 12, 20))
    add(f"Carriage{i+1}", box(16, 14, 6, 20 + i * 5, y0 + 1, 17))
    # концевой ролик
    add(f"EndRoll{i+1}", cyl(R_ROLL, BELT_H + 2, xe, (ya + yb) / 2, Z0))
    # угловые ролики у выхода
    add(f"Corner{i+1}a", cyl(R_ROLL, BELT_H + 2, xa + s * 0, ya, Z0))
    add(f"Corner{i+1}b", cyl(R_ROLL, BELT_H + 2, xb + s * 0, yb, Z0))
    # мотор с шестернёй
    add(f"Motor{i+1}", cyl(18, 15, mx, my, -17).fuse(cyl(R_PIN, 13, mx, my, Z0)))

    # лента: сегменты-полосы (визуально)
    segs = []
    def strip(x1, y1, x2, y2):
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy)
        b = box(L, 0.7, BELT_H, 0, -0.35, 0)
        b.rotate(Vector(0, 0, 0), Vector(0, 0, 1), math.degrees(math.atan2(dy, dx)))
        b.translate(Vector(x1, y1, Z0))
        return b
    segs.append(strip(xa, ya, xe, ya))            # поперёк, передняя
    segs.append(strip(xe, yb, xb, yb))            # поперёк, задняя
    segs.append(strip(xa, ya, xa, my - 10))       # вдоль грифа к деке
    segs.append(strip(xb, yb, xb, my - 10))
    segs.append(strip(xa, my - 10, mx, my))       # подводка к шестерне (усл.)
    segs.append(strip(xb, my - 10, mx, my))
    add(f"Belt{i+1}", Part.makeCompound(segs))

    # длина петли (прикидка): 2 поперёк + 2 вдоль + обороты
    run_cross = abs(xe - xa) + abs(xe - xb)
    run_along = 2 * (my - ya - 10) + 25
    per = run_cross + run_along + math.pi * (R_PIN + R_ROLL) + 4 * (math.pi / 2) * R_ROLL
    n_teeth = round(per / 4.347)
    report.append((i + 1, round(per), n_teeth, round(n_teeth * 4.347, 1)))

doc.recompute()
doc.saveAs(r"C:\App\gitar\Trainer_layout.FCStd")
print("lane | perimeter~ | teeth | belt len")
for r in report:
    print(f"  {r[0]}  |   {r[1]} mm  |  {r[2]}  | {r[3]} mm")
print("saved layout")
