#!/usr/bin/env python3
"""Render the measured green-canyon geometry into a blockout diagram (SVG + PNG),
CSV tables, and a build spec. Purely generated geometry - no source pixels.
"""
import json, os, csv

OUT = "/home/user/maps_build"
geo = json.load(open(f"{OUT}/data/green-canyon-geometry.json"))
os.makedirs(f"{OUT}/svg", exist_ok=True)
os.makedirs(f"{OUT}/png", exist_ok=True)
os.makedirs(f"{OUT}/tables", exist_ok=True)

FW, FH = geo["footprint_m"]["w"], geo["footprint_m"]["h"]
PAD_M = 14.0                      # margin in metres for legend/labels
S = 13.0                          # px per metre
TOP = 120.0                       # px reserved for the header text
PROF_H = 200.0                    # px for the elevation-profile strip
VW, VH = (FW + 2 * PAD_M) * S, TOP + (FH + 2 * PAD_M) * S + 70 + PROF_H

def X(m): return (m + PAD_M) * S
def Y(m): return TOP + (m + PAD_M) * S

BG        = "#10161c"
ZONE_FILL = {"H0": "#3d4b59", "H8": "#7f9bb0", "H16": "#dfe9f2"}
ZONE_STK  = {"H0": "#9fb2c4", "H8": "#b9cfe2", "H16": "#ffffff"}
BEACON    = "#ff8a1f"
SPAWNA    = "#e8394a"
SPAWNB    = "#3f7dff"
GATE      = "#b45cff"
GRID      = "#1b2630"
TXT       = "#e7eef5"
SUB       = "#8fa3b5"

shapes = []          # ("poly", pts_list, fill, stroke, sw) / ("circle",...) / ("text",...)
def poly(rings, fill, stroke, sw=1.6):
    shapes.append(("poly", rings, fill, stroke, sw))
def polypix(rings, fill, stroke, sw=1.2):
    shapes.append(("polypix", rings, fill, stroke, sw))
def circle(cx, cy, r, fill, stroke, sw=1.6, dash=None):
    shapes.append(("circle", cx, cy, r, fill, stroke, sw, dash))
def line(x0, y0, x1, y1, stroke, sw=1.2, dash=None):
    shapes.append(("line", x0, y0, x1, y1, stroke, sw, dash))
def text(x, y, s, size=13, fill=TXT, anchor="start", weight="normal", opacity=1.0, plate=False):
    shapes.append(("label" if plate else "text", x, y, s, size, fill, anchor, weight, opacity, plate))

# ---- 10 m grid -------------------------------------------------------------
for gx in range(0, int(FW) + 1, 10):
    line(X(gx), Y(0), X(gx), Y(FH), GRID, 1.0)
for gy in range(0, int(FH) + 1, 10):
    line(X(0), Y(gy), X(FW), Y(gy), GRID, 1.0)

# ---- height bands (low -> high so upper bands paint over lower) -----------
for key in ("H0", "H8", "H16"):
    for lobe in geo["polygons"][key]:
        rings = [lobe["outer"]]
        poly(rings, ZONE_FILL[key], ZONE_STK[key], 1.8)
    for lobe in geo["polygons"][key]:
        for h in lobe["holes"]:
            poly([h], BG, ZONE_STK[key], 1.2)

# ---- centre line ----------------------------------------------------------
cl = geo["nodes"]["centreline_x_m"]
line(X(cl), Y(-6), X(cl), Y(FH + 6), "#61798d", 1.2, "7 7")

# ---- sight-line arcs ------------------------------------------------------
for sp, r, col in (("spawnA", geo["nodes"]["sightline_radius_m"]["teamA"], SPAWNA),
                   ("spawnB", geo["nodes"]["sightline_radius_m"]["teamB"], SPAWNB)):
    n = geo["nodes"][sp]
    circle(X(n["x_m"]), Y(n["y_m"]), r * S, "none", col, 1.4, "10 8")

# ---- gates ----------------------------------------------------------------
for i, g in enumerate(geo["nodes"]["gates"]):
    w, h = g["size_m"]
    poly([[[g["x_m"] - w / 2, g["y_m"] - h / 2], [g["x_m"] + w / 2, g["y_m"] - h / 2],
           [g["x_m"] + w / 2, g["y_m"] + h / 2], [g["x_m"] - w / 2, g["y_m"] + h / 2]]],
         "none", GATE, 2.4)
    text(X(g["x_m"]), Y(g["y_m"]) - 16, f"GATE {i+1}", 12, GATE, "middle", "bold", plate=True)

