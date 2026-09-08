import FreeCAD
from FreeCAD import Vector
import Part, MeshPart, Mesh

for name, ln in [("pin_4x12_nado_4sht", 12.0), ("pin_4x10_nado_8sht", 10.0)]:
    p = Part.makeCylinder(1.9, ln, Vector(0, 0, 0))
    m = MeshPart.meshFromShape(Shape=p, LinearDeflection=0.03, AngularDeflection=0.25)
    Mesh.Mesh(m.Topology).write(rf"C:\App\gitar\print\1\{name}.stl")
    print("saved", name)
