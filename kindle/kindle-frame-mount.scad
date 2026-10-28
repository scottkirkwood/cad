// ====================================================================
// PICTURE FRAME INSERT FOR KINDLE PAPERWHITE
// ====================================================================
// Custom 3D printed mat board and snap-in cradle for Kindle Paperwhite.
// Creates a clean, professional white bezel around the e-ink screen,
// perfectly centered in a standard picture frame, with integrated
// snap-in retention clips and 90-degree USB routing.
//
// Recommended 3D print orientation:
//   Print flat with front face down on build plate (Z=0).
//   100% support-free print!
// ====================================================================

$fn = 60; // Curve resolution
eps = 0.05; // CSG overlap epsilon for manifold union

// ====================================================================
// 1. PICTURE FRAME PARAMETERS (mm)
// ====================================================================
// Dimensions of the inner opening / rabbet of the wooden frame
frame_inner_w        = 132.0; // Width of frame opening (13.2 cm)
frame_inner_h        = 183.0; // Height of frame opening (18.3 cm)
frame_clearance      = 1.5;   // Fit tolerance around outer edge of mat (1.5 mm all around to prevent bowing)
mat_thickness        = 2.4;   // Front mat faceplate thickness (mm)
mat_corner_radius    = 3.0;   // Outer corner radius to clear frame corners smoothly (mm)

// ====================================================================
// 2. KINDLE PAPERWHITE PARAMETERS (mm)
// ====================================================================
kindle_w             = 116.0; // Kindle body width (11.6 cm)
kindle_h             = 168.0; // Kindle body height (16.8 cm)
kindle_t             = 8.5;   // Kindle body thickness (mm)
kindle_corner_r      = 9.0;   // Kindle corner radius (mm)
kindle_tolerance     = 0.4;   // Pocket clearance for easy snap fit (mm)

// Kindle bezel widths (used for perfect display centering)
kindle_bezel_top     = 20.0;  // Plastic bezel at top of Kindle (mm)
kindle_bezel_bottom  = 27.0;  // Plastic bezel at bottom of Kindle with USB (mm)

// ====================================================================
// 3. DISPLAY / SCREEN WINDOW PARAMETERS (mm)
// ====================================================================
// Window enlarged by 2mm all around (+4mm total) to reveal a slim black border
// around the active screen and make edge touch controls easier to access.
screen_w             = 94.0;  // Visible display window width (mm, +2mm all around)
screen_h             = 126.0; // Visible display window height (mm, +2mm all around)
screen_corner_r      = 2.0;   // Corner rounding on display window (mm)
screen_chamfer       = 1.6;   // 45-degree inward bevel on front face (mm)

// ====================================================================
// 4. ORIENTATION & CABLE ROUTING PARAMETERS (mm)
// ====================================================================
// Set to true if USB port is at bottom (-Y), or false if at top (+Y)
usb_at_bottom        = true;

usb_cutout_w         = 50.0;  // Width for 90-degree USB plug & power button (mm)
frame_hack_depth     = 9.0;   // Depth of user cutout in wooden frame (mm)

// ====================================================================
// 5. SNAP-IN CRADLE PARAMETERS (mm)
// ====================================================================
wall_thickness       = 2.2;   // Cradle wall thickness (mm)
snap_lip_overhang    = 0.8;   // Retention lip overhang (mm)
snap_tab_length      = 22.0;  // Length of each flexible snap tab (mm)
snap_slot_w          = 1.5;   // Width of relief slots flanking each tab (mm)
snap_y_offset        = 42.0;  // Distance of snap tabs from Kindle center (mm)

// Optional frame mounting holes in corners (default false for pristine mat face)
add_frame_mounting_holes = false;
mount_hole_dia       = 3.0;   // Screw hole diameter (mm)

// ====================================================================
// 8. CARDBOARD BACKING RETENTION TABS (mm)
// ====================================================================
// 4 slim tabs with low-profile nubbins along the long sides to hold
// the cardboard backing and stand, with extra Z clearance for Kindle bow.
add_cardboard_clips      = true;  // Set true to generate the 4 backing clips
cardboard_z_height       = 6.0;   // Z height from cradle shelf to nubbin (was 3mm, doubled for Kindle bow)
cardboard_w              = 129.0; // Width of cardboard backing (nominal 13 cm)
cardboard_h              = 180.0; // Height of cardboard backing (nominal 18 cm)
cardboard_clip_len       = 14.0;  // Length of each clip along the long side (mm)
cardboard_clip_y_top     = 65.0;  // Y position of top clip pair along long side (mm)
cardboard_clip_y_bot     = -70.0; // Y position of bottom clip pair along long side (mm)
tab_wall_t               = 1.0;   // Slim tab upright thickness (mm, reduced from 1.5mm)
nubbin_overhang          = 0.75;  // Low-profile detent bump (mm, replaced bulky 2mm triangle)

