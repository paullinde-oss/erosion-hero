#!/usr/bin/env python3
"""Join the Canva semi cab + loaded trailer into the BMP truck, flip it to face left (its driving
direction), and paint the BMP Supplies mark in white on the sleeper panel -> art/vehicles/semi_bmp.png.
The full logo is too wide to stay legible at this size, so the truck carries the five-stripe mark
from the BMP Supplies logo with 'BMP' underneath."""
import colorsys, pathlib
from PIL import Image, ImageOps
root = pathlib.Path(__file__).resolve().parent.parent
cab = Image.open(root / "art/vehicles/semi_cab.png").convert("RGBA")
trailer = Image.open(root / "art/vehicles/semi_trailer.png").convert("RGBA")
# The Canva trailer faces the other way: flip it so its axles are at the back of the rig and its
# nose rides on the cab's fifth wheel. Its landing legs would sit on top of the cab's drive wheels,
# so they're trimmed (legs are cranked up while driving anyway).
trailer = ImageOps.mirror(trailer); tp = trailer.load()
DECK_BOTTOM, AXLES_END = 62, 75
for y in range(DECK_BOTTOM + 1, trailer.height):
    for x in range(AXLES_END, trailer.width): tp[x, y] = (0, 0, 0, 0)
# rolls: less orange, more natural straw beige (yellow straps and dark frame keep their color)
for y in range(trailer.height):
    for x in range(trailer.width):
        r, g, b, a = tp[x, y]
        if not a: continue
        h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
        if 0.03 < h < 0.125 and s > 0.35 and y < DECK_BOTTOM - 4:
            rr, gg, bb = colorsys.hls_to_rgb(0.105, min(0.82, l * 1.08 + 0.04), s * 0.45)
            tp[x, y] = (int(rr * 255), int(gg * 255), int(bb * 255), a)
OVERLAP = 40                                   # trailer nose sits over the cab's fifth wheel
GAP_LIFT = 3                                   # trailer deck rides just above the cab frame
W = trailer.width + cab.width - OVERLAP; H = max(cab.height, trailer.height + GAP_LIFT)
truck = Image.new("RGBA", (W, H))
# trailer first, cab on top: the load sits behind the cab, the way it looks on the road
truck.alpha_composite(trailer, (0, H - trailer.height - GAP_LIFT))
truck.alpha_composite(cab, (trailer.width - OVERLAP, H - cab.height))
truck = ImageOps.mirror(truck)                 # face left
px = truck.load()
# sleeper panel in the unflipped cab spans x 37..62, y 26..64; mirror into truck coordinates
cab_x0 = trailer.width - OVERLAP
panel_left = W - 1 - (cab_x0 + 62); panel_right = W - 1 - (cab_x0 + 37)
panel_top = (H - cab.height) + 28
WHITE = (242, 240, 230, 255)
# five-stripe mark, 12 wide x 9 tall
mark_w = 12; mx = panel_left + (panel_right - panel_left + 1 - mark_w) // 2; my = panel_top + 2
for r in range(0, 9, 2):
    for c in range(mark_w): px[mx + c, my + r] = WHITE
FONT = {"B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
        "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
        "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"]}
text_w = 3 * 6 - 1; tx = panel_left + (panel_right - panel_left + 1 - text_w) // 2; ty = my + 12
for i, ch in enumerate("BMP"):
    for r, row in enumerate(FONT[ch]):
        for c, bit in enumerate(row):
            if bit == "1": px[tx + i * 6 + c, ty + r] = WHITE
truck.save(root / "art/vehicles/semi_bmp.png")
print("truck", truck.size, "panel", panel_left, panel_right)
