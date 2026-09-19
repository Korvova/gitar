# -*- coding: utf-8 -*-
"""
Плата 4 моторов грифа: ESP32 DevKit (30 ножек, ряды 25.4) + 4 драйвера S2209 V4 (TMC2209).
Односторонняя, медь B.Cu снизу, детали сверху. Рисунок — маркером 1 мм, потом травление.
Вид KiCad = вид со стороны деталей.

Идея разводки без перемычек по питанию и сигналам:
  ряд ножек модуля — это стена, пройти можно только сквозь СВОЮ ножку;
  VM   — шина под драйверами (полоса B), ножка 1 вниз;
  GND  — цепочка: под драйвером от ножки 2 до 8 (полоса A), к соседу — дугой над его ножкой VM;
  VIO  — шина вдоль верхнего края, слева спускается в полосу D под драйверами, справа уходит к 3V3 ESP;
  UART — полоса C под драйверами (TX и RX каждого драйвера вместе), справа спускается к D16, к D17 через 1 кОм;
  EN/STEP/DIR — свои у каждого мотора: моторы 0 и 1 обходят ESP слева к нижнему ряду, 2 и 3 — в верхний ряд.
Остаются 3 перемычки адреса (MS1/MS2 -> полоса D): изолированный провод со стороны меди.

Запуск: "%LOCALAPPDATA%\\Programs\\KiCad\\10.0\\bin\\python.exe" build_board.py
"""
import os
import pcbnew
from pcbnew import VECTOR2I_MM, FromMM

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "plata_4_motora.kicad_pcb")
KICAD = r"C:\Users\AdminPC\AppData\Local\Programs\KiCad\10.0\share\kicad"
FP_ROOT = os.path.join(KICAD, "footprints")

W, H = 141.0, 90.0
W_SIG, W_PWR = 1.2, 1.5
PITCH = 2.54

# ---- драйверы ----
X0, DRV_P = 22.0, 22.86          # ножка 1 драйвера 0, шаг драйверов
Y_T, Y_B = 20.0, 32.7            # ряд мотора (VM GND A2 A1 B1 B2 VIO GND) и ряд сигналов (EN MS1 MS2 TX RX CLK STEP DIR)
Y_HDR = 7.0                      # штыри моторов
Y_VIO_TOP = 2.2
Y_HOP = 16.5                     # дуга GND над ножкой VM соседа
Y_A, Y_BUS, Y_D, Y_C = 22.9, 25.25, 27.6, 29.8   # полосы под драйвером: GND, VM, VIO, UART
# ---- ESP ----
XE, YE = 97.5, 54.0              # первая ножка верхнего ряда (D23); нижний ряд на YE + 25.4
UP = ["D23", "D22", "TX0", "RX0", "D21", "D19", "D18", "D5", "D17", "D16", "D4", "D2", "D15", "GND", "3V3"]
LO = ["EN", "VP", "VN", "D34", "D35", "D32", "D33", "D25", "D26", "D27", "D14", "D12", "D13", "GND", "VIN"]
# кто на какой ножке ESP (для прошивки)
PINMAP = {"EN0": "D32", "STEP0": "D33", "DIR0": "D25", "EN1": "D26", "STEP1": "D27", "DIR1": "D14",
          "EN2": "D23", "STEP2": "D22", "DIR2": "D21", "EN3": "D19", "STEP3": "D18", "DIR3": "D5"}
TRG_X, TRG_GND_Y = 112.0, 7.47                    # триггер справа: пары штырей GND и VCC, между ними 17.78
X_GNDR, Y_GNDB = 136.0, 83.5                      # GND к ESP: по правому краю вниз и вдоль нижнего края
# полосы между драйверами и ESP; все дорожки идут вправо, поэтому левая — ниже
LANES = {"DIR3": 38.0, "STEP3": 40.2, "EN3": 42.4, "DIR2": 44.6, "STEP2": 46.8, "EN2": 49.0}
WRAP = {"DIR1": 63.6, "STEP1": 65.8, "EN1": 68.0, "DIR0": 70.2, "STEP0": 72.4, "EN0": 74.6}  # полосы под ESP

