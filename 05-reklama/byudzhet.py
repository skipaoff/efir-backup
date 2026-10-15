#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Вписывает ответ человека про деньги и площадки в экран рекламы.

    python3 byudzhet.py "100 долларов" "Instagram и Facebook"
    python3 byudzhet.py "₴400 в день"

Без этого экран говорит свою цифру, и она спорит с тем, что человек только что
сказал вслух. Скрипт правит данные сцены и пересобирает Реклама.html.
"""
import io, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
IST = os.path.join(HERE, "istochnik")
SHOW = os.path.join(IST, "show")
GOTOVO = os.path.join(HERE, "Реклама.html")

# что меняем: было → чем заменить, подставляя ответ
PRAVKI = [
    ("scene_05.js", '["₴400 в день","старт завтра в 9:00"]', '["%(dengi)s","старт завтра в 9:00"]'),
    ("data_05.js",  '"на неделю выходит ₴2 800"', '"деньги делим между площадками поровну"'),
    ("scene_05.js", 'cBud:"₴400 / день"', 'cBud:"%(dengi)s"'),
    ("scene_05.js", 'cNote:"Reels и Stories, старт завтра в 9:00"', 'cNote:"%(gde)s, старт завтра в 9:00"'),
    ("data_05.js",  '"₴400 в день, старт завтра в 9:00"', '"%(dengi)s, старт завтра в 9:00"'),
]


def tekushchee(text, obrazec):
    """Берём то, что сейчас стоит в файле на месте образца."""
    m = re.search(re.escape(obrazec).replace(r"\₴400\ в\ день", r"[^\"]+"), text)
    return m.group(0) if m else None


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    dengi = sys.argv[1].strip()
    gde = sys.argv[2].strip() if len(sys.argv) > 2 else "Reels и Stories"

    for fayl, bylo, stalo in PRAVKI:
        p = os.path.join(SHOW, fayl)
        s = io.open(p, encoding="utf-8").read()
        # ищем и прежний образец, и уже подставленный раньше ответ
        shablon = re.escape(bylo).replace("₴400\\ в\\ день", '[^"]+').replace("₴400\\ /\\ день", '[^"]+')
        shablon = shablon.replace("Reels\\ и\\ Stories,\\ старт", '[^"]+, старт')
        novoe = stalo % {"dengi": dengi, "gde": gde}
        s2, n = re.subn(shablon, novoe.replace("\\", "\\\\"), s, count=1)
        if not n:
            print("не нашёл место в %s — пропускаю" % fayl)
            continue
        io.open(p, "w", encoding="utf-8").write(s2)

    # подпись под заголовком и финальная карточка живут в сборщике
    bp = os.path.join(IST, "build_show.py")
    b = io.open(bp, encoding="utf-8").read()
    # правим только блок 05-ads, иначе задеваем подпись сайта
    i = b.find('"05-ads": dict(')
    j = b.find('\n    ),', i)
    blok = b[i:j]
    blok = re.sub(r'who="([^"]*Київ)[^"]*"', lambda m: 'who="%s · %s"' % (m.group(1), dengi), blok, count=1)
    blok = re.sub(r'fin="Кампания включена: видео крутится в [^,]+, [^,]+, старт',
                  'fin="Кампания включена: видео крутится в %s, %s, старт' % (gde, dengi), blok, count=1)
    b = b[:i] + blok + b[j:]
    io.open(bp, "w", encoding="utf-8").write(b)

    subprocess.run([sys.executable, os.path.join(IST, "build_show.py"), "05-ads",
                    "--host", os.path.join(IST, "_gotovoe")],
                   cwd=IST, check=True, capture_output=True)
    sobrannyy = os.path.join(IST, "_gotovoe", "05-ads.html")
    io.open(GOTOVO, "w", encoding="utf-8").write(io.open(sobrannyy, encoding="utf-8").read())
    print(GOTOVO)


if __name__ == "__main__":
    main()
