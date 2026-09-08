import Mesh, math
m = Mesh.Mesh(r"C:\App\gitar\print\belt_pinion12.stl")
bb = m.BoundBox
print("bbox:", bb)
# радиусы вершин в нижней зоне (z < 6.5) возле центра
low = [p for p in m.Points if p.z < 6.4]
rads = sorted(set(round(math.hypot(p.x, p.y), 2) for p in low if math.hypot(p.x, p.y) < 4.5))
print("радиусы вершин у центра снизу:", rads)
# есть ли стенка кармана (r ~2.82) и его потолок
ring = [p for p in m.Points if 2.7 < math.hypot(p.x, p.y) < 2.95]
zs = sorted(set(round(p.z, 2) for p in ring))
print("z-уровни стенки кармана Ø5.65:", zs)
