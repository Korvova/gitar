# -*- coding: utf-8 -*-
"""
Плата 4 моторов грифа, КОМПАКТНАЯ: заготовка 100 x 100, рисунок 65 x 89 мм.
ESP32 DevKit (30 ножек, ряды 25.4) + 4 драйвера S2209 V4 (TMC2209) + PD-триггер + конденсатор.
Односторонняя, медь B.Cu снизу, детали сверху. Рисунок — маркером 1 мм, потом травление.
Вид KiCad = вид со стороны деталей.

Компоновка: драйверы 0 и 1 — сверху (штыри моторов у верхнего края), ESP — посередине,
драйверы 2 и 3 — снизу, развёрнуты на 180 градусов (штыри моторов у нижнего края).
Справа — триггер (плашмя, Type-C к правому краю) и конденсатор. USB ESP тоже смотрит вправо.

Разводка в один слой: ряд ножек — стена, пройти можно только сквозь свою ножку.
Под каждым драйвером 4 полосы: A = GND, B = VM, D = VIO (под перемычки адреса), C = UART.
Справа вложенные петли соединяют верхний и нижний ряд: UART (внутри), VM, GND (снаружи).
Слева — петля VIO, в неё же приходит 3V3 из-под ESP. UART к D16 спускается сквозь ножку RX драйвера 1.
Перемычки: 3 адресные (MS -> полоса VIO, изолированный провод со стороны меди) и 1 GND к ESP (сверху).

Запуск: "%LOCALAPPDATA%\\Programs\\KiCad\\10.0\\bin\\python.exe" build_board.py
"""
import os
import pcbnew
from pcbnew import VECTOR2I_MM, FromMM

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "plata_4_motora.kicad_pcb")
KICAD = r"C:\Users\AdminPC\AppData\Local\Programs\KiCad\10.0\share\kicad"
FP_ROOT = os.path.join(KICAD, "footprints")

W, H = 92.0, 92.0
W_SIG, W_PWR = 1.2, 1.5
P = 2.54

X0, DRV_P = 5.0, 21.0            # ножка 1 драйвера 0; шаг драйверов в ряду
XE = X0 + 8.3                    # первая ножка рядов ESP (D23 сверху, EN снизу)
XB = XE                          # левая ножка нижних драйверов
# --- y, сверху вниз ---
Y_VIO_T, Y_HDR_T, Y_HOP_T, Y_T = 2.2, 6.4, 7.9, 11.4
Y_A, Y_B, Y_D, Y_C, Y_S = 14.3, 16.65, 19.0, 21.2, 24.1          # полосы под верхними драйверами, ряд сигналов
L1, L2 = 27.6, 29.8
YE_U, YE_L = 33.1, 58.5
L3, L4 = 61.8, 64.0
Y_S2, Y_C2, Y_D2, Y_B2, Y_A2, Y_T2 = 67.5, 70.4, 72.6, 74.95, 77.3, 80.2
Y_HOP_B, Y_HDR_B, Y_VIO_B = 83.7, 85.2, 89.4
# --- x, петли ---
X_VIO = 2.4
X_UART, X_VM, X_GND = 54.6, 57.0, 65.6
TRG_X = 60.0                     # левая колонка штырей триггера (вторая +2.54); пары VCC и GND через 17.78
X_JG = XE + 13 * P               # перемычка GND к ESP — над ножкой GND верхнего ряда

UP = ["D23", "D22", "TX0", "RX0", "D21", "D19", "D18", "D5", "D17", "D16", "D4", "D2", "D15", "GND", "3V3"]
LO = ["EN", "VP", "VN", "D34", "D35", "D32", "D33", "D25", "D26", "D27", "D14", "D12", "D13", "GND", "VIN"]
PINMAP = {"EN0": "D23", "STEP0": "D22", "DIR0": "D21", "EN1": "D19", "STEP1": "D4", "DIR1": "D2",
          "DIR2": "D32", "STEP2": "D33", "EN2": "D25", "DIR3": "D26", "STEP3": "D27", "EN3": "D14"}

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


