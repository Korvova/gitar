# -*- coding: utf-8 -*-
# Шагоход: живая физика MuJoCo + панель ползунков. Запуск: python shag_sim.py  (проверка без окна: python shag_sim.py --test)
# Геометрия: отверстия реек — кольца капсул (реальный зазор и трение по нагрузке), зубья — выпуклые трапеции, гребёнка — боксы.
import math, sys, time
import numpy as np, mujoco as mj

DEF = dict(N=3, E=3.0, pin_d=5.0, clear=0.3, spacing=20.0, err=0.3, root=2.9, tip=1.0, h=4.0, post=2.0, overlap=0.7, mu=0.3)

def build(p):
    N = int(p["N"]); E = p["E"] / 1e3; rp = p["pin_d"] / 2e3; cl = p["clear"] / 1e3; XI = p["spacing"] / 1e3; err = p["err"] / 1e3
    Pt = 2 * E * math.sin(math.pi / N); r_ = p["root"] / 2e3; t_ = p["tip"] / 2e3; H = p["h"] / 1e3; po = p["post"] / 2e3; mu = p["mu"]
    y0 = max(0.009, rp + 0.003); yc = y0 + H + E * math.cos(math.pi / N) - p["overlap"] / 1e3; yp = y0 + H + E + 0.0005
    fr = f'friction="{mu} 0.005 0.0001"'
    COL = ["0.75 0.75 0.78 1", "0.4 0.5 0.75 1", "0.9 0.7 0.3 1", "0.5 0.8 0.6 1"]
    cz = lambda k: k * 0.004
    rc = rp + cl + 0.0004; n = max(16, int(2 * math.pi * rc / 0.0008))
    def ring(cx, k):
        s = ""
        for i in range(n):
            a = 2 * math.pi * i / n; x, y = cx + rc * math.cos(a), rc * math.sin(a)
            s += f'<geom type="capsule" fromto="{x:.6f} {y:.6f} -0.0015 {x:.6f} {y:.6f} 0.0015" size="0.0004" contype="{1 << k}" conaffinity="0" {fr} rgba="{COL[k]}"/>\n'
        return s
    def crank(name, x0):
        s = f'<body name="{name}" pos="{x0} 0 0"><joint name="{name}" type="hinge" axis="0 0 1" frictionloss="0.0002" damping="1e-6"/><inertial pos="0 0 0" mass="0.003" diaginertia="1e-7 1e-7 1e-7"/>\n'
        s += '<geom type="cylinder" fromto="0 0 -0.008 0 0 -0.003" size="0.0025" contype="0" conaffinity="0" rgba="0.1 0.2 0.8 1"/>\n'
        for k in range(N):
            a = 2 * math.pi * k / N; x, y = E * math.sin(a), E * math.cos(a); z = cz(k)
            s += f'<geom type="capsule" fromto="{x:.6f} {y:.6f} {z-0.0015:.5f} {x:.6f} {y:.6f} {z+0.0015:.5f}" size="{rp}" contype="0" conaffinity="{1 << k}" {fr} rgba="0.15 0.7 0.25 1"/>\n'
            s += f'<geom type="cylinder" fromto="0 0 {z-0.0028:.5f} 0 0 {z-0.0022:.5f}" size="{E+rp+0.0005:.5f}" contype="0" conaffinity="0" rgba="0.15 0.6 0.25 0.5"/>\n'
        return s + "</body>\n"
    racks = ""; nk = int(0.030 / Pt)
    for k in range(N):
        racks += f'<body name="rack{k}" pos="0 0 {cz(k):.5f}"><joint name="rx{k}" type="slide" axis="1 0 0"/><joint name="ry{k}" type="slide" axis="0 1 0"/><joint name="rz{k}" type="hinge" axis="0 0 1"/><inertial pos="0 0 0" mass="0.004" diaginertia="1e-6 1e-6 1e-6"/>\n'
        racks += ring(0.0, k) + ring(XI + err, k)
        for j in range(-nk, nk + 1):
            racks += f'<geom type="mesh" mesh="tooth" pos="{j*Pt:.6f} 0 0" contype="{1 << 4}" conaffinity="0" {fr} rgba="{COL[k]}"/>\n'
        racks += "</body>\n"
    posts = ""; zm = cz(N - 1) / 2; hz = cz(N - 1) / 2 + 0.002
    for j in range(-3, 3):
        posts += f'<geom type="box" pos="{(j+0.5)*Pt:.6f} {(yc+yp)/2:.6f} {zm:.5f}" size="{po} {(yp-yc)/2:.6f} {hz:.5f}" contype="0" conaffinity="{1 << 4}" {fr} rgba="0.6 0.2 0.7 1"/>\n'
    half = (3 * Pt + po)
    posts += f'<geom type="box" pos="0 {yp+0.0007:.6f} {zm:.5f}" size="{half:.5f} 0.0007 {hz:.5f}" contype="0" conaffinity="0" rgba="0.6 0.2 0.7 1"/>\n'
    posts += f'<geom type="box" pos="0 {yp/2:.6f} {zm+hz+0.0012:.5f}" size="{half:.5f} {yp/2+0.0007:.6f} 0.0008" contype="0" conaffinity="0" rgba="0.6 0.2 0.7 0.25"/>\n'
    verts = " ".join(f"{a:.6f}" for a in (-r_, y0, -0.0015, r_, y0, -0.0015, t_, y0+H, -0.0015, -t_, y0+H, -0.0015, -r_, y0, 0.0015, r_, y0, 0.0015, t_, y0+H, 0.0015, -t_, y0+H, 0.0015))
    return f'''<mujoco><option timestep="0.00005" gravity="0 0 0" integrator="implicitfast" cone="elliptic"/>
<visual><global offwidth="1200" offheight="800"/><headlight ambient="0.5 0.5 0.5" diffuse="0.6 0.6 0.6"/></visual>
<asset><mesh name="tooth" vertex="{verts}"/></asset>
<default><geom solref="0.002 1" solimp="0.9 0.95 0.0001" margin="0.00005"/></default><worldbody>
{crank("c1", 0)}{crank("c2", XI)}{racks}<body name="cart"><joint name="cart" type="slide" axis="1 0 0" frictionloss="0.05"/><inertial pos="0 0 0" mass="0.01" diaginertia="1e-6 1e-6 1e-6"/>{posts}</body></worldbody></mujoco>'''

