#!/usr/bin/env python3
"""Uphill Street (top-down) art: recolor the Canva BMP truck's rolls to straw beige and paint the
BMP Supplies five-stripe mark (navy) on the cab's white roof panel -> art/uphill/truck_bmp.png."""
import colorsys, pathlib
from PIL import Image
root = pathlib.Path(__file__).resolve().parent.parent
im = Image.open(root / "art/uphill/truck.png").convert("RGBA"); px = im.load()
# rolls: less orange, more natural straw beige (same treatment as the side-view truck)
for y in range(im.height):
    for x in range(im.width):
        r, g, b, a = px[x, y]
        if not a: continue
        h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
        if 0.03 < h < 0.125 and s > 0.35 and y > im.height * 0.25:
            rr, gg, bb = colorsys.hls_to_rgb(0.105, min(0.82, l * 1.08 + 0.04), s * 0.45)
            px[x, y] = (int(rr * 255), int(gg * 255), int(bb * 255), a)
# the white roof panel on the cab: bounding box of near-white pixels in the top quarter
white = [(x, y) for y in range(im.height // 4) for x in range(im.width)
         if px[x, y][3] and min(px[x, y][:3]) > 200]
x0, x1 = min(p[0] for p in white), max(p[0] for p in white)
y0, y1 = min(p[1] for p in white), max(p[1] for p in white)
NAVY = (27, 42, 92, 255)
for r in range(y0 + 1, y1, 2):            # five-stripe mark from the BMP logo
    for c in range(x0 + 1, x1): px[c, r] = NAVY
im.save(root / "art/uphill/truck_bmp.png")
print("roof panel", (x0, y0, x1, y1))
