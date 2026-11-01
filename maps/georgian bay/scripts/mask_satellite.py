#!/usr/bin/env python3
"""
Masks out the water from satellite_georgian_bay.png using the exact vector polygons
from georgian_bay_display.svg, producing an aligned RGBA PNG with 100% opaque land,
transparent water, and smooth C1 cosine shoreline feathering.
"""

import math
import os
import re
import sys
import numpy as np
from PIL import Image, ImageDraw
import scipy.ndimage as ndi

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    os.chdir(project_dir)

    sat_img_path = "satellite_georgian_bay.png"
    svg_path = "georgian_bay_display.svg"

    if not os.path.exists(sat_img_path):
        print(f"Error: {sat_img_path} not found.")
        sys.exit(1)
    if not os.path.exists(svg_path):
        print(f"Error: {svg_path} not found.")
        sys.exit(1)

    print("Loading satellite image and vector shoreline paths...")
    sat_img = Image.open(sat_img_path).convert("RGB")
    w_px, h_px = sat_img.size

    # Satellite projection coordinates (from MapConfig: MinLat=44.8225, MaxLat=44.9715, MinLon=-79.9140, MaxLon=-79.7660)
    SAT_X = 3.587
    SAT_Y = 3.000
    SAT_W = 156.626
    SAT_H = 222.600

    def to_px(pts):
        return [((p[0] - SAT_X) / SAT_W * w_px, (p[1] - SAT_Y) / SAT_H * h_px) for p in pts]

    def parse_svg_path(d_str):
        subpaths = []
        for part in re.split(r"[Mm]", d_str):
            part = part.strip()
            if not part:
                continue
            pts = []
            for cmd in re.split(r"[LZz]", part):
                cmd = cmd.strip()
                if not cmd:
                    continue
                coords = cmd.split()
                for i in range(0, len(coords), 2):
                    if i + 1 < len(coords):
                        try:
                            pts.append((float(coords[i]), float(coords[i+1])))
                        except ValueError:
                            pass
            if len(pts) >= 3:
                subpaths.append(pts)
        return subpaths

    with open(svg_path, "r", encoding="utf-8") as f:
        svg_text = f.read()

    # Extract mainland path (outer shoreline + inland lakes)
    m_mainland = re.search(r"<path id=\"mainland_shore\" d=\"([^\"]+)\"", svg_text)
    if not m_mainland:
        print("Error: mainland_shore path not found in SVG.")
        sys.exit(1)
    mainland_subpaths = parse_svg_path(m_mainland.group(1))

    # Extract islands
    islands_paths = re.findall(r"<path id=\"([^\"]+)\" d=\"([^\"]+)\" class=\"island\"", svg_text)

    print(f"Drawing land mask: Mainland with {len(mainland_subpaths)-1} lakes and {len(islands_paths)} islands...")
    mask = Image.new("L", (w_px, h_px), 0)
    draw = ImageDraw.Draw(mask)

    # 1. Draw mainland (outer = 255, inland lakes = 0)
    draw.polygon(to_px(mainland_subpaths[0]), fill=255)
    for lake in mainland_subpaths[1:]:
        draw.polygon(to_px(lake), fill=0)

    # 2. Draw islands (outer = 255, island lakes = 0)
    for iid, d in islands_paths:
        isl_subpaths = parse_svg_path(d)
        if isl_subpaths:
            draw.polygon(to_px(isl_subpaths[0]), fill=255)
            for lake in isl_subpaths[1:]:
                draw.polygon(to_px(lake), fill=0)

    land_mask = np.array(mask) > 0

    # 3. Distance transform into water for C1 continuous cosine smoothstep feathering
    dist_out = ndi.distance_transform_edt(~land_mask)
    feather_radius = 4.0  # pixels
    t = np.clip(dist_out / feather_radius, 0.0, 1.0)
    smooth_fade = 0.5 * (1.0 + np.cos(math.pi * t))

    # Land pixels stay 100% solid; shoreline gently feathers into water; water is 0 (transparent)
    alpha_channel = np.where(land_mask, 1.0, smooth_fade)
    alpha_u8 = (alpha_channel * 255).astype(np.uint8)

    rgba = sat_img.convert("RGBA")
    rgba.putalpha(Image.fromarray(alpha_u8))
    rgba.save(sat_img_path, format="PNG")
    print(f"Saved masked satellite image: {sat_img_path} (land=opaque, water=masked out).")

if __name__ == "__main__":
    main()
