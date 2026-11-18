# -*- coding: utf-8 -*-
r"""ПАРА с тележками 15 мм (18.11.2026, владелец, по рисунку с розовыми подложками).
Площадки под пальцы 15 мм вдоль струн, на шаге 24; модули стоят как в para.py (колпаки юбка к юбке).
  * Тележка А: площадка спереди; спереди тележка загибается вниз по наружной стороне передней стенки основания,
    крюк внизу заходит в продольную щель стенки — тележка не поднимается. Хвост на стенке и задняя губа убраны.
  * Тележка Б: площадка 15 мм вынесена вперёд, рейка к шестерням — на «подложке» ниже площадки (розовое на рисунке);
    спереди такой же загиб с крюком под балку. Балка — на колоннах по краям, колонны сзади балки, крюку не мешают.
Запуск из этой папки: ..\..\2-0\.venv-b123d\Scripts\python para15.py
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from build123d import *
import variant2 as V
T = V.T
os.chdir(HERE)
for d in ("stl_p15", "asm_p15"):
    os.makedirs(d, exist_ok=True)
BB, CZ = T.BB, T.CZ
S, A, HALF, L2, CW, RF, DED = T.S, T.A, T.HALF, T.L2, T.CW, T.RF, V.DED
W = 15.0                                                                          # площадка вдоль струн
C = 0.2                                                                           # зазор скольжения
ZT = V.Z_P1 + 1.6                                                                 # верх площадки 29.7
ZB = L2[1] + 0.15                                                                 # низ тележки над шестернями
D = 38.36                                                                         # модуль Б за модулем А (колпаки Ø38, зазор 0.36)
SK = 1.2                                                                          # толщина загиба, крюк 0.8 × 1.0

# ---------------- основание модуля: хвост на передней стенке снят ----------------
base1 = V.base2 - BB(-HALF - 1, HALF + 1, T.Y0 - 3, -3.9, L2[0] - 0.25, 40)


def rack_part():
    r = T.rack(-CW, CW, -RF - 0.05, 1, L2[0], L2[1] + 0.16, 0.3)
    r += BB(-CW, CW, -RF - DED - 0.35, -RF - DED - 0.05, L2[1] - 0.01, ZB + 0.01)
    return r


# крюк идёт прямо от рейки (владелец 18.11): спинка рейки продолжается вниз в паз передней стенки, внизу крюк вперёд (−y) в подрез.
# Назад (+y) крюку некуда — там сразу ползун, поэтому крюк смотрит вперёд, в толщу стенки.
Y_RB = -RF - 0.05 - DED - 0.3                                                     # спинка рейки −6.11
Y_RF = -RF - 0.05 - 0.1                                                           # к зубьям −5.0 (ниже шестерён зубьев нет)
Z_LIP0, Z_LIP1 = 20.5, 21.5                                                       # крюк
LIP = 1.4


def rack_hook():
    h = BB(-CW, CW, Y_RB, Y_RF, Z_LIP0, L2[0] + 0.01)                             # стойка крюка вниз от рейки
    h += BB(-CW, CW, Y_RB - LIP, Y_RF, Z_LIP0, Z_LIP1)                            # крюк вперёд
    return h


slot = BB(-HALF - 1, HALF + 1, Y_RB - C, Y_RF + C, Z_LIP0 - C, 40)                # паз в стенке под стойку
slot += BB(-HALF - 1, HALF + 1, Y_RB - LIP - C, Y_RF + C, Z_LIP0 - C, Z_LIP1 + C)  # подрез под крюк
base1 = base1 - slot

# ---------------- тележка А: площадка от спинки рейки назад, над шестернями ----------------
YA0 = Y_RB
YA1 = YA0 + W
cartA = rack_part() + rack_hook() + BB(-CW, CW, YA0, YA1, ZB, ZT)
Y_PA = (YA0 + YA1) / 2

# ---------------- тележка Б: площадка вынесена вперёд, держится крюком рейки в своей стенке; спереди лежит на балке ----------------
Y_PB = Y_PA + 24.0 - D
YB0, YB1 = Y_PB - W / 2, Y_PB + W / 2
cartB = rack_part() + rack_hook() + BB(-CW, CW, YB0, YB1, ZB, ZT)
if YB1 < -3.9:
    cartB += BB(-CW, CW, YB1 - 0.01, -3.9, ZB, V.Z_P1)                            # подложка до рейки, ниже площадки на 1.6
Z_BM1 = ZB - C                                                                    # балка: опора площадки Б при нажатии
YM0 = YB0 + 3.0
beam = BB(-HALF, HALF, YM0, YM0 + 3.0, Z_BM1 - 1.5, Z_BM1)
for sx in (-1, 1):
    beam -= CZ(0.85, Z_BM1 - 1.6, Z_BM1 - 0.5, sx * 23.0, YM0 + 1.5)
cols = None
for sx in (-1, 1):
    c = BB(*sorted((sx * 21.0, sx * HALF)), YM0, YM0 + 3.0, T.Z_FL - 0.01, Z_BM1 - 1.52) + CZ(0.75, Z_BM1 - 1.53, Z_BM1 - 0.6, sx * 23.0, YM0 + 1.5)
    cols = c if cols is None else cols + c


def env(cart, y0):
    e = []
    j = T.jacket.bounding_box()
    e.append(CZ(j.max.X + 0.3, j.min.Z - 0.3, j.max.Z + 0.3, 0, T.YM + y0))
    g = T.gear_m.bounding_box()
    e.append(CZ(g.max.X + 0.3, g.min.Z - 0.3, g.max.Z + 0.3, 0, T.YM + y0))
    for p, dx in ((T.sl, S), (T.flo0, S + A)):
        b = p.bounding_box()
        e.append(BB(b.min.X - dx - 0.3, b.max.X + dx + 0.3, b.min.Y + y0 - 0.3, b.max.Y + y0 + 0.3, b.min.Z - 0.3, b.max.Z + 0.3))
    for s in cart.solids():                                                       # каждая часть тележки отдельно — не коробка целиком
        b = s.bounding_box()
        e.append(BB(b.min.X - 2 * S - 0.3, b.max.X + 2 * S + 0.3, b.min.Y + y0 - 0.3, b.max.Y + y0 + 0.3, b.min.Z - 0.3, b.max.Z + 0.3))
    out = e[0]
    for x in e[1:]:
        out = out + x
    return out


def pieces(cart):
    """тележка как набор коробок по её зонам (для огибающей)"""
    return cart


partsA = Part() + [rack_part(), BB(-CW, CW, Y_RB - LIP, Y_RF, Z_LIP0, L2[0] + 0.01), BB(-CW, CW, YA0, YA1, ZB, ZT)]
partsB = Part() + [rack_part(), BB(-CW, CW, Y_RB - LIP, Y_RF, Z_LIP0, L2[0] + 0.01), BB(-CW, CW, YB0, max(YB1, -3.9), ZB, ZT)]
envA, envB = env(partsA, 0.0), env(partsB, D)
baseA = base1 - envB
baseB = Pos(0, D, 0) * base1 - envA
base = baseA + baseB + (Pos(0, D, 0) * cols - envA)
beamW = Pos(0, D, 0) * beam
rackA, rackB = V.fix2, Pos(0, D, 0) * V.fix2


def poseA(s):
    p = V.pose2(s); p["тележка"] = Pos(2 * s, 0, 0) * cartA; return p


def poseB(s):
    p = V.pose2(s); p["тележка"] = Pos(2 * s, 0, 0) * cartB
    return {k: Pos(0, D, 0) * v for k, v in p.items()}


PRINT = [("01_osnovanie_para", base, 0, 1), ("02_rejka_nepodvizhnaja_x2", V.fix2, 180, 2), ("03a_kolpak_rotora_x2", T.jacket, 180, 2),
         ("03b_shest_motora_x2", T.gear_m, 180, 2), ("05_polzun_x2", T.sl, 0, 2), ("06_shest_plav_x4", T.flo0, 0, 4),
         ("08_telezhka_A_15", cartA, 180, 1), ("08_telezhka_B_15", cartB, 180, 1), ("10_brusok_x2", T.beam, 0, 2), ("12_balka_B", beam, 0, 1)]

if __name__ == "__main__":
    import trimesh

    def iv(a, b):
        try:
            r = a & b
            return 0.0 if r is None else r.volume
        except Exception:
            return 0.0
    stat = {"основание": base, "рейкаА": rackA, "рейкаБ": rackB, "брусокА": T.beam, "брусокБ": Pos(0, D, 0) * T.beam, "моторА": T.motor,
            "моторБ": Pos(0, D, 0) * T.motor, "49E_А": T.hall, "49E_Б": Pos(0, D, 0) * T.hall, "балка": beamW}
    bad = 0
    for s1 in (-S, -5.5, 0, 5.5, S):
        for s2 in (-S, 0, S):
            mv = {**{"А." + k: v for k, v in poseA(s1).items()}, **{"Б." + k: v for k, v in poseB(s2).items()}}
            al = {**stat, **mv}
            ns = list(al)
            for i, a in enumerate(ns):
                for b in ns[i + 1:]:
                    if a in stat and b in stat:
                        continue
                    if {a, b} in ({"моторА", "А.шест.мотора"}, {"моторБ", "Б.шест.мотора"}):
                        continue
                    v = iv(al[a], al[b])
                    if v > 0.05:
                        bad += 1
                        print("  s=%+.1f/%+.1f %s × %s: %.2f" % (s1, s2, a, b, v))
    for a, b in (("рейкаА", "основание"), ("рейкаБ", "основание"), ("балка", "основание"), ("брусокА", "основание"), ("брусокБ", "основание")):
        v = iv(stat[a], stat[b])
        if v > 0.05:
            bad += 1; print("  статика %s × %s %.2f" % (a, b, v))
    if iv(Pos(0, 0, -0.3) * poseB(0)["тележка"], beamW) < 0.01:
        print("  внимание: площадка Б не ложится на балку при нажатии")
    for nm, c, other in (("А", poseA(0)["тележка"], base), ("Б", poseB(0)["тележка"], base)):
        if iv(Pos(0, 0, 0.5) * c, other) < 0.01:
            bad += 1; print("  тележка %s поднимается на 0.5 — не держится" % nm)
    print("пара 15: %s; площадки 15 мм, центры y %.2f и %.2f (шаг %.2f); зазор колпаков %.2f" % (
        "ЧИСТО" if not bad else "%d проблем" % bad, Y_PA, Y_PB + D, Y_PB + D - Y_PA, D - 38.0))
    for n, p, flip, cnt in PRINT:
        p = Rot(flip, 0, 0) * (Part() + p)
        b = p.bounding_box()
        p = Pos(-(b.min.X + b.max.X) / 2, -(b.min.Y + b.max.Y) / 2, -b.min.Z) * p
        export_stl(p, "stl_p15/%s.stl" % n, tolerance=0.01, angular_tolerance=0.1)
        m = trimesh.load("stl_p15/%s.stl" % n)
        ov = float(m.area_faces[(m.face_normals[:, 2] < -0.72) & (m.triangles_center[:, 2] > 0.25)].sum())
        print("  %-28s ×%d %5.1f × %5.1f × %4.1f герм %s нависание %.1f мм²" % (n, cnt, b.size.X, b.size.Y, b.size.Z, m.is_watertight, ov))
    for n, p in (("base", base), ("rackA", rackA), ("rackB", rackB), ("beamA", T.beam), ("beamB", Pos(0, D, 0) * T.beam), ("motorA", T.motor),
                 ("motorB", Pos(0, D, 0) * T.motor), ("hallA", T.hall), ("hallB", Pos(0, D, 0) * T.hall), ("per", beamW), ("slider", T.sl),
                 ("flo", T.flo0), ("cartA", cartA), ("cartB", cartB), ("pin_m", T.pin_m0), ("jacket", T.jacket)):
        export_stl(Part() + p, "asm_p15/%s.stl" % n, tolerance=0.02, angular_tolerance=0.2)
    open("asm_p15/D.txt", "w").write(str(D))
    print("asm_p15 готово")
