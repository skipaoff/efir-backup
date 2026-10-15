# -*- coding: utf-8 -*-
"""Страница состояния 3D-линии: живая сцена, все ассеты и что осталось сделать.

Это рабочее превью для Светы, не деливерабл клиенту. Показывает ровно то,
что уже лежит в assets, поэтому врать не может: чего нет, то не покажется.

Запуск:  python .claude/skills/site-agent/preview3d.py

Changes when: меняется состав ассетов 3D-линии или план работ.

Anti-goal: не рисует готовности, которой нет. Пустая полка значит пустая полка.
"""
import base64
import glob
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import scena  # noqa: E402  сцена и её движок живут там

ROOT = scena.ROOT
OUT = os.path.join(ROOT, "build", "Превью-3D.html")

ROLES = [
    ("issledovatel", "AI-исследователь", "лупа", "читает сайт клиники"),
    ("analitik",     "AI-аналитик",      "планшет с диаграммой", "разбирает конкурентов"),
    ("marketolog",   "AI-маркетолог",    "спираль ДНК", "разбирает клиента"),
    ("strateg",      "AI-стратег",       "лестница", "смотрит, кто дозрел"),
    ("kopirayter",   "AI-копирайтер",    "перо", "пишет тексты"),
    ("arhitektor",   "AI-дизайнер",      "чертёж", "проектирует страницы"),
    ("konversia",    "AI-продавец",      "чек-лист", "считает, кто запишется"),
    ("videograf",    "AI-видеограф",     "камера", "снимает видео"),
    ("razrabotchik", "AI-разработчик",   "паяльник", "собирает сайт"),
]

PLAN = [
    ("done", "Девять персонажей",
     "Разные по цвету и характеру, у каждого свой инструмент. Есть девочки и мальчики, "
     "как ты просила. Один лист генерации, поэтому стиль общий."),
    ("done", "Походка на каждого",
     "Свои кадры ходьбы, шесть фаз, ноги реально переставляются. Персонаж вырезан по фигуре, "
     "без плашки за спиной."),
    ("done", "Своё действие на каждого",
     "Исследователь водит лупой, видеограф крутит камеру, разработчик паяет. "
     "По три-четыре кадра, крутятся в цикле."),
    ("done", "Двухэтажная студия",
     "Серверная, библиотека, стена в стикерах, чертёжный стол, принтер, монтажка, верстак, "
     "наверху лаунж с диваном и кухней."),
    ("warn", "Работа не у всех своя",
     "У четверых кадры работы вышли короче, по три вместо четырёх: на листе слиплись соседние "
     "кадры. Цикл идёт, но чуть резче. Перегенерить эти четыре листа."),
    ("warn", "Пустой стол не встроен",
     "Сгенерён, но в сцене не стоит: сейчас стол появляется вместе с агентом, а должен ждать его "
     "на месте."),
    ("wait", "Связать сцену с этапами",
     "Сейчас сцена крутит свой цикл сама по себе. Нужно, чтобы работал ровно тот, чей этап идёт, "
     "как уже сделано в пиксельном офисе."),
    ("wait", "Свет и звук на события",
     "Вспышка и звук на завершении этапа. В пиксельной версии звук синтезируется в странице, "
     "тут будет так же."),
    ("wait", "Сцена из Blender",
     "Ждём от тебя объёмную сцену. Тогда персонажей можно поставить в настоящую 3D-глубину, "
     "а не в нарисованную. Для агента Влада, скорее всего, не пойдёт, ставим на нашу платформу."),
]

LABEL = {"done": "готово", "warn": "требует правки", "wait": "впереди"}


def uri(path):
    full = path if os.path.isabs(path) else os.path.join(ROOT, path)
    if not os.path.exists(full):
        return ""
    return "data:image/webp;base64," + base64.b64encode(io.open(full, "rb").read()).decode("ascii")


def strip_frames(kind, role, limit=6):
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, "assets", kind, role, "*.webp")))[:limit]:
        u = uri(f)
        if u:
            out.append('<img src="%s" alt="">' % u)
    return "".join(out)


