// ==============================================================================
// ESSENTIAL 3D PRINTABLE WOODWORKING JIGS FOR 3D PRINTER TABLE BUILD (V4 - AMS)
// ==============================================================================
// 100% SUPPORT-FREE PRINT DESIGNED FOR BAMBU AMS MULTI-COLOR (BLACK ON COLOR)
// ZERO OVERHANGS, ZERO BRIDGES, ZERO FLOATING CANTILEVERS.
//
// 1. FORSTNER_SADDLE_GUIDE:
//    Saddles over 1.5" (38.1mm) 2x4 edge with 19.5mm bore for 3/4" (or 5/8")
//    Forstner bit. Bases flat on bed; saddle channel and alignment V-notches
//    are open to +Z for 100% support-free printing.
//    Raised 0.6mm AMS text on top flange edges.
//
// 2. DRAWER_PULL_JIG:
//    Hooks over the top of 3/4" Walnut drawer faces with standard 5" (128mm)
//    center-to-center drill guide holes and center pencil alignment notch.
//    Raised 0.6mm AMS text on face plate.
// ==============================================================================

part = "all"; // [all, forstner_guide, drawer_pull_jig]

$fn = 60;

// ==============================================================================
// JIG 1: FORSTNER BIT SADDLE GUIDE (FOR FIGURE-8 CLIPS ON 2x4 EDGE)
// ==============================================================================
// Support-free orientation: Base plate sits flat on build plate (Z=0).
// Saddle walls and bore grow vertically into +Z. ZERO cantilevers.
module forstner_guide() {
    BOARD_W  = 38.6; // Actual 2x4 thickness (1.5" = 38.1mm + 0.5mm slip tolerance)
    LENGTH   = 50.0; // 50mm long along the 2x4 rail
    BASE_H   = 12.0; // 12mm thick guide block for dead-perpendicular drilling
    SADDLE_H = 16.0; // 16mm saddle drop over the 2x4 sides
    WALL_T   = 6.5;  // Solid 6.5mm wall thickness
    GUIDE_D  = 19.5; // Fits standard 3/4" (19.05mm) Forstner bit shank/head
    
    TOTAL_W  = BOARD_W + 2 * WALL_T; // 38.6 + 13.0 = 51.6mm
    TOTAL_H  = BASE_H + SADDLE_H;     // 12.0 + 16.0 = 28.0mm
    
    difference() {
        union() {
            // Main solid base block resting completely flat on build plate at Z=0
            cube([TOTAL_W, LENGTH, BASE_H]);
            
            // Left saddle flange (rises from Z=BASE_H to Z=TOTAL_H)
            translate([0, 0, BASE_H])
                cube([WALL_T, LENGTH, SADDLE_H]);
                
            // Right saddle flange (rises from Z=BASE_H to Z=TOTAL_H)
            translate([TOTAL_W - WALL_T, 0, BASE_H])
                cube([WALL_T, LENGTH, SADDLE_H]);
                
            // Raised AMS Text on the top of the flanges at Z = TOTAL_H (+0.6mm proud)
            // Left flange: "3/4\" FORSTNER"
            translate([WALL_T / 2, LENGTH / 2, TOTAL_H])
                rotate([0, 0, 90])
                    linear_extrude(0.6)
                        text("3/4\" FORSTNER", size=3.8, font="Liberation Sans:style=Bold", halign="center", valign="center");
                        
            // Right flange: "2x4 SADDLE"
            translate([TOTAL_W - WALL_T / 2, LENGTH / 2, TOTAL_H])
                rotate([0, 0, 90])
                    linear_extrude(0.6)
                        text("2x4 SADDLE", size=3.8, font="Liberation Sans:style=Bold", halign="center", valign="center");
        }
        
        // Centered Forstner bit drill guide bore (through the base block)
        translate([TOTAL_W / 2, LENGTH / 2, -1])
            cylinder(d=GUIDE_D, h=BASE_H + 2);
            
        // Precision alignment V-notches on both sides (indexes to pencil mark on 2x4)
        // Cut through the full height to avoid any overhead ceiling
        translate([0, LENGTH / 2, BASE_H - 1])
            rotate([0, 0, 45])
                cube([4.0, 4.0, SADDLE_H + 3]);
        translate([TOTAL_W, LENGTH / 2, BASE_H - 1])
            rotate([0, 0, 45])
                cube([4.0, 4.0, SADDLE_H + 3]);
    }
}

// ==============================================================================
// JIG 2: DRAWER PULL DRILLING JIG (5" / 128mm BAR PULLS)
// ==============================================================================
// Sits completely flat on build plate at Z=0. ZERO cantilevers.
module drawer_pull_jig() {
    HOLE_SPACING = 128.0; // Standard 5" (128mm) bar pull spacing
    HOLE_DIA     = 4.8;   // Clearance for #8 / M4 pull screws
    FENCE_DEPTH  = 22.0;  // 3/4" drawer face thickness (+tolerance)
    
    difference() {
        union() {
            // Main face plate
            cube([HOLE_SPACING + 40, 50, 6]);
            // Top registration lip (hooks over top edge of drawer front)
            cube([HOLE_SPACING + 40, 10, 6 + FENCE_DEPTH]);
            
            // Raised AMS text on the face plate (0.6mm proud)
            translate([(HOLE_SPACING + 40) / 2, 16, 6])
                linear_extrude(0.6)
                    text("5\" / 128mm DRAWER PULL", size=6.0, font="Liberation Sans:style=Bold", halign="center");
        }
        
        // Two drill guide holes spaced at 128mm (5.04")
        translate([20, 32, -1])
            cylinder(d=HOLE_DIA, h=10);
        translate([20 + HOLE_SPACING, 32, -1])
            cylinder(d=HOLE_DIA, h=10);
            
        // Center alignment notch (line up with pencil mark on center of drawer)
        translate([20 + HOLE_SPACING / 2, -1, -1])
            cube([2.0, 15, 40]);
    }
}

// ==============================================================================
// PRINT BED LAYOUT (All Support-Free, Wide Clearance)
// ==============================================================================
if (part == "all") {
    // 1. Forstner Saddle Guide (X: 20 to 71.6, Y: 20 to 70)
    translate([20, 20, 0])
        forstner_guide();
        
    // 2. Drawer Pull Jig (X: 20 to 188, Y: 85 to 135)
    translate([20, 85, 0])
        drawer_pull_jig();
} else if (part == "forstner_guide") {
    translate([20, 20, 0])
        forstner_guide();
} else if (part == "drawer_pull_jig") {
    translate([20, 20, 0])
        drawer_pull_jig();
}
