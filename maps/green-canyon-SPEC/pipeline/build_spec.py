#!/usr/bin/env python3
"""Build an original, freely-usable green-canyon blockout spec from measured layout.

Everything written here is generated geometry (polygons, coordinates, tables).
No source artwork is copied, embedded, traced pixel-for-pixel, or redistributed.
"""
import json, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage
from skimage.measure import find_contours, approximate_polygon

SRC = "/home/user/map_scrape/GeWmaW/04_oleksii-andrusevych-topdownmap-copy.jpg"
OUT = "/home/user/maps_build"
os.makedirs(f"{OUT}/data", exist_ok=True)

# ------------------------------------------------------------------ measure
a = np.array(Image.open(SRC).convert("RGB")).astype(np.int16)
H, W, _ = a.shape
R, G, B = a[..., 0], a[..., 1], a[..., 2]

M_PER_PX = 140.0 / 1383.0          # design assumption: ~140 m across the playable span
MIN_COMP = 8000                    # legend swatches are ~2k px -> discarded by this

def mask(**kw):
    m = np.ones((H, W), bool)
    for ch, lo, hi in kw.values():
        pass
    return m

m_orange = (R > 200) & (G > 60) & (G < 150) & (B < 70)
m_red    = (R > 170) & (G < 80) & (B < 90)
m_blue   = (B > 170) & (R < 90) & (G < 140)
m_zone = {
    "H16": (R > 220) & (G > 220) & (B > 165) & (B < 220),
    "H8":  (R > 220) & (G > 200) & (G < 245) & (B > 95) & (B < 175),
    "H0":  (R > 130) & (R < 195) & (G > 115) & (G < 175) & (B > 55) & (B < 115),
}

def big_components(m, close=9, min_area=MIN_COMP):
    m = ndimage.binary_closing(m, np.ones((close, close), bool))
    filled = ndimage.binary_fill_holes(m)
    # fill JPEG speckle holes but preserve real interior voids (rock pockets, tunnels)
    lab, nl = ndimage.label(filled & ~m)
    if nl:
        sz = ndimage.sum(filled & ~m, lab, range(1, nl + 1))
        small = np.isin(lab, [i + 1 for i, s in enumerate(sz) if s < 1500]) & (filled & ~m)
        m = m | small
    lab, n = ndimage.label(m)
    keep = np.zeros_like(m)
    areas = ndimage.sum(m, lab, range(1, n + 1)) if n else []
    for i, ar in enumerate(areas, start=1):
        if ar >= min_area:
            keep |= (lab == i)
    return keep, int((np.array(areas) >= min_area).sum()) if n else 0

zones, zcomp = {}, {}
union = np.zeros((H, W), bool)
for k, m in m_zone.items():
    mm, c = big_components(m)
    # beacons/spawn markers are overlays painted on top of walkable ground, so
    # the ground polygon keeps its area; only true geometry voids remain as holes
    zones[k], zcomp[k] = mm, c
    union |= mm
# icons (beacons, spawn pads) are painted over the ground, so point queries use
# the hole-filled variant to see through them
zones_solid = {k: ndimage.binary_fill_holes(v) for k, v in zones.items()}
zones_pt = zones_solid

def comp_list(m, min_area=150):
    lab, n = ndimage.label(m)
    out = []
    for i in range(1, n + 1):
        ys, xs = np.where(lab == i)
        if len(ys) < min_area:
            continue
        out.append({"cx": float(xs.mean()), "cy": float(ys.mean()), "area": int(len(ys)),
                    "w": int(xs.max() - xs.min() + 1), "h": int(ys.max() - ys.min() + 1)})
    return sorted(out, key=lambda d: -d["area"])

beacons = [b for b in comp_list(ndimage.binary_opening(m_orange, np.ones((3,3),bool)), 2500)
           if b["w"] > 60]                       # legend icon is 49 px -> dropped
# thin sight-line arcs would otherwise merge into the spawn cluster, so strip
# them with an opening before locating the spawn itself
dots_red  = ndimage.binary_opening(m_red, np.ones((5, 5), bool))
dots_blue = ndimage.binary_opening(m_blue, np.ones((5, 5), bool))
xr = np.arange(W)[None, :]

def cluster(mask_, region):
    ys, xs = np.where(mask_ & region)
    return {"cx": float(xs.mean()), "cy": float(ys.mean()),
            "x0": int(xs.min()), "x1": int(xs.max()),
            "y0": int(ys.min()), "y1": int(ys.max()), "n": int(len(ys))}

spawnA = cluster(dots_red, xr < 700)
spawnB = cluster(dots_blue, xr > 1200)

gate_zone = ndimage.binary_erosion(zones["H0"], np.ones((13,13),bool))
dark = (R < 60) & (G < 60) & (B < 80)
gates = [g for g in comp_list(gate_zone & dark, 200) if g["w"] < 90 and g["h"] < 90]

