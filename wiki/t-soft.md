Всё программное в проекте: прошивки ESP32, страницы-пульты в браузере, скрипты моделей, столов печати, плат и картинок.
Здесь — что есть, где лежит код, как запустить, скрины. Код — в репозитории [Korvova/gitar](https://github.com/Korvova/gitar).

## Этап 1. Прошивки ESP32

| Номер | Требование | Описание | Урок | Статус |
|---|---|---|---|---|
| 13.1 | Прошивка платы 4 моторов | [plata4_fw.ino](https://github.com/Korvova/gitar/blob/main/plata4_fw/plata4_fw.ino). USB 115200. Ножки — [Т. Плата для 4-х моторов](/homepage/iniciativa.-razrabotka/jepik-ruka-gitara/t-plata-4-motora) 9.8. Команды: `m 0…3` — выбрать мотор; `deg <°> [об/мин]`, `sw <полуугол> [об/мин]`, `stop`, `hold`, `free` — к выбранному; `off` — отпустить все; `cur <мА>` — ток всех; `init` — перенастроить драйверы; `diag` — все адреса, `diag N` — катушки, EN и STEP мотора N; `status`. Калибровка струн: `save N`, `ref N`, `go N [об/мин]`, `to M N [об/мин]`, `cal`, `calclr` (13.7) | Ток удержания 20% — моторы не греются стоя. `diag N` ловит «STEP не доходит» по счётчику микрошагов MSCNT. Функции в .ino объявлять до использования (заглушка ctags, см. 13.14) | ✅ Работает |
| 13.2 | Прошивка стенда одного мотора | [drive_web.ino](https://github.com/Korvova/gitar/blob/main/drive_web/drive_web.ino): один драйвер, Wi-Fi пульт и USB-команды, `diag` с подсчётом байт по RX2 — для поиска ошибок проводки | Урок стенда: драйвер на RX0/TX0 — команды проходят, мотор стоит ([Т. Плата для мотора](/homepage/iniciativa.-razrabotka/jepik-ruka-gitara/t-plata) 8.2) | ✅ Работает |
| 13.3 | Прошивки струн | [struny6_hall.ino](https://github.com/Korvova/gitar/blob/main/2-0/struny6_hall/struny6_hall.ino) — 6 датчиков Холла 49E на АЦП, 460800, ~650 строк/с; [hall49e_test.ino](https://github.com/Korvova/gitar/blob/main/2-0/hall49e_test/hall49e_test.ino) — проба одного датчика | Вспомогательная проверка правой руки — [Т. Струны](/homepage/iniciativa.-razrabotka/jepik-ruka-gitara/t-struny) | ✅ Работает |

## Этап 2. Пульты в браузере

| Номер | Требование | Описание | Урок | Статус |
|---|---|---|---|---|
| 13.4 | Пульт 4 моторов | [plata4_pult.html](https://github.com/Korvova/gitar/blob/main/2-0/websim/plata4_pult.html) — открыть в Chrome, «Подключить», выбрать COM-порт ESP. Вверху: драйверы, ток, «СТОП», «Отпустить все». Мелодия с темпом и звуком. Карточка на каждый мотор: повороты, скорость, качание, «Тест», калибровка струн. ![Пульт 4 моторов](https://raw.githubusercontent.com/Korvova/gitar/main/wiki/img/soft_plata4_pult.png) | Web Serial работает только в Chrome/Edge. Пока пульт подключён, прошивку не залить — порт занят: обновить вкладку (F5) | ✅ Работает |
| 13.5 | Пульт одного мотора | [serial_pult.html](https://github.com/Korvova/gitar/blob/main/2-0/websim/serial_pult.html) — для стенда `drive_web` | | ✅ Работает |
| 13.6 | Пульт струн | [struny6_pult.html](https://github.com/Korvova/gitar/blob/main/2-0/websim/struny6_pult.html) — шесть осциллографов, ноты EADGBE, синтез звука, подавитель наводок между струнами | | ✅ Работает |

## Этап 3. Калибровка струн и мелодии

| Номер | Требование | Описание | Урок | Статус |
|---|---|---|---|---|
| 13.7 | Калибровка струн в прошивке и пульте | По [Т. Тележки](/homepage/iniciativa.-razrabotka/jepik-ruka-gitara/t-telezhki) 11.8–11.9. В карточке мотора: «◀ 1° / 5° ▶» — подвинуть тележку под струну; кнопки 1…6 «Запомнить струну» — зелёные, если уже запомнены; «→1…→6» — ехать на струну; «Сверка: это струна 1» — в начале сессии. Хранится в памяти ESP (Preferences), переживает выключение | Запоминается положение вала в шагах, а не миллиметры: кривошип двигает тележку по синусу. Переезд идёт по тем же шагам, без полного оборота — тележка не проскакивает через край хода. После включения нужна сверка: мотор не знает, где стоит | ⚠️ Сделано 26.09, на грифе не проверено |
| 13.8 | Проигрыватель «Оды к радости» | В пульте блок «Мелодия»: ноты с пальцами и струнами подсвечиваются по ходу, на каждой ноте `to M N` — тележка пальца едет на свою струну, пульт играет звук ноты; темп 20–120 уд/мин, звук можно выключить. Ноты — [Т. Тележки](/homepage/iniciativa.-razrabotka/jepik-ruka-gitara/t-telezhki) 11.10, звук для прослушивания — [oda_k_radosti.wav](https://raw.githubusercontent.com/Korvova/gitar/main/wiki/audio/oda_k_radosti.wav) ([make_oda_wav.py](https://github.com/Korvova/gitar/blob/main/2-0/websim/make_oda_wav.py)) | Нужны откалиброванные: мотор 0 — струны 2 и 3, мотор 1 — 2, мотор 2 — 3, мотор 3 — 2. Мотор = палец: 0 указательный … 3 мизинец | ⚠️ Сделано 26.09, на грифе не проверено |

## Этап 4. Инструменты разработки

| Номер | Требование | Описание | Урок | Статус |
|---|---|---|---|---|
| 13.9 | Модели деталей кодом | build123d: [gitara_sec1_v2.py](https://github.com/Korvova/gitar/blob/main/2-0/gitara_sec1_v2.py), [gitara_sec2.py](https://github.com/Korvova/gitar/blob/main/2-0/gitara_sec2.py), [gitara_deka.py](https://github.com/Korvova/gitar/blob/main/2-0/gitara_deka.py), [gitara_lozhe.py](https://github.com/Korvova/gitar/blob/main/2-0/gitara_lozhe.py) и др. В конце каждого — численная проверка сборки [clearance.py](https://github.com/Korvova/gitar/blob/main/2-0/clearance.py): зазоры и посадки, при нарушении скрипт падает | Тяжёлые расчёты (дека) — на сервере: самопересекающийся профиль однажды съел всю память и повесил компьютер | ✅ |
| 13.10 | Столы печати | [make_3mf.py](https://github.com/Korvova/gitar/blob/main/2-0/make_3mf.py) — STL → столы .3mf через Bambu Studio CLI; `make_3mf.py 74 75` — только эти столы. Готовые столы — в `3-0/Print3mf` | Столы копировать в `3-0/Print3mf`: владелец печатает оттуда | ✅ |
| 13.11 | Платы: разводка и G-code | KiCad python: [build_board.py](https://github.com/Korvova/gitar/blob/main/plata-4-motora/build_board.py) → плата, [make_gcode.py](https://github.com/Korvova/gitar/blob/main/plata-4-motora/make_gcode.py) → маркер, сверло (ноль по крестику), обрезка; [make_models.py](https://github.com/Korvova/gitar/blob/main/plata-4-motora/make_models.py) — 3D-модели модулей | В строке `M0` не писать скобки внутри комментария — GRBL отвечает `error:2` | ✅ |
| 13.12 | Картинки и сцены | pyvista-рендеры шагов сборки (`2-0/render_*.py`), сцены Blender (`2-0/scene_*.py` → `.blend`, пробел — анимация), схемы плат (`tools/render_plata_shema.py`, `plata-4-motora/render_*.py`) | | ✅ |
| 13.13 | Публикация вики | [wiki_publish.py](https://github.com/Korvova/gitar/blob/main/tools/wiki_publish.py) — страницы из папки `wiki/` в Яндекс Вики, одна страница за запуск: `WIKI_TOKEN=… python tools/wiki_publish.py t-soft` | Порядок страниц в дереве вики API не меняет — только оглавление эпика | ✅ |
| 13.14 | Заливка прошивок | arduino-cli в `C:\App\esp-mini\tools`, FQBN `esp32:esp32:esp32`; порт ESP на плате — COM7 или COM8 (смотреть в диспетчере устройств). Подробно — [Прошивка ESP32](/homepage/iniciativa.-razrabotka/jepik-ruka-gitara/proshivka-esp32) | Родной ctags arduino-cli падает — стоит заглушка, поэтому функции в .ino объявлять до использования | ✅ |
