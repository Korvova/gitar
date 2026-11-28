# Показ (28.11, владелец): ведущая шестерня Ø10 вместо Ø5 — ремень обнимает её на конце петли (~180°, ~6 зубьев в зацеплении),
# моторы GB1806 под ведущими шестернями в шахматку (соседние ленты — на разных концах), второй конец — свободный ролик Ø5.
# Гриф 53, струны 8.4, ленты шагом 11.25, ремень 2 мм под сопло 0.4 (спинка 0.9). Запуск: blender -b -P remni4_d10.py
import bpy, math, os
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.unit_settings.scale_length = 0.001; sc.unit_settings.length_unit = 'MILLIMETERS'
HERE = os.path.dirname(os.path.abspath(__file__))
W = 53.0; HW = W / 2; WALL = 0.8
STR = [-21.0 + 8.4 * k for k in range(6)]
LANE = 11.25
TB, HB = 0.9, 2.0                                     # спинка, ширина ремня
P = 2.659
R_I = 2.54                                            # свободный ролик Ø5 (6 зубьев)
R_D = 12 * P / (2 * math.pi)                          # ведущая Ø10.16 — 12 зубьев того же шага
X_I = 22.0                                            # свободный ролик на ±22, как было
X_D = float(os.environ.get("X_D", "20.2"))            # ведущая: толкающее ушко-пила при тележке на 1-й/6-й струне ещё на прямом
R_M, H_MOT = 11.0, 20.5                               # GB1806 со стаканом
FL = 1.0; Z_RF = FL + H_MOT; Z_D0 = Z_RF + 0.2; Z_D1 = Z_D0 + 1.0; Z_B0 = Z_D1 + 0.3; Z_B1 = Z_B0 + HB
COLS = [(0.95, 0.85, 0.15, 1), (0.2, 0.3, 0.9, 1), (0.85, 0.15, 0.15, 1), (0.1, 0.75, 0.8, 1)]


def mat(n, c):
    m = bpy.data.materials.new(n); m.diffuse_color = c; return m


def mesh(name, v, f, m):
    me = bpy.data.meshes.new(name); me.from_pydata(v, [], f); me.update()
    o = bpy.data.objects.new(name, me); sc.collection.objects.link(o); o.data.materials.append(m); return o


def box(n, x0, x1, y0, y1, z0, z1, m):
    v = [(x, y, z) for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)]
    return mesh(n, v, [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)], m)


def cyl(n, r, z0, z1, x, y, m, seg=48):
    v = [(x + r * math.cos(2 * math.pi * k / seg), y + r * math.sin(2 * math.pi * k / seg), z) for z in (z0, z1) for k in range(seg)]
    f = [list(range(seg))[::-1], list(range(seg, 2 * seg))] + [[k, (k + 1) % seg, seg + (k + 1) % seg, seg + k] for k in range(seg)]
    return mesh(n, v, f, m)


def loop_pts(x1, a, x2, b, yc, n=40):                 # осевая ремня вокруг двух окружностей (x1, a) и (x2, b), обход по часовой
    d = x2 - x1; nx = -(b - a) / d; ny = math.sqrt(1 - nx * nx)
    au, al = math.atan2(ny, nx), math.atan2(-ny, nx)
    pts = []
    a2 = [au + (al - au) * k / n for k in range(n + 1)] if x2 > x1 else None
    # верх: от c1 к c2; дуга вокруг c2 (через сторону от c1); низ: от c2 к c1; дуга вокруг c1
    def arc(cx, r, t0, t1):
        return [(cx + r * math.cos(t0 + (t1 - t0) * k / n), yc + r * math.sin(t0 + (t1 - t0) * k / n)) for k in range(n + 1)]
    if x2 > x1:
        pts += arc(x2, b, au, al if al < au else al - 2 * math.pi)
        pts += arc(x1, a, al, au - 2 * math.pi if au > al else au)[::1]
        pts = arc(x2, b, au, al) + arc(x1, a, al - 2 * math.pi if False else al, au - 2 * math.pi)
    return pts


def band(name, cl, m):                                # лента вдоль замкнутой осевой (x, y), толщина TB, высота HB
    n = len(cl); v = []
    for i in range(n):
        (x0, y0), (x1, y1) = cl[i - 1], cl[(i + 1) % n]
        tx, ty = x1 - x0, y1 - y0; L = math.hypot(tx, ty); nx, ny = ty / L, -tx / L    # нормаль наружу (обход по часовой)
        x, y = cl[i]
        for s in (-TB / 2, TB / 2):
            for z in (Z_B0, Z_B1):
                v.append((x + nx * s, y + ny * s, z))
    f = []
    for i in range(n):
        a = [4 * i + k for k in range(4)]; b = [4 * ((i + 1) % n) + k for k in range(4)]
        for p, q in ((0, 1), (1, 3), (3, 2), (2, 0)):
            f.append((a[p], b[p], b[q], a[q]))
    return mesh(name, v, f, m)


