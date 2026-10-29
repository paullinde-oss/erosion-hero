#!/usr/bin/env python3
"""Pack the upgraded Canva sprites (cone, boat, Inspector walk cycles) into src/sprites_v2.js."""
import base64, io, json, pathlib
from PIL import Image, ImageOps
root = pathlib.Path(__file__).resolve().parent.parent
art = root / "art"
def uri(img):
    b = io.BytesIO(); img.save(b, "PNG"); return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()
def sized(img): return {"src": uri(img), "w": img.width / 2, "h": img.height / 2}
def full(img): return {"src": uri(img), "w": img.width, "h": img.height}
f = [Image.open(art / "inspector" / f"frame{i}.png") for i in range(1, 9)]
src = {
    "cone": uri(Image.open(art / "cone.png")),
    "boat": uri(Image.open(art / "boat.png")),
    # front: stand, step, stand, other step | back: stand, step, stand, mirrored step | side (faces right): stride, pass, stride, pass
    "inspDown": [uri(f[0]), uri(f[1]), uri(f[0]), uri(f[2])],
    "inspUp": [uri(f[3]), uri(f[4]), uri(f[3]), uri(ImageOps.mirror(f[4]))],
    "inspSide": [uri(f[6]), uri(f[5]), uri(f[7]), uri(f[5])],
    # Main Street: side-view vehicles, mirrored here to face left (the way traffic drives); w/h in world pixels
    "cars": [sized(ImageOps.mirror(Image.open(art / "vehicles" / f"{n}.png"))) for n in ("car_red", "car_blue", "pickup")],
    "bikeInspector": sized(ImageOps.mirror(Image.open(art / "vehicles" / "bike_inspector.png"))),
    "bmpTruck": sized(Image.open(art / "vehicles" / "semi_bmp.png")),
    "stores": [sized(Image.open(art / "stores" / f"frame{i}.png")) for i in (1, 2, 3)],
    "houses": [sized(Image.open(art / "houses" / f"frame{i}.png")) for i in (1, 2, 3)],
    # Main Street neighborhood (Canva art), one art pixel = one world pixel: houses with garages facing
    # the street on the top side, house backs behind privacy fences on the bottom side, yard props
    "nb": {
        "front": [full(Image.open(art / "neighborhood" / "front" / f"frame{i}.png")) for i in (1, 2, 3)],
        "back": [full(Image.open(art / "neighborhood" / "back" / f"frame{i}.png")) for i in (1, 2, 3)],
        **{n: full(Image.open(art / "neighborhood" / "props" / f"frame{i}.png"))
           for i, n in enumerate(("bush", "flowerBush", "tree", "picket", "privacy", "mailbox"), 1)},
    },
    # BMP inlet protection product: original art, only resampled to game size (colors untouched)
    "basinProtected": uri(Image.open(art / "basin_protected.png")),
    # open grate before protection: drawn by tools/draw_grate.py from the real grate photo
    "basinOpen": uri(Image.open(art / "basin_open.png")),
    # site 5 construction equipment on the shore (Canva art)
    "site5": {n: sized(Image.open(art / "site5" / f"{n}.png")) for n in ("crane", "excavator", "dumptruck", "stockpile")},
    # turbidity curtain float segment: drawn by tools/draw_boom.py
    "boom": uri(Image.open(art / "boom.png")),
}
(root / "src" / "sprites_v2.js").write_text("// Sprites generated in Canva, cut out by tools/sprite_cut.py\nconst SPRITE_SRC = " + json.dumps(src) + ";\n")
print("wrote src/sprites_v2.js")
