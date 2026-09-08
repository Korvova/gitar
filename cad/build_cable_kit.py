# ФИНАЛ v2: нитяные дорожки, этажи нитей по ВЫСОТЕ (3.3/4.3/5.3/6.3),
# ролики Ø4 на M2 вплотную к бортам (у всех дорожек одинаковый размах),
# перекрёстное крепление, ход ~43. Гриф 58, зона у первых ладов.
import FreeCAD
from FreeCAD import Vector
import Part, MeshPart, Mesh, math, os

OUT = r"C:\App\gitar"
doc = FreeCAD.newDocument("Cable_kit")
def add(n, s):
    o = doc.addObject("Part::Feature", n); o.Shape = s; return o
def box(x, y, z, px, py, pz): return Part.makeBox(x, y, z, Vector(px, py, pz))
def cyl(r, h, px, py, pz): return Part.makeCylinder(r, h, Vector(px, py, pz))

W = 58.0; HW = W / 2
NECK_L = 600.0
lanes_x = [55.0, 72.0, 89.0, 106.0]
# ближняя к деке дорожка - НИЖНИЙ этаж, дальняя - верхний (нити проходят НАД чужими роликами);
# шаг 1.4 = ролик 2.2 + зазор 0.3 над ребордой
CAB_LEVELS = [7.5, 6.1, 4.7, 3.3]
mot = {0: (645.0, -1), 1: (645.0, +1), 2: (705.0, -1), 3: (705.0, +1)}
R_ROLL = 2.0                     # ролик Ø4, ось M2
GY = HW - 1.5                    # линия нитей в 0.3 от стенки борта (27.5)
BASE_T = 2.0
COV0, COV1 = 10.6, 12.6          # крышка выше: ролик верхней дорожки + шляпка M2 = 10.2

# ---------- корпус ----------
body = box(NECK_L - 20, W, BASE_T, 20, -HW, 0)
for s in (+1, -1):
    body = body.fuse(box(NECK_L - 20, 1.2, COV0, 20, s * HW - (1.2 if s > 0 else 0), 0))
    # жёлоб нитей: одна внутренняя стенка, нити стопкой между ней и бортом (канал 1.8)
    body = body.fuse(box(NECK_L - 150, 0.8, 6.6, 130, s * (HW - 2.6) - (0.8 if s > 0 else 0), BASE_T))
# стойки крышки по центру
for cx in (30, 130, 200, 300, 400, 500, 580):
    body = body.fuse(cyl(2.5, COV0, cx, 0, BASE_T))
    body = body.cut(cyl(0.85, 8, cx, 0, COV0 - 7))

# ---------- зона: ролики на этажных пьедесталах ----------
for i, lx in enumerate(lanes_x):
    z0 = CAB_LEVELS[i]
    for rs in (+1, -1):
        cy = rs * GY - rs * R_ROLL * 0 - rs * 0.0
        cy = rs * (GY - R_ROLL)          # центр: касательная вдоль борта на линии GY
        cx = lx + R_ROLL
        ped_h = z0 - 1.1 - BASE_T        # верх пьедестала: канавка ролика точно на своём этаже
        if ped_h > 0.15:
            body = body.fuse(cyl(2.6, ped_h, cx, cy, BASE_T))
        body = body.cut(cyl(0.85, 10, cx, cy, BASE_T - 1.5))                   # М2 самонарезом
cover = box(NECK_L - 21, W, COV1 - COV0, 21, -HW, COV0)
for i, lx in enumerate(lanes_x):
    cover = cover.cut(box(4.2, 48, 4, lx - 2.1, -24, COV0 - 1))
for cx in (30, 130, 200, 300, 400, 500, 580):     # отверстия под винты M2 в стойки
    cover = cover.cut(cyl(1.15, 4, cx, 0, COV0 - 1))
add("Cover", cover.removeSplitter())
add("Body", body.removeSplitter())

# ---------- лодочка: универсальная, ножка 3.0, 4 пары ушек ----------
stem = box(3.0, 8, COV1 + 0.6 - 2.7, -1.5, -4, 2.7)
plat = box(16, 14, 1.8, -8, -7, COV1 + 0.6)
rim = box(16, 14, 1.6, -8, -7, COV1 + 2.4).cut(box(13.2, 11.2, 3, -6.6, -5.6, COV1 + 2.3))
skid1 = box(16, 2, 0.8, -8, -7, COV1 - 0.2)
skid2 = box(16, 2, 0.8, -8, 5, COV1 - 0.2)
boat = stem.fuse([plat, rim, skid1, skid2])
for li, lz in enumerate(CAB_LEVELS):     # пары отверстий на каждом этаже
    for sy in (-2.2, 2.2):
        boat = boat.cut(Part.makeCylinder(0.7, 5, Vector(-2.5, sy, lz), Vector(1, 0, 0)))
