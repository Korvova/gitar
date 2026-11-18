# -*- coding: utf-8 -*-
r"""ВАРИАНТ 2Б (18.11.2026, владелец): как вариант 2, но тележка вынесена ВПЕРЁД на отдельную стойку.
Сзади тележка, как раньше, держится за направляющую на передней стенке основания (губа спереди, спинка рейки сзади),
а её передняя часть лежит на перекладине стойки. Стойка — пол и две колонны по краям (x ±21…25) с перекладиной сверху;
между колоннами под тележкой пусто — туда может встать мотор соседнего модуля. Неподвижная рейка — как в варианте 2.
Запуск из этой папки: ..\..\2-0\.venv-b123d\Scripts\python variant2b.py
"""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from build123d import *
import variant2 as V
T = V.T
os.chdir(HERE)
for d in ("stl_b", "asm_b"):
    os.makedirs(d, exist_ok=True)
BB, CZ, PX = T.BB, T.CZ, T.prof_x
L2, RF, M, HALF, CW, DT, DED = T.L2, T.RF, T.M, T.HALF, T.CW, V.DT, V.DED
RY0, RY1, Z_P0, Z_P1 = V.RY0, V.RY1, V.Z_P0, V.Z_P1
W_C = 20.56                                                                       # тележка вдоль струн
Y_CB = -4.6                                                                      # задний край тележки: так тележки на шаге 24, а колпаки Ø38 не сталкиваются (пара)
Y_CF = Y_CB - W_C                                                                # передний край

# ---------------- тележка: задняя часть как в варианте 2 (рейка внутрь + губа на направляющей), спереди — плита над стойкой ----------------
cart = T.rack(-CW, CW, -RF - 0.05, 1, L2[0], L2[1] + 0.16, 0.3)
cart += BB(-CW, CW, -RF - DED - 0.35, -RF - DED - 0.05, L2[1] - 0.01, Z_P0 + 0.01)
cart += BB(-CW, CW, -RF - DED - 0.06, Y_CB, L2[1] + 0.15, Z_P0 + 0.01)
cart += PX([(RY0 - DT - 0.2, L2[1] + 0.01), (RY0 - 0.2, L2[0]), (RY0 - 1.4, L2[0]), (RY0 - DT - 1.4, L2[1] + 0.01), (RY0 - DT - 1.4, Z_P0 + 0.01), (RY0 - DT - 0.2, Z_P0 + 0.01)][::-1], -CW, CW)
cart += BB(-CW, CW, Y_CF, Y_CB, Z_P0, Z_P1)                                       # плита: от стойки до шестерён
cart += BB(-CW, CW, Y_CF, Y_CB, Z_P1 - 0.01, Z_P1 + 1.6)                          # площадка под палец
# балка по центру тележки (владелец 18.11) — ласточкин хвост; снизу тележки два крючка буквой «Г» обнимают её с боков
Y_RC = (Y_CF + Y_CB) / 2
for sg in (1, -1):
    pts = [(Y_RC + sg * 1.7, L2[0]), (Y_RC + sg * 2.9, L2[0]), (Y_RC + sg * 3.4, L2[1]), (Y_RC + sg * 3.4, Z_P0 + 0.01), (Y_RC + sg * 2.2, Z_P0 + 0.01), (Y_RC + sg * 2.2, L2[1])]
    cart += PX(pts if sg < 0 else pts[::-1], -CW, CW)

# ---------------- стойка: пол, две колонны по краям, перекладина под передней частью тележки ----------------
YR0, YR1 = Y_RC - 1.5, Y_RC + 1.5                                                # балка внизу (вверху шире на 0.5 с каждой стороны)
st = BB(-HALF, HALF, Y_CF - 0.5, T.Y0 - 0.05, 0, T.Z_FL)                          # пол, приклеить к передней стенке основания
for sx in (-1, 1):
    st += BB(*sorted((sx * 21.0, sx * HALF)), YR0, YR1, T.Z_FL - 0.01, L2[0] + 0.01)   # колонна
# перекладина — отдельная деталь (иначе мост 42 мм при печати), садится на штырьки колонн, на клей
per = PX([(YR0, L2[0]), (YR1, L2[0]), (YR1 + 0.5, L2[1]), (YR0 - 0.5, L2[1])], -HALF, HALF)   # верх на 0.2 ниже тележки
for sx in (-1, 1):
    st += CZ(0.75, L2[0] - 0.01, L2[0] + 1.2, sx * 23.0, (YR0 + YR1) / 2)        # штырёк
    per -= CZ(0.85, L2[0] - 0.1, L2[0] + 1.3, sx * 23.0, (YR0 + YR1) / 2)        # гнездо


