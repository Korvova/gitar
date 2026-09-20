# -*- coding: utf-8 -*-
"""
G-code платы 4 моторов -> TTC3018 (MKS DLC32, GRBL, Candle). Способ: маркер + травление.

Рабочее поле станка 100 x 100 мм, плата 141 x 90 — делается ДВУМЯ ПОЛОВИНАМИ.
Заготовка 100 x 150, медью ВВЕРХ, длинной стороной от себя, левым краем вдоль упора
(линейка или рейка, прижатая к столу): между половинами заготовка сдвигается по упору на себя.

Координаты: X = y KiCad, Y = W - x KiCad. Зеркало для рисунка со стороны меди даёт
переворот оси Y (у KiCad она вниз, у станка — от оператора). Штыри моторов слева, USB к оператору.

Четыре крестика остаются в меди как метки: Б (ближний), СЛ и СП (средние левый и правый), Д (дальний).
Каждый файл сам выставляется по крестику и проверяется по второму, поэтому между файлами
заготовку можно двигать (смещение маркера от шпинделя мерить не надо).

  A1_marker.nc  маркер.  X0Y0 = кончик маркера над левым ближним углом заготовки. Рисует Б, СЛ, СП и ближнюю половину.
  A2_sverlo.nc  сверло 1.0. X0Y0 = сверло над центром Б. Пауза над СЛ — проверить. Сверлит ближнюю половину.
  --- сдвинуть заготовку по упору на себя примерно на 70 мм ---
  B1_marker.nc  маркер.  X0Y0 = маркер над центром СЛ. Пауза над СП — проверить. Рисует дальнюю половину и Д.
  B2_sverlo.nc  сверло 1.0. X0Y0 = сверло над центром СЛ. Пауза над СП — проверить. Сверлит дальнюю половину.
Z0 всегда = инструмент касается меди.

Запуск: "%LOCALAPPDATA%\\Programs\\KiCad\\10.0\\bin\\python.exe" make_gcode.py
"""
import os
import math
import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
BOARD_FILE = os.path.join(HERE, "plata_4_motora.kicad_pcb")
OUTDIR = os.path.join(HERE, "gcode")
os.makedirs(OUTDIR, exist_ok=True)
for old in os.listdir(OUTDIR):
    if old[0] in "12AB" and old.endswith(".nc"):
        os.remove(os.path.join(OUTDIR, old))

OX, OY = 5.0, 4.5                      # отступ платы от левого ближнего угла заготовки
SPLIT_KX = 66.0                        # линия раздела половин, координата x KiCad
OVERLAP = 1.5                          # дорожки через раздел рисуются с нахлёстом
CROSS_K = {"B": (126.7, 40.0), "SL": (66.2, 9.5), "SP": (66.0, 80.0), "D": (10.0, 45.0)}   # KiCad
CROSS_ARM = 3.0
PEN = 1.0
PEN_DOWN, PEN_UP, PEN_FEED, PEN_PLUNGE = -1.0, 2.0, 450, 300
SAFE_Z, DRILL_DEPTH, DRILL_PECK, DRILL_FEED = 3.0, -1.9, -0.9, 50
SPINDLE = "S1000"

board = pcbnew.LoadBoard(BOARD_FILE)
mm = pcbnew.ToMM
BW = mm(board.GetBoardEdgesBoundingBox().GetWidth())


def m(x, y):
    return (y + OX, BW - x + OY)


Y_SPLIT = m(SPLIT_KX, 0)[1]
CROSS = {k: m(*v) for k, v in CROSS_K.items()}


def fat_line(a, b, w):
    """Линия шириной w маркером PEN: два прохода по кромкам (заодно двойной слой)."""
    off = max(0.0, (w - PEN) / 2)
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(dx, dy)
    if n < 1e-6:
        return [(a, a)]
    nx, ny = -dy / n * off, dx / n * off
    return [((a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny)), ((b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny))]


def clip(seg, lo, hi):
    """Отрезок, обрезанный по Y в [lo, hi]; None — если целиком снаружи."""
    (x1, y1), (x2, y2) = seg
    if max(y1, y2) < lo or min(y1, y2) > hi:
        return None
    if abs(y2 - y1) < 1e-9:
        return seg

    def at(y):
        t = (y - y1) / (y2 - y1)
        return (x1 + t * (x2 - x1), y)
    p1 = (x1, y1) if lo <= y1 <= hi else at(lo if y1 < lo else hi)
    p2 = (x2, y2) if lo <= y2 <= hi else at(lo if y2 < lo else hi)
    return (p1, p2)


