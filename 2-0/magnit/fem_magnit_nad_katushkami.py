# -*- coding: utf-8 -*-
r"""Идея владельца 03.10: на тележке неодимовый магнит, внизу ряд самодельных электромагнитов
(стальной сердечник + намотка проводом 0.3) — по одному под каждой струной, шаг 8.8.
2D-расчёт методом конечных элементов (A_z), железо линейное μr 1000, магнит — эквивалентные токи
по боковым граням (M = Br/μ0). Сила на тележку — виртуальной работой по коэнергии ½∫J·A.

Геометрия (мм; x — поперёк грифа, y — вверх; глубина вдоль грифа DEPTH):
  сердечник — стальная планка 3 × 10 (высота) × DEPTH, катушка вокруг: окно 2.5 с каждой стороны;
  тележка — магнит MW × MH, намагничен вверх (или поперёк — варианты), снизу над сердечниками GAP;
  можно стальную пластину на тележке сверху магнита (замыкает поле).
Считает:
  1) «липкость» без тока: сила вбок и вниз по положению тележки между двумя сердечниками;
  2) перескок на соседнюю струну: текущая катушка отталкивает (−NI), соседняя тянет (+NI) —
     сила вбок по всему пути 0 → 8.8 должна быть в сторону соседней, иначе тележка застрянет.
Запуск на сервере: python fem_magnit_nad_katushkami.py
"""
import sys
import numpy as np
from multiprocessing import Pool
from skfem import MeshTri, Basis, ElementTriP1, ElementTriP0, BilinearForm, LinearForm, asm, condense, solve
from skfem.helpers import dot, grad

MU0 = 4e-7 * np.pi
MUR_IRON = 1000.0
PITCH = 8.8                    # шаг струн
CORE_W, CORE_H = 3.0, 10.0     # сердечник
WIN = 2.5                      # окно катушки с каждой стороны
DEPTH = 10.0                   # вдоль грифа: сердечник 3 × 10, магниты — 2–3 столбика дисков рядом
BR = 1.2                       # диски 4 × 2 (N35)
WIRE_N = 110                   # витков: окно 2.5 × 8 мм, заполнение 0.5, провод 0.3

xs = np.arange(-30, 30 + 1e-9, 0.1)
ys = np.unique(np.concatenate([np.linspace(-25, -0.5, 50), np.arange(-0.5, 9.0 + 1e-9, 0.05), np.linspace(9.0, 35, 40)]))
mesh = MeshTri.init_tensor(xs, ys)
basis = Basis(mesh, ElementTriP1())
b0 = Basis(mesh, ElementTriP0())
cx, cy = mesh.p[:, mesh.t].mean(axis=1)
D = mesh.boundary_nodes()
_u = mesh.p[:, mesh.t[1]] - mesh.p[:, mesh.t[0]]; _v = mesh.p[:, mesh.t[2]] - mesh.p[:, mesh.t[0]]
area_el = np.abs(_u[0] * _v[1] - _u[1] * _v[0]) / 2

coil_x = np.array([-2, -1, 0, 1, 2]) * PITCH
core = np.zeros_like(cx, bool)
for c in coil_x:
    core |= (np.abs(cx - c) < CORE_W / 2) & (cy > -CORE_H) & (cy < 0)
core |= (np.abs(cx) < 2.5 * PITCH) & (cy > -CORE_H - 1.5) & (cy < -CORE_H)   # общая стальная полоса снизу


def stator_J(ni):
    J = np.zeros_like(cx)
    jv = 1.0 / (WIN * (CORE_H - 2) * 1e-6)                          # А/м² на 1 ампер-виток
    for c, a in zip(coil_x, ni):
        if a == 0:
            continue
        L = (cx > c - CORE_W / 2 - WIN) & (cx < c - CORE_W / 2) & (cy > -CORE_H + 1) & (cy < -1)
        R = (cx > c + CORE_W / 2) & (cx < c + CORE_W / 2 + WIN) & (cy > -CORE_H + 1) & (cy < -1)
        J[L] += a * jv; J[R] -= a * jv
    return J


