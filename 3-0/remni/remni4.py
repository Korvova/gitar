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
STR = [-22.0 + 8.8 * k for k in range(6)]               # центры струн: 4 мм от краёв, шаг 8.8
S = 22.0                                                # ход центра тележки ±22 = от струны 6 до струны 1
FL = 1.5                                                # дно блока
R_M, H_M, H_CAP = 11.0, 13.0, 7.5                       # GB1806: Ø22 × 13 + стакан AS5600 7.5 (стакан ВНИЗ — провода сразу у дна)
Z_RF = FL + H_CAP + H_M                                 # торец ротора (вверху): 22.0
R_ID = 2.0                                              # ролики Ø4 (концевые и ведущий)
TB, HB = 1.2, 2.5                                       # ремень: толщина с зубом 1.2, ширина (по высоте) 2.5
Z_B0 = Z_RF + 0.4; Z_B1 = Z_B0 + HB                     # плоскость ремней 22.4..24.9
X_ID = HW - R_ID                                        # оси концевых роликов ±24 → ролик целиком внутри 52
CART_W, CART_L, T_CART = 8.0, 10.0, 1.6                 # тележка 8.0 (ровно в отступ 4 мм у крайних струн) × 10, толщина площадки
Z_C0 = Z_B1 + 0.3; Z_C1 = Z_C0 + T_CART                 # площадка над ремнями: верх ≈ 26.8
LANE = 11.25                                            # шаг ремней вдоль грифа: моторы Ø22 через одну ленту на 22.5 (шахматка)
XM = [13.0, -13.0, 13.0, -13.0]                         # моторы в шахматку: соседние ленты — на разных краях
COLS = [(0.95, 0.85, 0.15, 1), (0.2, 0.3, 0.9, 1), (0.85, 0.15, 0.15, 1), (0.1, 0.75, 0.8, 1)]
M_MOT, M_CAP, M_ID, M_FR, M_RAIL, M_STR = mat("мотор", (0.08, 0.08, 0.09, 1)), mat("стакан", (0.18, 0.18, 0.2, 1)), mat("ролик", (0.8, 0.8, 0.82, 1)), mat("корпус", (0.65, 0.65, 0.67, 1)), mat("полоз-балка", (0.45, 0.45, 0.5, 1)), mat("струна", (0.85, 0.75, 0.4, 1))

y_last = LANE * 3
FR = bpy.data.objects.new("корпус блока", None); sc.collection.objects.link(FR)
box("дно блока", -HW, HW, -LANE / 2 - 1.5, y_last + LANE / 2 + 1.5, 0, FL, M_FR, FR)
for k in range(6):                                      # струны нарисованы над блоком для ориентира
    box("струна %d" % (6 - k), STR[k] - 0.25, STR[k] + 0.25, -LANE / 2 - 4, y_last + LANE / 2 + 4, Z_C1 + 3, Z_C1 + 3.5, M_STR, FR)
for i in range(4):
    yc = LANE * i; mb = mat("ремень %d" % (i + 1), COLS[i])
    L = bpy.data.objects.new("лента %d (палец %d)" % (i + 1, i + 1), None); sc.collection.objects.link(L)
    # мотор стоя: стакан внизу, ротор вверху, на торце ведущий ролик Ø4 (зубчатый)
    cyl("стакан AS5600 (провода у дна)", R_M, FL, FL + H_CAP, XM[i], yc, M_CAP, L)
    cyl("мотор GB1806 (ротор вверху)", R_M, FL + H_CAP, Z_RF, XM[i], yc, M_MOT, L)
    drv = cyl("ведущий ролик Ø4 на роторе", R_ID, Z_RF, Z_B1 + 0.2, XM[i], yc, M_ID, L, 24)
    for sx in (-1, 1):
        cyl("концевой ролик Ø4", R_ID, Z_B0 - 0.2, Z_B1 + 0.2, sx * X_ID, yc, M_ID, L, 24)
        tube_arc("ремень вокруг ролика", R_ID, TB, Z_B0, Z_B1, sx * X_ID, yc, -90 if sx > 0 else 90, 90 if sx > 0 else 270, mb, L)
    # две ветви ремня: верхняя (к ней пристёгнута тележка) и нижняя
    for sy in (-1, 1):
        box("ветвь ремня", -X_ID, X_ID, *sorted((yc + sy * R_ID, yc + sy * (R_ID + TB))), Z_B0, Z_B1, mb, L)
    # балка-полоз вдоль ленты (связана с корпусом и мотором — по ней передаётся вибрация) — сбоку от нижней ветви
    box("балка-полоз (вибрация от мотора)", -HW, HW, yc - R_ID - TB - 2.2, yc - R_ID - TB - 0.6, Z_B0, Z_B1, M_RAIL, L)
    # тележка: площадка 8.5 × 10 + зажим на верхнюю ветвь + лыжа по балке
    C = bpy.data.objects.new("тележка %d" % (i + 1), None); sc.collection.objects.link(C); C.parent = L
    box("площадка пальца 8×10", -CART_W / 2, CART_W / 2, yc - CART_L / 2, yc + CART_L / 2, Z_C0, Z_C1, mb, C)
    box("зажим на ремень", -1.5, 1.5, yc + R_ID + TB + 0.1, yc + R_ID + TB + 0.9, Z_B0, Z_C0 + 0.01, mb, C)
    box("лыжа по балке", -CART_W / 2, CART_W / 2, yc - R_ID - TB - 2.3, yc - R_ID - TB - 0.5, Z_B1 + 0.01, Z_C0 + 0.01, mb, C)
    for f in range(1, 241, 3):
        s = S * math.sin(2 * math.pi * ((f - 1) / 120 + 0.27 * i))
        C.location.x = s; C.keyframe_insert("location", index=0, frame=f)
        drv.rotation_euler.z = s / R_ID; drv.keyframe_insert("rotation_euler", index=2, frame=f)
sc.frame_start, sc.frame_end = 1, 240; sc.frame_set(1)
for scr in bpy.data.screens:
    for ar in scr.areas:
        for sp in ar.spaces:
            if sp.type == 'VIEW_3D':
                sp.shading.type = 'SOLID'; sp.shading.color_type = 'MATERIAL'; sp.clip_start = 0.5; sp.clip_end = 3000
                r3 = sp.region_3d; r3.view_location = (0, y_last / 2, 12); r3.view_distance = 170; r3.view_rotation = (0.80, 0.50, 0.15, 0.28)
print("РЕМНИ ×4: блок %.0f × %.1f мм (поперёк × вдоль), верх площадок %.1f мм, шаг лент %.2f, ход ±%.0f, тележка в крайних до x=±%.2f (край грифа ±%.0f)" % (W, y_last + LANE + 3, Z_C1, LANE, S, S + CART_W / 2, HW))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "remni4.blend")); print("saved")
