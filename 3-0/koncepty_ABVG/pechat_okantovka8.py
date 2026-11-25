# -*- coding: utf-8 -*-
"""Печатный набор одного модуля в окантовке 8 (проба клика): MOD=P (по умолчанию) или Z.
Каждая деталь по одной (что нужно ×2 — помечено). Блок-навес над кнопкой — отдельная деталь на клей к стойке бруска (иначе нависание 7.8 мм).
Запуск: MOD=P python pechat_okantovka8.py → ../19.70_pechat_okantovka8_P (STL + детали.png)."""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from build123d import *
import trimesh
import modul_okantovka8 as Q
MOD = Q.MOD
T, K, DB, BB = Q.T, Q.K, Q.DB, Q.BB
OUT = os.path.join(os.path.dirname(HERE), "19.70_pechat_okantovka8_%s" % Q.TAG); os.makedirs(OUT, exist_ok=True)
for _f in os.listdir(OUT):
    if _f.endswith(".stl"): os.remove(os.path.join(OUT, _f))
base = Q.platform["base"]
parts = []
if MOD == "P":                                                                     # 24.11 (владелец): рейка с держателями-«Г» (плечо давит на кнопку, слева язык в паз) — одна деталь; брусок со стойками — одна деталь
    parts.append(("02_platforma_P", base, (0, 0, 0), 1, "пол с кольцом мотора, язычками-осью; гнёзда под стойки бруска и пазы под держатели рейки"))
    if Q.PV == "3":
        parts.append(("03a_plecho_prav", Q.ARMS["prav"], (0, 0, 0), 1, "правое плечо: шип сзади — в паз столба рейки, клей; низ — на шток кнопки; шип сверху — в паз бруска; печать плоско на низ"))
        parts.append(("03b_plecho_lev", Q.ARMS["lev"], (0, 0, 0), 1, "левое плечо: шип сзади — в паз столба рейки, клей; снизу паз — на шип стойки окантовки; шип сверху — в паз бруска; печать плоско на низ"))
    if Q.PV == "3":
        parts.append(("04a_derzhatel_prav", Q.HOLD["prav"], (-90, 0, 0), 1, "правый держатель рейки: низ в паз пола у кольца мотора, шип сверху — в паз рейки, спереди паз под шип плеча; клей; печать плашмя на задней грани"))
        parts.append(("04b_derzhatel_lev", Q.HOLD["lev"], (-90, 0, 0), 1, "левый держатель рейки: то же зеркально; печать плашмя на задней грани"))
    parts.append(("04_rejka_P", Q.parts["rack"], (180, 0, 0), 1, "рейка: снизу 2 паза под шипы держателей, клей; печать верхом на стол" if Q.PV == "3" else "рейка + 2 держателя-«Г» одной деталью: низ держателей в пазы пола (у кольца мотора), правое плечо — на кнопку, слева язык в паз стойки; клей внизу"))
else:                                                                             # 21.11: всё, что висит над окантовкой (блок стойки бруска, ножка балки, переходник), — отдельно на клей
    cut = Part() + [BB(*sorted((sx * Q.XP, sx * 30)), -40, 40, Q.Z_AW - 0.01, 40) for sx in (-1, 1)]
    nav = base & cut
    base = base - cut
    navR = Part() + [s_ for s_ in nav.solids() if s_.center().X > 0]
    navL = Part() + [s_ for s_ in nav.solids() if s_.center().X < 0]
    parts.append(("02_platforma_Z", base, (0, 0, 0), 1, "пол со стойками бруска, язычками-осью"))
    parts.append(("03a_noga_balki_prav", navR, (0, 0, 0), 1, "правая ножка балки с блоком над кнопкой — на клей к стойке бруска (печать стоя, низом на стол)"))
    parts.append(("03b_noga_balki_lev", navL, (0, 0, 0), 1, "левая ножка балки с блоком над кнопкой — на клей к стойке бруска (печать стоя, низом на стол)"))
    parts.append(("04_rejka_stolik_Z", Q.parts["rack"], (180, 0, 0), 1, "рейка-«столик» со стенками — низ стенок в паз пола"))
    parts.append(("03c_balka_Z", Q.parts["beam"], (180, 0, 0), 1, "балка под тележкой — на ножки, клей"))
if MOD == "Z":                                                                     # 23.11: у З стойки клеятся на окантовку ПОСЛЕ платформы соседа П (дно стойки — крышка его ямки)
    parts = [("14_stojka_knopki_Z", Q.PILLAR_BTN, (0, 0, 0), 1, "стойка с вазой под кнопку — на клей к окантовке справа под ножкой балки (в ряду: после того как вложен П, она накрывает его язычок)"),
             ("15_stojka_paza_Z", Q.PILLAR_GROOVE, (0, 0, 0), 1, "стойка с пазом — на клей к окантовке слева, ножка балки входит в паз")] + parts
parts = [("01_okantovka_%s" % MOD, Q.rim + (Q.vases if MOD == "P" else Part()), (0, 0, 0), 1, "окантовка: справа стойка с вазой под одну кнопку Ø6.4×5 наверху (у П — под держателем рейки) (щели по бокам, канавка для проводов), слева стойка с пазом, сзади ямки под язычки (открыты сверху)"),
         ("13_kryshki_osi_x2", Part() + Q.lids.solids()[0], (180, 0, 0), 2, "крышки на ямки язычков — кладёшь сверху после платформы, клей (можно пока не ставить, придерживать рукой)")] + parts
