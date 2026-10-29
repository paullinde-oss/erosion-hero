#!/usr/bin/env python3
"""Build the Aseprite starter kit described in the Erosion Hero Art Spec.

Outputs art-kit/: erosion-hero.gpl palette, palette swatch, tile sheet templates
(1x, to draw on) with 4x labeled slot maps, and character frame templates.
"""
import pathlib, shutil
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "art-kit"
T = 16

PALETTE = [  # (ramp, [hex light -> dark])
    ("Outline", ["3b2416", "1f1410"]),
    ("Skin", ["f6c99a", "e09a6c", "a8603f"]),
    ("Hard-hat yellow", ["fff1a8", "f7c935", "d9921c", "9a5a17"]),
    ("Safety orange", ["ff9d4a", "ef6420", "b23a1a"]),
    ("Denim blue", ["6fa8dc", "3d6fb0", "2a4680", "1e2a52"]),
    ("Grass", ["b8d65a", "79b043", "4b8a3b", "2e5e33", "1d3b2a"]),
    ("Dirt", ["d9a066", "b0743f", "8a5230", "5e3622"]),
    ("Straw", ["f2dc9b", "d6b25e", "a9823b"]),
    ("Clear water", ["9fe2f0", "4fb3d9", "2c7fb8", "1d4f86"]),
    ("Muddy water", ["a68a5b", "7d6342"]),
    ("Grays", ["f2f0e6", "b9b5aa", "8a867c", "5c5a55", "3a3a40"]),
    ("Red", ["e8473a", "9e2a2b"]),
]