def row(lib_name, ref, x1, y, names, value="", along=False):
    """Горизонтальный ряд, ножка 1 в (x1, y), дальше вправо; names — цепи по порядку слева направо.
    Площадки — овалы поперёк ряда (along=True — вдоль)."""
    n = len(names)
    fp = load_fp(*lib_name)
    fp.SetReference(ref)
    fp.SetValue(value)
    fp.SetPosition(VECTOR2I_MM(x1, y))
    fp.SetOrientationDegrees(90)
    board.Add(fp)
    if pad_xy(fp, n)[0] < x1:
        fp.SetOrientationDegrees(-90)
    assert pad_xy(fp, n) == (round(x1 + (n - 1) * P, 2), round(y, 2)), (ref, pad_xy(fp, n))
    for i, p in enumerate(sorted(fp.Pads(), key=lambda q: q.GetPosition().x)):
        p.SetShape(pcbnew.PAD_SHAPE_OVAL)
        p.SetSize(VECTOR2I_MM(1.6, 2.6) if along else VECTOR2I_MM(2.6, 1.6))
        p.SetDrillSize(VECTOR2I_MM(1.0, 1.0))
        if names[i]:
            p.SetNet(nets[names[i]])
    return fp


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


def text(s, x, y, size=1.4):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(s)
    t.SetPosition(VECTOR2I_MM(x, y))
    t.SetLayer(pcbnew.F_SilkS)
    t.SetTextSize(VECTOR2I_MM(size, size))
    t.SetTextThickness(FromMM(size * 0.15))
    board.Add(t)


def module_3d(ref, x, y, model, z, rot=0):
    fp = pcbnew.FOOTPRINT(board)
    fp.SetReference(ref)
    fp.Reference().SetVisible(False)
    fp.SetPosition(VECTOR2I_MM(x, y))
    m3 = pcbnew.FP_3DMODEL()
    m3.m_Filename = os.path.join(HERE, "models", model)
    m3.m_Offset = pcbnew.VECTOR3D(0, 0, z)
    m3.m_Rotation = pcbnew.VECTOR3D(0, 0, rot)
    fp.Models().push_back(m3)
    board.Add(fp)


def hole(ref, x, y, name, d=2.0, drill=1.0):
    fp = load_fp("Connector_PinHeader_2.54mm", "PinHeader_1x01_P2.54mm_Vertical")
    fp.SetReference(ref)
    fp.SetPosition(VECTOR2I_MM(x, y))
    board.Add(fp)
    p = fp.FindPadByNumber("1")
    p.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
    p.SetSize(VECTOR2I_MM(d, d))
    p.SetDrillSize(VECTOR2I_MM(drill, drill))
    p.SetNet(nets[name])
    fp.Models().clear()


SOCK8 = ("Connector_PinSocket_2.54mm", "PinSocket_1x08_P2.54mm_Vertical")
SOCK15 = ("Connector_PinSocket_2.54mm", "PinSocket_1x15_P2.54mm_Vertical")
HDR4 = ("Connector_PinHeader_2.54mm", "PinHeader_1x04_P2.54mm_Vertical")
HDR2 = ("Connector_PinHeader_2.54mm", "PinHeader_1x02_P2.54mm_Vertical")

# ================= верхние драйверы 0, 1 =================
# ряд мотора слева направо: VM GND A2 A1 B1 B2 VIO GND; ряд сигналов: EN MS1 MS2 TX RX CLK STEP DIR
for k in (0, 1):
    xk = X0 + DRV_P * k
    coil = ["M%d_%s" % (k, c) for c in ("A2", "A1", "B1", "B2")]
    row(SOCK8, "U%dT" % k, xk, Y_T, ["VM", "GND"] + coil + ["VIO", "GND"], "S2209")
    ms1 = "VIO" if k & 1 else None
    row(SOCK8, "U%dB" % k, xk, Y_S, ["EN%d" % k, ms1, None, "UART", "UART", None, "STEP%d" % k, "DIR%d" % k], "S2209")
    row(HDR4, "M%d" % k, xk + 2 * P, Y_HDR_T, coil, "мотор %d" % k)
    for j in range(4):
        x = xk + (2 + j) * P
        track(x, Y_HDR_T, x, Y_T, coil[j])
    track(xk, Y_T, xk, Y_B, "VM", W_PWR)
    route([(xk + P, Y_T), (xk + P, Y_A), (xk + 7 * P, Y_A), (xk + 7 * P, Y_T)], "GND")
    track(xk + 6 * P, Y_T, xk + 6 * P, Y_VIO_T, "VIO")
    for i in (3, 4):
        track(xk + i * P, Y_S, xk + i * P, Y_C, "UART")
    module_3d("DRV%d" % k, xk + 3.5 * P, (Y_T + Y_S) / 2, "s2209.step", 11.0)
    text("M%d" % k, xk + 0.5, Y_HDR_T - 1.0, 1.4)
