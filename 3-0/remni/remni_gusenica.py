# Идея владельца (28.11): ленты — вертикальные петли («гусеница») поперёк грифа; моторы GB1806 лёжа вынесены за зону пальцев,
# по два с каждого конца (блок А крутит ленты 1 и 2, блок Б — 3 и 4, зеркально). Внизу петли — ролики Ø10 (12 зубьев)
# на валах моторов: свой — ведущий, на чужом валу — свободная втулка.
# 28.11 v2 (владелец нашёл пересечение угловых роликов с нижними): угловые ролики убраны — у каждой петли только два ролика Ø10
# на концах (x = ±20.5, на двух валах своего блока): ремень обнимает ведущий на ~180°, верхняя ветвь ровная.
# Верхняя ветвь прямая, по ней едет тележка; ушки-пилы смотрят вверх, зуб тележки — сверху между ними.
# Запуск: blender -b -P remni_gusenica.py
import bpy, math, os
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.unit_settings.scale_length = 0.001; sc.unit_settings.length_unit = 'MILLIMETERS'
HERE = os.path.dirname(os.path.abspath(__file__))
W = 53.0; HW = W / 2
STR = [-21.0 + 8.4 * k for k in range(6)]
LANE = 11.25; YL = [LANE * (i - 1.5) for i in range(4)]
BW, TB, H_T = 3.0, 0.9, 0.7                         # ремень 3 мм (ширина вдоль грифа), спинка, зуб
P = 2.659; R_D = 12 * P / (2 * math.pi); R_I = 6 * P / (2 * math.pi)
R_M, L_BODY, L_CAP = 11.0, 13.0, 7.5                # GB1806: Ø22, корпус-ротор 13 + стакан 7.5
FL = 1.0                                            # дно блока
Z_M = FL + R_M                                      # ось мотора лёжа = ось нижних роликов (12)
X_M = float(os.environ.get("X_M", "20.5"))          # оси моторов = концы петли: ролик Ø10 со спинкой доходит до края грифа 26.5 (мотор в блоке выходит за гриф)
X_T = 22.0                                          # верхние угловые ролики
Z_TOP = Z_M + R_D                                   # внутренняя сторона верхней ветви — по верху роликов Ø10
Z_BACK = Z_TOP + TB
HP = 1.5                                            # ушки-пилы вверх
Z_CART0 = Z_BACK + HP + 0.2; Z_CART1 = Z_CART0 + 1.2
Y_FACE = YL[3] + 5.0 + 2.0                          # торец ротора: за площадкой тележки (10 вдоль грифа) + 2
COLS = [(0.95, 0.85, 0.15, 1), (0.2, 0.3, 0.9, 1), (0.85, 0.15, 0.15, 1), (0.1, 0.75, 0.8, 1)]


def mat(n, c):
    m = bpy.data.materials.new(n); m.diffuse_color = c; return m


def mesh(name, v, f, m):
    me = bpy.data.meshes.new(name); me.from_pydata(v, [], f); me.update()
    o = bpy.data.objects.new(name, me); sc.collection.objects.link(o); o.data.materials.append(m); return o


def box(n, x0, x1, y0, y1, z0, z1, m):
    v = [(x, y, z) for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)]
    return mesh(n, v, [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)], m)


def cyl_y(n, r, y0, y1, x, z, m, seg=48):          # цилиндр с осью вдоль грифа (y)
    v = [(x + r * math.cos(2 * math.pi * k / seg), y, z + r * math.sin(2 * math.pi * k / seg)) for y in (y0, y1) for k in range(seg)]
    f = [list(range(seg)), list(range(seg, 2 * seg))[::-1]] + [[k, seg + k, seg + (k + 1) % seg, (k + 1) % seg] for k in range(seg)]
    return mesh(n, v, f, m)


def hull(pts):                                      # выпуклая оболочка, против часовой
    pts = sorted(set(pts))
    def cross(o, a, b): return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0: lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0: up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


