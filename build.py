#!/usr/bin/env python3
"""Inline the art, title background and pixel font into one self-contained HTML file.

Edit src/game.html (game code), then run:  python3 build.py
Output: Erosion_Hero.html (works offline; no network needed at the booth).
"""
import base64
import pathlib

root = pathlib.Path(__file__).resolve().parent
src = (root / "src" / "game.html").read_text()
assets = (root / "src" / "assets.js").read_text()
hero = (root / "src" / "hero_sprites.js").read_text()
tiles = (root / "src" / "tiles_v2.js").read_text()
sprites = (root / "src" / "sprites_v2.js").read_text()
title_bg = (root / "src" / "title_bg.txt").read_text().strip()
font = base64.b64encode((root / "src" / "pressstart2p-latin.woff2").read_bytes()).decode()

out = (src.replace("/*@@ASSETS@@*/", assets)
          .replace("/*@@HERO@@*/", hero)
          .replace("/*@@TILES@@*/", tiles)
          .replace("/*@@SPRITES@@*/", sprites)
          .replace("@@TITLE_BG@@", title_bg)
          .replace("@@FONT_WOFF2@@", font))
assert "@@" not in out, "unreplaced placeholder"
(root / "Erosion_Hero.html").write_text(out)
print(f"wrote Erosion_Hero.html ({len(out) / 1024:.0f} KB)")
