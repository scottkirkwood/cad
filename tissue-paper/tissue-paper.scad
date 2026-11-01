// =============================================================================
// Parametric Kleenex Box Cover with Mathematical Textures & Multi-Color Support
// Designed for 3D Printing (Bambu Lab / FDM)
// =============================================================================

/* [Box Dimensions] */
// Total height of the cover (mm)
height = 72;
// Inside cavity depth/width (mm) - preserved from original box (110 - 2 = 108)
inner_depth = 108;
// Inside cavity length (mm) - preserved from original box (230 - 2 = 228)
inner_len = 228;
// Base wall thickness on vertical sides (mm)
wall_thick = 1.6;
// Top face thickness (mm)
top_thick = 1.6;
// Outer corner fillet radius (mm)
corner_r = 6;

/* [Tissue Dispenser Slot] */
// Width / minor diameter of dispensing slot (mm)
cutout_d = 65;
// Length ratio of the slot ellipse (130mm = 65 * 2.0)
cutout_len_ratio = 2.0;

/* [Vertical Wall Mathematical Pattern] */
// Mathematical texture on the vertical walls
pattern_type = "wave_vertical"; // [none: Smooth walls, wave_vertical: Vertical Fluted Sine Waves, wave_horizontal: Horizontal Ripple Waves]
// Wave amplitude / depth (mm) - added outward so interior fit is never compromised
wave_amp = 1.2;
// Number of wave cycles along the length (for wave_vertical)
waves_len = 14;
// Number of wave cycles along the depth (for wave_vertical)
waves_depth = 6;
// Wavelength along Z in mm (for wave_horizontal)
wave_wavelength_z = 12;

/* [Multi-Color & Export Options] */
// Multi-color boundary style for Bambu Studio / AMS
color_mode = "cap"; // [cap: Top Cap Split (only 1 filament swap!), inlay: Flush Rim Inlay (sides wrap to top), unified: Single Piece]
// Which part to render/export
part = "preview"; // [preview: Colored 3D Assembly, all: Single Solid, top: Top Part Only (STL), sides: Sides Part Only (STL)]

/* [Preview Colors] */
color_top = "GhostWhite";
color_sides = "DarkSlateGray";

// =============================================================================
// Internal Calculations
// =============================================================================
inner_h = height - top_thick;
inner_r = max(1, corner_r - wall_thick);
base_w = inner_depth + 2 * wall_thick;
base_l = inner_len + 2 * wall_thick;

$fn = $preview ? 36 : 72;

// =============================================================================
// 2D Profile Generators
// =============================================================================

// Smooth rounded rectangle
module rounded_rect_2d(w, l, r) {
    hull() {
        translate([ w/2 - r,  l/2 - r]) circle(r=r);
        translate([-w/2 + r,  l/2 - r]) circle(r=r);
        translate([ w/2 - r, -l/2 + r]) circle(r=r);
        translate([-w/2 + r, -l/2 + r]) circle(r=r);
    }
}

// 2D Profile with mathematical sine waves along edges and smooth corner arcs
module vertical_wave_2d(w, l, r, amp, nw, nl) {
    sw = w - 2 * r;
    sl = l - 2 * r;
    fn_edge = $preview ? 30 : 60;
    fn_corner = $preview ? 12 : 24;
    
    pts = [
        // Bottom edge (Y = -l/2): X from -sw/2 to sw/2
        for (i = [0:fn_edge])
            let(u = i / fn_edge, x = -sw/2 + u * sw, wave = amp * (1 - cos(u * nw * 360)) / 2)
            [x, -l/2 - wave],
        // Bottom-right corner arc
        for (i = [1:fn_corner])
            let(a = -90 + i * (90 / fn_corner))
            [w/2 - r + r * cos(a), -l/2 + r + r * sin(a)],
        // Right edge (X = w/2): Y from -sl/2 to sl/2
        for (i = [1:fn_edge])
            let(u = i / fn_edge, y = -sl/2 + u * sl, wave = amp * (1 - cos(u * nl * 360)) / 2)
            [w/2 + wave, y],
        // Top-right corner arc
        for (i = [1:fn_corner])
            let(a = 0 + i * (90 / fn_corner))
            [w/2 - r + r * cos(a), l/2 - r + r * sin(a)],
        // Top edge (Y = l/2): X from sw/2 down to -sw/2
        for (i = [1:fn_edge])
            let(u = i / fn_edge, x = sw/2 - u * sw, wave = amp * (1 - cos(u * nw * 360)) / 2)
            [x, l/2 + wave],
        // Top-left corner arc
        for (i = [1:fn_corner])
            let(a = 90 + i * (90 / fn_corner))
            [-w/2 + r + r * cos(a), l/2 - r + r * sin(a)],
        // Left edge (X = -w/2): Y from sl/2 down to -sl/2
        for (i = [1:fn_edge])
            let(u = i / fn_edge, y = sl/2 - u * sl, wave = amp * (1 - cos(u * nl * 360)) / 2)
            [-w/2 - wave, y],
        // Bottom-left corner arc
        for (i = [1:fn_corner-1])
            let(a = 180 + i * (90 / fn_corner))
            [-w/2 + r + r * cos(a), -l/2 + r + r * sin(a)]
    ];
    polygon(pts);
}

