#!/usr/bin/env python3
"""
===============================================================================
PARAMETRIC 3D PRINTER WORKBENCH & STORAGE BENCH FOR FREECAD (V3)
===============================================================================
Updated based on user feedback:
1. "L-SHAPED" 2x4 LEGS (BUDGET FAVORITE — NO PLANER OR 4x4 NEEDED!):
   - Corner posts are constructed by joining two standard 2x4s at 90° (an "L" profile).
   - Joined using internal Kreg pocket screws (or JessEm 3/8" dowels) + wood glue.
   - Joins the factory-flat edge of one 2x4 to the flat face of the other:
     ZERO PLANING OR JOINTING NEEDED.
   - Extremely rigid against lateral CoreXY printer racking.
   - Includes a 2" x 2" solid corner foot block nestled inside the base of each
     L-leg to house the threaded leveling foot glide insert.
2. 100% IN-STOCK AT HOME DEPOT CANADA:
   - Frame is 100% standard SPF Premium 2x4 studs (~$6.50 ea).
   - Only 7 standard 2x4x8' studs needed for the entire solid timber base frame!
3. FLUSH DRAWER CONSTRUCTION & ARTICULATION:
   - 3/4" Walnut drawer face mounted flush (0.0" gap) to 1/2" Birch drawer box.
   - Middle spool drawer modeled extended 10" forward on 18" ball-bearing slides
     with 12 upright 1kg filament spools loaded inside.
4. CREALITY CR-6 SE PRINTER:
   - Modeled and staged on the lower right tech shelf with 5.5" clearance above gantry.
5. DUAL-SPOOL HEATED FILAMENT DRYER:
   - Modeled on tabletop beside Bambu CoreXY printer.
===============================================================================
"""

import os
import sys
import math
import FreeCAD
import Part
import Spreadsheet
import TechDraw

FreeCAD.Units.setSchema(3)  # ImperialDecimal (inches)
FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Units").SetInt("UserSchema", 3)

INCH = 25.4  # mm per inch

def in_to_mm(val):
    return val * INCH

def v_in(x, y, z):
    return FreeCAD.Vector(x * INCH, y * INCH, z * INCH)

print("=" * 75)
print("  BUILDING FREECAD 3D PRINTER BENCH (V3 - L-SHAPED 2x4 LEGS, CR-6, DRYER)")
print(f"  FreeCAD Version: {FreeCAD.Version()}")
print("=" * 75)

# =============================================================================
# 1. PARAMETERS & ENVELOPE
# =============================================================================
TOP_WIDTH           = 48.00   # Existing Walnut desktop width
TOP_DEPTH           = 24.00   # Existing Walnut desktop depth
TOP_THICKNESS       = 1.00    # 1.0" solid walnut

TOTAL_HEIGHT        = 31.50   # Finished height to top of desktop
OVERHANG_SIDES      = 1.50    # Overhang on left and right
OVERHANG_FRONT      = 1.50    # Overhang at front
OVERHANG_BACK       = 1.50    # Overhang at rear

BASE_WIDTH          = TOP_WIDTH - 2 * OVERHANG_SIDES   # 45.00"
BASE_DEPTH          = TOP_DEPTH - (OVERHANG_FRONT + OVERHANG_BACK) # 21.00"
BASE_TOP_Z          = TOTAL_HEIGHT - TOP_THICKNESS     # 30.50"

# 2x4 Lumber Dimensions (Standard Actual: 1.5" x 3.5")
LUMBER_2X4_W        = 3.50    # 3.50" wide
LUMBER_2X4_T        = 1.50    # 1.50" thick

FOOT_HEIGHT         = 0.50    # Leveling feet clearance off floor
LEG_Z_BOTTOM        = FOOT_HEIGHT                      # 0.50"
LEG_HEIGHT          = BASE_TOP_Z - LEG_Z_BOTTOM        # 30.00"

BOTTOM_RAIL_Z_BOT   = 1.50    # Bottom stretcher 1.5" off floor
BOTTOM_RAIL_HEIGHT  = LUMBER_2X4_W                     # 3.50"
BOTTOM_RAIL_Z_TOP   = BOTTOM_RAIL_Z_BOT + BOTTOM_RAIL_HEIGHT # 5.00"

TOP_RAIL_HEIGHT     = LUMBER_2X4_W                     # 3.50"
TOP_RAIL_Z_BOT      = BASE_TOP_Z - TOP_RAIL_HEIGHT     # 27.00"

PLY_SHEAR_THICK     = 0.50    # 1/2" back panel for zero racking
PLY_CARCASS_THICK   = 0.75    # 3/4" birch plywood for partition & shelves
DRAWER_REVEAL       = 0.125   # 1/8" gap around drawer fronts

# Rail Spans:
# Front & Rear rails span between the 3.5" wide front/back leg flanges:
# 45.0" base width - 2 * 3.5" = 38.0" span!
front_rail_span     = BASE_WIDTH - 2 * LUMBER_2X4_W   # 38.00"

# Side rails span between the 3.5" deep front/rear side return flanges:
# 21.0" base depth - 2 * 3.5" (front flange 1.5" + side return 3.5" ... wait:
# Front flange is at Y=1.5 to 3.0. Side return flange is Y=3.0 to 6.5.
# Rear flange is at Y=21.0 to 22.5. Rear side return flange is Y=17.5 to 21.0.
# Side rail spans from Y=6.5 to Y=17.5: 17.5 - 6.5 = 11.00"
side_rail_span      = BASE_DEPTH - 2 * (LUMBER_2X4_T + LUMBER_2X4_W) # 21.0 - 2*(5.0) = 11.00"

# Center cross-ties span between front and rear aprons (from Y=3.0 to Y=21.0):
center_tie_span     = BASE_DEPTH - 2 * LUMBER_2X4_T   # 18.00"

DOC_NAME = "Bambu_Printer_Stand"
if FreeCAD.activeDocument() and FreeCAD.activeDocument().Name == DOC_NAME:
    FreeCAD.closeDocument(DOC_NAME)
doc = FreeCAD.newDocument(DOC_NAME)
doc.Label = "Bambu Stand (V3 - L-Shaped 2x4 Legs, CR-6, Dryer)"

# Spreadsheet
sheet = doc.addObject("Spreadsheet::Sheet", "Parameters")
sheet.Label = "Bench Parameters & Lumber Specs"

