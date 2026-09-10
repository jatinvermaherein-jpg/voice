# AI builder brief - green-canyon-style 5-beacon arena

Plain-language spec written from the measured geometry above. It contains no artwork, no screenshots, no game names and no brand terms, so any image/mesh/level generator can take it without an IP question. Paste it in as-is.

## Brief

Build a symmetric team PvP arena footprint **140 m x 63 m** on a flat base plate, three height levels only: **0 m, 8 m, 16 m**.

Layout, left to right, mirrored about the centre:

- x 1-21 m (20 m wide): **spawn plateau at 16 m**, one per team
- x 21-31 m (10 m wide): **rock face / cliff wall**, unclimbable
- x 31-59 m (28 m wide): **main terrace ring at 8 m** with rock pockets cut into it
- x 59-81 m (23 m wide): **sunken centre pit at 0 m**
- x 82-109 m (28 m wide): **main terrace ring at 8 m** with rock pockets cut into it
- x 110-119 m (10 m wide): **rock face / cliff wall**, unclimbable
- x 119-139 m (20 m wide): **spawn plateau at 16 m**, one per team

- **5 capture beacons**: B1 at (33, 28) standing on 8 m, B2 at (44, 56) standing on 8 m, B3 at (70, 32) standing on 0 m, B4 at (96, 7) standing on 8 m, B5 at (107, 35) standing on 8 m.
  Capture radius 8 m. The centre beacon is fully open; the four outer ones each have about 16% of their ring blocked by rock so they can be contested from cover.
- **2 gate slots** in the centre pit wall at (69, 18) and (71, 45), each about 4 x 2 m - these are the elevators/chokepoints.
- **2 spawn zones**, 8 pads each in a staggered 2 x 4 block, at (6, 32) and (134, 32).
- Ramps only where you want a ground route: an 8 m step at 1:6 needs 48 m of run, so prefer jump pads or the gate elevators for the terrace-to-pit drop.
- Style: arid canyon rock, eroded concrete facility inserts, optional landmark props (a wrecked vehicle, a dam wall). Any original sci-fi industrial look. No branding, no logos.

## Easy version

11 boxes on a 10 m grid: 2 x 16 m plateaus at the ends (20 m wide), 2 x 8 m terraces (28 m), 1 x 0 m pit (22 m) in the middle, 6 cover blocks placed where the rock pockets sit. Add the 5 beacons and 2 gates. Playable at that coarseness.

## Files with the exact shapes

`data/green-canyon-geometry.json` -> `polygons.H0 / H8 / H16`, each lobe as `outer` plus `holes` rings in metres. Feed those rings straight into an extrude/solidify node and you have the map.