def pose_b(s):
    p = V.pose2(s)
    p["тележка"] = Pos(2 * s, 0, 0) * cart
    return p


PRINT = [("01_osnovanie", V.base2, 0, 1), ("02_rejka_nepodvizhnaja", V.fix2, 180, 1), ("03a_kolpak_rotora_s_magnitami", T.jacket, 180, 1),
         ("03b_shest_motora", T.gear_m, 180, 1), ("05_polzun", T.sl, 0, 1), ("06_shest_plav_x2", T.flo0, 0, 2),
         ("08_telezhka_dlinnaja", cart, 180, 1), ("10_brusok", T.beam, 0, 1), ("11_stojka", st, 0, 1), ("12_perekladina", per, 180, 1)]

if __name__ == "__main__":
    import trimesh

    def iv(a, b):
        try:
            r = a & b
            return 0.0 if r is None else r.volume
        except Exception:
            return 0.0
    stat = {"основание": V.base2, "рейка": V.fix2, "брусок": T.beam, "мотор": T.motor, "49E": T.hall, "стойка": st, "перекладина": per}
    bad = 0
    for s in (-T.S, -8.25, -5.5, -2.75, 0, 2.75, 5.5, 8.25, T.S):
        al = {**stat, **pose_b(s)}
        ns = list(al)
        for i, a in enumerate(ns):
            for b in ns[i + 1:]:
                if (a in stat and b in stat) or {a, b} == {"мотор", "шест.мотора"}:
                    continue
                v = iv(al[a], al[b])
                if v > 0.03:
                    bad += 1
                    print("  ПЕРЕСЕЧЕНИЕ s=%+.2f %s × %s: %.2f" % (s, a, b, v))
    v = iv(st, V.base2)
    if v > 0.03:
        bad += 1; print("  стойка × основание %.2f" % v)
    if iv(Pos(0, 0, 0.6) * cart, V.base2) < 0.01:
        bad += 1; print("  тележка поднимается на 0.6 — не держится")
    if iv(Pos(0, 0, -0.3) * cart, per) < 0.01:
        print("  внимание: тележка не опирается на перекладину при нажатии 0.3")
    # место под мотор соседа: цилиндр Ø28 × 20.4 между колоннами
    nb = CZ(14.0, T.Z_FL, T.Z_FL + T.MOT_H + 8.0, 0, (Y_CF + T.Y0) / 2)
    print("место под мотор соседа (Ø28, высота %.1f): стойка %.2f, перекладина %.2f, тележка %.2f" % (T.MOT_H + 8.0, iv(nb, st), iv(nb, per), iv(nb, cart)))
    print("вариант 2Б: %s; тележка по Y %.1f…%.1f (%.0f мм), стойка до y %.1f" % ("ЧИСТО" if not bad else "%d проблем" % bad, Y_CF, Y_CB, W_C, Y_CF - 0.5))
    for n, p, flip, cnt in PRINT:
        p = Rot(flip, 0, 0) * (Part() + p)
        b = p.bounding_box()
        p = Pos(-(b.min.X + b.max.X) / 2, -(b.min.Y + b.max.Y) / 2, -b.min.Z) * p
        export_stl(p, "stl_b/%s.stl" % n, tolerance=0.01, angular_tolerance=0.1)
        m = trimesh.load("stl_b/%s.stl" % n)
        ov = float(m.area_faces[(m.face_normals[:, 2] < -0.72) & (m.triangles_center[:, 2] > 0.25)].sum())
        print("  %-30s ×%d %5.1f × %5.1f × %4.1f герм %s нависание %.1f мм²" % (n, cnt, b.size.X, b.size.Y, b.size.Z, m.is_watertight, ov))
    for n, p in (("base", V.base2), ("rack", V.fix2), ("motor", T.motor), ("beam", T.beam), ("hall", T.hall), ("slider", T.sl), ("flo", T.flo0),
                 ("cart", cart), ("pin_m", T.pin_m0), ("jacket", T.jacket), ("stojka", st), ("perekladina", per)):
        export_stl(Part() + p, "asm_b/%s.stl" % n, tolerance=0.02, angular_tolerance=0.2)
    print("asm_b готово")
