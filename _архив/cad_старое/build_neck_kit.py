# Печатный комплект грифа v1 (по архитектуре layout v5).
# Слои: base 0..2 | низ 2..11.4 (лента 3..10) | палуба 11.4..12.8 |
#       верх 12.8..22.2 (лента 13.8..20.8) | крышка 22.2..24.2
# Сегменты: S1 x20..250 (голова+зона), S2 x250..480, S3 x480..600. Дека x600..800.
import FreeCAD
from FreeCAD import Vector
import Part, MeshPart, Mesh, math, os

OUT = r"C:\App\gitar"
doc = FreeCAD.newDocument("Neck_kit")
def add(n, s):
    o = doc.addObject("Part::Feature", n); o.Shape = s; return o
def box(x, y, z, px, py, pz): return Part.makeBox(x, y, z, Vector(px, py, pz))
def cyl(r, h, px, py, pz): return Part.makeCylinder(r, h, Vector(px, py, pz))

NECK_L = 600.0
def hw(x): return 23.85 + (x / NECK_L) * 4.65
BH = 7.0
Z_B0, Z_B1 = 3.0, 13.8            # низ лент этажей
DECK0, DECK1 = 11.4, 12.8
COV0, COV1 = 22.2, 24.2
R_ER, R_CR, R_PIN = 4.0, 3.0, 8.3
SLOT_W = 2.2                       # канавка ленты
# по ОДНОЙ ленте на борт/этаж. Слоты (центры полотен) B=18.25 (внутр), A=21.75 (внешн):
# зубья веток смотрят друг на друга, между кончиками 0.6; общая полость 17.6..22.4 БЕЗ средней стенки
lanes = [
    dict(x=55.0,  zb=Z_B0, s=+1, slots=(18.25, 21.75), er_off=None),
    dict(x=72.0,  zb=Z_B1, s=-1, slots=(18.25, 21.75), er_off=None),
    dict(x=89.0,  zb=Z_B0, s=-1, slots=(18.25, 21.75), er_off=13.0),
    dict(x=106.0, zb=Z_B1, s=+1, slots=(18.25, 21.75), er_off=13.0),
]
mot = {0: (665.0, +1), 1: (665.0, -1), 2: (745.0, -1), 3: (745.0, +1)}

def plate(x0, x1, z0, t, grow=0.0):
    pts = [Vector(x0, -hw(x0) - grow, z0), Vector(x1, -hw(x1) - grow, z0),
           Vector(x1, hw(x1) + grow, z0), Vector(x0, hw(x0) + grow, z0)]
    return Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(Vector(0, 0, t))

def wall_along(x0, x1, y_off, t, z0, z1):
    """стенка вдоль борта, параллельна конусу: y = ±(hw(x)-y_off)"""
    sgn = 1 if y_off >= 0 else -1
    pts = []
    n = 8
    for k in range(n + 1):
        x = x0 + (x1 - x0) * k / n
        pts.append(Vector(x, (hw(x) - abs(y_off)) * (1 if y_off > 0 else -1), z0))
    for k in range(n, -1, -1):
        x = x0 + (x1 - x0) * k / n
        pts.append(Vector(x, (hw(x) - abs(y_off) - t) * (1 if y_off > 0 else -1), z0))
    f = Part.Face(Part.makePolygon(pts + [pts[0]]))
    return f.extrude(Vector(0, 0, z1 - z0))

# ============ КАРКАС (единый, потом порежем на сегменты) ============
body = plate(20, NECK_L, 0, 2)                                  # дно
for sgn in (+1, -1):
    body = body.fuse(wall_along(20, NECK_L, sgn * 0.0, 1.2, 0, COV1))   # борта
deck = plate(21, NECK_L, DECK0, DECK1 - DECK0, -1.2)            # палуба (чуть уже)
cover = plate(21, NECK_L, COV0, COV1 - COV0, -1.2)              # крышка

