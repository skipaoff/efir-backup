#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Проверка перед эфиром: все ли экраны на месте и живы ли ссылки результатов."""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
EKRANY = [
    ("Сайт",             "01-sajt/Экран.html"),
    ("Видеоконсультант", "02-zvonok/Видеоконсультант.html"),
    ("Продавец",         "03-telegram/Продавец.html"),
    ("Ролик",            "04-video/vitrina/index.html"),
    ("Реклама",          "05-reklama/Реклама.html"),
]
SSYLKI = [
    ("сайт клиники",        "https://comfort-stom-1.vercel.app/"),
    ("сайт со звонком",     "https://comfort-stom-2.vercel.app/"),
    ("сайт с продавцом",    "https://comfort-stom-3.vercel.app/"),
]
ok = True


def stroka(good, text):
    global ok
    if not good:
        ok = False
    print("  %s %s" % ("✓" if good else "×", text))


def zhivaya(url):
    try:
        r = subprocess.run(["curl", "-sSL", "-o", os.devnull, "-w", "%{http_code}",
                            "--max-time", "15", url], capture_output=True, text=True, timeout=25)
        return int((r.stdout or "0").strip() or 0)
    except Exception:
        return 0


print("\nЭкраны")
for imya, rel in EKRANY:
    p = os.path.join(HERE, rel)
    est = os.path.exists(p)
    stroka(est, "%-18s %s" % (imya, ("%d КБ" % (os.path.getsize(p) / 1024)) if est else "нет файла"))

print("\nВитрина ролика")
vit = os.path.join(HERE, "04-video", "vitrina")
nado = ["scenarii.js", "lib", "assets"]
for n in nado:
    stroka(os.path.exists(os.path.join(vit, n)), n)

print("\nСсылки результатов")
for imya, url in SSYLKI:
    kod = zhivaya(url)
    stroka(kod == 200, "%-18s %s" % (imya, kod or "не отвечает"))

print("\n%s\n" % ("Всё на месте, можно в эфир." if ok else "Есть незакрытые пункты — смотри строки с ×."))
sys.exit(0 if ok else 1)
