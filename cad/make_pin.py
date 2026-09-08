import FreeCAD
from FreeCAD import Vector
import Part, MeshPart, Mesh

pin = Part.makeCylinder(1.9, 26, Vector(0, 0, 0))
m = MeshPart.meshFromShape(Shape=pin, LinearDeflection=0.03, AngularDeflection=0.25)
Mesh.Mesh(m.Topology).write(r"C:\App\gitar\print\pin_rod_4x26.stl")
print("pin saved")