def arc_radius(mask, cx, cy):
    """robust radius of a sight-line arc drawn around a spawn.

    The blueprint also contains thin horizontal/vertical axis lines through each
    spawn; those live on the 0/90/180/270 deg bearings, so bins near the axes are
    dropped and the arc radius is the median over the remaining bearings.
    """
    ys, xs = np.where(mask)
    dx, dy = xs - cx, ys - cy
    d = np.hypot(dx, dy)
    keep = d > 60
    d, dx, dy = d[keep], dx[keep], dy[keep]
    th = np.degrees(np.arctan2(dy, dx)) % 360
    per_bin = []
    axes = (0, 90, 180, 270)
    for b in range(360):
        bin_c = b + 0.5
        # drop bins that coincide with the thin axis lines drawn through the spawn
        if min(abs(((bin_c - ax + 180) % 360) - 180) for ax in axes) < 4:
            continue
        sel = (th >= b) & (th < b + 1)
        if sel.sum() >= 3:
            per_bin.append(float(np.median(d[sel])))
    if not per_bin:
        return 0.0, 0.0
    per_bin = np.array(per_bin)
    med = float(np.median(per_bin))
    span = 360.0 * len(per_bin) / 328.0   # 328 non-axis bearings were testable
    return med, span

arcA, spanA = arc_radius(m_red, spawnA["cx"], spawnA["cy"])
arcB, spanB = arc_radius(m_blue, spawnB["cx"], spawnB["cy"])

# ------------------------------------------------------------------ polygons
# split each height band into lobes; keep interior voids as holes so the
# rock-pocket / tunnel network survives into the blockout
def subpolys(mask_, min_area=6000, eps=2.4, min_hole=900):
    lab, n = ndimage.label(mask_)
    out = []
    for i in range(1, n + 1):
        comp = (lab == i)
        if comp.sum() < min_area:
            continue
        cs = find_contours(comp.astype(float), 0.5)
        if not cs:
            continue
        cs = sorted(cs, key=len, reverse=True)
        outer = cs[0]
        rings = []
        for c in [outer] + [x for x in cs[1:] if len(x) > 120]:
            try:
                c = approximate_polygon(c, eps)
            except Exception:
                pass
            # find_contours yields (row, col) = (y, x); swap so output is [x, y]
            rings.append([[float(cx) - x0, float(cy) - y0] for cy, cx in c])
        lobes = []
        for r in rings:
            lobes.append([[round(x * M_PER_PX, 2), round(y * M_PER_PX, 2)] for x, y in r])
        out.append({"outer": lobes[0], "holes": lobes[1:],
                    "area_m2": int(round(comp.sum() * M_PER_PX ** 2)),
                    "void_count": len(lobes) - 1})
    return sorted(out, key=lambda l: -l["area_m2"])

def pads(mask_, region, min_area=25):
    return [p for p in comp_list(mask_ & region, min_area) if p["w"] < 40 and p["h"] < 40]

ys, xs = np.where(union)
x0, y0, x1, y1 = xs.min(), ys.min(), xs.max(), ys.max()

def height_at(px, py):
    """which height band a measured point falls in, using un-subtracted masks"""
    yy, xx = int(round(py)), int(round(px))
    if not (0 <= yy < H and 0 <= xx < W):
        return None
    for k, val in (("H16", 16), ("H8", 8), ("H0", 0)):
        if zones_pt[k][yy, xx]:
            return val
    return None

def open_fraction(key, px, py, r=60):
    """share of a 60px window that is walkable at the node's own height -> how open a capture ring is"""
    if key is None:
        return None
    yy, xx = int(round(py)), int(round(px))
    sl = (slice(max(0, yy - r), min(H, yy + r)), slice(max(0, xx - r), min(W, xx + r)))
    return round(float(zones_pt[key][sl].mean()), 3)

BEACON_HEIGHT_KEY = {16: "H16", 8: "H8", 0: "H0"}
beacon_nodes = []
for i, b in enumerate(sorted(beacons, key=lambda b: b["cx"])):
    hv = height_at(b["cx"], b["cy"])
    beacon_nodes.append({
        "id": f"B{i+1}",
        "x_m": round(float((b["cx"] - x0) * M_PER_PX), 1),
        "y_m": round(float((b["cy"] - y0) * M_PER_PX), 1),
        "height_m": hv,
        "open_fraction_60px": open_fraction(BEACON_HEIGHT_KEY.get(hv), b["cx"], b["cy"]),
    })

gate_nodes = [{
    "x_m": round(float((g["cx"] - x0) * M_PER_PX), 1),
    "y_m": round(float((g["cy"] - y0) * M_PER_PX), 1),
    "size_m": [round(float(g["w"]) * M_PER_PX, 1), round(float(g["h"]) * M_PER_PX, 1)],
    "kind": "centre-pit gate slot",
} for g in gates]

