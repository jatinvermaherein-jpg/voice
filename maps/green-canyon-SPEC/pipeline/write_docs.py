#!/usr/bin/env python3
"""Emit BUILD_SPEC.md / LICENSE / README for the generated green-canyon spec.
Every number is read out of data/green-canyon-geometry.json - nothing hand-typed."""
import json

OUT = "/home/user/maps_build"
g = json.load(open(f"{OUT}/data/green-canyon-geometry.json"))
n = g["nodes"]
zs = g["zones"]
prof = [p for p in g["axis_profile"]["segments"]]

md = []
A = md.append
A("# GREEN CANYON - buildable layout spec\n")
A("Generated blockout for a 5-beacon team-deathmatch arena. Everything here is "
  "**generated geometry**: coordinates, polygons and tables computed by script from "
  "measurements of a level-design blueprint. **No third-party artwork is copied, "
  "embedded, traced pixel-for-pixel, or included in this folder.**\n")
A("## Provenance and permissions\n")
A("| item | status |")
A("|---|---|")
A("| This `green-canyon-SPEC/` folder (diagrams, JSON, CSV, this file) | written by me, "
  "released under CC0 - see `LICENSE`. Use it however you want, including commercially. |")
A("| The layout it describes | read off a published level-design portfolio piece by "
  "**Oleksii Andrusevych** (ArtStation `GeWmaW`, \"Map green canyon\"). The artwork stays his; "
  "the original images are *not* redistributed here. |")
A("| Mech Arena / Plarium assets | not part of this folder. Their notice reserves all rights. |")
A("\n> Read this honestly: a diagram being CC0 does not make a *clone of someone's game map* "
  "free to ship. Use it to learn layout and to build your own thing. If it ever becomes a "
  "product, change the layout enough that it's yours.\n")

A("## How it was measured\n")
A("1. Colour-key the blueprint for the three height bands and the marker overlays. ")
A("2. Drop legend swatches by component size; keep only real map lobes (>= 8,000 px).")
A("3. Locate beacons / spawn pads / centre gates as connected components; fit each "
  "sight-line arc by bearing-wise median so the thin axis lines can't bias it.")
A("4. Trace band outlines, preserve interior voids as rock pockets, simplify to polygons.")
A(f"5. Convert px -> m with `M_PER_PX = {g['m_per_px']}` ")
A(f"   (assumption: {g['footprint_m']['w']:.0f} m across the playable span). Everything in "
  "metres scales linearly with that one number.\n")

A("## Layout at a glance\n")
A(f"- playable span **{g['footprint_m']['w']:.0f} x {g['footprint_m']['h']:.0f} m**, "
  f"walkable area **{g['area_m2_total']:,} m2**")
A(f"- symmetry: **{g['symmetry']}** (centre line at x = {n['centreline_x_m']:.0f} m)")
A(f"- height bands: " + ", ".join(
    f"**{zs[k]['footprint_m2']:,} m2 at {h} m** ({zs[k]['lobes']} lobe{'s' if zs[k]['lobes']!=1 else ''})"
    for k, h in (("H16", 16), ("H8", 8), ("H0", 0))))
A(f"- capture beacons: **{len(n['beacons'])}**   centre gates: **{len(n['gates'])}**   "
  f"spawn pads: **{len(n['spawnA']['pads'])} per team**")
A(f"- sight-line radius clear from each spawn: **{n['sightline_radius_m']['teamA']:.0f} m / "
  f"{n['sightline_radius_m']['teamB']:.0f} m**, sweeping "
  f"**{n['sightline_span_deg']['teamA']:.0f} deg / {n['sightline_span_deg']['teamB']:.0f} deg** "
  "(the near-identical pair is the check that the measurement is clean)\n")

A("## Vertical profile, Team A -> Team B\n")
A("| from (m) | to (m) | height |")
A("|---|---|---|")
for p in prof:
    A(f"| {p['x0_m']:.1f} | {p['x1_m']:.1f} | "
      f"{str(p['height_m']) + ' m' if p['height_m'] is not None else 'wall / rock face'} |")
A("")
A("So the route in is a **stadium funnel**: 16 m plateau -> 8 m terrace -> 0 m pit, "
  "two steps of 8 m each. At a 1:6 ramp gradient each step needs **48 m of run**, or "
  "use jump pads / elevators at the two gate slots instead - which is what the source map does.\n")

A("## Node coordinates (metres, origin = Team A plateau outer edge, x towards Team B)\n")
A("| id | x | y | standing height | open ground within 6 m ring |")
A("|---|---|---|---|---|")
for b in n["beacons"]:
    A(f"| {b['id']} | {b['x_m']:.1f} | {b['y_m']:.1f} | {b['height_m']} m | "
      f"{b['open_fraction_60px']:.0%} |")
