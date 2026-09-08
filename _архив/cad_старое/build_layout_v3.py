# Компоновка v3: зона дорожек у ПЕРВЫХ ладов (голова грифа), ленты дотянуты
# до шестерён моторов в деке (с роликом-разводчиком), сужение грифа учтено.
import FreeCAD
from FreeCAD import Vector
import Part, math

doc = FreeCAD.newDocument("Trainer_layout_v3")
def add(n, s):
    o = doc.addObject("Part::Feature", n); o.Shape = s; return o
def box(x, y, z, px, py, pz): return Part.makeBox(x, y, z, Vector(px, py, pz))
def cyl(r, h, px, py, pz): return Part.makeCylinder(r, h, Vector(px, py, pz))

NECK_L = 600.0
def hw(x):                      # полуширина грифа с конусностью 47.7 -> 57
    return 23.85 + (x / NECK_L) * 4.65

Z_LOW, Z_HIGH = 3.5, 12.8
BH = 7.0
R_ER, R_CR, R_PIN = 3.5, 3.0, 8.3
lanes_x = [55.0, 72.0, 89.0, 106.0]         # первые лады
lane_layer = [Z_LOW, Z_HIGH, Z_LOW, Z_HIGH]
lane_side = [-1, -1, +1, +1]
CH1, CH2 = 20.6, 22.8                        # каналы (по модулю y), впритык к узкому месту

# --- корпус грифа (клин по ширине) ---
sec = []
for x0, x1 in [(20, NECK_L)]:
    pts = [Vector(x0, -hw(x0), 0), Vector(x1, -hw(x1), 0),
           Vector(x1, hw(x1), 0), Vector(x0, hw(x0), 0)]
    f = Part.Face(Part.makePolygon(pts + [pts[0]]))
    sec.append(f.extrude(Vector(0, 0, 3)))
neck = sec[0]
# борта
for s in (-1, 1):
    pts = [Vector(20, s*hw(20), 0), Vector(NECK_L, s*hw(NECK_L), 0)]
    w = box(NECK_L - 20, 1.6, 17, 20, 0, 3)
    # наклонная стенка: построим как loft узкой полосы вдоль борта
    p0, p1 = pts
    d = p1 - p0
    ang = math.degrees(math.atan2(d.y, d.x))
    L = d.Length
    wall = box(L, 1.6, 17, 0, -1.6 if s > 0 else 0, 3)
    wall.rotate(Vector(0, 0, 0), Vector(0, 0, 1), ang)
    wall.translate(p0)
    neck = neck.fuse(wall)
add("Neck_base", neck.removeSplitter())

LIFT = 30.0
cover_pts = [Vector(20, -hw(20), 0), Vector(NECK_L, -hw(NECK_L), 0),
             Vector(NECK_L, hw(NECK_L), 0), Vector(20, hw(20), 0)]
cover = Part.Face(Part.makePolygon(cover_pts + [cover_pts[0]])).extrude(Vector(0, 0, 2.2))
cover.translate(Vector(0, 0, 20 + LIFT))
for i, lx in enumerate(lanes_x):
    cover = cover.cut(box(3.6, 40, 4, lx - 6.2, -20, 19 + LIFT))
add("Cover_lifted", cover.removeSplitter())

# --- дека (контур упрощённо, реальная ширина) ---
add("Deka_start", box(220, 300, 3, NECK_L, -150, 0))

mot = {0: (660, -32.0), 1: (720, -32.0), 2: (660, 32.0), 3: (720, 32.0)}