board = pcbnew.NewBoard(OUT)
CU = pcbnew.B_Cu

NET_NAMES = ["VM", "GND", "VIO", "UART", "TX2R"] + list(PINMAP) + \
            ["M%d_%s" % (k, c) for k in range(4) for c in ("A2", "A1", "B1", "B2")]
nets = {}
for n in NET_NAMES:
    ni = pcbnew.NETINFO_ITEM(board, n)
    board.Add(ni)
    nets[n] = ni


def load_fp(lib, name):
    fp = pcbnew.FootprintLoad(os.path.join(FP_ROOT, lib + ".pretty"), name)
    assert fp is not None, "нет футпринта: %s/%s" % (lib, name)
    return fp


def pad_xy(fp, num):
    pos = fp.FindPadByNumber(str(num)).GetPosition()
    return (round(pcbnew.ToMM(pos.x), 2), round(pcbnew.ToMM(pos.y), 2))


def row(lib_name, ref, x1, y, n, value=""):
    """Горизонтальный ряд: ножка 1 в (x1, y), дальше вправо. Площадки — овалы поперёк ряда."""
    fp = load_fp(*lib_name)
    fp.SetReference(ref)
    fp.SetValue(value)
    fp.SetPosition(VECTOR2I_MM(x1, y))
    fp.SetOrientationDegrees(90)
    board.Add(fp)
    if pad_xy(fp, n)[0] < x1:
        fp.SetOrientationDegrees(-90)
    assert pad_xy(fp, n) == (round(x1 + (n - 1) * PITCH, 2), round(y, 2)), (ref, pad_xy(fp, n))
    for p in fp.Pads():
        p.SetShape(pcbnew.PAD_SHAPE_OVAL)
        p.SetSize(VECTOR2I_MM(2.6, 1.6))          # в осях футпринта; после поворота длинная ось — поперёк ряда
        p.SetDrillSize(VECTOR2I_MM(1.0, 1.0))
    return fp


def net(fp, num, name):
    fp.FindPadByNumber(str(num)).SetNet(nets[name])


def track(x1, y1, x2, y2, name, w=W_SIG):
    t = pcbnew.PCB_TRACK(board)
    t.SetStart(VECTOR2I_MM(x1, y1))
    t.SetEnd(VECTOR2I_MM(x2, y2))
    t.SetWidth(FromMM(w))
    t.SetLayer(CU)
    t.SetNet(nets[name])
    board.Add(t)


def route(pts, name, w=W_SIG):
    for a, b in zip(pts, pts[1:]):
        track(a[0], a[1], b[0], b[1], name, w)


def text(s, x, y, size=1.5, layer=pcbnew.F_SilkS):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(s)
    t.SetPosition(VECTOR2I_MM(x, y))
    t.SetLayer(layer)
    t.SetTextSize(VECTOR2I_MM(size, size))
    t.SetTextThickness(FromMM(size * 0.15))
    board.Add(t)


SOCK8 = ("Connector_PinSocket_2.54mm", "PinSocket_1x08_P2.54mm_Vertical")
SOCK15 = ("Connector_PinSocket_2.54mm", "PinSocket_1x15_P2.54mm_Vertical")
HDR4 = ("Connector_PinHeader_2.54mm", "PinHeader_1x04_P2.54mm_Vertical")


def add_model(fp, path, off=(0, 0, 0), rot=(0, 0, 0)):
    m = pcbnew.FP_3DMODEL()
    m.m_Filename = path
    m.m_Offset = pcbnew.VECTOR3D(*off)
    m.m_Rotation = pcbnew.VECTOR3D(*rot)
    fp.Models().push_back(m)


def module_3d(ref, x, y, model):
    fp = pcbnew.FOOTPRINT(board)
    fp.SetReference(ref)
    fp.Reference().SetVisible(False)
    fp.SetPosition(VECTOR2I_MM(x, y))
    add_model(fp, os.path.join(HERE, "models", model), off=(0, 0, 11.0))   # гнездо 8.5 + посадка штыря
    board.Add(fp)


