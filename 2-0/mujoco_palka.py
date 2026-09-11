# -*- coding: utf-8 -*-
"""MuJoCo: привод «палка» четырёх станций грифа на настоящей физике.

Цепочка каждой станции k: кривошип на валу NEMA (в деке, Y=MY[k]) → палец Ø5
вниз в ВИЛКУ хвоста ленты → лента (свободное тело, лежит на полу этажа, ходит
в жёлобе x 5.4..14.6) → КОЛЬЦО головы ленты на стаде плеча → плечо качается
на оси (Y=AXES_Y[k]) → ШТЫРЬ на конце плеча (Y=CARTS_Y[k]) метёт поперёк грифа.

Что «настоящее»: лента — свободное тело, её держат только контакты (пол,
потолок, жёлоб, стад в кольце, палец в вилке). Мотор — позиционный сервопривод
с реальным пределом момента NEMA14. Оси плеча и вала — шарниры (люфт Ø5/Ø6
не моделируется — упрощение, как в Bullet-модели через GENERIC ±0.5).
Единицы: мм, кг, с (гравитация 9810; момент = кг·мм²/с² = 1e-6 Н·м).

Запуск (venv build123d):
  .venv-b123d\\Scripts\\python 2-0\\mujoco_palka.py            # окно + панель
  .venv-b123d\\Scripts\\python 2-0\\mujoco_palka.py --test     # без окна: качание, отчёт, картинки
Ключи: rpin4.3 slotx7.5 amp62 — как у gitara_physics4.py.
"""
import sys, math, time, os

import mujoco
import numpy as np

argv = sys.argv[1:]
TEST = "--test" in argv
def _arg(pref, default):
    return next((float(a[len(pref):]) for a in argv if a.startswith(pref)), default)

# ---------------- параметры из gitara_sec1.py / gitara_deka.py ----------------
CARTS_Y = [18, 34, 50, 66]
AXES_Y = [y + 52 for y in CARTS_Y]
LANE = 10
Z_FLOOR = [3, 8.4, 13.8, 19.2]
FLOOR_T, CAV = 1.6, 3.8
Z_DECK, DECK_T = 23, 3
MY = [505, 555, 605, 668]
COMB_Y = (535, 585, 635, 698)      # гребёнки деки: мотор + 30 (gitara_deka.py)
R_PIN = _arg("rpin", 4.3)      # радиус пальца кривошипа
SLOTX = _arg("slotx", 7.5)     # полуширина паза вилки ленты (по X)
AMP = _arg("amp", 62)          # сектор качания в тесте, град
NEMA14_TORQUE = 0.10 * 1e6     # 0.10 Н·м в единицах кг·мм²/с²

HERE = os.path.dirname(os.path.abspath(__file__))
COL = {"static": "0.78 0.75 0.70 0.35", "wall": "0.6 0.6 0.62 0.5", "arm": "0.25 0.45 0.8 1",
       "band": "0.85 0.35 0.2 1", "crank": "0.85 0.7 0.2 1", "stud": "0.3 0.3 0.3 1",
       "pin": "0.1 0.6 0.3 1", "cart": "0.95 0.95 0.9 1"}


def box(x0, x1, y0, y1, z0, z1, rgba, cls="", extra=""):
    return ('<geom type="box" pos="%.3f %.3f %.3f" size="%.3f %.3f %.3f" rgba="%s" %s %s/>'
            % ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2, abs(x1 - x0) / 2, abs(y1 - y0) / 2,
               abs(z1 - z0) / 2, rgba, cls, extra))


def cyl(cx, cy, z0, z1, r, rgba, cls="", extra=""):
    return ('<geom type="cylinder" pos="%.3f %.3f %.3f" size="%.3f %.3f" rgba="%s" %s %s/>'
            % (cx, cy, (z0 + z1) / 2, r, abs(z1 - z0) / 2, rgba, cls, extra))


