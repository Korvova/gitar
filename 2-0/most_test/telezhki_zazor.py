# две тележки теста с разным зазором хвоста: 0.3 и 0.2
import os, sys, importlib
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "gitar_most_v2"))
from build123d import *
import trimesh
def iv(a, b):
    r = a & b
    return 0.0 if r is None else r.volume
for cl in ("0.3", "0.2"):
    os.environ["CL"] = cl
    import most_v2 as M; M = importlib.reload(M); os.chdir(HERE)
    c = M.cart - M.BB(-0.75, 0.75, -5.1, -4.5, M.Z_RL - 0.6, M.Z_RL)
    for x, y in M.PEG:
        c += M.CZ(0.66, M.Z_CT - 1.01, M.Z_CT, x, y)
    lift = iv(Pos(0, 0, 1.0) * c, M.lid) > 0.01
    p = Rot(180, 0, 0) * c; b = p.bounding_box(); p = Pos(-(b.min.X + b.max.X) / 2, -(b.min.Y + b.max.Y) / 2, -b.min.Z) * p
    f = "stl/05_telezhka_zazor_%s.stl" % cl.replace(".", "")
    export_stl(p, f, tolerance=0.01, angular_tolerance=0.1)
    print(f, "ширина %.1f" % b.size.Y, "герм", trimesh.load(f).is_watertight, "пересечение с крышкой", round(iv(c, M.lid), 3), "держит вверх" if lift else "")