# GND к соседу: дугой над ножкой VM драйвера 1
route([(X0 + 7 * P, Y_T), (X0 + 7 * P, Y_HOP_T), (X0 + DRV_P + P, Y_HOP_T), (X0 + DRV_P + P, Y_T)], "GND")

# ================= нижние драйверы 2, 3 (развёрнуты на 180) =================
# ряд сигналов слева направо: DIR STEP CLK RX TX MS2 MS1 EN; ряд мотора: GND VIO B2 B1 A1 A2 GND VM
for k in (2, 3):
    xk = XB + DRV_P * (k - 2)
    coil = ["M%d_%s" % (k, c) for c in ("B2", "B1", "A1", "A2")]
    ms2 = "VIO" if k & 2 else None
    ms1 = "VIO" if k & 1 else None
    row(SOCK8, "U%dB" % k, xk, Y_S2, ["DIR%d" % k, "STEP%d" % k, None, "UART", "UART", ms2, ms1, "EN%d" % k], "S2209")
    row(SOCK8, "U%dT" % k, xk, Y_T2, ["GND", "VIO"] + coil + ["GND", "VM"], "S2209")
    row(HDR4, "M%d" % k, xk + 2 * P, Y_HDR_B, coil, "мотор %d" % k)
    for j in range(4):
        x = xk + (2 + j) * P
        track(x, Y_T2, x, Y_HDR_B, coil[j])
    track(xk + 7 * P, Y_T2, xk + 7 * P, Y_B2, "VM", W_PWR)
    route([(xk, Y_T2), (xk, Y_A2), (xk + 6 * P, Y_A2), (xk + 6 * P, Y_T2)], "GND")
    track(xk + P, Y_T2, xk + P, Y_VIO_B, "VIO")
    for i in (3, 4):
        track(xk + i * P, Y_S2, xk + i * P, Y_C2, "UART")
    if k == 3:
        track(xk + 5 * P, Y_S2, xk + 6 * P, Y_S2, "VIO")
    module_3d("DRV%d" % k, xk + 3.5 * P, (Y_T2 + Y_S2) / 2, "s2209.step", 11.0, 180)
    text("M%d" % k, xk + 7 * P - 0.5, Y_HDR_B + 1.0, 1.4)
# GND к соседу: дугой под ножкой VM драйвера 2
route([(XB + 6 * P, Y_T2), (XB + 6 * P, Y_HOP_B), (XB + DRV_P, Y_HOP_B), (XB + DRV_P, Y_T2)], "GND")

# ================= полосы и петли =================
track(X0 + 3 * P, Y_C, X_UART, Y_C, "UART")                                # C верх
route([(X_UART, Y_C), (X_UART, Y_C2), (XB + 3 * P, Y_C2)], "UART")         # петля UART, C низ
track(X0, Y_B, TRG_X + P, Y_B, "VM", W_PWR)                                # B верх -> штыри VCC триггера
route([(X_VM, Y_B), (X_VM, Y_B2), (XB + 7 * P, Y_B2)], "VM", W_PWR)        # петля VM, B низ
route([(X0 + DRV_P + 7 * P, Y_A), (X_GND, Y_A), (X_GND, Y_HOP_B),
       (XB + DRV_P + 6 * P, Y_HOP_B), (XB + DRV_P + 6 * P, Y_T2)], "GND")  # петля GND снаружи
# VIO: верхняя шина, левая вертикаль, нижняя шина; полосы D под перемычки адреса; 3V3 из-под ESP
route([(X0 + DRV_P + 6 * P, Y_VIO_T), (X_VIO, Y_VIO_T), (X_VIO, Y_VIO_B), (XB + DRV_P + P, Y_VIO_B)], "VIO")
track(X_VIO, Y_D, X0 + DRV_P + P, Y_D, "VIO")
track(X_VIO, Y_D2, XB + DRV_P + 6 * P, Y_D2, "VIO")
X3V3 = XE + 14 * P
route([(X_VIO, 46.0), (X3V3, 46.0), (X3V3, YE_U)], "VIO")

