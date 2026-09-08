import FreeCAD
from FreeCAD import Vector
import Part, math

src = FreeCAD.openDocument(r"C:\App\gitar\Stand_v3.FCStd")
out = FreeCAD.newDocument("Stand_v3_anim")

def add(name, shape):
    o = out.addObject("Part::Feature", name)
    o.Shape = shape
    return o

add("Base", src.getObject("Base").Shape)
add("BeltPinion", src.getObject("BeltPinion12T").Shape)
add("Idler", src.getObject("Idler").Shape)

# импровизированный мотор: блин Ø36x17 + уши 43.85 + вал + шестерёнка Ø5.9
motor = Part.makeCylinder(18, 17, Vector(0, 0, -20))
ear = Part.makeBox(46, 8, 2.5, Vector(-23, -4, -5.5))
motor = motor.fuse(ear).cut(Part.makeCylinder(18.01, 3.1, Vector(0, 0, -6)).cut(Part.makeCylinder(17.99, 3.2, Vector(0, 0, -6.1))))
shaft = Part.makeCylinder(2.5, 8, Vector(0, 0, -3))
gear10 = Part.makeCylinder(2.95, 4, Vector(0, 0, 2))
motor = motor.fuse([shaft, gear10]).removeSplitter()
add("Motor_improv", motor)

co = src.getObject("CarriageOuter").Shape.copy()
ci = src.getObject("CarriageInner").Shape.copy()
add("CarriageOuter", co)   # позицию задаёт макрос
add("CarriageInner", ci)

rail = src.getObject("Rail").Shape.copy()
rail.rotate(Vector(0, 0, 0), Vector(0, 1, 0), 90)
rail.translate(Vector(-16, 14, 18))
add("Rail", rail)

# лента-кольцо
R = 8.65; ix = 53.0
w = Part.Wire([
    Part.makeLine(Vector(0, 8.3, 0), Vector(ix, 8.3, 0)),
    Part.Arc(Vector(ix, 8.3, 0), Vector(ix + 8.3, 0, 0), Vector(ix, -8.3, 0)).toShape(),
    Part.makeLine(Vector(ix, -8.3, 0), Vector(0, -8.3, 0)),
    Part.Arc(Vector(0, -8.3, 0), Vector(-8.3, 0, 0), Vector(0, 8.3, 0)).toShape()])
ring = Part.Face(w.makeOffset2D(0.7)).cut(Part.Face(w))
belt = ring.extrude(Vector(0, 0, 15)); belt.translate(Vector(0, 0, 7))
add("Belt", belt)

# 4 метки на ленте (анимируются макросом вдоль петли)
mark = Part.makeBox(3.0, 1.4, 15, Vector(-1.5, -0.7, 7))
for i in range(4):
    add(f"Mark{i+1}", mark)

out.recompute()
out.saveAs(r"C:\App\gitar\Stand_v3_anim.FCStd")
print("anim doc saved, objects:", len(out.Objects))