def band(name, cl, y0, y1, m):                      # лента вдоль замкнутой осевой в плоскости x-z, толщина TB
    n = len(cl); v = []
    for i in range(n):
        (xa, za), (xb, zb) = cl[i - 1], cl[(i + 1) % n]
        tx, tz = xb - xa, zb - za; L = math.hypot(tx, tz); nx, nz = tz / L, -tx / L
        x, z = cl[i]
        for s in (-TB / 2, TB / 2):
            for y in (y0, y1):
                v.append((x + nx * s, y, z + nz * s))
    f = []
    for i in range(n):
        a = [4 * i + k for k in range(4)]; b = [4 * ((i + 1) % n) + k for k in range(4)]
        for p, q in ((0, 1), (1, 3), (3, 2), (2, 0)):
            f.append((a[p], b[p], b[q], a[q]))
    return mesh(name, v, f, m)


M_FR, M_MOT, M_CAP = mat("основа", (0.65, 0.65, 0.67, 1)), mat("мотор", (0.08, 0.08, 0.09, 1)), mat("стакан", (0.2, 0.2, 0.22, 1))
M_ROL, M_FREE, M_SH, M_STR = mat("ведущий ролик", (0.85, 0.85, 0.87, 1)), mat("свободная втулка", (0.5, 0.5, 0.55, 1)), mat("вал", (0.75, 0.6, 0.3, 1)), mat("струна", (0.85, 0.75, 0.4, 1))
Y_END = Y_FACE + L_BODY + L_CAP + 1
box("плита грифа", -HW, HW, -Y_END - 10, Y_END + 10, -2.0, -0.05, mat("гриф", (0.8, 0.65, 0.45, 1)))
box("дно", -HW, HW, -Y_END, Y_END, 0, FL, M_FR)
for k in range(6):
    box("струна %d" % (6 - k), STR[k] - 0.25, STR[k] + 0.25, -Y_FACE + 1, Y_FACE - 1, Z_CART1 + 3, Z_CART1 + 3.5, M_STR)
# моторы: блок А (−y) — ленты 1 (x = −13) и 2 (x = +13); блок Б (+y) — ленты 4 (x = +13) и 3 (x = −13)
DRIVE = {0: (-X_M, -1), 1: (X_M, -1), 3: (X_M, 1), 2: (-X_M, 1)}
for lane, (xm, sd) in DRIVE.items():
    y0 = sd * Y_FACE
    cyl_y("мотор GB1806 лёжа (лента %d)" % (lane + 1), R_M, *sorted((y0, y0 + sd * L_BODY)), xm, Z_M, M_MOT)
    cyl_y("стакан AS5600 (лента %d)" % (lane + 1), R_M, *sorted((y0 + sd * L_BODY, y0 + sd * (L_BODY + L_CAP))), xm, Z_M, M_CAP)
    y_far = YL[1 if sd < 0 else 2] - sd * (BW / 2 + 1.5)          # вал проходит обе ленты своего блока
    cyl_y("вал Ø3 от ротора к ленте %d" % (lane + 1), 1.5, *sorted((y0, y_far)), xm, Z_M, M_SH)
wrap = {}
for i in range(4):
    yc = YL[i]; mb = mat("ремень %d" % (i + 1), COLS[i]); y0, y1 = yc - BW / 2, yc + BW / 2
    circ = [(-X_M, Z_M, R_D), (X_M, Z_M, R_D)]
    pts = [(round(cx + (r + TB / 2) * math.cos(2 * math.pi * k / 360), 4), round(cz + (r + TB / 2) * math.sin(2 * math.pi * k / 360), 4)) for cx, cz, r in circ for k in range(360)]
    cl = hull(pts)
    band("ремень %d (вертикальная петля)" % (i + 1), cl, y0, y1, mb)
    xd = DRIVE[i][0]
    wrap[i] = len([p for p in cl if abs(math.hypot(p[0] - xd, p[1] - Z_M) - (R_D + TB / 2)) < 0.01])   # точек по 1° на ведущем
    for cx, cz, r in circ:
        drv = (cz == Z_M and cx == xd)
        nm = "ведущий ролик Ø10 (на валу своего мотора)" if drv else "свободный ролик Ø10 (крутится на неподвижной трубке)"
        mm = M_ROL if drv else M_FREE
        cyl_y(nm, r, y0 - 0.2, y1 + 0.2, cx, cz, mm)
        cyl_y(nm + ": юбка", r + TB + 0.3, y0 - 0.8, y0 - 0.2, cx, cz, mm)
        cyl_y(nm + ": юбка", r + TB + 0.3, y1 + 0.2, y1 + 0.8, cx, cz, mm)
    C = bpy.data.objects.new("тележка %d" % (i + 1), None); sc.collection.objects.link(C)
    for sx in (-1, 1):                                  # ушки-пилы на верхней ветви (вверх), между ними зуб тележки
        u0 = 0.85
        v = [(sx * u0, y0, Z_BACK - 0.02), (sx * (u0 + 3), y0, Z_BACK - 0.02), (sx * (u0 + 3), y0, Z_BACK + 0.05), (sx * u0, y0, Z_BACK + HP)]
        v += [(x, y1, z) for x, _, z in v]
        mesh("ушко-пила", v, [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)], mb).parent = C
    box("зуб тележки", -0.75, 0.75, y0, y1, Z_BACK + 0.1, Z_CART0 + 0.01, mb).parent = C
    box("площадка 8.5 × 10", -4.25, 4.25, yc - 5, yc + 5, Z_CART0, Z_CART1, mb).parent = C
    for f in range(1, 241, 3):
        C.location.x = 21 * math.sin(2 * math.pi * ((f - 1) / 120 + 0.27 * i)); C.keyframe_insert("location", index=0, frame=f)
