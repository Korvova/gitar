# -*- coding: utf-8 -*-
"""ГИТАРА: КОРПУС в настоящих размерах классики (решения юзера 2026-07-29).
Восьмёрка 480 x 370, талия ~235, глубина 95 (как настоящая). Корпус свисает
ВНИЗ от плоскости грифа: крышка z 23..26 (уровень фретбордов), дно z -69..-66,
моторы NEMA17 (до z-48) прячутся внутри. Хребет (наша дека с моторами) стоит
на 9 тумбах от дна, винты М3 сверху сквозь дно хребта. Обечайка = лента PETG
1 мм плашмя, прикручивается М3 к бортикам 10x10 на дне и крышке (юзер).
Розетка Ø87 на классическом месте (y=570). Дно 4 куска, крышка 4 куска,
лента 6-7 сегментов — всё на стол 256.
Запуск: .venv-b123d\\Scripts\\python gitara_korpus.py
"""
import numpy as np
from build123d import *

OUT = r"C:\App\gitar\2-0\Print\Print"

# ---------------- контур восьмёрки (полуконтур восточной стороны) ----------
PROF = [(480, 60), (492, 100), (510, 124), (535, 138), (560, 140),
        (590, 134), (620, 124), (650, 118), (668, 117), (690, 121),
        (720, 136), (750, 158), (775, 174), (800, 183), (830, 185),
        (860, 181), (890, 168), (915, 147), (935, 118), (950, 82),
        (958, 44), (960, 0)]

def catmull(pts, per_seg=6):
    """Плотная полилиния Катмулла-Рома по опорным точкам."""
    p = np.array(pts, float)
    p = np.vstack([p[0], p, p[-1]])
    out = []
    for i in range(1, len(p) - 2):
        for t in np.linspace(0, 1, per_seg, endpoint=False):
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p[i]) + (-p[i - 1] + p[i + 1]) * t +
                       (2 * p[i - 1] - 5 * p[i] + 4 * p[i + 1] - p[i + 2]) * t2 +
                       (-p[i - 1] + 3 * p[i] - 3 * p[i + 1] + p[i + 2]) * t3))
    out.append(p[-2])
    return np.array(out)

half = catmull(PROF)                                   # (y, halfwidth) плотно
east = np.c_[half[:, 1], half[:, 0]][::-1]             # (x,y) от юга (0,960) к северу
west = np.c_[-half[:, 1], half[:, 0]]                  # зеркало, север -> юг
top = np.array([[x, 480.0] for x in np.linspace(55, -55, 12)])  # торец восток->запад
CONTOUR = np.vstack([east, top, west[:-1]])            # без повтора (0,960)

def poly_offset(pts, d):
    """Сдвиг замкнутого контура ВНУТРЬ на d (по вершинным нормалям)."""
    p = np.array(pts, float)
    e = np.roll(p, -1, 0) - p                          # рёбра
    en = e / np.linalg.norm(e, axis=1, keepdims=True)
    nrm = np.c_[-en[:, 1], en[:, 0]]                   # нормаль ребра
    vn = nrm + np.roll(nrm, 1, 0)
    vn /= np.linalg.norm(vn, axis=1, keepdims=True)
    # знак: центр восьмёрки (0, 720) должен быть со стороны нормали
    inward = vn if np.dot(vn[0], np.array([0, 720]) - p[0]) > 0 else -vn
    return p + inward * d, inward

C0, NIN = poly_offset(CONTOUR, 0)                      # контур + нормали внутрь
C1, _ = poly_offset(CONTOUR, 1.0)                      # внутренняя грань ленты
C11, _ = poly_offset(CONTOUR, 11.0)                    # внутренняя грань бортика

SEG = np.linalg.norm(np.roll(C0, -1, 0) - C0, axis=1)
S = np.r_[0, np.cumsum(SEG)]                           # дуговая длина вершин
P_LEN = S[-1]

