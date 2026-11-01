# -*- coding: utf-8 -*-
r"""Сцена: общая сборка тренажёра «мотор в тележке» с корпусом из фанеры (01.11.2026, концепт для заказа лазерной резки).
Цвет = из чего деталь: ФАНЕРА (лазерная резка, заказ), ПЕЧАТЬ (свой принтер), АЛЮМИНИЙ (магазин), ПЭТ (бока),
электроника и моторы. Кадр 1 — собрано, кадр 120 — разлёт (порядок сборки). Пробел — анимация.
Корпус — контур классики из gitara_korpus.py (480 × 370, глубина 95); гриф (01.11, владелец): платформа с 4 тележками
GB1806 высотой ~27 мм и есть гриф; дно плоское; перед платформой — плоское дно со струнами; толкатель из корпуса
(короб с проводами) толкает платформу, NEMA17 в корпусе; тележки ходят ±22 и выходят за края грифа.
Запуск: blender -b -P 2-0\scene_sborka_fanera.py
"""
import math
import os
import bpy
import bmesh
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "Гитара_сборка_фанера.blend")
FR = 120

# ---------------- контур корпуса (как gitara_korpus.py): гриф к −Y, корпус y 480 … 960 ----------------
PROF = [(480, 60), (492, 100), (510, 124), (535, 138), (560, 140), (590, 134), (620, 124), (650, 118), (668, 117),
        (690, 121), (720, 136), (750, 158), (775, 174), (800, 183), (830, 185), (860, 181), (890, 168), (915, 147),
        (935, 118), (950, 82), (958, 44), (960, 0)]


def catmull(pts, per_seg=6):
    p = np.array(pts, float)
    p = np.vstack([p[0], p, p[-1]])
    out = []
    for i in range(1, len(p) - 2):
        for t in np.linspace(0, 1, per_seg, endpoint=False):
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p[i]) + (-p[i - 1] + p[i + 1]) * t + (2 * p[i - 1] - 5 * p[i] + 4 * p[i + 1] - p[i + 2]) * t2 +
                              (-p[i - 1] + 3 * p[i] - 3 * p[i + 1] + p[i + 2]) * t3))
    out.append(p[-2])
    return np.array(out)


half = catmull(PROF)
east = np.c_[half[:, 1], half[:, 0]][::-1]
west = np.c_[-half[:, 1], half[:, 0]]
top = np.array([[x, 480.0] for x in np.linspace(55, -55, 12)])
CONTOUR = np.vstack([east, top, west[:-1]])
# 01.11 (владелец): как у настоящей классики — корпус начинается на XII ладу (325 мм от порожка), а не на 480
BODY_DY = 325.0 - 480.0
CONTOUR = CONTOUR + np.array([0.0, BODY_DY])


def inset(pts, d):
    p = np.array(pts, float)
    e = np.roll(p, -1, 0) - p
    en = e / np.linalg.norm(e, axis=1, keepdims=True)
    nrm = np.c_[-en[:, 1], en[:, 0]]
    vn = nrm + np.roll(nrm, 1, 0)
    vn /= np.linalg.norm(vn, axis=1, keepdims=True)
    inward = vn if np.dot(vn[0], np.array([0, 720 + BODY_DY]) - p[0]) > 0 else -vn
    return p + inward * d


# ---------------- высоты ----------------
Z_N0, Z_N2 = -1.5, 0.0                    # дно грифа: плоский лист 1.5 мм (01.11: мотор 22 + ~3 мм на дно и платформу)
Z_DECK0, Z_DECK1 = 26.5, 32.5             # 01.11: дека над коробом толкателя во всю высоту грифа (верх ложа 25.7)
DEPTH = 95.0
Z_BOT0 = Z_DECK1 - DEPTH                  # −84
Z_BOT1 = Z_BOT0 + 6                       # −78
PLY_RING = 13.0                           # ширина колец-рамок
STRIP = 1.5                               # бока: полоса ПЭТ
NUT_Y, BODY_Y, TAIL_Y = 0.0, 325.0, 775.0               # порожек, край корпуса (XII), хвост канала толкателя
HEAD_Y = -180.0
W = 52.0
P0 = 140.0                                # платформа на V позиции

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.unit_settings.system, sc.unit_settings.scale_length, sc.unit_settings.length_unit = 'METRIC', 0.001, 'MILLIMETERS'
sc.frame_start, sc.frame_end = 1, FR


