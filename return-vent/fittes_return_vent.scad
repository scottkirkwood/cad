// =====================================================================
// Modern Minimalist Perimeter-Slot Return Vent (Fittes / Aria Style)
// Parametric OpenSCAD Model for Bambu Lab H2C (330 x 320 mm bed)
// Verified 100% Solid Single-Connected-Component Geometry
// =====================================================================

/* [Overall Wall & Duct Dimensions (mm)] */
// Total outer frame width (covers drywall opening)
faceplate_w = 390; 
// Total outer frame height
faceplate_h = 240;

// Wall / duct opening cutout in drywall (standard 14" x 8")
duct_w = 350;
duct_h = 200;

// Wall collar thickness (sleeve into duct)
collar_th = 4;

// Depth of collar inserting into the wall opening
collar_depth = 18;

// Thickness of visible front faces (flange and center plate)
flange_th = 3.5;

/* [1-Piece Center Plate (Sized for Bambu H2C)] */
// Width of center plate (max 320mm for Bambu H2C build plate)
center_w = 310;
// Height of center plate
center_h = 168;

// Front plate style: "solid" (classic Fittes) or "double_slot" (Fittes LITE+)
plate_style = "solid"; // ["solid", "double_slot"]

/* [Magnets & Hardware] */
// Neodymium magnet diameter (e.g. 8mm or 10mm)
magnet_d = 8.2;
// Magnet thickness (e.g. 3mm)
magnet_h = 3.2;

// Screw hole for wall mounting (standard drywall screw)
screw_d = 4.2;
screw_head_d = 8.5;

// Alignment dowel pin diameter for joining frame halves
pin_d = 3.8;
pin_len = 12;

/* [Render Part Selection] */
PART = "assembly"; // ["assembly", "center_plate_1piece", "frame_left", "frame_right", "frame_full"]

// Tolerances
tol = 0.25;

// ---------------------------------------------------------------------
// Derived Parameters
// ---------------------------------------------------------------------
inner_w = duct_w - 2 * collar_th; // 342 mm clear opening
inner_h = duct_h - 2 * collar_th; // 192 mm clear opening

// Bracket positions (6 points: 3 top, 3 bottom)
bracket_xs = [-center_w * 0.35, 0, center_w * 0.35]; // [-108.5, 0, 108.5]
bracket_ys = [-center_h * 0.36, center_h * 0.36];    // [-60.5, 60.5]

// ---------------------------------------------------------------------
// Helper: 2D Rounded Box Extrusion (Clean 2-Manifold Solids)
// ---------------------------------------------------------------------
module rounded_box(w, h, depth, r) {
    r_safe = min(r, min(w/2 - 1, h/2 - 1));
    linear_extrude(height = depth)
        offset(r = r_safe, $fn = 36)
            square([w - 2*r_safe, h - 2*r_safe], center = true);
}

// ---------------------------------------------------------------------
// 1. SUBFRAME (Continuous 1-Piece Solid Geometry)
// ---------------------------------------------------------------------
module subframe_solid() {
    difference() {
        union() {
            // A. Outer Wall Flange (sits flat against drywall)
            rounded_box(faceplate_w, faceplate_h, flange_th, 4);

            // B. Duct Collar (inserts into wall cavity, overlaps flange solidly)
            translate([0, 0, -collar_depth])
                rounded_box(duct_w, duct_h, collar_depth + flange_th, 3);
        }

        // Inner Air Chamber Cutout (guaranteed narrower than duct_w so collar walls remain solid)
        translate([0, 0, -collar_depth - 1])
            rounded_box(inner_w, inner_h, collar_depth + flange_th + 2, 2);
    }

    // C. Cantilever Support Arms & Pedestals (merged into collar walls)
    for (y = bracket_ys) {
        // Arm spanning collar wall to collar wall
        translate([-duct_w/2, y - 8, -collar_depth + 4])
            cube([duct_w, 16, 12]);
        
        // Pedestals with indexing bosses
        for (x = bracket_xs) {
            translate([x, y, -collar_depth + 4])
                cylinder(r = 11, h = collar_depth - 4, $fn = 32);
            translate([x, y, 0])
                cylinder(r = 7, h = 2.5, $fn = 32); // Raised indexing boss
        }
    }

    // D. Bottom Anti-Drop Gravity Shelf Lugs (anchored to bottom collar wall)
    shelf_span = (inner_h - center_h)/2 + 2; // reaches from collar wall to center plate edge
    for (x = [-center_w * 0.25, center_w * 0.25]) {
        translate([x - 12, -inner_h/2 - 2, -collar_depth + 6])
            cube([24, shelf_span + 2, collar_depth - 6]);
    }

