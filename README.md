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

## Title screen
PRESS START plays. HOW TO PLAY and LEADERBOARD are below it (joystick down/left/right + A, or click/tap). A leaderboard opened from the title stays on screen until someone exits (idle reset is skipped), so it can be left up at the booth.

## Operator menu (PIN protected)
- Open it with the small hard-hat icon (bottom right of the title) or the backtick key `` ` ``. It asks for the operator PIN: **123** by default. Enter it with UP/DOWN + A on a controller, by typing, or on the on-screen keypad. Change it in the menu under OPERATOR PIN.
- Inside: jump to any site, event mode, controller setup, secret heroes, music/SFX/scanlines/idle reset, fullscreen, PIN, and conference leads.
- **F**: fullscreen. **M**: music on/off.
- **Idle reset:** menus return to the title after 30s with no input; a game in progress returns after 60s.

## Event modes (operator menu > EVENT MODE)
- **PUBLIC** (default): names only. When `FIREBASE_CONFIG` is set in `src/game.html`, scores go to the online leaderboard. Each score is saved on the device first and uploaded when there's internet, so nothing is lost offline. The title has no badge.
- **CONFERENCE**: offline board on this laptop only (browser storage), name + company, title shows "CONFERENCE EDITION". **EXPORT CSV** downloads the leads ranked by score (the top row is your prize winner). **RESET** only works after exporting the current list, then asks to confirm, so the board is ready for the next event.
- Both modes reject offensive names, including number spellings like 5H1T.

## Retro USB controller (NES style)
Generic USB pads number their buttons differently. Once per laptop: operator menu → CONTROLLER → press A, then B. After that A selects and lays blankets; B goes back (and also lays blankets during play). Start pauses.

## Character select
After PRESS START, players pick from the six-person crew (Daryl, Sheryl, Marcus, Tanya, Rosa, Kenji). Below the crew, **UNLOCK SECRET HEROES** opens a second page of guest stars (Mike, Wayne, Oprah, Ralph, Leia, Donald, Chief, Taylor, Doug). In the operator menu, SECRET HEROES → LOCKED keeps the button visible but locked. The leaderboard shows each player's face. Names and one-line bios are in `tools/build_crew.py`; the secret list is `SECRET_IDS` in `src/game.html`. Leia's walk frames are composited by `tools/build_leia_walk.py` (Canva refused that sprite sheet).

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
Conference scores live in this browser's localStorage (`erosionHeroLeads_v1`). Public scores are kept in `erosionHeroScores_public_v1` and, once Firebase is configured, uploaded to the Firestore collection `scores` through the REST API (no SDK). To go online, paste `{apiKey:"...", projectId:"..."}` from the Firebase web config into `FIREBASE_CONFIG` and rebuild. The security rules allow anyone to read and add scores (name, crew, score, site, curtain %, date only), and nobody to edit or delete them from the game.

## Scoring
- +50 per erosion control blanket (each covers 2 tiles), +25 per protected inlet; -15 per life lost.
- Blanket and basin sites: +100 for clearing the site, +100 more if you finished it without getting hit.
- Curtain sites (one pass each, 45s limit): your match to the plan, 0-100%, x 10 points (max 1,000), plus +100 for securing the site (Lakeshore). Being 5px off the line on average scores about 85%; only a near-perfect trace gets 100%.
- Finishing all seven: +50 per remaining life.
- Leaderboard ties are broken by the average curtain match, then by whoever scored first.