for i, lx in enumerate(lanes_x):
    z = lane_layer[i]
    s = lane_side[i]
    x1, x2 = lx - 3.9, lx + 3.9          # ветки поперёк (вокруг ER r3.5+0.35)
    W = hw(lx) - 2.6                      # внутренняя полуширина в зоне
    y_er = -s * (W - 4)                   # конец с петлёй
    add(f"EndRoll{i+1}", cyl(R_ER, BH + 2, lx, y_er, z - 1))
    # угловые: ветка1 -> канал CH1, ветка2 -> канал CH2
    add(f"Corner{i+1}a", cyl(R_CR, BH + 2, x1 + R_CR, s * (CH1 - R_CR), z - 1))
    add(f"Corner{i+1}b", cyl(R_CR, BH + 2, x2 + R_CR, s * (CH2 - R_CR), z - 1))

    mx, my = mot[i]
    segs = []
    def strip(xa, ya, xb, yb):
        dx, dy = xb - xa, yb - ya
        L = math.hypot(dx, dy)
        b = box(L, 0.7, BH, 0, -0.35, 0)
        b.rotate(Vector(0, 0, 0), Vector(0, 0, 1), math.degrees(math.atan2(dy, dx)))
        b.translate(Vector(xa, ya, z))
        return b
    # поперёк зоны
    segs.append(strip(x1, y_er, x1, s * (CH1 - R_CR)))
    segs.append(strip(x2, y_er, x2, s * (CH2 - R_CR)))
    # полукольцо на ER
    segs.append(cyl(R_ER + 0.7, BH, lx, y_er, z).cut(cyl(R_ER + 0.02, BH + 1, lx, y_er, z - 0.5)))
    # вдоль грифа
    segs.append(strip(x1 + R_CR, s * CH1, mx - 45, s * CH1))
    segs.append(strip(x2 + R_CR, s * CH2, mx - 45, s * CH2))
    # разводчик: ветка CH1 идёт прямо на ближнюю касательную шестерни (y = my - s*8.3... )
    y_t1 = my - s * (abs(my) - CH1)  # = s*CH1 -> касание снизу: центр шестерни на s*(CH1+8.3)
    # ставим шестерню так, чтобы ветка CH1 была касательной:
    # центр my = s*(CH1 + R_PIN); вторая касательная на s*(CH1 + 2R_PIN)
    my_c = s * (CH1 + R_PIN)
    y_far = s * (CH1 + 2 * R_PIN)
    add(f"Spread{i+1}", cyl(R_CR, BH + 2, mx - 42, s * (CH2 + 2.5), z - 1))
    segs.append(strip(mx - 45, s * CH1, mx, s * CH1))                    # касательная 1
    segs.append(strip(mx - 45, s * CH2, mx - 39, s * (CH2 + 4.5)))       # через разводчик
    segs.append(strip(mx - 39, s * (CH2 + 4.5), mx, y_far))              # к дальней касательной
    # кольцо на шестерне
    segs.append(cyl(R_PIN + 0.7, BH, mx, my_c, z).cut(cyl(R_PIN + 0.02, BH + 1, mx, my_c, z - 0.5)))
    add(f"Belt{i+1}", Part.makeCompound(segs))

    add(f"Motor{i+1}", cyl(18, 15, mx, my_c, -15.5).fuse(cyl(R_PIN, BH + 4, mx, my_c, z - 1)))

    # тележка на поднятой крышке + ножка на ленте (ветка x1)
    car = box(16, 14, 5, lx - 8, -7, 22.2 + LIFT)
    rimc = box(16, 14, 1.6, lx - 8, -7, 27.2 + LIFT).cut(
        box(13.2, 11.2, 3, lx - 6.6, -5.6, 27.1 + LIFT))
    add(f"Carriage{i+1}", car.fuse(rimc).removeSplitter())
    add(f"Stem{i+1}", box(2.6, 10, 20 - (z + BH) + 0.8, x1 - 3.4, -5, z + BH - 0.8))

    per = (2 * abs(y_er - s * CH1) + 2 * (mx - lx) + math.pi * (R_ER + R_PIN) + 60)
    print(f"lane{i+1}: петля ~{per:.0f} мм, зубьев ~{round(per/4.347)}")

doc.recompute()
doc.saveAs(r"C:\App\gitar\Trainer_layout_v3.FCStd")
print("objects:", len(doc.Objects))