def ring(cx, cy, z0, z1, rin, rout, rgba, cls="", extra=""):
    """Кольцо (дырка под стад) из 8 брусков — выпуклые контакты."""
    rc = (rin + rout) / 2
    w = 2 * rc * math.tan(math.pi / 8) + 0.2
    out = []
    for k in range(8):
        a = k * math.pi / 4
        q = "%.6f 0 0 %.6f" % (math.cos(a / 2), math.sin(a / 2))
        out.append('<geom type="box" pos="%.3f %.3f %.3f" quat="%s" size="%.3f %.3f %.3f" rgba="%s" %s %s/>'
                   % (cx + rc * math.cos(a), cy + rc * math.sin(a), (z0 + z1) / 2, q,
                      (rout - rin) / 2, w / 2, abs(z1 - z0) / 2, rgba, cls, extra))
    return "\n".join(out)


def plate_with_slots(z0, z1, slots, rgba, pockets=()):
    """Плита x±26, y 0..160 с дуговыми прорезями (X ±24.5, Y yc-3.5..yc+7.5):
    режем на Y-полосы, в зоне прорези остаются только бортики |x|>24.5.
    pockets: [(x0,x1,y0,y1,depth)] — карманы снизу плиты (под подшипник стада)."""
    ys = [0, 160] + [e for yc in slots for e in (yc - 3.5, yc + 7.5)]
    ys += [e for pk in pockets for e in (pk[2], pk[3])]
    edges = sorted(set(ys))
    out = []
    for a, b in zip(edges[:-1], edges[1:]):
        mid = (a + b) / 2
        in_slot = any(yc - 3.5 <= mid <= yc + 7.5 for yc in slots)
        pk = next((pk for pk in pockets if pk[2] <= mid <= pk[3]), None)
        if in_slot:
            out.append(box(-26, -24.5, a, b, z0, z1, rgba))
            out.append(box(24.5, 26, a, b, z0, z1, rgba))
        elif pk:
            x0, x1, _, _, dep = pk
            out.append(box(-26, x0, a, b, z0, z1, rgba))
            out.append(box(x1, 26, a, b, z0, z1, rgba))
            out.append(box(x0, x1, a, b, z0 + dep, z1, rgba))
        else:
            out.append(box(-26, 26, a, b, z0, z1, rgba))
    return "\n".join(out)


BEAR_STUD = dict(r=3.0, h=2.5, pocket=0.0, lip=0.4)   # MR63ZZ 3x6x2.5 в отверстии пада плеча, на бортике 0.4
BEAR_PIN = dict(r=4.0, h=4.0)                 # 693ZZ 3x8x4 на штыре в вилке тележки
ZC = Z_DECK + DECK_T + 0.15                   # низ тележки


