# Bambu 3D Printer Stand & Storage Workbench (V3 - L-Shaped Legs)

Parametric FreeCAD model and woodworking plans for a rock-solid, vibration-dampened 3D printer stand built around a **24" × 48" × 1" Walnut desktop**.

---

## What's New in Version 3 (L-Shaped 2×4 Corner Legs)

1. **"L-Shaped" 2×4 Legs (Zero Planer or 4×4 Needed):**
   - Each corner post is built from two standard 2×4s joined at 90° into a rigid "L" column.
   - Joined using your **Kreg Pocket Hole Jig (1-1/2" setting)** on the inside face + Titebond II wood glue.
   - Joins the factory-flat edge of one 2×4 to the flat face of the other: **100% flat, zero planing or jointing required**.
   - Includes a 2" × 2" corner foot block inside each L-leg to mount the 3/8" leveling foot insert.
2. **100% Off-the-Shelf at Home Depot Canada:**
   - The entire base frame uses standard **SPF Premium 2×4 studs** (`SKU 1000112108`, ~$6.50 CAD).
   - Only **7 standard 8-ft 2×4 studs** needed for the entire solid timber base frame! (~$45.50 CAD total).
3. **Flush Drawer Construction:**
   - 3/4" Walnut drawer faces are mounted flush (0.0" gap) against the 1/2" Birch drawer boxes.
   - Middle spool drawer modeled extended 10" forward on 18" ball-bearing slides with **12 upright 1kg filament spools** loaded inside.
4. **Creality CR-6 SE Staging:**
   - Modeled and parked on the lower right tech shelf with 5.5" clearance above its gantry.
5. **Dual-Spool Filament Dryer:**
   - Modeled on the tabletop beside the Bambu printer.

---

## File Directory

- [`create_freecad_table.py`](file:///home/scott/20p/cad/bambu-table/create_freecad_table.py): FreeCAD Python generator script that parametrically builds the entire solid model and shop sheet.
- [`bambu_printer_table.FCStd`](file:///home/scott/20p/cad/bambu-table/bambu_printer_table.FCStd): FreeCAD native document with parameters spreadsheet, labeled groups, and TechDraw blueprints.
- [`bambu_printer_table.step`](file:///home/scott/20p/cad/bambu-table/bambu_printer_table.step): Universal 3D STEP assembly (84 solid parts).
- [`shop_sheet_printer_table.dxf`](file:///home/scott/20p/cad/bambu-table/shop_sheet_printer_table.dxf): 2D shop elevation and cut list blueprint.
- [`CUT_LIST_AND_BOM.md`](file:///home/scott/20p/cad/bambu-table/CUT_LIST_AND_BOM.md): Complete dimensioned lumber cut list, hardware specs, and storage capacity.
- [`drawer_jigs.scad`](file:///home/scott/20p/cad/bambu-table/drawer_jigs.scad): OpenSCAD parametric model for 3D printable slide installation jigs.
- [`drawer_installation_jigs.stl`](file:///home/scott/20p/cad/bambu-table/drawer_installation_jigs.stl): Support-free 3D printable STL containing slide setback cradle, drawer box standoffs, and 1/8" reveal shims.
- [`shop_jigs.scad`](file:///home/scott/20p/cad/bambu-table/shop_jigs.scad): OpenSCAD model for woodworking companion jigs with raised AMS text (Forstner bit saddle guide and drawer pull template).
- [`woodworking_companion_jigs.stl`](file:///home/scott/20p/cad/bambu-table/woodworking_companion_jigs.stl): Support-free 3D printable STL containing the companion woodworking jigs (Forstner saddle guide + 5" pull template) with embossed labels for AMS multi-color.
- [`drawer_spacers.scad`](file:///home/scott/20p/cad/bambu-table/drawer_spacers.scad): OpenSCAD model for 1/8" drawer front T-spacers and internal 8-5/8" slide tier story stick with raised AMS labels.
- [`drawer_spacers_and_story_stick.stl`](file:///home/scott/20p/cad/bambu-table/drawer_spacers_and_story_stick.stl): Complete plate containing all 3 jigs (pair of 1/8" T-spacers + 8-5/8" story stick) with wide separation.
- [`drawer_front_t_spacers.stl`](file:///home/scott/20p/cad/bambu-table/drawer_front_t_spacers.stl): Individual STL containing just the pair of 1/8" drawer front T-spacers.
- [`slide_tier_story_stick.stl`](file:///home/scott/20p/cad/bambu-table/slide_tier_story_stick.stl): Individual STL containing just the 8-5/8" slide tier story stick.

---

## Step-by-Step Build Guide

### Step 1: Build the 4 L-Shaped Corner Legs
1. Using your **miter saw with a clamped stop block**, cut eight identical 30.0" pieces of 2×4.
2. Pair them into 4 sets of two (Piece A = Front/Rear Flange, Piece B = Side Return Flange).
3. Set your **Kreg Jig to 1-1/2" material**. Drill 3 pocket holes along the inside face of Piece B facing into the edge of Piece A.
4. Apply a generous bead of Titebond II wood glue along the seam, clamp Piece A and Piece B at 90° with a speed square, and drive **2-1/2" coarse pocket hole screws**.
5. Glue and screw a 2" × 2" scrap 2×4 block in the bottom inside corner of each "L". This creates a solid foot pad for your 3/8" leveling foot insert.

### Step 2: Cut the Aprons & Stretchers
From your remaining 2×4 studs, cut:
* 4 pcs @ 38.00" (Upper Front, Upper Rear, Lower Front, Lower Rear rails)
* 4 pcs @ 11.00" (Upper Left, Upper Right, Lower Left, Lower Right side rails)
* 2 pcs @ 18.00" (Upper & Lower Center Cross-Ties)

### Step 3: Join the Frame (Using JessEm Dowel Jig or Kreg Jig)
* Join the 38" front rails to the front flanges of the L-legs (flush on the front).
* Join the 11" side rails to the side return flanges of the L-legs (flush on the sides).
* Join the 18" center cross-ties between the front and rear rails.

### Step 4: Install the 1/2" Birch Shear Back Panel
* Using your **Milwaukee track saw on foam board**, cut the 1/2" Birch project panel down to 45.0" wide.
* Screw it across the rear flanges and rear rails. *(This locks the frame completely against racking).*

### Step 5: Install Center Partition & Shelves
* Cut the 3/4" Birch panel: Center Divider (18" × 22") and CR-6 Shelf (18" × 18.625").
* Mount between the center cross-ties and right-side rails.

### Step 6: Build the Drawers
* Cut 1/2" Birch drawer box parts with your track saw.
* Join with Kreg pocket holes on the outside of front & back pieces (hidden).
* Screw 1/2" (or 1/4") bottoms flush to the box underside.
* Mount 18" slides and screw 3/4" Walnut drawer faces flush from inside the box with 1/8" reveal shims.

### Step 7: Mount Tabletop & Leveling Feet
* Bore 1/8" deep recesses on the top edge of the 2×4 aprons using a Forstner bit with a tape flag.
* Fasten the Figure-8 desktop clips to the 24" × 48" walnut top (use 5/8" or 3/4" screws).
* Thread in the leveling feet and level the table.

---

## How to Re-Run or Customize

```bash
/home/scott/.local/bin/freecad -c "import runpy; runpy.run_path('/home/scott/20p/cad/bambu-table/create_freecad_table.py')"
```
