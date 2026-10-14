#!/usr/bin/env python3
"""
===============================================================================
PARAMETRIC UPRIGHT ARCADE CABINET GENERATOR FOR FREECAD (V2)
===============================================================================
Uses FreeCAD 1.0+ Variable Sets (App::VarSet), Sketches with Constraints
(Sketcher::SketchObject), and parametric expressions to create a fully
recomputable solid B-Rep arcade cabinet assembly.

Facing the cabinet from the front (player's perspective):
- Left is +Y (Player 1, Blue buttons, left magnetic catch & jamb cleat)
- Right is -Y (Player 2, Red buttons, right piano hinge, right rocker switch)
All transverse panels, doors, bezels, and shelves are centered symmetrically
around the cabinet Y-midplane (Y = 0.0), perfectly aligned between the inner
faces of the Left (+InnerWidth/2) and Right (-InnerWidth/2) Side Panels.
===============================================================================
"""

import sys
import os
import math
import FreeCAD
import Part
import Sketcher
import Spreadsheet
import TechDraw

FreeCAD.Units.setSchema(3)  # ImperialDecimal (inches)
FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Units").SetInt("UserSchema", 3)

print("=" * 75)
print("  BUILDING PARAMETRIC ARCADE CABINET IN FREECAD (V2)")
print(f"  FreeCAD Version: {FreeCAD.Version()}")
print("=" * 75)

INCH = 25.4  # 1 inch = 25.4 mm

def in_to_mm(val):
    return val * INCH

def v_in(x, y, z):
    return FreeCAD.Vector(x * INCH, y * INCH, z * INCH)

# Base Dimensions in Inches
CABINET_INNER_WIDTH     = 23.00   # Clear internal width between side panels
CABINET_DEPTH           = 18.00   # Main body depth
WOOD_THICKNESS          = 0.75    # 3/4" White Birch VC plywood
BACK_WOOD_THICKNESS     = 0.25    # 1/4" lightweight back panel plywood
SIDE_REVEAL             = 1.00    # 1.0" perimeter reveal / lip around side panels

TOE_KICK_HEIGHT         = 4.50    # Kickplate height off floor
TOE_KICK_DEPTH          = 2.25    # Kickplate setback depth
BASE_OFFSET_Z           = 0.75    # Base plate elevated 3/4" (flush with 3/4" corner pads)

CP_WIDTH                = 31.50   # User control box & shelf width
CP_DEPTH                = 10.50   # Control panel shelf depth
CP_HEIGHT_FRONT         = 3.50    # Console front height
CP_HEIGHT_BACK          = 5.00    # Console rear height
CP_RUBBER_FEET          = 0.25    # Console 1/4" rubber feet
CP_SHELF_HEIGHT         = 34.00   # Control shelf top height off ground
KEYBOARD_DRAWER_HEIGHT  = 3.25    # Clear drawer cavity height
KEYBOARD_TRAY_WIDTH     = 21.00   # Keyboard slide-out tray width
KEYBOARD_TRAY_DEPTH     = 9.00    # Keyboard slide-out tray depth

VESACrossbar_HEIGHT     = 5.50    # VESA crossbar height
VESA_HOLE_SPACING       = 3.937   # 100mm = 3.937"
MARQUEE_HEIGHT          = 5.50    # Marquee sign height
DOOR_CLEARANCE          = 0.0625  # 1/16" perimeter reveal on doors

SHELF_HEIGHT            = 16.00   # Equipment shelf elevation Z
SHELF_DEPTH             = 14.00   # Equipment shelf depth (leaving 2.0" rear slot)

# Calculated references
cp_front_x = -CP_DEPTH / 2.0                            # -5.25"
cp_rear_x  = CP_DEPTH / 2.0                             # +5.25"
shelf_bottom_z = CP_SHELF_HEIGHT - WOOD_THICKNESS       # 33.25"
console_base_z = CP_SHELF_HEIGHT + CP_RUBBER_FEET       # 34.25"
console_front_top_z = console_base_z + CP_HEIGHT_FRONT  # 37.75"
console_rear_top_z  = console_base_z + CP_HEIGHT_BACK   # 39.25"

kb_bottom_z = shelf_bottom_z - KEYBOARD_DRAWER_HEIGHT   # 30.00"
kb_housing_bottom_z = kb_bottom_z - WOOD_THICKNESS      # 29.25"
diag_front_z = 23.50                                    # Front door / apron seam

x_bezel_top = 14.50
z_bezel_top = 53.00
x_marquee_bottom = 9.00
z_marquee_bottom = 58.00
x_marquee_top    = 7.75
z_marquee_top    = z_marquee_bottom + MARQUEE_HEIGHT    # 63.50"
z_roof           = z_marquee_top + WOOD_THICKNESS       # 64.25"

dx_bezel = x_bezel_top - cp_rear_x                      # 9.25"
dz_bezel = z_bezel_top - console_rear_top_z             # 13.75"
angle_bezel = math.atan2(dx_bezel, dz_bezel)            # 33.93 deg
bezel_len = math.sqrt(dx_bezel**2 + dz_bezel**2)        # 16.572"
bezel_bot_dz = WOOD_THICKNESS * math.tan(angle_bezel)    # 0.505"

dx_spk = x_marquee_bottom - x_bezel_top                 # -5.50"
dz_spk = z_marquee_bottom - z_bezel_top                 # +5.00"
angle_spk_from_vert = math.atan2(-dx_spk, dz_spk)       # 47.73 deg
panel_len_spk = math.sqrt(dx_spk**2 + dz_spk**2)        # 7.433"

miter_bezel_spk_deg = (math.degrees(angle_bezel) + math.degrees(angle_spk_from_vert)) / 2.0 # 40.83 deg
miter_bezel_spk_dz = WOOD_THICKNESS * math.tan(math.radians(miter_bezel_spk_deg))            # 0.648"

dx_marq = x_marquee_top - x_marquee_bottom
dz_marq = z_marquee_top - z_marquee_bottom
marquee_len = math.sqrt(dx_marq*dx_marq + dz_marq*dz_marq)
angle_marq = math.atan2(dx_marq, dz_marq)

spk_top_deg = math.degrees(angle_spk_from_vert) - abs(math.degrees(angle_marq))               # 34.93 deg
spk_top_dz = -WOOD_THICKNESS * math.tan(math.radians(spk_top_deg))                            # -0.524"

roof_front_deg = 12.80
roof_front_dz = WOOD_THICKNESS * math.tan(math.radians(roof_front_deg))                       # 0.170"

# =============================================================================
# 1. INITIALIZE DOCUMENT & VARIABLE SET
# =============================================================================
doc_name = "Arcade_Cabinet"
doc = FreeCAD.newDocument(doc_name)
doc.Label = "Arcade Cabinet (Parametric)"

# Create FreeCAD 1.0+ Variable Set (App::VarSet)
varset = doc.addObject("App::VarSet", "CabinetParameters")
varset.Label = "Cabinet Parameters"

varset_props = [
    ("InnerWidth",          f"{CABINET_INNER_WIDTH:.2f} in",    "Cabinet",   "Clear internal width between side panels"),
    ("CabinetDepth",        f"{CABINET_DEPTH:.2f} in",          "Cabinet",   "Depth of main cabinet carcass"),
    ("WoodThickness",       f"{WOOD_THICKNESS:.3f} in",         "Materials", "3/4\" White Birch VC structural plywood"),
    ("BackWoodThickness",   f"{BACK_WOOD_THICKNESS:.3f} in",    "Materials", "1/4\" lightweight back access panel"),
    ("SideReveal",          f"{SIDE_REVEAL:.2f} in",            "Cabinet",   "1.0\" perimeter side lip / jut-out"),
    ("ToeKickHeight",       f"{TOE_KICK_HEIGHT:.2f} in",        "Base",      "Height of kickplate recess off floor"),
    ("ToeKickDepth",        f"{TOE_KICK_DEPTH:.2f} in",         "Base",      "Setback of toe kickboard"),
    ("BaseOffsetZ",         f"{BASE_OFFSET_Z:.3f} in",          "Base",      "Elevation of base plate (corner pad thick)"),
    ("DoorClearance",       f"{DOOR_CLEARANCE:.4f} in",        "Doors",     "1/16\" perimeter reveal on inset doors"),
    ("CPShelfHeight",       f"{CP_SHELF_HEIGHT:.2f} in",        "Controls",  "Height of control panel shelf top"),
    ("CPWidth",             f"{CP_WIDTH:.2f} in",              "Controls",  "Control panel and shelf width span"),
    ("CPDepth",             f"{CP_DEPTH:.2f} in",              "Controls",  "Control panel shelf depth"),
    ("CPHeightFront",       f"{CP_HEIGHT_FRONT:.2f} in",       "Controls",  "Console box front height"),
    ("CPHeightBack",        f"{CP_HEIGHT_BACK:.2f} in",        "Controls",  "Console box rear height"),
    ("KeyboardDrawerH",     f"{KEYBOARD_DRAWER_HEIGHT:.2f} in", "Controls",  "Slide-out drawer cavity clear height"),
    ("KeyboardTrayW",       f"{KEYBOARD_TRAY_WIDTH:.2f} in",   "Controls",  "Slide-out keyboard tray width"),
    ("KeyboardTrayD",       f"{KEYBOARD_TRAY_DEPTH:.2f} in",   "Controls",  "Slide-out keyboard tray depth"),
    ("ShelfHeight",         f"{SHELF_HEIGHT:.2f} in",          "Interior",  "Equipment shelf elevation Z"),
    ("ShelfDepth",          f"{SHELF_DEPTH:.2f} in",           "Interior",  "Equipment shelf depth (2\" rear slot)"),
    ("VESACrossbarHeight",  f"{VESACrossbar_HEIGHT:.2f} in",    "Display",   "VESA 100 mounting crossbar height"),
    ("MarqueeHeight",       f"{MARQUEE_HEIGHT:.2f} in",        "Display",   "Marquee sign height"),
]

for name, val, cat, desc in varset_props:
    varset.addProperty("App::PropertyLength", name, cat, desc)
    setattr(varset, name, val)

# Also create Spreadsheet for users who view via Spreadsheet
sheet = doc.addObject("Spreadsheet::Sheet", "Parameters")
sheet.Label = "Parameters Spreadsheet"
for idx, (name, val, cat, desc) in enumerate(varset_props, start=1):
    sheet.set(f"A{idx}", name)
    sheet.set(f"B{idx}", val)
    sheet.setAlias(f"B{idx}", name)
    sheet.set(f"C{idx}", desc)

doc.recompute()
print("  [+] CabinetParameters VarSet created with 21 properties")

# =============================================================================
# 2. LOGICAL DOCUMENT GROUPS & COLORS
# =============================================================================
grp_structure     = doc.addObject("App::DocumentObjectGroup", "01_Structure")
grp_structure.Label = "01 Structure (3/4\" Birch Carcass)"

grp_doors_shelves = doc.addObject("App::DocumentObjectGroup", "02_Doors_and_Shelves")
grp_doors_shelves.Label = "02 Doors & Shelves (Access & Equipment)"

grp_base_feet     = doc.addObject("App::DocumentObjectGroup", "03_Base_and_Feet")
grp_base_feet.Label = "03 Base & Feet (Corner Pads & Glides)"

grp_controls      = doc.addObject("App::DocumentObjectGroup", "04_Controls")
grp_controls.Label = "04 Controls (31.5\" Console & Keyboard Drawer)"

grp_display_sound = doc.addObject("App::DocumentObjectGroup", "05_Display_and_Sound")
grp_display_sound.Label = "05 Display & Sound (Bezel, VESA, Speakers, Marquee)"

grp_hardware      = doc.addObject("App::DocumentObjectGroup", "06_Hardware_and_Electronics")
grp_hardware.Label = "06 Hardware & Electronics (Switches, Power, Pi, Subwoofer)"