def at_s(s):
    """(точка, нормаль внутрь) на дуговой позиции s."""
    s = s % P_LEN
    i = int(np.searchsorted(S, s, 'right')) - 1
    i = min(i, len(C0) - 1)
    t = (s - S[i]) / max(SEG[i], 1e-9)
    p2 = C0[(i + 1) % len(C0)]
    return C0[i] + (p2 - C0[i]) * t, NIN[i]

def face_of(poly):
    return make_face(Polyline(*[(x, y) for x, y in poly],
                              (poly[0][0], poly[0][1])))

F0, F1, F11 = face_of(C0), face_of(C1), face_of(C11)

Z_TOP0, Z_TOP1 = 23.0, 26.0                            # крышка (уровень фретбордов)
Z_BOT0, Z_BOT1 = -69.0, -66.0                          # дно
ROZ_Y, ROZ_R = 570.0, 43.5                             # розетка Ø87, классика

# проём грифа в северном торце: дуговые позиции x=+-28 на y=480
s_e = S[np.argmin(np.linalg.norm(C0 - [28, 480], axis=1))]
s_w = S[np.argmin(np.linalg.norm(C0 - [-28, 480], axis=1))]

def BB(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(
        abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))

def radial_holes(part, s_list, z):
    """Радиальные каналы Ø2.6 в бортике на дуговых позициях (под винты ленты)."""
    for s in s_list:
        p, n = at_s(s)
        ang = np.degrees(np.arctan2(n[1], n[0]))
        part -= (Pos(p[0], p[1], z) * Rot(0, 0, ang) * Rot(0, 90, 0) *
                 Pos(0, 0, 6) * Cylinder(1.3, 16))
    return part

# ---------------- дырки ленты: по сегментам, минуя проём --------------------
N_SEG = int(np.ceil(P_LEN / 238))
seg_len = P_LEN / N_SEG
phase = 0.0
while True:                                            # стыки сегментов не в проёме
    bnds = [(phase + i * seg_len) % P_LEN for i in range(N_SEG)]
    if all(not (s_e - 15 < b < s_w + 15) for b in bnds):
        break
    phase += 25
HOLES_S = []                                           # дуговые позиции всех винтов
SEG_HOLES = []                                         # то же по сегментам
for i in range(N_SEG):
    a, b = bnds[i], bnds[i] + seg_len
    hs = list(np.linspace(a + 8, b - 8, max(2, int(np.ceil((b - a) / 58)) + 1)))
    hs = [h for h in hs if not (s_e - 4 < (h % P_LEN) < s_w + 4)]   # в проёме пусто
    SEG_HOLES.append((a, b, hs))
    HOLES_S += [h % P_LEN for h in hs]

# ---------------- тумбы под хребет (мир x,y; верх z=0, винт сверху) --------
TUMBA = [(-15, 525), (-15, 585), (-15, 630), (-15, 685), (-15, 750),
         (20, 545), (20, 595), (20, 700), (20, 760)]
# крепёж крышки к стенкам хребта (вертикально, Ø3.2 в крышке / 2.6 в стенке)
TOP_SCREWS = [(sx, y) for y in (520, 580, 630, 690, 750) for sx in (-24, 24)]

# ================== ДНО ==================
# сплошное (хребет висит на тумбах высоко над ним), 4 куска: x=0 и y=720
dno = Pos(0, 0, Z_BOT0) * extrude(F1, Z_BOT1 - Z_BOT0)
dno += Pos(0, 0, Z_BOT1) * extrude(F1 - F11, 10)                   # бортик 10x10
for y in (600, 760, 840, 900):                                     # рёбра
    dno += (BB(-160, 160, y - 1.25, y + 1.25, Z_BOT1, Z_BOT1 + 6)
            & Pos(0, 0, Z_BOT1 + 3) * extrude(F11, 8, both=True))
for x, y in TUMBA:                                                 # тумбы хребта
    dno += BB(x - 8, x + 8, y - 8, y + 8, Z_BOT1, 0)
    dno -= Pos(x, y, -7) * Cylinder(1.3, 14.2)                     # канал М3
dno = radial_holes(dno, HOLES_S, Z_BOT1 + 5)                       # винты ленты

