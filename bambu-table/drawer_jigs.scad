// ==============================================================================
// 3D PRINTABLE DRAWER SLIDE INSTALLATION JIGS FOR BAMBU PRINTER (V2)
// ==============================================================================
// 100% SUPPORT-FREE DESIGN:
// Every part is engineered specifically for FDM 3D printing with 0 overhangs.
// No supports, no brims, no post-processing required.
//
// Includes 3 Jigs:
// 1. SLIDE_SETBACK_CRADLE: Hooks over front 2x4 leg/divider, automatically
//    sets the 2.5mm (3/32") setback, and cradles the slide dead-level while screwing.
// 2. DRAWER_BOX_MOUNTING_BLOCKS (Pair): Sits under drawer box so slide rails
//    align perfectly 6mm (1/4") up and parallel with bottom of the box.
// 3. REVEAL_SHIMS (Set of 4): 1/8" (3.18mm) U-shims with pull tabs for drawer fronts.
// ==============================================================================

part = "all"; // [all, setback_cradle, box_mount_spacers, reveal_shims]

$fn = 60;

// ==============================================================================
// JIG 1: SLIDE SETBACK CRADLE (100% Support-Free)
// ==============================================================================
module setback_cradle() {
    // Total footprint: 40mm wide x 85mm long x 28mm high
    // All features are open to +Z: ZERO ceilings, ZERO overhangs.
    difference() {
        // Solid base block resting flat on build plate
        cube([40, 85, 28]);
        
        // 1. Slide Support Shelf:
        // Ledge at Z = 10mm. Metal slide rests on this shelf (10mm to 29mm).
        // Leaves an 8mm guide wall on the left (X=0 to X=8) to reference the wood frame.
        translate([8, -1, 10])
            cube([33, 87, 20]);
            
        // 2. Setback Stop (Front Lip):
        // The slide butts against a 2.5mm front wall at Y = 2.5mm.
        // Recesses the metal slide by exactly 2.5mm (3/32") behind the 2x4 front face!
        translate([6, 2.5, 8])
            cube([35, 85, 22]);
            
        // 3. Front Face Frame Registration Hook:
        // Cutout for the front of the 2x4 / divider (from Y = -1 to Y = 16)
        translate([-1, -1, 10])
            cube([10, 18, 20]);
            
        // 4. Screw Access Window:
        // Open vertical slot so you can drive the front mounting screw into the wood
        translate([3, 26, -1])
            cube([38, 28, 32]);
            
        // 5. Chamfered rear corners for smooth handling
        translate([32, 75, -1])
            rotate([0, 0, 45])
                cube([20, 20, 32]);
    }
}

// ==============================================================================
// JIG 2: DRAWER BOX MOUNTING BLOCKS (Pair - Support-Free)
// ==============================================================================
module box_mount_spacer() {
    // Sits flat on the bench under the drawer box.
    // Holds the slide rail exactly 6.35mm (1/4") up from bottom of drawer box.
    difference() {
        union() {
            cube([55, 35, 6.35]); // 1/4" standoff step
            cube([10, 35, 22.0]); // Side fence that indexes against the drawer box side
        }
        // Easy-grip finger notch on top of the fence
        translate([5, 17.5, 18])
            rotate([0, 45, 0])
                cube([10, 20, 10], center=true);
    }
}

// ==============================================================================
// JIG 3: 1/8" (3.18mm) DRAWER FRONT REVEAL SHIMS (Support-Free)
// ==============================================================================
module reveal_shim() {
    SHIM_T = 3.175; // 1/8"
    // Sits completely flat on bed. Debossed text (0.6mm into top face).
    difference() {
        union() {
            // Main U-spacer
            cube([34, 30, SHIM_T]);
            // Ergonomic pull tab
            translate([0, 30, 0])
                cube([34, 16, SHIM_T]);
        }
        // Center clearance slot
        translate([9.5, -1, -0.5])
            cube([15, 20, SHIM_T + 1]);
            
        // Debossed label into the pull tab (0.6mm deep, no overhangs)
        translate([11, 35, SHIM_T - 0.6])
            linear_extrude(0.8)
                text("1/8\"", size=7, font="Liberation Sans:style=Bold");
    }
}

// ==============================================================================
// PRINT BED LAYOUT
// ==============================================================================
if (part == "all") {
    // 1. Setback Cradle
    translate([0, 0, 0])
        setback_cradle();
        
    // 2. Pair of Box Mount Spacers
    translate([52, 0, 0])
        box_mount_spacer();
    translate([52, 45, 0])
        box_mount_spacer();
        
    // 3. Set of Four 1/8" Reveal Shims
    for (i = [0:3]) {
        translate([120, i * 24, 0])
            reveal_shim();
    }
} else if (part == "setback_cradle") {
    setback_cradle();
} else if (part == "box_mount_spacers") {
    box_mount_spacer();
    translate([0, 45, 0]) box_mount_spacer();
} else if (part == "reveal_shims") {
    for (i = [0:3]) {
        translate([0, i * 24, 0]) reveal_shim();
    }
}
