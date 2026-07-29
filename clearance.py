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
        T = trimesh.transformations.euler_matrix(
            math.pi if flip else 0.0, 0.0, math.radians(rz))
        T[:3, 3] = loc
        m.apply_transform(T)
        self.meshes[name] = m
        return m

    def _dist(self, a, b):
        """Мин. зазор между мешами; при контакте/пересечении -> объём
        пересечения (мм³) булевой операцией (manifold) как мера беды."""
        cm = trimesh.collision.CollisionManager()
        cm.add_object(a, self.meshes[a])
        if not cm.in_collision_single(self.meshes[b]):
            return cm.min_distance_single(self.meshes[b]), 0.0
        inter = trimesh.boolean.intersection(
            [self.meshes[a], self.meshes[b]], engine='manifold')
        vol = float(inter.volume) if inter is not None and not inter.is_empty else 0.0
        return 0.0, vol

    def check(self, clearances=(), touching=(), verbose=True):
        ok = True
        for a, b, need in clearances:
            d, vol = self._dist(a, b)
            good = vol < 0.01 and d >= need - 1e-6
            ok &= good
            if verbose or not good:
                print(f"  {'OK ' if good else 'FAIL'} зазор {a} <-> {b}: "
                      f"{d:.3f} мм (нужно >= {need}, пересечение {vol:.2f} мм3)")
        for a, b in touching:
            d, vol = self._dist(a, b)
            good = vol < 1.0            # посадка: касание да, объёмного нет
            ok &= good
            if verbose or not good:
                print(f"  {'OK ' if good else 'FAIL'} посадка {a} <-> {b}: "
                      f"зазор {d:.3f} мм, пересечение {vol:.2f} мм3 (< 1)")
        if not ok:
            print("!! ГЕОМЕТРИЯ НАРУШЕНА — детали не выпускать")
            sys.exit(1)
        print("clearance: сборка чистая")
        return True