# каналы: ПРЯМЫЕ, одна лента (пара веток) на борт/этаж, общая полость:
# |стенка 17.0..17.6| полость 17.6..22.4 (обе ветки, зубья навстречу) |стенка 22.4..23.0|
CH_X0 = 132.0
for zb in (Z_B0, Z_B1):
    z0, z1 = zb - 1.0, zb + BH + 0.6
    for side in (+1, -1):
        for (y0w, y1w) in [(17.0, 17.6), (22.4, 23.0)]:
            w = box(NECK_L - CH_X0, y1w - y0w, z1 - z0,
                    CH_X0, side * y0w if side > 0 else -side * 0 - y1w, z0)
            if side < 0:
                w = box(NECK_L - CH_X0, y1w - y0w, z1 - z0, CH_X0, -y1w, z0)
            if zb == Z_B0:
                body = body.fuse(w)
            else:
                deck = deck.fuse(w)                # стенки верхнего этажа стоят на ПАЛУБЕ

# ============ ЗОНА: бобышки роликов, вырезы, щели ============
pins = []          # (x, y, z0, z1) осей
def boss_low(x, y):
    b = cyl(3.2, 1.0, x, y, 2.0)
    return b
def boss_high(x, y):
    return cyl(3.2, 1.0, x, y, DECK1)
roller_sites = []  # (name, x, y, layer, land_r)
for i, ln in enumerate(lanes):
    lx, zb, s = ln["x"], ln["zb"], ln["s"]
    y_in, y_out = ln["slots"]
    xa = lx - (R_ER + 0.35)
    xb = lx + (R_ER + 0.35)
    y_er = -s * (hw(lx) - 6.6) if ln["er_off"] is None else -s * ln["er_off"]
    roller_sites.append((f"er{i+1}", lx, y_er, zb, R_ER))
    yca = s * (y_out - R_CR)
    ycb = s * (y_in - R_CR)
    roller_sites.append((f"cr{i+1}a", xa + R_CR, yca, zb, R_CR))
    roller_sites.append((f"cr{i+1}b", xb + R_CR, ycb, zb, R_CR))
    # щели ножек: палуба (только нижний этаж) и крышка (все)
    if s > 0:
        ylo = y_er + R_ER + 1.7
        yhi = y_in - R_CR - 3.3
    else:
        ylo = -(y_in - R_CR - 3.3)
        yhi = y_er - R_ER - 1.7
    if zb == Z_B0:
        deck = deck.cut(box(3.6, yhi - ylo, 4, xa - 1.8, ylo, DECK0 - 1))
    cover = cover.cut(box(3.6, yhi - ylo, 4, xa - 1.8, ylo, COV0 - 1))

for name, x, y, zb, r in roller_sites:
    is_er = name.startswith("er")
    if zb == Z_B0:
        body = body.fuse(boss_low(x, y))
        body = body.cut(cyl(1.95, 12, x, y, -1))
        if is_er:                                            # посадка в палубу - только у петлевых
            deck = deck.cut(cyl(2.2, 4, x, y, DECK0 - 1))
    else:
        deck = deck.fuse(boss_high(x, y))
        deck = deck.cut(cyl(1.95, 12, x, y, DECK0 - 0.5))
        if is_er:
            cover = cover.cut(cyl(2.2, 4, x, y, COV0 - 1))

# ============ КРЕПЁЖ ПАЛУБЫ И КРЫШКИ (стойки M2) ============
col_xs = [30, 62.5, 96.5, 125, 180, 235, 265, 320, 400, 460, 500, 560, 592]
for k, cx in enumerate(col_xs):
    # нижняя стойка (дно -> палуба), y=0
    body = body.fuse(cyl(2.5, DECK0 - 2, cx, 0, 2))
    body = body.cut(cyl(0.85, 8, cx, 0, DECK0 - 8))
    deck = deck.cut(cyl(1.15, 4, cx, 0, DECK0 - 1))
    # верхняя стойка (палуба -> крышка), y = +-6 через одну
    uy = 6.0 if k % 2 == 0 else -6.0
    deck = deck.fuse(cyl(2.5, COV0 - DECK1, cx, uy, DECK1))
    deck = deck.cut(cyl(0.85, 8, cx, uy, COV0 - 8))
    cover = cover.cut(cyl(1.15, 4, cx, uy, COV0 - 1))

# заделы под будущие головные ролики (5-й мотор, v2)
for hy in (-10, 10):
    body = body.fuse(cyl(3.2, 1.5, 34, hy, 2))
    body = body.cut(cyl(1.95, 8, 34, hy, -1))

# ============ СЕГМЕНТЫ ============
def seg(shape, x0, x1):
    return shape.common(box(x1 - x0, 200, 60, x0, -100, -10))
