# GREEN CANYON - buildable layout spec

Generated blockout for a 5-beacon team-deathmatch arena. Everything here is **generated geometry**: coordinates, polygons and tables computed by script from measurements of a level-design blueprint. **No third-party artwork is copied, embedded, traced pixel-for-pixel, or included in this folder.**

## Provenance and permissions

| item | status |
|---|---|
| This `green-canyon-SPEC/` folder (diagrams, JSON, CSV, this file) | written by me, released under CC0 - see `LICENSE`. Use it however you want, including commercially. |
| The layout it describes | read off a published level-design portfolio piece by **Oleksii Andrusevych** (ArtStation `GeWmaW`, "Map green canyon"). The artwork stays his; the original images are *not* redistributed here. |
| Mech Arena / Plarium assets | not part of this folder. Their notice reserves all rights. |

> Read this honestly: a diagram being CC0 does not make a *clone of someone's game map* free to ship. Use it to learn layout and to build your own thing. If it ever becomes a product, change the layout enough that it's yours.

## How it was measured

1. Colour-key the blueprint for the three height bands and the marker overlays. 
2. Drop legend swatches by component size; keep only real map lobes (>= 8,000 px).
3. Locate beacons / spawn pads / centre gates as connected components; fit each sight-line arc by bearing-wise median so the thin axis lines can't bias it.
4. Trace band outlines, preserve interior voids as rock pockets, simplify to polygons.
5. Convert px -> m with `M_PER_PX = 0.10123` 
   (assumption: 140 m across the playable span). Everything in metres scales linearly with that one number.

## Layout at a glance

- playable span **140 x 63 m**, walkable area **3,916 m2**
- symmetry: **bilateral about the vertical centre line** (centre line at x = 70 m)
- height bands: **922 m2 at 16 m** (2 lobes), **2,599 m2 at 8 m** (2 lobes), **667 m2 at 0 m** (1 lobe)
- capture beacons: **5**   centre gates: **2**   spawn pads: **8 per team**
- sight-line radius clear from each spawn: **42 m / 42 m**, sweeping **224 deg / 220 deg** (the near-identical pair is the check that the measurement is clean)

## Vertical profile, Team A -> Team B

| from (m) | to (m) | height |
|---|---|---|
| 0.8 | 20.9 | 16 m |
| 21.1 | 30.6 | wall / rock face |
| 30.8 | 58.7 | 8 m |
| 58.9 | 81.4 | 0 m |
| 81.8 | 109.3 | 8 m |
| 109.5 | 119.0 | wall / rock face |
| 119.2 | 139.1 | 16 m |

So the route in is a **stadium funnel**: 16 m plateau -> 8 m terrace -> 0 m pit, two steps of 8 m each. At a 1:6 ramp gradient each step needs **48 m of run**, or use jump pads / elevators at the two gate slots instead - which is what the source map does.

## Node coordinates (metres, origin = Team A plateau outer edge, x towards Team B)

| id | x | y | standing height | open ground within 6 m ring |
|---|---|---|---|---|
| B1 | 33.4 | 28.0 | 8 m | 84% |
| B2 | 44.5 | 56.4 | 8 m | 83% |
| B3 | 70.0 | 31.6 | 0 m | 100% |
| B4 | 95.5 | 6.9 | 8 m | 84% |
| B5 | 106.6 | 35.3 | 8 m | 82% |
| SPAWN A | 5.9 | 31.7 | 16 m | 8 pads |
| SPAWN B | 134.1 | 31.6 | 16 m | 8 pads |
| GATE 1 | 68.6 | 18.3 | 0 m | 3.9 x 2.0 m slot |
| GATE 2 | 71.3 | 45.1 | 0 m | 3.8 x 1.9 m slot |

Beacon marker footprint in the source drawing is 7.8 m across. `B3` is the only beacon in the low pit (100% open, no rock inside its ring); `B1/B2/B4/B5` each sit with ~16% of their ring blocked by rock, which is what makes them contestable rather than free.

## Build kit (what you actually place)

| layer | count | spec |
|---|---|---|
| base plate | 1 | 140 x 63 m, 0 m datum |
| terrace slabs (8 m) | 2 | outer rings in `data/green-canyon-geometry.json` -> `polygons.H8`; 2,381 m2 walkable after pockets |
| spawn plateaus (16 m) | 2 | `polygons.H16`, 922 m2 combined |
| centre pit (0 m) | 1 | `polygons.H0`, 614 m2 |
| rock pockets / cover | 5 fully enclosed, plus every concavity in the outer rings | height 8-16 m above the band you stand on |
| beacon pads | 5 | disc, capture radius **8 m (my design value, not measured)** |
| gates | 2 | 3.9 x 2.0 m slots on the pit's north and south faces |
| spawn pads | 8 per team | staggered 2 x 4, cluster ~2.5 x 4.9 m at drawing scale - the icons are schematic, so treat this as one spawn ZONE, not literal pad positions |
| sight-line rings | 2 | 41.7 m from each spawn centre, ~220 deg clear |

### Easiest version

Drop the polygons and build it as **11 boxes on a 10 m grid**: 2 x (16 m plateau, 20 m wide) at the ends, 2 x (8 m terrace, 28 m) either side of the middle, 1 x (0 m pit, 22 m) in the centre, and 6 cover blocks inside the terrace ring at the pocket positions in the diagram. That is the whole map and it is playable, because the *shape* that matters - the funnel into a shared low centre with 4 flanking beacons and 1 free-beacon in the pit - survives at that coarseness. The exact rock silhouettes are cosmetic.

## Measured vs chosen

| value | source |
|---|---|
| node positions, band areas, band heights, gate slots, footprint, sight-line radii | **measured** from the blueprint |
| metres-per-pixel (0.10123) | assumption: 140 m span |
| 8 m capture radius, 1:6 ramp, pad spacing, cover block count | **my design choices** |
| team sizes, timers, respawns, mode rules | not in the drawing at all - invent them |
