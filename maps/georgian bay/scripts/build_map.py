#!/usr/bin/env python3
"""
Georgian Bay Display Map & CAD Generator (Refined v3)
Covers: Longuissa Bay to South Bay Cove, Thirty Thousand Islands, Georgian Bay.

Refinements:
- All layers are strictly the full size of the page (163.8 mm x 228.6 mm) with matching bounding frames so they never shift in CAD/slicers.
- Satellite layer added and perfectly aligned with geographic vector geometry.
- Authentic IHO / CHS Chart No. 1 spar buoys (slanted ~20 deg right, position dot, red conical / green cylindrical).
- Beausoleil Island text rotated 180 degrees (-80.5 deg) at the narrow waist of the island.
- Roberts Island rotated 180 deg (-77.8 deg) and shifted right.
- Little Beausoleil, Webber Island, and Minnicognashene Island rotated 180 deg.
- Dropped Beausoleil Bay.
- Honey Harbour and South Bay Cove sized much smaller (~1.5mm), with South Bay Cove positioned securely inside the page margin.
- Little anchor symbols at Brown Bay, Longuissa Bay, and Bone Island anchorages.
- Title block simplified to solid opaque 'GEORGIAN BAY' & 'THIRTY THOUSAND ISLANDS'.
- More interesting, refined nautical compass rose with faceted 8-point star and degree markings.
- Crisp Canadian Shield granite islands with hairline miter stroke (no rounded blobbiness).
"""

import os
import glob
import math
import base64
import urllib.request
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import scipy.ndimage as ndi

# -------------------------------------------------------------------------
# Geographic Bounds & Projection Setup
# -------------------------------------------------------------------------
MIN_LAT = 44.8225
MAX_LAT = 44.9715
MIN_LON = -79.9140
MAX_LON = -79.7660 # Right edge directly where South Bay Cove ends, zooming map up to fit!

TARGET_WIDTH = 163.8
TARGET_HEIGHT = 228.6
MARGIN_X = 3.0
MARGIN_Y = 3.0
MAP_W = TARGET_WIDTH - 2 * MARGIN_X
MAP_H = TARGET_HEIGHT - 2 * MARGIN_Y

LAT_CENTER = (MIN_LAT + MAX_LAT) / 2.0
COS_LAT = math.cos(math.radians(LAT_CENTER))

DLON = MAX_LON - MIN_LON
DLAT = MAX_LAT - MIN_LAT

SCALE_X = MAP_W / (DLON * COS_LAT)
SCALE_Y = MAP_H / DLAT
ISO_SCALE = min(SCALE_X, SCALE_Y)
OFFSET_X = MARGIN_X + (MAP_W - (DLON * COS_LAT * ISO_SCALE)) / 2.0
OFFSET_Y = MARGIN_Y + (MAP_H - (DLAT * ISO_SCALE)) / 2.0

# Exact geographic bounding rectangle of the satellite / map content
SAT_X = OFFSET_X
SAT_Y = OFFSET_Y
SAT_W = DLON * COS_LAT * ISO_SCALE
SAT_H = DLAT * ISO_SCALE

def geo_to_svg(lon, lat):
    """Project lon/lat to SVG coordinates in millimeters."""
    x = OFFSET_X + (lon - MIN_LON) * COS_LAT * ISO_SCALE
    y = OFFSET_Y + (MAX_LAT - lat) * ISO_SCALE
    return (x, y)

def simplify_points(pts, tolerance=0.005):
    """Ramer-Douglas-Peucker line simplification in SVG mm units."""
    if len(pts) <= 2:
        return pts
    first, last = pts[0], pts[-1]
    dx = last[0] - first[0]
    dy = last[1] - first[1]
    denom = math.hypot(dx, dy)
    
    max_d = 0.0
    index = 0
    for i in range(1, len(pts) - 1):
        if denom == 0:
            d = math.hypot(pts[i][0] - first[0], pts[i][1] - first[1])
        else:
            d = abs(dy * pts[i][0] - dx * pts[i][1] + last[0] * first[1] - last[1] * first[0]) / denom
        if d > max_d:
            max_d = d
            index = i
            
    if max_d > tolerance:
        left = simplify_points(pts[:index + 1], tolerance)
        right = simplify_points(pts[index:], tolerance)
        return left[:-1] + right
    else:
        return [first, last]

def get_polygon_orientation(pts):
    """Compute centroid and principal major axis angle (in degrees) in SVG coords."""
    n = len(pts)
    if n < 3:
        return (pts[0][0], pts[0][1], 0.0)
    cx = sum(p[0] for p in pts) / n
    cy = sum(p[1] for p in pts) / n
    mxx = sum((p[0] - cx)**2 for p in pts) / n
    myy = sum((p[1] - cy)**2 for p in pts) / n
    mxy = sum((p[0] - cx)*(p[1] - cy) for p in pts) / n
    theta = 0.5 * math.atan2(2 * mxy, mxx - myy)
    deg = math.degrees(theta)
    
    while deg > 90: deg -= 180
    while deg < -90: deg += 180
    if deg > 65: deg -= 180
    elif deg < -65: deg += 180
    return cx, cy, deg

# -------------------------------------------------------------------------
# Load OSM Vector Data
# -------------------------------------------------------------------------
print("Loading OpenStreetMap data...")
nodes = {}
ways = {}
relations = {}

for f in sorted(glob.glob('data/osm/*.osm')):
    tree = ET.parse(f)
    for el in tree.getroot():
        if el.tag == 'node':
            nodes[el.attrib['id']] = (float(el.attrib['lat']), float(el.attrib['lon']))
        elif el.tag == 'way':
            tags = {t.attrib['k']: t.attrib['v'] for t in el.findall('tag')}
            nds = [nd.attrib['ref'] for nd in el.findall('nd')]
            ways[el.attrib['id']] = {'tags': tags, 'nds': nds}
        elif el.tag == 'relation':
            tags = {t.attrib['k']: t.attrib['v'] for t in el.findall('tag')}
            members = [m.attrib for m in el.findall('member')]
            relations[el.attrib['id']] = {'tags': tags, 'members': members}

# -------------------------------------------------------------------------
# Extract Islands & Shorelines (High detail, crisp granite vertices)
# -------------------------------------------------------------------------
inner_members = set()
if '1205151' in relations:
    for m in relations['1205151']['members']:
        if m['role'] == 'inner':
            inner_members.add(m['ref'])

all_islands = []

