# Полноразмерная компоновка v2: конец грифа (как palka3: ширина 57, толщина 25)
# с зоной 4 дорожек в 2 этажа, узкие ленты 7мм, крышка приподнята (разнесённый вид).
import FreeCAD
from FreeCAD import Vector
import Part, math

doc = FreeCAD.newDocument("Trainer_layout_v2")
def add(n, s):
    o = doc.addObject("Part::Feature", n); o.Shape = s; return o
def box(x, y, z, px, py, pz): return Part.makeBox(x, y, z, Vector(px, py, pz))
def cyl(r, h, px, py, pz): return Part.makeCylinder(r, h, Vector(px, py, pz))

HW = 28.5            # полуширина грифа (57)
X0, X1 = 440.0, 600.0
Z_LOW, Z_HIGH = 3.5, 12.8   # низ ленты этажей
BH = 7.0             # ширина(высота) ленты
R_ER = 4.0           # концевой ролик
R_CR = 3.0           # угловой
R_PIN = 8.3
lanes_x = [527.0, 544.0, 561.0, 578.0]
lane_layer = [Z_LOW, Z_HIGH, Z_LOW, Z_HIGH]
lane_side = [-1, -1, +1, +1]          # 1,2 -> левый борт (y-), 3,4 -> правый (y+)
CH_Y1, CH_Y2 = 23.5, 25.7             # каналы вдоль грифа (абс. значения y)

# --- корпус: дно, борта, межэтажная полка, крышка (приподнята) ---
base = box(X1 - X0, 2 * HW, 3, X0, -HW, 0)
wallL = box(X1 - X0, 1.6, 17, X0, -HW, 3)
wallR = box(X1 - X0, 1.6, 17, X0, HW - 1.6, 3)
neck = base.fuse([wallL, wallR])
add("Neck_base", neck.removeSplitter())

shelf = box(X1 - X0, 2 * HW - 3.2, 1.6, X0, -HW + 1.6, 10.6)
for i, lx in enumerate(lanes_x):
    if lane_layer[i] == Z_LOW:        # щели в полке для ножек нижних тележек
        shelf = shelf.cut(box(3.4, 42, 4, lx - 6.05, -21, 10))
add("Shelf_midfloor", shelf.removeSplitter())

LIFT = 26.0                            # крышка приподнята для обзора
cover = box(X1 - X0, 2 * HW, 2.2, X0, -HW, 20 + LIFT)
for i, lx in enumerate(lanes_x):
    cover = cover.cut(box(3.4, 38, 4, lx - 6.05, -19, 19 + LIFT))
add("Cover_lifted", cover.removeSplitter())

# --- дорожки ---
for i, lx in enumerate(lanes_x):
    z = lane_layer[i]
    s = lane_side[i]
    x1, x2 = lx - 4.35, lx + 4.35     # передняя/задняя ветки поперёк
    y_er = -s * 20.5                   # конец с петлёй — противоположен выходу
    y_cr = s * 20.5
    add(f"EndRoll{i+1}", cyl(R_ER, BH + 2, lx, y_er, z - 1))
    add(f"Corner{i+1}a", cyl(R_CR, BH + 2, x1 + 3, y_cr, z - 1))
    add(f"Corner{i+1}b", cyl(R_CR, BH + 2, x2 + 3, s * (20.5 + 2.2), z - 1))

    segs = []
    def strip(xa, ya, xb, yb):
        dx, dy = xb - xa, yb - ya
        L = math.hypot(dx, dy)
        b = box(L, 0.7, BH, 0, -0.35, 0)
        b.rotate(Vector(0, 0, 0), Vector(0, 0, 1), math.degrees(math.atan2(dy, dx)))
        b.translate(Vector(xa, ya, z))
        return b
    segs.append(strip(x1, y_er, x1, y_cr))                      # поперёк
    segs.append(strip(x2, y_er, x2, s * (20.5 + 2.2)))
    # полукольцо на концевом ролике
    ring = cyl(R_ER + 0.7, BH, lx, y_er, z).cut(cyl(R_ER + 0.02, BH + 1, lx, y_er, z - 0.5))
    segs.append(ring)
    # вдоль грифа к деке
    ya_ch, yb_ch = s * CH_Y1, s * CH_Y2
    segs.append(strip(x1 + 3, ya_ch, 604, ya_ch))
    segs.append(strip(x2 + 3, yb_ch, 604, yb_ch))
    add(f"Belt{i+1}", Part.makeCompound(segs))

    # тележка на приподнятой крышке (ножка вниз в щель)
    car = box(16, 14, 5, lx - 8, -7, 22.2 + LIFT)
    rimc = box(16, 14, 1.6, lx - 8, -7, 27.2 + LIFT).cut(box(13.2, 11.2, 3, lx - 6.6, -5.6, 27.1 + LIFT))
    stem = box(3.0, 12, 22.5 - z - BH + LIFT + 0.2, lx - 5.85, -6, z + BH - 0.3 + LIFT * 0)
    # ножка рисуется от ленты вверх до крышки (без LIFT неразрывно; для вида - до низа поднятой тележки)
    stem = box(3.0, 12, 5, lx - 5.85, -6, z + BH - 0.3)
    add(f"Carriage{i+1}", car.fuse(rimc).removeSplitter())
    add(f"Stem{i+1}", stem)

# --- дека: начало + 4 мотора ---
add("Deka_start", box(160, 150, 3, 600, -75, 0))
mot = {0: (640, -30), 1: (700, -30), 2: (640, 30), 3: (700, 30)}
for i in range(4):
    mx, my = mot[i]
    z = lane_layer[i]
    add(f"Motor{i+1}", cyl(18, 15, mx, my, -15.5).fuse(cyl(R_PIN, BH + 4, mx, my, z - 1)))

doc.recompute()
doc.saveAs(r"C:\App\gitar\Trainer_layout_v2.FCStd")
print("objects:", len(doc.Objects))