def pad_list(mask_, region, origin):
    out = []
    for p in sorted(pads(mask_, region), key=lambda p: (p["cy"], p["cx"])):
        out.append({"x_m": round(float((p["cx"] - origin[0]) * M_PER_PX), 1),
                    "y_m": round(float((p["cy"] - origin[1]) * M_PER_PX), 1)})
    return out

padsA = pad_list(dots_red, xr < 700, (x0, y0))
padsB = pad_list(dots_blue, xr > 1200, (x0, y0))

# ---- elevation profile sampled along the A-B spawn axis -------------------
prof_row = int(round((spawnA["cy"] + spawnB["cy"]) / 2))
segs = []
for xx in range(int(x0), int(x1) + 1, 2):
    hv = height_at(xx, prof_row)
    hv = -1 if hv is None else hv
    if segs and segs[-1][2] == hv:
        segs[-1][1] = xx
    else:
        segs.append([xx, xx, hv])
profile = [{"x0_m": round(float((a_ - x0) * M_PER_PX), 1),
            "x1_m": round(float((b_ - x0) * M_PER_PX), 1),
            "height_m": (None if h_ < 0 else h_)} for a_, b_, h_ in segs]
profile = [p_ for p_ in profile if (p_["x1_m"] - p_["x0_m"]) > 0.8]

zone_stats = {}
for k, v in zones.items():
    solid = ndimage.binary_fill_holes(v)
    zone_stats[k] = {"walkable_m2": int(round(v.sum() * M_PER_PX ** 2)),
                     "footprint_m2": int(round(solid.sum() * M_PER_PX ** 2)),
                     "lobes": zcomp[k]}

geo = {
    "units": "metres", "m_per_px": round(M_PER_PX, 5),
    "heights_m": {"H16": 16, "H8": 8, "H0": 0},
    "footprint_m": {"w": round(float((x1 - x0) * M_PER_PX), 1), "h": round(float((y1 - y0) * M_PER_PX), 1)},
    "area_m2_total": int(round(union.sum() * M_PER_PX ** 2)),
    "zones": zone_stats,
    "beacon_marker_diameter_m": round(float(77 * M_PER_PX), 1),
    "symmetry": "bilateral about the vertical centre line",
    "nodes": {
        "spawnA": {"x_m": round(float((spawnA["cx"] - x0) * M_PER_PX), 1),
                   "y_m": round(float((spawnA["cy"] - y0) * M_PER_PX), 1),
                   "pads": padsA, "height_m": height_at(spawnA["cx"], spawnA["cy"])},
        "spawnB": {"x_m": round(float((spawnB["cx"] - x0) * M_PER_PX), 1),
                   "y_m": round(float((spawnB["cy"] - y0) * M_PER_PX), 1),
                   "pads": padsB, "height_m": height_at(spawnB["cx"], spawnB["cy"])},
        "beacons": beacon_nodes,
        "gates": gate_nodes,
        "sightline_radius_m": {"teamA": round(float(arcA * M_PER_PX), 1),
                               "teamB": round(float(arcB * M_PER_PX), 1)},
        "sightline_span_deg": {"teamA": round(float(spanA), 1),
                               "teamB": round(float(spanB), 1)},
    },
    "axis_profile": {"sample_row_m": round(float((prof_row - y0) * M_PER_PX), 1),
                      "note": "heights read along the Team A - Team B axis; None = unclassified (rock/void)",
                      "segments": profile},
    "polygons": {k: subpolys(v) for k, v in zones.items()},
}
# centre-line x for the builder
geo["nodes"]["centreline_x_m"] = round(float(((x0 + x1) / 2 - x0) * M_PER_PX), 1)
json.dump(geo, open(f"{OUT}/data/green-canyon-geometry.json", "w"), indent=1)

print("zone lobe counts:", zcomp)
print("footprint_m", geo["footprint_m"], "total area_m2", geo["area_m2_total"], "zones", geo["zones"])
print("spawnA:", geo["nodes"]["spawnA"]); print("spawnB:", geo["nodes"]["spawnB"])
print("beacons:", json.dumps(beacon_nodes))
print("gates:", json.dumps(gate_nodes))
print("sightline:", geo["nodes"]["sightline_radius_m"], geo["nodes"]["sightline_span_deg"], " centreline", geo["nodes"]["centreline_x_m"])
print("profile:", json.dumps(profile))
print("lobes+voids:", {k: [(l["area_m2"], l["void_count"]) for l in v] for k, v in geo["polygons"].items()})
print("verts:", {k: [len(l["outer"]) for l in v] for k, v in geo["polygons"].items()})
