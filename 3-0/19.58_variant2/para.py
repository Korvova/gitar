# -*- coding: utf-8 -*-
r"""ПАРА (18.11.2026, владелец): модуль на 2 пальца из варианта 2 (А, y = 0) и варианта 2Б (Б, сзади на D), тележки на шаге 24,
колпаки моторов юбка к юбке. Основание общее: оба основания сложены, а всё, что мешает подвижным частям соседа, вырезано.
Стойки Б нет: передняя часть тележки Б лежит на перекладине над мотором А, перекладина — на колоннах по краям основания.
Запуск из этой папки: ..\..\2-0\.venv-b123d\Scripts\python para.py
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from build123d import *
import variant2b as B
V, T = B.V, B.T
os.chdir(HERE)
for d in ("stl_para", "asm_para"):
    os.makedirs(d, exist_ok=True)
BB, CZ = T.BB, T.CZ
S, A, HALF, L2 = T.S, T.A, T.HALF, T.L2
c2 = V.cart2.bounding_box(); cb = B.cart.bounding_box()
Y_PA = (V.RY0 - V.DT - 1.4 + V.YB_R + V.DT + 1.4) / 2                          # центр площадки тележки А
Y_PB = (B.Y_CF + B.Y_CB) / 2                                                    # центр площадки тележки Б
D = round(24.0 + Y_PA - Y_PB, 2)                                                 # площадки под пальцы на шаге 24
CL = 0.3


def bb(p):
    return p.bounding_box()


def envelope(cart, y0):
    """всё, где бывают подвижные части модуля, сдвинутого на y0 (с зазором CL)"""
    e = []
    j = bb(T.jacket)
    e.append(CZ(max(-j.min.X, j.max.X) + CL, j.min.Z - CL, j.max.Z + CL, 0, T.YM + y0))   # колпак ротора
    g = bb(T.gear_m)
    e.append(CZ(max(-g.min.X, g.max.X) + CL, g.min.Z - CL, g.max.Z + CL, 0, T.YM + y0))  # шестерня мотора
    for p, dx in ((T.sl, S), (T.flo0, S + A)):
        b = bb(p)
        e.append(BB(b.min.X - dx - CL, b.max.X + dx + CL, b.min.Y + y0 - CL, b.max.Y + y0 + CL, b.min.Z - CL, b.max.Z + CL))
    b = bb(cart)
    e.append(BB(b.min.X - 2 * S - CL, b.max.X + 2 * S + CL, b.min.Y + y0 - CL, b.max.Y + y0 + CL, b.min.Z - CL, b.max.Z + CL))
    out = e[0]
    for x in e[1:]:
        out = out + x
    return out


envA = envelope(V.cart2, 0.0)
envB = envelope(B.cart, D)
baseA = V.base2 - envB
baseB = Pos(0, D, 0) * V.base2 - envA
# перекладина под переднюю часть тележки Б — над мотором А, на колоннах по краям (как стойка 2Б, без пола)
YR0, YR1 = B.YR0 + D, B.YR1 + D
cols = None
for sx in (-1, 1):
    c = BB(*sorted((sx * 21.0, sx * HALF)), YR0, YR1, T.Z_FL - 0.01, L2[0] - 0.02) + CZ(0.75, L2[0] - 0.03, L2[0] + 1.2, sx * 23.0, (YR0 + YR1) / 2)
    cols = c if cols is None else cols + c
base = baseA + baseB + (cols - envA)
per = Pos(0, D, 0) * B.per
rackA, rackB = V.fix2, Pos(0, D, 0) * V.fix2
beamA, beamB = T.beam, Pos(0, D, 0) * T.beam


def poseA(s):
    return V.pose2(s)


def poseB(s):
    return {k: Pos(0, D, 0) * v for k, v in B.pose_b(s).items()}


PRINT = [("01_osnovanie_para", base, 0, 1), ("02_rejka_nepodvizhnaja_x2", V.fix2, 180, 2), ("03a_kolpak_rotora_x2", T.jacket, 180, 2),
         ("03b_shest_motora_x2", T.gear_m, 180, 2), ("05_polzun_x2", T.sl, 0, 2), ("06_shest_plav_x4", T.flo0, 0, 4),
         ("08_telezhka_A", V.cart2, 180, 1), ("08_telezhka_B_dlinnaja", B.cart, 180, 1), ("10_brusok_x2", T.beam, 0, 2), ("12_perekladina", B.per, 180, 1)]

if __name__ == "__main__":
    import trimesh

    def iv(a, b):
        try:
            r = a & b
            return 0.0 if r is None else r.volume
        except Exception:
            return 0.0
    print("сдвиг модуля Б D = %.2f, зазор колпаков %.2f" % (D, D - 2 * max(-bb(T.jacket).min.X, bb(T.jacket).max.X)))
    stat = {"основание": base, "рейкаА": rackA, "рейкаБ": rackB, "брусокА": beamA, "брусокБ": beamB, "моторА": T.motor,
            "моторБ": Pos(0, D, 0) * T.motor, "49E_А": T.hall, "49E_Б": Pos(0, D, 0) * T.hall, "перекладина": per}
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
                    if a in mv and b in mv and a[:2] == b[:2] and s2 != 0:
                        continue                                                  # свои подвижные внутри модуля уже проверены
                    v = iv(al[a], al[b])
                    if v > 0.05:
                        bad += 1
                        print("  s=%+.1f/%+.1f %s × %s: %.2f" % (s1, s2, a, b, v))
    for a, b in (("рейкаА", "основание"), ("рейкаБ", "основание"), ("перекладина", "основание"), ("брусокА", "основание"), ("брусокБ", "основание")):
        v = iv(stat[a], stat[b])
        if v > 0.05:
            bad += 1; print("  статика %s × %s %.2f" % (a, b, v))
    if iv(Pos(0, 0, -0.3) * poseB(0)["тележка"], per) < 0.01:
        print("  внимание: тележка Б не опирается на перекладину")
    bbx = bb(base)
    print("пара: %s; основание %.1f × %.1f × %.1f; площадки под пальцы: центры y %.2f и %.2f" % ("ЧИСТО" if not bad else "%d пересечений" % bad, bbx.size.X, bbx.size.Y, bbx.size.Z,
          Y_PA, Y_PB + D))
    for n, p, flip, cnt in PRINT:
        p = Rot(flip, 0, 0) * (Part() + p)
        b = p.bounding_box()
        p = Pos(-(b.min.X + b.max.X) / 2, -(b.min.Y + b.max.Y) / 2, -b.min.Z) * p
        export_stl(p, "stl_para/%s.stl" % n, tolerance=0.01, angular_tolerance=0.1)
        m = trimesh.load("stl_para/%s.stl" % n)
        ov = float(m.area_faces[(m.face_normals[:, 2] < -0.72) & (m.triangles_center[:, 2] > 0.25)].sum())
        print("  %-28s ×%d %5.1f × %5.1f × %4.1f герм %s нависание %.1f мм²" % (n, cnt, b.size.X, b.size.Y, b.size.Z, m.is_watertight, ov))
    for n, p in (("base", base), ("rackA", rackA), ("rackB", rackB), ("beamA", beamA), ("beamB", beamB), ("motorA", T.motor), ("motorB", Pos(0, D, 0) * T.motor),
                 ("hallA", T.hall), ("hallB", Pos(0, D, 0) * T.hall), ("per", per), ("slider", T.sl), ("flo", T.flo0), ("cartA", V.cart2), ("cartB", B.cart),
                 ("pin_m", T.pin_m0), ("jacket", T.jacket)):
        export_stl(Part() + p, "asm_para/%s.stl" % n, tolerance=0.02, angular_tolerance=0.2)
    open("asm_para/D.txt", "w").write(str(D))
    print("asm_para готово")