# ================= драйверы =================
T_NETS = ["VM", "GND", None, None, None, None, "VIO", "GND"]     # ряд мотора, ножки 3..6 — свои у каждого
B_NETS = [None, None, None, "UART", "UART", None, None, None]    # ряд сигналов
COIL = ["A2", "A1", "B1", "B2"]
for k in range(4):
    xk = X0 + DRV_P * k
    t = row(SOCK8, "U%dT" % k, xk, Y_T, 8, "S2209")
    b = row(SOCK8, "U%dB" % k, xk, Y_B, 8, "S2209")
    h = row(HDR4, "M%d" % k, xk + 2 * PITCH, Y_HDR, 4, "мотор %d" % k)
    for i in range(8):
        if T_NETS[i]:
            net(t, i + 1, T_NETS[i])
        if B_NETS[i]:
            net(b, i + 1, B_NETS[i])
    for j, c in enumerate(COIL):
        net(t, 3 + j, "M%d_%s" % (k, c))
        net(h, 1 + j, "M%d_%s" % (k, c))
        x = xk + (2 + j) * PITCH
        track(x, Y_HDR, x, Y_T, "M%d_%s" % (k, c))
    net(b, 1, "EN%d" % k)
    net(b, 7, "STEP%d" % k)
    net(b, 8, "DIR%d" % k)
    # адрес по UART = MS2:MS1, единицы — перемычкой на полосу D (VIO)
    if k & 1:
        net(b, 2, "VIO")
    if k & 2:
        net(b, 3, "VIO")
    if k == 3:
        track(xk + PITCH, Y_B, xk + 2 * PITCH, Y_B, "VIO")

    # VM: ножка 1 вниз в шину
    track(xk, Y_T, xk, Y_BUS, "VM", W_PWR)
    # GND: полоса A между ножками 2 и 8
    route([(xk + PITCH, Y_T), (xk + PITCH, Y_A), (xk + 7 * PITCH, Y_A), (xk + 7 * PITCH, Y_T)], "GND")
    # GND к соседу: дугой над его ножкой VM
    if k < 3:
        route([(xk + 7 * PITCH, Y_T), (xk + 7 * PITCH, Y_HOP), (xk + DRV_P + PITCH, Y_HOP),
               (xk + DRV_P + PITCH, Y_T)], "GND")
    # VIO: ножка 7 вверх в верхнюю шину
    track(xk + 6 * PITCH, Y_T, xk + 6 * PITCH, Y_VIO_TOP, "VIO")
    # UART: TX и RX вверх в полосу C
    for i in (3, 4):
        track(xk + i * PITCH, Y_B, xk + i * PITCH, Y_C, "UART")
    module_3d("DRV%d" % k, xk + 3.5 * PITCH, (Y_T + Y_B) / 2, "s2209.step")
    text("M%d" % k, xk + 3.5 * PITCH, 3.4, 1.6)
    text("чёрный", xk + 0.3 * PITCH, Y_HDR + 3.0, 1.0)

X3 = X0 + DRV_P * 3
# шины под драйверами: VM от триггера (справа) до драйвера 0, UART — до спуска к D16
track(X0, Y_BUS, TRG_X + PITCH, Y_BUS, "VM", W_PWR)
track(X0 + 3 * PITCH, Y_C, XE + UP.index("D16") * PITCH, Y_C, "UART")
# VIO: верхняя шина -> слева вниз -> полоса D под всеми драйверами -> справа вниз к 3V3
route([(X3 + 6 * PITCH, Y_VIO_TOP), (2.2, Y_VIO_TOP), (2.2, Y_D), (XE + UP.index("3V3") * PITCH, Y_D)], "VIO")

