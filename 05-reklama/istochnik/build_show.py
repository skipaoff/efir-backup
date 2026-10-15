# -*- coding: utf-8 -*-
"""Собирает экран работы модуля: ядро одно, сцена своя.

Запуск:  python3 build_show.py           — собрать все модули
         python3 build_show.py 05-ads    — только один

Ядро (шапка, стопка шагов, полоса агентов, карточка «Готово») лежит в
show/core.html. Модуль добавляет к нему четыре файла:
  mock_NN.html / mock_NN.css — макет, который виден весь прогон
  scene_NN.js                — что показывать на каждом шаге
  data_NN.js                 — состав агентов и список шагов
"""
import base64
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
SHOW = HERE / "show"
SPRITES_DIR = HERE / "assets" / "pixel"

MODULES = {
    "01-leads": dict(
        n="01",
        page_title="Стоматологии Киева с Телеграмом",
        title="Поиск клиентов",
        who="Стоматологии Киева · 15 мест с проверенным Телеграмом",
        fin="Список готов: 16 клиник. У каждой — оценка, адрес, номер из Телеграма и кнопка «Написать».",
        go="Скопировать все номера",
        url="#leads",
    ),
    "02-site": dict(
        n="02",
        page_title="Сайт Comfort Dental",
        title="Сайт клиники с нуля",
        who="Стоматологія Comfort · Троєщина, Київ · ₴400 в день",
        fin="Сайт готов: главная и восемь страниц услуг, запись в два клика, на телефоне тоже работает.",
        go="Открыть сайт",
        url="https://comfort-stom-1.vercel.app/",
        extra={"__SITE_DESK__": "assets/site/desk.jpg", "__SITE_MOB__": "assets/site/mob.jpg",
               "__SITE_VHID__": "assets/site/vhid.jpg", "__SITE_KABINET__": "assets/site/kabinet.jpg",
               "__SITE_VINIR__": "assets/site/vinir.jpg", "__SITE_RESULT__": "assets/site/result.jpg",
               "__REAL_SAIT__": "assets/creo2/real-sait.jpg"},
    ),
    "03-video": dict(
        n="03",
        page_title="Видеоконсультант Comfort Dental",
        title="Видеоконсультант на сайт",
        who="Стоматологія Comfort · Троєщина, Київ",
        fin="Консультант отвечает на сайте: разговаривает голосом, отвечает на вопросы и записывает на приём.",
        go="Открыть сайт со звонком",
        url="https://comfort-stom-2.vercel.app/",
        extra={"__SITE_DESK__": "assets/site/desk.jpg"},
    ),
    "04-creo": dict(
        n="04",
        page_title="Ролик Comfort Dental",
        title="Видео-креатив для рекламы",
        who="Стоматологія Comfort · відбілювання Magic Smile · 9:16, 39 секунд",
        fin="Мастер готов: 39 секунд, вертикальный, с озвучкой, субтитрами и перебивками. Он же уходит в рекламу на следующем шаге.",
        go="Смотреть ролик",
        url="#creo",
        extra={"__C2_SAIT__": "assets/creo2/real-sait.jpg", "__C2_CENY__": "assets/creo2/real-ceny.jpg",
               "__C2_FOTO__": "assets/creo2/foto.jpg", "__C2_BOARD__": "assets/creo2/raskadrovka.jpg",
               "__C2_KADRY__": "assets/creo2/kadry.jpg", "__C2_VOLNA__": "assets/creo2/volna.png",
               "__C2_SUBS__": "assets/creo2/subtitry.jpg"},
    ),
    "05-ads": dict(
        n="05",
        page_title="Реклама Comfort Dental",
        title="Реклама в Facebook и Instagram",
        who="Стоматологія Comfort · Троєщина, Київ · 100 долларов на старт",
        fin="Кампания включена: видео крутится в Instagram и Facebook, 100 долларов на старт, старт завтра в 9:00. Люди с неё пишут продавцу в Telegram. Объявление — по кнопке.",
        go="Открыть объявление",
        url="https://adsmanager.facebook.com/adsmanager",
    ),
    "06-seller": dict(
        n="06",
        page_title="Продавец Comfort Dental",
        title="AI-продавец в Telegram",
        who="Стоматологія Comfort · Троєщина · AI-администратор в Telegram",
        fin="Продавец на связи, и на сайте появилась кнопка Telegram. Жми её — откроется чат с готовым сообщением: продавец встретит кружком, назовёт цену, запишет и примет предоплату.",
        extra={"__CIRCLE__": "assets/seller/circle.mp4", "__CIRCLE_THUMB__": "assets/seller/circle.jpg"},
        go="Открыть сайт с продавцом",
        url="https://comfort-stom-3.vercel.app/",
    ),
}