JD_Y = [(-130, 729), (-90, 729), (-45, 729), (45, 729), (90, 729), (130, 729)]
JD_X = [(9, y) for y in (510, 570, 640, 760, 810, 860, 910)]
slab = lambda z0, z1: Pos(0, 0, z0) * extrude(F1, z1 - z0)
polka_y = (slab(Z_BOT0, Z_BOT0 + 1.5) & BB(-185, 185, 720, 738, -80, 0))
polka_x = (slab(Z_BOT0, Z_BOT0 + 1.5) & BB(0, 18, 480, 960, -80, 0))
cut_y = BB(-185.1, 185.1, 720, 738, Z_BOT0 - 0.1, Z_BOT0 + 1.5)
cut_x = BB(0, 18, 479.9, 960.1, Z_BOT0 - 0.1, Z_BOT0 + 1.5)

def drill(part, pts, r, z0, z1):
    for x, y in pts:
        part -= Pos(x, y, (z0 + z1) / 2) * Cylinder(r, z1 - z0)
    return part

# запад несёт полку x-стыка, север несёт полку y-стыка
dno_w = dno & BB(-190, 0, 475, 965, -80, 5)
dno_w += polka_x
dno_e = dno & BB(0, 190, 475, 965, -80, 5)
dno_e -= cut_x
dno_nw = dno_w & BB(-190, 20, 475, 720, -80, 5)
dno_nw += (polka_y & BB(-190, 0, 700, 745, -80, 5))
dno_nw = drill(dno_nw, [p for p in JD_Y if p[0] < 0], 1.3, Z_BOT0 - 0.1, Z_BOT0 + 1.6)
dno_nw = drill(dno_nw, [p for p in JD_X if p[1] < 720], 1.6, Z_BOT0 - 0.1, Z_BOT1 + 0.1)
dno_ne = dno_e & BB(0, 190, 475, 720, -80, 5)
dno_ne += (polka_y & BB(0, 190, 700, 745, -80, 5))
dno_ne = drill(dno_ne, [p for p in JD_Y if p[0] > 0], 1.3, Z_BOT0 - 0.1, Z_BOT0 + 1.6)
dno_ne = drill(dno_ne, [p for p in JD_X if p[1] < 720], 1.3, Z_BOT0 + 1.4, Z_BOT0 + 3.2)
dno_sw = dno_w & BB(-190, 20, 720, 965, -80, 5)
dno_sw -= cut_y
dno_sw = drill(dno_sw, [p for p in JD_Y if p[0] < 0], 1.6, Z_BOT0 - 0.1, Z_BOT1 + 0.1)
dno_sw = drill(dno_sw, [p for p in JD_X if p[1] > 720], 1.6, Z_BOT0 - 0.1, Z_BOT1 + 0.1)
dno_se = dno_e & BB(0, 190, 720, 965, -80, 5)
dno_se -= cut_y
dno_se = drill(dno_se, [p for p in JD_Y if p[0] > 0], 1.6, Z_BOT0 - 0.1, Z_BOT1 + 0.1)
dno_se = drill(dno_se, [p for p in JD_X if p[1] > 720], 1.3, Z_BOT0 + 1.4, Z_BOT0 + 3.2)

# ================== КРЫШКА ==================
top_p = slab_t = Pos(0, 0, Z_TOP0) * extrude(F1, Z_TOP1 - Z_TOP0)
top_p -= Pos(0, ROZ_Y, Z_TOP0 + 1.5) * Cylinder(ROZ_R, 3.2)        # розетка
ring = Pos(0, ROZ_Y, Z_TOP0 - 3) * (Cylinder(ROZ_R + 5.5, 6) -
                                    Cylinder(ROZ_R + 2.5, 6.2))    # кольцо-ребро
