# Гриф на ремнях (концепт и ТЗ владельца 26.11): 4 зубчатых ремня TPU поперёк грифа, концевые ролики Ø4, GB1806 в шахматку под ремнями,
# тележки 8.5 мм, ход 44 (центр тележки от струны 6 до струны 1), ничего не выходит за 52 мм. Запуск: blender -b -P remni4.py
import bpy, math, os
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.unit_settings.scale_length = 0.001; sc.unit_settings.length_unit = 'MILLIMETERS'
HERE = os.path.dirname(os.path.abspath(__file__))


def mat(n, c):
    m = bpy.data.materials.new(n); m.diffuse_color = c; return m


def box(n, x0, x1, y0, y1, z0, z1, m, p=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    o = bpy.context.object; o.scale = (x1 - x0, y1 - y0, z1 - z0); bpy.ops.object.transform_apply(scale=True)
    o.name = n; o.data.materials.append(m)
    if p: o.parent = p
    return o


def cyl(n, r, z0, z1, x, y, m, p=None, v=48):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=z1 - z0, vertices=v, location=(x, y, (z0 + z1) / 2))
    o = bpy.context.object; o.name = n; o.data.materials.append(m)
    if p: o.parent = p
    return o


def seg(n, p0, p1, z0, z1, t, m, p=None):                # отрезок ремня по ломаной (толщина t)
    import math as _m
    (x0, y0), (x1, y1) = p0, p1; L_ = _m.hypot(x1 - x0, y1 - y0)
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), rotation=(0, 0, _m.atan2(y1 - y0, x1 - x0)))
    o = bpy.context.object; o.scale = (L_ + 0.3, t, z1 - z0); bpy.ops.object.transform_apply(scale=True); o.name = n; o.data.materials.append(m)
    if p: o.parent = p
    return o


def tube_arc(n, rc, t, z0, z1, x, y, a0, a1, m, p=None, seg=16):     # дуга ремня вокруг ролика (полукольцо)
    import bmesh
    me = bpy.data.meshes.new(n); bm = bmesh.new(); ring = []
    for i in range(seg + 1):
        a = math.radians(a0 + (a1 - a0) * i / seg)
        for r in (rc, rc + t):
            for z in (z0, z1):
                ring.append(bm.verts.new((x + r * math.cos(a), y + r * math.sin(a), z)))
    for i in range(seg):
        q = [ring[4 * i + k] for k in range(4)]; w = [ring[4 * (i + 1) + k] for k in range(4)]
        for a_, b_ in ((0, 1), (1, 3), (3, 2), (2, 0)):
            bm.faces.new((q[a_], q[b_], w[b_], w[a_]))
    bm.to_mesh(me); o = bpy.data.objects.new(n, me); sc.collection.objects.link(o); o.data.materials.append(m)
    if p: o.parent = p
    return o