# ================= питание: PD-триггер (фиолетовый, 30x20) штырями насквозь, Type-C к правому краю =================
HDR2 = ("Connector_PinHeader_2.54mm", "PinHeader_1x02_P2.54mm_Vertical")
tg = row(HDR2, "TRG_GND", TRG_X, TRG_GND_Y, 2, "триггер GND")
tv = row(HDR2, "TRG_VCC", TRG_X, Y_BUS, 2, "триггер VCC")
for fp_, name in ((tg, "GND"), (tv, "VM")):
    for n in (1, 2):
        net(fp_, n, name)
    for pd in fp_.Pads():
        pd.SetSize(VECTOR2I_MM(1.6, 2.6))          # овал вдоль шины: под ним проходит полоса VIO
track(TRG_X, TRG_GND_Y, TRG_X + PITCH, TRG_GND_Y, "GND")
# GND: в цепочку драйверов через ножку 8 драйвера 3 и по правому краю вниз — к ESP
route([(TRG_X, TRG_GND_Y), (X3 + 7 * PITCH, TRG_GND_Y), (X3 + 7 * PITCH, Y_T)], "GND")
route([(TRG_X + PITCH, TRG_GND_Y), (X_GNDR, TRG_GND_Y), (X_GNDR, Y_GNDB)], "GND")
fp3 = pcbnew.FOOTPRINT(board)
fp3.SetReference("TRG")
fp3.Reference().SetVisible(False)
fp3.SetPosition(VECTOR2I_MM(TRG_X - 1.27 + 15.0, (TRG_GND_Y + Y_BUS) / 2))
add_model(fp3, os.path.join(HERE, "models", "pd_trigger.step"), off=(0, 0, 2.5), rot=(0, 0, 180))
board.Add(fp3)
text("12V", 126.0, 30.5, 1.6)

# конденсатор — на левом конце шины VM
cap = load_fp("Capacitor_THT", "CP_Radial_D10.0mm_P5.00mm")
cap.SetReference("C1")
cap.SetValue("470u 35V")
CX = 13.0
cap.SetPosition(VECTOR2I_MM(CX, Y_BUS))
cap.SetOrientationDegrees(90)
board.Add(cap)
if pad_xy(cap, 2) != (CX, round(Y_BUS - 5.0, 2)):
    cap.SetOrientationDegrees(-90)
assert pad_xy(cap, 2) == (CX, round(Y_BUS - 5.0, 2)), pad_xy(cap, 2)
for num, name in (("1", "VM"), ("2", "GND")):
    pd = cap.FindPadByNumber(num)
    pd.SetNet(nets[name])
    pd.SetShape(pcbnew.PAD_SHAPE_OVAL)
    pd.SetSize(VECTOR2I_MM(1.6, 2.4))              # после поворота длинная ось — вдоль шины
    pd.SetDrillSize(VECTOR2I_MM(1.0, 1.0))
track(CX, Y_BUS, X0, Y_BUS, "VM", W_PWR)
route([(CX, Y_BUS - 5.0), (CX, Y_HOP), (X0 + PITCH, Y_HOP), (X0 + PITCH, Y_T)], "GND")

# ================= ESP =================
up = row(SOCK15, "ESP_UP", XE, YE, 15, "ESP32 D23..3V3")
lo = row(SOCK15, "ESP_LO", XE, YE + 25.4, 15, "ESP32 EN..VIN")
module_3d("ESP", XE - 7.5 + 25.75, YE + 12.7, "esp32_devkit30.step")


def ex(name, names=UP):
    return XE + names.index(name) * PITCH


for sig, pin in PINMAP.items():
    if pin in UP:
        net(up, UP.index(pin) + 1, sig)
    else:
        net(lo, LO.index(pin) + 1, sig)
net(up, UP.index("D16") + 1, "UART")
net(up, UP.index("D17") + 1, "TX2R")
net(up, UP.index("3V3") + 1, "VIO")
net(lo, LO.index("GND") + 1, "GND")


def src(sig):
    k = int(sig[-1])
    i = {"EN": 0, "STEP": 6, "DIR": 7}[sig[:-1]]
    return X0 + DRV_P * k + i * PITCH