COL_BLACK_PAINT = (0.20, 0.20, 0.22)
COL_DOOR        = (0.28, 0.28, 0.30)
COL_BACK_14     = (0.42, 0.42, 0.45)
COL_WOOD_EDGE   = (0.80, 0.68, 0.48)
COL_CHROME      = (0.75, 0.75, 0.78)
COL_STEEL_DARK  = (0.35, 0.35, 0.38)
COL_RED_LED     = (0.90, 0.15, 0.15)
COL_BEZEL       = (0.12, 0.12, 0.14)
COL_SCREEN      = (0.05, 0.05, 0.07)
COL_MARQUEE     = (0.95, 0.95, 0.95)
COL_PCB_GREEN   = (0.10, 0.55, 0.20)

def set_style(obj, color):
    if hasattr(obj, "ViewObject") and obj.ViewObject:
        obj.ViewObject.ShapeColor = color
        obj.ViewObject.LineColor = (0.1, 0.1, 0.1)

# Helper for creating beveled cross-section sketches on XZ and extruding along Y
def make_xz_profile_extrusion(name, pts_xz, group, color=COL_BLACK_PAINT):
    sk = doc.addObject("Sketcher::SketchObject", f"Sketch_{name}")
    sk.MapMode = "Deactivated"
    sk.Placement = FreeCAD.Placement(
        FreeCAD.Vector(0, in_to_mm(-CABINET_INNER_WIDTH / 2.0), 0),
        FreeCAD.Rotation(FreeCAD.Vector(1, 0, 0), 90)
    )
    sk.setExpression("Placement.Base.y", "-CabinetParameters.InnerWidth / 2")
    n = len(pts_xz)
    for i in range(n):
        p1 = FreeCAD.Vector(pts_xz[i][0] * INCH, pts_xz[i][1] * INCH, 0)
        p2 = FreeCAD.Vector(pts_xz[(i+1)%n][0] * INCH, pts_xz[(i+1)%n][1] * INCH, 0)
        sk.addGeometry(Part.LineSegment(p1, p2))
    for i in range(n):
        sk.addConstraint(Sketcher.Constraint("Coincident", i, 2, (i+1)%n, 1))
    
    ext = doc.addObject("Part::Extrusion", name)
    ext.Base = sk
    ext.DirMode = "Custom"
    ext.Dir = FreeCAD.Vector(0, 1, 0)
    ext.setExpression("LengthFwd", "CabinetParameters.InnerWidth")
    ext.Solid = True
    group.addObject(sk)
    group.addObject(ext)
    set_style(ext, color)
    return ext

# =============================================================================
# 3. GROUP 01: STRUCTURE (3/4" Birch Carcass)
# =============================================================================
print("  [*] Building 01 Structure with Sketches & Constraints...")

# Side Panel 15-Vertex Profile Sketch on XZ
sk_side = doc.addObject("Sketcher::SketchObject", "Sketch_SidePanel")
sk_side.MapMode = "Deactivated"
sk_side.Placement = FreeCAD.Placement(FreeCAD.Vector(0,0,0), FreeCAD.Rotation(FreeCAD.Vector(1,0,0), 90))

side_pts_in = [
    (TOE_KICK_DEPTH, 0.0),                               # P0:  Bottom toe-kick riser
    (TOE_KICK_DEPTH, TOE_KICK_HEIGHT),                   # P1:  Top of toe-kick recess (4.5")
    (-SIDE_REVEAL, TOE_KICK_HEIGHT),                     # P2:  Front lower corner (1" lip)
    (-SIDE_REVEAL, diag_front_z),                        # P3:  Top of coin door vertical lip
    (cp_front_x - SIDE_REVEAL, kb_housing_bottom_z),     # P4:  Solid diagonal corbel (PARALLEL TO APRON!)
    (cp_front_x - SIDE_REVEAL, shelf_bottom_z),          # P5:  Front vertical cheek of keyboard cavity
    (cp_rear_x, shelf_bottom_z),                         # P6:  Rear edge of shelf ledge
    (cp_rear_x, console_rear_top_z + 0.75),              # P7:  Vertical rise behind console
    (6.00, 42.16),                                       # P8:  Extra transition angle
    (13.19, 52.84),                                      # P9:  Monitor cheek
    (8.10, 57.47),                                       # P10: Speaker cheek
    (6.75, 63.50),                                       # P11: Top of marquee visor
    (6.75, z_roof + SIDE_REVEAL),                        # P12: Front top corner of roof lip
    (CABINET_DEPTH + SIDE_REVEAL, z_roof + SIDE_REVEAL), # P13: Top back roof corner
    (CABINET_DEPTH + SIDE_REVEAL, 0.0),                  # P14: Bottom back floor corner
]

num_side_pts = len(side_pts_in)
for i in range(num_side_pts):
    p1 = FreeCAD.Vector(side_pts_in[i][0] * INCH, side_pts_in[i][1] * INCH, 0)
    p2 = FreeCAD.Vector(side_pts_in[(i+1)%num_side_pts][0] * INCH, side_pts_in[(i+1)%num_side_pts][1] * INCH, 0)
    sk_side.addGeometry(Part.LineSegment(p1, p2))

# Coincident constraints
for i in range(num_side_pts):
    sk_side.addConstraint(Sketcher.Constraint("Coincident", i, 2, (i+1)%num_side_pts, 1))

# Orthogonal constraints
sk_side.addConstraint(Sketcher.Constraint("Vertical", 0))    # P0->P1
sk_side.addConstraint(Sketcher.Constraint("Horizontal", 1))  # P1->P2
sk_side.addConstraint(Sketcher.Constraint("Vertical", 2))    # P2->P3
sk_side.addConstraint(Sketcher.Constraint("Vertical", 4))    # P4->P5
sk_side.addConstraint(Sketcher.Constraint("Horizontal", 5))  # P5->P6
sk_side.addConstraint(Sketcher.Constraint("Vertical", 6))    # P6->P7
sk_side.addConstraint(Sketcher.Constraint("Vertical", 11))   # P11->P12
sk_side.addConstraint(Sketcher.Constraint("Horizontal", 12)) # P12->P13
sk_side.addConstraint(Sketcher.Constraint("Vertical", 13))   # P13->P14
sk_side.addConstraint(Sketcher.Constraint("Horizontal", 14)) # P14->P0
grp_structure.addObject(sk_side)

# Facing the cabinet: LEFT is +Y, RIGHT is -Y!
# Side Panel Left: Extruded from +InnerWidth/2 to +InnerWidth/2 + WoodThickness (+Y)
side_l = doc.addObject("Part::Extrusion", "Side_Panel_Left")
side_l.Base = sk_side
side_l.DirMode = "Custom"
side_l.Dir = FreeCAD.Vector(0, 1, 0)
side_l.setExpression("LengthFwd", "CabinetParameters.WoodThickness")
side_l.setExpression("Placement.Base.y", "CabinetParameters.InnerWidth / 2")
side_l.Solid = True
grp_structure.addObject(side_l)
set_style(side_l, COL_BLACK_PAINT)

# Side Panel Right: Extruded from -InnerWidth/2 - WoodThickness to -InnerWidth/2 (-Y)
side_r_raw = doc.addObject("Part::Extrusion", "Side_Panel_Right_Body")
side_r_raw.Base = sk_side
side_r_raw.DirMode = "Custom"
side_r_raw.Dir = FreeCAD.Vector(0, 1, 0)
side_r_raw.setExpression("LengthFwd", "CabinetParameters.WoodThickness")
side_r_raw.setExpression("Placement.Base.y", "-CabinetParameters.InnerWidth / 2 - CabinetParameters.WoodThickness")
side_r_raw.Solid = True
grp_structure.addObject(side_r_raw)

# Rocker switch 20mm through-hole + 1/2" relief pocket on inside face of Right Side Panel (-Y)
sw_x = 15.00
sw_z = 34.00
sw_hole = doc.addObject("Part::Cylinder", "Rocker_Switch_Hole")
sw_hole.Radius = in_to_mm(0.394) # Dia 20mm
sw_hole.Height = in_to_mm(WOOD_THICKNESS + 0.2)
sw_hole.Placement.Base = FreeCAD.Vector(sw_x * INCH, (-CABINET_INNER_WIDTH / 2.0 - WOOD_THICKNESS - 0.1) * INCH, sw_z * INCH)
sw_hole.Placement.Rotation = FreeCAD.Rotation(FreeCAD.Vector(1, 0, 0), -90)

sw_pocket = doc.addObject("Part::Cylinder", "Rocker_Switch_Relief_Pocket")
sw_pocket.Radius = in_to_mm(0.875) # Dia 1.75"
sw_pocket.Height = in_to_mm(0.50)  # 1/2" deep pocket on inside
sw_pocket.Placement.Base = FreeCAD.Vector(sw_x * INCH, (-CABINET_INNER_WIDTH / 2.0 - 0.5) * INCH, sw_z * INCH)
sw_pocket.Placement.Rotation = FreeCAD.Rotation(FreeCAD.Vector(1, 0, 0), -90)

cut_r1 = doc.addObject("Part::Cut", "Side_Panel_Right_Hole")
cut_r1.Base = side_r_raw
cut_r1.Tool = sw_hole

side_r = doc.addObject("Part::Cut", "Side_Panel_Right")
side_r.Base = cut_r1
side_r.Tool = sw_pocket
grp_structure.addObject(side_r)
set_style(side_r, COL_BLACK_PAINT)

# 1. Toe Kick Board: X = 2.25", Y = -InnerWidth/2 to +InnerWidth/2, Z = 0 to 4.5"
tk_board = doc.addObject("Part::Box", "Toe_Kick_Board")
tk_board.setExpression("Length", "CabinetParameters.WoodThickness")
tk_board.setExpression("Width", "CabinetParameters.InnerWidth")
tk_board.setExpression("Height", "CabinetParameters.ToeKickHeight")
tk_board.setExpression("Placement.Base.x", "CabinetParameters.ToeKickDepth")
tk_board.setExpression("Placement.Base.y", "-CabinetParameters.InnerWidth / 2")
tk_board.Placement.Base.z = 0.0
grp_structure.addObject(tk_board)
set_style(tk_board, COL_BLACK_PAINT)

# 2. Toe Kick Ceiling / Kickplate Cover: X = 0.75" to 2.25", Z = 4.5" to 5.25"
tk_ceil = doc.addObject("Part::Box", "Toe_Kick_Ceiling")
tk_ceil.setExpression("Length", "CabinetParameters.ToeKickDepth - CabinetParameters.WoodThickness")
tk_ceil.setExpression("Width", "CabinetParameters.InnerWidth")
tk_ceil.setExpression("Height", "CabinetParameters.WoodThickness")
tk_ceil.setExpression("Placement.Base.x", "CabinetParameters.WoodThickness")
tk_ceil.setExpression("Placement.Base.y", "-CabinetParameters.InnerWidth / 2")
tk_ceil.setExpression("Placement.Base.z", "CabinetParameters.ToeKickHeight")
grp_structure.addObject(tk_ceil)
set_style(tk_ceil, COL_BLACK_PAINT)

# 3. Door Header Rail (Fixed transverse anti-racking structural stretcher)
# Pocket screwed between side panels directly behind top of front door
hdr_rail = doc.addObject("Part::Box", "Door_Header_Rail")
hdr_rail.setExpression("Length", "CabinetParameters.WoodThickness")
hdr_rail.setExpression("Width", "CabinetParameters.InnerWidth")
hdr_rail.Height = in_to_mm(1.50)
hdr_rail.setExpression("Placement.Base.x", "CabinetParameters.WoodThickness")
hdr_rail.setExpression("Placement.Base.y", "-CabinetParameters.InnerWidth / 2")
hdr_rail.Placement.Base.z = in_to_mm(diag_front_z - 1.50)
grp_structure.addObject(hdr_rail)
set_style(hdr_rail, COL_BLACK_PAINT)

