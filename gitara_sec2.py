# -*- coding: utf-8 -*-
"""ГИТАРА: СЕКЦИИ 2 и 3 (средняя и нижняя части грифа) — РАЗБОРНЫЕ.
Три равные секции по 160 (идея юзера): 3 x 160 = 480 = полный гриф классики.
Каждая секция: дно (карман + стенки + зап. стенка до накладки + стыки)
+ 4 одинаковые П-рейки стопкой (ленты в них) + крышка + накладка-фретборд
с ладами на НАСТОЯЩИХ позициях мензуры 650.
Винты автоматически привязываются к серединам межладовых промежутков.
Запуск: .venv-b123d\\Scripts\\python gitara_sec2.py
"""
from build123d import *

OUT = r"C:\App\gitar\2-0\Print\Print"
L = 160
Z_FLOOR = [3, 8.4, 13.8, 19.2]
JX = (-21, -9, 5, 21)
MENZURA = 650.0


def BB(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(
        abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))


def frets_in(y0, y1):
    """Мировые позиции ладов мензуры в диапазоне [y0, y1]."""
    out, n = [], 1
    while True:
        Ln = MENZURA * (1 - 2 ** (-n / 12))
        if Ln > y1:
            return out
        if Ln >= y0:
            out.append(Ln)
        n += 1


def snap_mid(y_target, sec_y0):
    """Привязать локальный y к середине ближайшего межладового промежутка."""
    fs = [sec_y0] + frets_in(sec_y0 + 0.5, sec_y0 + L) + [sec_y0 + L]
    mids = [(a + b) / 2 - sec_y0 for a, b in zip(fs, fs[1:]) if b - a > 7]
    return min(mids, key=lambda m: abs(m - y_target))


def build_section(tag, sec_y0, south_shelf=True):
    wy_wall = [snap_mid(12, sec_y0), snap_mid(148, sec_y0)]
    wy_west = [snap_mid(t, sec_y0) for t in (40, 85, 130)]

    base = BB(-26, 26, 0, L, 0, 3)
    base += BB(7, 10, 0, L, 3, 23)
    base += BB(22, 25, 0, L, 3, 23)
    base -= BB(9.8, 22.2, 18, L + 0.1, 1.4, 23.1)       # карман (после стыка)
    base += BB(-26, -22, 0, L, 3, 23)                   # западная стенка сплошная
    for yr in (50, 110):
        base += BB(-22, 5, yr - 2, yr + 2, 3, 8)        # рёбра дна
    # стык СЕВЕР: верхняя полка + бутербродные Ø2.6
    base -= BB(-26.1, 26.1, -0.1, 18, -0.1, 1.5)
    for hx in JX:
        base -= Pos(hx, 9, 2.25) * Cylinder(1.3, 1.7)
    if south_shelf:                                     # стык ЮГ: нижняя полка
        base += BB(-26, 26, L, L + 18, 0, 1.5)
        for hx in JX:
            base -= Pos(hx, L + 9, 0.75) * Cylinder(1.6, 1.7)
    for wx in (8.5, 23.5):                              # каналы винтов крышки
        for wy in wy_wall:
            base -= Pos(wx, wy, 18) * Cylinder(1.3, 10.2)
    for wy in wy_west:                                  # каналы накладки (запад)
        base -= Pos(-23.8, wy, 19.6) * Cylinder(1.3, 10.2)

    # фретборд = и крышка стопки (идея юзера): язычок-потолок верхней ленты
    # с 45-градусными скосами — печать ладами вверх без поддержек
    fret = BB(-26, 26, 0, L, 0, 2)
    tongue = Polyline((11.5, 0), (20.5, 0), (18.5, -2), (13.5, -2), (11.5, 0))
    tface = make_face(Plane.XZ * tongue)
    fret += Pos(0, 18, 0) * extrude(tface, -(L - 18))
    for Ln in frets_in(sec_y0 + 5, sec_y0 + L - 5):
        fret += Pos(0, Ln - sec_y0, 2) * Rot(0, 90, 0) * Cylinder(1.2, 48)
    holes = [(wx, wy) for wx in (8.5, 23.5) for wy in wy_wall]
    holes += [(-23.8, wy) for wy in wy_west]
    for wx, wy in holes:
        fret -= Pos(wx, wy, 1) * Cylinder(1.6, 2.2)
    return base, fret, holes

tray = BB(10.2, 21.8, 18, L, 0, 1.6)
tray += BB(10.2, 11.4, 18, L, 1.6, 5.4)
tray += BB(20.6, 21.8, 18, L, 1.6, 5.4)
export_stl(Part() + tray, rf"{OUT}\gs2_tray.stl")
print("gs2_tray ok")

band = BB(-4, 4, -10, L + 10, 0, 1.6)
export_stl(Part() + band, rf"{OUT}\gs2_band_test.stl")

ALL = {}
for tag, y0 in (("gs2", 160), ("gs3", 320)):
    base, fret, holes = build_section(tag, y0)
    for nm, part in ((f"{tag}_base", base), (f"{tag}_fret", fret)):
        p = Part() + part
        export_stl(p, rf"{OUT}\{nm}.stl")
        print(f"{nm}: volume={p.volume:.0f} mm3, solids={len(p.solids())}")
    ALL[tag] = holes
print("export done")

# ================= ПРОВЕРКИ =================
from clearance import Assembly
import numpy as np

for tag in ("gs2", "gs3"):
    asm = Assembly()
    asm.add("base", rf"{OUT}\{tag}_base.stl")
    clear, touch = [], []
    for k, zf in enumerate(Z_FLOOR):
        asm.add(f"tray{k}", rf"{OUT}\gs2_tray.stl", loc=(0, 0, zf - 1.6))
        asm.add(f"band{k}", rf"{OUT}\gs2_band_test.stl", loc=(16, 0, zf + 0.05))
        clear.append((f"band{k}", f"tray{k}", 0.0))
        touch.append((f"tray{k}", "base"))
        if k:
            touch.append((f"tray{k}", f"tray{k - 1}"))
            clear.append((f"band{k - 1}", f"tray{k}", 0.15))
    asm.add("fret", rf"{OUT}\{tag}_fret.stl", loc=(0, 0, 23))
    touch += [("fret", "base"), ("fret", "tray3")]
    clear += [("band3", "fret", 0.15)]
    asm.check(clearances=clear, touching=touch, verbose=False)
    asm.check_holes("fret", [(wx, wy, 24.0, 1.6) for wx, wy in ALL[tag]],
                    verbose=False)
    # каналы стыка (север) сквозные с предыдущей секцией (все донья одинаковы
    # по стыку: сверяем с сек-1 для gs2)
    if tag == "gs2":
        asm.add("p0", rf"{OUT}\gs1_p0_base.stl", loc=(0, -160, 0))
        for hx in JX:
            pts = np.array([[hx, 9, zz] for zz in (0.5, 2.0)])
            for nm in ("base", "p0"):
                if asm.meshes[nm].contains(pts).any():
                    print(f"  FAIL канал стыка x={hx}: перекрыт {nm}")
                    raise SystemExit(1)
    print(f"{tag}: чисто")
print("holes: все кольца замкнуты; каналы стыков сквозные")