S1 = seg(body, 20, 250); S2 = seg(body, 250, 480); S3 = seg(body, 480, NECK_L)
D1 = seg(deck, 21, 250); D2 = seg(deck, 250, 480); D3 = seg(deck, 480, NECK_L)
C1 = seg(cover, 21, 250); C2 = seg(cover, 250, 480); C3 = seg(cover, 480, NECK_L)
# стыковые пластины (снизу, 4 отв Ø2 под M2)
splice = box(40, 30, 1.8, 0, 0, 0)
for (px, py) in [(6, 6), (34, 6), (6, 24), (34, 24)]:
    splice = splice.cut(cyl(1.1, 4, px, py, -1))
for xj in (250, 480):
    for (pxo, pyo) in [(-20, -15)]:
        pass
    for sname, sh in [("S", None)]:
        pass
# отверстия под стыковые пластины в дне сегментов
for xj in (250, 480):
    for dx in (-14, 14):
        for dy in (-9, 9):
            hole = cyl(1.1, 6, xj + dx, dy, -1)
            S1 = S1.cut(hole); S2 = S2.cut(hole); S3 = S3.cut(hole)

# ============ ДЕКА-ПАНЕЛЬ с моторами ============
panel = box(200, 170, 3, NECK_L, -85, 0)
for i in range(4):
    mx, s = mot[i]
    y_in = lanes[i]["slots"][0]
    myc = s * (y_in + R_PIN)
    panel = panel.cut(cyl(18.6, 5, mx, myc, -1))
    for a0 in (55, 235):
        arc = Part.makeCylinder(24.5, 5, Vector(mx, myc, -1), Vector(0, 0, 1), 70)
        arc = arc.cut(cyl(21.4, 6, mx, myc, -1.5))
        arc.rotate(Vector(mx, myc, 0), Vector(0, 0, 1), a0)
        panel = panel.cut(arc)
    # разводчик
    zb = lanes[i]["zb"]
    x_sp = mx - 55 + 2
    y_sp = s * (lanes[i]["slots"][1] + 2)
    panel = panel.fuse(cyl(3.2, 1.0, x_sp, y_sp, 3.0))
    panel = panel.cut(cyl(1.95, 12, x_sp, y_sp, -1))
    # прорези под стяжки проводов рядом с мотором
    panel = panel.cut(box(8, 3.5, 6, mx - 4, myc + (26 if s > 0 else -29.5), -1))

# ============ РОЛИКИ (ступенчатые) ============
def stepped_roller(land_r, zb):
    """низ детали = z0 ленты-1; зубцы ленты внизу (3.2), гладкая сверху"""
    h_teeth, h_smooth = 3.4, 3.8
    r_under = land_r - 0.9
    p = cyl(land_r + 1.0, 0.8, 0, 0, 0)                       # нижний бортик
    p = p.fuse(cyl(r_under, h_teeth, 0, 0, 0.8))              # проточка под зубцы
    p = p.fuse(cyl(land_r, h_smooth, 0, 0, 0.8 + h_teeth))    # поясок (гладкая зона)
    p = p.fuse(cyl(land_r + 1.0, 0.8, 0, 0, 0.8 + h_teeth + h_smooth))
    p = p.cut(cyl(2.05, 12, 0, 0, -1))
    return p.removeSplitter()
add("Roller_ER", stepped_roller(R_ER, 0))
add("Roller_CR", stepped_roller(R_CR, 0))

# ============ ШЕСТЕРНИ-ЭТАЖЕРКИ ============
def pinion(z_teeth_bottom):
    p = cyl(4.5, z_teeth_bottom - 1.9 + 0.2, 0, 0, 1.9)       # колонна от посадки до зубьев
    disc = cyl(R_PIN, 3.6, 0, 0, z_teeth_bottom - 0.2)
    cuts = []
    for k in range(12):
        a = 2 * math.pi * k / 12
        u = Vector(math.cos(a), math.sin(a), 0)
        t = Vector(-math.sin(a), math.cos(a), 0)
        c = Vector(0, 0, z_teeth_bottom - 0.7)
        pp = [c + u*(R_PIN+0.15) + t*1.275, c + u*(R_PIN+0.15) - t*1.275,
              c + u*(R_PIN-1.37) - t*0.95, c + u*(R_PIN-1.37) + t*0.95]
        cuts.append(Part.Face(Part.makePolygon(pp + [pp[0]])).extrude(Vector(0, 0, 4.6)))
    p = p.fuse(disc.cut(cuts))
    p = p.cut(cyl(2.825, 4.3, 0, 0, 1.9))                     # посадка на шестерёнку 5.65
    p = p.cut(cyl(1.6, 30, 0, 0, 0))
    return p.removeSplitter()