// Preview helper toggles
show_ghost_kindle        = false; // Set true in OpenSCAD GUI to see Kindle placement ghost
show_ghost_cardboard     = false; // Set true in OpenSCAD GUI to see Cardboard Backing ghost

// ====================================================================
// COMPUTED OFFSETS & DIMENSIONS
// ====================================================================
mat_w = frame_inner_w - 2 * frame_clearance;
mat_h = frame_inner_h - 2 * frame_clearance;

pocket_w = kindle_w + 2 * kindle_tolerance;
pocket_h = kindle_h + 2 * kindle_tolerance;
cradle_wall_w = pocket_w + 2 * wall_thickness;
cradle_wall_h = pocket_h + 2 * wall_thickness;

// Vertical offset of Kindle body to center the active screen at (0, 0)
kindle_y_offset = usb_at_bottom ?
    -((kindle_bezel_bottom - kindle_bezel_top) / 2) :
    +((kindle_bezel_bottom - kindle_bezel_top) / 2);

// ====================================================================
// 2D HELPER SHAPES
// ====================================================================
module rounded_rect_2d(w, h, r) {
    r_eff = min(r, min(w/2, h/2));
    hull() {
        translate([ w/2 - r_eff,  h/2 - r_eff]) circle(r = r_eff);
        translate([-w/2 + r_eff,  h/2 - r_eff]) circle(r = r_eff);
        translate([-w/2 + r_eff, -h/2 + r_eff]) circle(r = r_eff);
        translate([ w/2 - r_eff, -h/2 + r_eff]) circle(r = r_eff);
    }
}

// ====================================================================
// 3D MODULES
// ====================================================================

// Screen cutout with 45-degree chamfer facing the front (Z=0)
module screen_cutout() {
    // 45-degree beveled entry on the front face (Z=0 to Z=screen_chamfer)
    hull() {
        translate([0, 0, -eps])
            linear_extrude(height = eps)
                rounded_rect_2d(screen_w + 2*screen_chamfer, screen_h + 2*screen_chamfer, screen_corner_r + screen_chamfer);
        translate([0, 0, screen_chamfer])
            linear_extrude(height = eps)
                rounded_rect_2d(screen_w, screen_h, screen_corner_r);
    }
    // Straight cutout through the rest of the mat thickness
    translate([0, 0, screen_chamfer - eps])
        linear_extrude(height = mat_thickness - screen_chamfer + 2*eps)
            rounded_rect_2d(screen_w, screen_h, screen_corner_r);
}

// Front mat faceplate
module front_mat() {
    difference() {
        linear_extrude(height = mat_thickness)
            rounded_rect_2d(mat_w, mat_h, mat_corner_radius);
        screen_cutout();
    }
}

// Cradle walls surrounding the Kindle (overlaps mat slightly for manifold solid)
module cradle_walls() {
    translate([0, kindle_y_offset, mat_thickness - eps]) {
        difference() {
            // Outer wall shape
            linear_extrude(height = kindle_t + eps)
                rounded_rect_2d(cradle_wall_w, cradle_wall_h, kindle_corner_r + wall_thickness);
            // Pocket void
            translate([0, 0, eps])
                linear_extrude(height = kindle_t + 1.0)
                    rounded_rect_2d(pocket_w, pocket_h, kindle_corner_r);
        }
    }
}

// Snap tab retention lip on inner wall
module snap_lip(is_left) {
    x_base = is_left ? -(pocket_w / 2 + eps) : (pocket_w / 2 + eps);
    x_tip  = is_left ? -(pocket_w / 2 - snap_lip_overhang) : (pocket_w / 2 - snap_lip_overhang);
    z_top  = mat_thickness + kindle_t;
    z_mid  = z_top - 0.8;
    z_bot  = z_top - 2.0;

    // Prismatic snap lip profile extruded along Y
    rotate([90, 0, 0])
        linear_extrude(height = snap_tab_length, center = true)
            polygon(points = [
                [x_base, z_bot],
                [x_tip,  z_mid],
                [x_tip,  z_top],
                [x_base, z_top]
            ]);
}

// Relief slot pair flanking each snap tab (cuts ONLY through the wall, NOT the mat!)
module snap_relief_slots(is_left, y_pos) {
    x_pos = is_left ? -(pocket_w / 2 + wall_thickness / 2) : (pocket_w / 2 + wall_thickness / 2);
    for (dy = [-snap_tab_length/2 - snap_slot_w/2, snap_tab_length/2 + snap_slot_w/2]) {
        translate([x_pos, kindle_y_offset + y_pos + dy, mat_thickness + (kindle_t + 1.0)/2])
            cube([wall_thickness * 2.5, snap_slot_w, kindle_t + 1.0], center = true);
    }
}

