# -*- coding: utf-8 -*-
"""Численное «зрение» для сборок: проверка пересечений и зазоров через FCL.
Использование в конце каждого генератора деталей:

    from clearance import Assembly
    asm = Assembly()
    asm.add("part_a", "path/a.stl", loc=(0,0,0), rz=0)
    asm.add("part_b", "path/b.stl", loc=(10,0,0), rz=90, flip=True)
    asm.check(
        clearances=[("part_a", "part_b", 0.2)],   # требуемый мин. зазор, мм
        touching=[("part_a", "part_c")],          # касание/посадка: пересечение
    )                                             #   до 0.05 мм допустимо

Падает с ненулевым кодом и громким отчётом, если геометрия нарушена.
"""
import math
import sys

import numpy as np
import trimesh


class Assembly:
    def __init__(self):
        self.meshes = {}

    def add(self, name, stl_path, loc=(0, 0, 0), rz=0.0, flip=False):
        m = trimesh.load(stl_path, force='mesh')
        if not m.is_volume:                      # STL после сложных булев бывает
            m.merge_vertices()                   # с микрощелями — лечим
            trimesh.repair.fill_holes(m)
            trimesh.repair.fix_normals(m)
        T = trimesh.transformations.euler_matrix(
            math.pi if flip else 0.0, 0.0, math.radians(rz))
        T[:3, 3] = loc
        m.apply_transform(T)
        self.meshes[name] = m
        return m

    def _dist(self, a, b):
        """(зазор, глубина): зазор в мм если нет контакта; при контакте —
        глубина проникновения в мм (сэмпл поверхности одной детали, signed
        distance внутрь другой; не требует идеальных мешей)."""
        cm = trimesh.collision.CollisionManager()
        cm.add_object(a, self.meshes[a])
        if not cm.in_collision_single(self.meshes[b]):
            return cm.min_distance_single(self.meshes[b]), 0.0
        for A, B in ((a, b), (b, a)):
            mB = self.meshes[B]
            if not mB.is_volume:
                continue
            pts = self.meshes[A].sample(3000)
            try:
                d = trimesh.proximity.signed_distance(mB, pts)
            except BaseException:
                continue
            return 0.0, max(float(d.max()), 0.0)
        return 0.0, 999.0     # оба меша битые — чинить исходники

    def check(self, clearances=(), touching=(), verbose=True):
        ok = True
        for a, b, need in clearances:
            d, depth = self._dist(a, b)
            good = depth <= 0.05 and d >= need - 1e-6
            ok &= good
            if verbose or not good:
                print(f"  {'OK ' if good else 'FAIL'} зазор {a} <-> {b}: "
                      f"{d:.3f} мм (нужно >= {need}, глубина {depth:.2f})")
        for a, b in touching:
            d, depth = self._dist(a, b)
            good = depth <= 0.1          # посадка: касание да, вреза нет
            ok &= good
            if verbose or not good:
                print(f"  {'OK ' if good else 'FAIL'} посадка {a} <-> {b}: "
                      f"зазор {d:.3f} мм, глубина {depth:.2f} (<= 0.1)")
        if not ok:
            print("!! ГЕОМЕТРИЯ НАРУШЕНА — детали не выпускать")
            sys.exit(1)
        print("clearance: сборка чистая")
        return True