mock = T.CZ(13.9, T.Z_FL, T.Z_M1) + T.CZ(4.0, T.Z_M1 - 0.01, T.Z_M1 + 0.1) + T.CZ(1.5, T.Z_M1 + 0.09, T.L1[1])
parts += ([] if Q.BRUSOK is None else [("05_brusok", Q.BRUSOK, (180, 0, 0) if MOD == "P" else (0, 0, 0), 1, ("брусок: снизу 2 паза под шипы плеч — положить на плечи, клей; печать верхом на стол, без поддержек" if Q.PV == "3" else "брусок со стойками одной деталью — низ стоек в гнёзда пола, клей; снизу выемка над ротором") if MOD == "P" else "брусок под ползуном с упорами хода на концах — на стойки, клей"),
          ])
parts += [("06_polzun", Q.SL, (0, 0, 0), 1, "ползун: паз снизу, ложится на брусок"),
          ("07_shest_plav_x2", K.flo0, (0, 0, 0), 2, "плавающие шестерни на оси ползуна"),
          ("08_shest_motora", K.gm, (180, 0, 0), 1, "шестерня мотора — квадратом в гнездо платформы ротора, клей"),
          ("09_platforma_rotora", DB.plat, (0, 0, 0), 1, "платформа ротора: 8 магнитов Ø4×1.9 боком, N/S через один"),
          ("10_stojka_49E_x2", Q.P0, (0, 0, 0), 2, "стойка датчика 49E — низом в прорезь кольца/пола"),
          ("11_telezhka_%s" % MOD, Q.cart, (180, 0, 0), 1, "тележка с площадкой"),
          ("12_maket_motora", mock, (0, 0, 0), 1, "макет мотора 2204 для пробы без мотора (ось Ø3)")]
lines = []
print("печатный набор модуля %s → %s" % (MOD, OUT))
for n, p, rot, cnt, note in parts:
    p = Rot(*rot) * (Part() + p); b = p.bounding_box(); p = Pos(-(b.min.X + b.max.X) / 2, -(b.min.Y + b.max.Y) / 2, -b.min.Z) * p
    f = os.path.join(OUT, n + ".stl"); export_stl(p, f, tolerance=0.01, angular_tolerance=0.1)
    m = trimesh.load(f); ov = float(m.area_faces[(m.face_normals[:, 2] < -0.72) & (m.triangles_center[:, 2] > 0.25)].sum())
    b = p.bounding_box()
    s = "  %-24s ×%d  %5.1f × %5.1f × %4.1f  герм %s  нависание %.0f мм²  — %s" % (n, cnt, b.size.X, b.size.Y, b.size.Z, m.is_watertight, ov, note)
    print(s); lines.append(s)
open(os.path.join(OUT, "spisok.txt"), "w", encoding="utf-8").write("\n".join(lines) + "\nКупить на модуль: мотор 2204, 1 кнопка Ø6.4×5 (корпус 3.5 + шток 1.5), 2× SS49E, 8 магнитов Ø4×1.9, винты М2.\n")
# картинка: все детали по отдельности
import pyvista as pv
pv.OFF_SCREEN = True
fs = [(n, cnt) for n, *_r, cnt, _nt in [(x[0], x[1], x[2], x[3], x[4]) for x in parts]]
cols = 4; rows = (len(parts) + cols - 1) // cols
pl = pv.Plotter(off_screen=True, shape=(rows, cols), window_size=(cols * 420, rows * 380), border=False)
for i, (n, *_r) in enumerate(parts):
    pl.subplot(i // cols, i % cols); pl.set_background("white")
    mesh = pv.read(os.path.join(OUT, n + ".stl"))
    pl.add_mesh(mesh, color="#a7b4c6", smooth_shading=False, show_edges=False)
    pl.add_text(n, font_size=9, color="black", position="upper_left")
    pl.camera_position = "iso"; pl.reset_camera()
pl.screenshot(os.path.join(OUT, "detali_%s.png" % MOD))
print("картинка деталей:", os.path.join(OUT, "detali_%s.png" % MOD))
# 23.11: те же детали в собранном положении (для сцены «что куда»): ../19.70_.../sborka/*.stl
SB = os.path.join(OUT, "sborka"); os.makedirs(SB, exist_ok=True)
for _f in os.listdir(SB):
    if _f.endswith(".stl"): os.remove(os.path.join(SB, _f))
pose = {n: p for n, p, *_r in parts}
mb = K.motor.bounding_box(); kb = mock.bounding_box()
pose["13_kryshki_osi_x2"] = Q.lids
pose["07_shest_plav_x2"] = Part() + [Pos(sx * Q.A, K.Y_G, 0) * K.flo0 for sx in (-1, 1)]
pose["08_shest_motora"] = Pos(0, Q.YM, 0) * K.gm
pose["09_platforma_rotora"] = Pos(0, Q.YM, 0) * DB.plat
pose["10_stojka_49E_x2"] = Q.parts["posts"]
pose["12_maket_motora"] = Pos((mb.min.X + mb.max.X - kb.min.X - kb.max.X) / 2, (mb.min.Y + mb.max.Y - kb.min.Y - kb.max.Y) / 2, 0) * mock
pose["k1_knopka"] = Q.btns
pose["k2_magnity"] = Pos(0, Q.YM, 0) * DB.mags
pose["k3_datchiki_49E"] = Q.parts["sens"]
for n, p in pose.items():
    export_stl(Part() + p, os.path.join(SB, n + ".stl"), tolerance=0.02, angular_tolerance=0.2)
print("сборка (детали на местах):", SB, len(pose))
