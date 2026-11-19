# -*- coding: utf-8 -*-
"""Кнопки модуля «З» теперь встроены в modul_za_motorom.py (балка с колоннами, стаканы в основании). Здесь только экспорт кнопок для сцены."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from build123d import *
import modul_za_motorom as Z
os.chdir(HERE); os.makedirs("asm_kn", exist_ok=True)
export_stl(Part() + Z.btns, "asm_kn/btns.stl", tolerance=0.02, angular_tolerance=0.2)
print("кнопки экспортированы")
