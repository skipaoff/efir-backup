# -*- coding: utf-8 -*-
"""Вырезает персонажа из кадра: фон становится прозрачным.

Без этого персонаж едет по сцене в квадратной плашке своего фона.
Фон на листах генерации однородный и связный, поэтому идём заливкой от
краёв: всё, что дотянулось от рамки и похоже по цвету на фон, стираем.
Внутренние тёмные части робота заливка не трогает, потому что до них
не дойти, не пройдя через светлые края фигуры.

Запуск:  python .claude/skills/site-agent/alfa.py assets/hod

Changes when: меняется фон листов или порог похожести.

Anti-goal: не выедает сам силуэт. Лучше оставить каёмку фона, чем дыру в роботе.
"""
import io
import os
import sys
from collections import deque

try:
    from PIL import Image
except ImportError:
    sys.exit("нужен Pillow: python -m pip install pillow")

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
TOL = 26          # насколько цвет может отличаться от фона и всё ещё считаться фоном
FEATHER = 1       # размытие края, чтобы не было пилы


def close(a, b, tol):
    return abs(a[0] - b[0]) <= tol and abs(a[1] - b[1]) <= tol and abs(a[2] - b[2]) <= tol


def cut(path):
    im = Image.open(path).convert("RGBA")
    w, h = im.size
    px = im.load()
    bg = px[0, 0][:3]

    seen = bytearray(w * h)
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            q.append((x, y))
    for y in range(h):
        for x in (0, w - 1):
            q.append((x, y))

    while q:
        x, y = q.popleft()
        if x < 0 or y < 0 or x >= w or y >= h:
            continue
        k = y * w + x
        if seen[k]:
            continue
        if not close(px[x, y][:3], bg, TOL):
            continue
        seen[k] = 1
        px[x, y] = (0, 0, 0, 0)
        q.append((x + 1, y)); q.append((x - 1, y))
        q.append((x, y + 1)); q.append((x, y - 1))

    if FEATHER:
        alpha = im.split()[3]
        from PIL import ImageFilter
        im.putalpha(alpha.filter(ImageFilter.GaussianBlur(FEATHER)))

    out = os.path.splitext(path)[0] + ".png"
    im.save(out, "PNG", optimize=True)
    if out != path and os.path.exists(path) and path.lower().endswith(".webp"):
        os.remove(path)
    solid = sum(1 for i in range(w * h) if not seen[i])
    return out, solid * 100.0 / (w * h)


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "assets/hod"
    full = target if os.path.isabs(target) else os.path.join(ROOT, target)
    files = []
    if os.path.isdir(full):
        files = [os.path.join(full, f) for f in sorted(os.listdir(full))
                 if f.lower().endswith((".webp", ".png"))]
    elif os.path.exists(full):
        files = [full]
    if not files:
        sys.exit("нечего резать: " + full)

    for f in files:
        out, share = cut(f)
        print("%-28s фигура занимает %.1f%%" % (os.path.basename(out), share))
        if share > 70:
            print("   похоже, фон не вырезался: проверь глазами")


if __name__ == "__main__":
    main()