# 1. Beausoleil Island (Ways 118832495 & 1571158879)
w1, w2 = ways.get('118832495'), ways.get('1571158879')
if w1 and w2:
    raw_nodes = [nodes[n] for n in w1['nds'] if n in nodes] + [nodes[n] for n in w2['nds'][1:] if n in nodes]
    svg_pts = [geo_to_svg(p[1], p[0]) for p in raw_nodes]
    b_sim = simplify_points(svg_pts, 0.005)
    all_islands.append({
        'id': 'beausoleil_island',
        'name': 'Beausoleil Island',
        'pts': b_sim
    })

# Inland lakes on Beausoleil (Fairy Lake & Goblin Lake) to carve as water
beausoleil_inland_lakes = []
for wid in ['118832805', '1636182']:
    w = ways.get(wid)
    if w:
        raw_nodes = [nodes[n] for n in w['nds'] if n in nodes]
        if raw_nodes and raw_nodes[0] == raw_nodes[-1]:
            s_pts = [geo_to_svg(p[1], p[0]) for p in raw_nodes]
            beausoleil_inland_lakes.append(simplify_points(s_pts, 0.005))

# 2. Bone Island
w_bone = ways.get('118780853')
if w_bone:
    raw_nodes = [nodes[n] for n in w_bone['nds'] if n in nodes]
    svg_pts = [geo_to_svg(p[1], p[0]) for p in raw_nodes]
    all_islands.append({
        'id': 'bone_island',
        'name': 'Bone Island',
        'pts': simplify_points(svg_pts, 0.005)
    })

# 3. All other islands
exclude_ids = {'118832495', '1571158879', '118780853'}
for wid, w in ways.items():
    if wid in exclude_ids:
        continue
    if wid in inner_members or w['tags'].get('place') in ('island', 'islet'):
        nds = w['nds']
        if len(nds) >= 3 and nds[0] == nds[-1]:
            raw_nodes = [nodes[n] for n in nds if n in nodes]
            if len(raw_nodes) < 3:
                continue
            lats = [p[0] for p in raw_nodes]
            lons = [p[1] for p in raw_nodes]
            if max(lats) < MIN_LAT or min(lats) > MAX_LAT or max(lons) < MIN_LON or min(lons) > MAX_LON:
                continue
            s_pts = [geo_to_svg(p[1], p[0]) for p in raw_nodes]
            sim = simplify_points(s_pts, 0.005)
            if len(sim) >= 3:
                all_islands.append({
                    'id': wid,
                    'name': w['tags'].get('name', ''),
                    'pts': sim
                })

print(f"Total crisp islands loaded: {len(all_islands)}")

# -------------------------------------------------------------------------
# Clean Mainland Shoreline & Polygon (Strictly Clipped)
# -------------------------------------------------------------------------
outer_refs = ['118891587', '118854934', '118811515', '118811612', '118778440', 
              '118778442', '118748660', '118729396', '1350706397', '1350706396']
shore_raw = []
for ref in outer_refs:
    if ref in ways:
        w_nds = ways[ref]['nds']
        pts_this = [nodes[n] for n in w_nds if n in nodes]
        if not pts_this: continue
        if not shore_raw:
            shore_raw.extend(pts_this)
        else:
            if pts_this[0] == shore_raw[-1]:
                shore_raw.extend(pts_this[1:])
            elif pts_this[-1] == shore_raw[-1]:
                shore_raw.extend(pts_this[-2::-1])
            else:
                shore_raw.extend(pts_this)

xmin = MARGIN_X
xmax = TARGET_WIDTH - MARGIN_X
ymin = MARGIN_Y
ymax = TARGET_HEIGHT - MARGIN_Y

main_shore = []
start_idx = 1400

# Interpolate entry at left border (x=xmin)
for i in range(1300, 1500):
    p1 = geo_to_svg(shore_raw[i][1], shore_raw[i][0])
    p2 = geo_to_svg(shore_raw[i+1][1], shore_raw[i+1][0])
    if p1[0] < xmin and p2[0] >= xmin:
        t = (xmin - p1[0]) / (p2[0] - p1[0])
        y_int = p1[1] + t * (p2[1] - p1[1])
        main_shore.append((xmin, max(ymin, min(ymax, y_int))))
        start_idx = i + 1
        break

# Trace shoreline down to bottom border (y=ymax)
for i in range(start_idx, len(shore_raw)-1):
    p1 = geo_to_svg(shore_raw[i][1], shore_raw[i][0])
    p2 = geo_to_svg(shore_raw[i+1][1], shore_raw[i+1][0])
    if p1[1] <= ymax and p2[1] > ymax:
        t = (ymax - p1[1]) / (p2[1] - p1[1])
        x_int = p1[0] + t * (p2[0] - p1[0])
        main_shore.append((max(xmin, min(xmax, p1[0])), max(ymin, min(ymax, p1[1]))))
        main_shore.append((max(xmin, min(xmax, x_int)), ymax))
        break
    main_shore.append((max(xmin, min(xmax, p1[0])), max(ymin, min(ymax, p1[1]))))

main_shore_sim = simplify_points(main_shore, 0.005)
mainland_poly = main_shore_sim + [(xmax, ymax), (xmax, ymin), (xmin, ymin)]