segs = []          # отрезки дорожек (станок)
for t in board.GetTracks():
    s, e = t.GetStart(), t.GetEnd()
    segs += fat_line(m(mm(s.x), mm(s.y)), m(mm(e.x), mm(e.y)), mm(t.GetWidth()))

pads, holes = [], []     # pads: (центр, [штрихи-полилинии])
for fp in board.GetFootprints():
    for pad in fp.Pads():
        pos = pad.GetPosition()
        kx, ky = mm(pos.x), mm(pos.y)
        c = m(kx, ky)
        holes.append(c)
        if pad.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
            continue
        bb = pad.GetBoundingBox()
        w, h = mm(bb.GetWidth()), mm(bb.GetHeight())
        if abs(w - h) < 0.05:
            r = max(0.05, (w - PEN) / 2)
            ring = [(c[0] + r * math.cos(k * math.pi / 6), c[1] + r * math.sin(k * math.pi / 6)) for k in range(13)]
            pads.append((c, [[c] + ring + [c]]))
        else:
            d = abs(h - w) / 2
            a, b = (m(kx, ky - d), m(kx, ky + d)) if h > w else (m(kx - d, ky), m(kx + d, ky))
            pads.append((c, [[p, q] for p, q in fat_line(a, b, min(w, h))]))


def cross_strokes(c):
    return [[(c[0] - CROSS_ARM, c[1]), (c[0] + CROSS_ARM, c[1])], [(c[0], c[1] - CROSS_ARM), (c[0], c[1] + CROSS_ARM)]]


def order_strokes(strokes, start):
    out, cur, rest = [], start, strokes[:]
    while rest:
        i = min(range(len(rest)), key=lambda k: min(math.dist(cur, rest[k][0]), math.dist(cur, rest[k][-1])))
        st = rest.pop(i)
        if math.dist(cur, st[-1]) < math.dist(cur, st[0]):
            st = st[::-1]
        out.append(st)
        cur = st[-1]
    return out


def half(near):
    lo, hi = (-1e9, Y_SPLIT + OVERLAP) if near else (Y_SPLIT - OVERLAP, 1e9)
    strokes = []
    for sg in segs:
        c = clip(sg, lo, hi)
        if c:
            strokes.append([c[0], c[1]])
    for c, sts in pads:
        if (c[1] <= Y_SPLIT) == near:
            strokes += sts
    hl = [h for h in holes if (h[1] <= Y_SPLIT) == near]
    return strokes, hl


def write_marker(name, strokes, crosses, origin, check, title):
    ox, oy = origin
    g = ["(%s)" % title, "G21 G90 G94", "G17", "M5", "G0 Z%.1f" % PEN_UP]
    if check:
        g += ["G0 X%.3f Y%.3f" % (check[0] - ox, check[1] - oy), "G0 Z0.5",
              "M0 (proverka: marker nad centrom krestika SP? da - prodolzhit)", "G0 Z%.1f" % PEN_UP]
    allst = [s for c in crosses for s in cross_strokes(c)] + order_strokes(strokes, origin)
    for st in allst:
        g += ["G0 X%.3f Y%.3f" % (st[0][0] - ox, st[0][1] - oy), "G1 Z%.2f F%d" % (PEN_DOWN, PEN_PLUNGE)]
        g += ["G1 X%.3f Y%.3f F%d" % (p[0] - ox, p[1] - oy, PEN_FEED) for p in st[1:]]
        g.append("G0 Z%.1f" % PEN_UP)
    g += ["G0 Z10", "G0 X0 Y0", "M2"]
    open(os.path.join(OUTDIR, name), "w").write("\n".join(g) + "\n")
    pts = [p for st in allst for p in st]
    return (min(p[0] for p in pts), max(p[0] for p in pts), min(p[1] for p in pts), max(p[1] for p in pts),
            sum(math.dist(a, b) for st in allst for a, b in zip(st, st[1:])) / 1000)


