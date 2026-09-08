# Стенд v3: + тележка на ленте. Ролик = R шестерни (ветки параллельны оси X).
# Тележка: 2 пластины зажимают ленту (2 x M2 через гладкую зону), едет по 4мм штырю-рельсе.
import FreeCAD
from FreeCAD import Vector
import Part, MeshPart, Mesh, math, os

OUT = r"C:\App\gitar"
BELT_PITCH = 4.347
Z_PIN = 12
R_PIN = Z_PIN * BELT_PITCH / (2 * math.pi)   # 8.30
GAP_DEPTH = 1.37
R_IDLER = R_PIN                               # ветки параллельны
BELT_RELAX = 156.5
CD = (BELT_RELAX * 1.01 - math.pi * (R_PIN + R_IDLER)) / 2
print(f"CD = {CD:.1f}")
ix = CD
BORE = 5.65 / 2

# ---- шестерня ленты (без изменений, z 2..15) ----
pin = Part.makeCylinder(R_PIN, 13.0, Vector(0, 0, 2.0))
cuts = []
for i in range(Z_PIN):
    a = 2 * math.pi * i / Z_PIN
    u = Vector(math.cos(a), math.sin(a), 0)
    t = Vector(-math.sin(a), math.cos(a), 0)
    c = Vector(0, 0, 1.5)
    pp = [c + u*(R_PIN+0.15) + t*1.275, c + u*(R_PIN+0.15) - t*1.275,
          c + u*(R_PIN-GAP_DEPTH) - t*0.95, c + u*(R_PIN-GAP_DEPTH) + t*0.95]
    cuts.append(Part.Face(Part.makePolygon(pp + [pp[0]])).extrude(Vector(0, 0, 14)))
pin = pin.cut(cuts)
pin = pin.cut(Part.makeCylinder(BORE, 4.3, Vector(0, 0, 1.9)))
pin = pin.cut(Part.makeCylinder(1.6, 20, Vector(0, 0, 0)))
pin = pin.removeSplitter()

# ---- ролик v2: R = R_PIN, бортики ----
idler = Part.makeCylinder(R_IDLER + 1.5, 1.0, Vector(ix, 0, 5.4))
idler = idler.fuse(Part.makeCylinder(R_IDLER, 16.4, Vector(ix, 0, 6.4)))
idler = idler.fuse(Part.makeCylinder(R_IDLER + 1.5, 1.0, Vector(ix, 0, 22.8)))
idler = idler.cut(Part.makeCylinder(2.05, 26, Vector(ix, 0, 4)))
idler = idler.removeSplitter()

# ---- база: гнездо мотора + бобышка ролика + 2 стойки рельса ----
base = Part.makeBox(CD + 44, 64, 3, Vector(-22, -32, -3))
base = base.cut(Part.makeCylinder(18.6, 5, Vector(0, 0, -4)))
for a0 in (55, 235):
    arc = Part.makeCylinder(24.5, 5, Vector(0, 0, -4), Vector(0, 0, 1), 70)
    arc = arc.cut(Part.makeCylinder(21.4, 6, Vector(0, 0, -4.5)))
    arc.rotate(Vector(0, 0, 0), Vector(0, 0, 1), a0)
    base = base.cut(arc)
base = base.fuse(Part.makeCylinder(4.5, 5.3, Vector(ix, 0, 0)))
base = base.cut(Part.makeCylinder(1.9, 12, Vector(ix, 0, -3)))
# рельса: 4мм штырь вдоль X на y=14, z=18; стойки за пределами хода
RAIL_Y, RAIL_Z = 14.0, 18.0
for px in (-14, ix + 9):
    post = Part.makeBox(6, 6, RAIL_Z + 3, Vector(px - 3, RAIL_Y - 3, 0))
    base = base.fuse(post)
    base = base.cut(Part.makeCylinder(1.95, 8, Vector(px, RAIL_Y, RAIL_Z), Vector(1, 0, 0)))
# отверстия рельса: сквозные по X через обе стойки
base = base.cut(Part.makeCylinder(1.95, CD + 40, Vector(-18, RAIL_Y, RAIL_Z), Vector(1, 0, 0)))
base = base.removeSplitter()
print("base:", base.isValid(), "solids", len(base.Solids))

