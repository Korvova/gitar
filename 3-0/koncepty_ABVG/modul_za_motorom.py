# -*- coding: utf-8 -*-
r"""Один модуль концепта В: тележка ЦЕЛИКОМ за краем своего мотора (владелец 19.11). Рейка тележки цепляет шестерни у края мотора,
сама тележка и площадка уходят вперёд за мотор, лежат на балке-хвосте, которая стоит за мотором на колоннах по краям;
крючки «Г» тележки обнимают балку — не поднимается. Над своим мотором тележки нет.
Запуск: ..\..\2-0\.venv-b123d\Scripts\python modul_za_motorom.py
"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from build123d import *
import ryad_V4b as V
K, T, R = V.K, V.T, V.R
os.chdir(HERE); os.makedirs("asm_zm", exist_ok=True)
BB, CZ, PX, rack = T.BB, T.CZ, T.prof_x, T.rack
S, A, RF, RM, YM, CW, HALF, L2 = T.S, T.A, T.RF, T.RM, T.YM, T.CW, T.HALF, T.L2
DED, C = K.DED, 0.2
W = 15.0
Y_MOT0 = YM - 13.9                                                                 # передний край мотора (1.6)
Y_P1 = Y_MOT0                                                                      # площадка целиком перед мотором
Y_P0 = Y_P1 - W
ZB, ZT = L2[1] + 0.15, R.Z_PD1                                                     # низ и верх тележки
# балка-хвост за мотором (под серединой площадки), колонны по краям
Y_BC = (Y_P0 + Y_P1) / 2
BM_B, BM_T = 3.0, 5.0
beam = PX([(Y_BC - BM_B / 2, L2[0]), (Y_BC + BM_B / 2, L2[0]), (Y_BC + BM_T / 2, L2[1]), (Y_BC - BM_T / 2, L2[1])], -HALF, HALF)
base = V.base_o + BB(-HALF, HALF, Y_P0 - 1.0, Y_MOT0 + 0.01 - 1.1, 0, T.Z_FL)     # пол вперёд под балку
# клик (19.11, владелец): балка + 2 колонны = одна деталь; колонны стоят на круглых кнопках Ø6 в стаканах на полу
BTN_D, BTN_H, BTN_HP, BTN_DP = 6.4, 3.5, 1.5, 2.6                                # кнопка: корпус Ø6.4 (19.11 печать: оказалась толще 6), шток Ø2.6, всего 5
XCB, R_P = {"1": 20.0, "8": 14.7}.get(os.environ.get("OKANT", ""), 20.8), BTN_D / 2 + 0.15                                               # центр стакана; гнездо Ø6.7 (+0.4 после печати)
CUP_R = 4.15                                                                     # наружу не растёт (край основания 25), стенка 0.8
T_BAR = float(os.environ.get("T_BAR", "11.0"))                                     # перекладина «Т»: высота (19.11: поднять вдоль колонны)
T_IN = float(os.environ.get("T_IN", "5.0"))                                       # стенки стакана выше штока (19.11: +2, не выше — кнопку удобно класть)
CUP_H = BTN_H + BTN_HP + T_IN                                                   # стенки стакана выше штока на 3 — «Т» глубоко в пазах
KMODE = os.environ.get("KLAV", "0")
KLAV = KMODE == "1"                                                              # 19.11: «модуль-клавиша» — кнопка Ø6 на раме под полом, «Т» вклеена в стакан
KLAV2 = KMODE == "2"                                                             # 19.11 (владелец): SMD-кнопки 5.2×5.2×1.5 под ровным полом, стойки — простые колонны
GAP = 0.5                                                                        # зазор пол модуля — рама (ход клавиши)
SMD_W, SMD_H, SMD_HP = 5.2, 1.0, 0.5                                             # SMD-кнопка: корпус 5.2×5.2×1.0 + шток Ø2×0.5 (всего 1.5)
if KLAV2:
    Z_B0, Z_BTOP = -(SMD_H + SMD_HP), 0.0                                        # кнопка в гнезде рамы, шток касается низа пола
else:
    Z_B0 = -GAP if KLAV else T.Z_FL                                              # низ кнопки: на раме / на полу модуля
    Z_BTOP = Z_B0 + BTN_H + BTN_HP                                               # верх штока = низ колонны
def btn_at(x, y):
    if KLAV2:
        return BB(x - SMD_W / 2, x + SMD_W / 2, y - SMD_W / 2, y + SMD_W / 2, Z_B0, Z_B0 + SMD_H) + CZ(1.0, Z_B0 + SMD_H - 0.01, Z_BTOP, x, y)
    return CZ(BTN_D / 2, Z_B0, Z_B0 + BTN_H, x, y) + CZ(BTN_DP / 2, Z_B0 + BTN_H - 0.01, Z_BTOP, x, y)
def sock_cut(x, y):                                                             # KLAV2: мелкое гнездо в полу под колонну (на клей)
    return BB(x - 2.15, x + 2.15, y - 1.65, y + 1.65, T.Z_FL - 0.6, T.Z_FL + 0.01)
TAB, TAB_W = CUP_R - 0.2, 1.4                                                    # боковой выступ «Т плашмя» (к центру модуля): длина / ширина (узкий — стойки стакана толще)
CUP_RI = float(os.environ.get("CUP_RI", "5.0"))                                  # 19.11 печать: стойки у пазов хрупкие — внутренняя (к центру) половина стакана толще
def cup_at(x, y):                                                               # стакан: гнездо кнопки, узкая прорезь выводов, паз перекладины (по Y) и паз выступа (по X, к центру)
    if KLAV2:
        return Part()
    sx = 1 if x > 0 else -1
    c = CZ(CUP_R, T.Z_FL - 0.01, T.Z_FL + CUP_H, x, y)
    c += CZ(CUP_RI, T.Z_FL - 0.01, T.Z_FL + CUP_H, x, y) & BB(*sorted((x, x - sx * (CUP_RI + 1))), y - CUP_RI - 1, y + CUP_RI + 1, T.Z_FL - 1, T.Z_FL + CUP_H + 1)
    c -= CZ(R_P, T.Z_FL - (3 if KLAV else 0), T.Z_FL + CUP_H + 1, x, y)
    c -= BB(x - 0.6, x + 0.6, y - CUP_RI - 1, y + CUP_RI + 1, T.Z_FL, T.Z_FL + CUP_H + 1)
    c -= BB(x - 1.65, x + 1.65, y - CUP_RI - 1, y + CUP_RI + 1, Z_BTOP - 0.4, T.Z_FL + CUP_H + 1)
    c -= BB(*sorted((x, x - sx * (CUP_RI + 1))), y - TAB_W / 2 - 0.15, y + TAB_W / 2 + 0.15, Z_BTOP - 0.4, T.Z_FL + CUP_H + 1)   # выступ держит балку от сдвига вбок
    return c
def leg_place(x, y, leg):                                                       # выступ ножки смотрит к центру модуля
    return Pos(x, y, 0) * (Rot(0, 0, 180) if x < 0 else Rot(0, 0, 0)) * leg
cups, btns = Part(), Part()
leg_parts = []
for sx in (-1, 1):
    cups += cup_at(sx * XCB, Y_BC)
    btns += btn_at(sx * XCB, Y_BC)
    if KLAV2:
        base -= sock_cut(sx * XCB, Y_BC)
    # колонна заодно с балкой; внизу перекладина — перевёрнутая «Т»: лежит в пазу стакана на штоке, паз держит колонну
    leg_parts.append((sx * XCB, Y_BC))
base += cups
# ножка «Т» — ОТДЕЛЬНАЯ деталь (владелец: вставлять в гнездо балки и клеить); под балкой — гнездо-бобышка
SOCK = 2.0                                                                       # глубина гнезда
def leg_at(x, y, z_top):                                                        # перекладина «Т» + колонна, верх колонны входит в гнездо на SOCK
    if KLAV2:                                                                    # простая колонна 4×3 от гнезда в полу до гнезда под балкой
        return BB(x - 2.0, x + 2.0, y - 1.5, y + 1.5, T.Z_FL - 0.6, z_top)
    return (BB(x - 1.5, x + 1.5, y - CUP_R, y + CUP_R, Z_BTOP, Z_BTOP + T_BAR) +
            BB(x - TAB, x + 0.01, y - TAB_W / 2, y + TAB_W / 2, Z_BTOP, Z_BTOP + T_BAR) +          # «Т плашмя»: выступ к −X в своём пазу стакана
            BB(x - 2.0, x + 2.0, y - 1.5, y + 1.5, Z_BTOP + T_BAR - 0.01, z_top))
def socket_at(x, y0, y1, z_top):                                                # бобышка под балкой/рейкой с гнездом под верх колонны (зазор 0.15)
    yc = (y0 + y1) / 2                                                           # верх бобышки вровень с низом балки (не задевает крючки тележки), срощена узким шипом
    return (BB(x - 3.2, x + 3.2, y0, y1, z_top - SOCK, z_top) + BB(x - 3.2, x + 3.2, yc - 0.6, yc + 0.6, z_top - 0.01, z_top + 0.3)) - BB(x - 2.15, x + 2.15, yc - 1.65, yc + 1.65, z_top - SOCK - 1, z_top - 0.3)
leg0 = leg_at(0, 0, L2[0] - 0.3)                                                 # ножка у начала координат (для печати)
legs = Part()
beam_body = beam
for x, y in leg_parts:
    beam_body += socket_at(x, y - 2.6, y + 2.6, L2[0])
    legs += leg_place(x, y, leg0)
beam = beam_body + legs                                                         # для проверок — в сборе
# тележка: рейка у шестерён + плита вперёд + площадка + крючки вокруг балки
cart = rack(-CW, CW, K.Y_FIX - 0.05, 1, L2[0], L2[1] + 0.16, 0.3)
Y_RB = K.Y_FIX - 0.05 - DED - 0.3
cart += BB(-CW, CW, Y_P0, Y_RB + DED + 0.3 + 0.8, ZB, ZT)                           # плита от площадки до рейки
for sg in (1, -1):
    pts = [(Y_BC + sg * (BM_B / 2 + C), L2[0]), (Y_BC + sg * (BM_B / 2 + C + 1.2), L2[0]), (Y_BC + sg * (BM_T / 2 + C + 1.2), L2[1] + 0.16),
           (Y_BC + sg * (BM_T / 2 + C + 1.2), ZB + 0.5), (Y_BC + sg * (BM_T / 2 + C), ZB + 0.5), (Y_BC + sg * (BM_T / 2 + C), L2[1])]
    cart += PX(pts if sg < 0 else pts[::-1], -CW, CW)

if __name__ == "__main__":
    def iv(a, b):
        try:
            r = a & b
            return 0.0 if r is None else r.volume
        except Exception:
            return 0.0
    st = {"основание": base, "рейка": V.fix_o, "брусок": K.beam, "мотор": K.motor, "балка": beam}
    bad = 0
    for s in (-S, -5.5, 0, 5.5, S):
        rf = math.degrees(s / RF)
        mv = {"ползун": Pos(s, 0, 0) * K.sl, "плав1": Pos(s - A, K.Y_G, 0) * Rot(0, 0, rf) * K.flo0, "плав2": Pos(s + A, K.Y_G, 0) * Rot(0, 0, rf) * K.flo0,
              "шестерня": Pos(0, YM, 0) * Rot(0, 0, math.degrees(s / RM)) * K.gm}
        c = Pos(2 * s, 0, 0) * cart
        for n, p in {**st, **mv}.items():
            v = iv(c, p)
            if v > 0.05: bad += 1; print("  s=%+.1f тележка × %s %.2f" % (s, n, v))
        for n in ("плав1", "плав2", "ползун"):
            for m in ("рейка", "основание", "балка"):
                v = iv(mv[n], st[m])
                if v > 0.05: bad += 1; print("  s=%+.1f %s × %s %.2f" % (s, n, m, v))
    if iv(Pos(0, 0, 0.6) * cart, beam) < 0.01:
        bad += 1; print("  тележка поднимается")
    print("модуль «тележка за мотором»: %s; площадка y %.1f…%.1f, край мотора %.1f; модуль вдоль струн %.1f" % (
        "ЧИСТО" if not bad else "%d проблем" % bad, Y_P0, Y_P1, Y_MOT0, base.bounding_box().size.Y))
    for n, p in (("base", base), ("fix", V.fix_o), ("beam_k", K.beam), ("beam", beam), ("motor", K.motor), ("slider", K.sl), ("flo", K.flo0),
                 ("cart", cart), ("gm", K.gm), ("plat", K.plat)):
        export_stl(Part() + p, "asm_zm/%s.stl" % n, tolerance=0.02, angular_tolerance=0.2)
    print("asm_zm готово")
