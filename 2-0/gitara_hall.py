# -*- coding: utf-8 -*-
"""ГИТАРА: ДАТЧИКИ ПОЛОЖЕНИЯ ТЕЛЕЖЕК — четыре стойки с 49E в деке v3 (черновик 14.09.2026).

Идея (владелец): положение тележки читать по ленте, а не по тележке: лента ходит
всего ±R_CR (±4.8 мм), это зона, где датчик Холла видит магнит уверенно. В деке
место есть и электроника рядом.

Как устроено: на ленте k сверху приклеен магнит Ø4×1.5 (у восточного края ленты,
X = 12, Y = MAG_Y[k]); рядом с лентой, восточнее жёлоба (X 14.8..19), на дне хребта
стоит стойка со своим 49E, лежащим плашмя в кармане на высоте магнита. Магнит
проезжает мимо датчика вдоль Y; датчик стоит со сдвигом +R_CR+0.5 от среднего
положения магнита, поэтому за весь ход поле меняется монотонно.

Стойки — отдельные детали (клей или капля суперклея на дно), хребет v3 и ленты не
меняются: магнит клеится сверху ленты. Провода датчика уходят по канавке на восточной
грани стойки вниз и по дну к восточной стенке.

Запуск: .venv-b123d\\Scripts\\python gitara_hall.py
  -> Print/Print/gdk_hall_post{k}_v1.stl + проверка зазоров с декой v3 при ходе ленты
"""
import math
import os
import sys
from build123d import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "Print", "Print")
sys.path.insert(0, HERE)

# ---- из gitara_deka.py v3 (не импортируем: тот скрипт при импорте всё пересчитывает) ----
Z_FLOOR = [3, 8.4, 13.8, 19.2]
LANE = 10
MY = [515, 565, 615, 678]
COMB_Y = (540, 590, 634)
R_CR = 4.8
PIN_R = 2.5
DISK_R = R_CR + PIN_R + 1.0
YOKE_HALF_Y = PIN_R + 0.15 + 1.5
EAR_R, EAR_ANG = 43.85 / 2, 56.0
MOT_X = 0.0
DK1_Y0, DK2_Y0 = 480, 640
TUMBA1 = [(-18, 60), (-18, 110)]
TUMBA2 = [(-18, 65), (18, 65), (-18, 135), (18, 135)]

# ---- датчик и магнит ----
SENS_W, SENS_L, SENS_T = 3.0, 4.0, 1.5      # 49E плашмя: ширина (X), длина (Y), толщина
MAG_D, MAG_H = 4.0, 1.5
# сторона стойки: восток (X 14.8..19, магнит на X=12) или запад (X 1.4..5.2, магнит на X=8);
# лента X 6..14, зазор до стойки 0.8. Запад нужен этажу 0: его хвост короткий, а у уха мотора 0 на востоке тесно
SIDE_POST = {+1: (14.8, 19.0), -1: (1.4, 5.2)}
SIDE_MAGX = {+1: 12.0, -1: 8.0}
POST_HY = 4.0                               # полудлина стойки по Y
BAND_T = 1.6


def BB(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(
        abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))


def ear_holes(my, sign):
    a = math.radians(EAR_ANG)
    dx, dy = EAR_R * math.sin(a), EAR_R * math.cos(a)
    return [(MOT_X + sign * dx, my + dy), (MOT_X - sign * dx, my - dy)]


