// ==============================================================================
// ESSENTIAL 3D PRINTABLE WOODWORKING JIGS FOR 3D PRINTER TABLE BUILD (V3 - AMS)
// ==============================================================================
// 100% Support-free prints designed for Bambu CoreXY 3D Printer.
// All labels are embossed 0.6mm proud on the top surface for instant
// 1-click black coloring using the Bambu Studio "Fill" or "Height Range" tool!
//
// 1. FORSTNER_SADDLE_GUIDE: Saddles over the 1.5" 2x4 edge, holding a 3/4" (or 5/8")
//    Forstner bit dead-perpendicular and centered for Figure-8 desktop clips.
// 2. DRAWER_PULL_JIG: Hooks over the top of the 3/4" Walnut drawer faces with 
//    standard 5" (128mm) center-to-center drill guide holes.
// ==============================================================================

part = "all"; // [all, forstner_guide, drawer_pull_jig]

$fn = 60;

// ==============================================================================
// JIG 1: FORSTNER BIT SADDLE GUIDE (FOR FIGURE-8 CLIPS ON 2x4 EDGE)
// ==============================================================================
module forstner_guide() {
    BOARD_W = 38.5; // 1.5" actual 2x4 thickness (+0.4mm tolerance)
    WALL    = 5.0;
    GUIDE_D = 19.5; // Fits standard 3/4" (19.05mm) Forstner bit shank/head
    
    difference() {
        union() {
            // Main saddle body
            cube([BOARD_W + 2 * WALL, 45, 26]);
            
            // Raised text for AMS Black Filament (0.6mm proud on top face)
            translate([(BOARD_W + 2 * WALL) / 2, 8, 26])
                linear_extrude(0.6)
                    text("3/4\" FORSTNER", size=4.0, font="Liberation Sans:style=Bold", halign="center");
            translate([(BOARD_W + 2 * WALL) / 2, 37, 26])
                linear_extrude(0.6)
                    text("2x4 SADDLE", size=4.0, font="Liberation Sans:style=Bold", halign="center");
        }
        
        // Saddle channel (slides snugly over 2x4 edge)
        translate([WALL, -1, -1])
            cube([BOARD_W, 47, 16]);
            
        // Centered Forstner bit drill bore (through the top)
        translate([WALL + BOARD_W / 2, 22.5, -2])
            cylinder(d=GUIDE_D, h=32);
            
        // Sight windows on sides to see alignment mark on 2x4
        translate([-1, 22.5, 7.5])
            cube([BOARD_W + 2 * WALL + 2, 8, 20], center=true);
    }
}

// ==============================================================================
// JIG 2: DRAWER PULL DRILLING JIG (5" / 128mm BAR PULLS)
// ==============================================================================
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
// PRINT BED LAYOUT (All Support-Free)
// ==============================================================================
if (part == "all") {
    // 1. Forstner Saddle Guide
    translate([0, 0, 0])
        forstner_guide();
        
    // 2. Drawer Pull Jig (Compact layout beside saddle guide)
    translate([60, 0, 0])
        drawer_pull_jig();
} else if (part == "forstner_guide") {
    forstner_guide();
} else if (part == "drawer_pull_jig") {
    drawer_pull_jig();
}
