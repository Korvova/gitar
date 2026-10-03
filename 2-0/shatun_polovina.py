import math, numpy as np
RS, F = 18.0, 3.0
def run(LB, d, R=10.0):
    # шатун подбираем так, чтобы при кривошипе в середине (pin y = 0 смещения) плечо стояло посередине
    PHM = math.asin(20 / LB)
    best = None
    for LC in np.arange(d - 15, d + 15, 0.25):
        rows = []
        for th in np.radians(np.arange(-90, 90.01, 0.5)):        # пол-оборота: палец кривошипа ходит по Y ±R
            cx, cy = R * math.cos(th) * 0 + (R * math.cos(th) - R) * 0 + R * math.sin(th) * 0, 0  # заглушка
        # кривошип: ось (0, d), палец (R cosθ', d + R sinθ'); сектор пол-оборота симметрично вокруг θ' = 0 и 180 — палец ходит вдоль Y
        for side in (0.0, math.pi):
            rows = []
            ok = True
            for th in np.radians(np.arange(-90, 90.01, 0.5)):
                a_ = th + side
                cx, cy = R * math.cos(a_), d + R * math.sin(a_)
                dd = math.hypot(cx, cy)
                if dd > RS + LC or dd < abs(RS - LC):
                    ok = False; break
                a = (RS ** 2 - LC ** 2 + dd ** 2) / (2 * dd)
                h = math.sqrt(max(RS ** 2 - a ** 2, 0))
                px, py = a * cx / dd, a * cy / dd
                sx, sy = max([(px + h * cy / dd, py - h * cx / dd), (px - h * cy / dd, py + h * cx / dd)], key=lambda q: q[0])
                phi = math.atan2(sy, sx)
                lx, ly = sx - cx, sy - cy
                mu = 90 - math.degrees(math.acos(min(1, abs(lx * (-sy) + ly * sx) / (LC * RS))))
                rows.append((phi, mu, LB * math.sin(phi)))
            if not ok:
                continue
            xs = [r[2] for r in rows]
            if max(xs) < 19.5 or min(xs) > -19.5:
                continue
            mu_min = min(r[1] for r in rows if abs(r[2]) <= 20.01)
            dx = max(abs(xs[i + 1] - xs[i]) / math.radians(0.5) for i in range(len(xs) - 1))
            if best is None or mu_min > best[0]:
                best = (mu_min, LC, dx, max(xs), min(xs))
    return best
for d in (32, 60, 90, 150, 250, 500):
    pass
for d in (32, 60, 90, 150, 250, 500):
    b = run(32.51, d, 11.2)
    if b:
        print(f"мотор в {d:3d} мм от оси плеча: худший угол на плече {b[0]:.0f}°, шатун {b[1]:.1f}, ложе {b[4]:.1f}..{b[3]:.1f}, момент на 3 Н {F * b[2] / 1000:.3f} Н·м")
    else:
        print(f"мотор в {d} мм: R10 на пол-оборота не даёт ±20")