# ---- где ставить: Y магнита на ленте k (в среднем положении) ----
def pick_mag_y(k):
    """Магнит на ленте k между 500 (после защёлки 480..498) и мотором k, подальше от
    ушей всех моторов (обе стороны), гребёнок, тумб и дисков нижних кривошипов."""
    obstacles = []
    for my in MY:
        for s in (1, -1):
            obstacles += ear_holes(my, s)
    obstacles += [(tx, DK1_Y0 + ty) for tx, ty in TUMBA1] + [(tx, DK2_Y0 + ty) for tx, ty in TUMBA2]
    comb_pts = [(x, yg) for yg in COMB_Y for x in (-6, 0, 5.4, 10.2)]   # спинка и зубья гребёнки
    y_max = MY[k] - YOKE_HALF_Y - DISK_R - 6
    y_min = 492 if k == 0 else 502            # этаж 0: магнит на языке защёлки, после штырька (486.5)
    best = None
    for side in (+1, -1):
        px0, px1 = SIDE_POST[side]
        xc = (px0 + px1) / 2
        for y in range(y_min, int(y_max)):
            ys = y + R_CR + 0.5               # датчик сдвинут на +R_CR+0.5 от магнита
            d = min(math.hypot(xc - ox, ys - oy) for ox, oy in obstacles) - 3.5
            dcomb = min(math.hypot(xc - ox, ys - oy) for ox, oy in comb_pts) - POST_HY
            ddisk = min(math.hypot(xc - MOT_X, ys - my) for my in MY) - DISK_R - POST_HY
            score = min(d, dcomb, ddisk)
            if best is None or score > best[0]:
                best = (score, y, side)
    return best[1], best[0], best[2]


MAG_Y, SENS_Y, SIDE = [], [], []
for k in range(4):
    y, score, side = pick_mag_y(k)
    MAG_Y.append(y); SENS_Y.append(y + R_CR + 0.5); SIDE.append(side)
    print(f"этаж {k}: магнит Y={y} (от начала хвоста {y - 480} мм, X={SIDE_MAGX[side]}), датчик Y={SENS_Y[k]:.1f}, "
          f"сторона {'восток' if side > 0 else 'запад'}, запас {score:.1f} мм")
import json as _json
_json.dump({"MAG_Y": MAG_Y, "SENS_Y": SENS_Y, "SIDE": SIDE, "SIDE_POST": {str(k): v for k, v in SIDE_POST.items()},
            "SIDE_MAGX": {str(k): v for k, v in SIDE_MAGX.items()}}, open(os.path.join(HERE, "_hall_pos.json"), "w"))


# ---- стойка ----
def post_part(k):
    zf = Z_FLOOR[k]
    mag_zc = zf + 0.05 + BAND_T + MAG_H / 2          # центр магнита (лента лежит на Z_FLOOR+0.05)
    top = mag_zc + SENS_T / 2                        # датчик плашмя: центр на высоте магнита
    ys = SENS_Y[k]
    px0, px1 = SIDE_POST[SIDE[k]]
    far = px1 if SIDE[k] > 0 else px0          # грань, обращённая от ленты: туда уходят ножки
    p = BB(px0, px1, ys - POST_HY, ys + POST_HY, 3, top)
    fx0, fx1 = (px0, px1 + 1.5) if SIDE[k] > 0 else (px0 - 1.5, px1)   # пятка под клей только от ленты и вдоль Y (лента 0 идёт по полу рядом)
    p += BB(fx0, fx1, ys - POST_HY - 1.5, ys + POST_HY + 1.5, 3, 4.0)
    # карман под 49E: датчик лежит длиной вдоль Y
    xc = (px0 + px1) / 2
    p -= BB(xc - SENS_W / 2 - 0.1, xc + SENS_W / 2 + 0.1, ys - SENS_L / 2 - 0.1, ys + SENS_L / 2 + 0.1,
            top - SENS_T - 0.1, top + 0.1)
    # ножки: щель от кармана до дальней грани, затем канавка вниз по этой грани
    if SIDE[k] > 0:
        p -= BB(xc, far + 0.1, ys - 2.0, ys + 2.0, top - SENS_T - 0.1, top + 0.1)
        p -= BB(far - 1.2, far + 0.1, ys - 1.2, ys + 1.2, 3.5, top + 0.1)
    else:
        p -= BB(far - 0.1, xc, ys - 2.0, ys + 2.0, top - SENS_T - 0.1, top + 0.1)
        p -= BB(far - 0.1, far + 1.2, ys - 1.2, ys + 1.2, 3.5, top + 0.1)
    return p


posts = [post_part(k) for k in range(4)]
for k, p in enumerate(posts):
    pp = Part() + p
    export_stl(pp, os.path.join(OUT, f"gdk_hall_post{k}_v1.stl"))
    print(f"gdk_hall_post{k}_v1: volume={pp.volume:.0f} mm3, solids={len(pp.solids())}, верх Z={pp.bounding_box().max.Z:.2f}")

