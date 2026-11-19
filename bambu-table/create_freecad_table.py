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

# Corner Legs & Vertical Envelope
FOOT_HEIGHT         = 0.50    # Leveling feet clearance off floor
LEG_Z_BOTTOM        = FOOT_HEIGHT                      # 0.50"
LEG_HEIGHT          = BASE_TOP_Z - LEG_Z_BOTTOM        # 30.00" (SPF 2x4 leg length)

# Vertical Rail Positions (Parametric):
# Offset from bottom of wood leg to underside of bottom stretcher:
# 0.00" offset makes bottom rail flush with leg bottom (leaving 23.00" clear opening).
LOWER_RAIL_LEG_OFFSET   = 0.00  # Lower stretchers flush with bottom of 30" wood legs
BOTTOM_RAIL_HEIGHT      = LUMBER_2X4_W                     # 3.50"
BOTTOM_RAIL_Z_BOT       = LEG_Z_BOTTOM + LOWER_RAIL_LEG_OFFSET # 0.50"
BOTTOM_RAIL_Z_TOP       = BOTTOM_RAIL_Z_BOT + BOTTOM_RAIL_HEIGHT # 4.00"

TOP_RAIL_HEIGHT         = LUMBER_2X4_W                     # 3.50"
TOP_RAIL_Z_BOT          = BASE_TOP_Z - TOP_RAIL_HEIGHT     # 27.00"

# Clear Vertical Opening between Upper Apron and Lower Stretcher:
CLEAR_BAY_HEIGHT        = TOP_RAIL_Z_BOT - BOTTOM_RAIL_Z_TOP # 23.00"

# Center Divider Gable (22.00" cut height) & Grooved 2x4 Top Spacer:
DIVIDER_GABLE_HEIGHT    = 22.00   # Pre-cut 3/4" Birch center gable height
GROOVED_SPACER_W        = LUMBER_2X4_W # 3.50" wide (full unripped 2x4 laid flat!)
GROOVED_SPACER_H        = LUMBER_2X4_T # 1.50" tall (2x4 thickness)
GROOVED_SPACER_GROOVE_D = 0.50    # 1/2" deep routed dado groove (leaves 1.00" effective spacer)
GROOVED_SPACER_EFF_H    = GROOVED_SPACER_H - GROOVED_SPACER_GROOVE_D # 1.00"
REAR_TIE_BLOCK_H        = 6.00    # 6.00" tall x 1.50" x 3.50" 2x4 rear tie block behind gable

PLY_SHEAR_THICK         = 0.50    # 1/2" back panel for zero racking
SHEAR_PANEL_HEIGHT      = 24.00   # 24.00" tall (from 24"x48" project panel, mounted flush at top)
PLY_CARCASS_THICK       = 0.75    # 3/4" birch plywood for partition & shelves
DRAWER_REVEAL           = 0.125   # 1/8" gap around drawer fronts
SLIDE_CLEARANCE_SIDE    = 0.50    # 1/2" ball-bearing slide clearance per side (1.00" total)
DRAWER_WALL_THICK       = 0.50    # 1/2" birch plywood drawer box walls
DRAWER_BOTTOM_THICK     = 0.25    # 1/4" birch plywood drawer bottom (screwed flush to underside)
DRAWER_FACE_THICK       = 0.75    # 3/4" walnut plywood drawer faces
DRAWER_SPOOL_FACE_H     = 8.50    # Middle & Bottom spool drawer face height
DRAWER_TOOL_FACE_H      = CLEAR_BAY_HEIGHT - 2 * DRAWER_SPOOL_FACE_H - 4 * DRAWER_REVEAL # 5.50"
DRAWER_SPOOL_BOX_H      = 7.75    # Spool drawer wall height (+ 0.25" bottom = 8.00" total)
DRAWER_TOOL_BOX_H       = 3.50    # Tool drawer wall height (+ 0.25" bottom = 3.75" total)

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
def make_subgroup(name, label, parent):
    sub = doc.addObject("App::DocumentObjectGroup", name)
    sub.Label = label
    parent.addObject(sub)
    return sub

grp_top       = doc.addObject("App::DocumentObjectGroup", "01_Walnut_Tabletop")
grp_top.Label = "01 Walnut Tabletop (24x48x1)"

grp_timber    = doc.addObject("App::DocumentObjectGroup", "02_L_Shaped_2x4_Frame")
grp_timber.Label = "02 L-Shaped 2x4 Legs & Rails"
grp_legs      = make_subgroup("02a_Corner_L_Legs", "02a Corner L-Legs & Foot Blocks", grp_timber)
grp_rails     = make_subgroup("02b_Perimeter_Rails", "02b Aprons, Stretchers & Cross-Ties", grp_timber)
grp_runners   = make_subgroup("02c_Slide_Runners", "02c Left Drawer Slide Runners", grp_timber)

grp_panels    = doc.addObject("App::DocumentObjectGroup", "03_Shear_Panels_and_Shelves")
grp_panels.Label = "03 Shear Back Panel & Partition"

grp_drawers   = doc.addObject("App::DocumentObjectGroup", "04_Articulated_Drawers")
grp_drawers.Label = "04 Drawers & Ball-Bearing Slides"

grp_printers  = doc.addObject("App::DocumentObjectGroup", "05_Equipment_and_Printers")
grp_printers.Label = "05 Printers (Bambu & CR-6) & Dual Dryer"
grp_bambu     = make_subgroup("05a_Bambu_Printer_AMS", "05a Bambu CoreXY & AMS", grp_printers)
grp_cr6       = make_subgroup("05b_Creality_CR6_SE", "05b Creality CR-6 SE", grp_printers)
grp_dryer     = make_subgroup("05c_Dual_Filament_Dryer", "05c Dual-Spool Filament Dryer", grp_printers)

grp_hardware  = doc.addObject("App::DocumentObjectGroup", "06_Hardware_and_Feet")
grp_hardware.Label = "06 Leveling Feet"

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
    if dy > dx and dy >= dz:
        # Board runs front-to-back along Y: orient local X along world Y so Length = dy (e.g. 18.0" or 11.0")
        box.Length = in_to_mm(dy)
        box.Width  = in_to_mm(dx)
        box.Height = in_to_mm(dz)
        box.Placement = FreeCAD.Placement(
            v_in(x + dx, y, z),
            FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), 90)
        )
    else:
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
leg_fl_front = make_box("L_Leg_FL_FrontFlange", grp_legs,
                        OVERHANG_SIDES, OVERHANG_FRONT, LEG_Z_BOTTOM,
                        LUMBER_2X4_W, LUMBER_2X4_T, LEG_HEIGHT,
                        COL_LEG_FLANGE)
leg_fl_side  = make_box("L_Leg_FL_SideReturn", grp_legs,
                        OVERHANG_SIDES, OVERHANG_FRONT + LUMBER_2X4_T, LEG_Z_BOTTOM,
                        LUMBER_2X4_T, LUMBER_2X4_W, LEG_HEIGHT,
                        COL_LEG_RETURN)