params = [
    ("TopWidth", f"{TOP_WIDTH:.2f} in", "Walnut Desktop Width"),
    ("TopDepth", f"{TOP_DEPTH:.2f} in", "Walnut Desktop Depth"),
    ("TopThickness", f"{TOP_THICKNESS:.2f} in", "Walnut Desktop Thickness"),
    ("TotalHeight", f"{TOTAL_HEIGHT:.2f} in", "Finished Height"),
    ("BaseWidth", f"{BASE_WIDTH:.2f} in", "Outer Base Frame Width"),
    ("BaseDepth", f"{BASE_DEPTH:.2f} in", "Outer Base Frame Depth"),
    ("LegHeight", f"{LEG_HEIGHT:.2f} in", "L-Leg Length (30.00 in)"),
    ("RailThickness", f"{LUMBER_2X4_T:.2f} in", "2x4 Rail Thickness"),
    ("RailWidth", f"{LUMBER_2X4_W:.2f} in", "2x4 Rail Width"),
    ("FrontRailSpan", f"{front_rail_span:.2f} in", "Front/Rear Apron Length"),
    ("SideRailSpan", f"{side_rail_span:.2f} in", "Side Apron Length"),
    ("BackShearThick", f"{PLY_SHEAR_THICK:.2f} in", "Anti-Racking Shear Panel"),
    ("ShelfPlywoodThick", f"{PLY_CARCASS_THICK:.2f} in", "Divider & Shelf Plywood"),
]

for idx, (alias, val, desc) in enumerate(params, start=1):
    sheet.set(f"A{idx}", alias)
    sheet.set(f"B{idx}", val)
    sheet.setAlias(f"B{idx}", alias)
    sheet.set(f"C{idx}", desc)

doc.recompute()
print("  [+] Parameters spreadsheet updated.")

# =============================================================================
# 2. DOCUMENT GROUPS & COLORS
# =============================================================================
grp_top       = doc.addObject("App::DocumentObjectGroup", "01_Walnut_Tabletop")
grp_top.Label = "01 Walnut Tabletop (24x48x1)"

grp_timber    = doc.addObject("App::DocumentObjectGroup", "02_L_Shaped_2x4_Frame")
grp_timber.Label = "02 L-Shaped 2x4 Legs & Rails"

grp_panels    = doc.addObject("App::DocumentObjectGroup", "03_Shear_Panels_and_Shelves")
grp_panels.Label = "03 Shear Back Panel & Partition"

grp_drawers   = doc.addObject("App::DocumentObjectGroup", "04_Articulated_Drawers")
grp_drawers.Label = "04 Drawers & Ball-Bearing Slides"

grp_printers  = doc.addObject("App::DocumentObjectGroup", "05_Equipment_and_Printers")
grp_printers.Label = "05 Printers (Bambu & CR-6) & Dual Dryer"

grp_hardware  = doc.addObject("App::DocumentObjectGroup", "06_Hardware_and_Feet")
grp_hardware.Label = "06 Leveling Feet & Pulls"

# Color Palette
COL_WALNUT      = (0.36, 0.22, 0.13)
COL_LEG_FLANGE  = (0.83, 0.70, 0.50)
COL_LEG_RETURN  = (0.86, 0.73, 0.53)
COL_PINE_RAILS  = (0.87, 0.75, 0.55)
COL_PLY_BIRCH   = (0.91, 0.82, 0.66)
COL_STEEL_DARK  = (0.24, 0.24, 0.26)
COL_CHROME      = (0.78, 0.78, 0.80)
COL_SLIDE_ZINC  = (0.70, 0.72, 0.75)
COL_BAMBU_BODY  = (0.18, 0.19, 0.21)
COL_CR6_ALUM    = (0.20, 0.20, 0.22)
COL_CR6_BED     = (0.12, 0.12, 0.13)
COL_DRYER_BASE  = (0.88, 0.88, 0.88)
COL_DRYER_DOME  = (0.65, 0.75, 0.85)
COL_SPOOL_PLA   = (0.85, 0.20, 0.20)
COL_SPOOL_PETG  = (0.15, 0.45, 0.85)

def set_style(obj, color, transparency=0):
    if hasattr(obj, "ViewObject") and obj.ViewObject:
        obj.ViewObject.ShapeColor = color
        obj.ViewObject.LineColor = (0.15, 0.15, 0.15)
        obj.ViewObject.Transparency = transparency

def make_box(name, group, x, y, z, dx, dy, dz, color, transparency=0):
    box = doc.addObject("Part::Box", name)
    box.Length = in_to_mm(dx)
    box.Width  = in_to_mm(dy)
    box.Height = in_to_mm(dz)
    box.Placement = FreeCAD.Placement(v_in(x, y, z), FreeCAD.Rotation(0, 0, 0, 1))
    group.addObject(box)
    set_style(box, color, transparency)
    return box

def make_cylinder(name, group, cx, cy, cz, r, h, color, axis=(0,0,1)):
    cyl = doc.addObject("Part::Cylinder", name)
    cyl.Radius = in_to_mm(r)
    cyl.Height = in_to_mm(h)
    if axis == (0, 1, 0):
        rot = FreeCAD.Rotation(FreeCAD.Vector(1, 0, 0), -90)
    elif axis == (1, 0, 0):
        rot = FreeCAD.Rotation(FreeCAD.Vector(0, 1, 0), 90)
    else:
        rot = FreeCAD.Rotation(0, 0, 0, 1)
    cyl.Placement = FreeCAD.Placement(v_in(cx, cy, cz), rot)
    group.addObject(cyl)
    set_style(cyl, color)
    return cyl

# =============================================================================
# 3. GROUP 01: EXISTING WALNUT DESKTOP
# =============================================================================
print("  [*] Modeling Existing Walnut Desktop...")
top = make_box("Walnut_Desktop_Top", grp_top,
               0.0, 0.0, BASE_TOP_Z,
               TOP_WIDTH, TOP_DEPTH, TOP_THICKNESS,
               COL_WALNUT)

# =============================================================================
# 4. GROUP 02: "L-SHAPED" 2x4 CORNER LEGS & 2x4 APRONS (NO PLANER NEEDED!)
# =============================================================================
print("  [*] Modeling L-Shaped 2x4 Corner Legs (8 pcs 2x4 joined at 90°)...")

# Each corner post is an "L" made of two 2x4 pieces joined at 90°:
# Piece 1: Front (or Rear) Flange: 3.50" wide x 1.50" thick x 30.00" tall
# Piece 2: Side Return Flange:    1.50" thick x 3.50" deep x 30.00" tall

