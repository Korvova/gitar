# -*- coding: utf-8 -*-
r"""ВАРИАНТ 2 (18.11.2026, владелец): телескоп v6 с 49E снизу, но тележка СПЕРЕДИ над плавающими шестернями —
палец у переднего края модуля, без длинной накладки. Основа — концепт Б (koncepty_ABVG/koncept_B.py), доведён до печати:
  * у тележки рейка зубьями ВНУТРЬ (к шестерням), её спинка — задняя сторона ласточкина хвоста, передняя губа тележки
    со скосом обнимает направляющую на передней стенке основания (вверху шире на 0.5);
  * неподвижная рейка — отдельная деталь ЗА шестернями, зубьями к ним, концами лежит на стойках бруска;
  * моста, ножек, подушек, крышек и накладок нет: тележка ездит по передней направляющей. Клик и вибро — потом;
  * 49E в основании, колпак ротора с магнитами, шестерня мотора, ползун, брусок — как в 19.57.
Запуск из этой папки: ..\..\2-0\.venv-b123d\Scripts\python variant2.py
"""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from build123d import *
import teleskop_v6 as T
os.chdir(HERE)
for d in ("stl", "asm"):
    os.makedirs(d, exist_ok=True)
BB, CZ, PX = T.BB, T.CZ, T.prof_x
L2, RF, M, HALF, CW = T.L2, T.RF, T.M, T.HALF, T.CW
DT = 1.0                                                                          # хвост вверху шире на 1.0: при подъёме на 0.6 губа уже упирается
DED = 1.2 * M

# ---------------- основание: старая передняя рейка снята, на передней стенке — направляющая-хвост ----------------
RY0, RY1 = -8.4, -6.2                                                            # направляющая внизу (вверху шире вперёд на DT)
base2 = T.base - BB(-HALF - 1, HALF + 1, T.Y0 - 1, -3.9, L2[0] - 0.2, 40)
base2 += PX([(RY0, L2[0] - 0.21), (RY1, L2[0] - 0.21), (RY1, L2[1]), (RY0 - DT, L2[1])], -HALF, HALF)

# ---------------- неподвижная рейка за шестернями, зубья к шестерням (−Y), концы на стойках бруска ----------------
fix2 = T.rack(-HALF, HALF, RF, -1, L2[0], L2[1], 1.6)
YB_R = RF + DED + 1.6                                                             # спинка неподвижной рейки
fix2 += PX([(YB_R - 0.01, L2[0]), (YB_R, L2[0]), (YB_R + DT, L2[1]), (YB_R - 0.01, L2[1])], -HALF, HALF)   # спинка — второй ласточкин хвост (владелец 18.11)
for sx in (-1, 1):
    fix2 += BB(*sorted((sx * 23.7, sx * HALF)), RF + DED - 0.01, RF + DED + 1.6, T.Z_BM1, L2[0] + 0.01)

# ---------------- тележка: рейка зубьями внутрь (+Y) = задняя сторона хвоста, губа спереди под скос, площадка под палец ----------------
Z_P0, Z_P1 = L2[1] + 0.2, L2[1] + 2.2
cart2 = T.rack(-CW, CW, -RF - 0.05, 1, L2[0], L2[1] + 0.16, 0.3)                        # 0.05 — зазор в зацеплении
cart2 += BB(-CW, CW, -RF - DED - 0.35, -RF - DED - 0.05, L2[1] - 0.01, Z_P0 + 0.01)   # перемычка над спинкой рейки
cart2 += BB(-CW, CW, -RF - DED - 0.06, -3.9, L2[1] + 0.15, Z_P0 + 0.01)             # над шестернями зазор 0.15
cart2 += BB(-CW, CW, RY0 - DT - 1.4, -3.9, Z_P0, Z_P1)
cart2 += PX([(RY0 - DT - 0.2, L2[1] + 0.01), (RY0 - 0.2, L2[0]), (RY0 - 1.4, L2[0]), (RY0 - DT - 1.4, L2[1] + 0.01), (RY0 - DT - 1.4, Z_P0 + 0.01), (RY0 - DT - 0.2, Z_P0 + 0.01)][::-1], -CW, CW)
cart2 += BB(-CW, CW, -3.95, YB_R + DT + 1.4, L2[1] + 0.15, Z_P1)                  # тележка тянется назад над шестернями до спинки неподвижной рейки
cart2 += PX([(YB_R + 0.2, L2[0]), (YB_R + 1.4, L2[0]), (YB_R + DT + 1.4, L2[1] + 0.16), (YB_R + DT + 1.4, Z_P0 + 0.01), (YB_R + DT + 0.2, Z_P0 + 0.01), (YB_R + DT + 0.2, L2[1] + 0.16)], -CW, CW)   # задняя губа за спинкой рейки
cart2 += BB(-CW, CW, RY0 - DT - 1.4, YB_R + DT + 1.4, Z_P1 - 0.01, Z_P1 + 1.6)   # площадка под палец: от передней губы до задней — половина модуля, без выступа