# Front-Right L-Leg
leg_fr_front = make_box("L_Leg_FR_FrontFlange", grp_legs,
                        TOP_WIDTH - OVERHANG_SIDES - LUMBER_2X4_W, OVERHANG_FRONT, LEG_Z_BOTTOM,
                        LUMBER_2X4_W, LUMBER_2X4_T, LEG_HEIGHT,
                        COL_LEG_FLANGE)
leg_fr_side  = make_box("L_Leg_FR_SideReturn", grp_legs,
                        TOP_WIDTH - OVERHANG_SIDES - LUMBER_2X4_T, OVERHANG_FRONT + LUMBER_2X4_T, LEG_Z_BOTTOM,
                        LUMBER_2X4_T, LUMBER_2X4_W, LEG_HEIGHT,
                        COL_LEG_RETURN)

# Back-Left L-Leg
leg_bl_rear  = make_box("L_Leg_BL_RearFlange", grp_legs,
                        OVERHANG_SIDES, TOP_DEPTH - OVERHANG_BACK - LUMBER_2X4_T, LEG_Z_BOTTOM,
                        LUMBER_2X4_W, LUMBER_2X4_T, LEG_HEIGHT,
                        COL_LEG_FLANGE)
leg_bl_side  = make_box("L_Leg_BL_SideReturn", grp_legs,
                        OVERHANG_SIDES, TOP_DEPTH - OVERHANG_BACK - LUMBER_2X4_T - LUMBER_2X4_W, LEG_Z_BOTTOM,
                        LUMBER_2X4_T, LUMBER_2X4_W, LEG_HEIGHT,
                        COL_LEG_RETURN)

# Back-Right L-Leg
leg_br_rear  = make_box("L_Leg_BR_RearFlange", grp_legs,
                        TOP_WIDTH - OVERHANG_SIDES - LUMBER_2X4_W, TOP_DEPTH - OVERHANG_BACK - LUMBER_2X4_T, LEG_Z_BOTTOM,
                        LUMBER_2X4_W, LUMBER_2X4_T, LEG_HEIGHT,
                        COL_LEG_FLANGE)
leg_br_side  = make_box("L_Leg_BR_SideReturn", grp_legs,
                        TOP_WIDTH - OVERHANG_SIDES - LUMBER_2X4_T, TOP_DEPTH - OVERHANG_BACK - LUMBER_2X4_T - LUMBER_2X4_W, LEG_Z_BOTTOM,
                        LUMBER_2X4_T, LUMBER_2X4_W, LEG_HEIGHT,
                        COL_LEG_RETURN)

# Foot Base Blocks (Actual installed 2.00" x 2.00" x 1.50" blocks at Z=0.50" to 2.00" housing leveling feet)
foot_block_size = 2.00
foot_block_h    = 1.50
foot_fl = make_box("L_Leg_FL_FootBlock", grp_legs,
                   OVERHANG_SIDES + LUMBER_2X4_T, OVERHANG_FRONT + LUMBER_2X4_T, LEG_Z_BOTTOM,
                   foot_block_size, foot_block_size, foot_block_h,
                   COL_PINE_RAILS)
foot_fr = make_box("L_Leg_FR_FootBlock", grp_legs,
                   TOP_WIDTH - OVERHANG_SIDES - LUMBER_2X4_W, OVERHANG_FRONT + LUMBER_2X4_T, LEG_Z_BOTTOM,
                   foot_block_size, foot_block_size, foot_block_h,
                   COL_PINE_RAILS)
foot_bl = make_box("L_Leg_BL_FootBlock", grp_legs,
                   OVERHANG_SIDES + LUMBER_2X4_T, TOP_DEPTH - OVERHANG_BACK - LUMBER_2X4_T - foot_block_size, LEG_Z_BOTTOM,
                   foot_block_size, foot_block_size, foot_block_h,
                   COL_PINE_RAILS)
foot_br = make_box("L_Leg_BR_FootBlock", grp_legs,
                   TOP_WIDTH - OVERHANG_SIDES - LUMBER_2X4_W, TOP_DEPTH - OVERHANG_BACK - LUMBER_2X4_T - foot_block_size, LEG_Z_BOTTOM,
                   foot_block_size, foot_block_size, foot_block_h,
                   COL_PINE_RAILS)

# Optional Upper Buttress Caps (4x unripped 2.00" crosscuts of 2x4: 1.50" W x 3.50" D x 2.00" H)
# Sits directly on top of the 1.50" foot blocks (Z=2.00" to 4.00", flush with Lower Stretchers)
COL_FOOT_BLOCK = (0.76, 0.55, 0.34)
buttress_w     = LUMBER_2X4_T                              # 1.50"
buttress_d     = LUMBER_2X4_W                              # 3.50"
buttress_h     = BOTTOM_RAIL_HEIGHT - foot_block_h         # 3.50 - 1.50 = 2.00"
buttress_z     = LEG_Z_BOTTOM + foot_block_h               # 2.00"

buttress_fl = make_box("L_Leg_FL_UpperButtress", grp_legs,
                       OVERHANG_SIDES + LUMBER_2X4_T, OVERHANG_FRONT + LUMBER_2X4_T, buttress_z,
                       buttress_w, buttress_d, buttress_h, COL_FOOT_BLOCK)
buttress_fr = make_box("L_Leg_FR_UpperButtress", grp_legs,
                       TOP_WIDTH - OVERHANG_SIDES - 2 * LUMBER_2X4_T, OVERHANG_FRONT + LUMBER_2X4_T, buttress_z,
                       buttress_w, buttress_d, buttress_h, COL_FOOT_BLOCK)
buttress_bl = make_box("L_Leg_BL_UpperButtress", grp_legs,
                       OVERHANG_SIDES + LUMBER_2X4_T, TOP_DEPTH - OVERHANG_BACK - LUMBER_2X4_T - buttress_d, buttress_z,
                       buttress_w, buttress_d, buttress_h, COL_FOOT_BLOCK)
buttress_br = make_box("L_Leg_BR_UpperButtress", grp_legs,
                       TOP_WIDTH - OVERHANG_SIDES - 2 * LUMBER_2X4_T, TOP_DEPTH - OVERHANG_BACK - LUMBER_2X4_T - buttress_d, buttress_z,
                       buttress_w, buttress_d, buttress_h, COL_FOOT_BLOCK)

# Upper Aprons (Top Rails, 2x4: 1.5" x 3.5")
# Front & Rear aprons span 38.00" between the front leg flanges:
apron_front = make_box("Upper_Apron_Front", grp_rails,
                       OVERHANG_SIDES + LUMBER_2X4_W, OVERHANG_FRONT, TOP_RAIL_Z_BOT,
                       front_rail_span, LUMBER_2X4_T, TOP_RAIL_HEIGHT,
                       COL_PINE_RAILS)

