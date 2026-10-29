#!/usr/bin/env python3
"""Pack the upgraded ground tiles in art/ into src/tiles_v2.js for the build.
usage: build_tiles.py SOIL.png SLOPE.png ERODING.png BLANKET.png"""
import base64, json, pathlib, sys
root = pathlib.Path(__file__).resolve().parent.parent
keys = ["soil", "slope", "eroding", "blanket"]
src = {k: "data:image/png;base64," + base64.b64encode((root / p).read_bytes()).decode() for k, p in zip(keys, sys.argv[1:5])}
(root / "src" / "tiles_v2.js").write_text("// Ground tiles generated in Canva, cleaned up by tools/pixelize.py\nconst TILE_SRC = " + json.dumps(src) + ";\n")
print("wrote src/tiles_v2.js")
