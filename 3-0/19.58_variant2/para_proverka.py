# -*- coding: utf-8 -*-
# Пара: вариант 2 (y = 0) и вариант 2Б сзади (y = +D), тележки на шаге 24. Проверка пересечений при разных положениях обеих тележек.
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from build123d import *
import variant2b as B
V, T = B.V, B.T
c2 = V.cart2.bounding_box(); cb = B.cart.bounding_box()
y2 = (c2.min.Y + c2.max.Y) / 2; yb = (cb.min.Y + cb.max.Y) / 2
D = 24.0 + y2 - yb
print("центр тележки 2: %.2f, 2Б: %.2f → сдвиг модуля 2Б D = %.2f (колпаки Ø38: зазор %.2f)" % (y2, yb, D, D - 38.0))
def iv(a, b):
    try:
        r = a & b; return 0.0 if r is None else r.volume
    except Exception:
        return 0.0
sA = {"осн": V.base2, "рейка": V.fix2, "брусок": T.beam, "мотор": T.motor, "колпак": Pos(0, T.YM, 0) * T.jacket}
sB = {"осн": V.base2, "рейка": V.fix2, "брусок": T.beam, "мотор": T.motor, "колпак": Pos(0, T.YM, 0) * T.jacket, "стойка": B.st, "перекладина": B.per}
sB = {k: Pos(0, D, 0) * v for k, v in sB.items()}
bad = 0
for a, pa in sA.items():
    for b, pb in sB.items():
        v = iv(pa, pb)
        if v > 0.05: bad += 1; print("  статика А.%s × Б.%s %.2f" % (a, b, v))
for s1 in (-T.S, 0, T.S):
    for s2 in (-T.S, 0, T.S):
        mA = V.pose2(s1); mB = {k: Pos(0, D, 0) * v for k, v in B.pose_b(s2).items()}
        for a, pa in list(mA.items()) + list(sA.items()):
            for b, pb in mB.items():
                v = iv(pa, pb)
                if v > 0.05: bad += 1; print("  s=%+.0f/%+.0f А.%s × Б.%s %.2f" % (s1, s2, a, b, v))
        for a, pa in mA.items():
            for b, pb in sB.items():
                v = iv(pa, pb)
                if v > 0.05: bad += 1; print("  s=%+.0f/%+.0f А.%s × Б.%s %.2f" % (s1, s2, a, b, v))
print("пара: %s; длина пары вдоль струн %.1f мм" % ("ЧИСТО" if not bad else "%d пересечений" % bad, (V.base2.bounding_box().max.Y + D) - min(V.base2.bounding_box().min.Y, B.st.bounding_box().min.Y + D)))
