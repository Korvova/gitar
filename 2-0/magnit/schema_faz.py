# -*- coding: utf-8 -*-
r"""Схема подключения 8 катушек пробного русла в две фазы — картинка wiki/img/mag_sb_7_shema.png.
Запуск: .venv-b123d\Scripts\python magnit\schema_faz.py"""
import os
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "wiki", "img", "mag_sb_7_shema.png")
F = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 22)
FS = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 17)
W, H = 1200, 620
im = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(im)
PH = ["A", "B", "B", "A", "B", "A", "A", "B"]
REV = {3, 6}
COL = {"A": (240, 140, 40), "B": (60, 170, 90)}
x0, cw, top = 110, 120, 230
pos = {}
for k in range(8):
    x = x0 + k * cw
    c = COL[PH[k]]
    d.rectangle([x, top, x + 70, top + 150], outline=c, width=10)
    d.rectangle([x + 28, top + 25, x + 42, top + 125], fill="white")
    d.text((x + 35, top - 32), f"{k + 1}", font=F, fill="black", anchor="mm")
    d.text((x + 35, top + 175), PH[k] + (" наоборот" if k + 1 in REV else ""), font=FS, fill=c, anchor="mm")
    pos[k + 1] = (x + 10, x + 60)                  # вывод «начало» слева, «конец» справа
    d.text((x + 10, top + 205), "н", font=FS, fill="gray", anchor="mm")
    d.text((x + 60, top + 205), "к", font=FS, fill="gray", anchor="mm")


FB = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 24)
d.text((60, 470), "Фаза A:   A1 → 1н   1к → 4н   4к → 7н   7к → 6к   6н → A2", font=FB, fill=COL["A"])
d.text((60, 530), "Фаза B:   B1 → 2н   2к → 5н   5к → 8н   8к → 3к   3н → B2", font=FB, fill=COL["B"])
d.text((60, 580), "«1к → 4н» — спаять конец катушки 1 с началом катушки 4. У катушек 3 и 6 провод входит в конец (к) — они наоборот.", font=FS, fill="black")
d.text((W / 2, 30), "Две фазы: последовательно, катушки 3 и 6 — наоборот (меняем местами н и к)", font=F, fill="black", anchor="mm")
d.text((W / 2, 70), "н — начало (внутренний вывод, из прорези оправки), к — конец (наружный). Все катушки мотать в одну сторону", font=FS, fill="black", anchor="mm")
d.text((W / 2, 100), "A1–A2 и B1–B2 — в разъём мотора на плате вместо пар проводов мотора (пару находим прозвонкой)", font=FS, fill="black", anchor="mm")
im.save(OUT)
print("saved", OUT)
