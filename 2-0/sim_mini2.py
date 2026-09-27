# -*- coding: utf-8 -*-
"""Физика стенда v2 с шатуном (gitara_mini2.py): хватит ли мотора, не клинит ли, крутит ли палец мотор.

1) Квазистатика (формулы): момент на кривошипе, чтобы двигать ложе против пальца F, с трением
   μ = 0.3 (PETG по PETG) в шарнирах и в дырке ложа; угол передачи; сравнение со старым приводом
   (кривошип R4.8 + плечо 52:10 — ложе = 25·sin θ мм).
2) MuJoCo: четырёхзвенник как есть — кривошип (мотор = сервопривод с ограничением момента), шатун,
   плечо, ложе на ползуне; палец давит на ложе против хода. Ищем наименьший момент мотора, при
   котором он делает 3 полных оборота без срыва, и силу пальца, при которой он проворачивает
   мотор, стоящий на удержании.
Рисунков нет — только числа. Тяжёлое — на сервере: python sim_mini2.py
"""
import math

R, RS, LB, LC = 10.0, 18.0, 32.51, 34.87       # мм, из gitara_mini2.py
MY, CART_Y = 80.0, 16.0
AX = CART_Y + LB
MU, PIN_R = 0.3, 2.5                            # трение PETG, радиус стадов/пальцев
F = 3.0                                         # Н, палец давит на ложе против хода


def rocker(th):
    cx, cy = R * math.cos(th), MY + R * math.sin(th)
    dx, dy = cx, cy - AX
    d = math.hypot(dx, dy)
    a = (RS ** 2 - LC ** 2 + d ** 2) / (2 * d)
    h = math.sqrt(max(RS ** 2 - a ** 2, 0))
    px, py = a * dx / d, a * dy / d
    cands = [(px + h * dy / d, py - h * dx / d), (px - h * dy / d, py + h * dx / d)]
    sx, sy = max(cands, key=lambda q: q[0])
    return math.atan2(sy, sx), (cx, cy), (sx, AX + sy)


# ---------------- 1) квазистатика ----------------
N = 720
rows = []
for i in range(N):
    th = 2 * math.pi * i / N
    phi, (cx, cy), (sx, sy) = rocker(th)
    phi2, _, _ = rocker(th + 1e-5)
    dphi = (phi2 - phi) / 1e-5
    dx = LB * math.cos(phi) * dphi                          # мм/рад: ход ложа на радиан кривошипа
    lx, ly = sx - cx, sy - cy                               # шатун
    ux, uy = -(sy - AX), sx                                 # скорость стада плеча (перпендикуляр к RS)
    cosg = abs(lx * ux + ly * uy) / (LC * RS)               # косинус угла «шатун — скорость стада»
    gamma = 90 - math.degrees(math.acos(min(1, cosg)))      # угол передачи: шатун к плечу (90° — идеально)
    # трение: момент на плече от пальца + трение штыря в дырке ложа, сила в шатуне, трение шарниров
    m_arm = F * LB * abs(math.cos(phi)) + MU * F * LB * abs(math.sin(phi))           # Н·мм
    fl = m_arm / (RS * max(cosg, 1e-3))                     # Н, сила в шатуне
    t_ideal = F * abs(dx)                                   # Н·мм
    t_fric = t_ideal + MU * PIN_R * fl * 3 + MU * F * LB * abs(math.sin(phi)) * abs(dphi)
    rows.append((th, dx, gamma, t_ideal, t_fric, fl))

dx_max = max(abs(r[1]) for r in rows)
g_min = min(r[2] for r in rows)
t_max = max(r[4] for r in rows)
fl_max = max(r[5] for r in rows)
old_dx = 25.0                                               # старый привод: ложе = 25·sin θ, макс. 25 мм/рад
print("=== квазистатика (палец %.0f Н против хода, трение %.1f) ===" % (F, MU))
print("ход ложа на радиан кривошипа: макс %.1f мм/рад (старый привод: %.1f)" % (dx_max, old_dx))
print("угол передачи: минимум %.0f° (клин — если меньше ~17°, угла трения)" % g_min)
print("момент на кривошипе: без трения макс %.0f Н·мм, с трением макс %.0f Н·мм (%.3f Н·м)"
      % (max(r[3] for r in rows), t_max, t_max / 1000))
print("старый привод без трения: %.0f Н·мм" % (F * old_dx))
print("сила в шатуне: макс %.1f Н" % fl_max)
for deg in (0, 45, 90, 135, 180, 225, 270, 315):
    r = rows[int(deg / 360 * N)]
    print("  θ %3d°: ложе %+5.1f мм, ход %5.1f мм/рад, угол передачи %3.0f°, момент %4.0f Н·мм"
          % (deg, LB * math.sin(rocker(r[0])[0]), abs(r[1]), r[2], r[4]))

# ---------------- 2) MuJoCo ----------------
import mujoco
import numpy as np

m2 = 0.001                                                  # мм -> м