def mat(name, rgba, alpha=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rgba
    if alpha < 1:
        b.inputs["Alpha"].default_value = alpha
        m.surface_render_method = 'BLENDED'
    m.diffuse_color = (rgba[0], rgba[1], rgba[2], alpha)
    return m


M_PLY = mat("ФАНЕРА — лазерная резка", (0.86, 0.70, 0.48, 1))
M_PLY_D = mat("ФАНЕРА — дека (лазер)", (0.80, 0.62, 0.40, 1), 0.45)
M_PRN = mat("ПЕЧАТЬ — свой принтер", (0.95, 0.55, 0.20, 1))
M_ALU = mat("АЛЮМИНИЙ — магазин", (0.72, 0.74, 0.78, 1))
M_PET = mat("ПЭТ 1.5 мм — бока", (0.92, 0.94, 0.96, 1), 0.35)
M_EL = mat("ЭЛЕКТРОНИКА", (0.15, 0.55, 0.25, 1))
M_MOT = mat("МОТОРЫ", (0.12, 0.12, 0.14, 1))
M_STR = mat("струны (нарисованы)", (0.95, 0.95, 0.97, 1))
M_LZ = mat("ложе", (0.85, 0.30, 0.30, 1))
M_CAGE = mat("ПЕЧАТЬ — тележка", (0.95, 0.55, 0.20, 1), 0.45)
M_SHELL = mat("ПЕЧАТЬ — корпус тележки (в цвет короба толкателя)", (0.86, 0.70, 0.48, 1))

OBJS = []                                  # (объект, смещение при разлёте)


def mesh_obj(name, verts, faces, m, ex=(0, 0, 0)):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], faces)
    me.update()
    ob = bpy.data.objects.new(name, me)
    sc.collection.objects.link(ob)
    ob.data.materials.append(m)
    OBJS.append((ob, ex))
    return ob


def prism(name, poly, z0, z1, m, ex=(0, 0, 0)):
    """призма по замкнутому многоугольнику (x, y)"""
    n = len(poly)
    v = [(x, y, z0) for x, y in poly] + [(x, y, z1) for x, y in poly]
    f = [list(range(n))[::-1], list(range(n, 2 * n))] + [[i, (i + 1) % n, n + (i + 1) % n, n + i] for i in range(n)]
    ob = mesh_obj(name, v, f, m, ex)
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ob.data)
    bm.free()
    return ob


def ring(name, outer, inner, z0, z1, m, ex=(0, 0, 0)):
    """кольцо между двумя контурами с одинаковым числом точек"""
    n = len(outer)
    v = ([(x, y, z0) for x, y in outer] + [(x, y, z1) for x, y in outer] +
         [(x, y, z0) for x, y in inner] + [(x, y, z1) for x, y in inner])
    f = []
    for i in range(n):
        j = (i + 1) % n
        f += [[i, j, n + j, n + i], [2 * n + j, 2 * n + i, 3 * n + i, 3 * n + j],
              [n + i, n + j, 3 * n + j, 3 * n + i], [j, i, 2 * n + i, 2 * n + j]]
    ob = mesh_obj(name, v, f, m, ex)
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ob.data)
    bm.free()
    return ob


def box(name, x0, x1, y0, y1, z0, z1, m, ex=(0, 0, 0)):
    return prism(name, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, z1, m, ex)


def cut(ob, cutter):
    mod = ob.modifiers.new("cut", 'BOOLEAN')
    mod.object, mod.operation, mod.solver = cutter, 'DIFFERENCE', 'EXACT'
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.modifier_apply(modifier=mod.name)


