# -*- coding: utf-8 -*-
"""Отчёт по запечённой симуляции четырёх станций (gitara_physics4.py).
Запуск: blender -b 2-0/Гитара_физика4_<вариант>.blend -P 2-0/gitara_physics4_report.py
Читает кэш Bullet из файла — пересчёта нет."""
import bpy, math

sc = bpy.context.scene
CARTS_Y = [18, 34, 50, 66]
Z_FLOOR = [3, 8.4, 13.8, 19.2]
SETTLE, PERIOD = 40, 200
rows = []
for k in range(4):
    cart, band, arm = (bpy.data.objects[n % k] for n in ("тележка%d", "лента%d", "плечо%d"))
    X, Y, YAW, BZ, AZ = [], [], [], [], []
    for fr in range(SETTLE, sc.frame_end + 1):
        sc.frame_set(fr)
        m = cart.matrix_world
        X.append(m.translation.x); Y.append(m.translation.y - CARTS_Y[k])
        ax = m.to_3x3().col[0]
        YAW.append(abs(math.degrees(math.atan2(ax.y, ax.x))))
        BZ.append(band.matrix_world.translation.z - (Z_FLOOR[k] + 1.0))
        AZ.append(arm.matrix_world.translation.z - (Z_FLOOR[k] + 1.0))
    rows.append((k, min(X), max(X), max(X) - min(X), min(Y), max(Y), max(YAW),
                 min(BZ), max(BZ), min(AZ), max(AZ)))
print("REPORT_BEGIN")
print("ст | ход X мм (min..max = размах) | дрейф Y мм | yaw° | лента dz | плечо dz")
for r in rows:
    print("%d | %6.1f .. %5.1f = %4.1f | %5.1f .. %4.1f | %4.1f | %+.2f/%+.2f | %+.2f/%+.2f" % r)
print("REPORT_END")
for k in range(4):
    cart = bpy.data.objects["тележка%d" % k]
    line = []
    for fr in range(SETTLE, sc.frame_end + 1, 20):
        sc.frame_set(fr); m = cart.matrix_world; ax = m.to_3x3().col[0]
        line.append("%d:%.0f/%.0f/%.0f" % (fr, m.translation.x, m.translation.y - CARTS_Y[k], math.degrees(math.atan2(ax.y, ax.x))))
    print("ТРАССА ст%d (кадр:x/y/yaw): " % k + "  ".join(line))
