import FreeCAD
from FreeCAD import Vector, Rotation, Placement
import Part

src = FreeCAD.openDocument(r"C:\App\gitar\Stand_v3.FCStd")
out = FreeCAD.newDocument("Stand_v3_view")

def add(name, shape):
    o = out.addObject("Part::Feature", name)
    o.Shape = shape

add("Base", src.getObject("Base").Shape)
add("BeltPinion12T", src.getObject("BeltPinion12T").Shape)
add("Idler", src.getObject("Idler").Shape)

co = src.getObject("CarriageOuter").Shape.copy(); co.translate(Vector(18.5, 0, 0))
ci = src.getObject("CarriageInner").Shape.copy(); ci.translate(Vector(18.5, 0, 0))
add("CarriageOuter", co); add("CarriageInner", ci)

rail = src.getObject("Rail").Shape.copy()
rail.rotate(Vector(0, 0, 0), Vector(0, 1, 0), 90)
rail.translate(Vector(-16, 14, 18))
add("Rail", rail)

# лента-призрак: петля вокруг шестерни (0,0) и ролика (53,0), R=8.3, стенка 0.7, z 7..22
import math
R = 8.3; ix = 53.0
w = Part.Wire([
    Part.makeLine(Vector(0, R, 0), Vector(ix, R, 0)),
    Part.Arc(Vector(ix, R, 0), Vector(ix + R, 0, 0), Vector(ix, -R, 0)).toShape(),
    Part.makeLine(Vector(ix, -R, 0), Vector(0, -R, 0)),
    Part.Arc(Vector(0, -R, 0), Vector(-R, 0, 0), Vector(0, R, 0)).toShape()])
ring = Part.Face(w.makeOffset2D(0.7)).cut(Part.Face(w))
belt = ring.extrude(Vector(0, 0, 15)); belt.translate(Vector(0, 0, 7))
add("Belt_ghost", belt)

out.recompute()
out.saveAs(r"C:\App\gitar\Stand_v3_view.FCStd")
print("view saved")
