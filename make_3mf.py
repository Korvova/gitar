# -*- coding: utf-8 -*-
"""
Сборка готовых 3mf-проектов для Bambu Studio из STL + наших настроек печати.
Результат: Print3mf\01..05*.3mf — открыть, нарезать, печатать.

Запуск: .venv-b123d\Scripts\python make_3mf.py
"""
import json, os, shutil, subprocess, sys, math
import numpy as np
import trimesh

BS = r"C:\Program Files\Bambu Studio"
EXE = BS + r"\bambu-studio.exe"
PROF = BS + r"\resources\profiles\BBL"
SRC = r"C:\App\gitar\2-0\Print\Print"
OUT = r"C:\App\gitar\2-0\Print3mf"
TMP = OUT + r"\_tmp"
os.makedirs(TMP, exist_ok=True)

# ---------- разрешение наследования профилей ----------
def resolve(folder, name, seen=None):
    seen = seen or set()
    path = os.path.join(PROF, folder, name + ".json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    parent_name = data.pop("inherits", None)
    if parent_name and parent_name not in seen:
        seen.add(parent_name)
        parent = resolve(folder, parent_name, seen)
        parent.update(data)
        data = parent
    return data

def tweak(profile, deltas):
    ref_len = 1
    for v in profile.values():
        if isinstance(v, list) and len(v) > 1:
            ref_len = len(v)
            break
    for k, val in deltas.items():
        cur = profile.get(k)
        if isinstance(cur, list):
            profile[k] = [str(val)] * len(cur)
        elif cur is not None:
            profile[k] = str(val)          # скалярный ключ — оставить скаляром
        else:
            profile[k] = str(val)          # нет в базе — писать скаляром,
    return profile                          # список CLI молча отвергает

def write_json(profile, fname):
    p = os.path.join(TMP, fname)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=1)
    return p

# ---------- профили ----------
machine = resolve("machine", "Bambu Lab P2S 0.4 nozzle")
machine_j = write_json(machine, "machine.json")

fila = resolve("filament", "Bambu PETG HF @BBL P2S 0.4 nozzle")
tweak(fila, {"fan_min_speed": 40, "fan_max_speed": 80})
fila_j = write_json(fila, "filament.json")

# усиленное охлаждение для столов с 1-2 мелкими деталями
fila_cool = resolve("filament", "Bambu PETG HF @BBL P2S 0.4 nozzle")
tweak(fila_cool, {"fan_min_speed": 60, "fan_max_speed": 100,
                  "slow_down_layer_time": 15})
fila_cool_j = write_json(fila_cool, "filament_cool.json")

COMMON = {  # для всех столов
    "outer_wall_speed": 45,
    "small_perimeter_speed": "50%",
    "small_perimeter_threshold": 20,
    "reduce_crossing_wall": 1,
}
SMALL = dict(COMMON, **{  # мелочь: колёсики, тележки, плавники
    "brim_type": "outer_only",
    "brim_width": 3,
    "brim_object_gap": 0.1,
    "wall_loops": 4,
})

p020 = tweak(resolve("process", "0.20mm Standard @BBL P2S"), COMMON)
p020_j = write_json(p020, "p020.json")

p012 = tweak(resolve("process", "0.12mm High Quality @BBL P2S"), SMALL)
p012_j = write_json(p012, "p012.json")

p012fin = tweak(resolve("process", "0.12mm High Quality @BBL P2S"),
                dict(SMALL, sparse_infill_density="99%",   # CLI падает ровно на 100%
                     sparse_infill_pattern="zig-zag", wall_loops=6))
p012fin_j = write_json(p012fin, "p012fin.json")

# барабаны вверх ногами: поддержка ТОЛЬКО от стола (кольцо под юбкой)
p012drum = tweak(resolve("process", "0.12mm High Quality @BBL P2S"),
                 dict(SMALL, sparse_infill_density="99%",
                      sparse_infill_pattern="zig-zag", wall_loops=6,
                      enable_support=1, support_on_build_plate_only=1,
                      support_type="normal(auto)", support_top_z_distance=0.2))
p012drum_j = write_json(p012drum, "p012drum.json")

