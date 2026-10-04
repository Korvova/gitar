# -*- coding: utf-8 -*-
r"""3D МКЭ: стержень из дисков 15×5 N52 (полюс 15 = 3 диска) + стальные шайбы в стыках + неподвижный стальной
П-жёлоб (дно и бока) или почти закрытая труба (щель 3 мм сверху) — сколько прибавляет к силе катушки Ø24 (04.10).
Полный скалярный потенциал: B = -μ(H)∇φ + Br, ∇·B = 0. Сталь — кривая Фрёлиха (μr нач. 1000, насыщение 2.0 Тл),
итерации по μ. Половина области (y ≥ 0, симметрия). Сила ∝ амплитуде первой гармоники среднего по кольцу катушки
радиального поля Br(x) (2 фазы, синус/косинус). Запуск на сервере: python fem3d_zhelob.py"""
import time
import numpy as np
import pyamg
from skfem import MeshHex, Basis, ElementHex1, ElementHex0, BilinearForm, LinearForm, asm, condense
from skfem.helpers import dot, grad

import sys
ITERS = 40 if "sloi" in sys.argv else 25
MU0, BR, R_M, POLE, NPOLE = 4e-7 * np.pi, 1.43, 7.5, 15.0, 6
JS = 2.0; A_F = JS / (MU0 * 999)
R0, R1 = 8.5, 12.0                     # обмотка катушки Ø24
G_IN, T_ST = 12.5, 1.5                 # сталь жёлоба: внутренняя грань и толщина


def axis(fine_lim, fine, far, n_far, sym=False):
    a = np.arange(0, fine_lim + 1e-9, fine)
    b = fine_lim + (far - fine_lim) * (np.linspace(0, 1, n_far + 1)[1:] ** 1.6)
    h = np.concatenate([a, b])
    return h if sym else np.concatenate([-h[:0:-1], h])