# Tile sheet layouts: (label, col, row, w_tiles, h_tiles). 12 columns wide.
def nine(prefix, c0, r0):
    names = ["TL", "T", "TR", "L", "C", "R", "BL", "B", "BR"]
    return [(f"{prefix} {n}", c0 + i % 3, r0 + i // 3, 1, 1) for i, n in enumerate(names)]

SHEETS = {
    "tiles_yard": (12, 8, [
        *[(f"grass {i+1}", i, 0, 1, 1) for i in range(4)],
        ("tuft", 4, 0, 1, 1), ("flowers 1", 5, 0, 1, 1), ("flowers 2", 6, 0, 1, 1), ("pebbles", 7, 0, 1, 1),
        *nine("soil", 0, 1), ("soil C2", 3, 1, 1, 1), ("soil C3", 3, 2, 1, 1),
        *nine("slope", 4, 1), ("slope C2", 7, 1, 1, 1), ("slope C3", 7, 2, 1, 1),
        *nine("pond", 8, 1), ("pond C2", 11, 1, 1, 1), ("pond C3", 11, 2, 1, 1),
        *[(f"erode f{i+1}", i, 4, 1, 1) for i in range(4)],
        *[(f"washout f{i+1}", 4 + i, 4, 1, 1) for i in range(6)],
        ("blanket 1", 10, 4, 1, 1), ("blanket 2", 11, 4, 1, 1),
        ("fence H1", 0, 5, 1, 1), ("fence H2", 1, 5, 1, 1), ("fence V1", 2, 5, 1, 1), ("fence V2", 3, 5, 1, 1),
        ("fence TL", 4, 5, 1, 1), ("fence TR", 5, 5, 1, 1), ("fence BL", 6, 5, 1, 1), ("fence BR", 7, 5, 1, 1),
        ("wattle", 0, 6, 2, 2), ("silt fence", 2, 6, 2, 2), ("hay bale", 4, 6, 2, 2),
        ("wheelbarrow", 6, 6, 2, 2), ("toilet", 8, 6, 2, 2), ("BMP sign", 10, 6, 2, 2),
    ]),
    "tiles_road": (12, 7, [
        ("asphalt 1", 0, 0, 1, 1), ("asphalt 2", 1, 0, 1, 1), ("asphalt 3", 2, 0, 1, 1),
        ("center dash", 3, 0, 1, 1), ("edge top", 4, 0, 1, 1), ("edge bottom", 5, 0, 1, 1),
        ("curb top", 6, 0, 1, 1), ("curb bottom", 7, 0, 1, 1), ("sidewalk 1", 8, 0, 1, 1), ("sidewalk 2", 9, 0, 1, 1),
        ("basin open", 10, 0, 1, 1), ("basin protected", 11, 0, 1, 1),
        ("cone", 0, 1, 1, 1), ("barricade", 1, 1, 1, 1),
        ("store 1", 0, 2, 2, 3), ("store 2", 2, 2, 2, 3), ("store 3", 4, 2, 2, 3),
        ("house 1", 6, 2, 2, 3), ("house 2", 8, 2, 2, 3),
        ("skyline (tiles L-R)", 0, 5, 8, 2),
    ]),
    "tiles_lake": (12, 2, [
        *[(f"water f{i+1}", i, 0, 1, 1) for i in range(4)],
        *[(f"muddy f{i+1}", 4 + i, 0, 1, 1) for i in range(4)],
        ("shore 1", 8, 0, 1, 1), ("shore 2", 9, 0, 1, 1), ("anchor start", 10, 0, 1, 1), ("anchor end", 11, 0, 1, 1),
        *[(f"foam f{i+1}", i, 1, 1, 1) for i in range(4)],
        ("reeds 1", 4, 1, 1, 1), ("reeds 2", 5, 1, 1, 1), ("shrub", 6, 1, 1, 1),
        ("buoy orange 8x8", 7, 1, 1, 1), ("buoy white 8x8", 8, 1, 1, 1), ("boom 16x8", 9, 1, 1, 1),
    ]),
}

CHARACTERS = {  # file: (frame w, h, [(tag, frames)])
    "hero": (16, 32, [("idle_down", 2), ("idle_up", 2), ("idle_side", 2), ("walk_down", 4), ("walk_up", 4),
                      ("walk_side", 4), ("hurt", 2), ("cheer", 3)]),
    "hero_lay": (32, 32, [("lay_down", 4), ("lay_up", 4), ("lay_right", 4), ("lay_left", 4)]),
    "inspector": (16, 32, [("walk_down", 4), ("walk_up", 4), ("walk_side", 4), ("alert", 2), ("write_up", 4)]),
    "boat": (32, 16, [("idle", 2), ("move", 2)]),
    "vehicles": (32, 16, [("car_a", 2), ("car_b", 2), ("truck", 2), ("scooter", 2)]),
}

def font(size):
    for f in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
        if pathlib.Path(f).exists():
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()

def hexrgb(h):
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def write_palette():
    lines = ["GIMP Palette", "Name: Erosion Hero", "Columns: 8", "#"]
    lines.append("255   0 255\tTransparent (slot 0, do not paint with it)")
    for ramp, cols in PALETTE:
        for i, h in enumerate(cols):
            r, g, b = hexrgb(h)
            lines.append(f"{r:3d} {g:3d} {b:3d}\t{ramp} {i+1}")
    (OUT / "erosion-hero.gpl").write_text("\n".join(lines) + "\n")
    # swatch
    sw, rh, lw = 76, 44, 190
    img = Image.new("RGB", (lw + 5 * sw + 20, len(PALETTE) * rh + 20), "#1c1712")
    d = ImageDraw.Draw(img); f = font(15); fs = font(10)
    for y, (ramp, cols) in enumerate(PALETTE):
        d.text((10, 10 + y * rh + 13), ramp, fill="#eee3c8", font=f)
        for x, h in enumerate(cols):
            x0, y0 = lw + x * sw, 10 + y * rh
            d.rectangle([x0, y0, x0 + sw - 4, y0 + rh - 4], fill="#" + h)
            r, g, b = hexrgb(h)
            d.text((x0 + 2, y0 + rh - 16), "#" + h, fill="#000" if r + g + b > 380 else "#fff", font=fs)
    img.save(OUT / "palette-swatch.png")

def write_sheet(name, cols, rows, slots):
    w, h = cols * T, rows * T
    # 1x drawing template: faint alternating slot fills on a guide you hide before export
    tpl = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(tpl)
    for i, (label, c, r, sw, sh) in enumerate(slots):
        col = (255, 0, 255, 40) if i % 2 else (0, 200, 255, 40)
        d.rectangle([c * T, r * T, (c + sw) * T - 1, (r + sh) * T - 1], fill=col)
    tpl.save(OUT / "tiles" / f"{name}_template.png")
    # 4x labeled map
    S = 6
    mp = Image.new("RGB", (w * S + 2, h * S + 2), "#f2f0e6"); d = ImageDraw.Draw(mp); f = font(11)
    for i, (label, c, r, sw, sh) in enumerate(slots):
        box = [c * T * S + 1, r * T * S + 1, (c + sw) * T * S, (r + sh) * T * S]
        d.rectangle(box, fill="#d6ecf5" if i % 2 == 0 else "#f6dcef", outline="#3a3a40")
        words, lines, cur = label.split(), [], ""
        for wd in words:
            if len(cur + " " + wd) > 11 and cur: lines.append(cur); cur = wd
            else: cur = (cur + " " + wd).strip()
        lines.append(cur)
        for j, ln in enumerate(lines):
            d.text((box[0] + 4, box[1] + 4 + j * 13), ln, fill="#1f1410", font=f)
    mp.save(OUT / "tiles" / f"{name}_slot-map.png")

def write_character(name, fw, fh, tags):
    n = sum(k for _, k in tags)
    # 1x guide: frame tint, center column, feet row
    g = Image.new("RGBA", (fw * n, fh), (0, 0, 0, 0)); d = ImageDraw.Draw(g)
    i = 0
    for t, (tag, k) in enumerate(tags):
        for _ in range(k):
            x = i * fw
            d.rectangle([x, 0, x + fw - 1, fh - 1], fill=(0, 200, 255, 30) if t % 2 == 0 else (255, 0, 255, 30))
            d.line([x + fw // 2 - 1, 0, x + fw // 2 - 1, fh - 1], fill=(255, 0, 0, 70))
            d.line([x, fh - 1, x + fw - 1, fh - 1], fill=(255, 0, 0, 140))
            i += 1
    g.save(OUT / "characters" / f"{name}_guide.png")
    # labeled map
    S = 6
    mp = Image.new("RGB", (fw * n * S + 2, fh * S + 40), "#f2f0e6"); d = ImageDraw.Draw(mp); f = font(11)
    i = 0
    for t, (tag, k) in enumerate(tags):
        x0 = i * fw * S + 1
        d.rectangle([x0, 0, (i + k) * fw * S, 30], fill="#e8b923" if t % 2 == 0 else "#ef6420", outline="#3a3a40")
        d.text((x0 + 4, 8), tag, fill="#1f1410", font=f)
        for j in range(k):
            x = (i + j) * fw * S + 1
            d.rectangle([x, 32, x + fw * S - 1, 32 + fh * S - 1], fill="#d6ecf5", outline="#3a3a40")
            d.line([x + (fw // 2) * S, 32, x + (fw // 2) * S, 32 + fh * S], fill="#e8473a")
            d.rectangle([x, 32 + (fh - 1) * S, x + fw * S - 1, 32 + fh * S - 1], fill="#e8473a")
            d.text((x + 3, 36), str(j + 1), fill="#3a3a40", font=f)
        i += k
    mp.save(OUT / "characters" / f"{name}_frame-map.png")

def main():
    if OUT.exists(): shutil.rmtree(OUT)
    for sub in ["tiles", "characters"]: (OUT / sub).mkdir(parents=True)
    write_palette()
    for name, (c, r, slots) in SHEETS.items(): write_sheet(name, c, r, slots)
    for name, (fw, fh, tags) in CHARACTERS.items(): write_character(name, fw, fh, tags)
    (OUT / "README.txt").write_text(
        "Erosion Hero - Aseprite starter kit (see the Erosion Hero Art Spec doc)\n\n"
        "erosion-hero.gpl      Palette. Aseprite: Palette panel options menu > Load Palette.\n"
        "                      Slot 0 (magenta) is the transparent color - never paint with it.\n"
        "palette-swatch.png    The same palette as a labeled picture.\n\n"
        "tiles/*_template.png  Open in Aseprite (File > Open), set Color Mode to Indexed with the\n"
        "                      palette, and keep it as a hidden 'guide' layer. Draw each tile in its\n"
        "                      tinted slot. Hide the guide layer before exporting.\n"
        "tiles/*_slot-map.png  Zoomed map naming every slot.\n\n"
        "characters/*_guide.png      One tinted cell per frame, in tag order. The red bottom row is\n"
        "                            where the feet go; the red vertical line is the center.\n"
        "characters/*_frame-map.png  Zoomed map showing which frames belong to which tag.\n"
        "                            In Aseprite, start a new file at the frame size and import the\n"
        "                            guide with File > Import Sprite Sheet (Type: By Rows, size = frame size).\n")
    print("ok")

main()