def build_xml(r_pin=R_PIN, slotx=SLOTX, carts=False, bear_stud=False, bear_pin=False):
    S = []   # статика
    # --- секция-1: этажная стопка ---
    S.append(box(-26, 26, 0, 160, 0, 3, COL["static"]))                    # P0 дно
    S.append(box(-26, -24, 0, 160, 3, 6.8, COL["wall"]))
    S.append(box(24, 26, 0, 160, 3, 6.8, COL["wall"]))
    def pockets_for(k):   # карман в потолке этажа k-1 над стадом его плеча
        if not bear_stud or k == 0 or BEAR_STUD["pocket"] <= 0:
            return ()
        ay = AXES_Y[k - 1]
        return [(LANE - 6, LANE + 6, ay - 6, ay + 6, BEAR_STUD["pocket"])]
    for k in (1, 2, 3):
        zf = Z_FLOOR[k]
        S.append(plate_with_slots(zf - FLOOR_T, zf, CARTS_Y[:k], COL["static"], pockets_for(k)))
        S.append(box(-26, -24, 0, 160, zf, zf + CAV, COL["wall"]))
        S.append(box(24, 26, 0, 160, zf, zf + CAV, COL["wall"]))
    S.append(plate_with_slots(Z_DECK, Z_DECK + DECK_T, CARTS_Y, COL["static"], pockets_for(4)))   # палуба
    if carts:   # борта общего канала тележек на палубе
        S.append(box(-26, 26, CARTS_Y[0] - 10.35, CARTS_Y[0] - 7.35, Z_DECK + DECK_T, Z_DECK + DECK_T + 4, COL["wall"]))
        S.append(box(-26, 26, CARTS_Y[3] + 7.35, CARTS_Y[3] + 10.35, Z_DECK + DECK_T, Z_DECK + DECK_T + 4, COL["wall"]))
    for k in range(4):   # стады осей плеч (визуально; ось = шарнир)
        S.append(cyl(0, AXES_Y[k], Z_FLOOR[k], Z_FLOOR[k] + 3.6, 2.5, COL["stud"], extra='contype="0" conaffinity="0"'))
    # --- секции 2–3 и дека: пол/потолок жёлоба и боковые рейки для лент ---
    for k in range(4):
        zf = Z_FLOOR[k]
        S.append(box(2, 18, 160, 480, zf - FLOOR_T, zf, COL["static"]))               # пол этажа под лентой (сек 2–3)
        S.append(box(3.4, 5.4, 160, 480, zf, zf + CAV, COL["wall"]))                   # рейки жёлоба (сек 2–3)
        S.append(box(14.6, 16.6, 160, 480, zf, zf + CAV, COL["wall"]))
    S.append(box(2, 18, 160, 480, Z_DECK, Z_DECK + DECK_T, COL["static"]))           # потолок верхнего этажа (сек 2–3)
    S.append(box(-26, 26, 480, 800, 0, 3, COL["static"]))                              # дно деки
    for yg in COMB_Y:   # гребёнки деки: щели лент x 5.4..14.6 на каждом этаже, между этажами — тело
        S.append(box(-6, 5.4, yg - 2, yg + 2, 3, 22.5, COL["wall"]))
        S.append(box(14.6, 21.9, yg - 2, yg + 2, 3, 22.5, COL["wall"]))
        for k in range(4):
            zf = Z_FLOOR[k]
            S.append(box(5.4, 14.6, yg - 2, yg + 2, zf + 1.95, zf + CAV, COL["wall"]))   # над щелью до потолка
            S.append(box(5.4, 14.6, yg - 2, yg + 2, zf - FLOOR_T, zf - 0.15, COL["wall"]))  # пол щели под лентой
    B = []   # подвижные тела
    ACT, SENS = [], []
    for k in range(4):
        zA = Z_FLOOR[k] + 0.2
        ay = AXES_Y[k]
        pin_h = (Z_DECK + DECK_T + 4) - (zA + 1.6)
        # --- плечо: шарнир в оси ---
        g = [ring(0, 0, 0, 1.6, 3.0, 5.0, COL["arm"], extra='contype="0" conaffinity="0"'),
             box(-2.5, 2.5, -52, -3, 0, 1.6, COL["arm"]),
             cyl(0, -52, 0, 1.6, 3.5, COL["arm"]),
             box(5, LANE - 4, -2.5, 2.5, 0, 1.6, COL["arm"])]
        sub = []
        if bear_stud:   # пад плеча = бортик 0.4 + стенка вокруг отверстия Ø6.1; подшипник — своё тело на шарнире
            lip = BEAR_STUD["lip"]
            g.append(cyl(LANE, 0, 0, lip, 4.5, COL["arm"]))
            g.append(ring(LANE, 0, lip, 1.6, BEAR_STUD["r"] + 0.05, 4.5, COL["arm"], extra='contype="0" conaffinity="0"'))
            g.append(cyl(LANE, 0, lip, lip + BEAR_STUD["h"], 1.5, COL["stud"], extra='contype="0" conaffinity="0"'))   # штифт Ø3
            sub.append('<body name="bstud%d" pos="%.3f 0 %.3f"><joint type="hinge" axis="0 0 1" damping="0.001"/>'
                       '<geom type="cylinder" size="%.3f %.3f" rgba="0.85 0.85 0.9 1" friction="0.02 0.001 0.0001"/></body>'
                       % (k, LANE, lip + BEAR_STUD["h"] / 2, BEAR_STUD["r"], BEAR_STUD["h"] / 2))
        else:
            g.append(cyl(LANE, 0, 0, 1.6, 4.0, COL["arm"]))                        # пад угла-1
            g.append(cyl(LANE, 0, 1.6, 3.4, 2.5, COL["stud"]))                     # стад Ø5 под кольцо ленты
        if bear_pin:    # штырь Ø5 до палубы, выше — штифт Ø3 с подшипником 693
            zb = ZC + 1.0 - zA                                                   # низ подшипника чуть выше низа тележки
            g.append(cyl(0, -52, 1.6, zb, 2.5, COL["pin"]))
            g.append(cyl(0, -52, zb, 1.6 + pin_h, 1.5, COL["pin"], extra='contype="0" conaffinity="0"'))
            sub.append('<body name="bpin%d" pos="0 -52 %.3f"><joint type="hinge" axis="0 0 1" damping="0.001"/>'
                       '<geom type="cylinder" size="%.3f %.3f" rgba="0.85 0.85 0.9 1" friction="0.02 0.001 0.0001"/></body>'
                       % (k, zb + BEAR_PIN["h"] / 2, BEAR_PIN["r"], BEAR_PIN["h"] / 2))
        else:
            g.append(cyl(0, -52, 1.6, 1.6 + pin_h, 2.5, COL["pin"]))               # штырь Ø5 в тележку
        B.append('<body name="arm%d" pos="0 %.3f %.3f"><joint name="arm%d" type="hinge" axis="0 0 1" damping="20"/>'
                 '<site name="pin%d" pos="0 -52 %.3f" size="1"/>%s%s</body>' % (k, ay, zA, k, k, 1.6 + pin_h, "\n".join(g), "\n".join(sub)))
        # --- тележка: скользит по каналу палубы (шарнир-направляющая), вилка открыта на север ---
        if carts:
            cy = CARTS_Y[k]
            half = BEAR_PIN["r"] + 0.1 if bear_pin else 3.0                   # полупаз: 8.2 под подшипник / 6 под штырь
            g = [box(-half - 3, -half, -7, 7, 0, 6, COL["cart"]),
                 box(half, half + 3, -7, 7, 0, 6, COL["cart"]),
                 box(-half, half, -7, -(half + 0.9), 0, 6, COL["cart"])]        # закрытый торец на юге, зазор ~1 мм
            B.append('<body name="cart%d" pos="0 %.3f %.3f"><joint name="cart%d" type="slide" axis="1 0 0" damping="0.5" range="-25 25"/>%s</body>'
                     % (k, cy, ZC, k, "\n".join(g)))
        # --- лента: свободное тело ---
        yEnd = MY[k] + 10
        rin = BEAR_STUD["r"] + 0.05 if bear_stud else 3.0                        # дырка Ø6.1 под подшипник / Ø6 под стад
        g = [ring(LANE, ay, zA + 1.8, zA + 3.4, rin, 5.5, COL["band"]),
             box(LANE - 4, LANE + 4, ay + (rin + 0.55), ay + 16, zA + 1.8, zA + 3.4, COL["band"]),   # ступень начинается за дыркой + 0.5
             box(LANE - 4, LANE + 4, ay + 12, ay + 16, zA, zA + 3.4, COL["band"]),
             box(LANE - 4, LANE + 4, ay + 12, MY[k] - 6, zA, zA + 1.6, COL["band"]),
             box(LANE - slotx - 2, LANE - slotx, MY[k] - 6, yEnd, zA, zA + 1.6, COL["band"]),
             box(LANE + slotx, LANE + slotx + 2, MY[k] - 6, yEnd, zA, zA + 1.6, COL["band"]),
             box(LANE - slotx, LANE + slotx, MY[k] - 6, MY[k] - 3, zA, zA + 1.6, COL["band"]),
             box(LANE - slotx, LANE + slotx, MY[k] + 3, yEnd, zA, zA + 1.6, COL["band"])]
        for yp in (166.5, 326.5, 486.5):
            g.append(cyl(LANE, yp, zA + 0.8, zA + 3.2, 1.5, COL["band"]))
        B.append('<body name="band%d" pos="0 0 0"><freejoint name="band%d"/>%s</body>' % (k, k, "\n".join(g)))
        # --- кривошип: шарнир на валу, сервопривод ---
        dz0 = Z_FLOOR[k] + 1.8 + 0.25
        g = [cyl(0, 0, dz0, dz0 + 2.5, 7.0, COL["crank"]),
             cyl(r_pin, 0, dz0 - 1.7, dz0, 2.5, COL["crank"])]
        B.append('<body name="crank%d" pos="%.3f %.3f 0"><joint name="crank%d" type="hinge" axis="0 0 1" damping="5"/>%s</body>'
                 % (k, LANE, MY[k], k, "\n".join(g)))
        ACT.append('<position name="m%d" joint="crank%d" kp="%.0f" kv="%.0f" ctrlrange="-3.2 3.2" forcerange="-%.0f %.0f"/>'
                   % (k, k, 3e5, 3e3, NEMA14_TORQUE, NEMA14_TORQUE))
        SENS.append('<framepos name="pin%d" objtype="site" objname="pin%d"/>' % (k, k))
    xml = """<mujoco model="palka4">
  <compiler angle="radian"/>
  <option timestep="0.0001" gravity="0 0 -9810" integrator="implicitfast" cone="elliptic" impratio="10"/>
  <visual><global offwidth="1600" offheight="1000"/><map znear="0.001" zfar="50"/><headlight ambient="0.5 0.5 0.5" diffuse="0.6 0.6 0.6"/></visual>
  <default>
    <geom density="1.24e-6" friction="0.2 0.005 0.0001" solref="0.002 1" solimp="0.95 0.99 0.001" margin="0"/>
    <joint armature="0.0001"/>
  </default>
  <worldbody>
    <light pos="0 300 800" dir="0 -0.3 -1" directional="true"/>
    <camera name="top" pos="0 90 400" xyaxes="1 0 0 0 1 0"/>
    <camera name="deck" pos="200 600 250" xyaxes="0 1 0 -0.7 0 0.7"/>
    <body name="static">%s</body>
    %s
  </worldbody>
  <actuator>%s</actuator>
  <sensor>%s</sensor>
</mujoco>""" % ("\n".join(S), "\n".join(B), "\n".join(ACT), "\n".join(SENS))
    return xml


