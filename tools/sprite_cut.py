#!/usr/bin/env python3
"""Cut AI-generated sprites off a flat background and make them game-ready.

The background color is read from the image corners; everything close to it becomes
transparent. Each sprite is cropped, scaled to a target height (pixel grid), snapped to
the Erosion Hero palette and saved with hard (0/255) alpha.

usage:
  sprite_cut.py IN OUT --height 26                      # one sprite
  sprite_cut.py IN OUTDIR --frames 8 --height 48 --cell 28x48   # a row of frames
  add --pink for sprites with pink/purple in them (e.g. sequins): only near-pure magenta is
  treated as background, and colors are kept instead of snapped to the palette (which has no pinks).
"""
import argparse, pathlib, sys
from PIL import Image, ImageFilter
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import importlib.util
spec = importlib.util.spec_from_file_location("pz", pathlib.Path(__file__).resolve().parent / "pixelize.py")

def load_palette():
    import re
    gpl = pathlib.Path(__file__).resolve().parent.parent / "art-kit" / "erosion-hero.gpl"
    out = []
    for line in gpl.read_text().splitlines()[5:]:
        m = re.match(r"\s*(\d+)\s+(\d+)\s+(\d+)", line)
        if m: out.append(tuple(int(m.group(i)) for i in (1, 2, 3)))
    return out

PAL = [c for c in load_palette() if c not in [(255, 0, 255), (232, 71, 58), (158, 42, 43)]]

def bg_color(img):
    w, h = img.size; px = img.load()
    cs = [px[2, 2], px[w - 3, 2], px[2, h - 3], px[w - 3, h - 3]]
    return tuple(sorted(c[i] for c in cs)[1] for i in range(3))

PINK = False   # set by --pink

def key_out(img, tol):
    img = img.convert("RGBA"); px = img.load(); bg = bg_color(img)
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            d = abs(r - bg[0]) + abs(g - bg[1]) + abs(b - bg[2])
            # magenta fringe: strongly red+blue with little green also counts as background
            fringe = bg[0] > 200 and bg[2] > 200 and bg[1] < 80 and r - g > 55 and b - g > 55
            if PINK: fringe = fringe and r > 200 and b > 170 and g < 70
            if d < tol or fringe: px[x, y] = (0, 0, 0, 0)
    return img

def snap(img):
    px = img.load()
    if PINK:   # keep the real colors, just harden the alpha
        for y in range(img.height):
            for x in range(img.width):
                if px[x, y][3] < 128: px[x, y] = (0, 0, 0, 0)
                else: px[x, y] = px[x, y][:3] + (255,)
        # edge pixels still tinted by the magenta background become a dark outline
        W, H = img.size
        for depth in range(3):   # peel inward: pass 1 outlines the edge, later passes clear what's behind it
            src = img.copy(); sp = src.load()
            for y in range(H):
                for x in range(W):
                    r, g, b, al = sp[x, y]
                    if not al or not (r - g > 45 and b - g > 30): continue
                    if any(not (0 <= x+dx < W and 0 <= y+dy < H) or not sp[x+dx, y+dy][3] or sp[x+dx, y+dy][:3] == (34, 26, 22)
                           for dx, dy in ((1,0),(-1,0),(0,1),(0,-1))):
                        px[x, y] = (34, 26, 22, 255) if depth == 0 else (0, 0, 0, 0)
        return img
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            if a < 128: px[x, y] = (0, 0, 0, 0); continue
            c = min(PAL, key=lambda p: (p[0]-r)**2*0.3 + (p[1]-g)**2*0.59 + (p[2]-b)**2*0.11)
            px[x, y] = c + (255,)
    return img

def defringe(img):
    px = img.load(); w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a and r - g > 40 and b - g > 40 and (not PINK or (r > 190 and b > 160 and g < 80)): px[x, y] = (0, 0, 0, 0)
    return img

def shrink(img, height):
    bb = img.getbbox(); img = img.crop(bb)
    w = max(1, round(img.width * height / img.height))
    # premultiplied-alpha friendly downscale, then hard alpha
    return defringe(img.resize((w, height), Image.LANCZOS))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inp"); ap.add_argument("out")
    ap.add_argument("--height", type=int, required=True)
    ap.add_argument("--frames", type=int, default=1)
    ap.add_argument("--cell", default="")
    ap.add_argument("--tol", type=int, default=120)
    ap.add_argument("--pink", action="store_true")
    a = ap.parse_args()
    global PINK; PINK = a.pink
    img = key_out(Image.open(a.inp).convert("RGB"), a.tol)
    if a.frames == 1:
        snap(shrink(img, a.height)).save(a.out); return
    # split the row into frames by empty columns
    alpha = img.split()[3]; w = img.width
    cols = [any(alpha.getpixel((x, y)) for y in range(img.height)) for x in range(w)]
    runs, start = [], None
    for x, c in enumerate(cols + [False]):
        if c and start is None: start = x
        if not c and start is not None:
            if x - start > 3: runs.append((start, x))
            start = None
    if a.frames > 1 and len(runs) < a.frames:
        # some frames touch: cut at the emptiest column near each evenly spaced frame boundary
        x0, x1 = runs[0][0], runs[-1][1]; step = (x1 - x0) / a.frames
        fg = [sum(1 for y in range(img.height) if alpha.getpixel((x, y))) for x in range(w)]
        cuts = [x0] + [min(range(int(x0 + k*step - step*0.2), int(x0 + k*step + step*0.2)), key=lambda x: fg[x])
                       for k in range(1, a.frames)] + [x1]
        runs = [(cuts[k], cuts[k+1]) for k in range(a.frames)]
        runs = [(s0 + next((i for i in range(e0 - s0) if fg[s0+i]), 0), e0) for s0, e0 in runs]
    print("found", len(runs), "frames:", runs)
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    frames = [img.crop((s, 0, e, img.height)) for s, e in runs]
    # one shared scale: tallest frame -> target height, so sizes stay consistent between frames
    tall = max(f.getbbox()[3] - f.getbbox()[1] for f in frames)
    cw, ch = (int(v) for v in a.cell.split("x")) if a.cell else (None, a.height)
    for i, f in enumerate(frames):
        bb = f.getbbox(); f = f.crop(bb)
        nh = max(1, round(f.height * a.height / tall)); nw = max(1, round(f.width * a.height / tall))
        f = snap(defringe(f.resize((nw, nh), Image.LANCZOS)))
        if cw:
            cell = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
            cell.alpha_composite(f, ((cw - nw) // 2, ch - nh))  # feet on the bottom row, centered
            f = cell
        f.save(out / f"frame{i+1}.png")

main()
