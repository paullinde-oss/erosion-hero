#!/usr/bin/env python3
"""Draw one turbidity-curtain section (36x16, seen from above), following the BMP photos in
art/photo/curtain_ref*.png: a boxy yellow float section joined end to end with the next one,
a white tow line along the outside, and the skirt just under the water."""
import pathlib
from PIL import Image
root = pathlib.Path(__file__).resolve().parent.parent
W, H = 36, 16
Y_HI, Y, Y_SH, Y_DK = (255, 241, 168), (247, 201, 53), (217, 146, 28), (154, 90, 23)
OUT, LINE, LINE_SH, SKIRT = (59, 36, 22), (242, 240, 230), (185, 181, 170), (29, 79, 134)
img = Image.new("RGBA", (W, H)); px = img.load()
for x in range(W):
    # float body: flat top with a bevel, darker lower face
    px[x, 2] = OUT + (255,)
    px[x, 3] = Y_HI + (255,)
    for y in (4, 5, 6): px[x, y] = Y + (255,)
    for y in (7, 8): px[x, y] = Y_SH + (255,)
    px[x, 9] = Y_DK + (255,)
    px[x, 10] = OUT + (255,)
    # skirt showing under the water, then the white tow line running alongside
    px[x, 11] = SKIRT + (140,)
    sag = 1 if 9 <= x <= W - 10 else 0      # the line sags slightly between joints
    px[x, 12 + sag] = LINE + (255,)
    px[x, 13 + sag] = LINE_SH + (170,)
# seam where this section joins the next (the photos show a slight pinch at each joint)
for y in range(3, 10): px[0, y] = Y_DK + (255,); px[1, y] = Y_SH + (255,)
px[0, 3] = OUT + (255,); px[0, 9] = OUT + (255,)
# fabric fold / strap mark mid-section
for y in range(4, 9): px[W // 2, y] = Y_SH + (255,)
img.save(root / "art/boom.png")
print("ok")