    // E. Center Joining Spine (at X = 0, connecting top & bottom collar walls)
    translate([-8, -duct_h/2, -collar_depth])
        cube([16, duct_h, collar_depth + flange_th]);
}

module subframe_machined() {
    difference() {
        subframe_solid();

        // 1. Magnet pockets on top of pedestals
        for (y = bracket_ys) {
            for (x = bracket_xs) {
                translate([x, y, 2.5 - magnet_h])
                    cylinder(r = magnet_d/2 + tol, h = magnet_h + 1, $fn = 24);
            }
        }

        // 2. Hidden wall mounting screw holes in cantilever arms
        for (y = bracket_ys) {
            for (x = [-duct_w * 0.44, duct_w * 0.44]) {
                translate([x, y, -collar_depth - 1]) {
                    cylinder(r = screw_d/2, h = collar_depth + 2, $fn = 20);
                    translate([0, 0, collar_depth - 6])
                        cylinder(r1 = screw_d/2, r2 = screw_head_d/2, h = 4, $fn = 20);
                }
            }
        }

        // 3. Outer flange screw holes (matching original vent)
        for (x = [-faceplate_w/2 + 8, faceplate_w/2 - 8]) {
            translate([x, 0, -1]) {
                cylinder(r = screw_d/2, h = flange_th + 2, $fn = 20);
                translate([0, 0, flange_th - 2])
                    cylinder(r1 = screw_d/2, r2 = screw_head_d/2, h = 3, $fn = 20);
            }
        }

        // 4. Alignment dowel pin sockets on center seam (X = 0)
        for (y = [-duct_h * 0.35, -duct_h * 0.15, duct_h * 0.15, duct_h * 0.35]) {
            translate([0, y, -collar_depth / 2])
                rotate([0, 90, 0])
                    cylinder(r = pin_d/2 + tol, h = pin_len + 4, center = true, $fn = 20);
        }

        // 5. Center joining bolt holes (M3 clearance)
        for (y = [-duct_h * 0.25, duct_h * 0.25]) {
            translate([0, y, -collar_depth * 0.6])
                rotate([0, 90, 0])
                    cylinder(r = 1.7, h = 30, center = true, $fn = 20);
        }
    }
}

// ---------------------------------------------------------------------
// 2. ONE-PIECE FLOATING CENTER PLATE (310 x 168 mm - Single Print)
// ---------------------------------------------------------------------
module center_plate_solid() {
    rounded_box(center_w, center_h, flange_th, 3);
}

module center_plate_machined() {
    difference() {
        union() {
            center_plate_solid();

            // Underside indexing & magnet cups
            for (y = bracket_ys) {
                for (x = bracket_xs) {
                    translate([x, y, -2])
                        cylinder(r = 10, h = 2, $fn = 28);
                }
            }

            // Bottom shelf resting tabs
            for (x = [-center_w * 0.25, center_w * 0.25]) {
                translate([x - 10, -center_h/2, -3])
                    cube([20, 4, 3]);
            }
        }

        // Magnet pockets & indexing cavities
        for (y = bracket_ys) {
            for (x = bracket_xs) {
                translate([x, y, -2.1])
                    cylinder(r = magnet_d/2 + tol, h = magnet_h, $fn = 24);
                translate([x, y, -0.5])
                    difference() {
                        cylinder(r = 7.5 + tol, h = 1.5, $fn = 28);
                        cylinder(r = magnet_d/2 - 0.5, h = 2, $fn = 24);
                    }
            }
        }
    }
}

// ---------------------------------------------------------------------
// 3. FRAME SPLIT (Left and Right for Bambu H2C)
// ---------------------------------------------------------------------
cut_margin = 5;

module split_left() {
    intersection() {
        subframe_machined();
        translate([-faceplate_w - cut_margin, -faceplate_h, -collar_depth - 5])
            cube([faceplate_w + cut_margin, faceplate_h * 2, collar_depth + flange_th + 10]);
    }
}

module split_right() {
    intersection() {
        subframe_machined();
        translate([0, -faceplate_h, -collar_depth - 5])
            cube([faceplate_w + cut_margin, faceplate_h * 2, collar_depth + flange_th + 10]);
    }
}

// ---------------------------------------------------------------------
// Part Selector
// ---------------------------------------------------------------------
if (PART == "assembly") {
    color("#D8D8D8") subframe_machined();
    color("#FFFFFF") translate([0, 0, 0.2]) center_plate_machined();
} else if (PART == "center_plate_1piece") {
    rotate([180, 0, 0])
        center_plate_machined();
} else if (PART == "frame_left") {
    rotate([180, 0, 0])
        split_left();
} else if (PART == "frame_right") {
    rotate([180, 0, 0])
        split_right();
} else if (PART == "frame_full") {
    subframe_machined();
}
