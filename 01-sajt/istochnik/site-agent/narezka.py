# -*- coding: utf-8 -*-
"""Режет лист персонажей 3x3 на девять картинок и обрезает их по фигуре.

Лист приходит с Higgsfield одной картинкой: девять роботов в сетке на общем
тёмном фоне. Здесь он режется на ячейки, каждая обрезается по видимой фигуре
и уменьшается до размера, в котором поедет в артефакт.

Запуск:  python .claude/skills/site-agent/narezka.py assets/roboty-list.png

Changes when: меняется лист персонажей или нужный размер аватарок.

Anti-goal: не «улучшает» картинку фильтрами, только режет и жмёт.
"""
import io
import os
import sys

try:
    from PIL import Image
except ImportError:
    sys.exit("нужен Pillow: python -m pip install pillow")

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
OUTDIR = os.path.join(ROOT, "assets", "roboty")

# порядок ролей на листе: слева направо, сверху вниз
ROLES = [
    "issledovatel",   # лупа
    "analitik",       # планшет с диаграммой
    "marketolog",     # ДНК
    "strateg",        # лестница
    "kopirayter",     # перо
    "arhitektor",     # чертёж
    "konversia",      # чек-лист
    "videograf",      # камера
    "razrabotchik",   # паяльник
]

CELL_MAX = 460      # сторона готовой аватарки
PAD = 0.04          # запас вокруг фигуры, доля от стороны ячейки


def bbox_of_figure(cell, bg):
    """Границы фигуры: всё, что заметно светлее общего фона."""
    grey = cell.convert("L")
    w, h = grey.size
    px = grey.load()
    thr = bg + 14
    x0, y0, x1, y1 = w, h, 0, 0
    step = 2
    for y in range(0, h, step):
        for x in range(0, w, step):
            if px[x, y] > thr:
                if x < x0: x0 = x
                if y < y0: y0 = y
                if x > x1: x1 = x
                if y > y1: y1 = y
    if x1 <= x0 or y1 <= y0:
        return None
    return x0, y0, x1, y1


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "assets", "roboty-list.png")
    if not os.path.isabs(src):
        src = os.path.join(ROOT, src)
    if not os.path.exists(src):
        sys.exit("нет листа персонажей: " + src)

    sheet = Image.open(src).convert("RGB")
    W, H = sheet.size
    cw, ch = W // 3, H // 3
    os.makedirs(OUTDIR, exist_ok=True)

    # фон берём из угла листа, там точно нет фигуры
    bg = sheet.convert("L").getpixel((4, 4))

    for i, role in enumerate(ROLES):
        col, row = i % 3, i // 3
        cell = sheet.crop((col * cw, row * ch, (col + 1) * cw, (row + 1) * ch))
        box = bbox_of_figure(cell, bg)
        if box:
            pad = int(min(cw, ch) * PAD)
            x0 = max(0, box[0] - pad); y0 = max(0, box[1] - pad)
            x1 = min(cw, box[2] + pad); y1 = min(ch, box[3] + pad)
            # держим квадрат, чтобы все девять были одного формата
            side = max(x1 - x0, y1 - y0)
            cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
            x0 = max(0, cx - side // 2); y0 = max(0, cy - side // 2)
            cell = cell.crop((x0, y0, min(cw, x0 + side), min(ch, y0 + side)))
        if cell.width > CELL_MAX:
            cell = cell.resize((CELL_MAX, CELL_MAX), Image.LANCZOS)
        out = os.path.join(OUTDIR, role + ".webp")
        cell.save(out, "WEBP", quality=88, method=6)
        print("%-14s %sx%s  %.0f КБ" % (role, cell.width, cell.height,
                                        os.path.getsize(out) / 1024.0))

    total = sum(os.path.getsize(os.path.join(OUTDIR, r + ".webp")) for r in ROLES)
    print("итого девять картинок: %.0f КБ" % (total / 1024.0))
    if total > 3 * 1024 * 1024:
        print("ВНИМАНИЕ: тяжело для артефакта, уменьши CELL_MAX")


if __name__ == "__main__":
    main()
