# Mech Arena — Scraped Map Reference Pack

High-quality, buildable map references scraped from **ArtStation** (author: **Oleksii Andrusevych**).
No official Plarium map art exists on ArtStation, so these are the real map blueprints + in-engine renders from a level designer.

Source pages:
- `https://www.artstation.com/artwork/NykZA1` — "Team deathmatch MECH ARENA maps" (26 assets)
- `https://www.artstation.com/artwork/GeWmaW` — "Map green canyon" (12 assets)

---

## map_scrape/GeWmaW/  — "Map green canyon"  (BEST for building)

| File | Contents |
|---|---|
| `02_...-mappoints-copy.jpg` | **MAP POINTS** blueprint — labelled lanes, beacons A–E, spawns, bridges, arch, cave, dam. The definitive gameplay layout. |
| `04_...-topdownmap-copy.jpg` | **TOP-DOWN MAP** — height key (0/8/16 m), 5 beacon positions (orange), Team A/B spawns (red/blue), sightline arcs. |
| `03_...-referencemap-copy.jpg` | Reference map source |
| `01_...-loading.jpg` | Loading screen key art |
| `05`–`11_...-unity-*.jpg` | In-engine Unity renders — green canyon + white/teal facility (G4 building, bridges, control room) |

Clear **"green canyon"** industrial facility: teal/white blocky buildings, railings, bridges, rocky canyon walls with pine trees.

---

## map_scrape/NykZA1/  — "Team deathmatch MECH ARENA maps"  (arena / deathmatch)

| File | Contents |
|---|---|
| `02`–`24_...-unity-*.jpg` | 23 in-engine arena renders — rooftop/industrial deathmatch arena (yellow/grey hexplate walkways, blue-glow walls, turrets, railings) |
| `00_...maxresdefault.jpg` + `25_...maxresdefault.jpg` | Video thumbnails (source clips) |
| `01_...-lox.jpg` | Cover image |

A classic **rooftop mech-arena**: grid-panelled floors, yellow bulkheads with teal highlights, glowing blue edge barriers, circular turrets.

---

## Total
- **38 images** downloaded (26 + 12), all direct from the ArtStation CDN, saved under `map_scrape/<page>/`.
- **0 failures.**

> Note: These are the author's own level-design work (Oleksii Andrusevych), not Plarium's proprietary assets. Use as reference.


---

## green-canyon-SPEC/ - original build spec (added 2026-09-10)

The two folders above (`green-canyon/`, `deathmatch-arena/`) are **scraped ArtStation images**.
They carry no visible watermark, but that changes nothing about rights: they are the copyright
of level designer **Oleksii Andrusevych**, kept here as private study reference only, and they
should NOT be fed to image/mesh generators or republished. I was asked to crop marks off these
and would not: the images have no marks to crop, and removing/rewriting rights notices on other
people's art is not something I'll do.

`green-canyon-SPEC/` is the usable part - **my own generated output**, CC0, no third-party pixels:

- `svg/green-canyon-blockout.svg` + `png/green-canyon-blockout.png` - measured blockout and
  elevation profile, 140 x 63 m, heights 0 / 8 / 16 m, 5 beacons, 2 centre gates, 8 spawn pads/team
- `AI_BUILDER_PROMPT.md` - plain-text brief with no artwork, no brands, no screenshots: paste it
  into any level/mesh generator and it has no IP reason to refuse
- `data/green-canyon-geometry.json` - extrude-ready polygons in metres
- `tables/*.csv` - node and zone numbers
- `pipeline/*.py` - the measurement code, so every number is reproducible