# 4. Door Jamb Stop Cleats (Left at +Y, Right at -Y)
jamb_l = doc.addObject("Part::Box", "Door_Jamb_Cleat_Left")
jamb_l.setExpression("Length", "CabinetParameters.WoodThickness")
jamb_l.Width = in_to_mm(0.75)
jamb_l.Height = in_to_mm(16.0)
jamb_l.setExpression("Placement.Base.x", "CabinetParameters.WoodThickness")
jamb_l.setExpression("Placement.Base.y", "CabinetParameters.InnerWidth / 2 - 0.75 in")
jamb_l.setExpression("Placement.Base.z", "CabinetParameters.ToeKickHeight + 0.75 in")
grp_structure.addObject(jamb_l)
set_style(jamb_l, COL_WOOD_EDGE)

jamb_r = doc.addObject("Part::Box", "Door_Jamb_Cleat_Right")
jamb_r.setExpression("Length", "CabinetParameters.WoodThickness")
jamb_r.Width = in_to_mm(0.75)
jamb_r.Height = in_to_mm(16.0)
jamb_r.setExpression("Placement.Base.x", "CabinetParameters.WoodThickness")
jamb_r.setExpression("Placement.Base.y", "-CabinetParameters.InnerWidth / 2")
jamb_r.setExpression("Placement.Base.z", "CabinetParameters.ToeKickHeight + 0.75 in")
grp_structure.addObject(jamb_r)
set_style(jamb_r, COL_WOOD_EDGE)

# 5. Console Diagonal Apron (Uniform 3/4" Plywood: 42.4° Beveled Ends, Parallel Faces)
# Exactly 0.75" thick throughout with ZERO tapering; parallel to side panel corbel!
dx_ap = cp_front_x - 0.0
dz_ap = kb_housing_bottom_z - diag_front_z
L_ap = math.sqrt(dx_ap**2 + dz_ap**2)
nx_ap = (dz_ap / L_ap) * WOOD_THICKNESS
nz_ap = (-dx_ap / L_ap) * WOOD_THICKNESS
t_top_ap = -nz_ap / dz_ap
s_bot_ap = -nx_ap / dx_ap

apron_pts = [
    (0.0, diag_front_z),
    (cp_front_x, kb_housing_bottom_z),
    (cp_front_x + nx_ap + t_top_ap * dx_ap, kb_housing_bottom_z),
    (0.0, diag_front_z + nz_ap + s_bot_ap * dz_ap)
]
make_xz_profile_extrusion("Console_Diagonal_Apron", apron_pts, grp_structure, COL_BLACK_PAINT)

# 6. Keyboard Housing Bottom Plate (Uniform 3/4" Plywood: 5.25" x 23.00" x 0.75")
# Sits directly above diagonal apron from X = -5.25" to X = 0.0" with zero penetration
kb_plate_pts = [
    (cp_front_x, kb_housing_bottom_z),
    (cp_front_x, kb_housing_bottom_z + WOOD_THICKNESS),
    (0.0, kb_housing_bottom_z + WOOD_THICKNESS),
    (0.0, kb_housing_bottom_z)
]
make_xz_profile_extrusion("Keyboard_Bottom_Plate", kb_plate_pts, grp_structure, COL_BLACK_PAINT)

# 7. Top Roof Panel (Beveled 12.80° front)
roof_pts = [
    (x_marquee_top, z_roof - WOOD_THICKNESS),
    (x_marquee_top + roof_front_dz, z_roof),
    (CABINET_DEPTH, z_roof),
    (CABINET_DEPTH, z_roof - WOOD_THICKNESS)
]
make_xz_profile_extrusion("Top_Roof_Panel", roof_pts, grp_structure, COL_BLACK_PAINT)

# =============================================================================
# 4. GROUP 02: DOORS & SHELVES
# =============================================================================
print("  [*] Building 02 Doors & Shelves with Sketches & Constraints...")

# 1. Lower Front Access Door (3/4" Birch VC: 1/16" Perimeter Reveals)
# Modeled via constrained Sketch_FrontDoor and extruded forward by WoodThickness
sk_door = doc.addObject("Sketcher::SketchObject", "Sketch_FrontDoor")
sk_door.MapMode = "Deactivated"
# Local sketch plane: X is Width (along cabinet Y), Y is Height (along cabinet Z)
door_w_init = (CABINET_INNER_WIDTH - 2.0 * DOOR_CLEARANCE) * INCH
door_h_init = ((diag_front_z - TOE_KICK_HEIGHT) - 2.0 * DOOR_CLEARANCE) * INCH

sk_door.addGeometry(Part.LineSegment(FreeCAD.Vector(0,0,0), FreeCAD.Vector(door_w_init, 0, 0)))
sk_door.addGeometry(Part.LineSegment(FreeCAD.Vector(door_w_init, 0, 0), FreeCAD.Vector(door_w_init, door_h_init, 0)))
sk_door.addGeometry(Part.LineSegment(FreeCAD.Vector(door_w_init, door_h_init, 0), FreeCAD.Vector(0, door_h_init, 0)))
sk_door.addGeometry(Part.LineSegment(FreeCAD.Vector(0, door_h_init, 0), FreeCAD.Vector(0, 0, 0)))

for i in range(4):
    sk_door.addConstraint(Sketcher.Constraint("Coincident", i, 2, (i+1)%4, 1))
# Lock point 0 to sketch origin (-1, 1) to prevent drift
sk_door.addConstraint(Sketcher.Constraint("Coincident", 0, 1, -1, 1))
sk_door.addConstraint(Sketcher.Constraint("Horizontal", 0))
sk_door.addConstraint(Sketcher.Constraint("Vertical", 1))
sk_door.addConstraint(Sketcher.Constraint("Horizontal", 2))
sk_door.addConstraint(Sketcher.Constraint("Vertical", 3))

# Width and Height dimensional constraints linked to VarSet expressions
sk_door.addConstraint(Sketcher.Constraint("DistanceX", 0, 1, 0, 2, door_w_init))
sk_door.setExpression(f"Constraints[{len(sk_door.Constraints)-1}]", "CabinetParameters.InnerWidth - 2 * CabinetParameters.DoorClearance")

sk_door.addConstraint(Sketcher.Constraint("DistanceY", 3, 2, 3, 1, door_h_init))
sk_door.setExpression(f"Constraints[{len(sk_door.Constraints)-1}]", "(23.5 in - CabinetParameters.ToeKickHeight) - 2 * CabinetParameters.DoorClearance")

# Align sketch coordinate system directly at the door opening!
rot_face = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), 90) * FreeCAD.Rotation(FreeCAD.Vector(1, 0, 0), 90)
sk_door.Placement = FreeCAD.Placement(
    FreeCAD.Vector(0, in_to_mm(-CABINET_INNER_WIDTH / 2.0 + DOOR_CLEARANCE), in_to_mm(TOE_KICK_HEIGHT + DOOR_CLEARANCE)),
    rot_face
)
sk_door.setExpression("Placement.Base.y", "-CabinetParameters.InnerWidth / 2 + CabinetParameters.DoorClearance")
sk_door.setExpression("Placement.Base.z", "CabinetParameters.ToeKickHeight + CabinetParameters.DoorClearance")
grp_doors_shelves.addObject(sk_door)

door_panel = doc.addObject("Part::Extrusion", "Lower_Front_Panel")
door_panel.Base = sk_door
door_panel.DirMode = "Custom"
door_panel.Dir = FreeCAD.Vector(1, 0, 0)
door_panel.setExpression("LengthFwd", "CabinetParameters.WoodThickness")
door_panel.Solid = True
grp_doors_shelves.addObject(door_panel)
set_style(door_panel, COL_DOOR)

# 2. Rear Access Panel (1/4" LIGHTWEIGHT PLYWOOD - IEC320 C14 Cutout & Cam Lock)
# Outer opening: 23.0" x 62.75" -> Panel: 22.875" W x 62.625" H x 0.25" T
sk_back = doc.addObject("Sketcher::SketchObject", "Sketch_BackAccessPanel")
sk_back.MapMode = "Deactivated"
back_w_init = (CABINET_INNER_WIDTH - 2.0 * DOOR_CLEARANCE) * INCH
back_h_raw = z_roof - WOOD_THICKNESS - BASE_OFFSET_Z
back_h_init = (back_h_raw - 2.0 * DOOR_CLEARANCE) * INCH

# Outer panel border
sk_back.addGeometry(Part.LineSegment(FreeCAD.Vector(0,0,0), FreeCAD.Vector(back_w_init, 0, 0)))
sk_back.addGeometry(Part.LineSegment(FreeCAD.Vector(back_w_init, 0, 0), FreeCAD.Vector(back_w_init, back_h_init, 0)))
sk_back.addGeometry(Part.LineSegment(FreeCAD.Vector(back_w_init, back_h_init, 0), FreeCAD.Vector(0, back_h_init, 0)))
sk_back.addGeometry(Part.LineSegment(FreeCAD.Vector(0, back_h_init, 0), FreeCAD.Vector(0, 0, 0)))
for i in range(4):
    sk_back.addConstraint(Sketcher.Constraint("Coincident", i, 2, (i+1)%4, 1))
# Lock point 0 to sketch origin (-1, 1) to prevent drift
sk_back.addConstraint(Sketcher.Constraint("Coincident", 0, 1, -1, 1))
sk_back.addConstraint(Sketcher.Constraint("Horizontal", 0))
sk_back.addConstraint(Sketcher.Constraint("Vertical", 1))
sk_back.addConstraint(Sketcher.Constraint("Horizontal", 2))
sk_back.addConstraint(Sketcher.Constraint("Vertical", 3))

# Width and Height constraints
sk_back.addConstraint(Sketcher.Constraint("DistanceX", 0, 1, 0, 2, back_w_init))
sk_back.setExpression(f"Constraints[{len(sk_back.Constraints)-1}]", "CabinetParameters.InnerWidth - 2 * CabinetParameters.DoorClearance")

# Cutout for IEC320 C14 Power Module (snap-in 2.0" x 1.25" at Y=+6.0", Z=4.0")
iec_local_x = (CABINET_INNER_WIDTH / 2.0 + 6.0 - 1.0) * INCH
iec_local_y = 4.0 * INCH
sk_back.addGeometry(Part.LineSegment(FreeCAD.Vector(iec_local_x, iec_local_y, 0), FreeCAD.Vector(iec_local_x + 2.0*INCH, iec_local_y, 0)))
sk_back.addGeometry(Part.LineSegment(FreeCAD.Vector(iec_local_x + 2.0*INCH, iec_local_y, 0), FreeCAD.Vector(iec_local_x + 2.0*INCH, iec_local_y + 1.25*INCH, 0)))
sk_back.addGeometry(Part.LineSegment(FreeCAD.Vector(iec_local_x + 2.0*INCH, iec_local_y + 1.25*INCH, 0), FreeCAD.Vector(iec_local_x, iec_local_y + 1.25*INCH, 0)))
sk_back.addGeometry(Part.LineSegment(FreeCAD.Vector(iec_local_x, iec_local_y + 1.25*INCH, 0), FreeCAD.Vector(iec_local_x, iec_local_y, 0)))
for i in range(4, 8):
    sk_back.addConstraint(Sketcher.Constraint("Coincident", i, 2, (4 + (i-4+1)%4), 1))

# Cam lock hole (Dia 0.75" at top center)
cam_x = (back_w_init / 2.0)
cam_y = (back_h_init - 3.0 * INCH)
sk_back.addGeometry(Part.Circle(FreeCAD.Vector(cam_x, cam_y, 0), FreeCAD.Vector(0,0,1), 0.375 * INCH))

# Place rear sketch directly at rear panel opening!
sk_back.Placement = FreeCAD.Placement(
    FreeCAD.Vector(
        in_to_mm(CABINET_DEPTH - BACK_WOOD_THICKNESS),
        in_to_mm(-CABINET_INNER_WIDTH / 2.0 + DOOR_CLEARANCE),
        in_to_mm(BASE_OFFSET_Z + DOOR_CLEARANCE)
    ),
    rot_face
)
sk_back.setExpression("Placement.Base.x", "CabinetParameters.CabinetDepth - CabinetParameters.BackWoodThickness")
sk_back.setExpression("Placement.Base.y", "-CabinetParameters.InnerWidth / 2 + CabinetParameters.DoorClearance")
sk_back.setExpression("Placement.Base.z", "CabinetParameters.BaseOffsetZ + CabinetParameters.DoorClearance")
grp_doors_shelves.addObject(sk_back)

