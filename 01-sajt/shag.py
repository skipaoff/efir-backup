#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Двигает экран сайта на один этап и пересобирает его.

    python3 shag.py 1          — первый этап в работу
    python3 shag.py 4          — первые три готовы, четвёртый в работе
    python3 shag.py finish     — смена закончена
    python3 shag.py reset      — вернуть на старт

После каждой команды публикуй Экран.html инструментом Artifact по тому же пути.
"""
import io, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
IST = os.path.join(HERE, "istochnik")
STATE = os.path.join(IST, "state.json")
SKRIPT = os.path.join(IST, "site-agent", "artifact.py")

# сколько примерно идёт этап, чтобы часы на экране не врали
NA_ETAP = 45


def komanda(d, nomer):
    """Человек работает, если работает его этап; закончил — если все его этапы готовы."""
    for t in d["team"]:
        imya = t["name"].replace("AI-", "")
        moi = [s for s in d["steps"] if s.get("by", "").lower() == imya.lower()]
        if any(s["status"] == "run" for s in moi):
            t["status"] = "run"
        elif moi and all(s["status"] == "done" for s in moi):
            t["status"] = "done"
        else:
            t["status"] = "wait"


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    cmd = sys.argv[1]
    d = json.loads(io.open(STATE, encoding="utf-8").read())
    vsego = len(d["steps"])

    if cmd == "reset":
        for s in d["steps"]: s["status"] = "wait"
        d["livetext"] = "готов к запуску"; d["elapsed"] = 0
    elif cmd == "finish":
        for s in d["steps"]: s["status"] = "done"
        d["livetext"] = "смена закончена"; d["elapsed"] = vsego * NA_ETAP
    else:
        n = int(cmd)
        if n < 1 or n > vsego:
            sys.exit("этапа %d нет, всего %d" % (n, vsego))
        for i, s in enumerate(d["steps"], 1):
            s["status"] = "done" if i < n else ("run" if i == n else "wait")
        d["livetext"] = d["steps"][n - 1]["title"]
        d["elapsed"] = (n - 1) * NA_ETAP
    komanda(d, cmd)
    io.open(STATE, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=2))
    subprocess.run([sys.executable, SKRIPT], check=True, capture_output=True)
    print(os.path.join(HERE, "Экран.html"))


if __name__ == "__main__":
    main()
