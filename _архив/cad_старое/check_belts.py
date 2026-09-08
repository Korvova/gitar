import FreeCAD
import Mesh, math
doc = FreeCAD.openDocument(r"C:\App\gitar\Belts.FCStd")
for o in doc.Objects:
    sh = o.Shape
    print(f"{o.Name}: solids={len(sh.Solids)} valid={sh.isValid()}")
# и проверка STL первого: нет ли осколков (изолированных компонентов)
m = Mesh.Mesh(r"C:\App\gitar\print\3\belt_lane1.stl")
comps = m.getSeparateComponents()
print("belt_lane1.stl: компонентов сетки =", len(comps))