# ---------- ориентация STL ----------
def prep(name, transform=None, copies=1, tag=""):
    """Вернуть список путей к STL, при необходимости повернув деталь."""
    src = os.path.join(SRC, name + ".stl")
    if transform is None:
        return [src] * copies
    m = trimesh.load(src)
    m.apply_transform(transform)
    m.apply_translation([0, 0, -m.bounds[0][2]])   # на стол
    p = os.path.join(TMP, name + tag + "_orient.stl")
    m.export(p)
    return [p] * copies

FLIP = trimesh.transformations.rotation_matrix(math.pi, [1, 0, 0])      # вверх ногами
ID = np.eye(4)                                          # только положить на стол
LAY = trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0])  # лёжа (Y->Z)
LAYY = trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0])  # на бок (X->Z)

plates = [
    ("01_grif_L1-L5", p020_j, sum([prep(f"neckL{i}_v9") for i in range(1, 6)], [])),
    ("02_deka_rail_stop", p020_j,
     prep("deck_v9", FLIP) + prep("rail_v9", FLIP, 2) + prep("stop_v9", FLIP)),
    ("03_telezhki_roliki", p012_j,
     prep("cart_body_v9", copies=4) + prep("roller_corner_v9", copies=8)),
    ("04_guides", p012_j,
     sum([prep(f"guide_m{i}_v9", copies=2) for i in range(1, 5)], [])),
    ("05_plavniki_100pct", p012fin_j,      # плавники: A и B РАЗНЫЕ (палец зеркально)
     sum([prep(f"fin_f{i}_v9", LAY) for i in range(1, 5)], []) +
     sum([prep(f"fin_b{i}_v1", LAY) for i in range(1, 5)], [])),
    ("06_vtulki_vremennye", p012_j,
     sum([prep(f"bush_m{i}_v9", copies=3) for i in range(1, 5)], [])),
    ("07_cart_body_fix", p012_j, prep("cart_body_v9", copies=4)),
    # v9.7 СБОРНЫЙ барабан (все 4 одинаковые: 2 кольца + крышка) + подъёмные
    # столбики под уши моторов m2/m3/m4 (по 2 шт + запас); всё плоское
    ("08_barabany_fix", p012fin_j,
     prep("drum_ring_v9", copies=9) + prep("drum_top_v9", copies=5) +
     sum([prep(f"riser_m{i}_v9", copies=3) for i in (2, 3, 4)], []), "cool"),
    ("09_drum_test", p012fin_j,
     prep("drum_ring_v9", copies=2) + prep("drum_top_v9"), "cool"),
    ("14_disk_final", p012fin_j,             # ФИНАЛ: диск Ø27 с гнёздами ключей
     prep("bigdrum27_v9") + prep("keylock_key_v2", copies=3), "cool"),
    ("15_disk54", p012fin_j,               # диск Ø54 гладкий (прототип-фаза)
     prep("disk54_v1") + prep("keylock_key_v2", copies=3), "cool"),
    ("16_tier_disks", p012fin_j,           # ЯРУС-ДИСКИ v3: стопка на 2 винтах M2
     prep("tier_disk_v3", copies=2) + prep("keylock_key_v2", copies=3), "cool"),
    ("19_tier_disks_x4", p012fin_j,        # ПОЛНЫЙ КОМПЛЕКТ: 4 стопки на все моторы
     prep("tier_disk_v3", copies=8) + prep("keylock_key_v2", copies=9), "cool"),
    ("20_test_noga", p020_j,               # тест-нога 20 см на шестерню (+линейка до 40)
     prep("test_leg_v1") + prep("test_leg_ext_v1")),
    ("21_palka_test", p020_j,              # ТЕСТ-СТЕНД «палка» ФИНАЛ: кулиса-вилка,
     prep("ptest_plate_v2") + prep("ptest_triangle_v2") +      # 7 кривошипов
     prep("ptest_spica_v2") +                                  # r6..r10 (ход =
     prep("ptest_cart_v2") +                                   # 6.15*r - 10.6),
     prep("ptest_crank_r60_v2") + prep("ptest_crank_r65_v2") + # замки всех узлов
     prep("ptest_crank_r70_v2") + prep("ptest_crank_r80_v2") + # (мосты, шайба)
     prep("ptest_crank_r85_v2") + prep("ptest_crank_r90_v2") +
     prep("ptest_crank_r100_v2") + prep("ptest_leg_v1", copies=4) +
     prep("ptest_bridge_v1", copies=2) + prep("ptest_bridge_low_v1") +
     prep("ptest_bridge_high_v1", copies=2) + prep("ptest_washer_v1") +
     prep("ptest_plug_v2", FLIP)),
    ("30_gitara_joints", p020_j,           # ГИТАРА: тест узлов сборности —
     prep("git_spica_seg_a") + prep("git_spica_seg_b") +   # стык спицы-ленты
     prep("git_neck_joint_a") + prep("git_neck_joint_b", FLIP)),  # и стык грифа
    ("31_gitara_sec1_plity", p020_j,       # ГИТАРА секция-1: 5 плит стопки
     prep("gs1_p0_base") + prep("gs1_p1_mid") +
     prep("gs1_p2_mid") + prep("gs1_p3_mid")),
    ("32_gitara_sec1_meh", p012_j,         # палуба + механика (штыри с бримом)
     prep("gs1_p4_deck") + prep("gs1_cart", copies=4) +
     prep("gs1_arm0") + prep("gs1_arm1") + prep("gs1_arm2") + prep("gs1_arm3") +
     prep("gs1_spica0") + prep("gs1_spica1") + prep("gs1_spica2") + prep("gs1_spica3")),
    ("33_gitara_sec2", p020_j,             # секция-2 РАЗБОРНАЯ: дно + 4 П-рейки
     prep("gs2_base") + prep("gs2_tray", copies=4) + prep("gs2_fret")),
    ("34_gitara_sec3", p020_j,             # секция-3 (низ грифа): то же + свои лады
     prep("gs3_base") + prep("gs2_tray", copies=4) + prep("gs3_fret")),
    ("35_gitara_deka1", p020_j,            # ДЕКА-1: дно (3 мотора NEMA17) +
     prep("gdk1_base") + prep("gdk_comb", copies=3) +          # кривошипы, втулки,
     prep("gdk_crank0") + prep("gdk_crank1") + prep("gdk_crank2") +   # гребёнки
     prep("gdk_sleeve0") + prep("gdk_sleeve1") + prep("gdk_sleeve2")),
    ("36_gitara_deka2", p020_j,            # ДЕКА-2 + ленты: сегменты и хвосты
     prep("gdk2_base") + prep("gdk_crank3") + prep("gdk_sleeve3") +
     prep("gdk_comb") + prep("gdk_ext", copies=8) +
     prep("gdk_tail0") + prep("gdk_tail1") + prep("gdk_tail2") + prep("gdk_tail3")),
    # ---- КОРПУС в настоящих размерах: дно 4 куска (тумбами вверх),
    # крышка 4 куска (печать ВВЕРХ НОГАМИ: лицо на столе, бортики вверх),
    # обечайка: 7 плоских лент 95x~209 (PETG, гнутся при сборке)
    ("37_korpus_dno_nw", p020_j, prep("gk_dno_nw", ID)),
    ("38_korpus_dno_ne", p020_j, prep("gk_dno_ne", ID)),
    ("39_korpus_dno_sw", p020_j, prep("gk_dno_sw", ID)),
    ("40_korpus_dno_se", p020_j, prep("gk_dno_se", ID)),
    ("41_korpus_top_wn", p020_j, prep("gk_top_wn", FLIP)),
    ("42_korpus_top_ws", p020_j, prep("gk_top_ws", FLIP)),
    ("43_korpus_top_e", p020_j, prep("gk_top_en", FLIP) + prep("gk_top_es", FLIP)),
    ("44_korpus_lenty_a", p020_j, sum([prep(f"gk_band{i}", ID) for i in (0, 1)], [])),
    ("45_korpus_lenty_b", p020_j, sum([prep(f"gk_band{i}", ID) for i in (2, 3)], [])),
    ("46_korpus_lenty_c", p020_j,
     sum([prep(f"gk_band{i}", ID) for i in (4, 5, 6)], [])),
    ("48_struna_test", p020_j,             # ТЕСТ-СТЕНД струны: плита + прижим +
     prep("gst_test_plate") + prep("gst_test_klamp") +   # струна лёжа + столбик +
     prep("gst_struna", LAYY) + prep("gst_stolb") +      # 4 гармошки (2 жёсткости)
     prep("gst_garm", copies=2) + prep("gst_garm_soft", copies=2)),
    ("49_struna_test2", p020_j,            # ТЕСТ v2 «как струна»: без потенца —
     prep("gst_test2_plate") + prep("gst_struna2", LAYY) +
     prep("gst_stolb") + prep("gst_skoba", LAY, copies=2) +  # Г-обойма (+запас)
     prep("gst_garm", copies=2) + prep("gst_garm_soft", copies=2) +  # пружины!
     prep("gst_nozhka", copies=4)),        # ножки: снизу место дюпон-разъёмам
    ("50_skoba6_test", p020_j,             # обойма с ХВОСТОМ (вынос магнита) +
     prep("gst_skoba6", ID, copies=2) +    # подставка платы: прикрутить к
     prep("gst_podstavka", ID)),           # текущему стенду 49 и проверить
    ("51_struny6_rama", p020_j,            # ШЕСТИСТРУНКА: рама v3 (финал)
     prep("gst_rama6", ID)),
    ("52_struny6_detali", p020_j,          # вся мелочь шестиструнки:
     prep("gst_struna2", LAYY, copies=6) +           # 6 струн лёжа
     prep("gst_stolb", copies=12) +                  # 12 столбиков
     prep("gst_garm", copies=14) +                   # 12 пружин + запас
     prep("gst_garm_soft", copies=4) +               # мягкие на подбор
     prep("gst_skoba", ID, copies=3) +               # обоймы центр (2+1)
     prep("gst_skoba6", ID, copies=5) +              # обоймы с хвостом (4+1)
     prep("gst_kryshka_mag", ID, copies=5) +         # крышечки магнитов
     prep("gst_kryshka_big", ID) +                   # общая крышка плат
     prep("gst_shayba", copies=6)),                  # проставки рамы
    ("54_garm_mid", p020_j,                # гармошки 0.7: чередование жёсткостей
     prep("gst_garm_mid", copies=5)),      # против звона соседних струн
    ("53_cell_test", p020_j,               # тест-ячейка платы AS5600: карман,
     prep("gst_test_cell", ID)),           # посадка платы: ПРОВЕРЕН 02.08
    ("17_liners", p012fin_j,               # вкладыши: A/B зеркальные, с башмаком —
     sum([prep(f"liner_f{i}_v1") for i in range(1, 5)], []) +       # печать КАК ЕСТЬ
     sum([prep(f"liner_b{i}_v1") for i in range(1, 5)], []), "cool"),
    ("18_etazh1_test", p012fin_j,          # ЭТАЖ 1 руками: слой + тележка + оба
     prep("neckL1_v9") + prep("cart_body_v9") +                    # плавника (A и B),
     prep("fin_f1_v9", LAY) + prep("fin_b1_v1", LAY) +             # оба вкладыша,
     prep("liner_f1_v1") + prep("liner_b1_v1") +                   # 2 угловых ролика
     prep("roller_corner_v9", copies=2), "cool"),
    ("13_keylock", p012fin_j,                     # тест поворотного ключа (идея юзера)
     prep("keylock_plate_v3") + prep("keylock_key_v2", copies=2) + prep("toggle_peg_v1", copies=2), "cool"),
    ("10_kalibr_kupony", p012fin_j,
     sum([prep(f"coupon_spline_{i}") for i in range(1, 5)], []) +
     sum([prep(f"coupon_pilot_{i}") for i in range(1, 4)], []), "cool"),
]

# ---------- сборка 3mf ----------
for plate in plates:
    name, proc_j, stls = plate[0], plate[1], plate[2]
    fj = fila_cool_j if (len(plate) > 3 and plate[3] == "cool") else fila_j
    out = os.path.join(OUT, name + ".3mf")
    if os.path.exists(out):
        os.remove(out)
    cmd = [EXE,
           "--load-settings", f"{machine_j};{proc_j}",
           "--load-filaments", fj,
           "--arrange", "1",
           "--export-3mf", out] + stls
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    ok = os.path.exists(out)
    print(f"{name}: exit={r.returncode} file={'OK' if ok else 'НЕТ!'} ({len(stls)} дет.)")

print("done")
