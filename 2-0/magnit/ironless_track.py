"""Ironless moving-coil linear motor in a magnet U-channel (magpylib, no iron).
x = along the track, y = across the slot (magnetisation), z = height.
Track: walls of N52 blocks, alternating +y/-y every pole pitch TAU.
Carriage: 2 flat coils (2-phase, like a stepper), coil span = TAU, sitting in the slot.
Outputs force constant, motor constant Km = F/sqrt(P), current, power and heating for 500 g.
"""
import numpy as np, magpylib as magpy, itertools, json

BR = 1.43            # N52 remanence, T
RHO = 1.72e-8        # copper
FF = 0.55            # copper fill factor of the winding
CU_DENS, CU_C = 8960, 385
F_TARGET = 0.5 * 9.81

def track(TAU, T, H, G, n_slots, n_poles=12):
    """n_slots slots of width G between n_slots+1 magnet walls of thickness T."""
    col = magpy.Collection()
    for w in range(n_slots + 1):
        yc = -n_slots * (G + T) / 2 + w * (G + T)          # wall centres, slot k centred between walls
        for p in range(-n_poles // 2, n_poles // 2):
            s = 1 if p % 2 == 0 else -1
            col.add(magpy.magnet.Cuboid(polarization=(0, s * BR, 0),
                                        dimension=(TAU * 1e-3, T * 1e-3, H * 1e-3),
                                        position=((p + 0.5) * TAU * 1e-3, yc * 1e-3, 0)))
    return col

def design(TAU, T, H, TC, n_slots, slot=0):
    G = TC + 1.0                                             # 0.5 mm clearance each side
    col = track(TAU, T, H, G, n_slots)
    yslot = (-n_slots * (G + T) / 2 + (slot + 0.5) * (G + T))
    W = 0.8 * TAU                                            # leg width of the coil
    xs = np.linspace(-TAU, TAU, 81)
    ys = np.linspace(-TC / 2, TC / 2, 5) + yslot
    zs = np.linspace(-H / 2, H / 2, 9)
    X, Y, Z = np.meshgrid(xs, ys, zs, indexing="ij")
    B = col.getB(np.stack([X, Y, Z], -1).reshape(-1, 3) * 1e-3).reshape(len(xs), len(ys), len(zs), 3)
    By = B[..., 1].mean(axis=(1, 2))                         # averaged over coil thickness & height
    def leg(xc):                                             # mean By over a leg of width W
        m = np.abs(xs - xc) <= W / 2
        return By[m].mean()
    # best coil position: legs at x0 and x0+TAU, opposite currents
    k1 = max(abs(leg(x0) - leg(x0 + TAU)) for x0 in np.linspace(-TAU / 2, 0, 21)) * H * 1e-3  # N/A per turn
    l_turn = (2 * TAU + 2 * (H + W)) * 1e-3
    area = W * TC * 1e-6
    km = k1 * np.sqrt(FF * area / (RHO * l_turn))           # N/sqrt(W) for one coil (= 2-phase pair)
    P = (F_TARGET / km) ** 2                                 # total for the 2-coil carriage
    cu_mass = 2 * CU_DENS * FF * area * l_turn
    surf = 2 * 2 * (2 * TAU + W) * (H + W) * 1e-6           # both faces of 2 coils
    return dict(TAU=TAU, T=T, H=H, TC=TC, slots=n_slots, Bpk=float(np.abs(By).max()),
                km=float(km), P_W=float(P), cu_g=float(cu_mass * 1e3),
                dTdt=float(P / (cu_mass * CU_C)), dT_steady=float(P / (12 * surf)),
                lane_mm=float(T + G) if n_slots > 1 else float(2 * T + G))

if __name__ == "__main__":
    res = []
    for TAU, T, H, TC in itertools.product((8, 10, 12), (3, 4, 5), (10, 12, 15), (2, 3)):
        res.append(design(TAU, T, H, TC, 1))
    res.sort(key=lambda r: r["P_W"])
    for r in res[:8]: print({k: round(v, 2) if isinstance(v, float) else v for k, v in r.items()})
    best = res[0]
    print("--- same design, 4 slots with shared walls (inner slot):")
    s = design(best["TAU"], best["T"], best["H"], best["TC"], 4, slot=1)
    print({k: round(v, 2) if isinstance(v, float) else v for k, v in s.items()})
    for TAU, T, H, TC in ((10, 4, 12, 3), (10, 3, 12, 3), (10, 5, 15, 3)):
        print("4-slot", TAU, T, H, TC, {k: round(v, 2) for k, v in design(TAU, T, H, TC, 4, 1).items() if k in ("Bpk", "km", "P_W", "cu_g", "dTdt", "dT_steady", "lane_mm")})
    json.dump(res, open("ironless_sweep.json", "w"))