class Sim:
    def __init__(self, p):
        self.p = dict(p); self.m = mj.MjModel.from_xml_string(build(p)); self.d = mj.MjData(self.m); N = int(p["N"]); E = p["E"] / 1e3
        ad = lambda n: (self.m.jnt_qposadr[mj.mj_name2id(self.m, mj.mjtObj.mjOBJ_JOINT, n)], self.m.jnt_dofadr[mj.mj_name2id(self.m, mj.mjtObj.mjOBJ_JOINT, n)])
        for k in range(N):
            a = 2 * math.pi * k / N
            self.d.qpos[ad(f"rx{k}")[0]] = E * math.sin(a); self.d.qpos[ad(f"ry{k}")[0]] = E * math.cos(a)
        mj.mj_forward(self.m, self.d)
        self.q1, self.v1 = ad("c1"); self.q2, _ = ad("c2"); self.qc, self.vc = ad("cart")
        self.target = 0.0; self.mode = "stop"; self.dir = 1; self.tq = 0.0; self.slow = 0.0
    def step(self, n, Tmax, w, F):
        m, d = self.m, self.d
        for _ in range(n):
            d.qfrc_applied[:] = 0
            if self.mode == "motor":
                self.target += -self.dir * w * m.opt.timestep
                self.tq = float(np.clip(0.5 * (self.target - d.qpos[self.q1]) + 0.002 * (-self.dir * w - d.qvel[self.v1]), -Tmax, Tmax))
                d.qfrc_applied[self.v1] = self.tq
            elif self.mode == "finger":
                d.qfrc_applied[self.vc] = self.dir * F; self.tq = 0.0; self.target = d.qpos[self.q1]
            else:
                self.tq = 0.0; self.target = d.qpos[self.q1]
            mj.mj_step(m, d)
        moving = abs(d.qvel[self.v1]) > 0.15 * w if self.mode == "motor" else abs(d.qvel[self.vc]) > 0.001
        self.slow = 0.0 if (moving or self.mode == "stop") else self.slow + n * m.opt.timestep

if "--test" in sys.argv:
    s = Sim(DEF); s.mode = "motor"; t0 = time.time(); s.step(10000, 0.037, 2 * math.pi, 1.0)
    print("ok cart mm", round(s.d.qpos[s.qc] * 1e3, 2), "crank deg", round(math.degrees(s.d.qpos[s.q1]), 1), "wall s per 0.5 s sim", round(time.time() - t0, 1)); sys.exit()