back_panel = doc.addObject("Part::Extrusion", "Back_Access_Panel_1_4in")
back_panel.Base = sk_back
back_panel.DirMode = "Custom"
back_panel.Dir = FreeCAD.Vector(1, 0, 0)
back_panel.setExpression("LengthFwd", "CabinetParameters.BackWoodThickness")
back_panel.Solid = True
grp_doors_shelves.addObject(back_panel)
set_style(back_panel, COL_BACK_14)

# 3. Internal Equipment Shelf (With 2.25" Rear Cable Drop Slot!)
# Sits at Z = 16.00", X = 1.50" to 15.50" (flush with back of door jamb stop cleats, zero overlap!)
shelf_obj = doc.addObject("Part::Box", "Internal_Cabinet_Shelf")
shelf_obj.setExpression("Length", "CabinetParameters.ShelfDepth")
shelf_obj.setExpression("Width", "CabinetParameters.InnerWidth")
shelf_obj.setExpression("Height", "CabinetParameters.WoodThickness")
shelf_obj.setExpression("Placement.Base.x", "2 * CabinetParameters.WoodThickness")
shelf_obj.setExpression("Placement.Base.y", "-CabinetParameters.InnerWidth / 2")
shelf_obj.setExpression("Placement.Base.z", "CabinetParameters.ShelfHeight")
grp_doors_shelves.addObject(shelf_obj)
set_style(shelf_obj, COL_BLACK_PAINT)

# 4. Shelf Support Cleats (3/4" x 3/4" x 12.0" birch cleats)
sc_l = doc.addObject("Part::Box", "Shelf_Cleat_Left")
sc_l.Length = in_to_mm(12.0)
sc_l.Width = in_to_mm(0.75)
sc_l.Height = in_to_mm(0.75)
sc_l.Placement.Base.x = in_to_mm(2.25)
sc_l.setExpression("Placement.Base.y", "CabinetParameters.InnerWidth / 2 - 0.75 in")
sc_l.setExpression("Placement.Base.z", "CabinetParameters.ShelfHeight - 0.75 in")
grp_doors_shelves.addObject(sc_l)
set_style(sc_l, COL_WOOD_EDGE)

sc_r = doc.addObject("Part::Box", "Shelf_Cleat_Right")
sc_r.Length = in_to_mm(12.0)
sc_r.Width = in_to_mm(0.75)
sc_r.Height = in_to_mm(0.75)
sc_r.Placement.Base.x = in_to_mm(2.25)
sc_r.setExpression("Placement.Base.y", "-CabinetParameters.InnerWidth / 2")
sc_r.setExpression("Placement.Base.z", "CabinetParameters.ShelfHeight - 0.75 in")
grp_doors_shelves.addObject(sc_r)
set_style(sc_r, COL_WOOD_EDGE)

# =============================================================================
# 5. GROUP 03: BASE & FEET
# =============================================================================
print("  [*] Building 03 Base & Feet...")

# 1. Bottom Base Plate (Elevated 3/4" off floor, Z = 0.75" to 1.50")
base_plate = doc.addObject("Part::Box", "Bottom_Base_Plate")
base_plate.setExpression("Length", "(CabinetParameters.CabinetDepth - CabinetParameters.WoodThickness) - (CabinetParameters.ToeKickDepth + CabinetParameters.WoodThickness)")
base_plate.setExpression("Width", "CabinetParameters.InnerWidth")
base_plate.setExpression("Height", "CabinetParameters.WoodThickness")
base_plate.setExpression("Placement.Base.x", "CabinetParameters.ToeKickDepth + CabinetParameters.WoodThickness")
base_plate.setExpression("Placement.Base.y", "-CabinetParameters.InnerWidth / 2")
base_plate.setExpression("Placement.Base.z", "CabinetParameters.BaseOffsetZ")
grp_base_feet.addObject(base_plate)
set_style(base_plate, COL_BLACK_PAINT)

# 2. Four 3/4" Plywood Corner Blocks (Flush with Side Panels & Toe Kick at Z = 0.00"!)
block_size = 3.50
front_blk_x = TOE_KICK_DEPTH + WOOD_THICKNESS + 0.125
rear_blk_x  = (CABINET_DEPTH - WOOD_THICKNESS) - block_size - 0.125

corner_defs = [
    ("FL", front_blk_x, "CabinetParameters.InnerWidth / 2 - 3.625 in"),
    ("FR", front_blk_x, "-CabinetParameters.InnerWidth / 2 + 0.125 in"),
    ("RL", rear_blk_x,  "CabinetParameters.InnerWidth / 2 - 3.625 in"),
    ("RR", rear_blk_x,  "-CabinetParameters.InnerWidth / 2 + 0.125 in"),
]

for c_name, bx, by_expr in corner_defs:
    s_blk = doc.addObject("Part::Box", f"Corner_Block_{c_name}")
    s_blk.Length = in_to_mm(block_size)
    s_blk.Width  = in_to_mm(block_size)
    s_blk.setExpression("Height", "CabinetParameters.BaseOffsetZ")
    s_blk.Placement.Base.x = in_to_mm(bx)
    s_blk.setExpression("Placement.Base.y", by_expr)
    s_blk.Placement.Base.z = 0.0
    grp_base_feet.addObject(s_blk)
    set_style(s_blk, COL_WOOD_EDGE)

    # Centered heavy-duty leveler glide (Z = -0.20" to 0.00")
    cx = bx + block_size / 2.0
    cy_init = (CABINET_INNER_WIDTH / 2.0 - 0.125 - block_size / 2.0) if "L" in c_name else (-CABINET_INNER_WIDTH / 2.0 + 0.125 + block_size / 2.0)
    
    s_glide = doc.addObject("Part::Cylinder", f"Leveler_Glide_{c_name}")
    s_glide.Radius = in_to_mm(0.55)
    s_glide.Height = in_to_mm(0.20)
    s_glide.Placement.Base = FreeCAD.Vector(cx * INCH, cy_init * INCH, -0.20 * INCH)
    grp_base_feet.addObject(s_glide)
    set_style(s_glide, COL_STEEL_DARK)

    # Threaded steel stem (Z = 0.00" to 1.00")
    s_stem = doc.addObject("Part::Cylinder", f"Leveler_Stem_{c_name}")
    s_stem.Radius = in_to_mm(0.125)
    s_stem.Height = in_to_mm(1.00)
    s_stem.Placement.Base = FreeCAD.Vector(cx * INCH, cy_init * INCH, 0.0)
    grp_base_feet.addObject(s_stem)
    set_style(s_stem, COL_CHROME)

# =============================================================================
# 6. GROUP 04: CONTROLS
# =============================================================================
print("  [*] Building 04 Controls...")

# 1. Control Panel Support Shelf (31.5" Wide Overhanging Wing Shelf)
# Perfectly centered across Y=0: Y = -CPWidth/2 to +CPWidth/2!
cp_shelf = doc.addObject("Part::Box", "Control_Panel_Shelf")
cp_shelf.setExpression("Length", "CabinetParameters.CPDepth")
cp_shelf.setExpression("Width", "CabinetParameters.CPWidth")
cp_shelf.setExpression("Height", "CabinetParameters.WoodThickness")
cp_shelf.setExpression("Placement.Base.x", "-CabinetParameters.CPDepth / 2")
cp_shelf.setExpression("Placement.Base.y", "-CabinetParameters.CPWidth / 2")
cp_shelf.setExpression("Placement.Base.z", "CabinetParameters.CPShelfHeight - CabinetParameters.WoodThickness")
grp_controls.addObject(cp_shelf)
set_style(cp_shelf, COL_BLACK_PAINT)

# 2. Slide-out Keyboard Tray (21.0" W x 9.0" D x 0.75" T)
# Centered across Y=0: Y = -KeyboardTrayW/2 to +KeyboardTrayW/2!
kb_tray = doc.addObject("Part::Box", "Keyboard_Tray")
kb_tray.setExpression("Length", "CabinetParameters.KeyboardTrayD")
kb_tray.setExpression("Width", "CabinetParameters.KeyboardTrayW")
kb_tray.Height = in_to_mm(0.75)
kb_tray.setExpression("Placement.Base.x", "-CabinetParameters.CPDepth / 2 + 0.5 in")
kb_tray.setExpression("Placement.Base.y", "-CabinetParameters.KeyboardTrayW / 2")
kb_tray.Placement.Base.z = in_to_mm(kb_bottom_z + 0.35)
grp_controls.addObject(kb_tray)
set_style(kb_tray, COL_STEEL_DARK)

# 3. User's Remeasured 31.5" Control Box (Prismatic Solid with Palm Rest)
cbox_pts = [
    (cp_rear_x - 10.25, console_base_z),                          # Front bottom
    (cp_rear_x - 12.00, console_base_z + 1.25),                   # Palm rest overhang
    (cp_rear_x - 12.00, console_base_z + CP_HEIGHT_FRONT),        # Palm rest top front (37.75")
    (cp_rear_x,         console_base_z + CP_HEIGHT_BACK),         # Console top rear (39.25")
    (cp_rear_x,         console_base_z),                          # Console bottom rear
]
sk_cbox = doc.addObject("Sketcher::SketchObject", "Sketch_User_Control_Box")
sk_cbox.MapMode = "Deactivated"
sk_cbox.Placement = FreeCAD.Placement(
    FreeCAD.Vector(0, in_to_mm(-CP_WIDTH / 2.0), 0),
    FreeCAD.Rotation(FreeCAD.Vector(1, 0, 0), 90)
)
sk_cbox.setExpression("Placement.Base.y", "-CabinetParameters.CPWidth / 2")
for i in range(len(cbox_pts)):
    p1 = FreeCAD.Vector(cbox_pts[i][0] * INCH, cbox_pts[i][1] * INCH, 0)
    p2 = FreeCAD.Vector(cbox_pts[(i+1)%len(cbox_pts)][0] * INCH, cbox_pts[(i+1)%len(cbox_pts)][1] * INCH, 0)
    sk_cbox.addGeometry(Part.LineSegment(p1, p2))
for i in range(len(cbox_pts)):
    sk_cbox.addConstraint(Sketcher.Constraint("Coincident", i, 2, (i+1)%len(cbox_pts), 1))

cbox_ext = doc.addObject("Part::Extrusion", "User_Control_Box")
cbox_ext.Base = sk_cbox
cbox_ext.DirMode = "Custom"
cbox_ext.Dir = FreeCAD.Vector(0, 1, 0)
cbox_ext.setExpression("LengthFwd", "CabinetParameters.CPWidth")
cbox_ext.Solid = True
grp_controls.addObject(sk_cbox)
grp_controls.addObject(cbox_ext)
set_style(cbox_ext, (0.18, 0.18, 0.20))

# Joysticks and Player Buttons (Symmetrically arranged around Y=0)
# Facing the cabinet: LEFT is +Y (Player 1), RIGHT is -Y (Player 2)
# For each player, joystick is operated by left hand (more +Y) and buttons by right hand (more -Y)
cp_slope = (CP_HEIGHT_BACK - CP_HEIGHT_FRONT) / 10.25 # slope of console top face

