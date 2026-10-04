# -*- coding: utf-8 -*-
r"""Шайбы между группами дисков 15×5 — ОСЕСИММЕТРИЧНЫЙ МКЭ с насыщением стали (04.10).
Владелец: есть шайбы Ø9 / дырка Ø5 / 0.7 мм — можно ставить по 1–3 в стык. Сравниваем с квадратом 15×15×1.5
из листа (в осесимметрии — диск Ø15). ψ = r·Aφ; -∇·(ν/r ∇ψ) = Jφ; магниты — поверхностный ток на r = 7.5.
Сталь — кривая Фрёлиха (μr нач. 1000, насыщение 2.0 Тл), итерации по ν.
Мера силы бегунка — среднеквадратичное Br в зоне катушки r 8.25…12.25. Запуск на сервере: python fem_shaiby_osesim.py"""
import numpy as np
from skfem import MeshTri, Basis, ElementTriP1, ElementTriP0, BilinearForm, LinearForm, asm, condense, solve
from skfem.helpers import dot, grad

MU0, BR, R, POLE = 4e-7 * np.pi, 1.43, 7.5, 15.0
JS, A_F = 2.0, 2.0 / (4e-7 * np.pi * 999)                  # насыщение 2 Тл, μr нач. 1000
rs = np.unique(np.concatenate([np.arange(0.05, 13.0, 0.1), np.linspace(13.0, 45, 25)]))
rs = np.concatenate([[0.0], rs])
zs = np.unique(np.concatenate([np.linspace(-110, -55, 25), np.arange(-55, 55.01, 0.1), np.linspace(55, 110, 25)]))
mesh = MeshTri.init_tensor(rs, zs)
basis, b0 = Basis(mesh, ElementTriP1()), Basis(mesh, ElementTriP0())
cr, cz = mesh.p[:, mesh.t].mean(axis=1)
D = mesh.boundary_nodes()


@BilinearForm
def a(u, v, w):
    return w["nu"] / w.x[0] * dot(grad(u), grad(v))


@LinearForm
def l(v, w):
    return w["J"] * v


def nu_steel(B):
    B = np.maximum(B, 1e-6)
    p = B - MU0 * A_F - JS
    H = (p + np.sqrt(p * p + 4 * MU0 * B * A_F)) / (2 * MU0)
    return H / B


def run(t, d_out, d_in, n_poles=6):
    """t — толщина стали между группами (0 — без), d_out/d_in — наружный диаметр и дырка шайбы."""
    pitch = POLE + t
    J = np.zeros_like(cr); steel = np.zeros_like(cr, bool)
    M, band = BR / MU0, 0.1
    for i in range(n_poles):
        z0 = (i - n_poles / 2) * pitch + t / 2
        s = 1 if i % 2 == 0 else -1
        J[(cz > z0) & (cz < z0 + POLE) & (cr > R - band) & (cr < R)] = s * M / (band * 1e-3)
        if t > 0 and i < n_poles - 1:
            zt = z0 + POLE
            steel |= (cz > zt) & (cz < zt + t) & (cr > d_in / 2) & (cr < d_out / 2)
    nu = np.full_like(cr, 1 / MU0)
    for it in range(60):
        A = solve(*condense(asm(a, basis, nu=b0.interpolate(nu)), asm(l, basis, J=b0.interpolate(J)) * 1e-6, D=D))
        g = basis.interpolate(A).grad
        rq = basis.mapping.F(basis.X)[0]                   # r в точках квадратуры
        Br = (-g[1] / rq).mean(axis=1) * 1e3
        Bz = (g[0] / rq).mean(axis=1) * 1e3
        if not steel.any():
            break
        Bm = np.hypot(Br, Bz)
        new = np.where(steel, nu_steel(Bm), 1 / MU0)
        if np.max(np.abs(new - nu)[steel] / nu[steel]) < 1e-3:
            break
        nu = np.where(steel, 0.5 * nu + 0.5 * new, nu)
    coil = (cr > 8.25) & (cr < 12.25) & (np.abs(cz) < 2 * pitch)
    bst = np.hypot(Br, Bz)[steel].max() if steel.any() else 0
    return np.sqrt((Br[coil] ** 2).mean()), bst


ref, _ = run(0, 0, 0)
print(f"без стали: Br в катушке {ref:.3f} Тл")
for t, do, di, tag in ((1.5, 15, 0, "квадрат из листа 1.5 (≈диск Ø15)"),
                       (0.7, 9, 5, "1 шайба Ø9/5 × 0.7"),
                       (1.4, 9, 5, "2 шайбы Ø9/5 = 1.4"),
                       (2.1, 9, 5, "3 шайбы Ø9/5 = 2.1"),
                       (1.4, 0.001, 0, "просто зазор 1.4 без стали")):
    b, bs = run(t, do, di)
    print(f"  {tag}: сила ×{b / ref:.2f} (сталь до {bs:.1f} Тл)")