import tkinter as tk, mujoco.viewer as V
BUILD = [("N", "Слоёв реек", 2, 4, 1), ("E", "Эксцентрик, мм", 1, 5, 0.1), ("pin_d", "Ø штырька, мм", 2, 14, 0.1), ("clear", "Зазор в отверстии, мм", 0.05, 0.8, 0.05),
         ("spacing", "Между валами, мм", 12, 32, 0.5), ("err", "Отверстия рейки: +ошибка, мм", -0.6, 1.0, 0.05), ("root", "Зуб: низ, мм", 1, 4.5, 0.1), ("tip", "Зуб: вершина, мм", 0.2, 3, 0.1),
         ("h", "Зуб: высота, мм", 2, 7, 0.1), ("post", "Столбик гребёнки, мм", 0.6, 3, 0.1), ("overlap", "Захват при передаче, мм", 0.2, 1.6, 0.05), ("mu", "Трение", 0.05, 0.6, 0.05)]
root = tk.Tk(); root.title("Шагоход — ползунки"); root.attributes("-topmost", True)
vars_ = {}
for i, (k, t, a, b, st) in enumerate(BUILD):
    tk.Label(root, text=t, anchor="w", width=28).grid(row=i, column=0, sticky="w")
    v = tk.DoubleVar(value=DEF[k]); vars_[k] = v
    tk.Scale(root, variable=v, from_=a, to=b, resolution=st, orient="horizontal", length=240).grid(row=i, column=1)
r = len(BUILD)
live = {}
for j, (k, t, a, b, st, d0) in enumerate((("T", "Момент мотора, мН·м", 2, 60, 1, 37), ("W", "Обороты, об/с", 0.1, 3, 0.1, 1.0), ("F", "Сила пальца, Н", 0.1, 12, 0.1, 2.0))):
    tk.Label(root, text=t, anchor="w", width=28).grid(row=r + j, column=0, sticky="w")
    v = tk.DoubleVar(value=d0); live[k] = v
    tk.Scale(root, variable=v, from_=a, to=b, resolution=st, orient="horizontal", length=240).grid(row=r + j, column=1)
S = {"s": None, "h": None}
def open_viewer():
    s = Sim({k: v.get() for k, v in vars_.items()})
    if S["h"] is not None:
        try: S["h"].close()
        except Exception: pass
    S["s"] = s; S["h"] = V.launch_passive(s.m, s.d, show_left_ui=False, show_right_ui=False)
    c = S["h"].cam; c.lookat[:] = (0.01, 0.006, 0.004); c.distance = 0.11; c.elevation = -62; c.azimuth = 90
def go(mode, d):
    if S["s"]: S["s"].mode = mode; S["s"].dir = d; S["s"].slow = 0.0
f = tk.Frame(root); f.grid(row=r + 3, column=0, columnspan=2, pady=6)
for t, m_, d_ in (("◀ Мотор", "motor", -1), ("Мотор ▶", "motor", 1), ("◀ Палец", "finger", -1), ("Палец ▶", "finger", 1), ("Стоп", "stop", 1)):
    tk.Button(f, text=t, width=9, command=lambda m_=m_, d_=d_: go(m_, d_)).pack(side="left", padx=2)
tk.Button(root, text="ПРИМЕНИТЬ РАЗМЕРЫ И ПЕРЕЗАПУСТИТЬ", command=open_viewer, bg="#cfe8ff").grid(row=r + 4, column=0, columnspan=2, sticky="we", padx=4)
info = tk.Label(root, font=("Consolas", 11), justify="left", anchor="w"); info.grid(row=r + 5, column=0, columnspan=2, sticky="we", padx=4, pady=6)
def tick():
    s, h = S["s"], S["h"]
    if s and h and h.is_running():
        t0 = time.perf_counter(); done = 0
        with h.lock():
            while time.perf_counter() - t0 < 0.02:
                s.step(40, live["T"].get() / 1e3, live["W"].get() * 2 * math.pi, live["F"].get()); done += 40
        h.sync()
        d = s.d; a1 = -math.degrees(d.qpos[s.q1]); a2 = -math.degrees(d.qpos[s.q2]); st = "ЗАЕЛО" if s.slow > 0.15 else ("идёт" if s.mode != "stop" else "стоп")
        info.config(text=f"Тележка {d.qpos[s.qc]*1e3:7.2f} мм   {st}\nВал 1 {a1:7.1f}°  вал 2 {a2:7.1f}°  разница {a1-a2:5.1f}°\nМомент {abs(s.tq)*1e3:5.1f} мН·м   скорость счёта {done*s.m.opt.timestep/max(time.perf_counter()-t0,1e-3):.2f}× от реальной")
    root.after(5, tick)
root.after(100, open_viewer); root.after(300, tick); root.mainloop()