for p_num, p_center_y, col_btn in [(1, 7.5, (0.2, 0.5, 0.9)), (2, -7.5, (0.9, 0.2, 0.2))]:
    # Joystick is 2.0" to the player's left of their station center
    joy_x = cp_rear_x - 6.0
    joy_y = p_center_y + 2.0
    joy_surface_z = console_rear_top_z - (cp_rear_x - joy_x) * cp_slope
    joy_z_top = joy_surface_z + 2.5
    
    # Shaft
    s_shaft = doc.addObject("Part::Cylinder", f"Player_{p_num}_Joystick_Shaft")
    s_shaft.Radius = in_to_mm(0.15)
    s_shaft.Height = in_to_mm(2.0)
    s_shaft.Placement.Base = FreeCAD.Vector(joy_x * INCH, joy_y * INCH, (joy_z_top - 2.0) * INCH)
    grp_controls.addObject(s_shaft)
    set_style(s_shaft, COL_CHROME)

    # Balltop
    s_ball = doc.addObject("Part::Sphere", f"Player_{p_num}_Joystick_Ball")
    s_ball.Radius = in_to_mm(0.65)
    s_ball.Placement.Base = FreeCAD.Vector(joy_x * INCH, joy_y * INCH, joy_z_top * INCH)
    grp_controls.addObject(s_ball)
    set_style(s_ball, col_btn)

    # 6 Action Buttons (2 rows x 3 columns, to the player's right of joystick)
    for row in range(2):
        for col in range(3):
            bx = joy_x + (col - 1) * 1.3 - 0.5 - row * 1.3
            by = p_center_y - 0.25 - col * 1.3 - row * 0.4 # rightwards (decreasing Y)
            bz = console_rear_top_z - (cp_rear_x - bx) * cp_slope + 0.05
            s_btn = doc.addObject("Part::Cylinder", f"Player_{p_num}_Button_R{row}_C{col}")
            s_btn.Radius = in_to_mm(0.45)
            s_btn.Height = in_to_mm(0.30)
            s_btn.Placement.Base = FreeCAD.Vector(bx * INCH, by * INCH, bz * INCH)
            grp_controls.addObject(s_btn)
            set_style(s_btn, (0.9, 0.7, 0.1) if row == 0 else col_btn)

# =============================================================================
# 7. GROUP 05: DISPLAY & SOUND
# =============================================================================
print("  [*] Building 05 Display & Sound...")

# 1. Monitor Bezel Board (3/4" White Birch VC, angled 33.93°)
# Centerline Y=0: Screen active cutout 14.88" x 11.95" & button notch 1.06" x 2.55"
bezel_pts = [
    (cp_rear_x, console_rear_top_z),
    (cp_rear_x + WOOD_THICKNESS * math.sin(angle_bezel), console_rear_top_z + bezel_bot_dz),
    (x_bezel_top + WOOD_THICKNESS * math.sin(angle_bezel), z_bezel_top + miter_bezel_spk_dz),
    (x_bezel_top, z_bezel_top)
]
ext_bezel_raw = make_xz_profile_extrusion("Monitor_Bezel_Base", bezel_pts, grp_display_sound, COL_BEZEL)

# Screen Cutter Box (Centered at Y = 0!)
scr_w = 14.88
scr_h = 11.95
scr_z_start = (bezel_len - 13.55) / 2.0 + 1.15
notch_w = 1.06
notch_h = 2.55
notch_z_start = 1.60

rot_b = FreeCAD.Rotation(FreeCAD.Vector(0, 1, 0), math.degrees(angle_bezel))
pos_b = FreeCAD.Vector(cp_rear_x * INCH, 0, console_rear_top_z * INCH)
plc_b = FreeCAD.Placement(pos_b, rot_b)

scr_cutter = doc.addObject("Part::Box", "Screen_Cutter")
scr_cutter.Length = in_to_mm(WOOD_THICKNESS + 2.0)
scr_cutter.Width  = in_to_mm(scr_w)
scr_cutter.Height = in_to_mm(scr_h)
scr_cutter.Placement = plc_b.multiply(FreeCAD.Placement(FreeCAD.Vector(-1.0 * INCH, -scr_w/2.0 * INCH, scr_z_start * INCH), FreeCAD.Rotation()))

# Dell P1913S OSD button bar is at bottom-right of front bezel (-Y when facing monitor)
notch_cutter = doc.addObject("Part::Box", "OSD_Notch_Cutter")
notch_cutter.Length = in_to_mm(WOOD_THICKNESS + 2.0)
notch_cutter.Width  = in_to_mm(notch_w)
notch_cutter.Height = in_to_mm(notch_h)
notch_cutter.Placement = plc_b.multiply(FreeCAD.Placement(FreeCAD.Vector(-1.0 * INCH, (-scr_w/2.0 - notch_w) * INCH, notch_z_start * INCH), FreeCAD.Rotation()))

cut_bez1 = doc.addObject("Part::Cut", "Monitor_Bezel_Cut1")
cut_bez1.Base = ext_bezel_raw
cut_bez1.Tool = scr_cutter

bezel_final = doc.addObject("Part::Cut", "Monitor_Bezel_Board")
bezel_final.Base = cut_bez1
bezel_final.Tool = notch_cutter
grp_display_sound.addObject(bezel_final)
set_style(bezel_final, COL_BEZEL)

# 2. Dell P1913S 19" LCD Monitor Assembly (Centered at Y=0)
mon_w = 16.35
mon_h = 13.55
mon_thick = 2.10
mon_z_start = (bezel_len - mon_h) / 2.0

mon_chassis = doc.addObject("Part::Box", "Dell_P1913S_Chassis")
mon_chassis.Length = in_to_mm(mon_thick)
mon_chassis.Width  = in_to_mm(mon_w)
mon_chassis.Height = in_to_mm(mon_h)
mon_chassis.Placement = plc_b.multiply(FreeCAD.Placement(FreeCAD.Vector(WOOD_THICKNESS * INCH, -mon_w/2.0 * INCH, mon_z_start * INCH), FreeCAD.Rotation()))
grp_display_sound.addObject(mon_chassis)
set_style(mon_chassis, COL_BEZEL)

mon_glass = doc.addObject("Part::Box", "Dell_P1913S_LCD_Screen")
mon_glass.Length = in_to_mm(0.05)
mon_glass.Width  = in_to_mm(14.85)
mon_glass.Height = in_to_mm(11.95)
mon_glass.Placement = plc_b.multiply(FreeCAD.Placement(FreeCAD.Vector((WOOD_THICKNESS + 0.06) * INCH, -14.85/2.0 * INCH, scr_z_start * INCH), FreeCAD.Rotation()))
grp_display_sound.addObject(mon_glass)
set_style(mon_glass, COL_SCREEN)

# 3. VESA Mount Crossbar (Centered at Y=0, spanning across InnerWidth)
vesa_z_center = mon_z_start + mon_h / 2.0
vesa_raw = doc.addObject("Part::Box", "VESA_Mount_Crossbar_Base")
vesa_raw.setExpression("Length", "CabinetParameters.WoodThickness")
vesa_raw.setExpression("Width", "CabinetParameters.InnerWidth")
vesa_raw.setExpression("Height", "CabinetParameters.VESACrossbarHeight")
# In bezel local coordinates: X = WOOD_THICKNESS + mon_thick, Y = -InnerWidth/2, Z = vesa_z_center - VESA_HEIGHT/2
vesa_raw.Placement = plc_b.multiply(FreeCAD.Placement(
    FreeCAD.Vector((WOOD_THICKNESS + mon_thick) * INCH, -CABINET_INNER_WIDTH/2.0 * INCH, (vesa_z_center - VESACrossbar_HEIGHT/2.0) * INCH),
    FreeCAD.Rotation()
))
grp_display_sound.addObject(vesa_raw)
set_style(vesa_raw, COL_BLACK_PAINT)

# 4. Speaker Board (Angled 42.27°, two 3.75" speaker holes symmetrically placed)
spk_pts = [
    (x_bezel_top, z_bezel_top),
    (x_bezel_top + WOOD_THICKNESS * math.cos(math.radians(angle_spk_from_vert)), z_bezel_top - miter_bezel_spk_dz),
    (x_marquee_bottom + WOOD_THICKNESS * math.cos(math.radians(angle_spk_from_vert)), z_marquee_bottom + spk_top_dz),
    (x_marquee_bottom, z_marquee_bottom)
]
ext_spk_raw = make_xz_profile_extrusion("Speaker_Board_Base", spk_pts, grp_display_sound, COL_BLACK_PAINT)

# Speaker Holes (Cut at Left Y = +6.0" and Right Y = -6.0")
rot_spk_deg = math.degrees(math.atan2(dx_spk, dz_spk))
plc_s = FreeCAD.Placement(FreeCAD.Vector(x_bezel_top * INCH, 0, z_bezel_top * INCH), FreeCAD.Rotation(FreeCAD.Vector(0, 1, 0), rot_spk_deg))

spk_cyl_l = doc.addObject("Part::Cylinder", "Speaker_Hole_L")
spk_cyl_l.Radius = in_to_mm(1.875)
spk_cyl_l.Height = in_to_mm(WOOD_THICKNESS + 2.0)
spk_cyl_l.Placement = plc_s.multiply(FreeCAD.Placement(FreeCAD.Vector(-1.0 * INCH, 6.0 * INCH, panel_len_spk / 2.0 * INCH), FreeCAD.Rotation(FreeCAD.Vector(0, 1, 0), 90)))

spk_cyl_r = doc.addObject("Part::Cylinder", "Speaker_Hole_R")
spk_cyl_r.Radius = in_to_mm(1.875)
spk_cyl_r.Height = in_to_mm(WOOD_THICKNESS + 2.0)
spk_cyl_r.Placement = plc_s.multiply(FreeCAD.Placement(FreeCAD.Vector(-1.0 * INCH, -6.0 * INCH, panel_len_spk / 2.0 * INCH), FreeCAD.Rotation(FreeCAD.Vector(0, 1, 0), 90)))

cut_spk1 = doc.addObject("Part::Cut", "Speaker_Cut1")
cut_spk1.Base = ext_spk_raw
cut_spk1.Tool = spk_cyl_l

spk_final = doc.addObject("Part::Cut", "Speaker_Board")
spk_final.Base = cut_spk1
spk_final.Tool = spk_cyl_r
grp_display_sound.addObject(spk_final)
set_style(spk_final, COL_BLACK_PAINT)

# 5. Marquee Sign Assembly (Translucent Acrylic, centered at Y=0)
marq_pts = [
    (x_marquee_bottom, z_marquee_bottom),
    (x_marquee_bottom + 0.125, z_marquee_bottom),
    (x_marquee_top + 0.125, z_marquee_top),
    (x_marquee_top, z_marquee_top)
]
make_xz_profile_extrusion("Marquee_Sign", marq_pts, grp_display_sound, COL_MARQUEE)

# =============================================================================
# 8. GROUP 06: HARDWARE & ELECTRONICS
# =============================================================================
print("  [*] Building 06 Hardware & Electronics...")

# 1. Front Door Continuous Piano Hinge in 1/16" Right Reveal Gap (-Y)
# Centered at Y = -InnerWidth/2 + DoorClearance/2 (-11.46875")
door_h_total = (diag_front_z - TOE_KICK_HEIGHT) - 2.0 * DOOR_CLEARANCE
hinge_pin = doc.addObject("Part::Cylinder", "Door_Piano_Hinge")
hinge_pin.Radius = in_to_mm(0.0625) # Dia 1/8"
hinge_pin.Height = in_to_mm(door_h_total - 0.5)
hinge_pin.Placement.Base = FreeCAD.Vector(
    -0.02 * INCH,
    (-CABINET_INNER_WIDTH / 2.0 + DOOR_CLEARANCE / 2.0) * INCH,
    (TOE_KICK_HEIGHT + DOOR_CLEARANCE + 0.25) * INCH
)
grp_hardware.addObject(hinge_pin)
set_style(hinge_pin, COL_CHROME)

# 2. Door Magnetic Catch Housing & Steel Strike Plate on Left Jamb (+Y)
# Mounted on left stop cleat at Y = +InnerWidth/2 - 0.375" (+11.125")
mag_y = CABINET_INNER_WIDTH / 2.0 - 0.375
mag_z = TOE_KICK_HEIGHT + DOOR_CLEARANCE + door_h_total - 2.50

mag_body = doc.addObject("Part::Cylinder", "Door_Magnetic_Catch")
mag_body.Radius = in_to_mm(0.35)
mag_body.Height = in_to_mm(0.80)
mag_body.Placement.Base = FreeCAD.Vector((WOOD_THICKNESS + 0.40) * INCH, mag_y * INCH, mag_z * INCH)
mag_body.Placement.Rotation = FreeCAD.Rotation(FreeCAD.Vector(0, 1, 0), 90)
grp_hardware.addObject(mag_body)
set_style(mag_body, COL_CHROME)

