# -*- coding: utf-8 -*-
"""
G-code платы 4 моторов -> TTC3018 (MKS DLC32, GRBL, Candle). Способ: маркер + травление.

Заготовка 100 x 150, медью ВВЕРХ, длинной стороной ОТ СЕБЯ (по X у станка ~125 мм хода).
Координаты: X = y KiCad, Y = W - x KiCad (поворот без зеркала в сырых координатах; зеркало
для рисунка со стороны меди даёт сам переворот оси Y). Штыри моторов — слева, USB — к оператору.

  1_marker.nc   — маркер (шпиндель выключен). X0 Y0 = кончик маркера над левым ближним
                  углом заготовки, Z0 = маркер касается меди. Рисует два крестика на свободных местах платы
                  (ближний и дальний, в меди они останутся как метки) и всю плату. Прижимы — посередине ближнего и дальнего краёв.
  2_sverlo_1.0.nc — сверло 1.0. Смещение маркера от шпинделя мерить не надо:
                  X0 Y0 = сверло точно над центром БЛИЖНЕГО к себе крестика, Z0 = сверло касается меди.
                  Файл сначала уходит к дальнему крестику и встаёт на паузу в 0.5 мм над медью —
                  проверить, что попал в центр, и продолжить (Pause/Resume в Candle).

Запуск: "%LOCALAPPDATA%\\Programs\\KiCad\\10.0\\bin\\python.exe" make_gcode.py
"""
import os
import math
import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
BOARD_FILE = os.path.join(HERE, "plata_4_motora.kicad_pcb")
OUTDIR = os.path.join(HERE, "gcode")
os.makedirs(OUTDIR, exist_ok=True)

OX, OY = 5.0, 4.5                      # левый верхний угол платы KiCad в координатах маркера
CROSS_K = [(126.7, 40.0), (10.0, 45.0)]    # крестики синхронизации (координаты маркера): свободные места платы слева и справа
CROSS_ARM = 3.0
PEN = 1.0                              # ширина линии маркера
PEN_DOWN, PEN_UP, PEN_FEED, PEN_PLUNGE = -1.0, 2.0, 450, 300
SAFE_Z, DRILL_DEPTH, DRILL_PECK, DRILL_FEED = 3.0, -1.9, -0.9, 50
SPINDLE = "S1000"

board = pcbnew.LoadBoard(BOARD_FILE)
mm = pcbnew.ToMM


BW = mm(board.GetBoardEdgesBoundingBox().GetWidth())


def m(x, y):
    # плата повёрнута: длинная сторона — вдоль Y станка (по X у станка всего ~125 мм хода)
    return (round(y + OX, 3), round(BW - x + OY, 3))


CROSS = [m(*c) for c in CROSS_K]


# ---------- штрихи маркера ----------
strokes = []   # каждый штрих: список точек, рисуется без подъёма


def fat_line(a, b, w):
    """Линия шириной w маркером PEN: туда по одной кромке, обратно по другой (заодно двойной слой)."""
    off = max(0.0, (w - PEN) / 2)
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(dx, dy)
    if n < 1e-6:
        return [a, a]
    nx, ny = -dy / n * off, dx / n * off
    return [(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny), (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny),
            (a[0] + nx, a[1] + ny)]


for t in board.GetTracks():
    s, e = t.GetStart(), t.GetEnd()
    strokes.append(fat_line(m(mm(s.x), mm(s.y)), m(mm(e.x), mm(e.y)), mm(t.GetWidth())))

holes = []
for fp in board.GetFootprints():
    for pad in fp.Pads():
        pos = pad.GetPosition()
        kx, ky = mm(pos.x), mm(pos.y)
        c = m(kx, ky)
        holes.append((c, mm(pad.GetDrillSize().x), fp.GetReference()))
        if pad.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
            continue
        bb = pad.GetBoundingBox()                       # уже с учётом поворота
        w, h = mm(bb.GetWidth()), mm(bb.GetHeight())
        if abs(w - h) < 0.05:                           # круглая: кольцо + точка
            r = max(0.05, (w - PEN) / 2)
            ring = [(c[0] + r * math.cos(k * math.pi / 6), c[1] + r * math.sin(k * math.pi / 6)) for k in range(13)]
            strokes.append([c] + ring + [c])
        elif h > w:                                     # овал вдоль Y
            strokes.append(fat_line(m(kx, ky - (h - w) / 2), m(kx, ky + (h - w) / 2), w))
        else:                                           # овал вдоль X
            strokes.append(fat_line(m(kx - (w - h) / 2, ky), m(kx + (w - h) / 2, ky), h))

# уголки контура платы — по ним потом резать
bbx = board.GetBoardEdgesBoundingBox()
W, H = mm(bbx.GetWidth()), mm(bbx.GetHeight())
for cx, cy, sx, sy in ((0, 0, 1, 1), (W, 0, -1, 1), (0, H, 1, -1), (W, H, -1, -1)):
    strokes.append([m(cx + sx * 5, cy), m(cx, cy), m(cx, cy + sy * 5)])

