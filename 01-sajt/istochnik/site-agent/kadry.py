# -*- coding: utf-8 -*-
"""Режет лист ходьбы на отдельные кадры и ставит их в общую рамку.

Модель раскидывает фигуры по листу неравномерно и может обрезать крайний
кадр. Поэтому кадры ищутся по самим фигурам, а не делением на равные части,
и потом вклеиваются в одинаковую рамку по нижней точке ног: иначе персонаж
на анимации прыгает.

Запуск:  python .claude/skills/site-agent/kadry.py assets/walk-test.png hod

Changes when: меняется лист ходьбы или размер кадра.

Anti-goal: не додумывает недостающие кадры и не растягивает обрезанные.
"""
import io
import os
import sys

try:
    from PIL import Image
except ImportError:
    sys.exit("нужен Pillow: python -m pip install pillow")

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))

FRAME = 300        # сторона готового кадра
MIN_W = 40         # уже этого фигурой не считаем


def columns_with_figure(im, bg, thr=16):
    """Столбцы, где есть фигура. У прозрачного листа смотрим альфу, у обычного яркость."""
    w, h = im.size
    if im.mode == "RGBA":
        px = im.load()
        live = []
        for x in range(w):
            hit = False
            for y in range(0, h, 3):
                if px[x, y][3] > 24:
                    hit = True
                    break
            live.append(hit)
        return live
    grey = im.convert("L")
    px = grey.load()
    live = []
    for x in range(w):
        hit = False
        for y in range(0, h, 3):
            if px[x, y] > bg + thr:
                hit = True
                break
        live.append(hit)
    return live


def spans(live):
    """Непрерывные куски живых столбцов это отдельные фигуры."""
    out, start = [], None
    for x, v in enumerate(live):
        if v and start is None:
            start = x
        elif not v and start is not None:
            if x - start >= MIN_W:
                out.append((start, x))
            start = None
    if start is not None and len(live) - start >= MIN_W:
        out.append((start, len(live)))
    return out


def density(im, x0, x1):
    """Сколько непрозрачных пикселей в каждом столбце куска."""
    alpha = im.mode == "RGBA"
    px = im.load() if alpha else im.convert("L").load()
    h = im.size[1]
    col = []
    for x in range(x0, x1):
        n = 0
        for y in range(0, h, 3):
            v = px[x, y][3] if alpha else px[x, y]
            if v > (24 if alpha else 40):
                n += 1
        col.append(n)
    return col


def split_wide(im, figs):
    """Соседние кадры на листе часто соприкасаются и слипаются в одну фигуру.
    Слишком широкий кусок режем там, где фигура тоньше всего."""
    if len(figs) < 2:
        return figs
    widths = sorted(f[1] - f[0] for f in figs)
    norm = widths[len(widths) // 2]
    out = []
    for x0, x1 in figs:
        w = x1 - x0
        parts = int(round(w / float(norm)))
        if w < norm * 1.5 or parts < 2:
            out.append((x0, x1))
            continue
        col = density(im, x0, x1)
        cuts = []
        for k in range(1, parts):
            aim = int(w * k / float(parts))
            lo, hi = max(1, aim - int(norm * 0.28)), min(w - 1, aim + int(norm * 0.28))
            if hi <= lo:
                continue
            best = min(range(lo, hi), key=lambda t: col[t])
            cuts.append(x0 + best)
        edges = [x0] + cuts + [x1]
        for k in range(len(edges) - 1):
            if edges[k + 1] - edges[k] >= MIN_W:
                out.append((edges[k], edges[k + 1]))
        print("   слипшийся кусок разрезан на", len(edges) - 1)
    return out


def vertical_bounds(im, x0, x1, bg, thr=16):
    alpha = im.mode == "RGBA"
    px = im.load() if alpha else im.convert("L").load()
    h = im.size[1]
    top, bot = None, None
    for y in range(h):
        row = False
        for x in range(x0, x1, 3):
            if (px[x, y][3] > 24) if alpha else (px[x, y] > bg + thr):
                row = True
                break
        if row:
            if top is None:
                top = y
            bot = y
    return top, bot


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "assets/walk-test.png"
    name = sys.argv[2] if len(sys.argv) > 2 else "hod"
    if not os.path.isabs(src):
        src = os.path.join(ROOT, src)
    if not os.path.exists(src):
        sys.exit("нет листа: " + src)

    sheet = Image.open(src)
    sheet = sheet.convert("RGBA") if "A" in sheet.getbands() else sheet.convert("RGB")
    W, H = sheet.size
    bg = 0 if sheet.mode == "RGBA" else sheet.convert("L").getpixel((4, 4))
    outdir = os.path.join(ROOT, "assets", name)
    os.makedirs(outdir, exist_ok=True)

    figs = spans(columns_with_figure(sheet, bg))
    figs = split_wide(sheet, figs)
    print("нашла фигур:", len(figs))

    # общая высота фигуры, чтобы масштаб был одинаковый во всех кадрах
    heights = []
    keep = []
    for x0, x1 in figs:
        t, b = vertical_bounds(sheet, x0, x1, bg)
        if t is not None:
            heights.append(b - t)
            keep.append((x0, x1))
    figs = keep
    if not heights:
        sys.exit("фигур не видно, проверь фон листа")
    tall = max(heights)
    scale = (FRAME * 0.82) / float(tall)
    # мелочь рядом с фигурой это отвалившийся пропс, а не отдельный кадр
    wide = sorted(f[1] - f[0] for f in figs)
    norm_w = wide[len(wide) // 2]
    figs = [f for f, hh in zip(figs, heights)
            if hh >= tall * 0.55 and (f[1] - f[0]) >= norm_w * 0.45]
    print("кадров после отсева мелочи:", len(figs))

    kept = 0
    for i, (x0, x1) in enumerate(figs):
        # крайние обрезанные кадры пропускаем: их не починить
        if x0 <= 2 or x1 >= W - 2:
            print("кадр %d обрезан краем листа, пропускаю" % (i + 1))
            continue
        t, b = vertical_bounds(sheet, x0, x1, bg)
        if t is None:
            continue
        fig = sheet.crop((x0, t, x1, b))
        nw = max(1, int(fig.width * scale))
        nh = max(1, int(fig.height * scale))
        fig = fig.resize((nw, nh), Image.LANCZOS)

        canvas = Image.new("RGBA", (FRAME, FRAME), (0, 0, 0, 0))
        # по горизонтали в центр, по вертикали ноги на одну линию
        pos = ((FRAME - nw) // 2, int(FRAME * 0.93) - nh)
        canvas.paste(fig, pos, fig if fig.mode == "RGBA" else None)
        kept += 1
        out = os.path.join(outdir, "%02d.webp" % kept)
        canvas.save(out, "WEBP", quality=90, method=6, lossless=False)
        print("кадр %02d  %sx%s  %.0f КБ" % (kept, nw, nh, os.path.getsize(out) / 1024.0))

    print("готово кадров:", kept, "в", outdir)


if __name__ == "__main__":
    main()