def make(r_pin=R_PIN, slotx=SLOTX, **opt):
    m = mujoco.MjModel.from_xml_string(build_xml(r_pin, slotx, **opt))
    d = mujoco.MjData(m)
    mujoco.mj_forward(m, d)
    return m, d


def readout(m, d, k):
    """band dy (мм), угол плеча (град), X штыря (мм), угол кривошипа (град)."""
    band = d.body("band%d" % k)
    arm = d.joint("arm%d" % k).qpos[0]
    pin = d.sensor("pin%d").data if False else d.site("pin%d" % k).xpos
    crank = d.joint("crank%d" % k).qpos[0]
    cx = None
    if mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "cart%d" % k) >= 0:
        cx = d.joint("cart%d" % k).qpos[0]
    return band.xpos[1], math.degrees(arm), pin[0], math.degrees(crank), cx


# ============================ ТЕСТ БЕЗ ОКНА ============================
def run_test():
    amp = math.radians(AMP)
    T = 2.0
    configs = [("штыри без тележек", {}),
               ("тележки, штырь Ø5 / стад Ø5", dict(carts=True)),
               ("тележки + MR63 на стаде", dict(carts=True, bear_stud=True)),
               ("тележки + MR63 стад + 693 штырь", dict(carts=True, bear_stud=True, bear_pin=True))]
    print("=" * 78)
    print("MuJoCo палка: сектор ±%.0f°, палец r%.1f, паз ленты ±%.1f, момент NEMA14 0.10 Н·м" % (AMP, R_PIN, SLOTX))
    last = None
    for title, opt in configs:
        m, d = make(**opt)
        for _ in range(int(0.3 / m.opt.timestep)):
            mujoco.mj_step(m, d)
        y0 = [d.body("band%d" % k).xpos[1] for k in range(4)]
        log = {k: {"x": [], "dy": [], "phi": [], "tq": [], "cx": []} for k in range(4)}
        n = int(2 * T / m.opt.timestep)
        for i in range(n):
            t = i * m.opt.timestep
            ramp = min(1.0, t / 0.5)
            for k in range(4):
                d.ctrl[k] = ramp * amp * math.sin(2 * math.pi * (t / T - k / 4))
            mujoco.mj_step(m, d)
            if i % 100 == 0 and t > 0.6:
                for k in range(4):
                    dy, phi, px, th, cx = readout(m, d, k)
                    L = log[k]
                    L["x"].append(px); L["dy"].append(dy - y0[k]); L["phi"].append(phi)
                    L["tq"].append(abs(d.actuator_force[k]) * 1e-6)
                    if cx is not None:
                        L["cx"].append(cx)
        print("-- " + title)
        print("ст  штырь X (min..max) = ход    тележка ход   лента dY       момент макс, Н·м")
        for k in range(4):
            L = log[k]
            cart = "%5.1f" % (max(L["cx"]) - min(L["cx"])) if L["cx"] else "  -  "
            print("%d   %6.1f .. %5.1f = %4.1f     %s      %+4.1f..%+4.1f    %.3f" % (
                k, min(L["x"]), max(L["x"]), max(L["x"]) - min(L["x"]), cart, min(L["dy"]), max(L["dy"]), max(L["tq"])))
        last = (m, d)
    print("=" * 78)
    m, d = last
    # картинки
    r = mujoco.Renderer(m, 1000, 1600)
    for cam, name in (("top", "mj_palka_top.png"), ("deck", "mj_palka_deck.png")):
        r.update_scene(d, camera=cam)
        img = r.render()
        try:
            from PIL import Image
            Image.fromarray(img).save(os.path.join(HERE, name))
            print("saved", name)
        except ImportError:
            pass