# Front-Left L-Leg
leg_fl_front = make_box("L_Leg_FL_FrontFlange", grp_timber,
                        OVERHANG_SIDES, OVERHANG_FRONT, LEG_Z_BOTTOM,
                        LUMBER_2X4_W, LUMBER_2X4_T, LEG_HEIGHT,
                        COL_LEG_FLANGE)
leg_fl_side  = make_box("L_Leg_FL_SideReturn", grp_timber,
                        OVERHANG_SIDES, OVERHANG_FRONT + LUMBER_2X4_T, LEG_Z_BOTTOM,
                        LUMBER_2X4_T, LUMBER_2X4_W, LEG_HEIGHT,
                        COL_LEG_RETURN)

# Front-Right L-Leg
leg_fr_front = make_box("L_Leg_FR_FrontFlange", grp_timber,
                        TOP_WIDTH - OVERHANG_SIDES - LUMBER_2X4_W, OVERHANG_FRONT, LEG_Z_BOTTOM,
                        LUMBER_2X4_W, LUMBER_2X4_T, LEG_HEIGHT,
                        COL_LEG_FLANGE)
leg_fr_side  = make_box("L_Leg_FR_SideReturn", grp_timber,
                        TOP_WIDTH - OVERHANG_SIDES - LUMBER_2X4_T, OVERHANG_FRONT + LUMBER_2X4_T, LEG_Z_BOTTOM,
                        LUMBER_2X4_T, LUMBER_2X4_W, LEG_HEIGHT,
                        COL_LEG_RETURN)

# Back-Left L-Leg
leg_bl_rear  = make_box("L_Leg_BL_RearFlange", grp_timber,
                        OVERHANG_SIDES, TOP_DEPTH - OVERHANG_BACK - LUMBER_2X4_T, LEG_Z_BOTTOM,
                        LUMBER_2X4_W, LUMBER_2X4_T, LEG_HEIGHT,
                        COL_LEG_FLANGE)
leg_bl_side  = make_box("L_Leg_BL_SideReturn", grp_timber,
                        OVERHANG_SIDES, TOP_DEPTH - OVERHANG_BACK - LUMBER_2X4_T - LUMBER_2X4_W, LEG_Z_BOTTOM,
                        LUMBER_2X4_T, LUMBER_2X4_W, LEG_HEIGHT,
                        COL_LEG_RETURN)

# Back-Right L-Leg
leg_br_rear  = make_box("L_Leg_BR_RearFlange", grp_timber,
                        TOP_WIDTH - OVERHANG_SIDES - LUMBER_2X4_W, TOP_DEPTH - OVERHANG_BACK - LUMBER_2X4_T, LEG_Z_BOTTOM,
                        LUMBER_2X4_W, LUMBER_2X4_T, LEG_HEIGHT,
                        COL_LEG_FLANGE)
leg_br_side  = make_box("L_Leg_BR_SideReturn", grp_timber,
                        TOP_WIDTH - OVERHANG_SIDES - LUMBER_2X4_T, TOP_DEPTH - OVERHANG_BACK - LUMBER_2X4_T - LUMBER_2X4_W, LEG_Z_BOTTOM,
                        LUMBER_2X4_T, LUMBER_2X4_W, LEG_HEIGHT,
                        COL_LEG_RETURN)

# Foot Base Blocks (Nestled inside each L-leg at the bottom to house the leveling glide insert)
foot_block_size = 2.00
foot_fl = make_box("L_Leg_FL_FootBlock", grp_timber,
                   OVERHANG_SIDES + LUMBER_2X4_T, OVERHANG_FRONT + LUMBER_2X4_T, LEG_Z_BOTTOM,
                   foot_block_size, foot_block_size, 1.50,
                   COL_PINE_RAILS)
foot_fr = make_box("L_Leg_FR_FootBlock", grp_timber,
                   TOP_WIDTH - OVERHANG_SIDES - LUMBER_2X4_W, OVERHANG_FRONT + LUMBER_2X4_T, LEG_Z_BOTTOM,
                   foot_block_size, foot_block_size, 1.50,
                   COL_PINE_RAILS)
foot_bl = make_box("L_Leg_BL_FootBlock", grp_timber,
                   OVERHANG_SIDES + LUMBER_2X4_T, TOP_DEPTH - OVERHANG_BACK - LUMBER_2X4_T - foot_block_size, LEG_Z_BOTTOM,
                   foot_block_size, foot_block_size, 1.50,
                   COL_PINE_RAILS)
foot_br = make_box("L_Leg_BR_FootBlock", grp_timber,
                   TOP_WIDTH - OVERHANG_SIDES - LUMBER_2X4_W, TOP_DEPTH - OVERHANG_BACK - LUMBER_2X4_T - foot_block_size, LEG_Z_BOTTOM,
                   foot_block_size, foot_block_size, 1.50,
                   COL_PINE_RAILS)

# Upper Aprons (Top Rails, 2x4: 1.5" x 3.5")
# Front & Rear aprons span 38.00" between the front leg flanges:
apron_front = make_box("Upper_Apron_Front", grp_timber,
                       OVERHANG_SIDES + LUMBER_2X4_W, OVERHANG_FRONT, TOP_RAIL_Z_BOT,
                       front_rail_span, LUMBER_2X4_T, TOP_RAIL_HEIGHT,
                       COL_PINE_RAILS)

apron_back = make_box("Upper_Apron_Back", grp_timber,
                      OVERHANG_SIDES + LUMBER_2X4_W, TOP_DEPTH - OVERHANG_BACK - LUMBER_2X4_T, TOP_RAIL_Z_BOT,
                      front_rail_span, LUMBER_2X4_T, TOP_RAIL_HEIGHT,
                      COL_PINE_RAILS)

# Side aprons span 11.00" between the front & rear side return flanges:
apron_left = make_box("Upper_Apron_Left", grp_timber,
                      OVERHANG_SIDES, OVERHANG_FRONT + LUMBER_2X4_T + LUMBER_2X4_W, TOP_RAIL_Z_BOT,
                      LUMBER_2X4_T, side_rail_span, TOP_RAIL_HEIGHT,
                      COL_PINE_RAILS)

apron_right = make_box("Upper_Apron_Right", grp_timber,
                       TOP_WIDTH - OVERHANG_SIDES - LUMBER_2X4_T, OVERHANG_FRONT + LUMBER_2X4_T + LUMBER_2X4_W, TOP_RAIL_Z_BOT,
                       LUMBER_2X4_T, side_rail_span, TOP_RAIL_HEIGHT,
                       COL_PINE_RAILS)

