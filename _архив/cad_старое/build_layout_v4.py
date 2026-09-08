# v4: бесконфликтная разводка. Этаж LOW: дорожки 1(x55) и 3(x89) выходят на ПРАВЫЙ борт
# 4 параллельными слотами; их петлевые ролики - на левом. Этаж HIGH (2:x72, 4:x106) - зеркально.
# Углы - честные четверть-обхваты роликов, на моторе - разводчик + полуобхват шестерни.
import FreeCAD
from FreeCAD import Vector
import Part, math

doc = FreeCAD.newDocument("Trainer_layout_v4")
def add(n, s):
    o = doc.addObject("Part::Feature", n); o.Shape = s; return o
def box(x, y, z, px, py, pz): return Part.makeBox(x, y, z, Vector(px, py, pz))
def cyl(r, h, px, py, pz): return Part.makeCylinder(r, h, Vector(px, py, pz))
def ring(cx, cy, z, r_in, r_out, a0, a1, h):
    s = Part.makeCylinder(r_out, h, Vector(cx, cy, z), Vector(0, 0, 1), a1 - a0)
    s = s.cut(Part.makeCylinder(r_in, h + 1, Vector(cx, cy, z - 0.5)))
    s.rotate(Vector(cx, cy, 0), Vector(0, 0, 1), a0)
    return s

NECK_L = 600.0
def hw(x): return 23.85 + (x / NECK_L) * 4.65

Z_LOW, Z_HIGH = 3.5, 12.8
BH = 7.0
R_ER, R_CR, R_PIN = 3.5, 3.0, 8.3
SLOTS = [18.0, 19.3, 20.6, 21.9]     # |y| слотов канала

# дорожки: (x, этаж, борт выхода s, слоты (inner_i))
lanes = [
    dict(x=55.0,  z=Z_LOW,  s=+1, slots=(20.6, 21.9)),  # дальняя от деки - внешние слоты
    dict(x=72.0,  z=Z_HIGH, s=-1, slots=(20.6, 21.9)),
    dict(x=89.0,  z=Z_LOW,  s=+1, slots=(18.0, 19.3)),  # ближняя - внутренние
    dict(x=106.0, z=Z_HIGH, s=-1, slots=(18.0, 19.3)),
]
mot = {0: (665.0, +1), 1: (665.0, -1), 2: (725.0, +1), 3: (725.0, -1)}

# --- корпус ---
def plate(x0, x1, z0, t):
    pts = [Vector(x0, -hw(x0), z0), Vector(x1, -hw(x1), z0),
           Vector(x1, hw(x1), z0), Vector(x0, hw(x0), z0)]
    return Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(Vector(0, 0, t))
neck = plate(20, NECK_L, 0, 3)
for sgn in (-1, 1):
    p0 = Vector(20, sgn * hw(20), 0); p1 = Vector(NECK_L, sgn * hw(NECK_L), 0)
    d = p1 - p0
    wall = box(d.Length, 1.6, 17, 0, -1.6 if sgn > 0 else 0, 3)
    wall.rotate(Vector(0, 0, 0), Vector(0, 0, 1), math.degrees(math.atan2(d.y, d.x)))
    wall.translate(p0)
    neck = neck.fuse(wall)
add("Neck_base", neck.removeSplitter())

LIFT = 30.0
cover = plate(20, NECK_L, 20 + LIFT, 2.2)
for ln in lanes:
    cover = cover.cut(box(3.6, 40, 4, ln["x"] - 7.5, -20, 19 + LIFT))
add("Cover_lifted", cover.removeSplitter())
add("Deka_start", box(220, 300, 3, NECK_L, -150, 0))

