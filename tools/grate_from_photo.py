#!/usr/bin/env python3
"""Straighten the grate in art/photo/grate_photo.png into a top-down square and pixelate it."""
import pathlib, sys
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
root = pathlib.Path(__file__).resolve().parent.parent
src = Image.open(root / "art/photo/grate_photo.png").convert("RGB")
# grate corners in the photo: left, top, right, bottom -> square TL, TR, BR, BL
quad = [(338, 262), (585, 133), (795, 245), (548, 412)]
N = 256
dst = [(0, 0), (N, 0), (N, N), (0, N)]
A, B = [], []
for (x, y), (u, v) in zip(quad, dst):
    A.append([u, v, 1, 0, 0, 0, -x * u, -x * v]); B.append(x)
    A.append([0, 0, 0, u, v, 1, -y * u, -y * v]); B.append(y)
coef = np.linalg.solve(np.array(A, float), np.array(B, float))
flat = src.transform((N, N), Image.PERSPECTIVE, tuple(coef), Image.BICUBIC)
flat.save(root / "art/photo/grate_flat.png")
size = int(sys.argv[1]) if len(sys.argv) > 1 else 32
small = flat.filter(ImageFilter.GaussianBlur(1.2)).resize((size, size), Image.BOX)
small = ImageEnhance.Contrast(small).enhance(1.5)
small = ImageEnhance.Color(small).enhance(1.6)
import importlib.util
spec = importlib.util.spec_from_file_location("sc", pathlib.Path(__file__).resolve().parent / "sprite_cut.py")
# palette: grays, dirt and outline browns only
import re
pal = []
for line in (root / "art-kit/erosion-hero.gpl").read_text().splitlines()[5:]:
    m = re.match(r"\s*(\d+)\s+(\d+)\s+(\d+)\s+(.*)", line)
    if m and m.group(4).rsplit(" ", 1)[0] in ("Grays", "Dirt", "Outline"):
        pal.append(tuple(int(m.group(i)) for i in (1, 2, 3)))
px = small.load()
for y in range(size):
    for x in range(size):
        c = px[x, y]
        px[x, y] = min(pal, key=lambda p: (p[0]-c[0])**2*0.3 + (p[1]-c[1])**2*0.59 + (p[2]-c[2])**2*0.11)
small.save(root / "art/basin_open_photo.png")
print("ok", size)