apron_back = make_box("Upper_Apron_Back", grp_rails,
                      OVERHANG_SIDES + LUMBER_2X4_W, TOP_DEPTH - OVERHANG_BACK - LUMBER_2X4_T, TOP_RAIL_Z_BOT,
                      front_rail_span, LUMBER_2X4_T, TOP_RAIL_HEIGHT,
                      COL_PINE_RAILS)

# Side aprons span 11.00" between the front & rear side return flanges:
apron_left = make_box("Upper_Apron_Left", grp_rails,
                      OVERHANG_SIDES, OVERHANG_FRONT + LUMBER_2X4_T + LUMBER_2X4_W, TOP_RAIL_Z_BOT,
                      LUMBER_2X4_T, side_rail_span, TOP_RAIL_HEIGHT,
                      COL_PINE_RAILS)

apron_right = make_box("Upper_Apron_Right", grp_rails,
                       TOP_WIDTH - OVERHANG_SIDES - LUMBER_2X4_T, OVERHANG_FRONT + LUMBER_2X4_T + LUMBER_2X4_W, TOP_RAIL_Z_BOT,
                       LUMBER_2X4_T, side_rail_span, TOP_RAIL_HEIGHT,
                       COL_PINE_RAILS)

# Upper Center Cross-Tie (18.00" long)
apron_mid = make_box("Upper_Cross_Tie_Mid", grp_rails,
                     (TOP_WIDTH - LUMBER_2X4_T) / 2.0, OVERHANG_FRONT + LUMBER_2X4_T, TOP_RAIL_Z_BOT,
                     LUMBER_2X4_T, center_tie_span, TOP_RAIL_HEIGHT,
                     COL_PINE_RAILS)

# Lower Stretchers (Bottom Rails, 2x4: 1.5" x 3.5", at Z = 0.50")
stretcher_front = make_box("Lower_Stretcher_Front", grp_rails,
                           OVERHANG_SIDES + LUMBER_2X4_W, OVERHANG_FRONT, BOTTOM_RAIL_Z_BOT,
                           front_rail_span, LUMBER_2X4_T, BOTTOM_RAIL_HEIGHT,
                           COL_PINE_RAILS)

stretcher_back = make_box("Lower_Stretcher_Back", grp_rails,
                          OVERHANG_SIDES + LUMBER_2X4_W, TOP_DEPTH - OVERHANG_BACK - LUMBER_2X4_T, BOTTOM_RAIL_Z_BOT,
                          front_rail_span, LUMBER_2X4_T, BOTTOM_RAIL_HEIGHT,
                          COL_PINE_RAILS)

stretcher_left = make_box("Lower_Stretcher_Left", grp_rails,
                          OVERHANG_SIDES, OVERHANG_FRONT + LUMBER_2X4_T + LUMBER_2X4_W, BOTTOM_RAIL_Z_BOT,
                          LUMBER_2X4_T, side_rail_span, BOTTOM_RAIL_HEIGHT,
                          COL_PINE_RAILS)

stretcher_right = make_box("Lower_Stretcher_Right", grp_rails,
                           TOP_WIDTH - OVERHANG_SIDES - LUMBER_2X4_T, OVERHANG_FRONT + LUMBER_2X4_T + LUMBER_2X4_W, BOTTOM_RAIL_Z_BOT,
                           LUMBER_2X4_T, side_rail_span, BOTTOM_RAIL_HEIGHT,
                           COL_PINE_RAILS)

stretcher_mid = make_box("Lower_Cross_Tie_Mid", grp_rails,
                         (TOP_WIDTH - LUMBER_2X4_T) / 2.0, OVERHANG_FRONT + LUMBER_2X4_T, BOTTOM_RAIL_Z_BOT,
                         LUMBER_2X4_T, center_tie_span, BOTTOM_RAIL_HEIGHT,
                         COL_PINE_RAILS)

# =============================================================================
# 5. GROUP 03: ANTI-RACKING SHEAR WALL, GROOVED SPACER & PARTITION
# =============================================================================
print("  [*] Modeling Shear Wall Back Panel, Grooved Top Spacer & Center Partition...")

# 1/2" Plywood Rear Shear Panel (45.00" W x 24.00" H, mounted flush with top of Upper Rear Apron)
shear_panel_z_bot = BASE_TOP_Z - SHEAR_PANEL_HEIGHT # 30.50 - 24.00 = 6.50"
shear_panel = make_box("Back_Shear_Wall_Panel", grp_panels,
                       OVERHANG_SIDES, TOP_DEPTH - OVERHANG_BACK, shear_panel_z_bot,
                       BASE_WIDTH, PLY_SHEAR_THICK, SHEAR_PANEL_HEIGHT,
                       COL_PLY_BIRCH)

# Center Partition (3/4" Birch Plywood, 22.00" H x 18.00" D)
# Sits on Lower Center Cross-Tie (Z = 4.00") and nests 0.50" up into the Grooved 2x4 Top Spacer (to Z = 26.00")
divider_height = DIVIDER_GABLE_HEIGHT                 # 22.00"
divider_depth  = center_tie_span                      # 18.00"
divider_x      = (TOP_WIDTH - PLY_CARCASS_THICK) / 2.0 # 23.625"

divider = make_box("Center_Divider_Gable", grp_panels,
                   divider_x, OVERHANG_FRONT + LUMBER_2X4_T, BOTTOM_RAIL_Z_TOP,
                   PLY_CARCASS_THICK, divider_depth, divider_height,
                   COL_PLY_BIRCH)

# Grooved 2x4 Top Spacer Block (Full 2x4 laid flat: 3.50" W x 1.50" H x 18.00" L with 3/4" W x 1/2" D dado groove)
spacer_x = (TOP_WIDTH - GROOVED_SPACER_W) / 2.0       # 22.25" to 25.75" (centered at X = 24.00")
spacer_y = OVERHANG_FRONT + LUMBER_2X4_T              # 3.00" to 21.00" (18.00" long)
spacer_z = TOP_RAIL_Z_BOT - GROOVED_SPACER_H          # 25.50" to 27.00" (1.50" thick)

spacer_blank = doc.addObject("Part::Box", "Spacer_2x4_Blank")
spacer_blank.Length = in_to_mm(divider_depth)         # 18.00" Length
spacer_blank.Width  = in_to_mm(GROOVED_SPACER_W)      # 3.50" Width
spacer_blank.Height = in_to_mm(GROOVED_SPACER_H)      # 1.50" Height
spacer_blank.Placement = FreeCAD.Placement(
    v_in(spacer_x + GROOVED_SPACER_W, spacer_y, spacer_z),
    FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), 90)
)

spacer_dado = doc.addObject("Part::Box", "Spacer_Dado_Groove")
spacer_dado.Length = in_to_mm(divider_depth)          # 18.00" Length
spacer_dado.Width  = in_to_mm(PLY_CARCASS_THICK)      # 0.75" Groove Width
spacer_dado.Height = in_to_mm(GROOVED_SPACER_GROOVE_D)# 0.50" Groove Depth
spacer_dado.Placement = FreeCAD.Placement(
    v_in(divider_x + PLY_CARCASS_THICK, spacer_y, spacer_z),
    FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), 90)
)