for i, ln in enumerate(lanes):
    lx, z, s = ln["x"], ln["z"], ln["s"]
    y_in, y_out = ln["slots"]                  # приходящие слоты (|y|)
    xa = lx - (R_ER + 0.35)                    # ветка A (клемма тележки)
    xb = lx + (R_ER + 0.35)                    # ветка B
    y_er = -s * (hw(lx) - 1.6 - R_ER - 1.0)   # петля на противоположном борту
    mx, ms = mot[i]
    my_near = s * (y_in + R_PIN)               # центр шестерни: слот y_in - касательная

    segs = []
    def strip(p, q):
        d = (q[0] - p[0], q[1] - p[1])
        L = math.hypot(*d)
        b = box(L, 0.7, BH, 0, -0.35, 0)
        b.rotate(Vector(0, 0, 0), Vector(0, 0, 1), math.degrees(math.atan2(d[1], d[0])))
        b.translate(Vector(p[0], p[1], z))
        return b
    # петля ER (полуобхват со стороны борта)
    a0 = 90 if s > 0 else -90
    segs.append(ring(lx, y_er, z, R_ER, R_ER + 0.7, a0, a0 + 180, BH))
    add(f"EndRoll{i+1}", cyl(R_ER, BH + 2, lx, y_er, z - 1))
    # поперечные ветки: от ER до углов
    yca = s * (y_in - R_CR)                    # конец прямой ветки A перед углом
    ycb = s * (y_out - R_CR)
    segs.append(strip((xa, y_er), (xa, yca)))
    segs.append(strip((xb, y_er), (xb, ycb)))
    # углы (четверть-обхваты): центр (x+R, yc), поворот на +x
    for (xx, yc, y_sl) in [(xa, yca, s * y_in), (xb, ycb, s * y_out)]:
        cx, cy = xx + R_CR, yc
        aa = 90 if s > 0 else 180
        segs.append(ring(cx, cy, z, R_CR, R_CR + 0.7, 90 if s > 0 else -180, 180 if s > 0 else -90, BH))
        add(f"Corner{i+1}{'a' if xx == xa else 'b'}", cyl(R_CR, BH + 2, cx, cy, z - 1))
    # вдоль грифа
    x_sp = mx - 55
    segs.append(strip((xa + R_CR, s * y_in), (mx, s * y_in)))          # слот A прямо в касательную
    segs.append(strip((xb + R_CR, s * y_out), (x_sp, s * y_out)))      # слот B до разводчика
    # разводчик: подъём B на дальнюю касательную (y_in + 2R_PIN)
    y_far = s * (y_in + 2 * R_PIN)
    add(f"Spread{i+1}", cyl(R_CR, BH + 2, x_sp + 2, s * (y_out + 2), z - 1))
    segs.append(strip((x_sp, s * y_out), (x_sp + 14, y_far)))
    segs.append(strip((x_sp + 14, y_far), (mx, y_far)))
    # шестерня: полуобхват дальней стороной
    segs.append(ring(mx, my_near, z, R_PIN, R_PIN + 0.7, -90 if s > 0 else 90, 90 if s > 0 else 270, BH))
    add(f"Belt{i+1}", Part.makeCompound(segs))
    add(f"Motor{i+1}", cyl(18, 15, mx, my_near, -15.5).fuse(cyl(R_PIN, BH + 4, mx, my_near, z - 1)))

    # тележка + ножка на ветке A
    car = box(16, 14, 5, lx - 8, -7, 22.2 + LIFT)
    rimc = box(16, 14, 1.6, lx - 8, -7, 27.2 + LIFT).cut(
        box(13.2, 11.2, 3, lx - 6.6, -5.6, 27.1 + LIFT))
    add(f"Carriage{i+1}", car.fuse(rimc).removeSplitter())
    add(f"Stem{i+1}", box(2.6, 10, 20 - (z + BH) + 0.8, xa - 3.35, -5, z + BH - 0.8))

    trav = abs(y_er) + y_in - R_ER - R_CR - 4
    per = 2 * (abs(s * y_in - y_er)) + 2 * (mx - lx) + math.pi * (R_ER + R_PIN) + 40
    print(f"lane{i+1}: ход ~{trav:.0f} мм, петля ~{per:.0f} мм ({round(per/4.347)} зуб.)")

doc.recompute()
doc.saveAs(r"C:\App\gitar\Trainer_layout_v4.FCStd")
print("objects:", len(doc.Objects))
