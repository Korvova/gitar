# Концепт v2: тяги-линейки. 4 плоских линейки в 4 тонких этажах грифа;
# в деке каждую возит поперёк каретка на короткой ленточной петле (как стенд);
# конец линейки поднимается штырём к тележке на крышке (карманный зацеп).
import FreeCAD
from FreeCAD import Vector
import Part, math

doc = FreeCAD.newDocument("Concept_rods")
def add(n, s):
    o = doc.addObject("Part::Feature", n); o.Shape = s; return o
def box(x, y, z, px, py, pz): return Part.makeBox(x, y, z, Vector(px, py, pz))
def cyl(r, h, px, py, pz): return Part.makeCylinder(r, h, Vector(px, py, pz))

W = 58.0                      # ширина грифа (новая)
add("Grif_dno", box(600, W, 2, 0, -W/2, 0))
# крышка (приподнята для обзора)
LIFT = 26
add("Grif_kryshka", box(600, W, 2, 0, -W/2, 18 + LIFT))
add("Deka_plita", box(220, 200, 3, 600, -100, 0))

lanes_x = [55.0, 72.0, 89.0, 106.0]
layers_z = [3.0, 7.0, 11.0, 15.0]          # 4 тонких этажа линеек
mot = [(640, 60), (700, 60), (640, -60), (700, -60)]
# демо-смещения тележек (какая где стоит)
demo_y = [-15.0, 5.0, 18.0, -5.0]

for i in range(4):
    lx = lanes_x[i]
    z = layers_z[i]
    mx, my0 = mot[i]
    dy = demo_y[i]

    # короткая петля в деке (вдоль Y): шестерня у мотора + ролик + лента-овал
    add(f"Motor{i+1}", cyl(18, 12, mx, my0, -13).fuse(cyl(8.3, 4, mx, my0, z - 0.5)))
    iy = my0 - 44 * (1 if my0 > 0 else -1)
    add(f"Rolik{i+1}", cyl(8.3, 6, mx, iy, z - 1))
    # лента (условный овал)
    r = 8.65
    p0, p1 = (mx, my0), (mx, iy)
    w = Part.Wire([
        Part.makeLine(Vector(mx - r, my0, 0), Vector(mx - r, iy, 0)),
        Part.Arc(Vector(mx - r, iy, 0), Vector(mx, iy - r * (1 if my0 > 0 else -1), 0), Vector(mx + r, iy, 0)).toShape(),
        Part.makeLine(Vector(mx + r, iy, 0), Vector(mx + r, my0, 0)),
        Part.Arc(Vector(mx + r, my0, 0), Vector(mx, my0 + r * (1 if my0 > 0 else -1), 0), Vector(mx - r, my0, 0)).toShape()])
    ring = Part.Face(w.makeOffset2D(0.7)).cut(Part.Face(w))
    belt = ring.extrude(Vector(0, 0, 5)); belt.translate(Vector(0, 0, z - 0.5))
    add(f"Lenta{i+1}", belt)
    # каретка деки: зажата на ленте, возит хвост линейки
    ky = (my0 + iy) / 2 + dy
    add(f"Karetka{i+1}", box(14, 12, 5, mx - 7 - 9.5, ky - 6, z - 0.5))

    # линейка: от каретки вдоль грифа до своей дорожки (смещена на dy)
    ruler = box(mx - 16.5 - (lx - 2), 9, 2.6, lx - 2, dy - 4.5, z)
    add(f"Lineika{i+1}", ruler)
    # штырь вверх к тележке
    add(f"Shtyr{i+1}", box(4, 4, 18 + LIFT + 1 - z, lx, dy - 2, z))
    # тележка-лодочка на крышке
    car = box(16, 14, 4, lx - 8, dy - 7, 20 + LIFT)
    rim = box(16, 14, 1.6, lx - 8, dy - 7, 24 + LIFT).cut(
        box(13.2, 11.2, 3, lx - 6.6, dy - 5.6, 23.9 + LIFT))
    add(f"Telezhka{i+1}", car.fuse(rim))
    # щель в крышке над этой дорожкой (вырез)
    kr = doc.getObject("Grif_kryshka")
    kr.Shape = kr.Shape.cut(box(5, 46, 4, lx - 0.5, -23, 17 + LIFT))

    # гребёнка-опоры линейки (поперечные мостики со сквозным пазом)
    for gx in (200, 350, 500):
        sup = box(8, W - 4, 3.2, gx, -W/2 + 2, z - 0.3)
        sup = sup.cut(box(10, 48, 2.8, gx - 1, -24, z - 0.1))
        add(f"Opora{i+1}_{gx}", sup)

doc.recompute()
doc.saveAs(r"C:\App\gitar\Concept_rods.FCStd")
print("objects:", len(doc.Objects))