def pose2(s):
    p = T.pose(s)
    for k in ("тележка", "накладка"):
        p.pop(k, None)
    rf = math.degrees(s / RF)                                                    # рейка теперь за шестернями — крутятся в другую сторону
    p["плав1"] = Pos(s - T.A, 0, 0) * Rot(0, 0, rf) * T.flo0
    p["плав2"] = Pos(s + T.A, 0, 0) * Rot(0, 0, rf) * T.flo0
    p["тележка"] = Pos(2 * s, 0, 0) * cart2
    return p


PRINT = [("01_osnovanie", base2, 0, 1), ("02_rejka_nepodvizhnaja", fix2, 180, 1), ("03a_kolpak_rotora_s_magnitami", T.jacket, 180, 1),
         ("03b_shest_motora", T.gear_m, 180, 1), ("05_polzun", T.sl, 0, 1), ("06_shest_plav_x2", T.flo0, 0, 2),
         ("08_telezhka", cart2, 180, 1), ("10_brusok", T.beam, 0, 1)]

if __name__ == "__main__":
    import trimesh

    def iv(a, b):
        try:
            r = a & b
            return 0.0 if r is None else r.volume
        except Exception:
            return 0.0
    stat = {"основание": base2, "рейка": fix2, "брусок": T.beam, "мотор": T.motor, "49E": T.hall}
    bad = 0
    for s in (-T.S, -8.25, -5.5, -2.75, 0, 2.75, 5.5, 8.25, T.S):
        al = {**stat, **pose2(s)}
        ns = list(al)
        for i, a in enumerate(ns):
            for b in ns[i + 1:]:
                if (a in stat and b in stat) or {a, b} == {"мотор", "шест.мотора"}:
                    continue
                v = iv(al[a], al[b])
                if v > 0.03:
                    bad += 1
                    print("  ПЕРЕСЕЧЕНИЕ s=%+.2f %s × %s: %.2f" % (s, a, b, v))
    for a, b in (("рейка", "основание"), ("рейка", "брусок"), ("49E", "основание")):
        v = iv(stat[a], stat[b])
        if v > 0.03:
            bad += 1
            print("  СТАТИКА %s × %s %.2f" % (a, b, v))
    if iv(Pos(0, 0, 0.6) * cart2, base2) < 0.01:
        bad += 1
        print("  тележка поднимается на 0.6 — не держится")
    if iv(Pos(0, -0.6, 0) * cart2, base2) < 0.01 and iv(Pos(0, 0.6, 0) * cart2, base2) < 0.01:
        bad += 1
        print("  тележка болтается по Y")
    for g in ("плав1", "плав2"):
        p = pose2(0)
        if iv(Rot(0, 0, 0) * Pos(0, 0, 0) * (Pos(-T.A if g == "плав1" else T.A, 0, 0) * Rot(0, 0, 7.5) * T.flo0), fix2) < 0.01:
            print("  внимание: %s не в зацеплении с неподвижной рейкой" % g)
    print("вариант 2: %s" % ("ЧИСТО" if not bad else "%d проблем" % bad))
    yc = (RY0 - DT - 1.4 + YB_R + DT + 1.4) / 2
    b_ = base2.bounding_box(); print("тележка по Y %.1f…%.1f (%.1f мм), модуль %.1f…%.1f (%.1f мм)" % (RY0 - DT - 1.4, YB_R + DT + 1.4, YB_R + 2 * DT + 2.8 - RY0, b_.min.Y, b_.max.Y, b_.max.Y - b_.min.Y))
    print("центр площадки под палец y = %.1f (у варианта А ~%.1f); высота до верха площадки %.1f" % (yc, T.YC_CART, Z_P1 + 1.6))
    for n, p, flip, cnt in PRINT:
        p = Rot(flip, 0, 0) * (Part() + p)
        b = p.bounding_box()
        p = Pos(-(b.min.X + b.max.X) / 2, -(b.min.Y + b.max.Y) / 2, -b.min.Z) * p
        export_stl(p, "stl/%s.stl" % n, tolerance=0.01, angular_tolerance=0.1)
        m = trimesh.load("stl/%s.stl" % n)
        ov = float(m.area_faces[(m.face_normals[:, 2] < -0.72) & (m.triangles_center[:, 2] > 0.25)].sum())
        print("  %-30s ×%d %5.1f × %5.1f × %4.1f герм %s нависание %.1f мм²" % (n, cnt, b.size.X, b.size.Y, b.size.Z, m.is_watertight, ov))
    for n, p in (("base", base2), ("rack", fix2), ("motor", T.motor), ("beam", T.beam), ("hall", T.hall)):
        export_stl(Part() + p, "asm/%s.stl" % n, tolerance=0.02, angular_tolerance=0.2)
    export_stl(Part() + T.sl, "asm/slider.stl", tolerance=0.02, angular_tolerance=0.2)
    export_stl(Part() + T.flo0, "asm/flo.stl", tolerance=0.02, angular_tolerance=0.2)
    export_stl(Part() + cart2, "asm/cart.stl", tolerance=0.02, angular_tolerance=0.2)
    export_stl(Part() + T.pin_m0, "asm/pin_m.stl", tolerance=0.02, angular_tolerance=0.2)
    export_stl(Part() + T.jacket, "asm/jacket.stl", tolerance=0.02, angular_tolerance=0.2)
    print("asm готово")
