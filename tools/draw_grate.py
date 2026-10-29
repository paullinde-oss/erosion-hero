#!/usr/bin/env python3
"""Draw the open storm-drain grate (32x32) as pixel art, following the V slot pattern of
the real grate in art/photo/grate_photo.png. Colors come from the game palette."""
import pathlib
from PIL import Image
root = pathlib.Path(__file__).resolve().parent.parent
S = 32
OUT, RIM_HI, RIM, IRON, IRON_HI, RUST, SLOT, MUD = (
    (31, 20, 16), (185, 181, 170), (138, 134, 124), (92, 90, 85), (138, 134, 124), (138, 82, 48), (31, 20, 16), (125, 99, 66))
img = Image.new("RGBA", (S, S)); px = img.load()
for y in range(S):
    for x in range(S):
        edge = min(x, y, S - 1 - x, S - 1 - y)
        if edge == 0: c = OUT
        elif edge <= 2: c = RIM_HI if (x < y and x <= 2) or (y <= 2 and x < S - 3) else RIM
        else:
            c = IRON
            ix, iy = x - 4, y - 4                          # inner area 24x24, slots inset 1 more px
            inner = 4 <= x <= S - 5 and 4 <= y <= S - 5
            seam = abs(x - (S - 1) / 2) < 1.6               # solid bar down the middle where the V meets
            if inner and not seam:
                d = (x - y) if x < S / 2 else ((S - 1 - x) - y)  # mirror the diagonal for the right half
                if d % 5 in (0, 1): c = SLOT
        px[x, y] = c + (255,)
# light on the top-left edges of each bar, a little rust, and muddy water pooling in the lower slots
for y in range(1, S):
    for x in range(1, S):
        if px[x, y][:3] == IRON and px[x - 1, y - 1][:3] == SLOT: px[x, y] = IRON_HI + (255,)
for (x, y) in [(6, 9), (24, 7), (9, 22), (21, 25), (14, 5), (27, 18), (5, 15), (26, 26), (11, 27), (19, 10)]:
    if px[x, y][:3] in (IRON, IRON_HI): px[x, y] = RUST + (255,)
for y in range(20, S - 4):
    for x in range(4, S - 4):
        if px[x, y][:3] == SLOT and (x * 7 + y * 3) % 5 == 0: px[x, y] = MUD + (255,)
img.save(root / "art/basin_open.png")
print("ok")