# -------------------------------------------------------------------------
# Generate Aligned & Feathered Satellite Imagery
# -------------------------------------------------------------------------
def generate_feathered_satellite(raw_image_path='satellite_raw_2960.png', output_path='satellite_georgian_bay.png'):
    print("Generating perfectly aligned & feathered satellite imagery...")
    if not os.path.exists(raw_image_path):
        url = (
            f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/export?"
            f"bbox={MIN_LON:.4f},{MIN_LAT:.4f},{MAX_LON:.4f},{MAX_LAT:.4f}&bboxSR=4326&imageSR=4326&"
            f"size=2960,2980&format=png&f=image"
        )
        print(f"Downloading satellite imagery from Esri World Imagery ({url})...")
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as resp, open(raw_image_path, 'wb') as out_f:
            out_f.write(resp.read())
        print(f"Saved raw satellite image: {raw_image_path}")

    raw_img = Image.open(raw_image_path).convert('RGB')
    w_px, h_px = raw_img.size

    # Build binary land mask matching the vector polygons exactly
    mask = Image.new('L', (w_px, h_px), 0)
    draw = ImageDraw.Draw(mask)

    def to_px(pts):
        return [((p[0] - SAT_X) / SAT_W * w_px, (p[1] - SAT_Y) / SAT_H * h_px) for p in pts]

    # Draw mainland
    draw.polygon(to_px(mainland_poly), fill=255)

    # Draw all 400+ islands
    for isl in all_islands:
        draw.polygon(to_px(isl['pts']), fill=255)

    # Carve out inland lakes (Fairy Lake, Goblin Lake)
    for lake in beausoleil_inland_lakes:
        draw.polygon(to_px(lake), fill=0)

    land_mask = np.array(mask) > 0

    # Distance transform into water for C1 continuous cosine smoothstep feathering
    dist_out = ndi.distance_transform_edt(~land_mask)
    feather_radius = 5.0  # pixels (~0.27 mm in physical scale)

    t = np.clip(dist_out / feather_radius, 0.0, 1.0)
    smooth_fade = 0.5 * (1.0 + np.cos(math.pi * t))

    # All land pixels stay 100% solid; shoreline gently feathers into water
    alpha_channel = np.where(land_mask, 1.0, smooth_fade)
    alpha_u8 = (alpha_channel * 255).astype(np.uint8)

    rgba = raw_img.convert('RGBA')
    rgba.putalpha(Image.fromarray(alpha_u8))
    rgba.save(output_path, format='PNG')
    print(f"Saved aligned & feathered satellite image: {output_path} ({w_px}x{h_px})")

generate_feathered_satellite()

# -------------------------------------------------------------------------
# Authentic IHO / CHS Spar Buoys (Tilted 20° Right, Base Dot, Small)
# -------------------------------------------------------------------------
buoys_data = [
    # Starboard (Red) Spars
    {'type': 'red', 'pos': (-79.8235, 44.8580)},
    {'type': 'red', 'pos': (-79.8240, 44.8620)},
    {'type': 'red', 'pos': (-79.8222, 44.8655)},
    {'type': 'red', 'pos': (-79.8800, 44.9220)}, # Penetang Rock
    {'type': 'red', 'pos': (-79.8850, 44.9340)},
    {'type': 'red', 'pos': (-79.8860, 44.9410)},
    {'type': 'red', 'pos': (-79.8895, 44.9610)}, # Longuissa Point
    {'type': 'red', 'pos': (-79.7900, 44.8730)}, # South Bay
    {'type': 'red', 'pos': (-79.8100, 44.8730)}, # South Bay
    
    # Port (Green) Spars
    {'type': 'green', 'pos': (-79.8245, 44.8690)}, # C75 Turning Island
    {'type': 'green', 'pos': (-79.8185, 44.8740)}, # Inner Channel
    {'type': 'green', 'pos': (-79.8185, 44.8780)}, # Inner Channel North
    {'type': 'green', 'pos': (-79.8250, 44.8960)}, # North of Minnehaha Pt
    {'type': 'green', 'pos': (-79.8835, 44.9275)}, # Musquash Channel entry
    {'type': 'green', 'pos': (-79.8860, 44.9460)}, # Brown Bay approach
    {'type': 'green', 'pos': (-79.7850, 44.8730)}, # South Bay Cove approach
    {'type': 'green', 'pos': (-79.8000, 44.8740)}, # South Bay
]

for b in buoys_data:
    b['svg_pos'] = geo_to_svg(b['pos'][0], b['pos'][1])

# -------------------------------------------------------------------------
# Anchorages with Subtle Anchor Icons
# -------------------------------------------------------------------------
anchor_spots = [
    {'name': 'Brown Bay', 'pos': (-79.8891, 44.9485)},
    {'name': 'Longuissa Bay', 'pos': (-79.8895, 44.9635)},
    {'name': 'Bone Island Basin', 'pos': (-79.8680, 44.9390)},
]

for a in anchor_spots:
    a['svg_pos'] = geo_to_svg(a['pos'][0], a['pos'][1])

# -------------------------------------------------------------------------
# Island Orientations & Labels
# -------------------------------------------------------------------------
island_map = {isl['id']: isl for isl in all_islands}

# Updated configurations with exact user rotation requests
final_island_labels = [
    # Beausoleil Island: rotated 180 degrees (+99.5 deg), dropped down to narrow waist (Y approx 168mm)
    {'name': 'BEAUSOLEIL ISLAND', 'x': 49.5, 'y': 168.0, 'angle': 99.5, 'size': 3.0},
    # Roberts Island: shifted right, rotated 180 deg (-77.8 deg)
    {'name': 'ROBERTS ISLAND', 'x': 86.0, 'y': 168.0, 'angle': -77.8, 'size': 2.1},
    # Little Beausoleil: rotated 180 deg
    {'name': 'LITTLE BEAUSOLEIL I.', 'id': '118832581', 'angle_override': 80.3, 'size': 1.6},
    # Webber Island: rotated 180 deg
    {'name': 'WEBBER ISLAND', 'id': '118778024', 'angle_override': 84.7, 'size': 1.6},
    # Minnicognashene Island: rotated 180 deg
    {'name': 'MINNICOGNASHENE I.', 'id': '118832737', 'angle_override': -69.3, 'size': 1.5},
    # Bone Island (major axis)
    {'name': 'BONE ISLAND', 'id': 'bone_island', 'size': 2.8},
    # Tomahawk Island
    {'name': 'TOMAHAWK ISLAND', 'id': '118777995', 'size': 1.8},
    # Deer Island
    {'name': 'DEER ISLAND', 'id': '118832716', 'size': 1.8},
    # Mermaid Island
    {'name': 'MERMAID ISLAND', 'id': '118832865', 'size': 1.6},
    # Quarry Island
    {'name': 'QUARRY ISLAND', 'id': '118744916', 'size': 1.7},
    # Governor Island
    {'name': 'GOVERNOR ISLAND', 'id': '118832658', 'size': 1.5},
    # Arthur Island
    {'name': 'ARTHUR ISLAND', 'id': '118811665', 'size': 1.5},
    # Picnic Island
    {'name': 'PICNIC ISLAND', 'id': '118744790', 'size': 1.4},
    # Royal Island
    {'name': 'ROYAL ISLAND', 'id': '118744848', 'size': 1.4},
    # Present Island
    {'name': 'PRESENT ISLAND', 'pos': (-79.8510, 44.8230), 'angle': 15.0, 'size': 1.7},
    # Burnt Island
    {'name': 'BURNT ISLAND', 'id': '118832697', 'size': 1.7},
]

