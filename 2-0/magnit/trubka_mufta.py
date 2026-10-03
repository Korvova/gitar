# Магнитная связка: внутренний магнит Ø12×20 (ось вдоль трубки) и наружный магнит площадки над катушками.
import numpy as np, magpylib as magpy
inner = magpy.magnet.Cylinder(polarization=(0, 0, 1.43), dimension=(12e-3, 20e-3), position=(0, 0, 0), meshing=400).rotate_from_angax(90, "y")  # ось вдоль X
for gap_top, tag in ((11.5, "над катушкой r 11 + 0.5"), (13.0, "над катушкой r 12.5 + 0.5")):
    best = 0
    for d in np.linspace(0, 15, 16):
        # наружный: два магнита 10×10×5 над трубкой, полюсами вниз N и S, как у внутреннего концы
        outer = magpy.Collection(
            magpy.magnet.Cuboid(polarization=(0, 0, -1.43), dimension=(10e-3, 10e-3, 5e-3), position=((d - 10) * 1e-3, 0, (gap_top + 2.5) * 1e-3)),
            magpy.magnet.Cuboid(polarization=(0, 0, 1.43), dimension=(10e-3, 10e-3, 5e-3), position=((d + 10) * 1e-3, 0, (gap_top + 2.5) * 1e-3)))
        try:
            F, T = magpy.getFT(outer, inner)
            fx = abs(np.array(F).reshape(-1, 3).sum(axis=0)[0])
        except Exception as e:
            print("getFT нет:", e); raise SystemExit
        best = max(best, fx)
    print(f"связка {tag}: наибольшая сила вдоль трубки {best:.2f} Н ({best * 102:.0f} г)")
outer = magpy.Collection(
    magpy.magnet.Cuboid(polarization=(0, 0, -1.43), dimension=(10e-3, 10e-3, 5e-3), position=(-10e-3, 0, 14e-3)),
    magpy.magnet.Cuboid(polarization=(0, 0, 1.43), dimension=(10e-3, 10e-3, 5e-3), position=(10e-3, 0, 14e-3)))
F, T = magpy.getFT(outer, inner)
print("притяжение площадки к внутреннему магниту (вниз/вверх) при совпадении:", np.round(np.array(F).reshape(-1, 3).sum(axis=0), 2), "Н")
