# Сборка печатного набора З по шагам: детали из ../19.70_pechat_okantovka8_Z/sborka. Кадр 1 — всё разнесено вверх по порядку, дальше детали по одной садятся на место.
# Запуск: blender -b -P blender_sborka.py -- P|Z
import bpy, os, sys
MOD = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else "Z"
D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "19.70_pechat_okantovka8_%s" % MOD); S_ = os.path.join(D, "sborka")
STEPS_P = [
    (["01_okantovka_P", "k1_knopka"], "1. Окантовка: справа ваза — кнопка в неё, выводы в щели; слева стойка с пазом", (.35, .3, .25, 1)),
    (["02_platforma_P"], "2. Платформа — язычки сзади в ямки окантовки (НЕ клеить, она качается)", (.6, .62, .66, 1)),
    (["13_kryshki_osi_x2"], "3. Крышки ×2 на ямки язычков — клей только к окантовке (можно позже)", (.95, .85, .3, 1)),
    (["12_maket_motora"], "4. Мотор (или макет) — в кольцо платформы", (.12, .12, .14, 1)),
    (["09_platforma_rotora", "k2_magnity", "08_shest_motora"], "5. Ротор: 8 магнитов N/S через один, шестерня мотора квадратом в гнездо, клей; на ось мотора", (.6, .25, .7, 1)),
    (["10_stojka_49E_x2", "k3_datchiki_49E"], "6. Стойки 49E ×2 — низом в прорези у кольца, датчики к магнитам", (.78, .78, .72, 1)),
    (["05_brusok"], "7. Брусок со стойками — сверху, низ стоек в гнёзда пола, клей", (.7, .72, .76, 1)),
    (["06_polzun", "07_shest_plav_x2"], "8. Ползун пазом на брусок, 2 плавающие шестерни на его оси", (.2, .6, .3, 1)),
    (["04_rejka_P"], "9. Рейка с держателями — сверху: держатели в пазы пола, правое плечо на кнопку, левый язык в паз стойки; клей внизу", (.45, .48, .52, 1)),
    (["11_telezhka_P"], "10. Тележка — сверху, зубьями к шестерням", (.15, .4, .9, 1)),
]
STEPS = [  # (детали, подпись шага, цвет)
    (["01_okantovka_Z"], "1. Окантовка (рамка) — основа", (.35, .3, .25, 1)),
    (["14_stojka_knopki_Z", "k1_knopka"], "2. Стойка с вазой — справа на окантовку, клей. Кнопка в вазу, выводы в щели", (.85, .55, .2, 1)),
    (["15_stojka_paza_Z"], "3. Стойка с пазом — слева на окантовку, клей", (.75, .45, .15, 1)),
    (["02_platforma_Z"], "4. Платформа — язычки сзади в ямки окантовки (НЕ клеить, она качается)", (.6, .62, .66, 1)),
    (["13_kryshki_osi_x2"], "5. Крышки ×2 на ямки язычков — клей только к окантовке (можно позже)", (.95, .85, .3, 1)),
    (["12_maket_motora"], "6. Мотор (или макет) — в кольцо платформы", (.12, .12, .14, 1)),
    (["09_platforma_rotora", "k2_magnity", "08_shest_motora"], "7. Ротор: 8 магнитов N/S через один, шестерня мотора квадратом в гнездо, клей; на ось мотора", (.6, .25, .7, 1)),
    (["10_stojka_49E_x2", "k3_datchiki_49E"], "8. Стойки 49E ×2 — низом в прорези у кольца, датчики к магнитам", (.78, .78, .72, 1)),
    (["05_brusok"], "9. Брусок — на стойки платформы, клей", (.7, .72, .76, 1)),
    (["06_polzun", "07_shest_plav_x2"], "10. Ползун пазом на брусок, 2 плавающие шестерни на его оси", (.2, .6, .3, 1)),
    (["04_rejka_stolik_Z"], "11. Рейка-столик — стенками в паз пола сзади, клей", (.45, .48, .52, 1)),
    (["03a_noga_balki_prav", "03b_noga_balki_lev"], "12. Ножки балки: правая — над кнопкой, левая — в паз стойки; клей к стойкам бруска", (.55, .57, .6, 1)),
    (["03c_balka_Z"], "13. Балка — на ножки, клей", (.4, .42, .46, 1)),
    (["11_telezhka_Z"], "14. Тележка — на балку, зубьями к шестерням", (.15, .4, .9, 1)),
]
if MOD == "P": STEPS = STEPS_P
BUY = {"k1_knopka": (.9, .15, .15, 1), "k2_magnity": (.9, .9, .95, 1), "k3_datchiki_49E": (.05, .05, .3, 1)}
NAMES = {"k1_knopka": "кнопка (покупная)", "k2_magnity": "магниты 8 шт (покупные)", "k3_datchiki_49E": "датчики 49E (покупные)"}
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.unit_settings.scale_length = 0.001; sc.unit_settings.length_unit = 'MILLIMETERS'
UP, DUR, F0 = 8.0, 20, 10                                                        # шаг разноса по высоте, кадров на шаг
TXT = []
sc.frame_start, sc.frame_end = 1, F0 + DUR * len(STEPS) + 30
for i, (names, txt, col) in enumerate(STEPS):
    coll = bpy.data.collections.new("%02d %s" % (i + 1, txt.split("—")[0].split(". ", 1)[1].strip())); sc.collection.children.link(coll)
    fa, fb = F0 + DUR * i, F0 + DUR * i + DUR - 4
    for n in names:
        bpy.ops.wm.stl_import(filepath=os.path.join(S_, n + ".stl")); o = bpy.context.selected_objects[0]
        o.name = NAMES.get(n, n); [c.objects.unlink(o) for c in o.users_collection]; coll.objects.link(o)
        m = bpy.data.materials.new(o.name); m.diffuse_color = BUY.get(n, col); o.data.materials.append(m)
        o.location.z = UP * (i + 1); o.keyframe_insert("location", index=2, frame=fa)
        o.location.z = 0.0; o.keyframe_insert("location", index=2, frame=fb)
    t = bpy.data.curves.new("t%d" % i, 'FONT'); t.body = __import__("textwrap").fill(txt, 46); t.size = 2.4
    to = bpy.data.objects.new("подпись %02d" % (i + 1), t); coll.objects.link(to); TXT.append(to)
    sc.timeline_markers.new("%d" % (i + 1), frame=fb)
    tm = bpy.data.materials.new("txt"); tm.diffuse_color = (1, 1, 1, 1); t.materials.append(tm)
    for f, h in ((1, True), (fa - 1, True), (fa, False), (fa + DUR - 1, False), (fa + DUR, i != len(STEPS) - 1)):   # подпись видна только на своём шаге
        to.hide_viewport = h; to.hide_render = h; to.keyframe_insert("hide_viewport", frame=f); to.keyframe_insert("hide_render", frame=f)
tg = bpy.data.objects.new("ц", None); sc.collection.objects.link(tg); tg.location = (0, 8, 15)
cam = bpy.data.objects.new("Камера", bpy.data.cameras.new("Камера")); sc.collection.objects.link(cam); cam.location = (110, -120, 140); cam.data.clip_start = 1
k = cam.constraints.new('TRACK_TO'); k.target = tg; k.track_axis = 'TRACK_NEGATIVE_Z'; k.up_axis = 'UP_Y'; sc.camera = cam
bpy.context.view_layer.update()
for to in TXT:                                                                    # подписи висят перед камерой, в левом верхнем углу
    to.parent = cam; to.location = (-34, 20, -100); to.rotation_euler = (0, 0, 0)
sc.frame_set(1); bpy.ops.wm.save_as_mainfile(filepath=os.path.join(D, "sborka_%s.blend" % MOD)); print("saved", len(STEPS))