# Upper Center Cross-Tie (18.00" long)
apron_mid = make_box("Upper_Cross_Tie_Mid", grp_timber,
                     (TOP_WIDTH - LUMBER_2X4_T) / 2.0, OVERHANG_FRONT + LUMBER_2X4_T, TOP_RAIL_Z_BOT,
                     LUMBER_2X4_T, center_tie_span, TOP_RAIL_HEIGHT,
                     COL_PINE_RAILS)

# Lower Stretchers (Bottom Rails, 2x4: 1.5" x 3.5", at Z = 1.50")
stretcher_front = make_box("Lower_Stretcher_Front", grp_timber,
                           OVERHANG_SIDES + LUMBER_2X4_W, OVERHANG_FRONT, BOTTOM_RAIL_Z_BOT,
                           front_rail_span, LUMBER_2X4_T, BOTTOM_RAIL_HEIGHT,
                           COL_PINE_RAILS)

stretcher_back = make_box("Lower_Stretcher_Back", grp_timber,
                          OVERHANG_SIDES + LUMBER_2X4_W, TOP_DEPTH - OVERHANG_BACK - LUMBER_2X4_T, BOTTOM_RAIL_Z_BOT,
                          front_rail_span, LUMBER_2X4_T, BOTTOM_RAIL_HEIGHT,
                          COL_PINE_RAILS)

stretcher_left = make_box("Lower_Stretcher_Left", grp_timber,
                          OVERHANG_SIDES, OVERHANG_FRONT + LUMBER_2X4_T + LUMBER_2X4_W, BOTTOM_RAIL_Z_BOT,
                          LUMBER_2X4_T, side_rail_span, BOTTOM_RAIL_HEIGHT,
                          COL_PINE_RAILS)

stretcher_right = make_box("Lower_Stretcher_Right", grp_timber,
                           TOP_WIDTH - OVERHANG_SIDES - LUMBER_2X4_T, OVERHANG_FRONT + LUMBER_2X4_T + LUMBER_2X4_W, BOTTOM_RAIL_Z_BOT,
                           LUMBER_2X4_T, side_rail_span, BOTTOM_RAIL_HEIGHT,
                           COL_PINE_RAILS)

stretcher_mid = make_box("Lower_Cross_Tie_Mid", grp_timber,
                         (TOP_WIDTH - LUMBER_2X4_T) / 2.0, OVERHANG_FRONT + LUMBER_2X4_T, BOTTOM_RAIL_Z_BOT,
                         LUMBER_2X4_T, center_tie_span, BOTTOM_RAIL_HEIGHT,
                         COL_PINE_RAILS)

# =============================================================================
# 5. GROUP 03: ANTI-RACKING SHEAR WALL & PARTITION
# =============================================================================
print("  [*] Modeling Shear Wall Back Panel & Center Partition...")

# Full 1/2" Plywood Rear Shear Panel (Screwed across rear 2x4 flanges and rails)
shear_panel = make_box("Back_Shear_Wall_Panel", grp_panels,
                       OVERHANG_SIDES, TOP_DEPTH - OVERHANG_BACK, BOTTOM_RAIL_Z_BOT,
                       BASE_WIDTH, PLY_SHEAR_THICK, BASE_TOP_Z - BOTTOM_RAIL_Z_BOT,
                       COL_PLY_BIRCH)

# Center Partition (3/4" Birch Plywood)
divider_height = TOP_RAIL_Z_BOT - BOTTOM_RAIL_Z_TOP # 27.0 - 5.0 = 22.0"
divider_depth  = center_tie_span                     # 18.00"
divider_x      = (TOP_WIDTH - PLY_CARCASS_THICK) / 2.0 # 23.625"

divider = make_box("Center_Divider_Gable", grp_panels,
                   divider_x, OVERHANG_FRONT + LUMBER_2X4_T, BOTTOM_RAIL_Z_TOP,
                   PLY_CARCASS_THICK, divider_depth, divider_height,
                   COL_PLY_BIRCH)

# Bay Dimensions:
# Front rail span = 38.00". Minus 0.75" divider = 37.25" total clear width.
# Left Bay clear width = 18.625" (473 mm)
# Right Bay clear width = 18.625" (473 mm)
bay_width = (front_rail_span - PLY_CARCASS_THICK) / 2.0 # 18.625"

# Right Bay Lower Heavy Equipment Shelf (Supports Creality CR-6 SE)
shelf_cr6 = make_box("Right_Bay_CR6_Shelf", grp_panels,
                     TOP_WIDTH / 2.0 + PLY_CARCASS_THICK / 2.0, OVERHANG_FRONT + LUMBER_2X4_T, BOTTOM_RAIL_Z_TOP,
                     bay_width, divider_depth, PLY_CARCASS_THICK,
                     COL_PLY_BIRCH)

# =============================================================================
# 6. GROUP 04: ARTICULATED DRAWERS & BALL-BEARING SLIDES
# =============================================================================
print("  [*] Modeling Articulated Drawers with Ball-Bearing Slides...")

drawer_box_w     = bay_width - 1.00 # 17.625"
drawer_box_d     = 18.00            # 18.00" deep
drawer_box_x     = OVERHANG_SIDES + LUMBER_2X4_W + 0.50 # 5.50"
drawer_face_w    = bay_width - 2 * DRAWER_REVEAL        # 18.375"
drawer_face_x    = OVERHANG_SIDES + LUMBER_2X4_W + DRAWER_REVEAL # 5.125"
drawer_face_t    = 0.75             # 3/4" Walnut front

drawer_closed_box_y  = OVERHANG_FRONT # 1.50"
drawer_closed_face_y = OVERHANG_FRONT - drawer_face_t # 0.75"

drawer_specs = [
    ("Drawer_03_Bottom_Spools", 7.75, 8.50, 0.0 + DRAWER_REVEAL, False, 0.0),
    ("Drawer_02_Middle_Spools", 7.75, 8.50, 8.50 + 2 * DRAWER_REVEAL, True, 10.0), # EXTENDED 10" FORWARD!
    ("Drawer_01_Top_Tools",     3.50, 4.50, 17.00 + 3 * DRAWER_REVEAL, False, 0.0),
]