# 28.11 v3 (владелец): свободный ролик крутится на неподвижной трубке, вал соседа проходит внутри трубки и ролик не тянет.
# Трубку держит перегородка между лентами своего блока (y = ±11.25), она же — опора валов.
M_TUBE, M_RIB = mat("трубка (неподвижная)", (0.45, 0.65, 0.85, 1)), mat("перегородка", (0.6, 0.6, 0.64, 1))
T_RO, T_RI = 2.5, 1.75                                  # трубка Ø5 снаружи (по ней ролик), Ø3.5 внутри (вал Ø3 крутится свободно)
for sd in (-1, 1):
    y_rib = sd * LANE                                   # между лентами 1–2 (−11.25) и 3–4 (+11.25)
    box("перегородка между лентами (держит трубки и валы)", -HW + 1, HW - 1, y_rib - 0.6, y_rib + 0.6, FL, Z_M + T_RO + 1.0, M_RIB)
for lane, (xm, sd) in DRIVE.items():
    free = {0: 1, 1: 0, 3: 2, 2: 3}[lane]               # на какой ленте у этого вала свободный ролик
    yf = YL[free]; y_rib = sd * LANE
    ya, yb = sorted((y_rib, yf - (BW / 2 + 1.2) * (1 if yf > y_rib else -1) * -1))
    cyl_y("трубка Ø5 под свободный ролик ленты %d (вал мотора ленты %d внутри)" % (free + 1, lane + 1), T_RO, ya, yb, xm, Z_M, M_TUBE)
sc.frame_start, sc.frame_end = 1, 240; sc.frame_set(1)
print("ЗОНА ПАЛЬЦЕВ: верх площадок %.1f мм над грифом (+ плита грифа 2 = %.1f; v13 было 29.4); низ петли %.1f, верхняя ветвь %.1f..%.1f" % (
    Z_CART1, Z_CART1 + 2, Z_M - R_D - TB, Z_TOP, Z_BACK))
import itertools
print("ролики соседних лент на одном валу: зазор между юбками %.1f мм" % (LANE - BW - 1.6))
print("обхват ведущего Ø10: ~%d° (около %.1f зуба из 12)" % (wrap[0], wrap[0] / 30))
print("блоки моторов: по y от %.1f до %.1f с каждой стороны; моторы Ø22 на x = ±%.1f — край мотора %.1f (гриф ±%.1f)" % (Y_FACE, Y_END, X_M, X_M + R_M, HW))
for scr in bpy.data.screens:
    for ar in scr.areas:
        for sp in ar.spaces:
            if sp.type == 'VIEW_3D':
                sp.shading.type = 'SOLID'; sp.shading.color_type = 'MATERIAL'; sp.clip_start = 0.5; sp.clip_end = 3000
                r3 = sp.region_3d; r3.view_location = (0, 0, 10); r3.view_distance = 170; r3.view_rotation = (0.80, 0.50, 0.15, 0.28)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "remni_gusenica.blend")); print("saved")