top_p += ring - BB(-27.2, 27.2, 478, 801, Z_TOP0 - 10, Z_TOP0)     # мимо хребта
bort_t = Pos(0, 0, Z_TOP0 - 10) * extrude(F1 - F11, 10)            # бортик вниз
bort_t -= BB(-28, 28, 470, 500, Z_TOP0 - 10.1, Z_TOP0 + 0.1)       # проём грифа
top_p += bort_t
for y in (700, 800, 880):                                          # рёбра снизу
    top_p += ((BB(-160, 160, y - 1.25, y + 1.25, Z_TOP0 - 6, Z_TOP0)
               & Pos(0, 0, Z_TOP0 - 3) * extrude(F11, 8, both=True))
              - BB(-27.2, 27.2, 478, 801, Z_TOP0 - 10, Z_TOP0))    # мимо хребта
top_p = drill(top_p, TOP_SCREWS, 1.6, Z_TOP0 - 0.1, Z_TOP1 + 0.1)  # к хребту
top_p = radial_holes(top_p, HOLES_S, Z_TOP0 - 5)                   # винты ленты

JT_Y = [(-125, 729), (-80, 729), (-35, 729), (20, 729), (100, 729), (140, 729)]
JT_X = [(69, y) for y in (500, 560, 620, 690, 742, 800, 860, 915)]
polka_ty = (Pos(0, 0, Z_TOP0) * extrude(F1, 1.5)) & BB(-185, 185, 720, 738, 0, 30)
polka_tx = (Pos(0, 0, Z_TOP0) * extrude(F1, 1.5)) & BB(60, 78, 480, 960, 0, 30)
cut_ty = BB(-185.1, 185.1, 720, 738, Z_TOP0 - 0.1, Z_TOP0 + 1.5)
cut_tx = BB(60, 78, 479.9, 960.1, Z_TOP0 - 0.1, Z_TOP0 + 1.5)

top_w = top_p & BB(-190, 60, 475, 965, 0, 30)
top_w += polka_tx
top_e = top_p & BB(60, 190, 475, 965, 0, 30)
top_e -= cut_tx
top_wn = top_w & BB(-190, 80, 475, 720, 0, 30)
top_wn += (polka_ty & BB(-190, 78, 700, 745, 0, 30))
top_wn = drill(top_wn, [p for p in JT_Y if p[0] < 60], 1.3, Z_TOP0 - 0.1, Z_TOP0 + 1.6)
top_ws = top_w & BB(-190, 80, 720, 965, 0, 30)
top_ws -= cut_ty
top_ws = drill(top_ws, [p for p in JT_Y if p[0] < 60], 1.6, Z_TOP0 - 0.1, Z_TOP1 + 0.1)
top_ws = drill(top_ws, [p for p in JT_X if p[1] > 738], 1.6, Z_TOP0 - 0.1, Z_TOP1 + 0.1)
top_wn = drill(top_wn, [p for p in JT_X if p[1] < 720], 1.6, Z_TOP0 - 0.1, Z_TOP1 + 0.1)
top_en = top_e & BB(60, 190, 475, 720, 0, 30)
top_en += (polka_ty & BB(78, 190, 700, 745, 0, 30))
top_en = drill(top_en, [p for p in JT_Y if p[0] > 60], 1.3, Z_TOP0 - 0.1, Z_TOP0 + 1.6)
top_en = drill(top_en, [p for p in JT_X if p[1] < 720], 1.3, Z_TOP0 + 1.4, Z_TOP0 + 3.2)
top_es = top_e & BB(60, 190, 720, 965, 0, 30)
top_es -= cut_ty
top_es = drill(top_es, [p for p in JT_Y if p[0] > 60], 1.6, Z_TOP0 - 0.1, Z_TOP1 + 0.1)
top_es = drill(top_es, [p for p in JT_X if p[1] > 738], 1.3, Z_TOP0 + 1.4, Z_TOP0 + 3.2)

# ================== ЛЕНТА ОБЕЧАЙКИ (плоские сегменты + гнутая для сцены) ====
H_BAND = 95.0                                          # z -69..26
bands = []
for i, (a, b, hs) in enumerate(SEG_HOLES):
    L = b - a
    seg = BB(0, L, 0, H_BAND, 0, 1)
    for h in hs:                                       # два ряда дырок Ø3.2
        for zz in (Z_BOT1 + 5, Z_TOP0 - 5):
            seg -= Pos(h - a, zz - Z_BOT0, 0.5) * Cylinder(1.6, 1.2)
    if a < s_e < b or a < s_w < b or (a < s_e and b > s_w):        # проём грифа
        ea, eb = max(s_e - a, 0), min(s_w - a, L)
        seg -= BB(ea, eb, H_BAND - 26, H_BAND + 0.1, -0.1, 1.1)
        seg += BB(ea, eb, H_BAND - 34, H_BAND - 26, 1, 9)          # приступок пятки
    bands.append(seg)

