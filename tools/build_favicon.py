#!/usr/bin/env python3
"""Pixel hard-hat favicon (code-drawn, matches the game's palette).

Writes src/favicon.svg (browser tab), src/favicon-32.png (fallback), src/apple-touch-icon.png
(phone home screen) and favicon.ico at the repo root (for /favicon.ico requests on GitHub Pages).
build.py inlines the first three into the game.
"""
import pathlib
from PIL import Image, ImageDraw

root = pathlib.Path(__file__).resolve().parent.parent
HAT = [
    "................",
    "................",
    "......kkkk......",
    "....kkyhhykk....",
    "...kyyyhhyyyk...",
    "..kyhyyhhyyysk..",
    "..kyhyyhhyyysk..",
    "..kyhyyhhyyysk..",
    "..kyyyyhhyyysk..",
    "..kyyyyyyyyssk..",
    ".kkkkkkkkkkkkkk.",
    "kyyyyyyyyyyyyssk",
    "kssssssssssssssk",
    ".kkkkkkkkkkkkkk.",
    "................",
    "................",
]
PAL = {"k": "#0d0b08", "y": "#e8b923", "h": "#fff3c4", "s": "#a9823b"}
assert all(len(r) == 16 for r in HAT)

# SVG: one rect per horizontal run of a color
rects = []
for y, row in enumerate(HAT):
    x = 0
    while x < 16:
        c = row[x]
        if c == ".":
            x += 1; continue
        x2 = x
        while x2 < 16 and row[x2] == c: x2 += 1
        rects.append(f'<rect x="{x}" y="{y}" width="{x2-x}" height="1" fill="{PAL[c]}"/>')
        x = x2
svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" shape-rendering="crispEdges">'
       + "".join(rects) + "</svg>")
(root / "src" / "favicon.svg").write_text(svg)

def hat_img(scale, bg=None, size=None, pad_y=0):
    size = size or 16 * scale
    im = Image.new("RGBA", (size, size), bg or (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    ox = (size - 16 * scale) // 2; oy = (size - 16 * scale) // 2 + pad_y
    for y, row in enumerate(HAT):
        for x, c in enumerate(row):
            if c != ".":
                d.rectangle([ox + x * scale, oy + y * scale, ox + (x + 1) * scale - 1, oy + (y + 1) * scale - 1], fill=PAL[c])
    return im

hat_img(2).save(root / "src" / "favicon-32.png")
hat_img(10, bg="#1d2f8a", size=180).convert("RGB").save(root / "src" / "apple-touch-icon.png")   # iOS needs opaque
hat_img(3).save(root / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
print("favicon written")
