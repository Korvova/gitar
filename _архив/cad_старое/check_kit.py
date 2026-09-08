import FreeCAD
doc = FreeCAD.openDocument(r"C:\App\gitar\Neck_kit.FCStd")
for o in doc.Objects:
    sh = o.Shape
    n = len(sh.Solids)
    flag = ""
    if n != 1:
        # проверим, не висит ли что-то: солиды, чей ZMin выше плиты своего слоя
        flag = f"  <-- {n} солидов!"
    b = sh.BoundBox
    print(f"{o.Name}: solids={n} z[{b.ZMin:.1f}..{b.ZMax:.1f}]{flag}")