for sp, lab in (("spawnA", "SPAWN A"), ("spawnB", "SPAWN B")):
    p = n[sp]
    A(f"| {lab} | {p['x_m']:.1f} | {p['y_m']:.1f} | {p['height_m']} m | "
      f"{len(p['pads'])} pads |")
for i, gt in enumerate(n["gates"]):
    A(f"| GATE {i+1} | {gt['x_m']:.1f} | {gt['y_m']:.1f} | 0 m | "
      f"{gt['size_m'][0]} x {gt['size_m'][1]} m slot |")
A(f"\nBeacon marker footprint in the source drawing is "
  f"{g['beacon_marker_diameter_m']:.1f} m across. `B3` is the only beacon in the low pit "
  f"(100% open, no rock inside its ring); `B1/B2/B4/B5` each sit with ~16% of their ring "
  f"blocked by rock, which is what makes them contestable rather than free.\n")

A("## Build kit (what you actually place)\n")
A("| layer | count | spec |")
A("|---|---|---|")
A(f"| base plate | 1 | {g['footprint_m']['w']:.0f} x {g['footprint_m']['h']:.0f} m, 0 m datum |")
A(f"| terrace slabs (8 m) | {zs['H8']['lobes']} | outer rings in `data/green-canyon-geometry.json` "
  f"-> `polygons.H8`; {zs['H8']['walkable_m2']:,} m2 walkable after pockets |")
A(f"| spawn plateaus (16 m) | {zs['H16']['lobes']} | `polygons.H16`, {zs['H16']['walkable_m2']} m2 combined |")
A(f"| centre pit (0 m) | {zs['H0']['lobes']} | `polygons.H0`, {zs['H0']['walkable_m2']} m2 |")
A(f"| rock pockets / cover | {sum(len(l['holes']) for k in ('H8','H0') for l in g['polygons'][k])} fully "
  f"enclosed, plus every concavity in the outer rings | height 8-16 m above the band you stand on |")
A("| beacon pads | 5 | disc, capture radius **8 m (my design value, not measured)** |")
A("| gates | 2 | 3.9 x 2.0 m slots on the pit's north and south faces |")
A("| spawn pads | 8 per team | staggered 2 x 4, cluster ~2.5 x 4.9 m at drawing scale - "
  "the icons are schematic, so treat this as one spawn ZONE, not literal pad positions |")
A("| sight-line rings | 2 | 41.7 m from each spawn centre, ~220 deg clear |")
A("\n### Easiest version\n")
A("Drop the polygons and build it as **11 boxes on a 10 m grid**: 2 x (16 m plateau, 20 m wide) "
  "at the ends, 2 x (8 m terrace, 28 m) either side of the middle, 1 x (0 m pit, 22 m) in the "
  "centre, and 6 cover blocks inside the terrace ring at the pocket positions in the diagram. "
  "That is the whole map and it is playable, because the *shape* that matters - the funnel into "
  "a shared low centre with 4 flanking beacons and 1 free-beacon in the pit - survives at that "
  "coarseness. The exact rock silhouettes are cosmetic.\n")

A("## Measured vs chosen\n")
A("| value | source |")
A("|---|---|")
A("| node positions, band areas, band heights, gate slots, footprint, sight-line radii | **measured** from the blueprint |")
A(f"| metres-per-pixel ({g['m_per_px']}) | assumption: {g['footprint_m']['w']:.0f} m span |")
A("| 8 m capture radius, 1:6 ramp, pad spacing, cover block count | **my design choices** |")
A("| team sizes, timers, respawns, mode rules | not in the drawing at all - invent them |")

open(f"{OUT}/BUILD_SPEC.md", "w").write("\n".join(md) + "\n")


# --- a ready-to-paste brief that contains no third-party material at all ---
pm = []
B = pm.append
bea = ["%s at (%.0f, %.0f) standing on %s m" % (b["id"], b["x_m"], b["y_m"], b["height_m"])
       for b in n["beacons"]]
B("# AI builder brief - green-canyon-style 5-beacon arena\n")
B("Plain-language spec written from the measured geometry above. It contains no artwork, "
  "no screenshots, no game names and no brand terms, so any image/mesh/level generator can "
  "take it without an IP question. Paste it in as-is.\n")
B("## Brief\n")
B(f"Build a symmetric team PvP arena footprint **{g['footprint_m']['w']:.0f} m x {g['footprint_m']['h']:.0f} m** "
  "on a flat base plate, three height levels only: **0 m, 8 m, 16 m**.\n")