// USB connector & cable relief cutout at bottom (does NOT cut front mat face)
module usb_cable_cutout() {
    y_cutout = usb_at_bottom ?
        (kindle_y_offset - pocket_h/2) :
        (kindle_y_offset + pocket_h/2);
    
    translate([0, y_cutout, mat_thickness + (kindle_t + 1.0)/2])
        cube([usb_cutout_w, wall_thickness * 4 + frame_hack_depth * 2, kindle_t + 1.0], center = true);
}

// Optional frame mounting screw holes in the mat corners
module frame_mounting_holes() {
    if (add_frame_mounting_holes) {
        corner_x = mat_w / 2 - 5.0;
        corner_y = mat_h / 2 - 5.0;
        for (sx = [-1, 1], sy = [-1, 1]) {
            translate([sx * corner_x, sy * corner_y, -eps])
                cylinder(d = mount_hole_dia, h = mat_thickness + 2*eps);
        }
    }
}

// Cardboard backing retention tab with slim wall and low-profile nubbin
module cardboard_clip(is_left) {
    x_dir    = is_left ? -1 : 1;
    x_cradle = x_dir * (cradle_wall_w / 2);
    x_outer  = x_dir * (mat_w / 2);
    x_inner  = x_outer - x_dir * tab_wall_t;
    x_nubbin = x_inner - x_dir * nubbin_overhang;

    z_base   = mat_thickness - eps;
    z_shelf  = mat_thickness + kindle_t;
    z_nubbin_bot = z_shelf + cardboard_z_height - 0.8;
    z_nubbin_mid = z_shelf + cardboard_z_height;
    z_nubbin_top = z_shelf + cardboard_z_height + 0.8;
    z_top    = z_nubbin_top + 1.0;

    rotate([90, 0, 0])
        linear_extrude(height = cardboard_clip_len, center = true)
            polygon(points = [
                // Base firmly anchored to cradle wall & mat
                [x_cradle - x_dir * eps, z_base],
                [x_outer, z_base],
                [x_outer, z_top - 0.5],
                [x_outer - x_dir * 0.5, z_top],
                // Top lead-in down to nubbin peak
                [x_inner, z_top],
                [x_nubbin, z_nubbin_mid],
                [x_inner, z_nubbin_bot],
                // Slim vertical inner wall down to cradle shelf
                [x_inner, z_shelf],
                [x_cradle - x_dir * eps, z_shelf]
            ]);
}

// ====================================================================
// COMPLETE ASSEMBLED HOLDER
// ====================================================================
module kindle_frame_mount() {
    difference() {
        union() {
            // Front white mat faceplate
            front_mat();

            // Cradle perimeter walls
            cradle_walls();

            // Snap-in retention tabs on left and right walls for Kindle
            for (y_tab = [-snap_y_offset, snap_y_offset]) {
                translate([0, kindle_y_offset + y_tab, 0]) {
                    snap_lip(is_left = true);
                    snap_lip(is_left = false);
                }
            }

            // 4 Clips along the long sides to hold the 18x13cm cardboard backing
            if (add_cardboard_clips) {
                for (y_pos = [cardboard_clip_y_top, cardboard_clip_y_bot]) {
                    translate([0, y_pos, 0]) {
                        cardboard_clip(is_left = true);
                        cardboard_clip(is_left = false);
                    }
                }
            }
        }

        // Cut relief slots for each Kindle snap tab (stops at mat surface)
        for (y_tab = [-snap_y_offset, snap_y_offset]) {
            snap_relief_slots(is_left = true,  y_pos = y_tab);
            snap_relief_slots(is_left = false, y_pos = y_tab);
        }

        // Cutout for 90-degree USB plug and power button (stops at mat surface)
        usb_cable_cutout();

        // Optional corner screw holes to attach to frame
        frame_mounting_holes();
    }
}

// ====================================================================
// RENDER
// ====================================================================
kindle_frame_mount();

// ====================================================================
// PREVIEW HELPERS: Ghost views (F5 preview only)
// ====================================================================
if (show_ghost_kindle) {
    %translate([0, kindle_y_offset, mat_thickness + kindle_t/2]) {
        color([0.2, 0.2, 0.2, 0.4])
            linear_extrude(height = kindle_t, center = true)
                rounded_rect_2d(kindle_w, kindle_h, kindle_corner_r);
        // Display screen ghost
        color([0.9, 0.9, 0.9, 0.6])
            translate([0, -kindle_y_offset, -kindle_t/2 + 0.1])
                linear_extrude(height = 0.2)
                    rounded_rect_2d(screen_w, screen_h, screen_corner_r);
    }
}

if (show_ghost_cardboard) {
    %translate([0, 0, mat_thickness + kindle_t + cardboard_z_height/2]) {
        color([0.65, 0.5, 0.35, 0.5])
            linear_extrude(height = cardboard_z_height, center = true)
                rounded_rect_2d(cardboard_w, cardboard_h, 3.0);
    }
}