def assets():
    vlad = "data:image/jpeg;base64," + base64.b64encode((HERE / "assets" / "vlad.jpg").read_bytes()).decode()
    creo = "data:video/mp4;base64," + base64.b64encode((HERE / "assets" / "creo.mp4").read_bytes()).decode()
    sprites = ["data:image/png;base64," + base64.b64encode((SPRITES_DIR / ("char_%d.png" % i)).read_bytes()).decode()
               for i in range(6)]
    return vlad, creo, json.dumps(sprites)


def links():
    """Ссылки результатов лежат отдельно: поменял одну строку — и пересобрал."""
    path = HERE / "links.json"
    return json.loads(path.read_text()) if path.exists() else {}


def build(slug):
    m = dict(MODULES[slug])
    m.update(links().get(slug, {}))
    core = (SHOW / "core.html").read_text()
    # стиль модуля идёт последним, чтобы он мог перебить ядро
    core = core.replace("__STAGE_CSS__\n", "").replace("</style>", "__STAGE_CSS__\n</style>")
    vlad, creo, sprites = assets()
    page = (core
            .replace("__STAGE_CSS__", (SHOW / ("mock_%s.css" % m["n"])).read_text())
            .replace("__STAGE_HTML__", (SHOW / ("mock_%s.html" % m["n"])).read_text())
            .replace("__SCENE_JS__", (SHOW / ("scene_%s.js" % m["n"])).read_text())
            .replace("__DATA_JS__", (SHOW / ("data_%s.js" % m["n"])).read_text())
            .replace("__PAGE_TITLE__", m["page_title"])
            .replace("__TITLE__", m["title"])
            .replace("__WHO__", m["who"])
            .replace("__FIN_TEXT__", m["fin"])
            .replace("__GO__", m["go"])
            .replace("__URL__", m["url"])
            .replace("__SPRITES__", sprites)
            .replace("__VLAD__", vlad)
            .replace("__CREO__", creo))
    for key, rel in m.get("extra", {}).items():
        data = base64.b64encode((HERE / rel).read_bytes()).decode()
        mime = {".mp4": "video/mp4", ".png": "image/png"}.get(pathlib.Path(rel).suffix, "image/jpeg")
        page = page.replace(key, "data:%s;base64,%s" % (mime, data))
    import re
    left = sorted(set(re.findall(r"__[A-Z_]+__", page)))
    assert not left, left
    out = HERE / ("show-%s.html" % slug)
    out.write_text(page)
    print("%-10s %7d байт → %s" % (slug, len(page), out.name))


HOST_SKELETON = ('<!doctype html>\n<html lang="ru">\n<head>\n<meta charset="utf-8">\n'
                 '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
                 '<meta name="robots" content="noindex">\n<style>body{margin:0}[hidden]{display:none!important}</style>\n')


def host(slug, outdir):
    """Копия экрана для сайта: тот же экран, но с обычным каркасом страницы."""
    page = (HERE / ("show-%s.html" % slug)).read_text()
    head_end = page.index("</style>") + len("</style>")
    out = HOST_SKELETON + page[:head_end] + "\n</head>\n<body>\n" + page[head_end:] + "\n</body>\n</html>\n"
    target = pathlib.Path(outdir) / ("%s.html" % slug)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(out)
    print("  хостинг → %s" % target)


if __name__ == "__main__":
    args = sys.argv[1:]
    hosted = None
    if "--host" in args:
        i = args.index("--host"); hosted = args[i + 1]; args = args[:i] + args[i + 2:]
    for slug in (args or MODULES):
        build(slug)
        if hosted:
            host(slug, hosted)