# ================= ESP =================
up_nets = [None] * 15
lo_nets = [None] * 15
for sig, pin in PINMAP.items():
    if pin in UP:
        up_nets[UP.index(pin)] = sig
    else:
        lo_nets[LO.index(pin)] = sig
up_nets[UP.index("D16")] = "UART"
up_nets[UP.index("D17")] = "TX2R"
up_nets[UP.index("3V3")] = "VIO"
up_nets[UP.index("GND")] = "GND"
row(SOCK15, "ESP_UP", XE, YE_U, up_nets, "ESP32 D23..3V3")
row(SOCK15, "ESP_LO", XE, YE_L, lo_nets, "ESP32 EN..VIN")
module_3d("ESP", XE - 7.5 + 25.75, (YE_U + YE_L) / 2, "esp32_devkit30.step", 11.0)


def ex(name, names=UP):
    return XE + names.index(name) * P


def lane(sig, xs, ys, y, xd, yd):
    route([(xs, ys), (xs, y), (xd, y), (xd, yd)], sig)


def jog(sig, xs, ys, xd, yd, d):
    """Почти прямо: короткая диагональ сразу у ножки-источника."""
    s = 1 if yd > ys else -1
    route([(xs, ys), (xs, ys + s * d), (xd, ys + s * (d + abs(xd - xs))), (xd, yd)], sig)


# верх: EN0 S0 D0 EN1 [UART] S1 D1
lane("EN0", X0, Y_S, L1, ex("D23"), YE_U)
lane("STEP0", X0 + 6 * P, Y_S, L1, ex("D22"), YE_U)
jog("DIR0", X0 + 7 * P, Y_S, ex("D21"), YE_U, 2.0)
assert abs(X0 + DRV_P - ex("D19")) < 0.01
track(X0 + DRV_P, Y_S, ex("D19"), YE_U, "EN1")
lane("STEP1", X0 + DRV_P + 6 * P, Y_S, L1, ex("D4"), YE_U)
lane("DIR1", X0 + DRV_P + 7 * P, Y_S, L2, ex("D2"), YE_U)
# UART к D16 — сквозь ножку RX драйвера 1, прямо вниз
assert abs(X0 + DRV_P + 4 * P - ex("D16")) < 0.01
track(ex("D16"), Y_S, ex("D16"), YE_U, "UART")
# резистор 1 кОм под ESP: D17 -> R -> UART
xr = ex("D17")
res = load_fp("Resistor_THT", "R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal")
res.SetReference("R1")
res.SetValue("1k")
res.SetPosition(VECTOR2I_MM(xr, YE_U + 4.0))
board.Add(res)
assert pad_xy(res, 2) == (round(xr + 7.62, 2), round(YE_U + 4.0, 2)), pad_xy(res, 2)
for num, name in (("1", "TX2R"), ("2", "UART")):
    pd = res.FindPadByNumber(num)
    pd.SetNet(nets[name])
    pd.SetSize(VECTOR2I_MM(2.0, 2.0))
    pd.SetDrillSize(VECTOR2I_MM(0.9, 0.9))
track(xr, YE_U, xr, YE_U + 4.0, "TX2R")
route([(ex("D16"), YE_U), (ex("D16"), YE_U + 7.0), (xr + 7.62, YE_U + 7.0), (xr + 7.62, YE_U + 4.0)], "UART")

# низ: DIR2 S2 EN2 DIR3 S3 EN3
lane("DIR2", XB, Y_S2, L3, ex("D32", LO), YE_L)
lane("STEP2", XB + P, Y_S2, L4, ex("D33", LO), YE_L)
assert abs(XB + 7 * P - ex("D25", LO)) < 0.01
track(XB + 7 * P, Y_S2, ex("D25", LO), YE_L, "EN2")
jog("DIR3", XB + DRV_P, Y_S2, ex("D26", LO), YE_L, 2.0)
jog("STEP3", XB + DRV_P + P, Y_S2, ex("D27", LO), YE_L, 2.0)
lane("EN3", XB + DRV_P + 7 * P, Y_S2, L4, ex("D14", LO), YE_L)

