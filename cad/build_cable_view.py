# Сборочный вид нитяной архитектуры: лодочки, ролики, НИТИ (Ø0.8 для видимости),
# моторы с барабанами. Ближний конец нити мотается на барабан низко (z4.5),
# дальний приходит поперёк деки ВЕРХОМ (z6.8) - перекрёстки разведены по высоте.
import FreeCAD
from FreeCAD import Vector
import Part, math

doc = FreeCAD.newDocument("Cable_view")
def add(n, s):
    o = doc.addObject("Part::Feature", n); o.Shape = s; return o
def box(x, y, z, px, py, pz): return Part.makeBox(x, y, z, Vector(px, py, pz))
def cyl(r, h, px, py, pz): return Part.makeCylinder(r, h, Vector(px, py, pz))
def wire_seg(p1, p2, r=0.4):
    d = p2 - p1
    if d.Length < 0.05: return None
    return Part.makeCylinder(r, d.Length, p1, d)
def ring(cx, cy, z, r, a0, a1, rr=0.4):
    t = Part.makeCylinder(r + rr, rr * 2, Vector(cx, cy, z - rr), Vector(0, 0, 1), a1 - a0)
    t = t.cut(Part.makeCylinder(r - rr, rr * 2 + 1, Vector(cx, cy, z - rr - 0.5)))
    t.rotate(Vector(cx, cy, 0), Vector(0, 0, 1), a0)
    return t

W = 58.0; HW = W / 2
NECK_L = 600.0
lanes_x = [55.0, 72.0, 89.0, 106.0]
lane_side = [-1, +1, -1, +1]
mot = {0: (645.0, -1), 1: (645.0, +1), 2: (705.0, -1), 3: (705.0, +1)}
CAB_LEVELS = [7.5, 6.1, 4.7, 3.3]     # дальняя дорожка - верхний этаж (нить НАД чужими роликами)
GY = 27.5                              # |y| линии нитей: в 0.3 от стенки борта
demo_y = [-12.0, 6.0, 15.0, -4.0]

add("Grif_dno", box(NECK_L - 20, W, 2, 20, -HW, 0))
LIFT = 18
kr = box(NECK_L - 21, W, 2, 21, -HW, 9 + LIFT)
add("Deka_plita", box(200, 170, 3, NECK_L, -85, 0))

for i, lx in enumerate(lanes_x):
    by = demo_y[i]
    # лодочка (универсальная ножка до нижнего этажа нитей)
    car = box(16, 14, 4, lx - 8, by - 7, 11 + LIFT)
    rim = box(16, 14, 1.6, lx - 8, by - 7, 15 + LIFT).cut(
        box(13.2, 11.2, 3, lx - 6.6, by - 5.6, 14.9 + LIFT))
    stem = box(3.5, 8, 8.5, lx - 1.75, by - 4, 2.8)
    add(f"Lodochka{i+1}", car.fuse([rim, stem]))
    kr = kr.cut(box(4.6, 44.5, 4, lx - 2.3, -22.25, 8 + LIFT))

for i, lx in enumerate(lanes_x):
    s = lane_side[i]
    by = demo_y[i]
    zc0 = CAB_LEVELS[i]                                # этаж нитей этой дорожки
    mx, ms = mot[i]
    my = ms * 35.0
    segs = []
    for rs in (+1, -1):
        y_g = rs * GY                                  # линия у борта - у ВСЕХ одинаковая
        cx_r = lx + 2.4
        cy_r = y_g - rs * 2.4
        add(f"Rolik{i+1}{'p' if rs>0 else 'l'}",
            cyl(2.4, 2.2, cx_r, cy_r, zc0 - 1.1).fuse(cyl(3.0, zc0 - 1.1, cx_r, cy_r, 0)))
        # перекрёст: нить с этого борта крепится к ПРОТИВОПОЛОЖНОМУ ушку ножки
        p_boat = Vector(lx, by - (2 if rs > 0 else -2), zc0)
        p_tan1 = Vector(lx, cy_r, zc0)
        w = wire_seg(p_boat, p_tan1)
        if w: segs.append(w)
        segs.append(ring(cx_r, cy_r, zc0, 2.4, 90 if rs > 0 else 180, 180 if rs > 0 else 270))
        near = (rs == ms)
        x_end = mx - 42 if near else mx - 58
        segs.append(wire_seg(Vector(cx_r, y_g, zc0), Vector(x_end, y_g, zc0)))
        if near:
            segs.append(wire_seg(Vector(x_end, y_g, zc0), Vector(mx - 4.2, my - ms * 2, zc0)))
            segs.append(ring(mx, my, zc0, 4.2, 90, 300))
        else:
            zc = 8.6 + 1.2 * (i % 2)
            add(f"Glazok{i+1}", cyl(1.5, 4, x_end, y_g, zc0 - 1.5))
            y_in = rs * (GY - 7)
            segs.append(wire_seg(Vector(x_end, y_g, zc0), Vector(x_end + 5, y_in, zc0)))   # отход от борта на своём этаже
            segs.append(wire_seg(Vector(x_end + 5, y_in, zc0), Vector(x_end + 12, y_in, zc)))  # подъём внутри
            segs.append(wire_seg(Vector(x_end + 12, y_in, zc), Vector(mx - 4.2, my + ms * 2, zc)))
            segs.append(ring(mx, my, zc, 4.2, 60, 270))
    add(f"Nit{i+1}", Part.makeCompound([x for x in segs if x]))

    add(f"Motor{i+1}", cyl(18, 12, mx, my, -13).fuse(cyl(4.0, 6, mx, my, 2.0)))
    add(f"Baraban{i+1}", cyl(5.5, 0.8, mx, my, 1.9).fuse(cyl(4.0, 4.8, mx, my, 2.7)).fuse(cyl(5.5, 0.8, mx, my, 7.5)))

add("Grif_kryshka", kr)
doc.recompute()
doc.saveAs(r"C:\App\gitar\Cable_view.FCStd")
print("objects:", len(doc.Objects))
