# Концепт v2.1: продольные тяги (4 шт бок о бок в одном слое) + слой качалок 1:1.
# мотор -> короткая петля -> каретка -> тяга вдоль грифа -> качалка -> лодочка поперёк.
import FreeCAD
from FreeCAD import Vector
import Part, math

doc = FreeCAD.newDocument("Concept_rods2")
def add(n, s):
    o = doc.addObject("Part::Feature", n); o.Shape = s; return o
def box(x, y, z, px, py, pz): return Part.makeBox(x, y, z, Vector(px, py, pz))
def cyl(r, h, px, py, pz): return Part.makeCylinder(r, h, Vector(px, py, pz))

W = 58.0
add("Grif_dno", box(600, W, 2, 0, -W/2, 0))
LIFT = 22
kr = box(600, W, 2, 0, -W/2, 11 + LIFT)
add("Deka_plita", box(220, 200, 3, 600, -100, 0))

lanes_x = [55.0, 72.0, 89.0, 106.0]
rod_y = [-16.5, -5.5, 5.5, 16.5]           # 4 тяги бок о бок, слой z 2.5..5.5
mot = [(640, 60), (700, 60), (640, -60), (700, -60)]
demo_ang = [-30, 15, 40, 0]                # демо-углы качалок

for i in range(4):
    lx = lanes_x[i]
    ry = rod_y[i]
    mx, my0 = mot[i]
    ang = math.radians(demo_ang[i])

    # тяга: от деки до своей дорожки, слой один на всех
    demo_dx = 15 * math.sin(ang)           # смещение тяги = входное плечо качалки
    add(f"Tyaga{i+1}", box(mx - 20 - lx, 9, 3, lx + demo_dx, ry - 4.5, 2.5))

    # качалка: планка на оси (штифт 4мм) в слое выше, плечи 15/15
    piv = (lx, 0.0)
    lever = box(38, 8, 3, -19, -4, 0)
    lever = lever.fuse(cyl(3.5, 3, 0, 0, 0))
    lever = lever.fuse(cyl(1.8, 8, -15, 0, 3))     # палец вверх (к лодочке)
    lever = lever.fuse(cyl(1.8, 4, 15, 0, -3))     # палец вниз (в тягу)
    lever.rotate(Vector(0, 0, 0), Vector(0, 0, 1), 90 + demo_ang[i])
    lever.translate(Vector(piv[0], piv[1], 6.5))
    add(f"Kachalka{i+1}", lever)
    add(f"Os{i+1}", cyl(1.9, 8, piv[0], piv[1], 2))

    # лодочка на крышке, ведомая пальцем качалки (стоит по демо-углу)
    cy = 15 * math.sin(ang + math.pi/2) * -1
    cy = -15 * math.cos(ang) * 0 + (-15) * math.sin(ang) * 0
    # позиция пальца выхода: от оси на плече 15 под углом (90+ang)
    px_out = piv[0] + 15 * math.cos(math.radians(90 + demo_ang[i] + 180))
    py_out = piv[1] + 15 * math.sin(math.radians(90 + demo_ang[i] + 180))
    car = box(16, 14, 4, lx - 8, py_out - 7, 13 + LIFT)
    rim = box(16, 14, 1.6, lx - 8, py_out - 7, 17 + LIFT).cut(
        box(13.2, 11.2, 3, lx - 6.6, py_out - 5.6, 16.9 + LIFT))
    add(f"Lodochka{i+1}", car.fuse(rim))
    # дуговая прорезь в крышке
    arc = Part.makeCylinder(16.8, 4, Vector(piv[0], piv[1], 10 + LIFT), Vector(0, 0, 1), 120)
    arc = arc.cut(Part.makeCylinder(13.2, 5, Vector(piv[0], piv[1], 9.5 + LIFT)))
    arc.rotate(Vector(piv[0], piv[1], 0), Vector(0, 0, 1), 210)
    kr = kr.cut(arc)

    # дека: мотор + петля вдоль X + каретка
    add(f"Motor{i+1}", cyl(18, 12, mx, my0, -13).fuse(cyl(8.3, 4, mx, my0, 2.0)))
    ix2 = mx - 44
    add(f"Rolik{i+1}", cyl(8.3, 6, ix2, my0, 1.5))
    r = 8.65
    w = Part.Wire([
        Part.makeLine(Vector(ix2, my0 - r, 0), Vector(mx, my0 - r, 0)),
        Part.Arc(Vector(mx, my0 - r, 0), Vector(mx + r, my0, 0), Vector(mx, my0 + r, 0)).toShape(),
        Part.makeLine(Vector(mx, my0 + r, 0), Vector(ix2, my0 + r, 0)),
        Part.Arc(Vector(ix2, my0 + r, 0), Vector(ix2 - r, my0, 0), Vector(ix2, my0 - r, 0)).toShape()])
    ring = Part.Face(w.makeOffset2D(0.7)).cut(Part.Face(w))
    belt = ring.extrude(Vector(0, 0, 5)); belt.translate(Vector(0, 0, 1.5))
    add(f"Lenta{i+1}", belt)
    add(f"Karetka{i+1}", box(12, 14, 5, mx - 22 + demo_dx, my0 - 7, 2.0))
    # соединительная планка каретка->тяга (условно)
    add(f"Svyaz{i+1}", box(mx - 20 - (mx - 22) + 2, 3, 2, mx - 22 + demo_dx, ry + (my0 - ry) * 0 - 1.5, 5.5))

# гребёнки: держат тяги со всех сторон, свобода только вдоль X
for gx in (180, 320, 460):
    sup = box(10, W - 4, 5, gx, -W/2 + 2, 1.9)
    for ry in rod_y:
        sup = sup.cut(box(12, 9.8, 3.6, gx - 1, ry - 4.9, 2.3))
    add(f"Grebenka_{gx}", sup)

add("Grif_kryshka", kr)
doc.recompute()
doc.saveAs(r"C:\App\gitar\Concept_rods2.FCStd")
print("objects:", len(doc.Objects))