def xml(t_lim):
    return f"""
<mujoco>
  <compiler angle="radian"/>
  <option timestep="0.0001" gravity="0 0 0" integrator="implicitfast" iterations="200" tolerance="1e-12"/>
  <default><geom density="1270" contype="0" conaffinity="0"/><joint damping="0.00002"/></default>
  <worldbody>
    <body name="crank" pos="0 {MY*m2} 0">
      <joint name="crank" type="hinge" axis="0 0 1" frictionloss="{MU*PIN_R*m2*1.0}"/>
      <geom type="cylinder" size="{13.5*m2} {2.4*m2}"/>
      <body name="link" pos="{R*m2} 0 0">
        <joint name="link" type="hinge" axis="0 0 1" frictionloss="{MU*PIN_R*m2*1.0}"/>
        <geom type="box" size="{2.8*m2} {LC/2*m2} {0.8*m2}" pos="0 {LC/2*m2} 0"/>
        <site name="ls" pos="0 {LC*m2} 0"/>
      </body>
    </body>
    <body name="arm" pos="0 {AX*m2} 0">
      <joint name="arm" type="hinge" axis="0 0 1" frictionloss="{MU*PIN_R*m2*1.0}"/>
      <geom type="box" size="{2.5*m2} {LB/2*m2} {0.8*m2}" pos="0 {-LB/2*m2} 0"/>
      <geom type="box" size="{RS/2*m2} {2.5*m2} {0.8*m2}" pos="{RS/2*m2} 0 0"/>
      <site name="as" pos="{RS*m2} 0 0"/>
    </body>
  </worldbody>
  <equality>
    <connect site1="ls" site2="as" solref="0.0002 1" solimp="0.9999 0.9999 0.0001"/>   <!-- жёсткий шарнир: расхождение меряем ниже -->
  </equality>
  <actuator>
    <position name="motor" joint="crank" kp="5" kv="0.01" forcerange="{-t_lim} {t_lim}" ctrlrange="-100 100"/>
  </actuator>
</mujoco>"""


TRACE = []


def run(t_lim, turns=3, rps=1.0, force=F, hold=False):
    """Мотор тянет кривошип за целью (rps оборотов в секунду). Палец давит на ложе против скорости.
    Возвращает наибольшее отставание от цели (градусы) и ход ложа."""
    model = mujoco.MjModel.from_xml_string(xml(t_lim))
    data = mujoco.MjData(model)
    ja = model.joint("arm").qposadr[0]
    da = model.joint("arm").dofadr[0]
    jc = model.joint("crank").qposadr[0]
    jlk = model.joint("link").qposadr[0]
    phi0, (cx0, cy0), (sx0, sy0) = rocker(0.0)                  # начальная поза: кривошип 0°
    data.qpos[model.joint("arm").qposadr[0]] = phi0
    data.qpos[model.joint("link").qposadr[0]] = math.atan2(-(sx0 - cx0), sy0 - cy0)
    mujoco.mj_forward(model, data)
    lag, xs = 0.0, []
    TRACE.clear()
    T = turns / rps
    steps = int(T / model.opt.timestep)
    for i in range(steps):
        t = i * model.opt.timestep
        data.ctrl[0] = 0.0 if hold else 2 * math.pi * rps * t
        # палец давит на ложе вдоль хода — это момент на плече F·LB·cos φ (ложе x = LB·sin φ)
        ph, w = data.qpos[ja], data.qvel[da]
        arm_m = force * LB * m2 * math.cos(ph)
        # против хода: направление берём по геометрии (плечо мелко дрожит — по мгновенной скорости знак скачет)
        thc = data.qpos[jc]
        sgn = math.copysign(1, rocker(thc + 1e-4)[0] - rocker(thc - 1e-4)[0])
        data.qfrc_applied[da] = -arm_m if hold else -arm_m * sgn
        mujoco.mj_step(model, data)
        if not hold:
            lag = max(lag, math.degrees(abs(data.ctrl[0] - data.qpos[jc])))
        xs.append(LB * math.sin(data.qpos[ja]))
        TRACE.append((t, data.qpos[jc], data.qpos[ja], data.actuator_force[0], data.qpos[jlk],
                      float(np.linalg.norm(data.site("ls").xpos - data.site("as").xpos)) / m2))
    return lag, min(xs), max(xs), math.degrees(data.qpos[jc])


print("\n=== MuJoCo: мотор крутит 3 оборота за 3 с, палец %.0f Н против хода ===" % F)
lag, x0, x1, _ = run(1.0)
print("проверка модели (момент мотора не ограничен): ложе от %.1f до %.1f мм, отставание %.1f°" % (x0, x1, lag))
need = None
for t_lim in (0.2, 0.1, 0.07, 0.05, 0.04, 0.03, 0.025, 0.02, 0.015, 0.01):
    lag, x0, x1, _ = run(t_lim)
    ok = lag < 20
    print("  мотор %.3f Н·м: отставание макс %5.1f°  %s" % (t_lim, lag, "крутит" if ok else "СРЫВ"))
    if ok:
        need = t_lim
print("наименьший момент мотора, при котором крутит без срыва: %s Н·м" % (("%.3f" % need) if need else "больше 0.2"))

print("\n=== MuJoCo: мотор на удержании, палец давит на ложе — провернёт ли ===")
for t_hold in (0.02, 0.05):
    for fing in (2.0, 5.0, 10.0):
        _, _, _, ang = run(t_hold, turns=0.3, force=fing, hold=True)
        print("  удержание %.2f Н·м, палец %4.1f Н: кривошип ушёл на %5.1f°" % (t_hold, fing, abs(ang)))