for dname, box_h, face_h, z_rel, is_ext, ext_dist in drawer_specs:
    cur_z = BOTTOM_RAIL_Z_TOP + z_rel
    cur_face_y = drawer_closed_face_y - ext_dist
    cur_box_y  = drawer_closed_box_y - ext_dist
    
    # 1. Drawer Front Face (Mounted flush to box front)
    face = make_box(f"{dname}_Face", grp_drawers,
                    drawer_face_x, cur_face_y, cur_z,
                    drawer_face_w, drawer_face_t, face_h,
                    COL_WALNUT)
    
    # 2. Drawer Box (0.5" Birch Plywood walls)
    box = make_box(f"{dname}_Box", grp_drawers,
                   drawer_box_x, cur_box_y, cur_z + 0.25,
                   drawer_box_w, drawer_box_d, box_h,
                   COL_PLY_BIRCH)
    
    # 3. Handle / Bar Pull on Drawer Face
    h_len = 5.00
    h_h   = 0.50
    h_d   = 0.75
    h_x   = drawer_face_x + (drawer_face_w - h_len) / 2.0
    h_y   = cur_face_y - h_d
    h_z   = cur_z + (face_h - h_h) / 2.0
    handle = make_box(f"{dname}_Handle", grp_hardware,
                      h_x, h_y, h_z,
                      h_len, h_d, h_h,
                      COL_STEEL_DARK)
    
    # 4. Ball-Bearing Drawer Slides (Left & Right)
    slide_thick = 0.45
    slide_h     = 1.50
    slide_z     = cur_z + 1.50
    
    # Outer Carcass Member (Fixed to leg & partition)
    fixed_left = make_box(f"{dname}_Slide_Fixed_L", grp_drawers,
                          drawer_box_x - slide_thick, OVERHANG_FRONT + LUMBER_2X4_T, slide_z,
                          slide_thick, drawer_box_d - 1.0, slide_h,
                          COL_SLIDE_ZINC)
    fixed_right = make_box(f"{dname}_Slide_Fixed_R", grp_drawers,
                           drawer_box_x + drawer_box_w, OVERHANG_FRONT + LUMBER_2X4_T, slide_z,
                           slide_thick, drawer_box_d - 1.0, slide_h,
                           COL_SLIDE_ZINC)
    
    # Inner Drawer Member (Attached to box, extends with the drawer)
    if is_ext:
        ext_rail_l = make_box(f"{dname}_Slide_Ext_L", grp_drawers,
                              drawer_box_x - slide_thick * 0.7, cur_box_y + 1.0, slide_z + 0.25,
                              slide_thick * 0.6, drawer_box_d, slide_h - 0.5,
                              COL_CHROME)
        ext_rail_r = make_box(f"{dname}_Slide_Ext_R", grp_drawers,
                              drawer_box_x + drawer_box_w + slide_thick * 0.1, cur_box_y + 1.0, slide_z + 0.25,
                              slide_thick * 0.6, drawer_box_d, slide_h - 0.5,
                              COL_CHROME)
        
        # 12 Upright 1kg Filament Spools loaded inside!
        spool_r = 7.87 / 2.0
        spool_w = 2.56
        spool_z = cur_z + 0.50 + spool_r
        for row_idx, row_y in enumerate([cur_box_y + 4.5, cur_box_y + 12.5]):
            for col_idx in range(6):
                spool_x = drawer_box_x + 1.0 + col_idx * 2.65
                col = COL_SPOOL_PLA if (row_idx + col_idx) % 2 == 0 else COL_SPOOL_PETG
                make_cylinder(f"Drawer_Spool_R{row_idx}_C{col_idx}", grp_drawers,
                              spool_x, row_y, spool_z,
                              spool_r, spool_w, col, axis=(1, 0, 0))

# =============================================================================
# 7. GROUP 05: CREALITY CR-6 SE PRINTER (ON LOWER RIGHT SHELF)
# =============================================================================
print("  [*] Modeling Creality CR-6 SE 3D Printer inside Right Bay...")
cr6_base_w = 11.80
cr6_base_d = 15.00
cr6_base_h = 2.36
cr6_x = divider_x + PLY_CARCASS_THICK + (bay_width - cr6_base_w) / 2.0
cr6_y = OVERHANG_FRONT + LUMBER_2X4_T + 1.50
cr6_z = BOTTOM_RAIL_Z_TOP + PLY_CARCASS_THICK

cr6_base = make_box("CR6_Base_Chassis", grp_printers,
                    cr6_x, cr6_y, cr6_z,
                    cr6_base_w, cr6_base_d, cr6_base_h,
                    COL_CR6_ALUM)

bed_size = 9.25
cr6_bed = make_box("CR6_Glass_Print_Bed", grp_printers,
                   cr6_x + (cr6_base_w - bed_size) / 2.0, cr6_y + (cr6_base_d - bed_size) / 2.0, cr6_z + cr6_base_h,
                   bed_size, bed_size, 0.25,
                   COL_CR6_BED)

tower_w = 1.57
tower_d = 1.57
tower_h = 16.50
cr6_tower_l = make_box("CR6_Z_Tower_Left", grp_printers,
                       cr6_x + 0.5, cr6_y + 4.5, cr6_z + cr6_base_h,
                       tower_w, tower_d, tower_h,
                       COL_CR6_ALUM)

cr6_tower_r = make_box("CR6_Z_Tower_Right", grp_printers,
                       cr6_x + cr6_base_w - tower_w - 0.5, cr6_y + 4.5, cr6_z + cr6_base_h,
                       tower_w, tower_d, tower_h,
                       COL_CR6_ALUM)

cr6_top_bar = make_box("CR6_Gantry_Top_Crossbar", grp_printers,
                       cr6_x + 0.5, cr6_y + 4.5, cr6_z + cr6_base_h + tower_h,
                       cr6_base_w - 1.0, tower_d, 0.80,
                       COL_CR6_ALUM)

cr6_hotend = make_box("CR6_Printhead_Carriage", grp_printers,
                      cr6_x + cr6_base_w / 2.0 - 1.25, cr6_y + 4.0, cr6_z + cr6_base_h + 7.0,
                      2.50, 2.50, 2.50,
                      (0.15, 0.50, 0.85))

cr6_screen = make_box("CR6_Touchscreen_Display", grp_printers,
                      cr6_x + cr6_base_w + 0.2, cr6_y + 0.5, cr6_z + 0.5,
                      1.00, 3.50, 2.50,
                      (0.10, 0.10, 0.12))

# =============================================================================
# 8. GROUP 05: DUAL-SPOOL FILAMENT DRYER (ON TABLETOP)
# =============================================================================
print("  [*] Modeling Dual-Spool Filament Dryer with 2 Spools...")
dryer_w = 9.60
dryer_d = 8.80
dryer_h_base = 2.50
dryer_h_dome = 8.10
dryer_x = TOP_WIDTH - OVERHANG_SIDES - dryer_w - 4.0
dryer_y = (TOP_DEPTH - dryer_d) / 2.0
dryer_z = TOTAL_HEIGHT

