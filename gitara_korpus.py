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
ROZ_Y, ROZ_R = 665.0, 43.5                # розетка Ø87 у талии, как у настоящей

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
TOP_SCREWS = [(sx, y) for y in (486, 520, 580, 615, 715, 760) for sx in (-24, 24)]

# ================== ДНО ==================
# сплошное (хребет висит на тумбах высоко над ним), 4 куска: x=0 и y=720
dno = Pos(0, 0, Z_BOT0) * extrude(F1, Z_BOT1 - Z_BOT0)
dno += Pos(0, 0, Z_BOT1) * extrude(F1 - F11, 10)                   # бортик 10x10
for y in (600, 760, 840, 900):                                     # рёбра
    dno += ((BB(-160, 160, y - 1.25, y + 1.25, Z_BOT1, Z_BOT1 + 6)
             & Pos(0, 0, Z_BOT1 + 3) * extrude(F11, 8, both=True))
            - BB(-24, 24, 770, 960, Z_BOT1 - 1, Z_BOT1 + 7))   # проём планки
for x, y in TUMBA:                                                 # тумбы хребта
    dno += BB(x - 8, x + 8, y - 8, y + 8, Z_BOT1, 0)
    dno -= Pos(x, y, -7) * Cylinder(1.3, 14.2)                     # канал М3
dno = radial_holes(dno, HOLES_S, Z_BOT1 + 5)                       # винты ленты

# стыки кусков БЕЗ встречных полок (нависали при печати — юзер) — плоские
# торцы + ПЛАНКИ-накладки изнутри на винтах М3х4 (каналы Ø2.6 не насквозь)
JD_Y = [(sx * x, y) for sx in (-1, 1) for x in (50, 78, 100) for y in (710, 730)]
JD_X = [(sx * 10, y) for sx in (-1, 1) for y in (785, 835, 885, 920)]
for x, y in JD_Y + JD_X:
    dno -= Pos(x, y, -67.25) * Cylinder(1.3, 2.7)
dno_nw = dno & BB(-190, 0, 475, 720, -80, 5)
dno_ne = dno & BB(0, 190, 475, 720, -80, 5)
dno_sw = dno & BB(-190, 0, 720, 965, -80, 5)
dno_se = dno & BB(0, 190, 720, 965, -80, 5)

def drill(part, pts, r, z0, z1):
    for x, y in pts:
        part -= Pos(x, y, (z0 + z1) / 2) * Cylinder(r, z1 - z0)
    return part

def plank(x0, x1, y0, y1, z0, holes):
    pl = BB(x0, x1, y0, y1, z0, z0 + 1.5)
    for hx, hy in holes:
        pl -= Pos(hx, hy, z0 + 0.75) * Cylinder(1.6, 1.7)
    return pl

pl_dy_w = plank(-105, -40, 700, 740, Z_BOT1, [q for q in JD_Y if q[0] < 0])
pl_dy_e = plank(40, 105, 700, 740, Z_BOT1, [q for q in JD_Y if q[0] > 0])
pl_dx = plank(-20, 20, 772, 935, Z_BOT1, JD_X)

# ================== КРЫШКА ==================
top_p = slab_t = Pos(0, 0, Z_TOP0) * extrude(F1, Z_TOP1 - Z_TOP0)
top_p -= Pos(0, ROZ_Y, Z_TOP0 + 1.5) * Cylinder(ROZ_R, 3.2)        # розетка
ring = Pos(0, ROZ_Y, Z_TOP0 - 3) * (Cylinder(ROZ_R + 5.5, 6) -
                                    Cylinder(ROZ_R + 2.5, 6.2))    # кольцо-ребро
top_p += (ring - BB(-27.2, 27.2, 478, 801, Z_TOP0 - 10, Z_TOP0)    # мимо хребта
          - BB(38, 82, 478, 960, Z_TOP0 - 10, Z_TOP0))             # проём планки
top_p -= BB(-26.6, 26.6, 479.9, 500, 25, 26.1)     # ниша планки грифа
bort_t = Pos(0, 0, Z_TOP0 - 10) * extrude(F1 - F11, 10)            # бортик вниз
bort_t -= BB(-28, 28, 470, 500, Z_TOP0 - 10.1, Z_TOP0 + 0.1)       # проём грифа
top_p += bort_t
for y in (680, 800, 880):                                          # рёбра снизу
    top_p += ((BB(-160, 160, y - 1.25, y + 1.25, Z_TOP0 - 6, Z_TOP0)
               & Pos(0, 0, Z_TOP0 - 3) * extrude(F11, 8, both=True))
              - BB(-27.2, 27.2, 478, 801, Z_TOP0 - 10, Z_TOP0)     # мимо хребта
              - BB(38, 82, 478, 960, Z_TOP0 - 10, Z_TOP0))         # проём планки
top_p = drill(top_p, TOP_SCREWS, 1.6, Z_TOP0 - 0.1, Z_TOP1 + 0.1)  # к хребту
top_p = radial_holes(top_p, HOLES_S, Z_TOP0 - 5)                   # винты ленты