W = 52.0; HW = W / 2                                   # ширина грифа (x = поперёк струн, −26..26)
STR = [-21.0 + 8.4 * k for k in range(6)]               # v8 (владелец): шаг струн 8.4, размах 42 (как у порожка классики), до края 5
S = 21.0                                                # ход центра тележки ±22 = от струны 6 до струны 1
FL = 1.0                                                # дно блока (оно же сани по грифу); 26.11 v2: каждый мм на счету
R_M, H_M, H_CAP = 11.0, 13.0, 7.5                       # GB1806: Ø22 × 13 + стакан AS5600 7.5 (стакан ВНИЗ — провода сразу у дна)
Z_RF = FL + H_CAP + H_M                                 # торец ротора (вверху): 22.0
R_ID = 2.0                                              # ролики Ø4 (концевые и ведущий)
# v10 (владелец): ремень снова один — зубья на всю высоту 2.0; концевые ролики — свободные шестерёнки (лысая полоса и проточки не нужны)
TB, H_TH = 0.6, 0.4                                     # спинка 0.6, зуб 0.4 внутрь петли
H_SM, H_TZ = 1.0, 1.0                                   # лысая полоса 1.0 + зубчатая 1.0 = ремень 2.0
HB = H_SM + H_TZ
R_DRV = 2.5                                             # ведущий ролик больше — Ø5 (зубьев больше), ремень зубьями в его пазы
YD = 0.0                                                # v9: ведущий ролик В ЦЕНТРЕ петли (между ветвями) — сначала пробуем без прижимных
# v6 (владелец): прижимные ролики СНАРУЖИ петли, по гладкой спинке — классическая «Ω»: ремень поверх них, под ведущим
R_G, XG = 1.2, 5.0                                      # Ø2.4 на ±5.0 от ведущего
Y_G = -2.5 - 0.6 / 2 - (R_G + 0.6 / 2)                  # центр прижимного: ремень по осевой проходит по его верху на уровне ветви
_r1, _r2 = R_G + 0.3, R_DRV + 0.3                       # радиусы огибания по осевой ремня (спинка 0.6)
_dx, _dy = XG, (YD) - Y_G
_d = math.hypot(_dx, _dy); _phi = math.atan2(_dy, _dx); _beta = math.acos((_r1 + _r2) / _d)
A_T = math.degrees(_phi + _beta)                        # точка схода с прижимного (от его центра), к ведущему — внутренняя касательная
WRAP = 2 * (A_T + 180 - 270) * -1 if False else 2 * (270 - (A_T + 180))   # обхват ведущего
R_END = 2.5                                             # v3: концевые ролики Ø3 — тогда бока корпуса сплошные (с Ø4 петля не влезает в 52 со стенкой)
T_FLG, R_FLG = 0.4, R_END + TB                     # ролики «цилиндр с юбкой» (идея владельца): юбка снизу держит ремень, палуба не нужна
Z_FLG0 = Z_RF + 0.2; Z_B0 = Z_FLG0 + T_FLG; Z_B1 = Z_B0 + HB; Z_BM = Z_B0 + H_SM   # юбка роликов над ротором (зазор 0.2), на ней ремень
WALL = 0.8                                              # бока корпуса 0.8 — внутри габарита 52
X_ID = HW - WALL - 0.1 - R_FLG                           # оси концевых роликов ±22.7: петля ремня вровень с краем (в стенке щёлочка), внутри 52
CART_W, CART_L, T_CART = 7.5, 10.0, 1.2                 # тележка 8.0 (ровно в отступ 4 мм у крайних струн) × 10, толщина площадки
T_COV = 0.8; Z_COV0 = Z_B1 + 0.2; Z_COV1 = Z_COV0 + T_COV   # крышка корпуса над ремнями (прорези — направляющие тележек)
Z_C0 = Z_COV1 + 0.2; Z_C1 = Z_C0 + T_CART               # площадка над крышкой
LANE = 11.25                                            # v9: без провала «Ω» шаг лент снова 11.25
XM = [13.0, -13.0, 13.0, -13.0]                         # моторы в шахматку: соседние ленты — на разных краях
COLS = [(0.95, 0.85, 0.15, 1), (0.2, 0.3, 0.9, 1), (0.85, 0.15, 0.15, 1), (0.1, 0.75, 0.8, 1)]
M_MOT, M_CAP, M_ID, M_FR, M_RAIL, M_STR = mat("мотор", (0.08, 0.08, 0.09, 1)), mat("стакан", (0.18, 0.18, 0.2, 1)), mat("ролик", (0.8, 0.8, 0.82, 1)), mat("корпус", (0.65, 0.65, 0.67, 1)), mat("полоз-балка", (0.45, 0.45, 0.5, 1)), mat("струна", (0.85, 0.75, 0.4, 1))