dryer_base = make_box("Dryer_Heating_Base", grp_printers,
                      dryer_x, dryer_y, dryer_z,
                      dryer_w, dryer_d, dryer_h_base,
                      COL_DRYER_BASE)

dryer_screen = make_box("Dryer_LCD_Display", grp_printers,
                        dryer_x + (dryer_w - 3.5) / 2.0, dryer_y - 0.05, dryer_z + 0.5,
                        3.50, 0.10, 1.50,
                        (0.05, 0.05, 0.05))

dryer_dome = make_box("Dryer_Transparent_Lid", grp_printers,
                      dryer_x + 0.2, dryer_y + 0.2, dryer_z + dryer_h_base,
                      dryer_w - 0.4, dryer_d - 0.4, dryer_h_dome,
                      COL_DRYER_DOME, transparency=60)

dry_spool_r = 7.87 / 2.0
dry_spool_w = 2.56
spool_1_x = dryer_x + 1.2
spool_2_x = dryer_x + 5.2
dry_spool_y = dryer_y + dryer_d / 2.0
dry_spool_z = dryer_z + dryer_h_base + dry_spool_r + 0.2

make_cylinder("Dryer_Spool_1", grp_printers,
              spool_1_x, dry_spool_y, dry_spool_z,
              dry_spool_r, dry_spool_w, COL_SPOOL_PLA, axis=(1, 0, 0))

make_cylinder("Dryer_Spool_2", grp_printers,
              spool_2_x, dry_spool_y, dry_spool_z,
              dry_spool_r, dry_spool_w, COL_SPOOL_PETG, axis=(1, 0, 0))

# =============================================================================
# 9. GROUP 05: BAMBU LAB 3D PRINTER & AMS REFERENCE MOCKUP
# =============================================================================
print("  [*] Modeling Bambu 3D Printer & AMS Visual Scale Reference...")
p_w = 15.30
p_d = 15.30
p_h = 18.00
p_x = OVERHANG_SIDES + 3.0
p_y = (TOP_DEPTH - p_d) / 2.0
p_z = TOTAL_HEIGHT

printer_body = make_box("Bambu_Printer_Chassis", grp_printers,
                        p_x, p_y, p_z,
                        p_w, p_d, p_h,
                        COL_BAMBU_BODY)

printer_door = make_box("Bambu_Printer_Glass_Door", grp_printers,
                        p_x + 0.5, p_y - 0.15, p_z + 1.0,
                        p_w - 1.0, 0.15, p_h - 2.0,
                        (0.70, 0.85, 0.95), transparency=50)

ams_w = 14.50
ams_d = 11.10
ams_h = 8.80
ams_x = p_x + (p_w - ams_w) / 2.0
ams_y = p_y + (p_d - ams_d) / 2.0
ams_z = p_z + p_h

ams_unit = make_box("Bambu_AMS_Unit", grp_printers,
                    ams_x, ams_y, ams_z,
                    ams_w, ams_d, ams_h,
                    (0.85, 0.88, 0.90), transparency=35)

# =============================================================================
# 10. GROUP 06: LEVELING FEET (UNDER L-LEG CORNERS)
# =============================================================================
print("  [*] Modeling Heavy-Duty Vibration Dampening Leveling Feet...")
leg_centers = [
    ("FL", OVERHANG_SIDES + 2.0, OVERHANG_FRONT + 2.0),
    ("FR", TOP_WIDTH - OVERHANG_SIDES - 2.0, OVERHANG_FRONT + 2.0),
    ("BL", OVERHANG_SIDES + 2.0, TOP_DEPTH - OVERHANG_BACK - 2.0),
    ("BR", TOP_WIDTH - OVERHANG_SIDES - 2.0, TOP_DEPTH - OVERHANG_BACK - 2.0),
]

for tag, cx, cy in leg_centers:
    pad = make_cylinder(f"Leveling_Foot_Pad_{tag}", grp_hardware,
                        cx, cy, 0.0, 1.25, 0.35, COL_STEEL_DARK)
    stud = make_cylinder(f"Leveling_Foot_Stud_{tag}", grp_hardware,
                         cx, cy, 0.35, 0.25, 0.65, COL_CHROME)

doc.recompute()
print("  [+] Solid geometry generated and recomputed successfully!")

# =============================================================================
# 11. GROUP 07: TECHNICAL SHOP DRAWINGS (TECHDRAW WORKBENCH)
# =============================================================================
print("  [*] Building TechDraw Technical Shop Drawing Sheet...")
grp_drawings = doc.addObject("App::DocumentObjectGroup", "07_Technical_Drawings")
grp_drawings.Label = "07 Technical Drawings (Shop Blueprints)"

tmpl_file = os.path.join("/home/scott/20p/cad/bambu-table", "drawing_template.svg")
page = doc.addObject("TechDraw::DrawPage", "Page_Shop_Sheet_1")
page.Label = "Shop Sheet 1 - Bench Elevations & Specs"
template = doc.addObject("TechDraw::DrawSVGTemplate", "Template_Sheet_1")
template.Template = tmpl_file
page.Template = template
grp_drawings.addObject(page)
grp_drawings.addObject(template)
doc.recompute()

template.setEditFieldContent("DrawingTitle1", "BAMBU 3D PRINTER STAND & WORKBENCH")
template.setEditFieldContent("DrawingTitle2", "L-SHAPED 2x4 LEGS + CR-6 & DUAL DRYER")
template.setEditFieldContent("DrawingTitle3", "3-TIER SPOOL DRAWERS & TECH BAY")
template.setEditFieldContent("DrawnBy", "Scott Kirkwood")
template.setEditFieldContent("Sheet", "1 of 1")
template.setEditFieldContent("scale", "1:15")
template.setEditFieldContent("CompanyName", "WOODWORKING BLUEPRINTS")
template.setEditFieldContent("CompanyAddress", "ALL UNITS: INCHES (\") / DEGREES (°)")

shop_solids = [
    top,
    leg_fl_front, leg_fl_side, foot_fl,
    leg_fr_front, leg_fr_side, foot_fr,
    leg_bl_rear,  leg_bl_side, foot_bl,
    leg_br_rear,  leg_br_side, foot_br,
    apron_front, apron_back, apron_left, apron_right, apron_mid,
    stretcher_front, stretcher_back, stretcher_left, stretcher_right, stretcher_mid,
    shear_panel, divider, shelf_cr6,
    doc.getObject("Drawer_01_Top_Tools_Face"),
    doc.getObject("Drawer_02_Middle_Spools_Face"),
    doc.getObject("Drawer_02_Middle_Spools_Box"),
    doc.getObject("Drawer_03_Bottom_Spools_Face"),
    printer_body, ams_unit,
    cr6_base, cr6_tower_l, cr6_tower_r, cr6_top_bar, cr6_hotend,
    dryer_base, dryer_dome
]