# GND к ESP — перемычка сверху: от дуги у драйвера 1 к ножке GND верхнего ряда
hole("JG1", X_JG, Y_HOP_T + 0.5, "GND")
hole("JG2", X_JG, YE_U - 3.8, "GND")
route([(X0 + DRV_P + 7 * P, Y_T), (X0 + DRV_P + 7 * P, Y_HOP_T + 0.5), (X_JG, Y_HOP_T + 0.5)], "GND")
track(X_JG, YE_U - 3.8, X_JG, YE_U, "GND")

# ================= триггер и конденсатор =================
tv = row(HDR2, "TRG_VCC", TRG_X, Y_B, ["VM", "VM"], "триггер VCC", along=True)
tg = row(HDR2, "TRG_GND", TRG_X, Y_B + 17.78, ["GND", "GND"], "триггер GND", along=True)
for fp_ in (tv, tg):
    fp_.Models().clear()
route([(TRG_X, Y_B + 17.78), (X_GND, Y_B + 17.78)], "GND")
module_3d("TRG", TRG_X - 1.27 + 15.0, Y_B + 8.89, "pd_trigger.step", 0.0, 180)

cap = load_fp("Capacitor_THT", "CP_Radial_D10.0mm_P5.00mm")
cap.SetReference("C1")
cap.SetValue("470u 35V")
cap.SetPosition(VECTOR2I_MM(X_VM, 64.5))
board.Add(cap)
if pad_xy(cap, 2) != (round(X_VM + 5.0, 2), 64.5):
    cap.SetOrientationDegrees(180)
assert pad_xy(cap, 2) == (round(X_VM + 5.0, 2), 64.5), pad_xy(cap, 2)
for num, name in (("1", "VM"), ("2", "GND")):
    pd = cap.FindPadByNumber(num)
    pd.SetNet(nets[name])
    pd.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
    pd.SetSize(VECTOR2I_MM(2.0, 2.0))
    pd.SetDrillSize(VECTOR2I_MM(1.0, 1.0))
track(X_VM + 5.0, 64.5, X_GND, 64.5, "GND")


# ================= перемычки на слое пользователя =================
def user_line(x1, y1, x2, y2):
    ln = pcbnew.PCB_SHAPE(board)
    ln.SetShape(pcbnew.SHAPE_T_SEGMENT)
    ln.SetStart(VECTOR2I_MM(x1, y1))
    ln.SetEnd(VECTOR2I_MM(x2, y2))
    ln.SetLayer(pcbnew.Dwgs_User)
    ln.SetWidth(FromMM(0.6))
    board.Add(ln)


user_line(X0 + DRV_P + P, Y_S, X0 + DRV_P + P, Y_D)              # MS1 драйвера 1
user_line(XB + 5 * P, Y_S2, XB + 5 * P, Y_D2)                    # MS2 драйвера 2
user_line(XB + DRV_P + 6 * P, Y_S2, XB + DRV_P + 6 * P, Y_D2)    # MS1+MS2 драйвера 3
user_line(X_JG, Y_HOP_T + 0.5, X_JG, YE_U - 3.8)                 # GND к ESP

rect = pcbnew.PCB_SHAPE(board)
rect.SetShape(pcbnew.SHAPE_T_RECT)
rect.SetStart(VECTOR2I_MM(0, 0))
rect.SetEnd(VECTOR2I_MM(W, H))
rect.SetLayer(pcbnew.Edge_Cuts)
rect.SetWidth(FromMM(0.1))
board.Add(rect)

ds = board.GetDesignSettings()
ds.m_MinClearance = FromMM(0.7)
ds.m_TrackMinWidth = FromMM(1.0)
ds.m_CopperEdgeClearance = FromMM(1.0)
nc = ds.m_NetSettings.GetDefaultNetclass()
nc.SetClearance(FromMM(0.7))
nc.SetTrackWidth(FromMM(W_SIG))

pcbnew.SaveBoard(OUT, board)
print("saved:", OUT, " плата %.0f x %.0f" % (W, H))
for sig, pin in PINMAP.items():
    print("%-6s %s" % (sig, pin))
print("UART: D16 прямо, D17 через 1 кОм; адрес драйвера = номер мотора. Дорожек:", len(board.GetTracks()))