# порядок: жадно к ближайшему началу штриха
ordered, cur, rest = [], (0.0, 0.0), strokes[:]
while rest:
    i = min(range(len(rest)), key=lambda k: min(math.dist(cur, rest[k][0]), math.dist(cur, rest[k][-1])))
    st = rest.pop(i)
    if math.dist(cur, st[-1]) < math.dist(cur, st[0]):
        st = st[::-1]
    ordered.append(st)
    cur = st[-1]


def pen_stroke(pts):
    out = ["G0 X%.3f Y%.3f" % pts[0], "G1 Z%.2f F%d" % (PEN_DOWN, PEN_PLUNGE)]
    out += ["G1 X%.3f Y%.3f F%d" % (p[0], p[1], PEN_FEED) for p in pts[1:]]
    out.append("G0 Z%.1f" % PEN_UP)
    return out


g = ["(1: MARKER, shpindel vyklyuchen. X0Y0 = marker nad levym blizhnim uglom zagotovki 100x150 (dlinnaya storona ot sebya), Z0 = kasanie medi)",
     "G21 G90 G94", "G17", "M5", "G0 Z%.1f" % PEN_UP]
for cx, cy in CROSS:
    g += pen_stroke([(cx - CROSS_ARM, cy), (cx + CROSS_ARM, cy)])
    g += pen_stroke([(cx, cy - CROSS_ARM), (cx, cy + CROSS_ARM)])
for st in ordered:
    g += pen_stroke(st)
g += ["G0 Z10", "G0 X0 Y0", "M2"]
open(os.path.join(OUTDIR, "1_marker.nc"), "w").write("\n".join(g) + "\n")

# ---------- сверловка: ноль = центр левого крестика ----------
c0 = CROSS[0]
pts = sorted({(round(c[0] - c0[0], 3), round(c[1] - c0[1], 3)) for c, d, ref in holes})
order, cur, rest = [], (CROSS[1][0] - c0[0], CROSS[1][1] - c0[1]), list(pts)
while rest:
    i = min(range(len(rest)), key=lambda k: math.dist(cur, rest[k]))
    cur = rest.pop(i)
    order.append(cur)
g = ["(2: SVERLO 1.0. X0Y0 = sverlo nad centrom BLIZHNEGO k sebe krestika, Z0 = kasanie medi)",
     "G21 G90 G94", "G17", "G0 Z%.1f" % SAFE_Z,
     "G0 X%.3f Y%.3f" % (CROSS[1][0] - c0[0], CROSS[1][1] - c0[1]), "G0 Z0.5",
     "M0 (proverka: sverlo nad centrom DALNEGO krestika? da - prodolzhit)",
     "G0 Z%.1f" % SAFE_Z, "M3 %s" % SPINDLE, "G4 P2"]
for x, y in order:
    g += ["G0 X%.3f Y%.3f" % (x, y), "G1 Z%.2f F%d" % (DRILL_PECK, DRILL_FEED), "G0 Z0.3",
          "G1 Z%.2f F%d" % (DRILL_DEPTH, DRILL_FEED), "G0 Z%.1f" % SAFE_Z]
g += ["M5", "G0 Z10", "G0 X0 Y0", "M2"]
open(os.path.join(OUTDIR, "2_sverlo_1.0.nc"), "w").write("\n".join(g) + "\n")

xs = [p[0] for st in ordered for p in st]
ys = [p[1] for st in ordered for p in st]
length = sum(math.dist(a, b) for st in ordered for a, b in zip(st, st[1:]))
print("marker: %d shtrihov, %.1f m, pole X %.1f..%.1f  Y %.1f..%.1f" % (len(ordered), length / 1000, min(xs), max(xs), min(ys), max(ys)))
print("sverlo: %d otverstiy" % len(order))

# ---------- картинка для проверки: как ляжет на заготовку (вид сверху на станок) ----------
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 14), dpi=100)
    ax.add_patch(plt.Rectangle((0, 0), 100, 150, fc="#c9814a", ec="k"))
    for st in ordered:
        ax.plot([p[0] for p in st], [p[1] for p in st], color="#1b2a8a", lw=2.6, solid_capstyle="round")
    for cx, cy in CROSS:
        ax.plot([cx - 3, cx + 3], [cy, cy], color="#1b2a8a", lw=2.6)
        ax.plot([cx, cx], [cy - 3, cy + 3], color="#1b2a8a", lw=2.6)
    for c, d, ref in holes:
        ax.add_patch(plt.Circle(c, max(d, 1.0) / 2, fc="white", ec="none", zorder=5))
    ax.plot(0, 0, "r+", ms=25, mew=3)
    ax.text(2, -4, "X0 Y0 маркера — левый ближний угол заготовки", color="r", fontsize=11)
    ax.set_xlim(-5, 105)
    ax.set_ylim(-8, 155)
    ax.set_aspect("equal")
    ax.set_title("Вид сверху на станок: оператор снизу. Заготовка 100x150 (длинная сторона — от себя), синее — маркер, белое — отверстия")
    fig.savefig(os.path.join(HERE, "gcode_preview.png"), bbox_inches="tight")
    print("preview: gcode_preview.png")
except ImportError:
    print("matplotlib net - bez kartinki")