# магнит как деталь для проверки/картинок (сам магнит покупной)
for k in range(4):
    m = Pos(SIDE_MAGX[SIDE[k]], MAG_Y[k], Z_FLOOR[k] + 0.05 + BAND_T + MAG_H / 2) * Cylinder(MAG_D / 2, MAG_H)
    export_stl(Part() + m, os.path.join(OUT, f"_hall_magnet{k}_model.stl"))
print("export done")

# ================= ПРОВЕРКА: стойки против деки v3 при ходе ленты =================
import trimesh
from clearance import Assembly


def stl(name):
    return os.path.join(OUT, name + ".stl")


asm = Assembly()
asm.add("dk1", stl("gdk1_base_v3"), loc=(0, DK1_Y0, 0))
asm.add("dk2", stl("gdk2_base_v3"), loc=(0, DK2_Y0, 0))
asm.add("sp0", stl("gdk_spacer0_v3"), loc=(MOT_X, MY[0], 0))
for k in range(4):
    asm.add(f"mot{k}", stl(f"gdk_motor{k}_model"), loc=(MOT_X, MY[k], [-4.0, 0, 0, 0][k]))
for i, yg in enumerate(COMB_Y):
    asm.add(f"comb{i}", stl("gdk_comb_v3"), loc=(0, yg, 0))
for k in range(4):
    asm.add(f"post{k}", stl(f"gdk_hall_post{k}_v1"), loc=(0, 0, 0))
RAW_TL = [trimesh.load(stl(f"gdk_tail{k}_v3"), force="mesh") for k in range(4)]
RAW_CR = [trimesh.load(stl(f"gdk_crank{k}_v3"), force="mesh") for k in range(4)]
RAW_MG = [trimesh.load(stl(f"_hall_magnet{k}_model"), force="mesh") for k in range(4)]

bad = []
worst = {}


def need(a, b, gap, where):
    d, depth = asm._dist(a, b)
    key = f"{a}/{b}"
    worst[key] = min(worst.get(key, 99), d if depth <= 0.05 else -depth)
    if depth > 0.05 or d < gap:
        bad.append(f"{where}: {a} <-> {b} зазор {d:.2f} (нужно {gap}), вход {depth:.2f}")


def place(k, angle):
    dy = R_CR * math.sin(math.radians(angle))
    T = trimesh.transformations.rotation_matrix(math.radians(angle), [0, 0, 1])
    T[:3, 3] = (MOT_X, MY[k], 0)
    c = RAW_CR[k].copy(); c.apply_transform(T); asm.meshes[f"cr{k}"] = c
    t = RAW_TL[k].copy(); t.apply_translation((LANE, 480 + dy, Z_FLOOR[k] + 0.05)); asm.meshes[f"tl{k}"] = t
    m = RAW_MG[k].copy(); m.apply_translation((0, dy, 0)); asm.meshes[f"mg{k}"] = m


for th in range(0, 360, 30):
    for k in range(4):
        place(k, th)
    where = f"{th}°"
    for k in range(4):
        need(f"post{k}", "dk1" if SENS_Y[k] < DK2_Y0 else "dk2", 0.0, where)   # стоит на дне (касание)
        for j in range(4):
            need(f"post{k}", f"tl{j}", 0.5, where)          # ленты всех этажей мимо стойки
            need(f"post{k}", f"mg{j}", 0.3 if j == k else 1.0, where)
            need(f"post{k}", f"cr{j}", 0.5, where)
            need(f"post{k}", f"mot{j}", 0.5, where)
            need(f"mg{k}", f"tl{j}", 0.3, where) if j != k else None
            need(f"mg{k}", f"cr{j}", 0.3, where)
        for i in range(len(COMB_Y)):
            need(f"post{k}", f"comb{i}", 1.0, where)
            need(f"mg{k}", f"comb{i}", 0.3, where)
print("минимальные зазоры (мм):")
for key in sorted(worst):
    print(f"  {key:16s} {worst[key]:6.2f}")
real = [b for b in bad if "вход 999" not in b]
print("НАРУШЕНИЯ:" if real else "стойки: чисто", len(real))
for b in real[:20]:
    print("  " + b)