grooved_spacer = doc.addObject("Part::Cut", "Center_Gable_Grooved_Spacer")
grooved_spacer.Base = spacer_blank
grooved_spacer.Tool = spacer_dado
grp_rails.addObject(grooved_spacer)
set_style(grooved_spacer, COL_PINE_RAILS)

# Rear Tie Block (Full 2x4 offcut: 3.50" W x 1.50" D x 6.00" H bridging 1.50" gap between Center Gable and Rear Shear Wall)
rear_tie_z = BOTTOM_RAIL_Z_TOP + (divider_height - REAR_TIE_BLOCK_H) / 2.0
rear_tie_block = make_box("Center_Gable_Rear_Tie_Block", grp_rails,
                          spacer_x, TOP_DEPTH - OVERHANG_BACK - LUMBER_2X4_T, rear_tie_z,
                          LUMBER_2X4_W, LUMBER_2X4_T, REAR_TIE_BLOCK_H,
                          COL_PINE_RAILS)

# Bay Dimensions:
# Front rail span = 38.00". Minus 0.75" divider = 37.25" total clear width.
# Left Bay clear width = 18.625" (473 mm)
# Right Bay clear width = 18.625" (473 mm)
bay_width = (front_rail_span - PLY_CARCASS_THICK) / 2.0 # 18.625"

# Left Bay 2x4 Horizontal Slide Runners (3 pcs: 1.50" T x 3.50" H, with inside face flush at X = 5.00")
# Mounted against Left Side Return Flanges with 1/2" Birch shims (X = 3.00" to 3.50")
left_runner_x = OVERHANG_SIDES + LUMBER_2X4_W - LUMBER_2X4_T # 1.50 + 3.50 - 1.50 = 3.50" (inside face at 5.00")
left_runner_y = OVERHANG_FRONT + LUMBER_2X4_T                # 3.00"
runner_len    = 16.00                                        # Matches user's ~16" offcuts butted to front
tier_pitch    = DRAWER_SPOOL_FACE_H + DRAWER_REVEAL          # 8.625" (8-5/8")

left_runner_bot = make_box("Left_Slide_Runner_Bot", grp_runners,
                           left_runner_x, left_runner_y, BOTTOM_RAIL_Z_TOP,
                           LUMBER_2X4_T, runner_len, LUMBER_2X4_W, COL_PINE_RAILS)
left_runner_mid = make_box("Left_Slide_Runner_Mid", grp_runners,
                           left_runner_x, left_runner_y, BOTTOM_RAIL_Z_TOP + tier_pitch - 0.625,
                           LUMBER_2X4_T, runner_len, LUMBER_2X4_W, COL_PINE_RAILS)
left_runner_top = make_box("Left_Slide_Runner_Top", grp_runners,
                           left_runner_x, left_runner_y, BOTTOM_RAIL_Z_TOP + 2 * tier_pitch - 0.625,
                           LUMBER_2X4_T, runner_len, LUMBER_2X4_W, COL_PINE_RAILS)

# Right Bay Lower Heavy Equipment Shelf (Supports Creality CR-6 SE)
right_bay_x0 = divider_x + PLY_CARCASS_THICK # 24.375"
shelf_cr6 = make_box("Right_Bay_CR6_Shelf", grp_panels,
                     right_bay_x0, OVERHANG_FRONT + LUMBER_2X4_T, BOTTOM_RAIL_Z_TOP,
                     bay_width, divider_depth, PLY_CARCASS_THICK,
                     COL_PLY_BIRCH)

# CR-6 Shelf 3/4" Birch Plywood Support Cleats (Uses leftover 18.00" x 2.00" x 3/4" Birch offcuts!)
# Screwed flat against the inside faces of the Front and Rear Lower Stretchers in the Right Bay
CR6_CLEAT_LEN = center_tie_span   # 18.00" long (from leftover 3/4" Birch ply offcuts)
CR6_CLEAT_H   = 2.00              # 2.00" tall
CR6_CLEAT_T   = PLY_CARCASS_THICK # 0.75" thick (3/4" Birch plywood)
cleat_cr6_x   = right_bay_x0 + (bay_width - CR6_CLEAT_LEN) / 2.0 # Centered in 18.625" right bay

cleat_cr6_front = make_box("CR6_Shelf_Cleat_Front", grp_panels,
                           cleat_cr6_x, OVERHANG_FRONT + LUMBER_2X4_T, BOTTOM_RAIL_Z_TOP - CR6_CLEAT_H,
                           CR6_CLEAT_LEN, CR6_CLEAT_T, CR6_CLEAT_H, COL_PLY_BIRCH)
cleat_cr6_back  = make_box("CR6_Shelf_Cleat_Back", grp_panels,
                           cleat_cr6_x, TOP_DEPTH - OVERHANG_BACK - LUMBER_2X4_T - CR6_CLEAT_T, BOTTOM_RAIL_Z_TOP - CR6_CLEAT_H,
                           CR6_CLEAT_LEN, CR6_CLEAT_T, CR6_CLEAT_H, COL_PLY_BIRCH)

# =============================================================================
# 6. GROUP 04: ARTICULATED DRAWERS & BALL-BEARING SLIDES (LEFT BAY)
# =============================================================================
print("  [*] Modeling Articulated Drawers with Ball-Bearing Slides (Left Bay)...")

ACTUAL_DRAWER_BAY_W  = 18.500                                            # User-measured clear opening between runners & gable
left_bay_x0          = OVERHANG_SIDES + LUMBER_2X4_W                     # 5.000"
drawer_box_w         = ACTUAL_DRAWER_BAY_W - 2 * SLIDE_CLEARANCE_SIDE    # 17.500" outside box width
drawer_subpanel_w    = drawer_box_w - 2 * DRAWER_WALL_THICK              # 16.500" front/back sub-panel width
drawer_bottom_w      = drawer_box_w - 0.125                              # 17.375" (1/16" shy per side)
drawer_bottom_d      = center_tie_span - 0.125                           # 17.875" (1/16" shy front/back)
drawer_box_d         = center_tie_span                                   # 18.00" deep
drawer_box_x         = left_bay_x0 + SLIDE_CLEARANCE_SIDE                # 5.500"
drawer_face_w        = ACTUAL_DRAWER_BAY_W - 2 * DRAWER_REVEAL           # 18.250"
drawer_face_x        = left_bay_x0 + DRAWER_REVEAL                       # 5.125"
drawer_face_t        = DRAWER_FACE_THICK                                 # 0.75" Walnut front