# ---- beacons --------------------------------------------------------------
# inner disc = marker size measured off the blueprint; outer dashed ring =
# the 8 m capture radius chosen for this build (a design value, not measured)
MARK_R = geo.get("beacon_marker_diameter_m", 7.8) / 2.0
CAP_R = 8.0
for b in geo["nodes"]["beacons"]:
    circle(X(b["x_m"]), Y(b["y_m"]), CAP_R * S, "none", BEACON, 1.3, "6 6")
    circle(X(b["x_m"]), Y(b["y_m"]), max(MARK_R, 2.4) * S, BEACON + "55", BEACON, 2.2)
    circle(X(b["x_m"]), Y(b["y_m"]), 1.0 * S, BEACON, "none")
    text(X(b["x_m"]) + 9.6 * S, Y(b["y_m"]) - 8.6 * S, f"{b['id']}  {b['height_m']} m",
         14, BEACON, "start", "bold", plate=True)

# ---- spawns ---------------------------------------------------------------
for sp, col, name in (("spawnA", SPAWNA, "SPAWN A"), ("spawnB", SPAWNB, "SPAWN B")):
    n = geo["nodes"][sp]
    for p in n["pads"]:
        circle(X(p["x_m"]), Y(p["y_m"]), 1.0 * S, col, "none")
    text(X(n["x_m"]), Y(n["y_m"]) + 26 * S, f"{name}  ({n['height_m']} m)", 13, col, "middle", "bold", plate=True)

# ---- elevation profile along the A-B axis (same x scale as the plan) ------
prof = geo["axis_profile"]["segments"]
py1 = Y(FH) + 46                        # panel top
base = py1 + 118                        # 0 m datum
vs = 110.0 / 16.0                       # px per vertical metre
text(X(0), py1 + 2, "ELEVATION PROFILE ALONG THE A-B AXIS  (x scale matches the plan above)", 15, TXT, "start", "bold")
line(X(0), base, X(FW), base, "#6d8397", 1.4)
for seg in prof:
    x0p, x1p = X(seg["x0_m"]), X(seg["x1_m"])
    h = seg["height_m"]
    if h is None:
        polypix([[[x0p + 1, base - 26], [x1p - 1, base - 26], [x1p - 1, base - 1], [x0p + 1, base - 1]]],
                "#243140", "#41566b", 1.0)
        text((x0p + x1p) / 2, base - 34, "wall", 11, SUB, "middle")
        continue
    slab = 0 if h else 14          # give the 0 m pit a legible datum slab
    y_top = base - h * vs - slab
    fill = ZONE_FILL["H16" if h == 16 else ("H8" if h == 8 else "H0")]
    polypix([[[x0p + 1, y_top], [x1p - 1, y_top], [x1p - 1, base - 1], [x0p + 1, base - 1]]],
            fill, "#ffffff", 1.2)
    if seg["x1_m"] - seg["x0_m"] > 6:
        text((x0p + x1p) / 2, y_top + 22,
             f"{h} m   -   {seg['x1_m'] - seg['x0_m']:.0f} m wide",
             14, "#0d141b" if h == 16 else TXT, "middle", "bold")
for tick in range(0, int(FW) + 1, 20):
    line(X(tick), base, X(tick), base + 6, "#6d8397", 1.2)
    text(X(tick), base + 20, f"{tick} m", 11, SUB, "middle")

# ---- header / legend ------------------------------------------------------
text(X(0), 34, "GREEN CANYON  -  BLOCKOUT LAYOUT (generated from measured geometry)", 21, TXT, "start", "bold")
text(X(0), 56, f"{FW:.0f} x {FH:.0f} m playable span  |  heights 0 / 8 / 16 m  |  "
               f"5 capture beacons  |  2 centre gates  |  bilateral about x = {cl:.0f} m", 13, SUB)
ly = VH - 58
items = [(ZONE_FILL["H16"], ZONE_STK["H16"], "16 m plateaus"),
         (ZONE_FILL["H8"], ZONE_STK["H8"], "8 m terraces"),
         (ZONE_FILL["H0"], ZONE_STK["H0"], "0 m centre pit"),
         (BEACON + "55", BEACON, f"beacon + {CAP_R:.0f} m capture ring (design)"),
         ("none", GATE, "gate slot"),
         ("none", SPAWNA, "spawn pads (8/team)")]