def run(wash, steel):
    """wash: None или (D, d, t) — шайба; steel: '' / 'U' / 'tube'."""
    t = wash[2] if wash else 0.0
    pitch = POLE + t
    L = NPOLE * pitch
    xs = np.unique(np.concatenate([np.arange(-L / 2, L / 2 + 1e-9, pitch / 20),
                                   [(i - NPOLE / 2) * pitch + t / 2 + POLE for i in range(NPOLE)],
                                   -L / 2 - 30 * (np.linspace(0, 1, 7)[1:] ** 1.6),
                                   L / 2 + 30 * (np.linspace(0, 1, 7)[1:] ** 1.6)]))
    ys = axis(15.0, 0.6, 45.0, 6, sym=True)
    zs = axis(15.0, 0.6, 45.0, 6)
    mesh = MeshHex.init_tensor(xs, ys, zs)
    cx, cy, cz = mesh.p[:, mesh.t].mean(axis=1)
    rr = np.hypot(cy, cz)
    bx = np.zeros_like(cx)
    mag = np.zeros_like(cx, bool); st = np.zeros_like(cx, bool)
    for i in range(NPOLE):
        x0 = (i - NPOLE / 2) * pitch + t / 2
        sel = (cx > x0) & (cx < x0 + POLE) & (rr < R_M)
        bx[sel] = BR * (1 if i % 2 == 0 else -1); mag |= sel
        if wash and i < NPOLE - 1:
            st |= (cx > x0 + POLE) & (cx < x0 + POLE + t) & (rr < wash[0] / 2) & (rr > wash[1] / 2)
    inx = np.abs(cx) < L / 2 + 3
    if steel in ("U", "tube"):
        st |= inx & (cz > -G_IN - T_ST) & (cz < -G_IN) & (cy < G_IN + T_ST)                    # дно
        st |= inx & (cy > G_IN) & (cy < G_IN + T_ST) & (cz > -G_IN - T_ST) & (cz < G_IN)          # бок
    if steel == "tube":
        st |= inx & (cz > G_IN) & (cz < G_IN + T_ST) & (cy > 1.5) & (cy < G_IN + T_ST)          # верх со щелью 3
    mu = np.where(st, MU0 * 1000, MU0 * np.where(mag, 1.05, 1.0))

    # сетка — прямоугольные кирпичики по осям: матрица элемента = μ·(dy·dz/dx·Kx + dx·dz/dy·Ky + dx·dy/dz·Kz),
    # Kx/Ky/Kz — с единичного кубика; собираем numpy-ом за секунды вместо asm на каждой итерации по μ
    pe = mesh.p[:, mesh.t]                                   # 3 × 8 × ne
    dxyz = pe.max(axis=1) - pe.min(axis=1)                   # 3 × ne
    loc = np.round((pe - pe.min(axis=1)[:, None, :]) / dxyz[:, None, :]).astype(int)
    assert (loc == loc[:, :, :1]).all(), "разная нумерация узлов в элементах"
    one = MeshHex.init_tensor(np.array([0., 1.]), np.array([0., 1.]), np.array([0., 1.]))
    lo1 = np.round(one.p[:, one.t[:, 0]]).astype(int)
    perm = [next(j for j in range(8) if (lo1[:, j] == loc[:, i, 0]).all()) for i in range(8)]
    bone = Basis(one, ElementHex1())
    Kr = []
    for d in range(3):
        Kd = asm(BilinearForm(lambda u, v, w, d=d: u.grad[d] * v.grad[d]), bone).toarray()
        Kr.append(Kd[np.ix_(one.t[perm, 0], one.t[perm, 0])])
    gx, gy, gz = dxyz
    rows = np.repeat(mesh.t, 8, axis=0).ravel(); cols = np.tile(mesh.t, (8, 1)).ravel()
    from scipy.sparse import coo_matrix
    Nn = mesh.p.shape[1]

    def stiff(mu_e):
        ke = (Kr[0].ravel()[:, None] * (gy * gz / gx) + Kr[1].ravel()[:, None] * (gx * gz / gy)
              + Kr[2].ravel()[:, None] * (gx * gy / gz)) * mu_e
        return coo_matrix((ke.ravel(), (rows, cols)), shape=(Nn, Nn)).tocsr()

    # правая часть ∫ Br·∇v: у трилинейной функции ∫∂N/∂x по кирпичику = ±dy·dz/4 (узлы на правой/левой грани)
    sx = np.where(loc[0, :, 0] == 1, 1.0, -1.0)
    f = np.zeros(Nn)
    np.add.at(f, mesh.t.ravel(), (sx[:, None] * (gy * gz / 4) * bx).ravel())

    def grad_e(u):                                       # средний градиент по кирпичику
        ue = u[mesh.t]
        return np.vstack([((ue * np.where(loc[d, :, 0] == 1, 1.0, -1.0)[:, None]).sum(axis=0) / 4) / dxyz[d]
                          for d in range(3)])
    D = mesh.boundary_nodes()
    D = D[np.abs(mesh.p[1, D]) > 1e-6]                 # на y = 0 — симметрия (естественное условие)
    phi = np.zeros(mesh.p.shape[1])
    for it in range(ITERS):
        K = stiff(mu)
        A_, f_, x_, I = condense(K, f, D=D)
        ml = pyamg.smoothed_aggregation_solver(A_.tocsr())
        x0 = phi[I]
        phi[I] = ml.solve(f_, x0=x0, tol=1e-9, accel="cg")
        g = grad_e(phi)
        H = -g
        Hm = np.sqrt((H ** 2).sum(axis=0))
        if not st.any():
            break
        mu_new = np.where(st, MU0 + JS / (Hm + A_F), mu)
        ch = np.max(np.abs(mu_new - mu)[st] / mu[st])
        mu = np.where(st, np.sqrt(mu * mu_new), mu)
        if ch < 0.01:
            break
    B = mu * H + np.vstack([bx, 0 * bx, 0 * bx])
    Br = (B[1] * cy + B[2] * cz) / np.maximum(rr, 1e-9)
    coil = (rr > R0) & (rr < R1) & (np.abs(cx) < 2 * pitch)
    xc = np.round(cx[coil], 4); vals = Br[coil]
    ux = np.unique(xc)
    prof = np.array([vals[xc == u].mean() for u in ux])
    k = np.pi / pitch
    amp = np.hypot(np.mean(prof * np.sin(k * ux)), np.mean(prof * np.cos(k * ux))) * 2
    bmax = np.sqrt((B ** 2).sum(axis=0))[st].max() if st.any() else 0
    return amp, bmax, it + 1, mesh.t.shape[1]


CASES = [("без стали", None, ""),
         ("шайбы М5 DIN 9021 (15/5.3/1.2)", (15.0, 5.3, 1.2), ""),
         ("шайбы М8 DIN 125 (16/8.5/1.5)", (16.0, 8.5, 1.5), ""),
         ("только П-жёлоб (дно + бока)", None, "U"),
         ("шайбы М5 + П-жёлоб", (15.0, 5.3, 1.2), "U"),
         ("шайбы М5 + труба со щелью 3", (15.0, 5.3, 1.2), "tube")]
if "sloi" in sys.argv:                                  # сколько шайб М5 ставить в стык (владелец 04.10)
    CASES = [("без стали", None, ""),
             ("1 × М5 (1.2 мм)", (15.0, 5.3, 1.2), ""),
             ("2 × М5 (2.4 мм)", (15.0, 5.3, 2.4), ""),
             ("3 × М5 (3.6 мм)", (15.0, 5.3, 3.6), ""),
             ("2 × М5 + П-жёлоб", (15.0, 5.3, 2.4), "U"),
             ("2 × М5 + труба со щелью 3", (15.0, 5.3, 2.4), "tube")]
ref = None
for name, w, s in CASES:
    t0 = time.time()
    amp, bm, its, ne = run(w, s)
    ref = ref or amp
    g16 = 500 * amp / ref * np.sqrt(1.6 / 2.7)          # 15×5 без стали: 500 г за 2.7 Вт (sterzhen_diametr.py)
    print(f"{name}: Br1 {amp:.3f} Тл, сила ×{amp / ref:.2f}, при 1.6 Вт ≈ {g16:.0f} г; сталь до {bm:.2f} Тл "
          f"[{its} итер, {ne // 1000}k эл, {time.time() - t0:.0f} с]", flush=True)
