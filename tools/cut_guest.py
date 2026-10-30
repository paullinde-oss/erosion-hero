#!/usr/bin/env python3
"""Cut a guest hero's Canva sheet (walk: 8 frames, lay: 4 poses) in true-color mode and clean the
magenta/purple tint the cutter can leave between legs and along edges. Usage: cut_guest.py <id> walk|lay <raw.png>"""
import subprocess, sys, pathlib, shutil
from PIL import Image
root = pathlib.Path(__file__).resolve().parent.parent
cid, kind, raw = sys.argv[1], sys.argv[2], sys.argv[3]
TOL = sys.argv[4] if len(sys.argv) > 4 else "120"   # lower for pale pink/purple outfits
out = root / "art" / "crew" / cid / kind
shutil.rmtree(out, ignore_errors=True)
args = ["--frames", "8", "--height", "48", "--cell", "28x48"] if kind == "walk" else ["--frames", "4", "--height", "38"]
subprocess.run([sys.executable, str(root / "tools" / "sprite_cut.py"), raw, str(out), *args, "--pink", "--tol", TOL], check=True)
for f in out.glob("frame*.png"):
    im = Image.open(f).convert("RGBA"); px = im.load(); W, H = im.size
    for y in range(H):
        for x in range(W):
            r, g, b, a = px[x, y]
            if not a: continue
            if r > 170 and b > 150 and g < 90:                 # leftover background magenta
                px[x, y] = (0, 0, 0, 0)
            elif b > g + 30 and r > g + 25 and b > 70 and abs(r - b) < 70 and y > H * 0.55:
                px[x, y] = (34, 30, 34, a)                     # purple shading between the legs -> dark
    im.save(f)