y_last = LANE * 3
FR = bpy.data.objects.new("корпус блока", None); sc.collection.objects.link(FR)
Y0B, Y1B = -R_M - 0.3 - WALL + YD, y_last + R_M + 0.3 + WALL + YD     # блок по крайним моторам (они сдвинуты на YD)
box("дно блока", -HW, HW, Y0B, Y1B, 0, FL, M_FR, FR)
box("плита грифа 2 мм (по ней едет блок)", -HW, HW, Y0B - 25, Y1B + 25, -2.0, -0.05, mat("гриф", (0.8, 0.65, 0.45, 1)), FR)
M_COV = mat("крышка", (0.75, 0.75, 0.78, 1))
for sx in (-1, 1):                                        # бок: низ и верх сплошные, на уровне ремней — щёлочки под петли, между ними стойки
    xs = sorted((sx * (HW - WALL), sx * HW))
    box("бок корпуса сплошной 0.8", *xs, Y0B, Y1B, FL - 0.01, Z_COV1, M_COV, FR)
for yy in (Y0B, Y1B - WALL):
    box("торец корпуса", -HW, HW, yy, yy + WALL, FL - 0.01, Z_COV1, M_COV, FR)
YSL = R_FLG + 0.1 + 0.6                         # центр прорези от оси ленты (над зажимом, у верхней ветви)
cov_y = [Y0B] + sum([[LANE * i + YSL - 0.8, LANE * i + YSL + 0.8] for i in range(4)], []) + [Y1B]
for j in range(0, len(cov_y), 2):                         # крышка — полосы между прорезями шириной 1.6
    box("крышка (полоса между прорезями)", -HW, HW, cov_y[j], cov_y[j + 1], Z_COV0, Z_COV1, M_COV, FR)
for k in range(6):                                      # струны нарисованы над блоком для ориентира
    box("струна %d" % (6 - k), STR[k] - 0.25, STR[k] + 0.25, -LANE / 2 - 4, y_last + LANE / 2 + 4, Z_C1 + 3, Z_C1 + 3.5, M_STR, FR)