def write_drill(name, hl, origin, check, title, check_name):
    ox, oy = origin
    rest, cur, order = sorted(set((round(h[0], 3), round(h[1], 3)) for h in hl)), check, []
    while rest:
        i = min(range(len(rest)), key=lambda k: math.dist(cur, rest[k]))
        cur = rest.pop(i)
        order.append(cur)
    g = ["(%s)" % title, "G21 G90 G94", "G17", "G0 Z%.1f" % SAFE_Z,
         "G0 X%.3f Y%.3f" % (check[0] - ox, check[1] - oy), "G0 Z0.5",
         "M0 (proverka: sverlo nad centrom krestika %s? da - prodolzhit)" % check_name,
         "G0 Z%.1f" % SAFE_Z, "M3 %s" % SPINDLE, "G4 P2"]
    for x, y in order:
        g += ["G0 X%.3f Y%.3f" % (x - ox, y - oy), "G1 Z%.2f F%d" % (DRILL_PECK, DRILL_FEED), "G0 Z0.3",
              "G1 Z%.2f F%d" % (DRILL_DEPTH, DRILL_FEED), "G0 Z%.1f" % SAFE_Z]
    g += ["M5", "G0 Z10", "G0 X0 Y0", "M2"]
    open(os.path.join(OUTDIR, name), "w").write("\n".join(g) + "\n")
    return len(order)


sA, hA = half(True)
sB, hB = half(False)
eA = write_marker("A1_marker.nc", sA, [CROSS["B"], CROSS["SL"], CROSS["SP"]], (0.0, 0.0), None,
                  "A1 MARKER blizhnyaya polovina. X0Y0 = marker nad levym blizhnim uglom zagotovki, Z0 = kasanie medi")
nA = write_drill("A2_sverlo.nc", hA, CROSS["B"], CROSS["SL"],
                 "A2 SVERLO 1.0 blizhnyaya polovina. X0Y0 = sverlo nad centrom krestika B (blizhniy), Z0 = med", "SL")
eB = write_marker("B1_marker.nc", sB, [CROSS["D"]], CROSS["SL"], CROSS["SP"],
                  "B1 MARKER dalnyaya polovina. X0Y0 = marker nad centrom krestika SL (sredniy leviy), Z0 = kasanie medi")
nB = write_drill("B2_sverlo.nc", hB, CROSS["SL"], CROSS["SP"],
                 "B2 SVERLO 1.0 dalnyaya polovina. X0Y0 = sverlo nad centrom krestika SL, Z0 = med", "SP")
print("A1: X %.1f..%.1f  Y %.1f..%.1f  %.1f m" % eA, "| A2: %d otv" % nA)
print("B1: X %.1f..%.1f  Y %.1f..%.1f  %.1f m" % eB, "| B2: %d otv" % nB, "| razdel Y = %.1f" % Y_SPLIT)

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 14), dpi=100)
    ax.add_patch(plt.Rectangle((0, 0), 100, 150, fc="#c9814a", ec="k"))
    for strokes, col in ((sA, "#1b2a8a"), (sB, "#0b6b3a")):
        for st in strokes:
            ax.plot([p[0] for p in st], [p[1] for p in st], color=col, lw=2.4, solid_capstyle="round")
    for k, c in CROSS.items():
        for st in cross_strokes(c):
            ax.plot([p[0] for p in st], [p[1] for p in st], color="#b00020", lw=2.4)
        ax.text(c[0] + 3.5, c[1] + 1.5, {"B": "Б", "SL": "СЛ", "SP": "СП", "D": "Д"}[k], color="#b00020",
                fontsize=13, weight="bold")
    for h in holes:
        ax.add_patch(plt.Circle(h, 0.5, fc="white", ec="none", zorder=5))
    ax.axhline(Y_SPLIT, color="k", ls="--", lw=1)
    ax.text(101, Y_SPLIT, "раздел", fontsize=10, va="center")
    ax.plot(0, 0, "r+", ms=25, mew=3)
    ax.text(2, -5, "X0 Y0 файла A1 — маркер над левым ближним углом заготовки", color="r", fontsize=11)
    ax.set_xlim(-5, 112)
    ax.set_ylim(-9, 155)
    ax.set_aspect("equal")
    ax.set_title("Вид сверху на станок, оператор снизу. Синее — половина A, зелёное — половина B, красное — крестики")
    fig.savefig(os.path.join(HERE, "gcode_preview.png"), bbox_inches="tight")
    print("preview: gcode_preview.png")
except ImportError:
    print("matplotlib net - bez kartinki")