# Front Elevation View
v_front = doc.addObject("TechDraw::DrawViewPart", "View_Front_Elevation")
v_front.Source = shop_solids
v_front.Direction = FreeCAD.Vector(0, -1, 0)
v_front.XDirection = FreeCAD.Vector(1, 0, 0)
v_front.ScaleType = "Custom"
v_front.Scale = 0.075
page.addView(v_front)
v_front.X = 110.0
v_front.Y = 175.0
grp_drawings.addObject(v_front)

# Side Elevation View
v_side = doc.addObject("TechDraw::DrawViewPart", "View_Side_Elevation")
v_side.Source = shop_solids
v_side.Direction = FreeCAD.Vector(1, 0, 0)
v_side.XDirection = FreeCAD.Vector(0, 1, 0)
v_side.ScaleType = "Custom"
v_side.Scale = 0.075
page.addView(v_side)
v_side.X = 235.0
v_side.Y = 175.0
grp_drawings.addObject(v_side)

# Isometric 3D View
v_iso = doc.addObject("TechDraw::DrawViewPart", "View_Isometric_Assembly")
v_iso.Source = shop_solids
v_iso.Direction = FreeCAD.Vector(-1.0, -1.2, 0.9)
v_iso.XDirection = FreeCAD.Vector(1.2, -1.0, 0.0)
v_iso.ScaleType = "Custom"
v_iso.Scale = 0.055
page.addView(v_iso)
v_iso.X = 350.0
v_iso.Y = 180.0
grp_drawings.addObject(v_iso)

# Cut List Annotation Block
a_cut = doc.addObject("TechDraw::DrawViewAnnotation", "Annotation_Lumber_Cut_List")
a_cut.Text = [
    "MASTER LUMBER & HARDWARE SCHEDULE (V3: L-SHAPED 2x4 LEGS - NO PLANER NEEDED)",
    "=========================================================================================================",
    "PART NAME                 QTY  MATERIAL       FINISHED SIZE (IN)     NOTES",
    "---------------------------------------------------------------------------------------------------------",
    "Walnut Tabletop            1   1\" Walnut      24.00\" x 48.00\" x 1\"   Existing desktop; 1.5\" overhang",
    "L-Leg Front/Rear Flanges   4   2x4 SPF Lumber 1.50\" x 3.50\" x 30.00\" 2x4 joined at 90° with pocket screws",
    "L-Leg Side Return Flanges  4   2x4 SPF Lumber 1.50\" x 3.50\" x 30.00\" Factory-flat edges join flat face",
    "Front/Back Upper Aprons    2   2x4 SPF Lumber 1.50\" x 3.50\" x 38.00\" Upper perimeter frame",
    "Side Upper Aprons          2   2x4 SPF Lumber 1.50\" x 3.50\" x 11.00\" Upper side frame",
    "Upper Center Cross-Tie     1   2x4 SPF Lumber 1.50\" x 3.50\" x 18.00\" Desktop mid support & divider anchor",
    "Front/Back Lower Rails     2   2x4 SPF Lumber 1.50\" x 3.50\" x 38.00\" Lower stretchers 1.5\" off floor",
    "Side Lower Rails           2   2x4 SPF Lumber 1.50\" x 3.50\" x 11.00\" Lower side stretchers",
    "Lower Center Cross-Tie     1   2x4 SPF Lumber 1.50\" x 3.50\" x 18.00\" Bottom shelf & divider support",
    "Foot Corner Mount Blocks   4   2x4 Scrap      1.50\" x 2.00\" x 2.00\"  Glued in L-corners for leveling feet",
    "Rear Shear Wall Panel      1   1/2\" Birch Ply 45.00\" x 29.00\" x 1/2\" SCREWED TO REAR: LOCKS AGAINST RACKING",
    "Center Partition Gable     1   3/4\" Birch Ply 18.00\" x 22.00\" x 3/4\" Separates drawer bank and CR-6 bay",
    "Right Bay CR-6 Shelf       1   3/4\" Birch Ply 18.00\" x 18.625\"x 3/4\" Houses Creality CR-6 SE 3D Printer",
    "Spool Drawer Fronts        2   3/4\" Walnut    8.500\" x 18.375\"x 3/4\" FLUSH MOUNTED; Holds 24 spools upright",
    "Tool Drawer Front          1   3/4\" Walnut    4.500\" x 18.375\"x 3/4\" Tools, nozzles, PEI build plates",
]
page.addView(a_cut)
a_cut.X = 215.0
a_cut.Y = 55.0
a_cut.TextSize = 2.0
grp_drawings.addObject(a_cut)

doc.recompute()
print("  [+] TechDraw shop blueprint sheet updated.")

# =============================================================================
# 12. EXPORT STEP MODEL, DXF BLUEPRINTS & FREECAD DOCUMENT
# =============================================================================
out_dir = "/home/scott/20p/cad/bambu-table"
os.makedirs(out_dir, exist_ok=True)

fcstd_path = os.path.join(out_dir, "bambu_printer_table.FCStd")
doc.saveAs(fcstd_path)
print(f"  [+] Saved FreeCAD project: {fcstd_path}")

step_path = os.path.join(out_dir, "bambu_printer_table.step")
export_parts = [
    obj for obj in doc.Objects
    if hasattr(obj, "Shape") and obj.Shape and obj.Shape.isValid()
    and not obj.isDerivedFrom("Sketcher::SketchObject")
]
Part.export(export_parts, step_path)
print(f"  [+] Universal STEP solid model exported: {step_path} ({len(export_parts)} parts)")

dxf_path = os.path.join(out_dir, "shop_sheet_printer_table.dxf")
try:
    TechDraw.writeDXFPage(page, dxf_path)
    print(f"  [+] Exported TechDraw DXF blueprint: {dxf_path}")
except Exception as e:
    print(f"  [!] Note on DXF export: {e}")