# ---- тележка: наружная пластина (площадка + ушко рельса) + внутренняя пластина ----
# верхняя ветка ленты: наружная поверхность y = 9.0 (R+0.7), лента z 7..22, гладкая зона z 13.2..22
CL = 16.0   # длина тележки по X
outer = Part.makeBox(CL, 1.8, 9.0, Vector(0, 9.05, 13.0))          # прижимная наружная, z 13..22
inner = Part.makeBox(CL, 1.8, 9.0, Vector(0, 6.45, 13.0))          # внутренняя (внутри петли)
plat  = Part.makeBox(CL, 14, 1.8, Vector(0, 6.45, 22.0))           # площадка сверху
rim   = Part.makeBox(CL, 14, 1.6, Vector(0, 6.45, 23.8))
rim   = rim.cut(Part.makeBox(CL - 2.8, 11.2, 3, Vector(1.4, 7.85, 23.7)))
eye   = Part.makeBox(CL, 3.6, 6.0, Vector(0, RAIL_Y - 1.8, RAIL_Z - 3.0))
carriage_outer = outer.fuse([plat, rim, eye])
carriage_outer = carriage_outer.cut(
    Part.makeCylinder(2.15, CL + 2, Vector(-1, RAIL_Y, RAIL_Z), Vector(1, 0, 0)))  # скользит по рельсу
# два винта M2 сквозь ленту: по y, z 16 и 20
for sz in (16.0, 20.0):
    hole = Part.makeCylinder(1.1, 8, Vector(CL/2, 5.5, sz), Vector(0, 1, 0))
    carriage_outer = carriage_outer.cut(hole)
    inner = inner.cut(hole)
# карманы под гайки M2 на внутренней пластине (шестигранник ~4.2)
for sz in (16.0, 20.0):
    nut = Part.makeCylinder(2.35, 1.4, Vector(CL/2, 6.4, sz), Vector(0, 1, 0), 360)
    inner = inner.cut(nut)
carriage_outer = carriage_outer.removeSplitter()
inner = inner.removeSplitter()
print("carriage:", carriage_outer.isValid(), inner.isValid())

# ---- рельс ----
rail = Part.makeCylinder(1.9, CD + 32, Vector(0, 0, 0), Vector(0, 0, 1))

# ---- проверки (тележка в середине хода) ----
def dist(a, b, l): print(f"dist {l}: {a.distToShape(b)[0]:.3f}")
mid = Vector((CD - CL) / 2, 0, 0)
co = carriage_outer.copy(); co.translate(mid)
ci = inner.copy(); ci.translate(mid)
dist(co, base, "carr_outer-base")
dist(ci, base, "carr_inner-base")
dist(ci, idler, "carr_inner-idler(mid)")
dist(co, idler, "carr_outer-idler(mid)")
# и у краёв
for x0 in (1.0, CD - CL - 1.0):
    c2 = carriage_outer.copy(); c2.translate(Vector(x0, 0, 0))
    print(f"  x0={x0:.0f}:", round(c2.distToShape(idler)[0], 2), "до ролика,",
          round(c2.distToShape(pin)[0], 2), "до шестерни")

doc = FreeCAD.newDocument("Stand_v3")
for n, s in [("Base", base), ("BeltPinion12T", pin), ("Idler", idler),
             ("CarriageOuter", carriage_outer), ("CarriageInner", inner), ("Rail", rail)]:
    o = doc.addObject("Part::Feature", n)
    o.Shape = s
doc.recompute()
doc.saveAs(os.path.join(OUT, "Stand_v3.FCStd"))
os.makedirs(os.path.join(OUT, "print"), exist_ok=True)
for n, s in [("drive_base_v3", base), ("idler_v3", idler),
             ("carriage_outer", carriage_outer), ("carriage_inner", inner),
             ("rail_4x85", rail)]:
    m = MeshPart.meshFromShape(Shape=s, LinearDeflection=0.03, AngularDeflection=0.25)
    Mesh.Mesh(m.Topology).write(os.path.join(OUT, "print", n + ".stl"))
print("saved stand v3")
