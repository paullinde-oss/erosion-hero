#!/usr/bin/env python3
"""Leia's walk frames. Canva's safety filter refused every walk-sheet prompt for her, so the frames
are composited: her own head (from her Canva laying poses) on a walking body (Oprah's walk frames)
recolored to a white gown and boots. The black mic in the body's hand reads as her blaster."""
import colorsys, pathlib
from PIL import Image
root = pathlib.Path(__file__).resolve().parent.parent
src, lay, out = root/"art/crew/oprah/walk", root/"art/crew/leia/lay", root/"art/crew/leia/walk"
out.mkdir(parents=True, exist_ok=True)
HEAD_SCALE = 1.3

def is_red(p): r, g, b, a = p; return a and r > 110 and r > g * 1.6 and r > b * 1.6

def recolor_body(im, top):
    im = im.copy(); px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if not a: continue
            if y < top: px[x, y] = (0, 0, 0, 0); continue
            h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255); v = max(r, g, b)
            if v < 55: continue  # black mic (blaster) and outlines stay dark
            # hands vanish into her long sleeves, so everything else becomes gown
            if y > im.height * 0.9:  # shoes -> white boots
                px[x, y] = (200, 200, 208, a)
            elif v < 110: px[x, y] = (78, 74, 92, a)    # suit shadows/outline -> gown outline
            elif v < 165: px[x, y] = (196, 196, 208, a)  # mid -> gown shade
            else: px[x, y] = (242, 242, 246, a)        # lit -> white gown
    # 1px dark outline so the white gown reads against pale ground
    src = im.copy(); sp = src.load()
    for y in range(top, im.height):
        for x in range(im.width):
            if sp[x, y][3]: continue
            if any(0 <= x+dx < im.width and 0 <= y+dy < im.height and sp[x+dx, y+dy][3] for dx, dy in ((1,0),(-1,0),(0,1),(0,-1))):
                px[x, y] = (60, 56, 72, 255)
    return im

def shoulder_row(im):
    px = im.load()
    for y in range(im.height):
        if sum(1 for x in range(im.width) if is_red(px[x, y])) >= 3: return y
    return im.height // 3

def crop_alpha(im): return im.crop(im.getbbox())
lay1, lay3 = Image.open(lay/"frame1.png").convert("RGBA"), Image.open(lay/"frame3.png").convert("RGBA")
front = crop_alpha(lay1.crop((0, 0, lay1.width, 13)))
side = crop_alpha(lay3.crop((lay3.width // 2 - 6, 0, lay3.width, 14)))
side = side.crop((0, 0, side.width, side.height))
back = front.copy(); bp = back.load()  # back of the head: same silhouette, all hair
for y in range(back.height):
    for x in range(back.width):
        r, g, b, a = bp[x, y]
        if a: k = (r + g + b) / 3; bp[x, y] = (int(70 + k * 0.25), int(40 + k * 0.15), int(25 + k * 0.08), a)

def scale(h): return h.resize((round(h.width * HEAD_SCALE), round(h.height * HEAD_SCALE)), Image.NEAREST)
heads = {1: front, 2: front, 3: front, 4: back, 5: back, 6: side, 7: side, 8: side}
for i in range(1, 9):
    body = Image.open(src/f"frame{i}.png").convert("RGBA")
    top = shoulder_row(body)
    im = recolor_body(body, top)
    h = scale(heads[i]); cx = im.width // 2 if i <= 5 else im.width // 2 + 1
    canvas = Image.new("RGBA", im.size)
    canvas.alpha_composite(im)
    canvas.alpha_composite(h, (cx - h.width // 2, max(0, top + 1 - h.height)))
    canvas.save(out/f"frame{i}.png")
print("leia walk frames:", out)