# ============================ ОКНО + ПАНЕЛЬ ============================
def run_ui():
    import tkinter as tk
    from tkinter import ttk
    import mujoco.viewer

    state = {"m": None, "d": None, "sweep": False, "t": 0.0, "rebuild": False}
    state["m"], state["d"] = make()

    root = tk.Tk()
    root.title("Палка: моторы NEMA")
    root.geometry("+20+40")
    frm = ttk.Frame(root, padding=10); frm.pack(fill="both", expand=True)
    angles = [tk.DoubleVar(value=0.0) for _ in range(4)]
    labels = []
    for k in range(4):
        ttk.Label(frm, text="Станция %d (тележка Y=%d, мотор Y=%d)" % (k, CARTS_Y[k], MY[k])).grid(row=3 * k, column=0, columnspan=3, sticky="w", pady=(8, 0))
        s = ttk.Scale(frm, from_=-90, to=90, variable=angles[k], length=320)
        s.grid(row=3 * k + 1, column=0, columnspan=2, sticky="we")
        e = ttk.Entry(frm, textvariable=angles[k], width=7); e.grid(row=3 * k + 1, column=2, padx=4)
        lb = ttk.Label(frm, text="", font=("Consolas", 9)); lb.grid(row=3 * k + 2, column=0, columnspan=3, sticky="w")
        labels.append(lb)
    r0 = 12
    ttk.Separator(frm).grid(row=r0, column=0, columnspan=3, sticky="we", pady=8)
    master = tk.DoubleVar(value=0.0)
    ttk.Label(frm, text="Все четыре сразу, °").grid(row=r0 + 1, column=0, sticky="w")
    def on_master(*_):
        for a in angles: a.set(round(master.get(), 1))
    ttk.Scale(frm, from_=-90, to=90, variable=master, length=320, command=on_master).grid(row=r0 + 2, column=0, columnspan=2, sticky="we")
    sweep = tk.BooleanVar(value=False)
    amp_v = tk.DoubleVar(value=AMP); per_v = tk.DoubleVar(value=2.0)
    ttk.Checkbutton(frm, text="Качать сектором", variable=sweep).grid(row=r0 + 3, column=0, sticky="w", pady=(6, 0))
    ttk.Label(frm, text="±°").grid(row=r0 + 3, column=1, sticky="e"); ttk.Entry(frm, textvariable=amp_v, width=6).grid(row=r0 + 3, column=2)
    ttk.Label(frm, text="период, с").grid(row=r0 + 4, column=1, sticky="e"); ttk.Entry(frm, textvariable=per_v, width=6).grid(row=r0 + 4, column=2)
    ttk.Separator(frm).grid(row=r0 + 5, column=0, columnspan=3, sticky="we", pady=8)
    rp_v = tk.DoubleVar(value=R_PIN); sx_v = tk.DoubleVar(value=SLOTX)
    carts_v = tk.BooleanVar(value=False); bs_v = tk.BooleanVar(value=False); bp_v = tk.BooleanVar(value=False)
    ttk.Checkbutton(frm, text="Тележки в канале палубы", variable=carts_v, command=lambda: state.__setitem__("rebuild", True)).grid(row=r0 + 11, column=0, columnspan=3, sticky="w")
    ttk.Checkbutton(frm, text="MR63ZZ 3×6×2.5 на стаде плеча (карман 0.5 в потолке)", variable=bs_v, command=lambda: state.__setitem__("rebuild", True)).grid(row=r0 + 12, column=0, columnspan=3, sticky="w")
    ttk.Checkbutton(frm, text="693ZZ 3×8×4 на штыре в вилке тележки", variable=bp_v, command=lambda: state.__setitem__("rebuild", True)).grid(row=r0 + 13, column=0, columnspan=3, sticky="w")
    ttk.Label(frm, text="Палец кривошипа r, мм").grid(row=r0 + 6, column=0, sticky="w"); ttk.Entry(frm, textvariable=rp_v, width=6).grid(row=r0 + 6, column=2)
    ttk.Label(frm, text="Паз вилки ленты ±, мм").grid(row=r0 + 7, column=0, sticky="w"); ttk.Entry(frm, textvariable=sx_v, width=6).grid(row=r0 + 7, column=2)
    def rebuild():
        state["rebuild"] = True
    ttk.Button(frm, text="Пересобрать модель", command=rebuild).grid(row=r0 + 8, column=0, columnspan=3, sticky="we", pady=6)
    status = ttk.Label(frm, text="", foreground="gray"); status.grid(row=r0 + 9, column=0, columnspan=3, sticky="w")
    ttk.Label(frm, text="Момент мотора ограничен 0.10 Н·м (NEMA14).\nЛента — свободное тело на контактах.", foreground="gray").grid(row=r0 + 10, column=0, columnspan=3, sticky="w", pady=(8, 0))

    alive = {"ok": True}
    root.protocol("WM_DELETE_WINDOW", lambda: alive.__setitem__("ok", False))

    def loop(viewer):
        m, d = state["m"], state["d"]
        substeps = int(1 / 60 / m.opt.timestep)
        last = time.perf_counter()
        while viewer.is_running() and alive["ok"]:
            if state["rebuild"]:
                state["rebuild"] = False
                try:
                    m2, d2 = make(rp_v.get(), sx_v.get(), carts=carts_v.get(), bear_stud=bs_v.get(), bear_pin=bp_v.get())
                    state["m"], state["d"] = m2, d2
                    status.config(text="Пересобрано: r=%.1f паз ±%.1f, тележки=%s, MR63=%s, 693=%s" % (rp_v.get(), sx_v.get(), carts_v.get(), bs_v.get(), bp_v.get()))
                    return "rebuild"
                except Exception as ex:
                    status.config(text="Ошибка: %s" % ex)
            if sweep.get():
                state["t"] += 1 / 60
                a = amp_v.get() * math.sin(2 * math.pi * state["t"] / max(0.2, per_v.get()))
                for v in angles: v.set(round(a, 1))
            for k in range(4):
                d.ctrl[k] = math.radians(angles[k].get())
            for _ in range(substeps):
                mujoco.mj_step(m, d)
            viewer.sync()
            for k in range(4):
                dy, phi, px, th, cx = readout(m, d, k)
                tq = abs(d.actuator_force[k]) * 1e-6
                labels[k].config(text="крив %6.1f°  лента %+5.2f  плечо %+5.1f°  штырь X %+6.1f%s  M %.3f Н·м" % (
                    th, dy, phi, px, ("  тележка %+6.1f" % cx) if cx is not None else "", tq))
            try:
                root.update()
            except tk.TclError:
                return "closed"
            now = time.perf_counter()
            dt = 1 / 60 - (now - last)
            if dt > 0:
                time.sleep(dt)
            last = time.perf_counter()
        return "closed"

    while alive["ok"]:
        m, d = state["m"], state["d"]
        with mujoco.viewer.launch_passive(m, d, show_left_ui=False, show_right_ui=False) as viewer:
            viewer.cam.lookat[:] = (0, 90, 15); viewer.cam.distance = 320; viewer.cam.azimuth = 90; viewer.cam.elevation = -60
            res = loop(viewer)
        if res != "rebuild":
            break
    try:
        root.destroy()
    except tk.TclError:
        pass


if __name__ == "__main__":
    run_test() if TEST else run_ui()