// Active outer 2D cross-section
module outer_profile_2d() {
    if (pattern_type == "wave_vertical") {
        vertical_wave_2d(base_w, base_l, corner_r, wave_amp, waves_depth, waves_len);
    } else {
        rounded_rect_2d(base_w, base_l, corner_r);
    }
}

// 3D Outer Solid Envelope
module outer_envelope(h) {
    if (pattern_type == "wave_horizontal") {
        steps = $preview ? 24 : 48;
        dz = h / steps;
        for (i = [0:steps-1]) {
            hull() {
                z1 = i * dz;
                z2 = (i + 1) * dz;
                w1 = base_w + wave_amp * (1 - cos(360 * z1 / wave_wavelength_z));
                l1 = base_l + wave_amp * (1 - cos(360 * z1 / wave_wavelength_z));
                w2 = base_w + wave_amp * (1 - cos(360 * z2 / wave_wavelength_z));
                l2 = base_l + wave_amp * (1 - cos(360 * z2 / wave_wavelength_z));
                translate([0, 0, z1]) linear_extrude(0.01) rounded_rect_2d(w1, l1, corner_r);
                translate([0, 0, z2]) linear_extrude(0.01) rounded_rect_2d(w2, l2, corner_r);
            }
        }
    } else {
        linear_extrude(h)
            outer_profile_2d();
    }
}

// =============================================================================
// Cutouts & Cavities
// =============================================================================

// Oval tissue dispenser slot cutout
module dispenser_cutout() {
    translate([0, 0, -1])
        scale([1, cutout_len_ratio, 1])
            cylinder(h = top_thick + 2, d = cutout_d, $fn = $preview ? 60 : 120);
}

// Inner cavity to fit over the cardboard Kleenex box (leaves bottom open)
module inner_cavity(extra_down=0) {
    translate([0, 0, top_thick - extra_down])
        linear_extrude(height - top_thick + extra_down + 2)
            rounded_rect_2d(inner_depth, inner_len, inner_r);
}

// =============================================================================
// Component Parts (for Multi-Color & Multi-Material Printing)
// =============================================================================

// TOP PART
module top_part() {
    if (color_mode == "inlay") {
        difference() {
            linear_extrude(top_thick)
                rounded_rect_2d(inner_depth, inner_len, inner_r);
            dispenser_cutout();
        }
    } else {
        difference() {
            if (pattern_type == "wave_horizontal") {
                outer_envelope(top_thick);
            } else {
                linear_extrude(top_thick)
                    outer_profile_2d();
            }
            dispenser_cutout();
        }
    }
}

// SIDES PART
module sides_part() {
    if (color_mode == "inlay") {
        difference() {
            outer_envelope(height);
            inner_cavity();
            translate([0, 0, -0.5])
                linear_extrude(top_thick + 0.5)
                    rounded_rect_2d(inner_depth, inner_len, inner_r);
        }
    } else {
        difference() {
            translate([0, 0, top_thick])
                if (pattern_type == "wave_horizontal") {
                    translate([0, 0, -top_thick])
                        intersection() {
                            outer_envelope(height);
                            translate([0, 0, top_thick])
                                linear_extrude(height - top_thick + 1)
                                    square([base_w * 3, base_l * 3], center=true);
                        }
                } else {
                    linear_extrude(height - top_thick)
                        outer_profile_2d();
                }
            // Cut cleanly through bottom with extra_down=1 to prevent coplanar z-fighting
            inner_cavity(extra_down=1);
        }
    }
}

// =============================================================================
// Output Assembly
// =============================================================================
module kleenex_box() {
    if (part == "top") {
        top_part();
    } else if (part == "sides") {
        sides_part();
    } else if (part == "all" || color_mode == "unified") {
        difference() {
            outer_envelope(height);
            inner_cavity();
            dispenser_cutout();
        }
    } else {
        // "preview": Dual-color rendering
        color(color_top) top_part();
        color(color_sides) sides_part();
    }
}

kleenex_box();