for i in range(4):
    yc = LANE * i; mb = mat("ремень %d" % (i + 1), COLS[i])
    L = bpy.data.objects.new("лента %d (палец %d)" % (i + 1, i + 1), None); sc.collection.objects.link(L)
    # мотор стоя: стакан внизу, ротор вверху, на торце ведущий ролик Ø4 (зубчатый)
    yd = yc + YD                                          # v4: ведущий ролик (и ось мотора) сдвинут за нижнюю ветвь — ремень обнимает его буквой «Ω»
    cyl("стакан AS5600 (провода у дна)", R_M, FL, FL + H_CAP, XM[i], yd, M_CAP, L)
    cyl("мотор GB1806 (ротор вверху)", R_M, FL + H_CAP, Z_RF, XM[i], yd, M_MOT, L)
    drv = cyl("ведущий ролик Ø5: шестерня на всю высоту ремня", R_DRV - H_TH / 2, Z_B0 - 0.01, Z_B1 + 0.1, XM[i], yd, M_ID, L, 24)
    for o_ in (cyl("ведущий: ступица", R_DRV - H_TH - 0.2, Z_B0 - 0.01, Z_B0 + 0.01, XM[i], yd, M_ID, L, 32),
               cyl("юбка ведущего ролика", R_DRV + TB, Z_RF, Z_B0, XM[i], yd, M_ID, L, 32)):
        o_.parent = drv; o_.matrix_parent_inverse = drv.matrix_world.inverted()
    for sx in (-1, 1):
        cyl("концевой ролик Ø5: свободная шестерёнка (ось из крышки)", R_END - H_TH / 2, Z_FLG0, Z_B1 + 0.1, sx * X_ID, yc, M_ID, L, 24)
        cyl("концевой: ось", 0.75, Z_B1 + 0.09, Z_COV0 + 0.01, sx * X_ID, yc, M_ID, L, 24)
        cyl("юбка концевого ролика", R_FLG, Z_FLG0, Z_B0, sx * X_ID, yc, M_ID, L, 32)
        tube_arc("ремень вокруг ролика (спинка)", R_END, TB, Z_B0, Z_B1, sx * X_ID, yc, -90 if sx > 0 else 90, 90 if sx > 0 else 270, mb, L)
    # две ветви ремня: верхняя (к ней пристёгнута тележка) и нижняя; зубья — только в верхней полосе, внутрь петли
    box("верхняя ветвь (спинка; к ней тележка — идёт ровно)", -X_ID, X_ID, yc + R_END, yc + R_END + TB, Z_B0, Z_B1, mb, L)
    xt = -X_ID + 1.0
    while xt < X_ID - 1.0:
        box("зуб", xt - 0.5, xt + 0.5, yc + R_END - H_TH, yc + R_END + 0.01, Z_B0, Z_B1, mb, L); xt += 2.0
    yb = yc - R_END - TB / 2                              # осевая линия нижней ветви
    rc = _r2                                              # огибание ведущего по осевой ремня
    for x0, x1 in ((-X_ID, X_ID),):                       # зубья по всей нижней ветви
        xt = x0 + 1.0
        while xt < x1 - 1.0:
            box("зуб", xt - 0.5, xt + 0.5, yc - R_END - 0.01, yc - R_END + H_TH, Z_B0, Z_B1, mb, L); xt += 2.0
    box("нижняя ветвь (прямая, ведущий цепляет её зубья)", -X_ID, X_ID, yc - R_END - TB, yc - R_END, Z_B0, Z_B1, mb, L)
    # балка-полоз вдоль ленты (связана с корпусом и мотором — по ней передаётся вибрация) — сбоку от нижней ветви
    # тележка: площадка 8.5 × 10 + зажим на верхнюю ветвь + лыжа по балке
    C = bpy.data.objects.new("тележка %d" % (i + 1), None); sc.collection.objects.link(C); C.parent = L
    box("площадка пальца 8×10", -CART_W / 2, CART_W / 2, yc - CART_L / 2, yc + CART_L / 2, Z_C0, Z_C1, mb, C)
    box("зажим на верхнюю ветвь (1.2 мм)", -0.6, 0.6, yc + R_END + TB + 0.1, yc + YSL + 0.6, Z_B0 + 0.3, Z_B1, mb, C)
    box("пластинка в прорези (ведёт тележку)", -3.0, 3.0, yc + YSL - 0.6, yc + YSL + 0.6, Z_B1 - 0.5, Z_C0 + 0.01, mb, C)
    for f in range(1, 241, 3):
        s = S * math.sin(2 * math.pi * ((f - 1) / 120 + 0.27 * i))
        C.location.x = s; C.keyframe_insert("location", index=0, frame=f)
        drv.rotation_euler.z = s / R_DRV; drv.keyframe_insert("rotation_euler", index=2, frame=f)
sc.frame_start, sc.frame_end = 1, 240; sc.frame_set(1)
for scr in bpy.data.screens:
    for ar in scr.areas:
        for sp in ar.spaces:
            if sp.type == 'VIEW_3D':
                sp.shading.type = 'SOLID'; sp.shading.color_type = 'MATERIAL'; sp.clip_start = 0.5; sp.clip_end = 3000
                r3 = sp.region_3d; r3.view_location = (0, y_last / 2, 12); r3.view_distance = 170; r3.view_rotation = (0.80, 0.50, 0.15, 0.28)
print("РЕМНИ v10 (зубья на всю высоту, концевые — свободные шестерёнки, ведущий в центре): ВСЕГО с грифом %.1f мм; " % (Z_C1 + 2.0) + " блок %.0f × %.1f мм (поперёк × вдоль), верх площадок %.1f мм, шаг лент %.2f, ход ±%.1f, тележка в крайних до x=±%.2f (край грифа ±%.0f); ось концевого ролика ±%.2f, зажим доходит до ±%.2f" % (W, y_last + LANE + 3, Z_C1, LANE, S, S + CART_W / 2, HW, X_ID, S + 0.6))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "remni4_v10.blend")); print("saved")