bent = Pos(0, 0, Z_BOT0) * extrude(F0 - F1, H_BAND)                # для сцены
bent -= BB(-28, 28, 470, 500, 0, Z_TOP1 + 0.1)
bent += BB(-28, 28, 479, 481 + 8, -8, 0) & Pos(0, 0, -4) * extrude(F1, 8, both=True)

# ================== ЭКСПОРТ ==================
parts = [("gk_dno_ne", dno_ne), ("gk_dno_nw", dno_nw),
         ("gk_dno_se", dno_se), ("gk_dno_sw", dno_sw),
         ("gk_top_wn", top_wn), ("gk_top_ws", top_ws),
         ("gk_top_en", top_en), ("gk_top_es", top_es),
         ("gk_band_bent", bent)]
parts += [(f"gk_band{i}", bands[i]) for i in range(N_SEG)]
for name, part in parts:
    p = part if isinstance(part, Part) else Part() + part
    export_stl(p, rf"{OUT}\{name}.stl")
    print(f"{name}: volume={p.volume:.0f} mm3, solids={len(p.solids())}")
print(f"export done: периметр {P_LEN:.0f}, сегментов ленты {N_SEG}, "
      f"дырок ленты {len(HOLES_S)} на ряд")

# ================= ПРОВЕРКИ =================
from clearance import Assembly

asm = Assembly()
for nm in ("dno_ne", "dno_nw", "dno_se", "dno_sw",
           "top_wn", "top_ws", "top_en", "top_es"):
    asm.add(nm, rf"{OUT}\gk_{nm}.stl")
asm.add("bent", rf"{OUT}\gk_band_bent.stl")
asm.add("dk1", rf"{OUT}\gdk1_base.stl", loc=(0, 480, 0))
asm.add("dk2", rf"{OUT}\gdk2_base.stl", loc=(0, 640, 0))
touch = [("dno_ne", "dno_se"), ("dno_nw", "dno_sw"), ("dno_se", "dno_sw"),
         ("top_wn", "top_ws"), ("top_en", "top_es"), ("top_wn", "top_en"),
         ("top_ws", "top_es"),
         ("dno_ne", "dk1"), ("dno_nw", "dk1"),          # тумбы под дном хребта
         ("dno_se", "dk2"), ("dno_sw", "dk2"),
         ("top_wn", "dk1"), ("top_ws", "dk2"),          # крышка на стенках хребта
         ("bent", "dno_ne"), ("bent", "top_ws")]        # лента у бортиков
clear = [("dno_ne", "top_en", 5), ("bent", "dk1", 0.0)]
asm.check(clearances=clear, touching=touch, verbose=False)
# стыковые дырки: кольца замкнуты
asm.check_holes("dno_ne", [(x, y, Z_BOT0 + 0.7, 1.3) for x, y in JD_Y if x > 0],
                verbose=False)
asm.check_holes("top_ws", [(x, y, Z_TOP1 - 0.7, 1.6) for x, y in JT_Y if x < 60]
                + [(x, y, Z_TOP0 + 0.7, 1.6) for x, y in JT_X if y > 738],
                verbose=False)
# тумбы: каналы соосны дыркам в дне хребта (Ø3.4 в деке, мир TUMBA)
import numpy as _np
for x, y in TUMBA:
    dk = "dk1" if y < 640 else "dk2"
    pts = _np.array([[x, y, 1.5]])
    if asm.meshes[dk].contains(pts).any():
        print(f"  FAIL тумба ({x},{y}): дырка хребта не открыта")
        raise SystemExit(1)
print("корпус: каркас чист")
