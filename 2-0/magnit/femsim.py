"""2D magnetostatic FEM (A_z) of a reluctance linear motor: row of iron-core coils
under a sliding steel carriage. Compares carriage bottom shapes.

Forces via virtual work on co-energy W' = 1/2 * integral(J*A) (linear iron).
Units: mm in geometry, SI inside the solver. Depth (out of plane) DEPTH mm.
"""
import numpy as np, json, sys
from multiprocessing import Pool
from skfem import MeshTri, Basis, ElementTriP1, ElementTriP0, BilinearForm, LinearForm, asm, condense, solve
from skfem.helpers import dot, grad

MU0 = 4e-7 * np.pi
MUR_IRON = 1000.0
NI = 300.0             # ampere-turns per coil (~300 turns x 1 A)
DEPTH = 10.0           # mm, out-of-plane length (core ~10 mm)
PITCH = 20.0           # coil pitch along the neck, mm
GAP = 0.4              # air gap carriage-core, mm

# ---------- grid (uniform 0.25 mm in x, 0.05 mm in the gap / carriage band) ----------
xs = np.arange(-60, 60 + 1e-9, 0.25)
ys = np.unique(np.concatenate([
    np.linspace(-30, -0.5, 60),
    np.arange(-0.5, 7.0 + 1e-9, 0.05),
    np.linspace(7.0, 40, 40)]))
mesh = MeshTri.init_tensor(xs, ys)
basis = Basis(mesh, ElementTriP1())
b0 = Basis(mesh, ElementTriP0())
cx, cy = mesh.p[:, mesh.t].mean(axis=1)   # element centroids (mm)
D = mesh.boundary_nodes()

# ---------- stator ----------
coil_x = np.array([-40, -20, 0, 20, 40.0])
core = np.zeros_like(cx, bool)
for c in coil_x:
    core |= (np.abs(cx - c) < 2.0) & (cy > -12) & (cy < 0)
core |= (np.abs(cx) < 50) & (cy > -14) & (cy < -12)          # back iron
win_area = 2.5 * 10.0                                         # mm^2 per side
Jval = NI / (win_area * 1e-6)                                 # A/m^2
def stator_J(active):
    J = np.zeros_like(cx)
    for c, s in zip(coil_x, active):
        if s == 0: continue
        L = (cx > c - 4.5) & (cx < c - 2.0) & (cy > -11) & (cy < -1)
        R = (cx > c + 2.0) & (cx < c + 4.5) & (cy > -11) & (cy < -1)
        J[L] += s * Jval; J[R] -= s * Jval
    return J

# ---------- carriage shapes (X = carriage centre, g = gap) ----------
def carriage(shape, X, g):
    u = cx - X; v = cy - g          # local coords, v=0 is lowest point
    if shape == "flat":
        return (np.abs(u) < 20) & (v > 0) & (v < 5)
    plate = (np.abs(u) < 20) & (v > 3) & (v < 5)
    if shape == "wedge":                       # one triangle, tip down, 12 mm wide
        return plate | ((v > 0) & (v < 3) & (np.abs(u) < 6 * v / 3))
    if shape == "comb":                        # 3 square teeth 4 mm, pitch 15
        t = np.zeros_like(u, bool)
        for k in (-15, 0, 15):
            t |= (np.abs(u - k) < 2) & (v > 0) & (v < 3)
        return plate | t
    if shape == "comb_wedge":                  # 3 trapezoid teeth (tip 2 mm, base 8 mm)
        t = np.zeros_like(u, bool)
        for k in (-15, 0, 15):
            t |= (v > 0) & (v < 3) & (np.abs(u - k) < 1 + 3 * v / 3)
        return plate | t
    raise ValueError(shape)

@BilinearForm
def a(u, v, w): return w.nu * dot(grad(u), grad(v))
@LinearForm
def l(v, w): return w.J * v

def coenergy(shape, X, g, active=(0, 0, 1, 0, 0)):
    iron = core | carriage(shape, X, g)
    nu = np.where(iron, 1 / (MU0 * MUR_IRON), 1 / MU0)
    J = stator_J(active)
    nuf = b0.interpolate(nu); Jf = b0.interpolate(J)
    K = asm(a, basis, nu=nuf) * 1.0           # coordinates in mm: grad ~ 1/mm, dx ~ mm^2
    f = asm(l, basis, J=Jf)
    # rescale mm -> m : K is scale invariant in 2D, f picks up 1e-6 from area
    f = f * 1e-6
    A = solve(*condense(K, f, D=D))
    W = 0.5 * float(f @ A) * DEPTH * 1e-3     # J (co-energy, linear)
    return W

def job(args):
    shape, X, g = args
    return (shape, X, g, coenergy(shape, X, g))

if __name__ == "__main__":
    shapes = ["flat", "wedge", "comb", "comb_wedge"]
    Xs = np.arange(0, 20.0 + 1e-9, 0.5)
    jobs = [(s, float(X), GAP) for s in shapes for X in Xs]
    jobs += [(s, float(X), GAP + dg) for s in shapes for X in Xs[::2] for dg in (-0.05, 0.05)]
    with Pool(8) as p:
        res = p.map(job, jobs, chunksize=4)
    out = {}
    for s, X, g, W in res:
        out.setdefault(s, []).append([X, g, W])
    json.dump(out, open(sys.argv[1] if len(sys.argv) > 1 else "energies.json", "w"))
    print("done", len(res))