add("Boat", boat.removeSplitter())

# ---------- ролик Ø4 (ось M2) ----------
roll = cyl(2.0, 0.6, 0, 0, 0)
roll = roll.fuse(cyl(1.5, 1.0, 0, 0, 0.6))
roll = roll.fuse(cyl(2.0, 0.6, 0, 0, 1.6))
roll = roll.cut(cyl(1.15, 4, 0, 0, -0.5))
add("Roller4", roll.removeSplitter())

# ---------- дека-панель ----------
panel = box(200, 170, 3, NECK_L, -85, 0)
for i in range(4):
    mx, s = mot[i]
    my = s * 35.0
    panel = panel.cut(cyl(18.6, 5, mx, my, -1))
    for a0 in (55, 235):
        arc = Part.makeCylinder(24.5, 5, Vector(mx, my, -1), Vector(0, 0, 1), 70)
        arc = arc.cut(cyl(21.4, 6, mx, my, -1.5))
        arc.rotate(Vector(mx, my, 0), Vector(0, 0, 1), a0)
        panel = panel.cut(arc)
    # глазок ближнего конца + стойка-люк дальнего (подъём во 2-й ярус)
    z0 = CAB_LEVELS[i]
    panel = panel.fuse(box(5, 4, z0 + 1.5, mx - 44, my - s * 12, 3))
    p1 = Part.makeCylinder(0.9, 8, Vector(mx - 45, my - s * 12 + 2, z0), Vector(1, 0, 0))
    panel = panel.cut(p1)
    x_far = mx - 58
    panel = panel.fuse(cyl(2.2, 11.0, x_far + 8, -s * (GY - 7), 3))
    panel = panel.cut(Part.makeCylinder(0.9, 8, Vector(x_far + 6, -s * (GY - 7), 8.6 + 1.2 * (i % 2)), Vector(1, 0, 0)))
add("Deka_panel", panel.removeSplitter())

# ---------- барабан ----------
drum = cyl(5.5, 1.0, 0, 0, 1.9)
drum = drum.fuse(cyl(4.0, 7.0, 0, 0, 2.9))
drum = drum.fuse(cyl(5.5, 1.0, 0, 0, 9.9))
drum = drum.cut(cyl(2.825, 4.3, 0, 0, 1.9))
drum = drum.cut(cyl(1.6, 12, 0, 0, 0))
for a in (0, 180):
    drum = drum.cut(Part.makeCylinder(0.8, 6, Vector(0, 0, 5.6),
                    Vector(math.cos(math.radians(a)), math.sin(math.radians(a)), 0)))
add("Drum", drum.removeSplitter())

doc.recompute()
doc.saveAs(os.path.join(OUT, "Cable_kit.FCStd"))
seg = lambda sh, x0, x1: sh.common(box(x1 - x0, 200, 60, x0, -100, -10))
batches = {
    "1": [("zona_body", seg(doc.getObject("Body").Shape, 20, 250)),
          ("zona_cover", seg(doc.getObject("Cover").Shape, 21, 250)),
          ("boat_x4", doc.getObject("Boat").Shape),
          ("roller4_x8", doc.getObject("Roller4").Shape)],
    "2": [("seg2_body", seg(doc.getObject("Body").Shape, 250, 480)),
          ("seg3_body", seg(doc.getObject("Body").Shape, 480, NECK_L)),
          ("seg2_cover", seg(doc.getObject("Cover").Shape, 250, 480)),
          ("seg3_cover", seg(doc.getObject("Cover").Shape, 480, NECK_L)),
          ("deka_panel", doc.getObject("Deka_panel").Shape),
          ("drum_x4", doc.getObject("Drum").Shape)]}
for b, items in batches.items():
    os.makedirs(os.path.join(OUT, "print", b), exist_ok=True)
    for n, s in items:
        m = MeshPart.meshFromShape(Shape=s, LinearDeflection=0.05, AngularDeflection=0.3)
        Mesh.Mesh(m.Topology).write(os.path.join(OUT, "print", b, n + ".stl"))
        print("stl:", b, n)
print("CABLE KIT v2 SAVED")