mag_strike = doc.addObject("Part::Cylinder", "Door_Strike_Plate")
mag_strike.Radius = in_to_mm(0.38)
mag_strike.Height = in_to_mm(0.06)
mag_strike.Placement.Base = FreeCAD.Vector((WOOD_THICKNESS - 0.03) * INCH, mag_y * INCH, mag_z * INCH)
mag_strike.Placement.Rotation = FreeCAD.Rotation(FreeCAD.Vector(0, 1, 0), 90)
grp_hardware.addObject(mag_strike)
set_style(mag_strike, COL_STEEL_DARK)

# 3. uxcell Mini Round Rocker Switch (Mounted on Right Side Panel at -Y)
sw_bezel = doc.addObject("Part::Cylinder", "Side_Rocker_Switch_Bezel")
sw_bezel.Radius = in_to_mm(0.455)
sw_bezel.Height = in_to_mm(0.10)
sw_bezel.Placement.Base = FreeCAD.Vector(sw_x * INCH, (-CABINET_INNER_WIDTH / 2.0 - WOOD_THICKNESS) * INCH, sw_z * INCH)
sw_bezel.Placement.Rotation = FreeCAD.Rotation(FreeCAD.Vector(1, 0, 0), 90)
grp_hardware.addObject(sw_bezel)
set_style(sw_bezel, COL_BEZEL)

sw_btn = doc.addObject("Part::Cylinder", "Side_Rocker_Switch_Button")
sw_btn.Radius = in_to_mm(0.355)
sw_btn.Height = in_to_mm(0.12)
sw_btn.Placement.Base = FreeCAD.Vector(sw_x * INCH, (-CABINET_INNER_WIDTH / 2.0 - WOOD_THICKNESS - 0.03) * INCH, sw_z * INCH)
sw_btn.Placement.Rotation = FreeCAD.Rotation(FreeCAD.Vector(1, 0, 0), 90)
grp_hardware.addObject(sw_btn)
set_style(sw_btn, COL_RED_LED)

# 4. IEC320 C14 Power Socket Inlet Module (Snaps into 1/4" Rear Access Panel)
iec_y = 6.00
iec_z = BASE_OFFSET_Z + 4.00
iec_body = doc.addObject("Part::Box", "IEC_Power_Socket_Module")
iec_body.Length = in_to_mm(0.12)
iec_body.Width  = in_to_mm(2.00)
iec_body.Height = in_to_mm(1.25)
iec_body.Placement.Base = FreeCAD.Vector((CABINET_DEPTH - 0.05) * INCH, (iec_y - 1.0) * INCH, (iec_z - 0.62) * INCH)
grp_hardware.addObject(iec_body)
set_style(iec_body, COL_CHROME)

iec_cord = doc.addObject("Part::Cylinder", "AC_Power_Cord_Plug")
iec_cord.Radius = in_to_mm(0.50)
iec_cord.Height = in_to_mm(1.20)
iec_cord.Placement.Base = FreeCAD.Vector((CABINET_DEPTH + 0.07) * INCH, (iec_y - 0.35) * INCH, iec_z * INCH)
iec_cord.Placement.Rotation = FreeCAD.Rotation(FreeCAD.Vector(0, 1, 0), 90)
grp_hardware.addObject(iec_cord)
set_style(iec_cord, COL_BEZEL)

# 5. Floor Subwoofer (On base plate, centered at Y=0)
sub_size = 9.0
sub_x = TOE_KICK_DEPTH + WOOD_THICKNESS + 1.50
sub_box = doc.addObject("Part::Box", "Floor_Subwoofer_Cabinet")
sub_box.Length = in_to_mm(sub_size)
sub_box.Width  = in_to_mm(sub_size)
sub_box.Height = in_to_mm(sub_size)
sub_box.Placement.Base = FreeCAD.Vector(sub_x * INCH, -sub_size/2.0 * INCH, (BASE_OFFSET_Z + WOOD_THICKNESS) * INCH)
grp_hardware.addObject(sub_box)
set_style(sub_box, (0.30, 0.30, 0.32))

sub_cone = doc.addObject("Part::Cylinder", "Floor_Subwoofer_Driver")
sub_cone.Radius = in_to_mm(3.25)
sub_cone.Height = in_to_mm(0.20)
sub_cone.Placement.Base = FreeCAD.Vector((sub_x - 0.05) * INCH, 0, (BASE_OFFSET_Z + WOOD_THICKNESS + sub_size/2.0) * INCH)
sub_cone.Placement.Rotation = FreeCAD.Rotation(FreeCAD.Vector(0, 1, 0), -90)
grp_hardware.addObject(sub_cone)
set_style(sub_cone, COL_STEEL_DARK)

# 6. Raspberry Pi 4/5 Assembly on Equipment Shelf (Centered at Y=0)
pi_x = 2 * WOOD_THICKNESS + SHELF_DEPTH / 2.0
pi_z = SHELF_HEIGHT + WOOD_THICKNESS
pi_pcb = doc.addObject("Part::Box", "Raspberry_Pi_PCB")
pi_pcb.Length = in_to_mm(3.35)
pi_pcb.Width  = in_to_mm(2.30)
pi_pcb.Height = in_to_mm(0.06)
pi_pcb.Placement.Base = FreeCAD.Vector((pi_x - 1.675) * INCH, -1.15 * INCH, (pi_z + 0.25) * INCH)
grp_hardware.addObject(pi_pcb)
set_style(pi_pcb, COL_PCB_GREEN)

pi_sink = doc.addObject("Part::Box", "Raspberry_Pi_Armor_Heatsink")
pi_sink.Length = in_to_mm(3.20)
pi_sink.Width  = in_to_mm(2.20)
pi_sink.Height = in_to_mm(0.45)
pi_sink.Placement.Base = FreeCAD.Vector((pi_x - 1.60) * INCH, -1.10 * INCH, (pi_z + 0.31) * INCH)
grp_hardware.addObject(pi_sink)
set_style(pi_sink, COL_CHROME)

# 7. Power Strip
pstrip = doc.addObject("Part::Box", "Cabinet_Power_Strip")
pstrip.Length = in_to_mm(8.50)
pstrip.Width  = in_to_mm(2.20)
pstrip.Height = in_to_mm(1.40)
pstrip.Placement.Base = FreeCAD.Vector((sub_x + 1.0) * INCH, 5.5 * INCH, (BASE_OFFSET_Z + WOOD_THICKNESS) * INCH)
grp_hardware.addObject(pstrip)
set_style(pstrip, COL_CHROME)

# =============================================================================
# 9. RECOMPUTE & AUDIT PANEL ALIGNMENTS
# =============================================================================
doc.recompute()

print("\n" + "=" * 75)
print("  AUDITING PANEL ALIGNMENTS (Y-MIDPLANE SYMMETRY)")
print("=" * 75)

audit_parts = [
    ("Side_Panel_Left", side_l),
    ("Side_Panel_Right", side_r),
    ("Toe_Kick_Board", tk_board),
    ("Lower_Front_Panel", door_panel),
    ("Back_Access_Panel_1_4in", back_panel),
    ("Console_Diagonal_Apron", doc.getObject("Console_Diagonal_Apron")),
    ("Keyboard_Bottom_Plate", doc.getObject("Keyboard_Bottom_Plate")),
    ("Top_Roof_Panel", doc.getObject("Top_Roof_Panel")),
    ("Internal_Cabinet_Shelf", shelf_obj),
    ("Bottom_Base_Plate", base_plate),
    ("Control_Panel_Shelf", cp_shelf),
    ("Keyboard_Tray", kb_tray),
    ("User_Control_Box", cbox_ext),
    ("Monitor_Bezel_Board", bezel_final),
    ("Speaker_Board", spk_final),
    ("Marquee_Sign", doc.getObject("Marquee_Sign")),
]

for name, obj in audit_parts:
    bb = obj.Shape.BoundBox
    y_min_in = bb.YMin / INCH
    y_max_in = bb.YMax / INCH
    y_mid_in = (y_min_in + y_max_in) / 2.0
    width_in = y_max_in - y_min_in
    print(f"  {name:25s} | Y: [{y_min_in:7.3f}\", {y_max_in:7.3f}\"] | Width: {width_in:6.3f}\" | Mid: {y_mid_in:6.3f}\"")

# =============================================================================
# 10. GROUP 07: TECHNICAL SHOP DRAWINGS (TECHDRAW WORKBENCH)
# =============================================================================
print("  [*] Building 07 Technical Drawings (Complete 5-Sheet Shop Blueprint Set)...")

grp_drawings = doc.addObject("App::DocumentObjectGroup", "07_Technical_Drawings")
grp_drawings.Label = "07 Technical Drawings (Shop Sheets)"

tmpl_file = "/home/scott/20p/cad/arcade/drawing_template.svg"

def setup_page(name, label, title1, title2, title3, sheet_str, scale_str):
    p = doc.addObject("TechDraw::DrawPage", name)
    p.Label = label
    t = doc.addObject("TechDraw::DrawSVGTemplate", f"Template_{name}")
    t.Template = tmpl_file
    p.Template = t
    doc.recompute()
    t.setEditFieldContent("DrawingTitle1", title1)
    t.setEditFieldContent("DrawingTitle2", title2)
    t.setEditFieldContent("DrawingTitle3", title3)
    t.setEditFieldContent("DrawnBy", "Scott Kirkwood")
    t.setEditFieldContent("Sheet", sheet_str)
    t.setEditFieldContent("scale", scale_str)
    t.setEditFieldContent("CompanyName", "ARCADE SHOP BLUEPRINTS")
    t.setEditFieldContent("CompanyAddress", "ALL UNITS: INCHES / DEGREES")
    grp_drawings.addObject(p)
    return p, t

def add_dim(page, view, dir_idx, x_pos, y_pos):
    edges = view.getVisibleEdges()
    if edges:
        dim = TechDraw.makeExtentDim(view, [e for e in edges], dir_idx)
        page.addView(dim)
        dim.X = x_pos
        dim.Y = y_pos
        dim.ShowUnits = True
        dim.FormatSpec = "%.2w"
        return dim
    return None

# =============================================================================
# SHEET 1: SIDE PANEL MASTER TEMPLATE & 15-VERTEX COORDINATES
# =============================================================================
p1, t1 = setup_page(
    "Drawing_Page_01_Side_Panel",
    "Sheet 1 - Side Panel Profile & 15-Vertex Coordinates",
    "PARAMETRIC ARCADE CABINET",
    "SHEET 1: SIDE PANEL 15-VERTEX PROFILE",
    "3/4\" WHITE BIRCH VC PLYWOOD (2 REQUIRED)",
    "1 OF 5", "1 : 10"
)

v_side = doc.addObject("TechDraw::DrawViewPart", "View_Side_Panel_Profile")
v_side.Source = doc.getObject("Side_Panel_Left")
v_side.Direction = FreeCAD.Vector(0, 1, 0)
v_side.XDirection = FreeCAD.Vector(1, 0, 0)
v_side.ScaleType = "Custom"
v_side.Scale = 0.10
p1.addView(v_side)
v_side.X = 110.0
v_side.Y = 145.0
doc.recompute()

add_dim(p1, v_side, 0, 110.0, 35.0)  # Width (Depth 25.25 in)
add_dim(p1, v_side, 1, 40.0, 145.0)   # Height (65.25 in)

