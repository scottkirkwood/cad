// ==============================================================================
// 3D PRINTABLE DRAWER SPACING JIGS FOR BAMBU PRINTER (V3 - FIXED ORIENTATION)
// ==============================================================================
// 100% SUPPORT-FREE PRINT DESIGNED FOR BAMBU AMS MULTI-COLOR (BLACK ON COLOR)
//
// 1. DRAWER_FRONT_T_SPACER (Pair):
//    Saddles over 3/4" lower drawer front, creating an exact 1/8" (3.18mm) ledge
//    for the upper drawer front to rest on while clamping.
//    Printed on its flat side: 0 overhangs, crisp 90° corners, with bold
//    0.6mm raised "1/8\" GAP" text on the top surface.
//
// 2. SLIDE_TIER_STORY_STICK:
//    Exact 8-5/8" (219.08mm) repeat spacing between drawer slide tiers.
//    Lies 100% flat on the build plate (Z=0).
//    Features bold 0.6mm raised "8-5/8\" SLIDE TIER" text on top (+Z).
// ==============================================================================

part = "all"; // [all, front_t_spacers, slide_tier_stick]

$fn = 60;

// ==============================================================================
// JIG 1: DRAWER FRONT T-SPACER (1/8" REVEAL LEDGE)
// ==============================================================================
// Profile in X-Y plane, extruded in Z by WIDTH (22mm).
// Zero overhangs, 100% vertical walls, completely flat on build plate at Z=0.
module front_t_spacer() {
    PLY_T   = 19.5;   // 3/4" plywood drawer front thickness (+0.5mm clearance)
    GAP_T   = 3.175;  // Exact 1/8" reveal spacing
    LIP_H   = 14.0;   // Saddle drop depth over lower drawer front
    WALL_T  = 3.5;    // Wall thickness of saddle legs
    TAB_LEN = 16.0;   // Forward pull tab length for easy removal
    WIDTH   = 22.0;   // Width of jig along drawer edge (Z-height on bed)
    
    // Total Y-depth = WALL_T (rear) + PLY_T + WALL_T (front) + TAB_LEN
    TOTAL_Y = WALL_T + PLY_T + WALL_T + TAB_LEN; // 3.5 + 19.5 + 3.5 + 16 = 42.5mm
    TOTAL_X = LIP_H + GAP_T;                     // 14 + 3.175 = 17.175mm
    
    difference() {
        union() {
            // Main solid body extruded along Z
            linear_extrude(WIDTH) {
                difference() {
                    // Outer bounding envelope
                    square([TOTAL_X, TOTAL_Y]);
                    
                    // Saddle channel cutout for 3/4" drawer front
                    // Starts at X = 0, goes to X = LIP_H
                    // Y starts at WALL_T (3.5), width PLY_T (19.5)
                    translate([-0.1, WALL_T])
                        square([LIP_H + 0.1, PLY_T]);
                }
            }
            
            // Raised AMS Text on the flat top face at Z = WIDTH (+0.6mm proud)
            // Positioned on the front pull-tab region (X: [0, TOTAL_X], Y: [WALL_T + PLY_T, TOTAL_Y])
            translate([TOTAL_X / 2, WALL_T + PLY_T + TAB_LEN / 2 + 1.0, WIDTH])
                rotate([0, 0, -90])
                    linear_extrude(0.6) {
                        translate([0, 2.5])
                            text("1/8\"", size=5.0, font="Liberation Sans:style=Bold", halign="center", valign="center");
                        translate([0, -3.2])
                            text("GAP", size=4.2, font="Liberation Sans:style=Bold", halign="center", valign="center");
                    }
        }
    }
}

// ==============================================================================
// JIG 2: SLIDE TIER STORY STICK (8-5/8" / 219.08mm)
// ==============================================================================
// Lies 100% flat on the build plate (Z=0).
// Length along X (219.0mm), width along Y (20.0mm), height in Z (10.0mm).
module slide_tier_stick() {
    TIER_H   = 219.0; // Exact 8-5/8" spacing
    STICK_W  = 20.0;  // 20mm wide along Y
    STICK_T  = 10.0;  // 10mm thick along Z
    SLIDE_W  = 13.0;  // Standard 1/2" slide outer member width
    NOTCH_D  = 5.0;   // 5mm cradle nesting notch
    
    difference() {
        union() {
            // Solid rectangular spine resting flat on the build plate
            cube([TIER_H, STICK_W, STICK_T]);
            
            // Raised AMS Text on the top flat surface at Z = STICK_T (+0.6mm proud)
            translate([TIER_H / 2, STICK_W / 2, STICK_T])
                linear_extrude(0.6)
                    text("8-5/8\" SLIDE TIER", size=6.5, font="Liberation Sans:style=Bold", halign="center", valign="center");
        }
        
        // Bottom reference notch (cradles lower slide) - open to +Z for 100% support-free
        translate([-0.1, (STICK_W - SLIDE_W) / 2, STICK_T - 3.5])
            cube([NOTCH_D + 0.1, SLIDE_W, 4.0]);
            
        // Top reference notch (supports upper slide) - open to +Z for 100% support-free
        translate([TIER_H - NOTCH_D, (STICK_W - SLIDE_W) / 2, STICK_T - 3.5])
            cube([NOTCH_D + 0.1, SLIDE_W, 4.0]);
            
        // Weight-reduction cutouts (through-holes perpendicular to bed, 100% support-free)
        for (x_off = [32, 62, 157, 187]) {
            translate([x_off, STICK_W / 2, -0.5])
                cylinder(d=8.0, h=STICK_T + 1.0);
        }
    }
}

// ==============================================================================
// PRINT BED LAYOUT (All 3 Objects Laid Out with Wide Clearance)
// ==============================================================================
if (part == "all") {
    // 1. Slide Tier Story Stick (Front of plate, X: 18 to 237, Y: 18 to 38)
    translate([18, 18, 0])
        slide_tier_stick();
        
    // 2. Drawer Front T-Spacer #1 (Rear Left, X: 35 to 52.2, Y: 65 to 107.5)
    translate([35, 65, 0])
        front_t_spacer();
        
    // 3. Drawer Front T-Spacer #2 (Rear Right, X: 125 to 142.2, Y: 65 to 107.5)
    translate([125, 65, 0])
        front_t_spacer();
} else if (part == "front_t_spacers") {
    translate([35, 30, 0])
        front_t_spacer();
    translate([125, 30, 0])
        front_t_spacer();
} else if (part == "slide_tier_stick") {
    translate([18, 50, 0])
        slide_tier_stick();
}