EXTRA_CSS = """
.section{margin-top:26px}
.h2{font-family:Unbounded,Manrope,system-ui,sans-serif;font-size:18px;font-weight:600;
    margin:0 0 4px;letter-spacing:-.01em}
.section p.lead{color:var(--mid);margin:0 0 14px;font-size:14.5px;max-width:70ch}

.crew{display:grid;gap:12px;grid-template-columns:repeat(auto-fill,minmax(268px,1fr))}
.person{border:1px solid var(--line);border-radius:16px;background:var(--panel);padding:14px}
.person .top{display:flex;align-items:center;gap:12px}
.person .ava{width:64px;height:64px;flex:0 0 64px;border-radius:12px;background:#0a1017;
             display:grid;place-items:center;overflow:hidden}
.person .ava img{width:100%;height:100%;object-fit:contain}
.person b{display:block;font-size:15px}
.person span{display:block;font-size:12.5px;color:var(--dim)}
.person .tool{font-family:'JetBrains Mono',ui-monospace,monospace;font-size:10.5px;
              color:var(--neon);letter-spacing:.06em;text-transform:uppercase;margin-top:3px}
.strip{margin-top:11px}
.strip em{font-style:normal;font-family:'JetBrains Mono',ui-monospace,monospace;font-size:9.5px;
          letter-spacing:.12em;text-transform:uppercase;color:#3f5165;display:block;margin-bottom:5px}
.strip div{display:flex;gap:3px;background:#080d14;border:1px solid var(--line);border-radius:9px;
           padding:5px;overflow-x:auto}
.strip img{height:52px;width:auto;flex:0 0 auto}
.strip.short div{border-color:rgba(255,180,84,.4)}

.plan{display:flex;flex-direction:column;gap:9px}
.row{display:flex;gap:13px;align-items:flex-start;border:1px solid var(--line);border-radius:13px;
     background:var(--panel);padding:13px 15px}
.row i{width:9px;height:9px;border-radius:50%;flex:0 0 9px;margin-top:7px;background:var(--neon)}
.row[data-s="warn"] i{background:#ffb454}
.row[data-s="wait"] i{background:#2c3b4d}
.row b{display:block;font-size:15px;margin-bottom:2px}
.row p{margin:0;color:var(--mid);font-size:14px;max-width:78ch}
.row .st{margin-left:auto;font-family:'JetBrains Mono',ui-monospace,monospace;font-size:10px;
         letter-spacing:.08em;text-transform:uppercase;color:var(--dim);border:1px solid var(--line);
         border-radius:999px;padding:3px 9px;white-space:nowrap;align-self:flex-start}
.row[data-s="done"] .st{color:var(--neon);border-color:rgba(60,224,192,.35)}
.row[data-s="warn"] .st{color:#ffb454;border-color:rgba(255,180,84,.35)}
@media (max-width:560px){
  .row{flex-wrap:wrap}
  .row .st{margin-left:0}
}
"""


def build():
    walk = scena.frames  # переиспользуем загрузку кадров сцены

    people = []
    for role, name, tool, doing in ROLES:
        face = uri("assets/roboty/%s.webp" % role)
        hod = strip_frames("hod", role)
        rab = strip_frames("rabota", role)
        n_rab = len(glob.glob(os.path.join(ROOT, "assets", "rabota", role, "*.webp")))
        people.append(
            '<article class="person">'
            '<div class="top"><span class="ava">'
            + ('<img src="%s" alt="%s">' % (face, name) if face else "")
            + '</span><span><b>' + name + '</b><span>' + doing + '</span>'
              '<span class="tool">' + tool + '</span></span></div>'
            + ('<div class="strip"><em>походка</em><div>' + hod + '</div></div>' if hod else "")
            + ('<div class="strip' + (' short' if n_rab < 4 else '') + '"><em>работа, '
               + str(n_rab) + ' кадра</em><div>' + rab + '</div></div>' if rab else "")
            + '</article>')

    rows = []
    for st, title, text in PLAN:
        rows.append('<div class="row" data-s="' + st + '"><i></i><div><b>' + title + '</b>'
                    '<p>' + text + '</p></div><span class="st">' + LABEL[st] + '</span></div>')

    scene_page = scena.build()
    body = scene_page.split('<div class="wrap">', 1)[1].rsplit('</div>', 1)[0]
    # из страницы сцены берём только саму сцену, свои заголовки ставим ниже
    scene_only = body.split('<div class="studio"', 1)[1]
    scene_only = '<div class="studio"' + scene_only.split('<div class="bar">', 1)[0]
    tail = scene_page.split('<script>', 1)[1]

    return """<title>Наш офис 3D</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Unbounded:wght@500;600&family=Manrope:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap">
<style>%s%s</style>
<div class="wrap">
  <span class="lab">наша линия, не для Влада</span>
  <h1>Наш офис 3D</h1>
  <p class="sub">Состояние работ по объёмной версии офиса. Всё, что здесь показано, лежит в проекте: если полка пустая, значит ассета правда нет.</p>

  %s

  <section class="section">
    <div class="h2">Команда и её кадры</div>
    <p class="lead">У каждого свой персонаж, своя походка и своё действие. Ленты ниже это настоящие кадры из проекта, а не картинки для красоты.</p>
    <div class="crew">%s</div>
  </section>

  <section class="section">
    <div class="h2">Что дальше</div>
    <p class="lead">Сверху то, что уже стоит. Жёлтым то, что сделано, но требует переделки. Серым то, за что ещё не брались.</p>
    <div class="plan">%s</div>
  </section>
</div>
<script>%s
""" % (scena.CSS, EXTRA_CSS, scene_only, "".join(people), "".join(rows), tail)


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    io.open(OUT, "w", encoding="utf-8").write(build())
    print("превью собрано: %s (%.2f МБ)" % (OUT, os.path.getsize(OUT) / 1048576.0))


if __name__ == "__main__":
    main()
