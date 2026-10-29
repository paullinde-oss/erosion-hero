#!/usr/bin/env python3
"""Pack the playable crew into src/hero_sprites.js.

Per character: walk frames (art/crew/<id>/walk/frame1-8.png), laying poses (art/crew/<id>/lay/frame1-4.png,
order: down, up, right, left) and a character-select portrait cut from art/canva/portrait_<id>_raw.png.
All art generated in Canva; frames cut out by tools/sprite_cut.py."""
import base64, io, json, pathlib, sys
from PIL import Image, ImageOps
root = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root / "tools"))
CREW = [  # id, name, line shown on the select screen
    ("daryl", "DARYL", "Never met a slope he couldn't blanket."),
    ("sheryl", "SHERYL", "Reads a site plan faster than you read this."),
    ("marcus", "MARCUS", "Crew lead. Keeps everyone laughing and dry."),
    ("tanya", "TANYA", "Superintendent. Storms don't rattle her."),
    ("rosa", "ROSA", "Fastest blanket roller in three counties."),
    ("kenji", "KENJI", "Thirty storms in. Still hasn't lost a slope."),
    ("mike", "MIKE", "Six rings. Zero washouts. Flies over silt fence."),
    ("leia", "LEIA", "Rebel leader. Somebody has to save this slope."),
    ("oprah", "OPRAH", "And YOU get a blanket! And YOU get a blanket!"),
    ("ralph", "RALPH", "Hates erosion more than he hates the Foot Clan."),
    ("wayne", "WAYNE", "The Great One. Never misses an open slope."),
    ("chief", "CHIEF", "Wake me when there's a slope to save."),
    ("taylor", "TAYLOR", "Shakes off the silt. Never ever getting washed out again."),
    ("donald", "DONALD", "Lays the best blankets. Tremendous blankets."),
]
# select-grid face crop (fractions of the portrait); default is the top of the portrait
FACE_BOX = {"oprah": (0.22, 0.29, 0.78, 0.85)}  # her portrait has a speech bubble up top
def uri(img):
    b = io.BytesIO(); img.save(b, "PNG"); return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()
PINK_OUTFITS = {"taylor"}   # pink costumes: key out only near-pure magenta so the sequins survive
def key_out(img, strict=False):
    img = img.convert("RGBA"); px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            if (r > 200 and b > 200 and g < 90) or (not strict and r - g > 70 and b - g > 70): px[x, y] = (0, 0, 0, 0)
    return img
out = []
for cid, name, line in CREW:
    d = root / "art" / "crew" / cid
    w = [Image.open(d / "walk" / f"frame{i}.png") for i in range(1, 9)]
    lay = [Image.open(d / "lay" / f"frame{i}.png") for i in range(1, 5)]
    por = key_out(Image.open(root / "art" / "canva" / f"portrait_{cid}_raw.png"), cid in PINK_OUTFITS)
    por = por.crop(por.getbbox())
    side = max(por.size); sq = Image.new("RGBA", (side, side)); sq.alpha_composite(por, ((side - por.width) // 2, side - por.height))
    portrait = sq.resize((128, 128), Image.LANCZOS)
    fb = FACE_BOX.get(cid, (0.12, 0, 0.88, 0.76))
    face = sq.crop(tuple(side * f for f in fb)).resize((48, 48), Image.LANCZOS)
    out.append({
        "id": cid, "name": name, "line": line,
        "portrait": uri(portrait), "face": uri(face),
        "down": {"idle": uri(w[0]), "walk": [uri(w[0]), uri(w[1]), uri(w[0]), uri(w[2])]},
        "up": {"idle": uri(w[3]), "walk": [uri(w[3]), uri(w[4]), uri(w[3]), uri(ImageOps.mirror(w[4]))]},
        "side": {"idle": uri(w[5]), "walk": [uri(w[6]), uri(w[5]), uri(w[7]), uri(w[5])]},
        "lay": {k: {"src": uri(im), "w": im.width / 2, "h": im.height / 2} for k, im in zip(["down", "up", "right", "left"], lay)},
    })
(root / "src" / "hero_sprites.js").write_text("// Playable crew (Canva art), packed by tools/build_crew.py\nconst CREW_SRC = " + json.dumps(out) + ";\nconst HERO_SRC = CREW_SRC[0];\n")
print("crew:", ", ".join(c[1] for c in CREW))
