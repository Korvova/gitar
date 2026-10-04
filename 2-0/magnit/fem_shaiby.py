# -*- coding: utf-8 -*-
r"""Насколько стальные шайбы между группами магнитов усиливают поле в зоне бегущей катушки (04.10).
2D-сечение вдоль стержня (плоская модель — для ОТНОШЕНИЯ «с шайбами / без»): магниты 15 (высота сечения)
× 15 (полюс, 3 диска 15×5), намагничены вдоль стержня навстречу; шайбы сталь μ 1000, 1.5 мм; катушка — полоса
r 8.25…12.25. Сила бегунка ∝ среднеквадратичному радиальному полю в полосе катушки.
Запуск на сервере: python fem_shaiby.py"""
import numpy as np
from skfem import MeshTri, Basis, ElementTriP1, ElementTriP0, BilinearForm, LinearForm, asm, condense, solve
from skfem.helpers import dot, grad

MU0, BR, H, POLE = 4e-7 * np.pi, 1.43, 15.0, 15.0
xs = np.arange(-70, 70.01, 0.25)
ys = np.unique(np.concatenate([np.linspace(-40, -14, 20), np.arange(-14, 14.01, 0.1), np.linspace(14, 40, 20)]))
mesh = MeshTri.init_tensor(xs, ys)
basis, b0 = Basis(mesh, ElementTriP1()), Basis(mesh, ElementTriP0())
cx, cy = mesh.p[:, mesh.t].mean(axis=1)
D = mesh.boundary_nodes()


@BilinearForm
def a(u, v, w):
    return w["nu"] * dot(grad(u), grad(v))


@LinearForm
def l(v, w):
    return w["J"] * v


def field(sp):
    J = np.zeros_like(cx); iron = np.zeros_like(cx, bool)
    M = BR / MU0; band = 0.1
    pitch = POLE + sp
    for i in range(-3, 3):
        x0 = (i + 0.5) * pitch - POLE / 2
        s = 1 if i % 2 == 0 else -1
        top = (cx > x0) & (cx < x0 + POLE) & (cy > H / 2 - band) & (cy < H / 2)
        bot = (cx > x0) & (cx < x0 + POLE) & (cy > -H / 2) & (cy < -H / 2 + band)
        J[top] += s * M / (band * 1e-3); J[bot] -= s * M / (band * 1e-3)
        if sp > 0:
            iron |= (cx > x0 + POLE) & (cx < x0 + POLE + sp) & (np.abs(cy) < H / 2)
    nu = np.where(iron, 1 / (MU0 * 1000), 1 / MU0)
    K = asm(a, basis, nu=b0.interpolate(nu))
    f = asm(l, basis, J=b0.interpolate(J)) * 1e-6
    A = solve(*condense(K, f, D=D))
    g = basis.interpolate(A).grad                     # dA/dx, dA/dy в точках квадратуры (мм⁻¹)
    By = -g[0].mean(axis=1) * 1e3                     # Тл
    coil = (cy > 8.25) & (cy < 12.25) & (np.abs(cx) < 2 * pitch)
    return np.sqrt((By[coil] ** 2).mean())


b0_ = field(0.0)
for sp in (1.0, 1.5, 2.0):
    b = field(sp)
    print(f"шайба {sp} мм: поле в катушке ×{b / b0_:.2f} (без шайб {b0_:.3f} Тл, с шайбами {b:.3f} Тл) → сила при том же токе ×{b / b0_:.2f}, ватты на ту же силу ×{(b0_ / b) ** 2:.2f}")
