# -*- coding: utf-8 -*-
r"""Картинка: разрез поперёк щели скобы (вид с торца) — сейчас и с каркасом катушки. wiki/img/mag_shel_razrez.png"""
import os
from PIL import Image, ImageDraw, ImageFont
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "wiki", "img", "mag_shel_razrez.png")
F = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 20)
FB = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 24)
FS = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 16)
S = 70                                    # пикселей на мм
W, H = 1700, 900
im = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(im)
COL = {"сталь": (120, 125, 132), "магнит N": (215, 50, 50), "магнит S": (50, 90, 215), "воздух": (235, 245, 255),
       "каркас": (120, 170, 235), "провод": (230, 110, 30)}


def row(y0, title, layers):
    row.n = 0
    d.text((40, y0 - 95), title, font=FB, fill="black")
    total = sum(w for _, w in layers)
    x = (W - total * S) / 2
    hgt = 200
    for name, w in layers:
        x1 = x + w * S
        d.rectangle([x, y0, x1, y0 + hgt], fill=COL[name], outline="black" if name != "воздух" else (180, 190, 200))
        if name == "провод":
            for i in range(int(w / 0.34)):
                cx = x + (i + 0.5) * 0.34 * S
                for j in range(5):
                    cy = y0 + 25 + j * 37
                    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], outline=(150, 60, 10), width=2)
        lab = f"{name}\n{w:g} мм"
        yl = y0 + hgt + 14
        if w < 1:                                                        # тонкие слои — подписи вразбежку, с выноской
            yl += 52 * (row.n % 2)
            row.n += 1
            d.line([(x + x1) / 2, y0 + hgt, (x + x1) / 2, yl + 2], fill=(120, 120, 120), width=1)
        d.multiline_text(((x + x1) / 2, yl + 4), lab, font=FS, fill="black", anchor="ma", align="center")
        x = x1
    gx0 = (W - total * S) / 2 + (layers[0][1] + layers[1][1]) * S
    gx1 = gx0 + sum(w for _, w in layers[2:-2]) * S
    d.line([gx0, y0 - 12, gx1, y0 - 12], fill="black", width=3)
    d.text(((gx0 + gx1) / 2, y0 - 38), f"щель между магнитами {sum(w for _, w in layers[2:-2]):g} мм", font=F, fill="black", anchor="mm")


row(140, "Сейчас: голая катушка (мотаем на оправке и снимаем) — сила 100%",
    [("сталь", 1.5), ("магнит N", 5), ("воздух", 0.5), ("провод", 3), ("воздух", 0.5), ("магнит S", 5), ("сталь", 1.5)])
row(560, "С каркасом: мотаем прямо в каркас и вставляем в рамку — щель +1 мм, сила 82%",
    [("сталь", 1.5), ("магнит N", 5), ("воздух", 0.5), ("каркас", 0.5), ("провод", 3), ("каркас", 0.5), ("воздух", 0.5), ("магнит S", 5), ("сталь", 1.5)])
im.save(OUT); print("saved", OUT)
