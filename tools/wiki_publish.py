# -*- coding: utf-8 -*-
"""Публикация документации проекта в Яндекс Вики.

Страницы лежат в папке wiki/ рядом с репозиторием: имя файла = адрес страницы,
index.md — сам эпик.

Запуск:
    WIKI_TOKEN=<токен> python tools/wiki_publish.py            все страницы
    WIKI_TOKEN=<токен> python tools/wiki_publish.py t-struny   только эту

Токен в репозиторий не коммитим — берём из переменной окружения WIKI_TOKEN.
Получить новый: https://oauth.yandex.ru/authorize?response_type=token&client_id=22fcafe69ac24efe82098b7d8d5d869d
"""
import json
import os
import sys
import urllib.request
import urllib.error

BASE = "https://api.wiki.yandex.net/v1"
ORG = "d0d0f076-05d6-4525-84fd-206271e76feb"
ROOT = "homepage/iniciativa.-razrabotka/jepik-ruka-gitara"

# заголовки страниц: имя файла -> заголовок в вики
TITLES = {
    "index": "⌛🚀Эпик. Рука гитара",
    "t-struny": "✅Т. Струны",
    "t-grif": "⌛Т. Гриф и аппликатура",
    "t-korpus": "⌛Т. Корпус и дека",
    "t-elektronika": "⌛Т. Электроника и звук",
    "t-taktilka": "💤Т. Тактильная обратная связь",
    "arxitektura": "Архитектура и стек",
    "pechat-sborka": "Печать и сборка",
    "proshivka-esp32": "❓Прошивка ESP32: заливка без BOOT",
    "t-marketing": "⌛Т. маркетинг",
    "t-3d-modeli": "⌛Т. 3д модели",
    "t-plata": "⌛Т. Плата",
}

TOKEN = os.environ.get("WIKI_TOKEN", "")
if not TOKEN:
    sys.exit("Не задана переменная окружения WIKI_TOKEN")

HEADERS = {
    "Authorization": "OAuth " + TOKEN,
    "X-Collab-Org-Id": ORG,
    "Content-Type": "application/json",
}

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIKI_DIR = os.path.join(HERE, "wiki")


def request(method, path, payload=None):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload else None
    req = urllib.request.Request(BASE + path, data=data, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, (json.loads(body) if body else {})
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")


def publish(name, text):
    slug = ROOT if name == "index" else "%s/%s" % (ROOT, name)
    title = TITLES.get(name, name)
    # страница есть — обновляем по её id, нет — создаём
    code, page = request("GET", "/pages?slug=%s" % slug)
    if code == 200 and isinstance(page, dict) and page.get("id"):
        code, res = request("POST", "/pages/%d" % page["id"],
                            {"title": title, "content": text})
        action = "обновлена"
    else:
        code, res = request("POST", "/pages",
                            {"slug": slug, "title": title, "content": text})
        action = "создана"
    ok = code in (200, 201)
    print("%-16s %s %s" % (name, "OK    " if ok else "ОШИБКА %s" % code,
                           action if ok else str(res)[:160]))
    return ok


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    names = sorted(f[:-3] for f in os.listdir(WIKI_DIR) if f.endswith(".md"))
    if only:
        if only not in names:
            sys.exit("Нет страницы %s в %s" % (only, WIKI_DIR))
        names = [only]
    elif "index" in names:                     # эпик публикуем первым
        names = ["index"] + [n for n in names if n != "index"]
    bad = 0
    for name in names:
        path = os.path.join(WIKI_DIR, name + ".md")
        with open(path, encoding="utf-8") as f:
            if not publish(name, f.read()):
                bad += 1
    sys.exit(1 if bad else 0)


main()