computed_labels = []
for cfg in final_island_labels:
    if 'x' in cfg and 'y' in cfg:
        computed_labels.append(cfg)
    elif 'id' in cfg and cfg['id'] in island_map:
        isl = island_map[cfg['id']]
        cx, cy, deg = get_polygon_orientation(isl['pts'])
        angle = cfg.get('angle_override', deg)
        computed_labels.append({
            'name': cfg['name'],
            'x': cx,
            'y': cy,
            'angle': angle,
            'size': cfg['size']
        })
    elif 'pos' in cfg:
        x, y = geo_to_svg(cfg['pos'][0], cfg['pos'][1])
        computed_labels.append({
            'name': cfg['name'],
            'x': x,
            'y': y,
            'angle': cfg.get('angle', 0.0),
            'size': cfg['size']
        })

# Refined area labels: Honey Harbour & South Bay Cove sized small (~1.5mm)
# South Bay Cove placed safely inside the page with text-anchor='end'
area_labels = [
    {'name': 'HONEY HARBOUR', 'pos': (-79.8116, 44.8740), 'size': 1.5, 'weight': 'bold', 'color': '#ffffff', 'align': 'start', 'offset': (2.0, 0.4)},
    {'name': 'SOUTH BAY COVE', 'pos': (-79.7680, 44.8764), 'size': 1.5, 'weight': 'bold', 'color': '#ffffff', 'align': 'end', 'offset': (-2.0, -1.0)},
    {'name': 'BROWN BAY', 'pos': (-79.8891, 44.9485), 'size': 1.4, 'weight': '600', 'color': '#a8dadc', 'align': 'end', 'offset': (-3.0, 0.4)},
    {'name': 'LONGUISSA BAY', 'pos': (-79.8895, 44.9635), 'size': 1.4, 'weight': 'bold', 'color': '#ffffff', 'align': 'start', 'offset': (3.0, 0.4)},
    {'name': 'COGNASHENE', 'pos': (-79.9050, 44.9450), 'size': 1.7, 'weight': '600', 'color': '#e0e1dd', 'align': 'middle', 'offset': (0, 0)},
]

for al in area_labels:
    al['svg_pos'] = geo_to_svg(al['pos'][0], al['pos'][1])

# -------------------------------------------------------------------------
# SVG Rendering Functions
# -------------------------------------------------------------------------
def points_to_path(pts, closed=True):
    if not pts: return ""
    d = [f"M {pts[0][0]:.3f} {pts[0][1]:.3f}"]
    for p in pts[1:]:
        d.append(f"L {p[0]:.3f} {p[1]:.3f}")
    if closed:
        d.append("Z")
    return " ".join(d)

def chs_spar_buoy_svg(x, y, buoy_type):
    """
    Official IHO / CHS Chart No. 1 Spar Buoy Symbol:
    - Base circle at exact charted water position
    - Slender mast tilted 20 degrees to the right
    - Conical top for Starboard Red, cylindrical top for Port Green
    - Scaled to approx 1.4 mm height
    """
    col = '#e63946' if buoy_type == 'red' else '#06d6a0'
    if buoy_type == 'red':
        return (f'<g transform="translate({x:.3f}, {y:.3f})">'
                f'<circle cx="0" cy="0" r="0.22" fill="{col}" stroke="#111" stroke-width="0.08"/>'
                f'<g transform="rotate(20, 0, 0)">'
                f'<line x1="0" y1="0" x2="0" y2="-0.45" stroke="#111" stroke-width="0.14"/>'
                f'<polygon points="0,-1.35 0.28,-0.45 -0.28,-0.45" fill="{col}" stroke="#111" stroke-width="0.06"/>'
                f'</g></g>')
    else:
        return (f'<g transform="translate({x:.3f}, {y:.3f})">'
                f'<circle cx="0" cy="0" r="0.22" fill="{col}" stroke="#111" stroke-width="0.08"/>'
                f'<g transform="rotate(20, 0, 0)">'
                f'<line x1="0" y1="0" x2="0" y2="-0.45" stroke="#111" stroke-width="0.14"/>'
                f'<rect x="-0.22" y="-1.35" width="0.44" height="0.9" fill="{col}" stroke="#111" stroke-width="0.06"/>'
                f'</g></g>')

def subtle_anchor_svg(x, y, scale=0.3):
    """Clean, subtle nautical anchor symbol for anchorages."""
    return f"""<g transform="translate({x:.3f}, {y:.3f}) scale({scale})">
        <circle cx="0" cy="-3.6" r="1.0" fill="none" stroke="#ffd166" stroke-width="0.7"/>
        <line x1="-2.4" y1="-2.4" x2="2.4" y2="-2.4" stroke="#ffd166" stroke-width="0.8" stroke-linecap="round"/>
        <line x1="0" y1="-2.8" x2="0" y2="3.0" stroke="#ffd166" stroke-width="0.8" stroke-linecap="round"/>
        <path d="M -3.2 0.8 C -2.8 3.4 2.8 3.4 3.2 0.8" fill="none" stroke="#ffd166" stroke-width="0.8" stroke-linecap="round"/>
        <polygon points="-3.7,0.4 -2.5,1.0 -3.1,1.6" fill="#ffd166"/>
        <polygon points="3.7,0.4 2.5,1.0 3.1,1.6" fill="#ffd166"/>
    </g>"""

