# Erosion Hero: booth build

`Erosion_Hero.html` is the game. It's one self-contained file (art, font, music and SFX are all embedded) and runs offline in any modern browser.

## Editing
- Game code lives in `src/game.html`. The playable crew members (sprites + select-screen portraits) are Canva art packed by `python3 tools/build_crew.py`. Art is in `src/assets.js`, the title image in `src/title_bg.txt`, and the font in `src/pressstart2p-latin.woff2`.
- After editing, run `python3 build.py` to regenerate `Erosion_Hero.html`.

## Controls
| | Keyboard | Arcade encoder / gamepad | Touch |
|---|---|---|---|
| Move | Arrows / WASD | Stick or D-pad | On-screen D-pad |
| Action (lay blanket, confirm) | Space, Z, X, Left Ctrl/Alt/Shift | A (any face button until set up) | LAY |
| Back (delete letter, leave character select) | Backspace | B (also lays blankets during play) | — |
| Start | Enter, 1 | Start | Tap |
| Pause | Esc, P | Select (Start also pauses mid-game) | II |

Name entry also accepts typing letters directly on a keyboard.

## Operator shortcuts
- **Operator menu:** the backtick key `` ` ``, or the faint TEST button on the title screen. It lets you jump to a site, toggle music, SFX, CRT scanlines and idle reset, go fullscreen, **export leads as CSV**, and clear the leaderboard.
- **F**: fullscreen. **M**: music on/off.
- **Idle reset:** menus return to the attract screen after 30s with no input; a game in progress returns after 60s.

## Event modes (operator menu → EVENT MODE)
- **IECA SHOW** (default): offline booth board. Players enter name + company; the title shows "IECA EDITION". Export leads with EXPORT CSV.
- **PUBLIC**: names only, on a separate board. This is the board to move online (Firebase) for the website after the show.
- Both modes reject offensive names, including number spellings like 5H1T.

## Retro USB controller (NES style)
Generic USB pads number their buttons differently. Once per laptop: operator menu → CONTROLLER → press A, then B. After that A selects and lays blankets; B goes back (and also lays blankets during play). Start pauses.

## Character select
After PRESS START, players pick from the six-person crew (Daryl, Sheryl, Marcus, Tanya, Rosa, Kenji). Below the crew, **UNLOCK SECRET HEROES** opens a second page of guest stars (Mike, Wayne, Oprah, Ralph, Leia, Donald, Chief, plus two open slots). In the operator menu, SECRET HEROES → LOCKED keeps the button visible but locked. The leaderboard shows each player's face. Names and one-line bios are in `tools/build_crew.py`; the secret list is `SECRET_IDS` in `src/game.html`. Leia's walk frames are composited by `tools/build_leia_walk.py` (Canva refused that sprite sheet).

## Tablet arcade cabinet (joystick + 1 button)
- One button is enough: it starts the game, lays blankets, picks menu items and confirms letters in name entry. The joystick moves the hero and the menu cursor.
- The on-screen D-pad hides as soon as the joystick or button is used, and comes back if someone touches the screen.
- **Android or Windows tablet:** a standard USB arcade encoder (e.g. "zero delay" kits) works over a USB-C/OTG adapter as a gamepad.
- **iPad:** iPadOS doesn't support generic USB gamepads. Use an encoder that can run in **keyboard mode** (arrows + Space/Enter), which works as a USB keyboard.
- Before the doors open, tap the screen once after loading so the browser allows sound. Then turn off auto-lock/screen sleep, and lock the tablet to the game (Android: App Pinning; iPad: Guided Access).

## Kiosk setup (recommended)
Launch Chrome in kiosk mode so audio starts without a click:

```
chrome --kiosk --autoplay-policy=no-user-gesture-required "file:///path/to/Erosion_Hero.html"
```

## Leaderboard / Firebase
Scores are saved in this browser's localStorage (`erosionHeroLeads_v1`, same key as the prototype). The store is a small async adapter (`LocalStore` in `src/game.html`). For Firebase, implement the same `list()`, `add(entry)` and `clear()` methods against Firestore and assign the result to `Board.store`. Nothing else needs to change.

## The seven sites
Blankets first, then catch basins, then the two turbidity curtains.
1. **Residential Lot**: blankets
2. **Hillside Grading**: blankets on slopes
3. **Detention Pond**: blankets around a pond
4. **Main Street**: catch basins, side-scrolling street with the BMP truck
5. **Uphill Street**: catch basins seen from above. The hero walks uphill, traffic runs both ways, and any drain that rolls past the bottom unprotected costs a life. Tuning lives in its LEVELS entry (`scrollSpeed`, `basinSpawnInterval`, `carSpeed`, `obstacleInterval*`).
6. **Lakeshore**: turbidity curtain, top to bottom from the shore
7. **Riverbank**: turbidity curtain, left to right along the bank while the current pushes the boat out (finale)

## Scoring
- +50 per erosion control blanket (each covers 2 tiles), +25 per protected inlet; -15 per life lost.
- Blanket and basin sites: +100 for clearing the site, +100 more if you finished it without getting hit.
- Curtain sites (one pass each, 45s limit): your match to the plan, 0-100%, x 10 points (max 1,000), plus +100 for securing the site (Lakeshore). Being 5px off the line on average scores about 85%; only a near-perfect trace gets 100%.
- Finishing all seven: +50 per remaining life.
- Leaderboard ties are broken by the average curtain match, then by whoever scored first.