for i, (f_, st_, lab) in enumerate(items):
    bx = X(0) + i * 300
    shapes.insert(0, ("rect", bx, ly, 24, 14, f_, st_))
    text(bx + 32, ly + 12, lab, 13, TXT)
# scale bar (header row, right side)
sbx, sby = X(FW) - 270, 40
shapes.insert(0, ("rect", sbx, sby, 10 * S, 8, "#cfe0ef", "none"))
shapes.insert(0, ("rect", sbx + 10 * S, sby, 10 * S, 8, "#8fa3b5", "none"))
text(sbx, sby - 10, "scale  0 - 10 - 20 m", 12, SUB)

# --------------------------------------------------------------------------- render
def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{VW:.0f}" height="{VH:.0f}" '
       f'viewBox="0 0 {VW:.0f} {VH:.0f}"><rect width="100%" height="100%" fill="{BG}"/>']
def pts_str(pts):
    return " ".join(f"{X(x):.1f},{Y(y):.1f}" for x, y in pts)
for sh in shapes:
    if sh[0] == "rect":
        _, x, y, w, h, f, st = sh
        svg.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w}" height="{h}" '
                   f'fill="{f}" stroke="{st}" stroke-width="1.4"/>')
    elif sh[0] == "polypix":
        _, rings, f, st, sw = sh
        d = " ".join("M " + " ".join(f"{px:.1f},{py:.1f}" for px, py in r) + " Z" for r in rings)
        svg.append(f'<path d="{d}" fill="{f}" stroke="{st}" stroke-width="{sw}" stroke-linejoin="round"/>')
    elif sh[0] == "poly":
        _, rings, f, st, sw = sh
        d = " ".join("M " + pts_str(r) + " Z" for r in rings)
        svg.append(f'<path d="{d}" fill="{f}" fill-rule="evenodd" stroke="{st}" stroke-width="{sw}" stroke-linejoin="round"/>')
    elif sh[0] == "circle":
        _, cx, cy, r, f, st, sw, dash = sh
        da = f' stroke-dasharray="{dash}"' if dash else ""
        svg.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{f}" '
                   f'stroke="{st}" stroke-width="{sw}"{da}/>')
    elif sh[0] == "line":
        _, x0, y0, x1, y1, st, sw, dash = sh
        da = f' stroke-dasharray="{dash}"' if dash else ""
        svg.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" '
                   f'stroke="{st}" stroke-width="{sw}"{da}/>')
    elif sh[0] in ("text", "label"):
        _, x, y, s, size, fill, anchor, weight, op, *rest = sh
        plate = bool(rest and rest[0])
        if plate:
            wch = len(s) * size * 0.60
            x0p = x - wch / 2 if anchor == "middle" else x - 4
            svg.append(f'<rect x="{x0p - 5:.1f}" y="{y - size:.1f}" width="{wch + 10:.1f}" '
                       f'height="{size + 8:.1f}" fill="{BG}" fill-opacity="0.82" rx="3"/>')
        svg.append(f'<text x="{x:.1f}" y="{y:.1f}" font-family="DejaVu Sans, Arial, sans-serif" '
                   f'font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
                   f'font-weight="{weight}" opacity="{op}">{esc(s)}</text>')
svg.append("</svg>")
open(f"{OUT}/svg/green-canyon-blockout.svg", "w").write("\n".join(svg))
print("svg shapes:", len(shapes), f"{VW:.0f}x{VH:.0f}")