# =============================================================================
# 13. GENERATE UPDATED CUT LIST & BILL OF MATERIALS
# =============================================================================
bom_path = os.path.join(out_dir, "CUT_LIST_AND_BOM.md")
with open(bom_path, "w") as f:
    f.write(f"""# Bambu 3D Printer Stand & Storage Workbench (V3 - L-Shaped Legs)

**Top Surface:** Existing Walnut Desktop ({TOP_WIDTH:.0f}" × {TOP_DEPTH:.0f}" × {TOP_THICKNESS:.0f}")  
**Finished Bench Height:** {TOTAL_HEIGHT:.1f}" (Top surface at chest height for printer bed & AMS)  
**Footprint:** Base Frame {BASE_WIDTH:.1f}" Wide × {BASE_DEPTH:.1f}" Deep (1.5" perimeter top reveal)

---

## 1. Dimensional Lumber (100% SPF 2×4 — Home Depot Canada In-Stock)

All framing is built from standard **2-inch x 4-inch x 8-ft. SPF Premium Stud Lumber** (SKU `1000112108` / Model `112108`, ~$6.50 CAD). **No 4×4 posts and no planer needed!**

### Corner L-Legs (4 Legs = 8 pcs of 2×4)
| Part Name | Qty | Size (T × W × L) | Notes |
| :--- | :---: | :--- | :--- |
| **Front/Rear Leg Flanges** | 4 pcs | 1.5" × 3.5" × {LEG_HEIGHT:.2f}" | Front face of corner column |
| **Side Return Leg Flanges** | 4 pcs | 1.5" × 3.5" × {LEG_HEIGHT:.2f}" | Side return joined at 90° with pocket screws + glue |
| **Corner Foot Blocks** | 4 pcs | 1.5" × 2.0" × 2.0" | Glued in bottom inside corner of each L-leg to mount leveling feet |

### Framing Rails & Stretchers (2×4 Lumber)
| Part Name | Qty | Size (T × W × L) | Notes |
| :--- | :---: | :--- | :--- |
| **Front & Rear Upper Aprons** | 2 pcs | 1.5" × 3.5" × {front_rail_span:.2f}" | Upper perimeter long rails |
| **Side Upper Aprons** | 2 pcs | 1.5" × 3.5" × {side_rail_span:.2f}" | Upper short side rails |
| **Upper Center Cross-Tie** | 1 pc | 1.5" × 3.5" × {center_tie_span:.2f}" | Desktop mid support & divider anchor |
| **Front & Rear Lower Stretchers**| 2 pcs | 1.5" × 3.5" × {front_rail_span:.2f}" | Lower stretchers 1.5" off floor |
| **Side Lower Stretchers**| 2 pcs | 1.5" × 3.5" × {side_rail_span:.2f}" | Lower side stretchers |
| **Lower Center Cross-Tie** | 1 pc | 1.5" × 3.5" × {center_tie_span:.2f}" | Bottom shelf & divider support |

*Total 2×4 Lumber Needed:* **7 standard 8-foot (96") 2×4 studs** (~$45.50 CAD total for the entire solid timber base!).

---

## 2. Hardwood Plywood Project Panels (Columbia Forest Products PureBond)

| Item | Qty | Product Title on Home Depot Canada | Store SKU | Model # | Purpose |
| :--- | :---: | :--- | :---: | :---: | :--- |
| **3/4" Walnut** | 1 | CFP 3/4 in. x 2 ft. x 4 ft. PureBond Walnut Plywood ($54) | Online | — | All 3 drawer fronts (matches desktop) |
| **3/4" Birch** | 1 | CFP 3/4 in. x 2 ft. x 4 ft. PureBond Birch Plywood ($41) | `1001513690` | `4391` | Center divider & CR-6 printer shelf |
| **1/2" Birch** | 1 | CFP 1/2 in. x 2 ft. x 4 ft. PureBond Birch Plywood ($36) | `1001513691` | `4384` | Rear anti-racking shear wall panel |
| **1/2" Birch** | 2 | CFP 1/2 in. x 2 ft. x 4 ft. PureBond Birch Plywood (~$36 ea) | `1001513691` | `4384` | Drawer box front, back, and side walls |
| **1/4" Birch** | 1 | CFP 1/4 in. x 2 ft. x 4 ft. PureBond Birch Plywood (~$28) | `1001513692` | `4377` | Drawer box bottom panels (grooved) |

---

## 3. How the "L-Shaped" 2×4 Leg Joint is Built

```
TOP-DOWN VIEW OF FRONT-LEFT CORNER LEG:

            X = 1.5"             X = 5.0"
            ┌──────────────────────┐  ◄── Piece A (Front Flange: 1.5" x 3.5" x 30")
            │   1.5" x 3.5" 2x4    │
  Y = 3.0"  ├──────────┬───────────┘
            │          │  ◄── Pocket screws drilled on inside face of Piece B into Piece A
            │ Piece B  │      with Titebond II wood glue along the seam!
            │ (Side)   │
  Y = 6.5"  └──────────┘
```

1. **Cut:** Use your miter saw with a stop block to cut eight identical 30.0" pieces of 2×4.
2. **Pocket Holes:** Set your Kreg Jig to the **1-1/2" setting**. Drill 3 pocket holes along the inside face of Piece B facing into the edge of Piece A.
3. **Glue & Assemble:** Apply a bead of Titebond II wood glue along the seam, clamp Piece A and Piece B at 90° using a square, and drive **2-1/2" coarse pocket hole screws**.
4. **Foot Block:** Glue a 2" × 2" scrap 2×4 block in the bottom inside corner of the "L" to hold the 3/8" threaded leveling foot insert.
5. **No Planer Needed:** The factory-flat edge of Piece B butts against the factory-flat face of Piece A. The factory eased edges create a subtle, decorative V-groove reveal along the corner.

---

## 4. Hardware Checklist

- [ ] **Drawer Slides:** 18" Full-Extension Ball-Bearing Slides, 100 lb (Amazon 6-pack for $72)
- [ ] **Drawer Pulls:** 3 pcs modern 5" bar pulls
- [ ] **Leveling Feet:** 4 pcs heavy-duty 3/8"-16 threaded rubber swivel glides + pronged tee-nuts / threaded inserts
- [ ] **Pocket Screws:** 1 box 2-1/2" coarse pocket hole screws (for 2×4 frame & L-legs)
- [ ] **Drawer Screws:** 1 box 1" pocket screws (for 1/2" drawer boxes)
- [ ] **Tabletop Fasteners:** 8 pcs Figure-8 desktop fasteners (use 5/8" or 3/4" Forstner bit)
- [ ] **Wood Glue:** 1 bottle Titebond II
""")

print(f"  [+] Cut list and BOM exported: {bom_path}")
print("=" * 75)
print("  FREECAD MODEL GENERATION (V3) COMPLETED SUCCESSFULLY!")
print("=" * 75)