add("Pinion_low", pinion(Z_B0))          # зубья 3.0..6.4
add("Pinion_high", pinion(Z_B1))         # зубья 13.8..17.2 (колонна)

# ============ ТЕЛЕЖКИ ============
def carriage(zb):
    # ЛОКАЛЬНЫЕ координаты: линия ленты (ветка A) = x0, ход тележки - по Y.
    smooth0 = zb + 3.4                                        # низ гладкой зоны ленты
    top_b = zb + BH + 0.3                                     # чуть выше верха ленты
    outer = box(1.8, 8, top_b - smooth0 + 1.2, -2.15, -4, smooth0)   # снаружи ленты + вверх
    inner = box(1.8, 8, BH - 3.4 - 0.4, 0.35, -4, smooth0)           # внутри петли
    bridge = box(3.45, 8, 1.2, -2.15, -4, top_b)                     # мостик над лентой
    stem = box(2.6, 8, COV1 + 0.4 - top_b, -1.3, -4, top_b)          # ножка в щель
    plat = box(16, 14, 1.8, -8, -7, COV1 + 0.4)
    rim = box(16, 14, 1.6, -8, -7, COV1 + 2.2).cut(box(13.2, 11.2, 3, -6.6, -5.6, COV1 + 2.1))
    outer_part = outer.fuse([bridge, stem, plat, rim]).removeSplitter()
    for sy in (-2.2, 2.2):
        h = Part.makeCylinder(1.1, 8, Vector(-4, sy, smooth0 + 1.6), Vector(1, 0, 0))
        outer_part = outer_part.cut(h)
        inner = inner.cut(h)
        inner = inner.cut(Part.makeCylinder(2.35, 1.2, Vector(2.16, sy, smooth0 + 1.6), Vector(-1, 0, 0)))
    return outer_part, inner.removeSplitter()
co_l, ci_l = carriage(Z_B0)
co_h, ci_h = carriage(Z_B1)
add("Carriage_low_outer", co_l); add("Carriage_low_inner", ci_l)
add("Carriage_high_outer", co_h); add("Carriage_high_inner", ci_h)

# ============ сборка/экспорт ============
add("Seg1_base", S1); add("Seg2_base", S2); add("Seg3_base", S3)
add("Deck1", D1); add("Deck2", D2); add("Deck3", D3)
add("Cover1", C1); add("Cover2", C2); add("Cover3", C3)
add("Deka_panel", panel)
add("Splice_x2", splice)
doc.recompute()
doc.saveAs(os.path.join(OUT, "Neck_kit.FCStd"))

os.makedirs(os.path.join(OUT, "print", "_свежее_из_скрипта"), exist_ok=True)
export = [("seg1_base", S1), ("seg2_base", S2), ("seg3_base", S3),
          ("deck1", D1), ("deck2", D2), ("deck3", D3),
          ("cover1", C1), ("cover2", C2), ("cover3", C3),
          ("deka_panel", panel), ("splice_x2", splice),
          ("roller_ER_x4", doc.getObject("Roller_ER").Shape),
          ("roller_CR_x8", doc.getObject("Roller_CR").Shape),
          ("pinion_low_x2", doc.getObject("Pinion_low").Shape),
          ("pinion_high_x2", doc.getObject("Pinion_high").Shape),
          ("carriage_low_outer_x2", co_l), ("carriage_low_inner_x2", ci_l),
          ("carriage_high_outer_x2", co_h), ("carriage_high_inner_x2", ci_h)]
for n, s in export:
    m = MeshPart.meshFromShape(Shape=s, LinearDeflection=0.05, AngularDeflection=0.3)
    Mesh.Mesh(m.Topology).write(os.path.join(OUT, "print", "_свежее_из_скрипта", n + ".stl"))
    print("stl:", n)
print("KIT SAVED, objects:", len(doc.Objects))
