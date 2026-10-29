#!/usr/bin/env python3
"""Turn an AI-generated image into game-ready pixel art.

Shrinks to the target pixel size, snaps every pixel to the Erosion Hero palette
(optionally only some ramps), and can blend the edges so a texture tiles seamlessly.
usage: pixelize.py IN OUT --size 32 --ramps Dirt,Outline [--seamless]
"""
import argparse, pathlib, re
from PIL import Image, ImageFilter, ImageOps, ImageEnhance

GPL = pathlib.Path(__file__).resolve().parent.parent / "art-kit" / "erosion-hero.gpl"

def palette(ramps=None):
    out = []
    for line in GPL.read_text().splitlines()[5:]:
        m = re.match(r"\s*(\d+)\s+(\d+)\s+(\d+)\s+(.*)", line)
        if not m: continue
        name = m.group(4).rsplit(" ", 1)[0]
        if ramps and name not in ramps: continue
        out.append(tuple(int(m.group(i)) for i in (1, 2, 3)))
    return out

def snap(img, pal, contrast=1.0):
    img = img.convert("RGB"); px = img.load()
    # match the image's brightness range to the palette's so the full ramp gets used
    lum = lambda c: 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]
    ls = sorted(lum(px[x, y]) for x in range(img.width) for y in range(img.height))
    lo, hi = ls[len(ls) // 50], ls[-len(ls) // 50]
    pl = sorted(lum(c) for c in pal); plo, phi = pl[0], pl[-1]
    for y in range(img.height):
        for x in range(img.width):
            c = px[x, y]; l = lum(c)
            t = (l - lo) / max(1, hi - lo); t = 0.5 + (t - 0.5) * contrast
            target = plo + max(0, min(1, t)) * (phi - plo)
            # choose by brightness mostly, hue as a tiebreak
            best = min(pal, key=lambda p: abs(lum(p) - target) * 3 + sum(abs(a - b) for a, b in zip(p, c)) * 0.15)
            px[x, y] = best
    return img

def mix_snap(img, pal, shares):
    """Rank pixels by brightness and hand out palette colors (light to dark) in the given proportions."""
    img = img.convert("RGB"); px = img.load()
    lum = lambda c: 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]
    cols = sorted(pal, key=lum, reverse=True)[:len(shares)]
    coords = sorted(((x, y) for x in range(img.width) for y in range(img.height)), key=lambda p: -lum(px[p]))
    n = len(coords); i = 0
    for k, share in enumerate(shares):
        cnt = round(share / sum(shares) * n) if k < len(shares) - 1 else n - i
        for p in coords[i:i + cnt]: px[p] = cols[k]
        i += cnt
    return img

def nearest(img, pal):
    img = img.convert("RGB"); px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            c = px[x, y]
            px[x, y] = min(pal, key=lambda p: (p[0]-c[0])**2*0.3 + (p[1]-c[1])**2*0.59 + (p[2]-c[2])**2*0.11)
    return img

def seamless(img):
    """Blend opposite edges by mixing the image with its half-offset copy near the borders."""
    w, h = img.size
    off = Image.new(img.mode, img.size)
    off.paste(img.crop((w // 2, 0, w, h)), (0, 0)); off.paste(img.crop((0, 0, w // 2, h)), (w - w // 2, 0))
    off2 = Image.new(img.mode, img.size)
    off2.paste(off.crop((0, h // 2, w, h)), (0, 0)); off2.paste(off.crop((0, 0, w, h // 2)), (0, h - h // 2))
    mask = Image.new("L", img.size)
    mp = mask.load()
    for y in range(h):
        for x in range(w):
            dx = min(x, w - 1 - x) / (w * 0.25); dy = min(y, h - 1 - y) / (h * 0.25)
            mp[x, y] = int(255 * max(0, 1 - min(1, dx, dy)))
    return Image.composite(off2, img, mask)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inp"); ap.add_argument("out")
    ap.add_argument("--size", type=int, default=32)
    ap.add_argument("--ramps", default="")
    ap.add_argument("--seamless", action="store_true")
    ap.add_argument("--contrast", type=float, default=1.0)
    ap.add_argument("--mix", default="", help="share of each ramp color, light to dark, e.g. 0.15,0.5,0.28,0.07 (ramp order from the palette)")
    ap.add_argument("--blur", type=float, default=0)
    ap.add_argument("--punch", type=float, default=0, help="stretch contrast and boost color before matching (e.g. 1.5)")
    ap.add_argument("--nearest", action="store_true", help="plain nearest palette color (keeps hues such as water in mud)")
    ap.add_argument("--clean", type=int, default=0, help="passes that merge lone pixels into their neighbors")
    a = ap.parse_args()
    img = Image.open(a.inp).convert("RGB")
    s = min(img.size); img = img.crop(((img.width - s) // 2, (img.height - s) // 2, (img.width + s) // 2, (img.height + s) // 2))
    if a.seamless: img = seamless(img)
    if a.blur: img = img.filter(ImageFilter.GaussianBlur(a.blur))
    img = img.resize((a.size, a.size), Image.BOX)
    if a.punch:
        img = ImageOps.autocontrast(img, cutoff=1)
        img = ImageEnhance.Color(img).enhance(a.punch)
        img = ImageEnhance.Contrast(img).enhance(a.punch * 0.8)
    pal = palette(set(r.strip() for r in a.ramps.split(",") if r.strip()) or None)
    if a.nearest: out = nearest(img, pal)
    elif a.mix: out = mix_snap(img, pal, [float(v) for v in a.mix.split(",")])
    else: out = snap(img, pal, a.contrast)
    for _ in range(a.clean): out = out.filter(ImageFilter.ModeFilter(3))
    out.save(a.out)

main()