# Closed drawer box aligns with the 18.00" slides and 18.00" center gable (Y = 3.00" to 21.00")
# Closed 3/4" Walnut drawer face sits directly against box front (Y = 2.25" to 3.00", inset in 2x4 frame)
drawer_closed_box_y  = OVERHANG_FRONT + LUMBER_2X4_T                    # 3.00"
drawer_closed_face_y = drawer_closed_box_y - drawer_face_t              # 2.25"

drawer_specs = [
    ("Drawer_03_Bottom_Spools", DRAWER_SPOOL_BOX_H, DRAWER_SPOOL_FACE_H, DRAWER_REVEAL, False, 0.0, DRAWER_BOTTOM_THICK),
    ("Drawer_02_Middle_Spools", DRAWER_SPOOL_BOX_H, DRAWER_SPOOL_FACE_H, DRAWER_SPOOL_FACE_H + 2 * DRAWER_REVEAL, True, 10.0, DRAWER_BOTTOM_THICK), # EXTENDED 10" FORWARD!
    ("Drawer_01_Top_Tools",     DRAWER_TOOL_BOX_H,  DRAWER_TOOL_FACE_H,  2 * DRAWER_SPOOL_FACE_H + 3 * DRAWER_REVEAL, False, 0.0, DRAWER_WALL_THICK), # 1/2" bottom from Sheet #2 leftover
]

for dname, box_h, face_h, z_rel, is_ext, ext_dist, bot_t in drawer_specs:
    d_label = dname.replace("_", " ") + (" (Extended)" if is_ext else "")
    grp_d = make_subgroup(dname, d_label, grp_drawers)

    cur_z = BOTTOM_RAIL_Z_TOP + z_rel
    cur_face_y = drawer_closed_face_y - ext_dist
    cur_box_y  = drawer_closed_box_y - ext_dist
    
    # 1. Drawer Front Face (Mounted flush to box front)
    face = make_box(f"{dname}_Face", grp_d,
                    drawer_face_x, cur_face_y, cur_z,
                    drawer_face_w, drawer_face_t, face_h,
                    COL_WALNUT)
    
    # 2. Drawer Box (5 individual plywood panels with true butt joints)
    # 2a. Bottom Panel (1/4" Birch on Spool drawers, 1/2" Birch on Top Tool drawer)
    box_bot_z = cur_z + DRAWER_BOTTOM_THICK
    wall_z    = box_bot_z + bot_t
    box_bottom = make_box(f"{dname}_Box_Bottom", grp_d,
                          drawer_box_x + (drawer_box_w - drawer_bottom_w) / 2.0,
                          cur_box_y + (drawer_box_d - drawer_bottom_d) / 2.0,
                          box_bot_z,
                          drawer_bottom_w, drawer_bottom_d, bot_t,
                          COL_PLY_BIRCH)

    # 2b. Left & Right 1/2" Birch Side Walls (full 18.00" depth; Front & Back sit BETWEEN them)
    box_side_l = make_box(f"{dname}_Box_Side_L", grp_d,
                          drawer_box_x, cur_box_y, wall_z,
                          DRAWER_WALL_THICK, drawer_box_d, box_h,
                          COL_PLY_BIRCH)
    box_side_r = make_box(f"{dname}_Box_Side_R", grp_d,
                          drawer_box_x + drawer_box_w - DRAWER_WALL_THICK, cur_box_y, wall_z,
                          DRAWER_WALL_THICK, drawer_box_d, box_h,
                          COL_PLY_BIRCH)

    # 2c. Front & Back 1/2" Birch Sub-Panels (16.500" wide, butt-jointed between Side_L & Side_R)
    box_front = make_box(f"{dname}_Box_Front", grp_d,
                         drawer_box_x + DRAWER_WALL_THICK, cur_box_y, wall_z,
                         drawer_subpanel_w, DRAWER_WALL_THICK, box_h,
                         COL_PLY_BIRCH)
    box_back  = make_box(f"{dname}_Box_Back", grp_d,
                         drawer_box_x + DRAWER_WALL_THICK, cur_box_y + drawer_box_d - DRAWER_WALL_THICK, wall_z,
                         drawer_subpanel_w, DRAWER_WALL_THICK, box_h,
                         COL_PLY_BIRCH)
    
    # 3. Handle / Bar Pull on Drawer Face
    h_len = 5.00
    h_h   = 0.50
    h_d   = 0.75
    h_x   = drawer_face_x + (drawer_face_w - h_len) / 2.0
    h_y   = cur_face_y - h_d
    h_z   = cur_z + (face_h - h_h) / 2.0
    handle = make_box(f"{dname}_Handle", grp_d,
                      h_x, h_y, h_z,
                      h_len, h_d, h_h,
                      COL_STEEL_DARK)
    
    # 4. Ball-Bearing Drawer Slides (Left & Right, 1/4" standoff from bottom of box)
    slide_thick = 0.45
    slide_h     = 1.75
    slide_z     = cur_z + DRAWER_BOTTOM_THICK
    
    # Outer Carcass Member (Fixed to left 2x4 runner & center partition)
    fixed_left = make_box(f"{dname}_Slide_Fixed_L", grp_d,
                          drawer_box_x - slide_thick, drawer_closed_box_y, slide_z,
                          slide_thick, drawer_box_d, slide_h,
                          COL_SLIDE_ZINC)
    fixed_right = make_box(f"{dname}_Slide_Fixed_R", grp_d,
                           drawer_box_x + drawer_box_w, drawer_closed_box_y, slide_z,
                           slide_thick, drawer_box_d, slide_h,
                           COL_SLIDE_ZINC)
    
    # Inner Drawer Member (Attached to box, extends with the drawer)
    ext_rail_l = make_box(f"{dname}_Slide_Ext_L", grp_d,
                          drawer_box_x - slide_thick * 0.7, cur_box_y, slide_z + 0.25,
                          slide_thick * 0.6, drawer_box_d, slide_h - 0.5,
                          COL_CHROME)
    ext_rail_r = make_box(f"{dname}_Slide_Ext_R", grp_d,
                          drawer_box_x + drawer_box_w + slide_thick * 0.1, cur_box_y, slide_z + 0.25,
                          slide_thick * 0.6, drawer_box_d, slide_h - 0.5,
                          COL_CHROME)
    
    if is_ext:
        # 12 Upright 1kg Filament Spools loaded inside!
        grp_spools = make_subgroup(f"{dname}_Spools", "12x Filament Spools", grp_d)
        spool_r = 7.87 / 2.0
        spool_w = 2.56
        spool_z = cur_z + 2 * DRAWER_BOTTOM_THICK + spool_r
        for row_idx, row_y in enumerate([cur_box_y + 4.5, cur_box_y + 12.5]):
            for col_idx in range(6):
                spool_x = drawer_box_x + 1.0 + col_idx * 2.65
                col = COL_SPOOL_PLA if (row_idx + col_idx) % 2 == 0 else COL_SPOOL_PETG
                make_cylinder(f"Drawer_Spool_R{row_idx}_C{col_idx}", grp_spools,
                              spool_x, row_y, spool_z,
                              spool_r, spool_w, col, axis=(1, 0, 0))

