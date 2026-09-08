# Стенд v2: шестерня ленты (12T, шаг 4.347) НАПРЕССОВЫВАЕТСЯ на заводскую
# шестерёнку мотора (Ø5.9, 10T) как на накатку. Никаких печатных мелких шестерён.
# Лента belt1_wall07_short + натяжной ролик. Лента-призрак включена в модель.
import FreeCAD
from FreeCAD import Vector
import Part, MeshPart, Mesh, math, os

OUT = r"C:\App\gitar"
BELT_PITCH = 4.347
Z_PIN = 12
R_PIN = Z_PIN * BELT_PITCH / (2 * math.pi)     # 8.30 - лента едет по этому радиусу
GAP_DEPTH = 1.37
IDLER_R = 6.0
BELT_RELAX = 156.5
STRETCH = 1.01
CD = (BELT_RELAX * STRETCH - math.pi * (R_PIN + IDLER_R)) / 2   # мотор-ролик
print(f"CD motor-idler = {CD:.1f}")
ix, iy = CD, 0.0
BORE = 5.65 / 2      # прессом на шестерёнку Ø5.9

# ---- шестерня ленты: диск с вырезами под зубья ленты, отверстие-накатка ----
pin = Part.makeCylinder(R_PIN, 13.0, Vector(0, 0, 2.0))       # z 2..15
cuts = []
for i in range(Z_PIN):
    a = 2 * math.pi * i / Z_PIN
    u = Vector(math.cos(a), math.sin(a), 0)
    t = Vector(-math.sin(a), math.cos(a), 0)
    c = Vector(0, 0, 1.5)
    r_out, r_in = R_PIN + 0.15, R_PIN - GAP_DEPTH
    pp = [c + u*r_out + t*1.275, c + u*r_out - t*1.275,
          c + u*r_in - t*0.95, c + u*r_in + t*0.95]
    cuts.append(Part.Face(Part.makePolygon(pp + [pp[0]])).extrude(Vector(0, 0, 14)))
pin = pin.cut(cuts)
pin = pin.cut(Part.makeCylinder(BORE, 4.3, Vector(0, 0, 1.9)))   # глухая посадка (шестерёнка 4 мм)
pin = pin.cut(Part.makeCylinder(1.6, 20, Vector(0, 0, 0)))       # сквозной канал (если вал длиннее)
pin = pin.removeSplitter()
print("belt pinion:", pin.isValid(), "solids", len(pin.Solids))

# ---- натяжной ролик ----
idler = Part.makeCylinder(IDLER_R + 1.5, 1.0, Vector(ix, iy, 5.4))
idler = idler.fuse(Part.makeCylinder(IDLER_R, 16.4, Vector(ix, iy, 6.4)))
idler = idler.fuse(Part.makeCylinder(IDLER_R + 1.5, 1.0, Vector(ix, iy, 22.8)))
idler = idler.cut(Part.makeCylinder(2.05, 26, Vector(ix, iy, 4)))
idler = idler.removeSplitter()

# ---- база ----
base = Part.makeBox(CD + 40, 60, 3, Vector(-22, -30, -3))
base = base.cut(Part.makeCylinder(18.6, 5, Vector(0, 0, -4)))
for a0 in (55, 235):
    arc = Part.makeCylinder(24.5, 5, Vector(0, 0, -4), Vector(0, 0, 1), 70)
    arc = arc.cut(Part.makeCylinder(21.4, 6, Vector(0, 0, -4.5)))
    arc.rotate(Vector(0, 0, 0), Vector(0, 0, 1), a0)
    base = base.cut(arc)
boss = Part.makeCylinder(4.5, 5.3, Vector(ix, iy, 0))
base = base.fuse(boss)
base = base.cut(Part.makeCylinder(1.9, 12, Vector(ix, iy, -3)))
base = base.removeSplitter()
print("base:", base.isValid(), "solids", len(base.Solids))

# ---- лента-призрак в натянутом виде (петля вокруг шестерни и ролика) ----
def ext_tangent(c1, r1, c2, r2, side):
    dx, dy = c2[0]-c1[0], c2[1]-c1[1]
    L = math.hypot(dx, dy)
    na = math.atan2(dy, dx) + side * math.acos((r1 - r2) / L)
    n = (math.cos(na), math.sin(na))
    return ((c1[0]+r1*n[0], c1[1]+r1*n[1]), (c2[0]+r2*n[0], c2[1]+r2*n[1]))
def V2(p): return Vector(p[0], p[1], 0)
def arc2(c, r, p0, p1):
    a0 = math.atan2(p0[1]-c[1], p0[0]-c[0]); a1 = math.atan2(p1[1]-c[1], p1[0]-c[0])
    while a1 <= a0: a1 += 2*math.pi
    am = (a0+a1)/2
    return Part.Arc(V2(p0), V2((c[0]+r*math.cos(am), c[1]+r*math.sin(am))), V2(p1)).toShape()
CM, CI = (0.0, 0.0), (ix, iy)
t1, t2 = ext_tangent(CM, R_PIN, CI, IDLER_R, -1)
t3, t4 = ext_tangent(CM, R_PIN, CI, IDLER_R, +1)
inner = Part.Wire([Part.makeLine(V2(t1), V2(t2)), arc2(CI, IDLER_R, t2, t4),
                   Part.makeLine(V2(t4), V2(t3)), arc2(CM, R_PIN, t3, t1)])
print("belt path len:", round(inner.Length, 1))
ring = Part.Face(inner.makeOffset2D(0.7)).cut(Part.Face(inner))
belt_ghost = ring.extrude(Vector(0, 0, 15))
belt_ghost.translate(Vector(0, 0, 6.6))       # низ ленты z 6.6, зубцы 6.6..12.8 на шестерне

# ---- проверки ----
def dist(a, b, l): print(f"dist {l}: {a.distToShape(b)[0]:.3f}")
dist(pin, base, "pinion-base")
dist(idler, base, "idler-base")
dist(belt_ghost, base, "belt-base")
dist(belt_ghost, idler, "belt-idler (~0)")
dist(belt_ghost, pin, "belt-pinion (~0)")

doc = FreeCAD.newDocument("Drive_test")
for n, s in [("Base", base), ("BeltPinion12T", pin), ("Idler", idler),
             ("Belt_ghost", belt_ghost)]:
    o = doc.addObject("Part::Feature", n)
    o.Shape = s
doc.recompute()
doc.saveAs(os.path.join(OUT, "Drive_test.FCStd"))
os.makedirs(os.path.join(OUT, "print"), exist_ok=True)
for n, s in [("drive_base", base), ("belt_pinion12", pin), ("idler", idler)]:
    m = MeshPart.meshFromShape(Shape=s, LinearDeflection=0.03, AngularDeflection=0.25)
    Mesh.Mesh(m.Topology).write(os.path.join(OUT, "print", n + ".stl"))
print("saved v2")