JT_Y = [(sx * x, y) for sx in (-1, 1) for x in (50, 78, 100) for y in (710, 730)]
JT_XN = [(x, y) for x in (50, 70) for y in (510, 565, 625, 685)]
JT_XS = [(x, y) for x in (50, 70) for y in (755, 810, 865, 915)]
for x, y in JT_Y + JT_XN + JT_XS:                      # каналы снизу, не насквозь
    top_p -= Pos(x, y, 24.2) * Cylinder(1.3, 2.6)
top_wn = top_p & BB(-190, 60, 475, 720, 0, 30)
top_ws = top_p & BB(-190, 60, 720, 965, 0, 30)
top_en = top_p & BB(60, 190, 475, 720, 0, 30)
top_es = top_p & BB(60, 190, 720, 965, 0, 30)

pl_ty_w = plank(-105, -40, 700, 740, Z_TOP0 - 1.5, [q for q in JT_Y if q[0] < 0])
pl_ty_e = plank(40, 105, 700, 740, Z_TOP0 - 1.5, [q for q in JT_Y if q[0] > 0])
pl_tx_n = plank(40, 80, 500, 695, Z_TOP0 - 1.5, JT_XN)
pl_tx_n -= Pos(0, ROZ_Y, Z_TOP0 - 0.75) * Cylinder(ROZ_R + 2, 1.7)  # дуга розетки
pl_tx_s = plank(40, 80, 745, 940, Z_TOP0 - 1.5, JT_XS)

# планка ГРИФ-КРЫШКА (усиление верхнего пояса стыка, идея юзера): лежит в нише
# крышки (дно 25) и на фретборде сек-3 (верх 25); винты: 2 сквозь штатные
# дырки фретборда в стенки секции + 2 сквозь крышку в стенки хребта (486)
def _frets650(y0, y1):
    out, n = [], 1
    while True:
        Ln = 650.0 * (1 - 2 ** (-n / 12))
        if Ln > y1:
            return out
        if Ln >= y0:
            out.append(Ln)
        n += 1
_fs = [320.0] + _frets650(320.5, 480.0) + [480.0]
_mids = [(a + b) / 2 for a, b in zip(_fs, _fs[1:]) if b - a > 7]
Y3S = min(_mids, key=lambda m: abs(m - 468))           # южные винты фретборда
pl_neck = BB(-26, 26, 456, 500, 25, 26.5)
for f in _frets650(325, 475):                           # канавки под лады сек-3
    if f > 455:
        pl_neck -= Pos(0, f, 25) * Rot(0, 90, 0) * Cylinder(1.7, 54)
for hx, hy in ((2.5, Y3S), (17.7, Y3S), (-24, 486), (24, 486)):
    pl_neck -= Pos(hx, hy, 25.75) * Cylinder(1.6, 1.7)

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
for zz in (Z_BOT1 + 5, Z_TOP0 - 5):                    # дырки как у пластин
    bent = radial_holes(bent, HOLES_S, zz)
for b in bnds:                                         # щели-границы сегментов
    pb, nb = at_s(b)
    ang = np.degrees(np.arctan2(nb[1], nb[0]))
    bent -= (Pos(pb[0], pb[1], (Z_BOT0 + Z_TOP1) / 2) * Rot(0, 0, ang) *
             Box(30, 0.5, H_BAND + 2))

# ================== ЭКСПОРТ ==================
parts = [("gk_dno_ne", dno_ne), ("gk_dno_nw", dno_nw),
         ("gk_dno_se", dno_se), ("gk_dno_sw", dno_sw),
         ("gk_top_wn", top_wn), ("gk_top_ws", top_ws),
         ("gk_top_en", top_en), ("gk_top_es", top_es),
         ("gk_pl_dy_w", pl_dy_w), ("gk_pl_dy_e", pl_dy_e), ("gk_pl_dx", pl_dx),
         ("gk_pl_ty_w", pl_ty_w), ("gk_pl_ty_e", pl_ty_e),
         ("gk_pl_tx_n", pl_tx_n), ("gk_pl_tx_s", pl_tx_s),
         ("gk_pl_neck", pl_neck),
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
for nm in ("pl_dy_w", "pl_dy_e", "pl_dx", "pl_ty_w", "pl_ty_e",
           "pl_tx_n", "pl_tx_s"):
    asm.add(nm, rf"{OUT}\gk_{nm}.stl")
touch += [("pl_dy_w", "dno_nw"), ("pl_dy_e", "dno_se"), ("pl_dx", "dno_sw"),
          ("pl_ty_w", "top_wn"), ("pl_ty_e", "top_es"),
          ("pl_tx_n", "top_en"), ("pl_tx_s", "top_ws")]
clear += [("pl_ty_w", "dk1", 0.0), ("pl_ty_e", "dk2", 0.0)]
asm.add("pl_neck", rf"{OUT}\gk_pl_neck.stl")
asm.add("fret3", rf"{OUT}\gs3_fret.stl", loc=(0, 320, 23))
touch += [("pl_neck", "top_wn"), ("pl_neck", "fret3")]
asm.check(clearances=clear, touching=touch, verbose=False)
asm.check_holes("pl_dy_w", [(x, y, Z_BOT1 + 0.7, 1.6)
                            for x, y in JD_Y if x < 0], verbose=False)
asm.check_holes("pl_tx_n", [(x, y, Z_TOP0 - 0.7, 1.6) for x, y in JT_XN],
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