M_FR, M_MOT, M_ROL, M_STR = mat("корпус", (0.65, 0.65, 0.67, 1)), mat("мотор", (0.08, 0.08, 0.09, 1)), mat("ролик", (0.8, 0.8, 0.82, 1)), mat("струна", (0.85, 0.75, 0.4, 1))
y_last = 3 * LANE
Y0B, Y1B = -R_M - 0.3 - WALL, y_last + R_M + 0.3 + WALL
box("плита грифа 53", -HW, HW, Y0B - 20, Y1B + 20, -2.0, -0.05, mat("гриф", (0.8, 0.65, 0.45, 1)))
box("дно блока", -HW, HW, Y0B, Y1B, 0, FL, M_FR)
for sx in (-1, 1):
    box("бок корпуса 0.8", *sorted((sx * (HW - WALL), sx * HW)), Y0B, Y1B, FL, Z_B1 + 1.2, M_FR)
for k in range(6):
    box("струна %d" % (6 - k), STR[k] - 0.25, STR[k] + 0.25, Y0B - 10, Y1B + 10, Z_B1 + 4, Z_B1 + 4.5, M_STR)
SD = [1, -1, 1, -1]                                   # с какого конца ведущая (шахматка)
CART = [21.0, -21.0, 6.0, -10.0]                      # где стоят тележки (лента 1 и 2 — на крайних струнах)
for i in range(4):
    yc = LANE * i; s = SD[i]; mb = mat("ремень %d" % (i + 1), COLS[i])
    cyl("мотор GB1806 под ведущей", R_M, FL, Z_RF, s * X_D, yc, M_MOT)
    cyl("ведущая шестерня Ø10 (12 зубьев)", R_D, Z_B0 - 0.3, Z_B1 + 0.3, s * X_D, yc, M_ROL)
    cyl("свободный ролик Ø5", R_I, Z_B0 - 0.3, Z_B1 + 0.3, -s * X_I, yc, M_ROL)
    xa, xb = (-X_I, X_D) if s > 0 else (-X_D, X_I)
    ra, rb = (R_I, R_D) if s > 0 else (R_D, R_I)
    cl = loop_pts(xa, ra + TB / 2, xb, rb + TB / 2, yc)
    band("ремень %d" % (i + 1), cl, mb)
    # тележка 8.5 × 10 над крышкой (на высоте верхней ветви в этой точке — показать наклон ветви)
    box("тележка %d" % (i + 1), CART[i] - 4.25, CART[i] + 4.25, yc - 5, yc + 5, Z_B1 + 1.2, Z_B1 + 2.4, mb)

# цифры
nx = -(R_D - R_I) / (X_D + X_I); tilt = math.degrees(math.asin(-nx))
print("ведущая Ø%.2f на x = ±%.1f: от 1-й струны (21) до края шестерни %.1f мм; спинка ремня на ведущей до x = %.1f, стенка с %.1f (%s)" % (
    2 * R_D, X_D, X_D + R_D - 21, X_D + R_D + TB, HW - WALL, "влезает" if X_D + R_D + TB + 0.2 <= HW - WALL else "НЕ влезает на %.1f" % (X_D + R_D + TB + 0.2 - (HW - WALL))))
print("мотор Ø22 на x = ±%.1f: край мотора %.1f, край грифа %.1f — %s" % (X_D, X_D + R_M, HW, "внутри" if X_D + R_M <= HW - WALL else "торчит за гриф на %.1f мм" % (X_D + R_M - HW)))
print("верхняя ветвь идёт под углом %.1f° — на ходе 42 мм уходит вбок на %.1f мм" % (tilt, 42 * math.tan(math.radians(tilt))))
print("моторы одного конца через ленту: %.1f мм между осями (мотор 22) — зазор %.1f" % (2 * LANE, 2 * LANE - 2 * R_M))
for scr in bpy.data.screens:
    for ar in scr.areas:
        for sp in ar.spaces:
            if sp.type == 'VIEW_3D':
                sp.shading.type = 'SOLID'; sp.shading.color_type = 'MATERIAL'; sp.clip_start = 0.5; sp.clip_end = 3000
                r3 = sp.region_3d; r3.view_location = (0, y_last / 2, 12); r3.view_distance = 150; r3.view_rotation = (0.85, 0.42, 0.12, 0.28)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "remni4_d10.blend")); print("saved")
