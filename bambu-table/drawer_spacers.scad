// ==============================================================================
// 3D PRINTABLE DRAWER SPACING JIGS FOR BAMBU PRINTER (WITH AMS TEXT)
// ==============================================================================
// 1. DRAWER_FRONT_T_SPACER (Pair):
//    Hooks over the top of the 3/4" lower drawer front, creating an exact 1/8" (3.18mm)
//    shelf to rest the upper drawer face on while clamping.
// 2. SLIDE_TIER_STORY_STICK:
//    Internal carcass spacer (exact 8-5/8" / 219mm height). Rests on the lower slide
//    track inside the cabinet to hold the next slide at the exact elevation without measuring.
//
// Optimized for Bambu AMS multi-color:
// Text is embossed 0.6mm proud of the surface so you can use Bambu Studio's
// "Height Range" or "Fill" tool to paint the text BLACK in 2 clicks!
// ==============================================================================

part = "all"; // [all, front_t_spacers, slide_tier_stick]

$fn = 60;

// ==============================================================================
// JIG 1: DRAWER FRONT T-SPACER (1/8" REVEAL LEDGE)
// ==============================================================================
module front_t_spacer() {
    PLY_T   = 19.5;   // 3/4" plywood drawer front thickness (+0.5mm clearance)
    GAP_T   = 3.175;  // Exact 1/8" reveal spacing
    WIDTH   = 36.0;   // 36mm wide
    LIP_H   = 18.0;   // Drops down in front of lower drawer face
    BACK_H  = 12.0;   // Drops down behind lower drawer face
    WALL_T  = 4.0;
    
    difference() {
        union() {
            // Main saddle block
            cube([WIDTH, PLY_T + 2 * WALL_T, LIP_H + GAP_T]);
            
            // Raised text for AMS Black Filament (0.6mm proud)
            translate([WIDTH / 2, 0.4, LIP_H / 2])
                rotate([90, 0, 0])
                    linear_extrude(0.6)
                        text("1/8\" GAP", size=5.5, font="Liberation Sans:style=Bold", halign="center", valign="center");
        }
        
        // Channel that clips over the 3/4" lower drawer front
        translate([-1, WALL_T, -1])
            cube([WIDTH + 2, PLY_T, LIP_H + 1]);
            
        // Relieve back lip slightly so it's easy to slip on/off
        translate([-1, WALL_T + PLY_T, BACK_H])
            cube([WIDTH + 2, WALL_T + 1, LIP_H]);
    }
}

// ==============================================================================
// JIG 2: SLIDE TIER STORY STICK (8-5/8" / 219.08mm)
// ==============================================================================
module slide_tier_stick() {
    TIER_H   = 219.0; // 8-5/8" spacing between slide centerlines
    STICK_W  = 22.0;  // 22mm wide
    STICK_D  = 16.0;  // 16mm deep
    SLIDE_W  = 13.5;  // Standard 1/2" slide track width
    NOTCH_D  = 6.0;   // 6mm nesting notch
    
    difference() {
        union() {
            // Main vertical story stick body
            cube([STICK_W, STICK_D, TIER_H]);
            
            // Raised AMS Text on the front face (0.6mm proud)
            translate([STICK_W / 2, STICK_D, TIER_H / 2])
                rotate([90, 0, 180])
                    linear_extrude(0.6)
                        text("8-5/8\" SLIDE TIER", size=7.0, font="Liberation Sans:style=Bold", halign="center", valign="center");
        }
        
        // Bottom cradle notch (nests over the top of the lower slide)
        translate([(STICK_W - SLIDE_W) / 2, -1, -1])
            cube([SLIDE_W, STICK_D + 2, NOTCH_D + 1]);
            
        // Top cradle notch (holds the bottom of the upper slide)
        translate([(STICK_W - SLIDE_W) / 2, -1, TIER_H - NOTCH_D])
            cube([SLIDE_W, STICK_D + 2, NOTCH_D + 2]);
            
        // Weight-reduction / speed-printing center cutouts
        for (z_off = [30, 80, 130, 175]) {
            translate([-1, STICK_D / 2, z_off])
                rotate([0, 90, 0])
                    cylinder(d=10, h=STICK_W + 2);
        }
    }
}

// ==============================================================================
// PRINT BED LAYOUT (Lying flat, 100% Support-Free)
// ==============================================================================
if (part == "all") {
    // Pair of 1/8" Drawer Front T-Spacers
    translate([0, 0, 0])
        front_t_spacer();
    translate([45, 0, 0])
        front_t_spacer();
        
    // Slide Tier Story Stick (Lying on its side, fits easily on 256x256 bed)
    translate([95, 0, 0])
        rotate([0, -90, 0])
            slide_tier_stick();
} else if (part == "front_t_spacers") {
    front_t_spacer();
    translate([45, 0, 0]) front_t_spacer();
} else if (part == "slide_tier_stick") {
    rotate([0, -90, 0]) slide_tier_stick();
}