def refined_nautical_compass_svg(cx, cy, r=9.8):
    """
    Tasteful, refined 16-facet nautical compass rose:
    - Dual concentric rings with degree tick marks every 5, 15, and 30 degrees
    - Faceted 8-point nautical star with 16 light/shadow relief facets
    - Distinctive North point in Crimson (#d90429) & Gold (#ffd166) with finial arrowhead
    - Multi-stage polished brass center boss
    - Classic serif cardinal 'N' and clear secondary cardinals
    """
    svg = [f'<g transform="translate({cx:.2f}, {cy:.2f})" id="compass_rose">']
    # Outer background disc & rings
    svg.append(f'  <circle cx="0" cy="0" r="{r:.2f}" fill="#09131d" fill-opacity="0.96" stroke="#ffd166" stroke-width="0.45"/>')
    svg.append(f'  <circle cx="0" cy="0" r="{r*0.91:.2f}" fill="none" stroke="#2a3f55" stroke-width="0.15"/>')
    svg.append(f'  <circle cx="0" cy="0" r="{r*0.80:.2f}" fill="none" stroke="#ffd166" stroke-width="0.22"/>')
    
    # Degree tick marks around the outer bezel
    for deg in range(0, 360, 5):
        rad = math.radians(deg)
        if deg % 90 == 0:
            r_in = r * 0.76
            sw = '0.32'
            col = '#ffd166'
        elif deg % 30 == 0:
            r_in = r * 0.80
            sw = '0.20'
            col = '#ffd166'
        elif deg % 15 == 0:
            r_in = r * 0.84
            sw = '0.14'
            col = '#778da9'
        else:
            r_in = r * 0.87
            sw = '0.09'
            col = '#415a77'
        x1 = r_in * math.sin(rad)
        y1 = -r_in * math.cos(rad)
        x2 = r * 0.91 * math.sin(rad)
        y2 = -r * 0.91 * math.cos(rad)
        svg.append(f'  <line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{col}" stroke-width="{sw}"/>')
    
    # Faceted 8-point star geometry
    r_card = r * 0.78 # Main cardinal radius
    r_ord  = r * 0.52 # Ordinal radius
    r_in   = r * 0.20 # Inner valley radius
    
    # Ordinal Points (NE, SE, SW, NW) - 2-tone light and dark facets
    sin45 = 0.7071
    cos45 = 0.7071
    
    # NE (angle 45 deg)
    svg.append(f'  <polygon points="0,0 {r_ord*sin45:.2f},{-r_ord*cos45:.2f} {r_in*0.35:.2f},{-r_in*0.93:.2f}" fill="#3b5066"/>')
    svg.append(f'  <polygon points="0,0 {r_ord*sin45:.2f},{-r_ord*cos45:.2f} {r_in*0.93:.2f},{-r_in*0.35:.2f}" fill="#1b2838"/>')
    # SE (angle 135 deg)
    svg.append(f'  <polygon points="0,0 {r_ord*sin45:.2f},{r_ord*cos45:.2f} {r_in*0.93:.2f},{r_in*0.35:.2f}" fill="#3b5066"/>')
    svg.append(f'  <polygon points="0,0 {r_ord*sin45:.2f},{r_ord*cos45:.2f} {r_in*0.35:.2f},{r_in*0.93:.2f}" fill="#1b2838"/>')
    # SW (angle 225 deg)
    svg.append(f'  <polygon points="0,0 {-r_ord*sin45:.2f},{r_ord*cos45:.2f} {-r_in*0.35:.2f},{r_in*0.93:.2f}" fill="#3b5066"/>')
    svg.append(f'  <polygon points="0,0 {-r_ord*sin45:.2f},{r_ord*cos45:.2f} {-r_in*0.93:.2f},{r_in*0.35:.2f}" fill="#1b2838"/>')
    # NW (angle 315 deg)
    svg.append(f'  <polygon points="0,0 {-r_ord*sin45:.2f},{-r_ord*cos45:.2f} {-r_in*0.93:.2f},{-r_in*0.35:.2f}" fill="#3b5066"/>')
    svg.append(f'  <polygon points="0,0 {-r_ord*sin45:.2f},{-r_ord*cos45:.2f} {-r_in*0.35:.2f},{-r_in*0.93:.2f}" fill="#1b2838"/>')
    
    # Cardinal East (facing +X)
    svg.append(f'  <polygon points="0,0 {r_card*0.90:.2f},0 {r_in:.2f},{-r_in*0.38:.2f}" fill="#e0e1dd"/>')
    svg.append(f'  <polygon points="0,0 {r_card*0.90:.2f},0 {r_in:.2f},{r_in*0.38:.2f}" fill="#3b5066"/>')
    
    # Cardinal West (facing -X)
    svg.append(f'  <polygon points="0,0 {-r_card*0.90:.2f},0 {-r_in:.2f},{r_in*0.38:.2f}" fill="#e0e1dd"/>')
    svg.append(f'  <polygon points="0,0 {-r_card*0.90:.2f},0 {-r_in:.2f},{-r_in*0.38:.2f}" fill="#3b5066"/>')
    
    # Cardinal South (facing +Y)
    svg.append(f'  <polygon points="0,0 0,{r_card*0.90:.2f} {-r_in*0.38:.2f},{r_in:.2f}" fill="#e0e1dd"/>')
    svg.append(f'  <polygon points="0,0 0,{r_card*0.90:.2f} {r_in*0.38:.2f},{r_in:.2f}" fill="#3b5066"/>')
    
    # Cardinal North (facing -Y) - Vivid Crimson and Polished Gold
    svg.append(f'  <polygon points="0,0 0,{-r_card:.2f} {-r_in*0.38:.2f},{-r_in:.2f}" fill="#ffd166"/>')
    svg.append(f'  <polygon points="0,0 0,{-r_card:.2f} {r_in*0.38:.2f},{-r_in:.2f}" fill="#d90429"/>')
    # North Arrowhead Finial / Spearhead accent
    svg.append(f'  <polygon points="0,{-r_card*1.08:.2f} {-0.7:.2f},{-r_card*0.82:.2f} 0,{-r_card*0.88:.2f}" fill="#ffd166"/>')
    svg.append(f'  <polygon points="0,{-r_card*1.08:.2f} {0.7:.2f},{-r_card*0.82:.2f} 0,{-r_card*0.88:.2f}" fill="#d90429"/>')
    
    # Center multi-stage brass hub
    svg.append('  <circle cx="0" cy="0" r="1.30" fill="#ffd166" stroke="#09131d" stroke-width="0.25"/>')
    svg.append('  <circle cx="0" cy="0" r="0.70" fill="#b38f38" stroke="#09131d" stroke-width="0.15"/>')
    svg.append('  <circle cx="0" cy="0" r="0.30" fill="#09131d"/>')
    
    # Cardinal Lettering (Serif & clean)
    svg.append(f'  <text x="0" y="{-r*1.18:.2f}" fill="#ffd166" font-family="\'Cinzel\', \'Georgia\', serif" font-size="2.8" font-weight="bold" text-anchor="middle" dominant-baseline="central">N</text>')
    svg.append(f'  <text x="0" y="{r*1.15:.2f}" fill="#8da3b8" font-family="\'Helvetica Neue\', Arial, sans-serif" font-size="1.5" font-weight="600" text-anchor="middle" dominant-baseline="central">S</text>')
    svg.append(f'  <text x="{r*1.15:.2f}" y="0" fill="#8da3b8" font-family="\'Helvetica Neue\', Arial, sans-serif" font-size="1.5" font-weight="600" text-anchor="middle" dominant-baseline="central">E</text>')
    svg.append(f'  <text x="{-r*1.15:.2f}" y="0" fill="#8da3b8" font-family="\'Helvetica Neue\', Arial, sans-serif" font-size="1.5" font-weight="600" text-anchor="middle" dominant-baseline="central">W</text>')
    svg.append('</g>')
    return '\n'.join(svg)