def cutter_box(x0, x1, y0, y1, z0, z1):
    c = box("_cut", x0, x1, y0, y1, z0, z1, M_PLY)
    OBJS.pop()
    return c


def drop(c):
    bpy.data.objects.remove(c, do_unlink=True)


def cyl(name, r, y0, y1, x, z, m, ex=(0, 0, 0), axis='Y', n=32):
    """цилиндр вдоль Y (или X) — через призму в плоскости и поворот"""
    poly = [(r * math.cos(2 * math.pi * k / n), r * math.sin(2 * math.pi * k / n)) for k in range(n)]
    ob = prism(name, poly, 0, y1 - y0, m, ex)
    if axis == 'Y':
        ob.rotation_euler = (-math.pi / 2, 0, 0)
        ob.location = (x, y0, z)
    elif axis == 'X':
        ob.rotation_euler = (0, math.pi / 2, 0)
        ob.location = (y0, x, z)
    else:                                                # 'Z': y0 … y1 — высота, (x, z) — центр в плане
        ob.location = (x, z, y0)
    return ob


C0 = CONTOUR
C_STRIP = inset(C0, STRIP)
C_RING = inset(C0, STRIP + PLY_RING)

# ================= КОРПУС =================
EX_B = 1.0
prism("корпус: дно (фанера 6)", C0, Z_BOT0, Z_BOT1, M_PLY, (0, 0, -170))
ring("корпус: кольцо дна (фанера 6)", C_STRIP, C_RING, Z_BOT1, Z_BOT1 + 6, M_PLY, (0, 0, -120))
side = ring("корпус: бока (полоса ПЭТ 1.5)", C0, C_STRIP, Z_BOT1, Z_DECK0, M_PET, (0, 0, -60))
# проём в боку и кольце деки + окно в деке: на высоких позициях (IX–XII) платформа с тележками заезжает в корпус,
# тележки выступают за край грифа до ±36 — окно ±38, до конца платформы на XII (~420) с запасом
TR_X, TR_Y1 = 38.0, BODY_Y + 125
c = cutter_box(-TR_X, TR_X, BODY_Y - 10, TR_Y1, Z_N0 - 20, Z_DECK0 + 1)
cut(side, c)
rdk = ring("корпус: кольцо деки (фанера 6)", C_STRIP, C_RING, Z_DECK0 - 6, Z_DECK0, M_PLY, (0, 0, 110))
cut(rdk, c)
drop(c)
deck = prism("корпус: дека (фанера 6)", C0, Z_DECK0, Z_DECK1, M_PLY_D, (0, 0, 170))
c = cutter_box(-TR_X, TR_X, BODY_Y - 10, TR_Y1, Z_DECK0 - 1, Z_DECK1 + 1)
cut(deck, c)
drop(c)
ROZ_Y = TR_Y1 + 55                          # розетка — рисунок на деке (отверстие открыло бы толкатель)
cyl("корпус: розетка (рисунок)", 43.5, Z_DECK1, Z_DECK1 + 0.3, 0, ROZ_Y, mat("розетка", (0.25, 0.18, 0.12, 1)), (0, 0, 175), axis='Z')
box("корпус: подставка (декор, на мензуре 650)", -45, 45, 645, 660, Z_DECK1, Z_DECK1 + 8, M_PRN, (0, 0, 180))
box("корпус: брусок под пятку грифа (фанера, склейка)", -45, 45, BODY_Y + 3, BODY_Y + 85, Z_BOT1, Z_N0 - 16, M_PLY, (0, 0, -90))
box("корпус: брусок в хвосте (фанера, склейка)", -40, 40, TAIL_Y - 40, TAIL_Y + 10, Z_BOT1, Z_N0, M_PLY, (0, 0, -90))
box("корпус: плата питания и связи", -60, -10, 600, 660, Z_BOT1 + 6, Z_BOT1 + 8, M_EL, (0, 0, -40))
# NEMA17 толкателя: под каналом, шестерня через окно в нижнем слое дна грифа
Y_M = BODY_Y + 145                         # 470: под коробом толкателя при любом положении платформы
Z_GM = -2.7 - 16.5                         # ось шестерни: верх зубьев у низа рейки толкателя
box("корпус: NEMA17 толкателя", 28, 68, Y_M - 21, Y_M + 21, Z_GM - 21, Z_GM + 21, M_MOT, (80, 0, -30))
cyl("корпус: шестерня толкателя m1 z33 (печать)", 16.5, -3, 3, Y_M, Z_GM, M_PRN, (80, 0, -30), axis='X')
box("корпус: стойка мотора (печать)", 22, 70, Y_M - 24, Y_M + 24, Z_BOT1, Z_GM - 21, M_PRN, (80, 0, -60))