# =============================================================================
# 7. GROUP 05: CREALITY CR-6 SE PRINTER (ON LOWER RIGHT SHELF)
# =============================================================================
print("  [*] Modeling Creality CR-6 SE 3D Printer inside Right Bay...")
cr6_base_w = 11.80
cr6_base_d = 15.00
cr6_base_h = 2.36
cr6_x = right_bay_x0 + (bay_width - cr6_base_w) / 2.0
cr6_y = OVERHANG_FRONT + LUMBER_2X4_T + 1.50
cr6_z = BOTTOM_RAIL_Z_TOP + PLY_CARCASS_THICK

cr6_base = make_box("CR6_Base_Chassis", grp_cr6,
                    cr6_x, cr6_y, cr6_z,
                    cr6_base_w, cr6_base_d, cr6_base_h,
                    COL_CR6_ALUM)

bed_size = 9.25
cr6_bed = make_box("CR6_Glass_Print_Bed", grp_cr6,
                   cr6_x + (cr6_base_w - bed_size) / 2.0, cr6_y + (cr6_base_d - bed_size) / 2.0, cr6_z + cr6_base_h,
                   bed_size, bed_size, 0.25,
                   COL_CR6_BED)

tower_w = 1.57
tower_d = 1.57
tower_h = 16.50
cr6_tower_l = make_box("CR6_Z_Tower_Left", grp_cr6,
                       cr6_x + 0.5, cr6_y + 4.5, cr6_z + cr6_base_h,
                       tower_w, tower_d, tower_h,
                       COL_CR6_ALUM)

cr6_tower_r = make_box("CR6_Z_Tower_Right", grp_cr6,
                       cr6_x + cr6_base_w - tower_w - 0.5, cr6_y + 4.5, cr6_z + cr6_base_h,
                       tower_w, tower_d, tower_h,
                       COL_CR6_ALUM)

cr6_top_bar = make_box("CR6_Gantry_Top_Crossbar", grp_cr6,
                       cr6_x + 0.5, cr6_y + 4.5, cr6_z + cr6_base_h + tower_h,
                       cr6_base_w - 1.0, tower_d, 0.80,
                       COL_CR6_ALUM)

cr6_hotend = make_box("CR6_Printhead_Carriage", grp_cr6,
                      cr6_x + cr6_base_w / 2.0 - 1.25, cr6_y + 4.0, cr6_z + cr6_base_h + 7.0,
                      2.50, 2.50, 2.50,
                      (0.15, 0.50, 0.85))

