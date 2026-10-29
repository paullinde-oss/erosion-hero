#!/usr/bin/env python3
"""Draw the erosion control blanket texture (32x32, seamless): coir fibers under a square
twine net, following the close-up photo in art/photo/ref_493f6feb.png. Palette colors only."""
import pathlib, random
from PIL import Image
root = pathlib.Path(__file__).resolve().parent.parent
S = 32
LIGHT, MID, SHADE, DARK, TWINE, TWINE_HI = (242, 220, 155), (214, 178, 94), (169, 130, 59), (138, 82, 48), (242, 240, 230), (185, 181, 170)
rnd = random.Random(11)
img = Image.new("RGB", (S, S), SHADE); px = img.load()
def put(x, y, c): px[x % S, y % S] = c
# fibers: short curly strokes in random directions, wrapping at the edges so the tile is seamless
for _ in range(230):
    x, y = rnd.randrange(S), rnd.randrange(S)
    dx, dy = rnd.choice([(1, 0), (0, 1), (1, 1), (1, -1)])
    col = rnd.choices([LIGHT, MID, DARK, (94, 54, 34)], [3, 6, 5, 2])[0]
    for i in range(rnd.randint(2, 5)):
        put(x, y, col); x += dx; y += dy
        if rnd.random() < 0.3: dx, dy = rnd.choice([(1, 0), (0, 1), (1, 1), (1, -1)])
# twine net: thin light cords every 16 px, slightly wavy (sparser than the fibers, like the photo)
for k in range(0, S, 16):
    for t in range(S):
        wob = 1 if (t // 6 + k // 16) % 3 == 0 else 0
        put(k + 3 + wob, t, LIGHT if t % 3 else TWINE_HI)
        put(t, k + 5 + wob, LIGHT if t % 3 else TWINE_HI)
img.save(root / "art/blanket.png")
print("ok")