# ================= ГРИФ =================
EXN = -330.0                               # гриф при разлёте отъезжает вбок от корпуса
# 01.11 (владелец): гриф к корпусу расширяется, как у настоящей — 52 у порожка, 60 у XII; платформа и короб — 52
W12 = 60.0
hw = lambda y: W / 2 + (W12 - W) / 2 * min(max(y, 0.0), BODY_Y) / BODY_Y
head = [(-W / 2, NUT_Y), (-36, NUT_Y - 30), (-38, HEAD_Y + 10), (-28, HEAD_Y), (28, HEAD_Y), (38, HEAD_Y + 10), (36, NUT_Y - 30),
        (W / 2, NUT_Y), (W12 / 2, BODY_Y), (W12 / 2, TAIL_Y), (-W12 / 2, TAIL_Y), (-W12 / 2, BODY_Y)]
# 01.11 (владелец): гриф = платформа с тележками высотой ~27 мм, как настоящий гриф; дно грифа ПЛОСКОЕ (ни ребра, ни
# спинки); перед платформой гриф плоский со струнами; толкатель из корпуса толкает платформу, его ход — внутри корпуса;
# тележки ходят поперёк ±22 и на крайних струнах выходят за края грифа. Жёсткость плоского дна — открытый вопрос.
nb = prism("гриф: плоское дно с головой (алюминий 1.5 мм — жёсткость решить)", head, Z_N0, Z_N2, M_ALU, (EXN, 0, -40))
c = cutter_box(-5, 5, 175, TAIL_Y - 5, Z_N0 - 1, Z_N2 + 1)                  # паз под рейку толкателя (с IV лада — открытый вопрос)
cut(nb, c)
drop(c)
# 01.11 (владелец): клин снизу по грифу (у XII 27 + 16 = 43 мм против ~24 у настоящей) — «слишком толстый, не обхватить»;
# утолщение осталось только в корпусе — пятка грифа на бруске (фанерные пластины, лазер, склеить)
WEDGE1 = 16.0
Z_HEEL = Z_N0 - WEDGE1
prof = [(BODY_Y, Z_N0), (BODY_Y + 85, Z_N0), (BODY_Y + 85, Z_HEEL), (BODY_Y, Z_HEEL)]
n = len(prof)
vw = [(-W12 / 2, y, z) for y, z in prof] + [(W12 / 2, y, z) for y, z in prof]
fw = [list(range(n)), list(range(n, 2 * n))[::-1]] + [[i, n + i, n + (i + 1) % n, (i + 1) % n] for i in range(n)]
wd = mesh_obj("гриф: пятка в корпусе — пластины фанеры 6 мм (лазер, склеить)", vw, fw, M_PLY, (EXN, 0, -90))
bm = bmesh.new()
bm.from_mesh(wd.data)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(wd.data)
bm.free()
c = cutter_box(-5, 5, 175, BODY_Y + 90, Z_N0 - 3.5, Z_N0 + 0.1)          # паз под рейку толкателя: средняя пластина клина ниже
cut(wd, c)
drop(c)
for sx in (1, -1):                                       # метки ладов на торцах дна (мензура 650)
    for n in range(1, 15):
        yf = 650 - 650 / 2 ** (n / 12)
        x0, x1 = sorted((sx * hw(yf), sx * (hw(yf) + 0.4)))
        if yf < BODY_Y:
            box("гриф: метка лада %d" % n, x0, x1, yf - 0.6, yf + 0.6, Z_N0, Z_N2, M_STR, (EXN, 0, -40))