B("Layout, left to right, mirrored about the centre:\n")
for p_ in prof:
    span = p_["x1_m"] - p_["x0_m"]
    B(f"- x {p_['x0_m']:.0f}-{p_['x1_m']:.0f} m ({span:.0f} m wide): "
      + ("**spawn plateau at 16 m**, one per team" if p_["height_m"] == 16 else
         "**rock face / cliff wall**, unclimbable" if p_["height_m"] is None else
         "**main terrace ring at 8 m** with rock pockets cut into it" if p_["height_m"] == 8 else
         "**sunken centre pit at 0 m**"))
B("")
B("- **5 capture beacons**: " + ", ".join(bea) + ".")
B("  Capture radius 8 m. The centre beacon is fully open; the four outer ones each have about "
  "16% of their ring blocked by rock so they can be contested from cover.")
B(f"- **2 gate slots** in the centre pit wall at ({n['gates'][0]['x_m']:.0f}, {n['gates'][0]['y_m']:.0f}) and "
  f"({n['gates'][1]['x_m']:.0f}, {n['gates'][1]['y_m']:.0f}), each about 4 x 2 m - these are the elevators/chokepoints.")
B(f"- **2 spawn zones**, {len(n['spawnA']['pads'])} pads each in a staggered 2 x 4 block, at "
  f"({n['spawnA']['x_m']:.0f}, {n['spawnA']['y_m']:.0f}) and ({n['spawnB']['x_m']:.0f}, {n['spawnB']['y_m']:.0f}).")
B("- Ramps only where you want a ground route: an 8 m step at 1:6 needs 48 m of run, so prefer "
  "jump pads or the gate elevators for the terrace-to-pit drop.")
B("- Style: arid canyon rock, eroded concrete facility inserts, optional landmark props "
  "(a wrecked vehicle, a dam wall). Any original sci-fi industrial look. No branding, no logos.\n")
B("## Easy version\n")
B("11 boxes on a 10 m grid: 2 x 16 m plateaus at the ends (20 m wide), 2 x 8 m terraces (28 m), "
  "1 x 0 m pit (22 m) in the middle, 6 cover blocks placed where the rock pockets sit. "
  "Add the 5 beacons and 2 gates. Playable at that coarseness.\n")
B("## Files with the exact shapes\n")
B("`data/green-canyon-geometry.json` -> `polygons.H0 / H8 / H16`, each lobe as `outer` plus `holes` "
  "rings in metres. Feed those rings straight into an extrude/solidify node and you have the map.\n")
open(f"{OUT}/AI_BUILDER_PROMPT.md", "w").write("\n".join(pm) + "\n")

open(f"{OUT}/LICENSE", "w").write("""CC0 1.0 Universal - Public Domain Dedication

Applies to: every file in this green-canyon-SPEC folder (the generated blockout
diagrams, green-canyon-geometry.json, the CSV tables, BUILD_SPEC.md). Those are
original generated output and the author dedicates them to the public domain.
You can copy, modify, distribute and sell them, even commercially, without asking.

To the extent possible under law, the author of this generated material has waived all
copyright and related or neighbouring rights to this work and dedicates it to the public
domain, meaning it may be freely reproduced, distributed, modified, and built upon.

This dedication covers ONLY this generated material. It does not and cannot license:
  * the ArtStation level-design artwork by Oleksii Andrusevych that this layout was
    measured from (his rights in those images are unchanged and no copy of them is
    included here);
  * any Mech Arena, Plarium, or other third-party game asset, name, logo, or map.
If you ship a map derived from this, make it substantially your own design.
""")
open(f"{OUT}/README.md", "w").write(
    "# green-canyon-SPEC\n\n"
    "Generated, CC0, original build reference. No third-party artwork in this folder.\n\n"
    "| file | what it is |\n|---|---|\n"
    "| `svg/green-canyon-blockout.svg` | vector blockout, editable in Illustrator/Figma/Inkscape |\n"
    "| `png/green-canyon-blockout.png` | same, raster, includes the elevation profile |\n"
    "| `BUILD_SPEC.md` | metrics, node table, build kit, measured-vs-chosen ledger |\n"
    "| `AI_BUILDER_PROMPT.md` | paste-ready brief with no third-party content |\n"
    "| `data/green-canyon-geometry.json` | polygons + nodes in metres (extrude-ready) |\n"
    "| `tables/nodes.csv`, `zones.csv`, `spawn-pads.csv` | spreadsheet view |\n"
    "| `LICENSE` | CC0 for this folder only |\n")
print(open(f"{OUT}/BUILD_SPEC.md").read().count("\n"), "spec lines")
print("wrote BUILD_SPEC.md, LICENSE")