a1_coords = doc.addObject("TechDraw::DrawViewAnnotation", "Annotation_Sheet1_Coordinates")
a1_coords.Text = [
    "SIDE PANEL 15-VERTEX COORDINATE MAP (Inches from Origin [0, 0])",
    "==================================================================",
    "P0:  (X=+2.25, Z= 0.00) - Toe-kick riser base at floor",
    "P1:  (X=+2.25, Z=+4.50) - Top of toe-kick recess (4.50\" rise)",
    "P2:  (X=-1.00, Z=+4.50) - Front lower lip corner (1.00\" perimeter reveal)",
    "P3:  (X=-1.00, Z=+23.50) - Top of coin door lip (vertical front edge)",
    "P4:  (X=-6.25, Z=+29.25) - Apron corbel diagonal (47.60° rake, 42.40° miter)",
    "P5:  (X=-6.25, Z=+33.25) - Front vertical cheek of keyboard cavity (4.00\" high)",
    "P6:  (X=+5.25, Z=+33.25) - Control panel shelf support ledge (11.50\" deep)",
    "P7:  (X=+5.25, Z=+40.00) - Vertical rise behind control console (6.75\" high)",
    "P8:  (X=+6.00, Z=+42.16) - Transition angle to monitor cheek",
    "P9:  (X=+13.19, Z=+52.84) - Monitor cheek angle (33.93° rake, 16.57\" length)",
    "P10: (X=+8.10, Z=+57.47) - Speaker cheek angle (47.73° rake, 7.43\" length)",
    "P11: (X=+6.75, Z=+63.50) - Marquee visor top edge (12.80° visor rake)",
    "P12: (X=+6.75, Z=+65.25) - Front top corner of 1.00\" roof perimeter lip",
    "P13: (X=+19.00, Z=+65.25) - Top rear roof corner (65.25\" total height)",
    "P14: (X=+19.00, Z= 0.00) - Bottom rear floor corner (20.00\" carcass depth)",
]
p1.addView(a1_coords)
a1_coords.X = 295.0
a1_coords.Y = 180.0
a1_coords.TextSize = 2.6

a1_notes = doc.addObject("TechDraw::DrawViewAnnotation", "Annotation_Sheet1_Notes")
a1_notes.Text = [
    "FABRICATION & TOOLING NOTES:",
    "------------------------------------------------------------------",
    "1. CUT TWO (2) MIRRORED PANELS from 3/4\" White Birch VC plywood.",
    "2. T-MOLDING: Slot entire outer perimeter with 1/16\" 3-wing slotting cutter.",
    "3. ROCKER SWITCH: On RIGHT Side Panel only, drill 20mm (0.787\") hole at",
    "   (X=15.00\", Z=34.00\") with 1.75\" dia x 0.50\" deep inside relief pocket.",
    "4. ALL CORBELS PARALLEL: Apron cheek maintains strict 1.00\" perimeter reveal.",
]
p1.addView(a1_notes)
a1_notes.X = 295.0
a1_notes.Y = 65.0
a1_notes.TextSize = 2.6

# =============================================================================
# SHEET 2: CARCASS STRUCTURE & BEVELED PANELS
# =============================================================================
p2, t2 = setup_page(
    "Drawing_Page_02_Carcass_Panels",
    "Sheet 2 - Carcass Structure & Beveled Panels",
    "PARAMETRIC ARCADE CABINET",
    "SHEET 2: CARCASS STRUCTURE & BEVELED PANELS",
    "3/4\" WHITE BIRCH VC PLYWOOD (ALL WIDTH = 23.000\")",
    "2 OF 5", "1 : 8"
)

# Apron
v_apron = doc.addObject("TechDraw::DrawViewPart", "View_Console_Apron")
v_apron.Source = doc.getObject("Console_Diagonal_Apron")
v_apron.Direction = FreeCAD.Vector(-0.7385, 0, -0.6743)
v_apron.XDirection = FreeCAD.Vector(0, -1, 0)
v_apron.ScaleType = "Custom"
v_apron.Scale = 0.09
p2.addView(v_apron)
v_apron.X = 85.0
v_apron.Y = 195.0
doc.recompute()
add_dim(p2, v_apron, 0, 85.0, 170.0)
add_dim(p2, v_apron, 1, 35.0, 195.0)

# Keyboard Bottom Plate
v_kb = doc.addObject("TechDraw::DrawViewPart", "View_KB_Plate")
v_kb.Source = doc.getObject("Keyboard_Bottom_Plate")
v_kb.Direction = FreeCAD.Vector(0, 0, 1)
v_kb.XDirection = FreeCAD.Vector(0, -1, 0)
v_kb.ScaleType = "Custom"
v_kb.Scale = 0.09
p2.addView(v_kb)
v_kb.X = 215.0
v_kb.Y = 195.0
doc.recompute()
add_dim(p2, v_kb, 0, 215.0, 170.0)
add_dim(p2, v_kb, 1, 165.0, 195.0)

# Top Roof Panel
v_roof = doc.addObject("TechDraw::DrawViewPart", "View_Roof_Panel")
v_roof.Source = doc.getObject("Top_Roof_Panel")
v_roof.Direction = FreeCAD.Vector(0, 0, 1)
v_roof.XDirection = FreeCAD.Vector(0, -1, 0)
v_roof.ScaleType = "Custom"
v_roof.Scale = 0.09
p2.addView(v_roof)
v_roof.X = 345.0
v_roof.Y = 195.0
doc.recompute()
add_dim(p2, v_roof, 0, 345.0, 170.0)
add_dim(p2, v_roof, 1, 295.0, 195.0)

# Equipment Shelf
v_shelf = doc.addObject("TechDraw::DrawViewPart", "View_Equip_Shelf")
v_shelf.Source = doc.getObject("Internal_Cabinet_Shelf")
v_shelf.Direction = FreeCAD.Vector(0, 0, 1)
v_shelf.XDirection = FreeCAD.Vector(0, -1, 0)
v_shelf.ScaleType = "Custom"
v_shelf.Scale = 0.075
p2.addView(v_shelf)
v_shelf.X = 85.0
v_shelf.Y = 100.0
doc.recompute()
add_dim(p2, v_shelf, 0, 85.0, 60.0)
add_dim(p2, v_shelf, 1, 35.0, 100.0)

# Base Plate
v_base = doc.addObject("TechDraw::DrawViewPart", "View_Base_Plate")
v_base.Source = doc.getObject("Bottom_Base_Plate")
v_base.Direction = FreeCAD.Vector(0, 0, 1)
v_base.XDirection = FreeCAD.Vector(0, -1, 0)
v_base.ScaleType = "Custom"
v_base.Scale = 0.075
p2.addView(v_base)
v_base.X = 215.0
v_base.Y = 100.0
doc.recompute()
add_dim(p2, v_base, 0, 215.0, 60.0)
add_dim(p2, v_base, 1, 165.0, 100.0)

a2_notes = doc.addObject("TechDraw::DrawViewAnnotation", "Annotation_Sheet2_Table")
a2_notes.Text = [
    "BEVEL CUTS & BLADE TILT SPECIFICATIONS:",
    "==================================================================",
    "1. CONSOLE DIAGONAL APRON (7.786\" x 23.000\" x 0.750\"): ",
    "   - Table saw blade tilt: 42.40° ON BOTH TOP AND BOTTOM ENDS.",
    "   - Parallel board with zero taper. Top meets KB plate at Z=29.25\".",
    "2. KEYBOARD BOTTOM PLATE (5.250\" x 23.000\" x 0.750\"): ",
    "   - Square 90° edges on all sides (Z=29.25\" to 30.00\").",
    "3. TOP ROOF PANEL (10.250\" x 23.000\" x 0.750\"): ",
    "   - Front edge blade tilt: 12.80° BEVEL; Rear edge square 90°.",
    "4. TOE KICK RISER (4.500\" x 23.000\" x 0.750\"): Square 90° cuts.",
    "5. TOE KICK CEILING (1.500\" x 23.000\" x 0.750\"): Square 90° cuts.",
    "6. DOOR HEADER RAIL (1.500\" x 23.000\" x 0.750\"): Anti-racking stretcher.",
    "7. EQUIPMENT SHELF (14.000\" x 23.000\" x 0.750\"): Leaves 2.25\" rear slot.",
    "8. BOTTOM BASE PLATE (14.250\" x 23.000\" x 0.750\"): Elevated 0.75\" Z.",
]
p2.addView(a2_notes)
a2_notes.X = 335.0
a2_notes.Y = 85.0
a2_notes.TextSize = 2.2

# =============================================================================
# SHEET 3: DISPLAY & SOUND PANELS (BEZEL, SPEAKERS, MARQUEE)
# =============================================================================
p3, t3 = setup_page(
    "Drawing_Page_03_Display_Sound",
    "Sheet 3 - Display & Sound Panels (Bezel & Speakers)",
    "PARAMETRIC ARCADE CABINET",
    "SHEET 3: DISPLAY & SOUND PANELS",
    "3/4\" WHITE BIRCH PLYWOOD (ALL WIDTH = 23.000\")",
    "3 OF 5", "1 : 8"
)

# Monitor Bezel
v_bezel = doc.addObject("TechDraw::DrawViewPart", "View_Bezel_Face")
v_bezel.Source = doc.getObject("Monitor_Bezel_Board")
v_bezel.Direction = FreeCAD.Vector(-0.8297, 0, 0.5582)
v_bezel.XDirection = FreeCAD.Vector(0, -1, 0)
v_bezel.ScaleType = "Custom"
v_bezel.Scale = 0.09
p3.addView(v_bezel)
v_bezel.X = 110.0
v_bezel.Y = 150.0
doc.recompute()
add_dim(p3, v_bezel, 0, 110.0, 75.0)
add_dim(p3, v_bezel, 1, 45.0, 150.0)

# Speaker Board
v_spk = doc.addObject("TechDraw::DrawViewPart", "View_Speaker_Face")
v_spk.Source = doc.getObject("Speaker_Board")
v_spk.Direction = FreeCAD.Vector(-0.6727, 0, -0.7399)
v_spk.XDirection = FreeCAD.Vector(0, -1, 0)
v_spk.ScaleType = "Custom"
v_spk.Scale = 0.09
p3.addView(v_spk)
v_spk.X = 280.0
v_spk.Y = 195.0
doc.recompute()
add_dim(p3, v_spk, 0, 280.0, 160.0)
add_dim(p3, v_spk, 1, 220.0, 195.0)

a3_notes = doc.addObject("TechDraw::DrawViewAnnotation", "Annotation_Sheet3_Specs")
a3_notes.Text = [
    "DISPLAY & SOUND FABRICATION SPECIFICATIONS:",
    "==================================================================",
    "1. MONITOR BEZEL BOARD (16.572\" x 23.000\" x 0.750\"): ",
    "   - Screen rake angle: 33.93° FROM VERTICAL.",
    "   - Bottom edge bevel: 33.93° BEVEL (mates with horizontal shelf).",
    "   - Top edge miter: 40.83° MITER (mates with speaker board).",
    "   - Active screen cutout: 14.88\" W x 11.95\" H (centered at Y=0,",
    "     located 2.66\" up from bottom face).",
    "   - Dell P1913S button notch: 1.06\" W x 2.55\" H at bottom-right corner.",
    "2. SPEAKER BOARD (7.433\" x 23.000\" x 0.750\"): ",
    "   - Speaker rake angle: 47.73° FROM VERTICAL.",
    "   - Bottom edge miter: 40.83° MITER (mates with bezel board).",
    "   - Top edge miter: 34.93° MITER (mates with marquee sign).",
    "   - Two speaker holes: Dia 3.750\" centered at Y = ±6.00\" (12.00\" spacing).",
    "3. MARQUEE SIGN (5.500\" x 23.000\" x 0.125\" Translucent Acrylic): ",
    "   - Rakes back 12.80° between speaker board and roof panel.",
]
p3.addView(a3_notes)
a3_notes.X = 285.0
a3_notes.Y = 80.0
a3_notes.TextSize = 2.3

# =============================================================================
# SHEET 4: CONTROLS, KEYBOARD DRAWER & ACCESS DOORS
# =============================================================================
p4, t4 = setup_page(
    "Drawing_Page_04_Controls_Doors",
    "Sheet 4 - Controls, Keyboard Drawer & Access Doors",
    "PARAMETRIC ARCADE CABINET",
    "SHEET 4: CONTROLS & ACCESS PANELS",
    "3/4\" & 1/4\" PLYWOOD (CONSOLE, DOORS, TRAY)",
    "4 OF 5", "1 : 10"
)