box("гриф: порожек (печать)", -W / 2, W / 2, NUT_Y - 5, NUT_Y, Z_N2, Z_N2 + 8, M_PRN, (EXN, 0, 30))
for sx in (-22.0, -13.2, -4.4, 4.4, 13.2, 22.0):        # струны на неподвижном дне — перед платформой
    box("гриф: струна на дне", sx - 0.35, sx + 0.35, NUT_Y, P0, Z_N2, Z_N2 + 0.2, M_STR, (EXN, 0, -15))
box("гриф: плёнка PTFE под платформу", -24, 24, P0, P0 + 108, Z_N2, Z_N2 + 0.1, M_STR, (EXN, 0, 40))

# платформа: алюминий 1.5 мм, 4 рейки, 4 тележки GB1806, плата; дно 1.5 + платформа 1.5 + мотор 22 + ложе ≈ 27 мм
PL_L = 108.0                                              # 01.11: плата переехала в короб толкателя — платформа короче
Z_PL0, Z_PL1 = 0.1, 1.6                                   # платформа скользит по дну на плёнке PTFE 0.1
Z_MAX = Z_PL1 + 0.3 + 11                                  # ось мотора: низ мотора на 0.3 над платформой
Z_TOP = Z_MAX + 11 + 0.3                                  # клетка без крыши: сверху сразу ложе
box("платформа: основание (алюминий 1.5 мм)", -25.5, 25.5, P0, P0 + PL_L, Z_PL0, Z_PL1, M_ALU, (EXN, 0, 60))
ST = [13, 39, 65, 91]
FX = [-22.0, 4.4, 22.0, -13.2]                            # пальцы на разных струнах; на 1-й и 6-й тележка за краем грифа
for i, (sy, fx) in enumerate(zip(ST, FX)):
    y = P0 + sy
    box("платформа: рейка m1 %d (печать)" % (i + 1), -25.5, 25.5, y + 4, y + 9, Z_PL1, Z_MAX - 8 + 0.2, M_PRN, (EXN, 0, 80))
    # 01.11 (владелец): у каждой тележки свой корпус-«клавиша» — гладкая коробочка со скруглёнными углами в цвет короба
    # толкателя; общий короб на 4 тележки был бы ~76 мм шириной (ход 44 + тележка 28) — гриф под рукой шире настоящего
    sh = box("тележка %d: корпус-клавиша (печать)" % (i + 1), fx - 13.8, fx + 13.8, y - 11.5, y + 11.5, Z_PL1 + 0.3, Z_TOP + 4.5,
             M_SHELL, (EXN, 0, 150))
    c = cutter_box(fx - 10.5, fx + 10.5, y - 10, y + 10, Z_TOP + 1.5, Z_TOP + 6)                  # выемка под палец
    cut(sh, c)
    drop(c)
    bv = sh.modifiers.new("скругление", 'BEVEL')
    bv.width, bv.segments = 2.5, 4
    cyl("тележка %d: GB1806 + AS5048A" % (i + 1), 11, y - 10, y + 8, fx, Z_MAX, M_MOT, (EXN, 0, 120))
    cyl("тележка %d: шестерня m1 z14 (печать)" % (i + 1), 8, y + 8.4, y + 12, fx, Z_MAX, M_PRN, (EXN, 0, 120))
    box("тележка %d: ложе — мягкая накладка в выемке клавиши" % (i + 1), fx - 10, fx + 10, y - 9.5, y + 9.5, Z_TOP + 1.5, Z_TOP + 2.2,
        M_LZ, (EXN, 0, 190))