cr6_screen = make_box("CR6_Touchscreen_Display", grp_cr6,
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

dryer_base = make_box("Dryer_Heating_Base", grp_dryer,
                      dryer_x, dryer_y, dryer_z,
                      dryer_w, dryer_d, dryer_h_base,
                      COL_DRYER_BASE)

dryer_screen = make_box("Dryer_LCD_Display", grp_dryer,
                        dryer_x + (dryer_w - 3.5) / 2.0, dryer_y - 0.05, dryer_z + 0.5,
                        3.50, 0.10, 1.50,
                        (0.05, 0.05, 0.05))

dryer_dome = make_box("Dryer_Transparent_Lid", grp_dryer,
                      dryer_x + 0.2, dryer_y + 0.2, dryer_z + dryer_h_base,
                      dryer_w - 0.4, dryer_d - 0.4, dryer_h_dome,
                      COL_DRYER_DOME, transparency=60)

dry_spool_r = 7.87 / 2.0
dry_spool_w = 2.56
spool_1_x = dryer_x + 1.2
spool_2_x = dryer_x + 5.2
dry_spool_y = dryer_y + dryer_d / 2.0
dry_spool_z = dryer_z + dryer_h_base + dry_spool_r + 0.2

make_cylinder("Dryer_Spool_1", grp_dryer,
              spool_1_x, dry_spool_y, dry_spool_z,
              dry_spool_r, dry_spool_w, COL_SPOOL_PLA, axis=(1, 0, 0))

make_cylinder("Dryer_Spool_2", grp_dryer,
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

printer_body = make_box("Bambu_Printer_Chassis", grp_bambu,
                        p_x, p_y, p_z,
                        p_w, p_d, p_h,
                        COL_BAMBU_BODY)

printer_door = make_box("Bambu_Printer_Glass_Door", grp_bambu,
                        p_x + 0.5, p_y - 0.15, p_z + 1.0,
                        p_w - 1.0, 0.15, p_h - 2.0,
                        (0.70, 0.85, 0.95), transparency=50)

ams_w = 14.50
ams_d = 11.10
ams_h = 8.80
ams_x = p_x + (p_w - ams_w) / 2.0
ams_y = p_y + (p_d - ams_d) / 2.0
ams_z = p_z + p_h

ams_unit = make_box("Bambu_AMS_Unit", grp_bambu,
                    ams_x, ams_y, ams_z,
                    ams_w, ams_d, ams_h,
                    (0.85, 0.88, 0.90), transparency=35)

# =============================================================================
# 10. GROUP 06: LEVELING FEET (CENTERED ON 2.0"x2.0" FOOT BLOCKS)
# =============================================================================
print("  [*] Modeling Heavy-Duty Vibration Dampening Leveling Feet...")
foot_offset = OVERHANG_SIDES + LUMBER_2X4_T + foot_block_size / 2.0 # 1.50 + 1.50 + 1.00 = 4.00"
leg_centers = [
    ("FL", foot_offset, foot_offset),
    ("FR", TOP_WIDTH - foot_offset, foot_offset),
    ("BL", foot_offset, TOP_DEPTH - foot_offset),
    ("BR", TOP_WIDTH - foot_offset, TOP_DEPTH - foot_offset),
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
    shear_panel, divider, grooved_spacer, rear_tie_block,
    left_runner_bot, left_runner_mid, left_runner_top,
    shelf_cr6, cleat_cr6_front, cleat_cr6_back,
    doc.getObject("Drawer_01_Top_Tools_Face"),
    doc.getObject("Drawer_01_Top_Tools_Box_Bottom"),
    doc.getObject("Drawer_01_Top_Tools_Box_Side_L"),
    doc.getObject("Drawer_01_Top_Tools_Box_Side_R"),
    doc.getObject("Drawer_01_Top_Tools_Box_Front"),
    doc.getObject("Drawer_01_Top_Tools_Box_Back"),
    doc.getObject("Drawer_01_Top_Tools_Slide_Fixed_L"),
    doc.getObject("Drawer_01_Top_Tools_Slide_Fixed_R"),
    doc.getObject("Drawer_02_Middle_Spools_Face"),
    doc.getObject("Drawer_02_Middle_Spools_Box_Bottom"),
    doc.getObject("Drawer_02_Middle_Spools_Box_Side_L"),
    doc.getObject("Drawer_02_Middle_Spools_Box_Side_R"),
    doc.getObject("Drawer_02_Middle_Spools_Box_Front"),
    doc.getObject("Drawer_02_Middle_Spools_Box_Back"),
    doc.getObject("Drawer_02_Middle_Spools_Slide_Fixed_L"),
    doc.getObject("Drawer_02_Middle_Spools_Slide_Fixed_R"),
    doc.getObject("Drawer_02_Middle_Spools_Slide_Ext_L"),
    doc.getObject("Drawer_02_Middle_Spools_Slide_Ext_R"),
    doc.getObject("Drawer_03_Bottom_Spools_Face"),
    doc.getObject("Drawer_03_Bottom_Spools_Box_Bottom"),
    doc.getObject("Drawer_03_Bottom_Spools_Box_Side_L"),
    doc.getObject("Drawer_03_Bottom_Spools_Box_Side_R"),
    doc.getObject("Drawer_03_Bottom_Spools_Box_Front"),
    doc.getObject("Drawer_03_Bottom_Spools_Box_Back"),
    doc.getObject("Drawer_03_Bottom_Spools_Slide_Fixed_L"),
    doc.getObject("Drawer_03_Bottom_Spools_Slide_Fixed_R"),
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
    "Front/Back Lower Rails     2   2x4 SPF Lumber 1.50\" x 3.50\" x 38.00\" Lower stretchers flush with leg bottom",
    "Side Lower Rails           2   2x4 SPF Lumber 1.50\" x 3.50\" x 11.00\" Lower side stretchers",
    "Lower Center Cross-Tie     1   2x4 SPF Lumber 1.50\" x 3.50\" x 18.00\" Bottom shelf & divider support",
    "Grooved Gable Top Spacer   1   2x4 SPF Lumber 1.50\" x 3.50\" x 18.00\" 3/4\"W x 1/2\"D dado groove (1\" spacer)",
    "Left Slide 2x4 Runners     3   2x4 SPF Lumber 1.50\" x 3.50\" x 16.00\" Flush at X=5.00\" (w/ 1/2\" shims) for left slides",
    "Foot Corner Mount Blocks   4   2x4 Scrap      1.50\" x 2.00\" x 2.00\"  Glued in L-corners for leveling feet",
    "Rear Shear Wall Panel      1   1/2\" Birch Ply 45.00\" x 24.00\" x 1/2\" Flush at top; stops CoreXY racking",
    "Center Partition Gable     1   3/4\" Birch Ply 18.00\" x 22.00\" x 3/4\" Nests 1/2\" into grooved top spacer",
    "Right Bay CR-6 Shelf       1   3/4\" Birch Ply 18.00\" x 18.625\"x 3/4\" Houses Creality CR-6 SE 3D Printer",
    "Spool Drawer Fronts        2   3/4\" Walnut    8.500\" x 18.250\"x 3/4\" FLUSH MOUNTED; Holds 24 spools upright",
    "Tool Drawer Front          1   3/4\" Walnut    5.500\" x 18.250\"x 3/4\" Fills 23.0\" opening with 1/8\" reveals",
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

try:
    import FreeCADGui
    gdoc = FreeCADGui.getDocument(doc.Name) if hasattr(FreeCADGui, "getDocument") else None
    if gdoc:
        for obj in doc.Objects:
            vobj = gdoc.getObject(obj.Name)
            if vobj:
                if (
                    obj.isDerivedFrom("TechDraw::DrawPage")
                    or obj.isDerivedFrom("TechDraw::DrawView")
                    or obj.Name in ("Spacer_2x4_Blank", "Spacer_Dado_Groove")
                ):
                    vobj.Visibility = False
                else:
                    vobj.Visibility = True
        view = gdoc.ActiveView
        if view:
            view.viewAxometric()
            view.fitAll()
        doc.save()
        print("  [+] Native FreeCAD GUI document configured with Axonometric view and full visibility.")
except Exception as e:
    print(f"  [!] Note on GUI view: {e}")

step_path = os.path.join(out_dir, "bambu_printer_table.step")
export_parts = [
    obj for obj in doc.Objects
    if hasattr(obj, "Shape") and obj.Shape and obj.Shape.isValid()
    and not obj.isDerivedFrom("Sketcher::SketchObject")
    and obj.Name not in ("Spacer_2x4_Blank", "Spacer_Dado_Groove")
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
**Interior Bay Opening:** {bay_width:.3f}" Wide × {CLEAR_BAY_HEIGHT:.2f}" High × {center_tie_span:.2f}" Deep

---

## 1. Dimensional Lumber (100% SPF 2×4 — Home Depot Canada In-Stock)

All framing is built from standard **2-inch x 4-inch x 8-ft. SPF Premium Stud Lumber** (SKU `1000112108` / Model `112108`, ~$6.50 CAD). **No 4×4 posts and no planer needed!**

### Corner L-Legs (4 Legs = 8 pcs of 2×4)
| Part Name | Qty | Size (T × W × L) | Notes |
| :--- | :---: | :--- | :--- |
| **Front/Rear Leg Flanges** | 4 pcs | 1.50" × 3.50" × {LEG_HEIGHT:.2f}" | Front/rear face of corner column |
| **Side Return Leg Flanges** | 4 pcs | 1.50" × 3.50" × {LEG_HEIGHT:.2f}" | Side return joined at 90° with pocket screws + glue |
| **Corner Foot Blocks** | 4 pcs | 1.50" × 2.00" × 2.00" | Glued & screwed in bottom inside corner; center-drilled for 3/8" insert |

### Framing Rails, Stretchers & Interior Blocking (2×4 Lumber)
| Part Name | Qty | Size (T × W × L) | Notes |
| :--- | :---: | :--- | :--- |
| **Front & Rear Upper Aprons** | 2 pcs | 1.50" × 3.50" × {front_rail_span:.2f}" | Upper perimeter long rails (flush with top of legs) |
| **Side Upper Aprons** | 2 pcs | 1.50" × 3.50" × {side_rail_span:.2f}" | Upper short side rails |
| **Upper Center Cross-Tie** | 1 pc | 1.50" × 3.50" × {center_tie_span:.2f}" | Desktop mid support & divider anchor |
| **Front & Rear Lower Stretchers**| 2 pcs | 1.50" × 3.50" × {front_rail_span:.2f}" | Lower stretchers flush with bottom of legs (23.0" clear opening) |
| **Side Lower Stretchers**| 2 pcs | 1.50" × 3.50" × {side_rail_span:.2f}" | Lower side stretchers |
| **Lower Center Cross-Tie** | 1 pc | 1.50" × 3.50" × {center_tie_span:.2f}" | Bottom shelf & divider support |
| **Grooved Gable Top Spacer** | 1 pc | 1.50" × 3.50" × {center_tie_span:.2f}" | Unripped 2×4 laid flat with 3/4" W × 1/2" D dado groove (1.00" effective spacer) |
| **Gable Rear Tie Block** | 1 pc | 1.50" × 3.50" × {REAR_TIE_BLOCK_H:.2f}" | Bridges 1.50" gap between back of Center Gable and Rear Shear Wall |
| **Left Drawer Slide Runners** | 3 pcs | 1.50" × 3.50" × 16.00" | Screwed to left side return flanges w/ 1/2" shims (flush at X = 5.00") |
| **CR-6 Shelf Support Cleats** | 2 pcs | 0.75" × 2.00" × 18.00" (3/4" Birch) | Leftover 3/4" Birch strips screwed inside front & back lower stretchers (Right Bay) |

*Total 2×4 Lumber Needed:* **7 to 8 standard 8-foot (96") 2×4 studs** (uses spare 30" leg offcuts from Studs 4–7 for the three 18" left slide runners and cleats).

---

## 2. Hardwood Plywood Project Panels & Exact Cut List

| Item | Qty | Product Title on Home Depot Canada | Store SKU | Model # | Purpose |
| :--- | :---: | :--- | :---: | :---: | :--- |
| **3/4" Walnut** | 1 | CFP 3/4 in. x 2 ft. x 4 ft. PureBond Walnut Plywood ($54) | Online | — | All 3 drawer fronts (matches desktop) |
| **3/4" Birch** | 1 | CFP 3/4 in. x 2 ft. x 4 ft. PureBond Birch Plywood ($41) | `1001513690` | `4391` | Center divider (`18"×22"`) & CR-6 shelf (`18"×18.625"`) |
| **1/2" Birch** | 1 | CFP 1/2 in. x 2 ft. x 4 ft. PureBond Birch Plywood ($36) | `1001513691` | `4384` | Rear anti-racking shear wall (`45.0" × 24.0"`, mounted flush at top) |
| **1/2" Birch** | 2 | CFP 1/2 in. x 2 ft. x 4 ft. PureBond Birch Plywood (~$36 ea) | `1001513691` | `4384` | All 12 drawer box walls + Top Tool Drawer bottom (`17.375"×17.875"`) |
| **1/4" Birch** | 1 | CFP 1/4 in. x 2 ft. x 4 ft. PureBond Birch Plywood (~$28) | `1001513692` | `4377` | Middle & Bottom Spool Drawer bottoms (2 pcs `17.375"×17.875"`) |

### Exact Plywood Cut Dimensions (Corrected for {ACTUAL_DRAWER_BAY_W:.2f}" W × {CLEAR_BAY_HEIGHT:.2f}" H Drawer Bay)
| Component Label | Qty | Material | Cut Size (W × H / D) | Notes |
| :--- | :---: | :--- | :---: | :--- |
| **`Center_Divider_Gable`** | 1x | 3/4" Birch Ply | `18.00" D × 22.00" H` | Sits on lower tie; top nests 1/2" into Grooved 2×4 Spacer |
| **`CR6_Tech_Shelf`** | 1x | 3/4" Birch Ply | `18.625" W × 18.00" D` | Rests on cleats in right bay (optional 2.0"×18.0" filler strip) |
| **`Rear_Shear_Wall_Panel`** | 1x | 1/2" Birch Ply | `45.00" W × 24.00" H` | Mounted flush with top of Upper Rear Apron; leaves 6" cable pass-through |
| **`Spool_Box_Sides`** | 4x | 1/2" Birch Ply | `18.00" D × 7.75" H` | Left & right side walls for Middle & Bottom Spool Drawers |
| **`Spool_Box_Front_Back`** | 4x | 1/2" Birch Ply | `{drawer_subpanel_w:.3f}" W × 7.75" H` | Sits *between* 1/2" side walls (`{drawer_subpanel_w:.3f}" + 2×0.50" = {drawer_box_w:.3f}"` outer box width)* |
| **`Tool_Box_Sides`** | 2x | 1/2" Birch Ply | `18.00" D × 3.50" H` | Left & right side walls for Top Tool Drawer |
| **`Tool_Box_Front_Back`** | 2x | 1/2" Birch Ply | `{drawer_subpanel_w:.3f}" W × 3.50" H` | Sits *between* 1/2" side walls (`{drawer_subpanel_w:.3f}" + 2×0.50" = {drawer_box_w:.3f}"` outer box width)* |
| **`Spool_Drawer_Bottoms`** | 2x | 1/4" Birch Ply | `{drawer_bottom_w:.3f}" W × {drawer_bottom_d:.3f}" D` | Flush-screwed to Spool Drawers (preserves headroom for 7.87" spools) |
| **`Tool_Drawer_Bottom`** | 1x | 1/2" Birch Ply | `{drawer_bottom_w:.3f}" W × {drawer_bottom_d:.3f}" D` | From 1/2" Sheet #2 leftover; flush-screwed to Top Tool Drawer |
| **`Spool_Drawer_Faces`** | 2x | 3/4" Walnut Ply | `{drawer_face_w:.3f}" W × 8.50" H` | Middle & Bottom drawer faces (1/8" reveal on all sides) |
| **`Tool_Drawer_Face`** | 1x | 3/4" Walnut Ply | `{drawer_face_w:.3f}" W × 5.50" H` | Top drawer face (`8.5" + 8.5" + 5.5" + 0.5" reveals = 23.00"` bay height) |

*\*Note: Measure your actual assembled bay width $W_{{\\text{{bay}}}}$ and actual 1/2" plywood thickness $T_{{\\text{{ply}}}}$ before cutting drawer sub-panels: $\\text{{Sub-Panel Width}} = (W_{{\\text{{bay}}}} - 1.000\") - 2 \\times T_{{\\text{{ply}}}}$.*

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
4. **Foot Block:** Center-drill a 2" × 2" scrap 2×4 block for the 3/8" threaded leveling foot insert, then glue and screw it (from the inside outward) into the bottom inside corner of the "L".
5. **No Planer Needed:** The factory-flat edge of Piece B butts against the factory-flat face of Piece A.

---

## 4. Hardware Checklist

- [ ] **Drawer Slides:** 18" Full-Extension Ball-Bearing Slides, 100 lb (Amazon 6-pack for $72)
- [ ] **Drawer Pulls:** 3 pcs modern 5" (128 mm) bar pulls
- [ ] **Leveling Feet:** 4 pcs heavy-duty 3/8"-16 threaded rubber swivel glides + threaded inserts
- [ ] **Pocket Screws:** 1 box 2-1/2" coarse pocket hole screws (for 2×4 frame, L-legs & slide runners)
- [ ] **Drawer Screws:** 1 box 1" pan-head pocket screws (for 1/2" drawer boxes & mounting walnut faces)
- [ ] **Tabletop Fasteners:** 8 pcs Figure-8 desktop fasteners (use 3/4" Forstner bit)
- [ ] **Wood Glue:** 1 bottle Titebond II
""")

print(f"  [+] Cut list and BOM exported: {bom_path}")
print("=" * 75)
print("  FREECAD MODEL GENERATION (V3) COMPLETED SUCCESSFULLY!")
print("=" * 75)

import sys
sys.exit(0)