# -------------------------------------------------------------------------
# Build Master Composite SVG
# -------------------------------------------------------------------------
print("Generating refined georgian_bay_display.svg ...")

svg_header = f"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
     xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
     width="{TARGET_WIDTH}mm" height="{TARGET_HEIGHT}mm"
     viewBox="0 0 {TARGET_WIDTH} {TARGET_HEIGHT}">
<defs>
    <clipPath id="mapClip">
        <rect x="{MARGIN_X}" y="{MARGIN_Y}" width="{MAP_W}" height="{MAP_H}"/>
    </clipPath>
</defs>

<style>
    .water-bg {{ fill: #0b1d30; }}
    .mainland {{ fill: #18232c; stroke: #263543; stroke-width: 0.15; stroke-linejoin: miter; }}
    /* Crisp, non-blobby island styling with miter joints and hairline stroke */
    .island {{ fill: #243447; stroke: #3b5066; stroke-width: 0.06; stroke-linejoin: miter; stroke-miterlimit: 4; }}
    .inland-lake {{ fill: #0b1d30; stroke: none; }}
    
    .island-label {{ font-family: 'Helvetica Neue', Arial, sans-serif; font-weight: bold; fill: #e0e1dd; letter-spacing: 0.35px; opacity: 0.90; }}
    .area-label {{ font-family: 'Helvetica Neue', Arial, sans-serif; fill: #ffffff; letter-spacing: 0.4px; }}
    .title-primary {{ font-family: 'Cinzel', 'Trajan Pro', 'Georgia', serif; font-weight: bold; fill: #ffd166; letter-spacing: 1.5px; }}
    .title-sub {{ font-family: 'Helvetica Neue', Arial, sans-serif; font-weight: 600; fill: #f1faee; letter-spacing: 1.2px; }}
</style>

<!-- WATER -->
<g inkscape:groupmode="layer" id="layer_water" inkscape:label="Water">
    <rect id="water_background" x="0" y="0" width="{TARGET_WIDTH}" height="{TARGET_HEIGHT}" class="water-bg"/>
</g>

<!-- SATELLITE -->
<g inkscape:groupmode="layer" id="layer_satellite" inkscape:label="Satellite" style="display:none;" opacity="1.0">
    <g id="satellite_clipped" clip-path="url(#mapClip)">
        <image id="satellite_image" href="satellite_georgian_bay.png" x="{SAT_X:.3f}" y="{SAT_Y:.3f}" width="{SAT_W:.3f}" height="{SAT_H:.3f}" preserveAspectRatio="none"/>
    </g>
</g>

<!-- MAINLAND -->
<g inkscape:groupmode="layer" id="layer_mainland" inkscape:label="Mainland">
    <g clip-path="url(#mapClip)">
        <path id="mainland_shore" d="{points_to_path(mainland_poly)}" class="mainland"/>
    </g>
</g>

<!-- ISLANDS -->
<g inkscape:groupmode="layer" id="layer_islands" inkscape:label="Islands">
    <g clip-path="url(#mapClip)">
"""

svg_body = []

for isl in all_islands:
    path_d = points_to_path(isl['pts'])
    svg_body.append(f'    <path id="{isl["id"]}" d="{path_d}" class="island"/>')

for i, l_pts in enumerate(beausoleil_inland_lakes):
    svg_body.append(f'    <path id="beausoleil_lake_{i}" d="{points_to_path(l_pts)}" class="inland-lake"/>')

svg_body.append('</g>\n</g>\n')

# 4. CHS / IHO SPAR BUOYS (Tilted right ~20 deg)
svg_body.append("""<!-- BUOYS -->
<g inkscape:groupmode="layer" id="layer_buoys" inkscape:label="Buoys">""")
for b in buoys_data:
    bx, by = b['svg_pos']
    svg_body.append(f'    {chs_spar_buoy_svg(bx, by, b["type"])}')
svg_body.append('</g>\n')

# 5. SUBTLE ANCHORAGE ANCHORS
svg_body.append("""<!-- ANCHORAGES -->
<g inkscape:groupmode="layer" id="layer_anchorages" inkscape:label="Anchorages">""")
for a in anchor_spots:
    ax, ay = a['svg_pos']
    svg_body.append(f'    {subtle_anchor_svg(ax, ay, scale=0.32)}')
svg_body.append('</g>\n')

# 6. AXIS-ALIGNED ISLAND LABELS
svg_body.append("""<!-- ISLAND LABELS -->
<g inkscape:groupmode="layer" id="layer_island_labels" inkscape:label="Island Labels">""")
for lbl in computed_labels:
    deg = lbl['angle']
    svg_body.append(f'    <text transform="translate({lbl["x"]:.2f}, {lbl["y"]:.2f}) rotate({deg:.1f})" '
                    f'class="island-label" font-size="{lbl["size"]}" text-anchor="middle" dominant-baseline="central">{lbl["name"]}</text>')
svg_body.append('</g>\n')

# 7. AREA LABELS & CARTOGRAPHY
svg_body.append(f"""<!-- CARTOGRAPHY -->
<g inkscape:groupmode="layer" id="layer_cartography" inkscape:label="Cartography">
    <rect id="frame_outer" x="{MARGIN_X}" y="{MARGIN_Y}" width="{MAP_W}" height="{MAP_H}" fill="none" stroke="#ffd166" stroke-width="0.45"/>
    <rect id="frame_inner" x="{MARGIN_X + 0.7}" y="{MARGIN_Y + 0.7}" width="{MAP_W - 1.4}" height="{MAP_H - 1.4}" fill="none" stroke="#415a77" stroke-width="0.2"/>""")

for al in area_labels:
    ax, ay = al['svg_pos']
    ox, oy = al['offset']
    svg_body.append(f'    <text x="{ax + ox:.2f}" y="{ay + oy:.2f}" class="area-label" '
                    f'font-size="{al["size"]}" font-weight="{al["weight"]}" fill="{al["color"]}" '
                    f'text-anchor="{al["align"]}" dominant-baseline="central">{al["name"]}</text>')

# Refined, more interesting nautical compass rose over mainland in top-right
svg_body.append(refined_nautical_compass_svg(TARGET_WIDTH - MARGIN_X - 16.0, MARGIN_Y + 18.0, r=9.5))

# Solid Opaque Simplified Title Block
title_x = TARGET_WIDTH / 2.0 + 8.0
title_y = TARGET_HEIGHT - MARGIN_Y - 7.5
svg_body.append(f"""
    <!-- Master Title Block (Opaque, Clean) -->
    <g transform="translate({title_x:.2f}, {title_y:.2f})" id="title_block">
        <rect x="-42" y="-6.5" width="84" height="11.5" fill="#09131d" fill-opacity="1.0" rx="1.2" stroke="#ffd166" stroke-width="0.45"/>
        <line x1="-38" y1="-5.2" x2="38" y2="-5.2" stroke="#415a77" stroke-width="0.2"/>
        <line x1="-38" y1="3.8" x2="38" y2="3.8" stroke="#415a77" stroke-width="0.2"/>
        
        <text x="0" y="-1.2" class="title-primary" font-size="4.2" text-anchor="middle" dominant-baseline="central">GEORGIAN BAY</text>
        <text x="0" y="2.0" class="title-sub" font-size="1.9" text-anchor="middle" dominant-baseline="central">THIRTY THOUSAND ISLANDS</text>
    </g>
""")

svg_body.append('</g>\n')
svg_body.append('</svg>\n')

# Write Master SVG
master_svg_content = svg_header + "\n".join(svg_body)
with open('georgian_bay_display.svg', 'w') as f:
    f.write(master_svg_content)
print(f"Saved master SVG: georgian_bay_display.svg ({len(master_svg_content)} bytes)")

# -------------------------------------------------------------------------
# Build Aligned Satellite Display Composite SVG
# -------------------------------------------------------------------------
# In the satellite edition, layer_satellite is visible on top of the deep navy water base,
# and islands/mainland have fill: none so the vibrant feathered satellite greenery is 100% visible!
satellite_svg_content = master_svg_content.replace(
    'id="layer_satellite" inkscape:label="Satellite" style="display:none;"',
    'id="layer_satellite" inkscape:label="Satellite" style="display:inline;"'
).replace(
    '.island { fill: #243447; stroke: #3b5066; stroke-width: 0.06; stroke-linejoin: miter; stroke-miterlimit: 4; }',
    '.island { fill: none; stroke: #8ecae6; stroke-width: 0.08; stroke-linejoin: miter; stroke-miterlimit: 4; }'
).replace(
    '.mainland { fill: #18232c; stroke: #263543; stroke-width: 0.15; stroke-linejoin: miter; }',
    '.mainland { fill: none; stroke: #8ecae6; stroke-width: 0.12; stroke-linejoin: miter; }'
).replace(
    '.inland-lake { fill: #0b1d30; stroke: none; }',
    '.inland-lake { fill: none; stroke: #8ecae6; stroke-width: 0.06; }'
)

with open('georgian_bay_satellite_display.svg', 'w') as f:
    f.write(satellite_svg_content)
print("Saved satellite composite SVG: georgian_bay_satellite_display.svg")

# -------------------------------------------------------------------------
# Build Component Layer SVGs (ALL STRICTLY FULL PAGE SIZE 163.8 x 228.6 mm)
# -------------------------------------------------------------------------
print("Writing full-page layer SVGs into layers/ ...")

def make_full_page_layer_svg(filename, inner_svg_content):
    """
    Every layer SVG is strictly the exact size of the page (163.8 x 228.6 mm)
    with an invisible full-bleed bounding rectangle so CAD/slicers never shift them!
    """
    content = f"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{TARGET_WIDTH}mm" height="{TARGET_HEIGHT}mm"
     viewBox="0 0 {TARGET_WIDTH} {TARGET_HEIGHT}">
  <defs>
    <clipPath id="mapClip">
      <rect x="{MARGIN_X}" y="{MARGIN_Y}" width="{MAP_W}" height="{MAP_H}"/>
    </clipPath>
  </defs>
{inner_svg_content}
</svg>"""
    with open(os.path.join('layers', filename), 'w') as f:
        f.write(content)

# Layer 0: Aligned Satellite Image Layer (Full Page)
make_full_page_layer_svg('00_satellite.svg', f"""
  <g clip-path="url(#mapClip)">
    <image href="../satellite_georgian_bay.png" x="{SAT_X:.3f}" y="{SAT_Y:.3f}" width="{SAT_W:.3f}" height="{SAT_H:.3f}" preserveAspectRatio="none"/>
  </g>
""")

# Layer 1: Water Base Plate (Full Page)
make_full_page_layer_svg('01_water_base.svg', f'<rect id="water_background" x="0" y="0" width="{TARGET_WIDTH}" height="{TARGET_HEIGHT}" fill="#0b1d30"/>')

# Layer 2: Muted Mainland (Full Page)
make_full_page_layer_svg('02_mainland.svg', f"""
  <g clip-path="url(#mapClip)">
    <path id="mainland_shore" d="{points_to_path(mainland_poly)}" fill="#18232c"/>
  </g>
""")

# Layer 3: Crisp Uniform Islands (Full Page)
islands_paths = "\n".join([f'    <path id="{isl["id"]}" d="{points_to_path(isl["pts"])}" fill="#243447"/>' for isl in all_islands])
lakes_paths = "\n".join([f'    <path id="beausoleil_lake_{i}" d="{points_to_path(l_pts)}" fill="#0b1d30"/>' for i, l_pts in enumerate(beausoleil_inland_lakes)])
make_full_page_layer_svg('03_islands.svg', f"""
  <g clip-path="url(#mapClip)">
{islands_paths}
{lakes_paths}
  </g>
""")

# Layer 4: Buoys & Anchors (Full Page)
buoys_svg_list = []
for b in buoys_data:
    bx, by = b['svg_pos']
    col = '#e63946' if b['type'] == 'red' else '#06d6a0'
    buoys_svg_list.append(f'    <circle cx="{bx:.3f}" cy="{by:.3f}" r="0.6" fill="{col}"/>')
for a in anchor_spots:
    ax, ay = a['svg_pos']
    buoys_svg_list.append(f'    <circle cx="{ax:.3f}" cy="{ay:.3f}" r="1.0" fill="#ffd166"/>')
make_full_page_layer_svg('04_buoys.svg', "\n".join(buoys_svg_list))

# Multi-Color Bambu Light Box SVG (Full Page)
bambu_svg_content = f"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg"
     width="{TARGET_WIDTH}mm" height="{TARGET_HEIGHT}mm"
     viewBox="0 0 {TARGET_WIDTH} {TARGET_HEIGHT}">
  <defs>
    <clipPath id="mapClip">
      <rect x="{MARGIN_X}" y="{MARGIN_Y}" width="{MAP_W}" height="{MAP_H}"/>
    </clipPath>
  </defs>
  
  <g id="color_1_water" fill="#003566">
    <rect x="0" y="0" width="{TARGET_WIDTH}" height="{TARGET_HEIGHT}"/>
  </g>
  
  <g id="color_2_mainland" fill="#18232c" clip-path="url(#mapClip)">
    <path d="{points_to_path(mainland_poly)}"/>
  </g>
  
  <g id="color_3_islands" fill="#2d3748" clip-path="url(#mapClip)">
{islands_paths}
{lakes_paths}
  </g>
  
  <g id="color_4_buoys">
{"".join(buoys_svg_list)}
  </g>
</svg>"""

with open(os.path.join('layers', 'bambu_lightbox_multicolor.svg'), 'w') as f:
    f.write(bambu_svg_content)

# -------------------------------------------------------------------------
# Build OpenSCAD Model (georgian_bay_display.scad)
# -------------------------------------------------------------------------
print("Writing refined OpenSCAD model: georgian_bay_display.scad ...")

scad_content = f"""// =========================================================================
// GEORGIAN BAY 3D DISPLAY & LIGHTBOX (Refined v3)
// Longuissa Bay to South Bay Cove, Thirty Thousand Islands, Georgian Bay
// Designed for Bambu Lab 3D Printers (H2C, X1C, P1S, A1) & AMS multi-color
// All layers share the exact page dimensions ({TARGET_WIDTH} x {TARGET_HEIGHT} mm)
// =========================================================================

mode = "complete"; // [complete, backlit_faceplate, lightbox_box, water_base, mainland, islands, buoys]

display_width  = {TARGET_WIDTH};  // 163.8 mm (standard Bambu lightbox size)
display_height = {TARGET_HEIGHT}; // 228.6 mm (9.0 inches)

t_water_base   = 1.0;  // 1.0 mm (translucent light transmission)
t_mainland     = 2.2;  // 2.2 mm muted mainland
t_islands      = 2.6;  // 2.6 mm crisp raised islands
t_buoys        = 3.2;  // 3.2 mm raised navigation spar markers
t_frame_lip    = 7.0;  // 7.0 mm perimeter snap-lip for lightbox housing

box_depth      = 38.0; // 38 mm box depth for LED strip
wall_thick     = 2.4;  // 2.4 mm sturdy housing wall
cable_hole_dia = 9.0;  // 9 mm hole for DC / USB-C power cord

c_water      = [0.05, 0.20, 0.35, 0.95]; // Deep Nautical Blue
c_mainland   = [0.18, 0.22, 0.25, 1.0];  // Muted Slate Charcoal
c_islands    = [0.28, 0.35, 0.42, 1.0];  // Granite Island Relief
c_buoy_red   = [0.90, 0.15, 0.20, 1.0];  // Red Spar
c_frame      = [0.08, 0.10, 0.14, 1.0];  // Dark Charcoal Bezel

if (mode == "complete") {{
    full_display();
}} else if (mode == "backlit_faceplate") {{
    backlit_faceplate();
}} else if (mode == "lightbox_box") {{
    lightbox_enclosure();
}} else if (mode == "water_base") {{
    color(c_water) water_plate();
}} else if (mode == "mainland") {{
    color(c_mainland) mainland_part();
}} else if (mode == "islands") {{
    color(c_islands) islands_part();
}} else if (mode == "buoys") {{
    color(c_buoy_red) buoys_part();
}}

module water_plate() {{
    cube([display_width, display_height, t_water_base]);
}}

module mainland_part() {{
    linear_extrude(height = t_mainland)
        import("layers/02_mainland.svg");
}}

module islands_part() {{
    linear_extrude(height = t_islands)
        import("layers/03_islands.svg");
}}

module buoys_part() {{
    linear_extrude(height = t_buoys)
        import("layers/04_buoys.svg");
}}

module frame_rim() {{
    difference() {{
        cube([display_width, display_height, t_frame_lip]);
        translate([wall_thick, wall_thick, -1])
            cube([display_width - 2 * wall_thick, display_height - 2 * wall_thick, t_frame_lip + 2]);
    }}
}}

module full_display() {{
    union() {{
        color(c_water) water_plate();
        color(c_mainland) mainland_part();
        color(c_islands) islands_part();
        color(c_buoy_red) buoys_part();
        color(c_frame) frame_rim();
    }}
}}

module backlit_faceplate() {{
    union() {{
        water_plate();
        mainland_part();
        islands_part();
        buoys_part();
        frame_rim();
    }}
}}

module lightbox_enclosure() {{
    outer_w = display_width + 1.2;
    outer_h = display_height + 1.2;
    
    difference() {{
        cube([outer_w, outer_h, box_depth]);
        translate([wall_thick, wall_thick, wall_thick])
            cube([outer_w - 2 * wall_thick, outer_h - 2 * wall_thick, box_depth]);
        translate([wall_thick - 0.6, wall_thick - 0.6, box_depth - t_frame_lip])
            cube([display_width + 0.4, display_height + 0.4, t_frame_lip + 1]);
        translate([outer_w / 2, -1, wall_thick + cable_hole_dia / 2 + 2])
            rotate([-90, 0, 0])
                cylinder(r = cable_hole_dia / 2, h = wall_thick + 2, $fn = 32);
        translate([outer_w / 2, outer_h - 30, -1])
            cylinder(r = 5.0, h = wall_thick + 2, $fn = 32);
        translate([outer_w / 2 - 2.5, outer_h - 30, -1])
            cube([5.0, 10.0, wall_thick + 2]);
    }}
}}
"""

with open('georgian_bay_display.scad', 'w') as f:
    f.write(scad_content)

print("Saved georgian_bay_display.scad successfully.")

# -------------------------------------------------------------------------
# Render Previews (Inkscape)
# -------------------------------------------------------------------------
print("Rendering preview images via Inkscape...")
os.system("inkscape georgian_bay_display.svg -o georgian_bay_display_preview.png -w 1600")
os.system("inkscape georgian_bay_satellite_display.svg -o georgian_bay_satellite_preview.png -w 1600")
print("All maps and previews generated successfully.")