# толкатель: из корпуса толкает платформу; внутри — провода; ход прячется в корпусе
PU0, PU1 = P0 + PL_L, P0 + PL_L + 375.0                  # длина 375: на I конец у мотора, на XII не выходит из корпуса
# 01.11 (владелец): толкатель — короб во всю высоту грифа (красивее): верх вровень с ложами, ширина грифа; внутри провода
Z_PU1 = Z_TOP + 1.5
box("толкатель: короб, верх (фанера 3)", -W / 2, W / 2, PU0, PU1, Z_PU1 - 3, Z_PU1, M_PLY, (EXN, 0, 70))
for sx in (1, -1):
    x0, x1 = sorted((sx * W / 2, sx * (W / 2 - 3)))
    box("толкатель: короб, бок (фанера 3)", x0, x1, PU0, PU1, Z_PL0, Z_PU1 - 3, M_PLY, (EXN + sx * 20, 0, 50))
box("толкатель: короб, торец к платформе (фанера 3, окно под провода)", -W / 2 + 3, W / 2 - 3, PU0, PU0 + 3, Z_PL0 + 3, Z_PU1 - 3, M_PLY, (EXN, 0, 50))
box("толкатель: короб, дно (фанера 3)", -W / 2 + 3, W / 2 - 3, PU0, PU1, Z_PL0, Z_PL0 + 3, M_PLY, (EXN, 0, 30))
box("толкатель: плата ESP32 + 4 драйвера (внутри короба, у переднего конца)", -22, 22, PU0 + 6, PU0 + 48, Z_PL0 + 3, Z_PL0 + 4.6, M_EL,
    (EXN, 0, 100))
box("толкатель: рейка снизу (печать)", -4, 4, PU0 + 50, PU0 + 339, Z_PL0 - 3, Z_PL0, M_PRN, (EXN, 0, 50))
for sx in (-22.0, -13.2, -4.4, 4.4, 13.2, 22.0):
    box("толкатель: струна", sx - 0.35, sx + 0.35, PU0, PU1, Z_PU1, Z_PU1 + 0.2, M_STR, (EXN, 0, 70))
for k in range(4):                                       # винты пятки грифа в брусок
    box("винт пятки М4", -30 + 20 * k - 2, -30 + 20 * k + 2, BODY_Y + 40, BODY_Y + 44, Z_N0 - 36, Z_N2 + 1, M_ALU, (EXN, 0, -40))
print("гриф: от дна до ложа %.1f мм" % (Z_TOP + 1.5 - Z_N0))

# ---------------- анимация разлёта ----------------
for ob, ex in OBJS:
    base = tuple(ob.location)
    for f, k in ((1, 0.0), (20, 0.0), (90, 1.0), (FR, 1.0)):
        ob.location = (base[0] + ex[0] * k, base[1] + ex[1] * k, base[2] + ex[2] * k)
        ob.keyframe_insert("location", frame=f)

# камера, свет
tgt = bpy.data.objects.new("цель", None)
sc.collection.objects.link(tgt)
tgt.location = (-150, 380, -30)
cam = bpy.data.objects.new("Камера", bpy.data.cameras.new("Камера"))
sc.collection.objects.link(cam)
cam.data.clip_start, cam.data.clip_end, cam.data.lens = 1, 50000, 35
cam.location = (650, -330, 900)
tc = cam.constraints.new('TRACK_TO')
tc.target, tc.track_axis, tc.up_axis = tgt, 'TRACK_NEGATIVE_Z', 'UP_Y'
sc.camera = cam
w = bpy.data.worlds.new("мир")
w.color = (0.92, 0.92, 0.9)
sc.world = w
sun = bpy.data.objects.new("Солнце", bpy.data.lights.new("Солнце", "SUN"))
sun.data.energy = 3
sun.rotation_euler = (math.radians(30), math.radians(15), math.radians(30))
sc.collection.objects.link(sun)
sc.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("сборка: деталей", len(OBJS))