# моторы 2 и 3 — в верхний ряд ESP
for sig, y in LANES.items():
    xs, xd = src(sig), ex(PINMAP[sig])
    route([(xs, Y_B), (xs, y), (xd, y), (xd, YE)], sig)
# UART: из полосы C прямо вниз к D16, под ESP через резистор к D17
xd = ex("D16")
track(xd, Y_C, xd, YE, "UART")
xr = ex("D17")
res = load_fp("Resistor_THT", "R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal")
res.SetReference("R1")
res.SetValue("1k")
res.SetPosition(VECTOR2I_MM(xr, YE + 4.0))
board.Add(res)
assert pad_xy(res, 2) == (round(xr + 7.62, 2), round(YE + 4.0, 2)), pad_xy(res, 2)
for num, name in (("1", "TX2R"), ("2", "UART")):
    p = res.FindPadByNumber(num)
    p.SetNet(nets[name])
    p.SetSize(VECTOR2I_MM(2.0, 2.0))
    p.SetDrillSize(VECTOR2I_MM(0.9, 0.9))
track(xr, YE, xr, YE + 4.0, "TX2R")
route([(xd, YE), (xd, YE + 7.0), (xr + 7.62, YE + 7.0), (xr + 7.62, YE + 4.0)], "UART")
# VIO и GND к ESP
xd = ex("3V3")
track(xd, Y_D, xd, YE, "VIO")
xg = ex("GND", LO)
route([(X_GNDR, Y_GNDB), (xg, Y_GNDB), (xg, YE + 25.4)], "GND")
# моторы 0 и 1 — в обход ESP слева, к нижнему ряду
for sig, y in WRAP.items():
    xs, xd = src(sig), ex(PINMAP[sig], LO)
    route([(xs, Y_B), (xs, y), (xd, y), (xd, YE + 25.4)], sig)

# ================= перемычки адреса (рисуются на слое пользователя, в меди их нет) =================
for k in (1, 2, 3):
    xk = X0 + DRV_P * k
    xm = xk + (PITCH if k & 1 else 2 * PITCH)
    ln = pcbnew.PCB_SHAPE(board)
    ln.SetShape(pcbnew.SHAPE_T_SEGMENT)
    ln.SetStart(VECTOR2I_MM(xm, Y_B))
    ln.SetEnd(VECTOR2I_MM(xm, Y_D))
    ln.SetLayer(pcbnew.Dwgs_User)
    ln.SetWidth(FromMM(0.6))
    board.Add(ln)

# ================= крепёж и контур =================
for i, (x, y) in enumerate(((7.0, 8.0), (137.0, 3.6), (6.0, 85.5), (120.0, 86.3))):
    fp = load_fp("MountingHole", "MountingHole_3.2mm_M3")
    fp.SetReference("H%d" % (i + 1))
    fp.SetPosition(VECTOR2I_MM(x, y))
    board.Add(fp)

rect = pcbnew.PCB_SHAPE(board)
rect.SetShape(pcbnew.SHAPE_T_RECT)
rect.SetStart(VECTOR2I_MM(0, 0))
rect.SetEnd(VECTOR2I_MM(W, H))
rect.SetLayer(pcbnew.Edge_Cuts)
rect.SetWidth(FromMM(0.1))
board.Add(rect)

# правила под маркер 1 мм
ds = board.GetDesignSettings()
ds.m_MinClearance = FromMM(0.7)
ds.m_TrackMinWidth = FromMM(1.0)
ds.m_CopperEdgeClearance = FromMM(1.0)
nc = ds.m_NetSettings.GetDefaultNetclass()
nc.SetClearance(FromMM(0.7))
nc.SetTrackWidth(FromMM(W_SIG))

pcbnew.SaveBoard(OUT, board)
print("saved:", OUT, " плата %.0f x %.0f" % (W, H))
print("\n--- ножки ESP для прошивки ---")
for sig, pin in PINMAP.items():
    print("%-6s %s" % (sig, pin))
print("UART: D16 прямо, D17 через 1 кОм; адреса драйверов 0..3 = номер мотора")
print("дорожек:", len(board.GetTracks()))
