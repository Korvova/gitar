import FreeCAD
doc = FreeCAD.openDocument(r"C:\App\gitar\Cable_view.FCStd")
nits = [doc.getObject(f"Nit{i}") for i in range(1, 5)]
bad = 0
for a in range(4):
    for b in range(a + 1, 4):
        d = nits[a].Shape.distToShape(nits[b].Shape)[0]
        mark = " !!!" if d < 0.1 else ""
        if d < 0.1: bad += 1
        print(f"Nit{a+1}-Nit{b+1}: {d:.2f}{mark}")
# нити против чужих барабанов и лодочек
for i in range(4):
    for j in range(4):
        if i == j: continue
        d = nits[i].Shape.distToShape(doc.getObject(f"Baraban{j+1}").Shape)[0]
        if d < 0.1:
            bad += 1
            print(f"Nit{i+1} - Baraban{j+1}: {d:.2f} !!!")
print("conflicts:", bad)