# Control Panel Shelf
v_cp = doc.addObject("TechDraw::DrawViewPart", "View_CP_Shelf")
v_cp.Source = doc.getObject("Control_Panel_Shelf")
v_cp.Direction = FreeCAD.Vector(0, 0, 1)
v_cp.XDirection = FreeCAD.Vector(0, -1, 0)
v_cp.ScaleType = "Custom"
v_cp.Scale = 0.075
p4.addView(v_cp)
v_cp.X = 105.0
v_cp.Y = 205.0
doc.recompute()
add_dim(p4, v_cp, 0, 105.0, 175.0)
add_dim(p4, v_cp, 1, 40.0, 205.0)

# Keyboard Tray
v_tray = doc.addObject("TechDraw::DrawViewPart", "View_KB_Tray")
v_tray.Source = doc.getObject("Keyboard_Tray")
v_tray.Direction = FreeCAD.Vector(0, 0, 1)
v_tray.XDirection = FreeCAD.Vector(0, -1, 0)
v_tray.ScaleType = "Custom"
v_tray.Scale = 0.075
p4.addView(v_tray)
v_tray.X = 330.0
v_tray.Y = 205.0
doc.recompute()
add_dim(p4, v_tray, 0, 330.0, 175.0)
add_dim(p4, v_tray, 1, 270.0, 205.0)

# Front Door
v_fdoor = doc.addObject("TechDraw::DrawViewPart", "View_Front_Door")
v_fdoor.Source = doc.getObject("Lower_Front_Panel")
v_fdoor.Direction = FreeCAD.Vector(-1, 0, 0)
v_fdoor.XDirection = FreeCAD.Vector(0, -1, 0)
v_fdoor.ScaleType = "Custom"
v_fdoor.Scale = 0.075
p4.addView(v_fdoor)
v_fdoor.X = 105.0
v_fdoor.Y = 95.0
doc.recompute()
add_dim(p4, v_fdoor, 0, 105.0, 45.0)
add_dim(p4, v_fdoor, 1, 40.0, 95.0)

# Back Access Panel
v_bdoor = doc.addObject("TechDraw::DrawViewPart", "View_Back_Panel")
v_bdoor.Source = doc.getObject("Back_Access_Panel_1_4in")
v_bdoor.Direction = FreeCAD.Vector(1, 0, 0)
v_bdoor.XDirection = FreeCAD.Vector(0, 1, 0)
v_bdoor.ScaleType = "Custom"
v_bdoor.Scale = 0.055
p4.addView(v_bdoor)
v_bdoor.X = 225.0
v_bdoor.Y = 110.0
doc.recompute()
add_dim(p4, v_bdoor, 0, 225.0, 35.0)
add_dim(p4, v_bdoor, 1, 185.0, 110.0)

a4_notes = doc.addObject("TechDraw::DrawViewAnnotation", "Annotation_Sheet4_Specs")
a4_notes.Text = [
    "CONTROLS & DOORS SPECIFICATIONS:",
    "==================================================================",
    "1. CONTROL PANEL SUPPORT SHELF (10.500\" x 31.500\" x 0.750\"): ",
    "   - 31.50\" wide wing shelf centered at Y=0; overhangs sides by 4.25\".",
    "2. KEYBOARD SLIDE-OUT TRAY (9.000\" x 21.000\" x 0.750\"): ",
    "   - Slides on 12\" full-extension ball-bearing slides (1.00\" clearance/side).",
    "3. LOWER FRONT ACCESS DOOR (18.875\" x 22.875\" x 0.750\"): ",
    "   - Opening: 19.000\" x 23.000\" with strict 1/16\" perimeter reveal.",
    "   - Continuous piano hinge mounted in 1/16\" gap on Right side.",
    "   - Magnetic catch and strike plate mounted on Left stop cleat.",
    "4. BACK ACCESS PANEL (62.625\" x 22.875\" x 0.250\" LIGHTWEIGHT PLYWOOD): ",
    "   - IEC320 C14 Power Module snap-in cutout: 2.00\" x 1.25\" at",
    "     (Y = +6.00\", Z = 4.00\" off base).",
    "   - Cam lock cylinder hole: Dia 0.750\" at top center (3.00\" from top).",
]
p4.addView(a4_notes)
a4_notes.X = 335.0
a4_notes.Y = 85.0
a4_notes.TextSize = 2.2

# =============================================================================
# SHEET 5: CABINET ELEVATIONS & MASTER CUT LIST SCHEDULE
# =============================================================================
p5, t5 = setup_page(
    "Drawing_Page_05_Elevations_CutList",
    "Sheet 5 - Cabinet Elevations & Master Cut List",
    "PARAMETRIC ARCADE CABINET",
    "SHEET 5: ELEVATIONS & MASTER CUT LIST",
    "FULL ASSEMBLY ELEVATIONS & COMPONENT SCHEDULE",
    "5 OF 5", "1 : 14"
)

major_assembly = [
    doc.getObject("Side_Panel_Left"),
    doc.getObject("Side_Panel_Right"),
    doc.getObject("Toe_Kick_Board"),
    doc.getObject("Lower_Front_Panel"),
    doc.getObject("Console_Diagonal_Apron"),
    doc.getObject("Keyboard_Bottom_Plate"),
    doc.getObject("Control_Panel_Shelf"),
    doc.getObject("User_Control_Box"),
    doc.getObject("Monitor_Bezel_Board"),
    doc.getObject("Speaker_Board"),
    doc.getObject("Marquee_Sign"),
    doc.getObject("Top_Roof_Panel"),
    doc.getObject("Back_Access_Panel_1_4in")
]

v5_front = doc.addObject("TechDraw::DrawViewPart", "View_Assy_Front")
v5_front.Source = major_assembly
v5_front.Direction = FreeCAD.Vector(-1, 0, 0)
v5_front.XDirection = FreeCAD.Vector(0, -1, 0)
v5_front.ScaleType = "Custom"
v5_front.Scale = 0.065
p5.addView(v5_front)
v5_front.X = 75.0
v5_front.Y = 190.0

v5_side = doc.addObject("TechDraw::DrawViewPart", "View_Assy_Side")
v5_side.Source = major_assembly
v5_side.Direction = FreeCAD.Vector(0, 1, 0)
v5_side.XDirection = FreeCAD.Vector(-1, 0, 0)
v5_side.ScaleType = "Custom"
v5_side.Scale = 0.065
p5.addView(v5_side)
v5_side.X = 175.0
v5_side.Y = 190.0

v5_iso = doc.addObject("TechDraw::DrawViewPart", "View_Assy_Isometric")
v5_iso.Source = major_assembly
v5_iso.Direction = FreeCAD.Vector(-1.0, -1.2, 0.9)
v5_iso.XDirection = FreeCAD.Vector(1.2, -1.0, 0.0)
v5_iso.ScaleType = "Custom"
v5_iso.Scale = 0.050
p5.addView(v5_iso)
v5_iso.X = 310.0
v5_iso.Y = 195.0

doc.recompute()

a5_cut = doc.addObject("TechDraw::DrawViewAnnotation", "Annotation_Sheet5_Master_CutList")
a5_cut.Text = [
    "MASTER PLYWOOD CUT LIST SCHEDULE (All Transverse Carcass Panels Width = 23.000\" Inner Width)",
    "==================================================================================================",
    "PART NAME                 QTY THK  FINISH SIZE (IN)  TOP BEVEL/MITER   BOT BEVEL/MITER   NOTES",
    "--------------------------------------------------------------------------------------------------",
    "Side Panels (Left/Right)   2  3/4\" 20.00\" x 65.25\"   Per 15-Vertex Map Square 90° Base   1/16\" T-molding",
    "Console Diagonal Apron     1  3/4\" 7.786\" x 23.000\"  42.40° Blade Tilt 42.40° Blade Tilt Parallel, no taper",
    "Keyboard Bottom Plate      1  3/4\" 5.250\" x 23.000\"  Square 90°        Square 90°        Z=29.25\"-30.00\"",
    "Monitor Bezel Board        1  3/4\" 16.572\" x 23.000\" 40.83° Miter      33.93° Bevel      33.93° rake; P1913S",
    "Speaker Board              1  3/4\" 7.433\" x 23.000\"  34.93° Miter      40.83° Miter      47.73° rake; 2x3.75\"",
    "Top Roof Panel             1  3/4\" 10.250\" x 23.000\" Square 90°        12.80° Bevel      Rakes from visor",
    "Toe Kick Board             1  3/4\" 4.500\" x 23.000\"  Square 90°        Square 90°        Setback 2.25\"",
    "Toe Kick Ceiling           1  3/4\" 1.500\" x 23.000\"  Square 90°        Square 90°        Covers kick recess",
    "Door Header Stretcher      1  3/4\" 1.500\" x 23.000\"  Square 90°        Square 90°        Anti-racking rail",
    "Internal Equipment Shelf   1  3/4\" 14.000\" x 23.000\" Square 90°        Square 90°        2.25\" cable slot",
    "Bottom Base Plate          1  3/4\" 14.250\" x 23.000\" Square 90°        Square 90°        Elevated 0.75\" Z",
    "Lower Front Access Door    1  3/4\" 18.875\" x 22.875\" Square 90°        Square 90°        1/16\" reveal all sides",
    "Back Access Panel          1  1/4\" 62.625\" x 22.875\" Square 90°        Square 90°        1/4\" ply; IEC socket",
    "Control Panel Wing Shelf   1  3/4\" 10.500\" x 31.500\" Square 90°        Square 90°        31.50\" wing span",
    "Keyboard Slide-Out Tray    1  3/4\" 9.000\" x 21.000\"  Square 90°        Square 90°        For 12\" slides",
    "Marquee Acrylic Sign       1  1/8\" 5.500\" x 23.000\"  Square 90°        Square 90°        Translucent acrylic",
]
p5.addView(a5_cut)
a5_cut.X = 215.0
a5_cut.Y = 55.0
a5_cut.TextSize = 1.8

doc.recompute()
print("  [+] All 5 TechDraw Shop Sheets created and recomputed successfully!")

# Export Shop DXF files
for i, page in enumerate([p1, p2, p3, p4, p5], start=1):
    dxf_path = f"/home/scott/20p/cad/arcade/shop_sheet_{i}.dxf"
    TechDraw.writeDXFPage(page, dxf_path)
    print(f"  [+] Exported {dxf_path}")

TechDraw.writeDXFPage(p1, "/home/scott/20p/cad/arcade/shop_sheet_1_side_panel.dxf")
TechDraw.writeDXFPage(p5, "/home/scott/20p/cad/arcade/shop_sheet_2_cabinet_elevations.dxf")
TechDraw.writeDXFView(v_side, "/home/scott/20p/cad/arcade/side_panel_profile.dxf")
print("  [+] Exported 1:1 Side Panel profile DXF")

# =============================================================================
# 11. SAVE FREECAD PROJECT & EXPORT STEP MODEL
# =============================================================================
fcstd_path = "/home/scott/20p/cad/arcade/arcade_cabinet.FCStd"
doc.saveAs(fcstd_path)
print(f"\n  [+] FreeCAD project saved: {fcstd_path}")

step_path = "/home/scott/20p/cad/arcade/arcade_cabinet.step"
export_parts = [
    obj for obj in doc.Objects
    if hasattr(obj, "Shape") and obj.Shape and obj.Shape.isValid()
    and not obj.isDerivedFrom("Sketcher::SketchObject")
    and not obj.isDerivedFrom("TechDraw::DrawView")
    and not obj.isDerivedFrom("TechDraw::DrawPage")
    and not obj.isDerivedFrom("TechDraw::DrawTemplate")
]
Part.export(export_parts, step_path)
print(f"  [+] Universal STEP solid model exported: {step_path} ({len(export_parts)} parts)")

print("\n" + "=" * 75)
print("  FREECAD PARAMETRIC RECONSTRUCTION COMPLETED SUCCESSFULLY!")
print("=" * 75 + "\n")

sys.exit(0)