def cart(X, gap, mw, mh, back):
    """Магнит намагничен вверх: эквивалентные токи на боковых гранях (полосы 0.1 мм)."""
    J = np.zeros_like(cx); iron = np.zeros_like(cx, bool)
    M = BR / MU0
    band = 0.1
    inside_y = (cy > gap) & (cy < gap + mh)
    L = inside_y & (cx > X - mw / 2) & (cx < X - mw / 2 + band)
    R = inside_y & (cx > X + mw / 2 - band) & (cx < X + mw / 2)
    J[L] -= M / (band * 1e-3); J[R] += M / (band * 1e-3)            # знак проверяется по притяжению к железу
    if back:
        iron |= (np.abs(cx - X) < mw / 2 + 1) & (cy > gap + mh) & (cy < gap + mh + 1.2)
    return J, iron


@BilinearForm
def a_form(u, v, w):
    return w["nu"] * dot(grad(u), grad(v))


@LinearForm
def l_form(v, w):
    return w["J"] * v


def coenergy(X, gap, ni, mw, mh, back):
    Jc, ironc = cart(X, gap, mw, mh, back)
    J = stator_J(ni) + Jc
    iron = core | ironc
    nu = np.where(iron, 1 / (MU0 * MUR_IRON), 1 / MU0)
    K = asm(a_form, basis, nu=b0.interpolate(nu))
    f = asm(l_form, basis, J=b0.interpolate(J)) * 1e-6               # сетка в мм: ∫J·v dS — площадь в м²
    A = solve(*condense(K, f, D=D))
    Ae = A[mesh.t].mean(axis=0)
    return 0.5 * np.sum(J * Ae * area_el) * 1e-6 * DEPTH * 1e-3     # Дж


def force(args):
    X, gap, ni, mw, mh, back = args
    h = 0.1
    fx = (coenergy(X + h, gap, ni, mw, mh, back) - coenergy(X - h, gap, ni, mw, mh, back)) / (2 * h * 1e-3)
    fy = (coenergy(X, gap + h / 2, ni, mw, mh, back) - coenergy(X, gap - h / 2, ni, mw, mh, back)) / (h * 1e-3)
    return fx, fy


if __name__ == "__main__":
    gap = float(sys.argv[1]) if len(sys.argv) > 1 else 2.0
    I = float(sys.argv[2]) if len(sys.argv) > 2 else 1.5
    NI = WIRE_N * I
    pos = np.linspace(0, PITCH, 12)
    with Pool(8) as pool:
        for mw, mh, back, tag in ((4.0, 4.0, False, "магнит 4 × 4 (2 диска), без стали"),
                                  (4.0, 4.0, True, "магнит 4 × 4 + сталь сверху"),
                                  (8.0, 4.0, True, "магнит 8 × 4 (плитка 2 × 2 дисков) + сталь сверху")):
            idle = pool.map(force, [(x, gap, [0, 0, 0, 0, 0], mw, mh, back) for x in pos])
            j1 = pool.map(force, [(x, gap, [0, 0, -NI, NI, 0], mw, mh, back) for x in pos])
            j2 = pool.map(force, [(x, gap, [0, 0, NI, -NI, 0], mw, mh, back) for x in pos])
            jump = j1 if min(f[0] for f in j1) > min(f[0] for f in j2) else j2   # полярность катушек выбирается прошивкой
            print(f"\n=== {tag}; зазор {gap} мм, глубина {DEPTH} мм, катушка {WIRE_N} витков × {I} А = {NI:.0f} А·в ===")
            print(" x от струны |  без тока: вбок, вниз (г) | перескок на соседнюю: вбок (г)")
            for x, (fx0, fy0), (fx1, fy1) in zip(pos, idle, jump):
                print(f"   {x:5.2f}     |   {fx0 * 102:+7.0f}  {-fy0 * 102:+7.0f}       |   {fx1 * 102:+7.0f}")
            fmin = min(f[0] for f in jump)
            fr = 0.3 * max(-f[1] for f in idle)                                # трение скольжения PETG μ 0.3 от прижима вниз
            print(f" наименьшая сила к соседней струне на пути: {fmin * 102:+.0f} г; трение при скольжении ~{fr * 102:.0f} г "
                  f"-> {'перескочит' if fmin > fr else ('перескочит только на колёсиках' if fmin > 0 else 'ЗАСТРЯНЕТ')}")