# ---- PNG from the same shape list, drawn independently -------------------
try:
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new("RGB", (int(VW), int(VH)), BG)
    d = ImageDraw.Draw(img)

    def col(c):
        """PIL has no #rrggbbaa; composite it over the background instead."""
        if not isinstance(c, str):
            return c
        if c == "none":
            return None
        if len(c) != 9:
            return c
        r, g, b = int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16)
        al = int(c[7:9], 16) / 255.0
        bg = [int(BG[i:i + 2], 16) for i in (1, 3, 5)]
        return tuple(int(round(v * al + bv * (1 - al))) for v, bv in zip((r, g, b), bg))
    F = {s: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", s)
         for s in (11, 12, 13, 16, 21)}
    FB = {s: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", s)
          for s in (11, 12, 13, 16, 21)}

    def draw_shape(sh):
        if sh[0] == "rect":
            _, x, y, w, h, f, st = sh
            if f != "none":
                d.rectangle([x, y, x + w, y + h], fill=col(f))
            if st != "none":
                d.rectangle([x, y, x + w, y + h], outline=col(st), width=2)
        elif sh[0] == "polypix":
            _, rings, f, st, sw = sh
            d.polygon([(px, py) for px, py in rings[0]], fill=col(f))
            if st != "none":
                for r in rings:
                    dd = list(r) + [r[0]]
                    d.line(dd, fill=col(st), width=max(1, int(sw)))
        elif sh[0] == "poly":
            _, rings, f, st, sw = sh
            d.polygon([(X(x), Y(y)) for x, y in rings[0]], fill=col(f))
            for r in rings[1:]:
                d.polygon([(X(x), Y(y)) for x, y in r], fill=BG)
            if st != "none":
                for r in rings:
                    dd = [(X(x), Y(y)) for x, y in r] + [(X(r[0][0]), Y(r[0][1]))]
                    d.line(dd, fill=col(st), width=max(1, int(sw)))
        elif sh[0] == "circle":
            _, cx, cy, r, f, st, sw, dash = sh
            if f != "none":
                d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col(f))
            if st != "none":
                if dash:
                    import math
                    a = 0.0
                    while a < 2 * math.pi:
                        b = min(a + math.radians(12), 2 * math.pi)
                        d.arc([cx - r, cy - r, cx + r, cy + r], math.degrees(a), math.degrees(b), fill=col(st), width=max(1, int(sw)))
                        a = b + math.radians(10)
                else:
                    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col(st), width=max(1, int(sw)))
        elif sh[0] == "line":
            _, x0, y0, x1, y1, st, sw, dash = sh
            if dash:
                import math
                L = math.hypot(x1 - x0, y1 - y0)
                ux, uy = (x1 - x0) / L, (y1 - y0) / L
                on, off = 7, 7
                t = 0
                while t < L:
                    t2 = min(t + on, L)
                    d.line([x0 + ux * t, y0 + uy * t, x0 + ux * t2, y0 + uy * t2], fill=col(st), width=max(1, int(sw)))
                    t = t2 + off
            else:
                d.line([x0, y0, x1, y1], fill=col(st), width=max(1, int(sw)))
        elif sh[0] in ("text", "label"):
            _, x, y, s, size, fill, anchor, weight, op, *rest = sh
            fnt = (FB if weight == "bold" else F).get(size, F[13])
            if rest and rest[0]:
                wch = d.textlength(s, font=fnt)
                x0p = x - wch / 2 if anchor == "middle" else x - 4
                d.rectangle([x0p - 5, y - size - 4, x0p + wch + 5, y + 4], fill="#0b1116cc")
            wpx = d.textlength(s, font=fnt)
            ox = x - wpx / 2 if anchor == "middle" else x
            d.text((ox, y - size), s, font=fnt, fill=col(fill))

    for sh in shapes:
        draw_shape(sh)
    img.save(f"{OUT}/png/green-canyon-blockout.png")
    print("png:", img.size)
except Exception as e:
    print("PNG render skipped:", type(e).__name__, e)

# ---- CSV tables -----------------------------------------------------------
with open(f"{OUT}/tables/nodes.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["id", "kind", "x_m", "y_m", "height_m", "notes"])
    for b in geo["nodes"]["beacons"]:
        w.writerow([b["id"], "beacon", b["x_m"], b["y_m"], b["height_m"],
                    f"open_fraction={b['open_fraction_60px']}"])
    for sp, col in (("spawnA", "team A"), ("spawnB", "team B")):
        n = geo["nodes"][sp]
        w.writerow([col, "spawn", n["x_m"], n["y_m"], n["height_m"],
                     f"{len(n['pads'])} pads"])
    for i, g in enumerate(geo["nodes"]["gates"]):
        w.writerow([f"gate{i+1}", "gate", g["x_m"], g["y_m"], 0, f"slot {g['size_m'][0]}x{g['size_m'][1]} m"])
with open(f"{OUT}/tables/zones.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["zone", "height_m", "lobes", "walkable_m2", "footprint_m2"])
    for k, v in geo["zones"].items():
        w.writerow([k, geo["heights_m"][k], v["lobes"], v["walkable_m2"], v["footprint_m2"]])
with open(f"{OUT}/tables/spawn-pads.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["team", "pad", "x_m", "y_m"])
    for sp, col in (("spawnA", "A"), ("spawnB", "B")):
        for i, p in enumerate(geo["nodes"][sp]["pads"]):
            w.writerow([col, i + 1, p["x_m"], p["y_m"]])
print("tables written")
