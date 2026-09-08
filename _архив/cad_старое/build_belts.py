# Ленты-змейки для 4 дорожек (папка 3). Петля печатается в форме серпантина:
# хребет из 3 колен, лента = "гоночный трек" вокруг хребта (offset 1.4 и 2.1),
# зубья по внутреннему контуру с шагом 4.347, зона зубьев - нижние 3.2 мм высоты.
import FreeCAD
from FreeCAD import Vector
import Part, MeshPart, Mesh, math, os

OUT = r"C:\App\gitar"
PITCH = 4.347
BH = 7.0
TOOTH_H, ROOT_W, TIP_W = 1.1, 2.2, 1.66
R_ER, R_CR, R_PIN = 4.0, 3.0, 8.3

def hw(x): return 23.85 + (x / 600.0) * 4.65
lanes = [
    dict(x=55.0,  s=+1, er_off=None, mx=665.0),
    dict(x=72.0,  s=-1, er_off=None, mx=665.0),
    dict(x=89.0,  s=-1, er_off=13.0, mx=745.0),
    dict(x=106.0, s=+1, er_off=13.0, mx=745.0),
]
Y_IN, Y_OUT = 18.25, 21.75

def assembled_len(ln):
    lx, s, mx = ln["x"], ln["s"], ln["mx"]
    xa, xb = lx - (R_ER + 0.35), lx + (R_ER + 0.35)
    y_er = (hw(lx) - 6.6) if ln["er_off"] is None else ln["er_off"]   # |y|
    cross_a = abs(-y_er - (Y_OUT - R_CR)) if False else (y_er + Y_OUT - R_CR)
    cross_b = (y_er + Y_IN - R_CR)
    er_wrap = math.pi * R_ER
    corners = 2 * (math.pi / 2) * R_CR
    along_b = mx - (xb + R_CR)
    x_sp = mx - 53
    along_a = (x_sp - (xa + R_CR)) + math.hypot(14, (Y_IN + 2*R_PIN) - (Y_OUT + 2)) + (mx - (x_sp + 14))
    pin_wrap = math.pi * R_PIN
    return cross_a + cross_b + er_wrap + corners + along_b + along_a + pin_wrap

def spine_wire(A, n_legs=3, P=16.0, Rt=8.0):
    e = []
    y = 0.0
    pts_dir = +1
    for leg in range(n_legs):
        x0, x1 = (0.0, A) if pts_dir > 0 else (A, 0.0)
        e.append(Part.makeLine(Vector(x0, y, 0), Vector(x1, y, 0)))
        if leg < n_legs - 1:
            cx = A if pts_dir > 0 else 0.0
            cy = y + P / 2
            mid_x = cx + (Rt if pts_dir > 0 else -Rt)
            e.append(Part.Arc(Vector(cx, y, 0), Vector(mid_x, cy, 0), Vector(cx, y + P, 0)).toShape())
            y += P
            pts_dir = -pts_dir
    return Part.Wire(e)

def build_belt(name, target_inner):
    # подбор длины колена, чтобы внутренний контур = целому числу зубьев
    n_teeth = int(target_inner // PITCH)
    goal = n_teeth * PITCH
    OFF_IN, OFF_OUT = 4.0, 4.7          # мин. радиус покоя 4 мм (= рабочий ролик)
    A = (goal - 130) / 6.0
    for _ in range(8):
        sp = spine_wire(A)
        inner = sp.makeOffset2D(OFF_IN)
        err = goal - inner.Length
        if abs(err) < 0.02:
            break
        A += err / 6.0
    sp = spine_wire(A)
    inner = sp.makeOffset2D(OFF_IN)
    outer = sp.makeOffset2D(OFF_OUT)
    print(f"{name}: цель {goal:.1f} ({n_teeth} зуб.), контур {inner.Length:.1f}, колено {A:.1f}")
    band = Part.Face(outer).cut(Part.Face(inner))
    belt = band.extrude(Vector(0, 0, BH))

    # зубья по внутреннему контуру: нормаль = точное направление к хребту
    pts = inner.discretize(Distance=PITCH)
    teeth = []
    bad = 0
    for k in range(len(pts) - (1 if inner.isClosed() else 0)):
        p = pts[k]
        d, pares = sp.distToShape(Part.Vertex(p))[0:2]
        foot = Vector(pares[0][0].x, pares[0][0].y, 0)
        n = foot - Vector(p.x, p.y, 0)
        if n.Length < 1e-6:
            bad += 1
            continue
        n.normalize()
        t = Vector(-n.y, n.x, 0)
        base = Vector(p.x, p.y, 0) - n * 0.25
        pp = [base + t * (ROOT_W / 2), base - t * (ROOT_W / 2),
              base - t * (TIP_W / 2) + n * (TOOTH_H + 0.25),
              base + t * (TIP_W / 2) + n * (TOOTH_H + 0.25)]
        # самопроверка: кончик обязан быть ближе к хребту, чем корень
        tip_mid = base + n * (TOOTH_H + 0.25)
        if sp.distToShape(Part.Vertex(tip_mid))[0] >= sp.distToShape(Part.Vertex(base))[0]:
            bad += 1
            continue
        poly = Part.makePolygon(pp + [pp[0]])
        teeth.append(Part.Face(poly).extrude(Vector(0, 0, 3.2)))
    belt = belt.fuse(teeth)
    print(f"  TEETH: {len(teeth)}, BAD_DIR: {bad} (must be 0)")
    return belt.removeSplitter(), n_teeth

doc = FreeCAD.newDocument("Belts")
os.makedirs(os.path.join(OUT, "print", "3"), exist_ok=True)
lines = ["ПАПКА 3 — ленты (TPU 95A, стенка: линия 0.35 x 2 периметра, слои 0.15,",
         "шов на зубчатую сторону, печатаются как лежат - змейкой):"]
for i, ln in enumerate(lanes):
    L = assembled_len(ln) * 0.99          # натяг 1%
    belt, nt = build_belt(f"belt_lane{i+1}", L)
    o = doc.addObject("Part::Feature", f"Belt_lane{i+1}")
    o.Shape = belt
    m = MeshPart.meshFromShape(Shape=belt, LinearDeflection=0.08, AngularDeflection=0.4)
    Mesh.Mesh(m.Topology).write(os.path.join(OUT, "print", "3", f"belt_lane{i+1}.stl"))
    lines.append(f"belt_lane{i+1}.stl - 1 шт ({nt} зубьев)")
doc.recompute()
doc.saveAs(os.path.join(OUT, "Belts.FCStd"))
with open(os.path.join(OUT, "print", "3", "README.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\nЗубья снизу (первые 3.2 мм высоты). Устанавливать зубьями к своей шестерне.\n")
print("BELTS SAVED")
