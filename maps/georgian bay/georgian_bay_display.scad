// =========================================================================
// GEORGIAN BAY 3D DISPLAY & LIGHTBOX (Refined v4)
// Longuissa Bay to South Bay Cove, Thirty Thousand Islands, Georgian Bay
// Designed for Bambu Lab 3D Printers (H2C, X1C, P1S, A1) & AMS multi-color
// All layers share the exact page dimensions (163.8 x 228.6 mm)
// =========================================================================

mode = "complete"; // [complete, backlit_faceplate, lightbox_box, water_base, mainland, islands, buoys]

display_width  = 163.8;  // 163.8 mm (standard Bambu lightbox size)
display_height = 228.6; // 228.6 mm (9.0 inches)

t_water_base   = 1.0;  // 1.0 mm (translucent light transmission)
t_mainland     = 2.2;  // 2.2 mm muted mainland
t_islands      = 2.6;  // 2.6 mm crisp raised islands
t_buoys        = 3.2;  // 3.2 mm raised navigation spar markers
t_frame_lip    = 7.0;  // 7.0 mm perimeter snap-lip for lightbox housing

box_depth      = 38.0; // 38 mm box depth for LED strip
wall_thick     = 2.4;  // 2.4 mm sturdy housing wall
cable_hole_dia = 9.0;  // 9 mm hole for DC / USB-C power cord

c_water      = [0.05, 0.20, 0.35, 0.95]; // Deep Nautical Blue
c_mainland   = [0.18, 0.22, 0.25, 1.0];  // Muted Slate Charcoal
c_islands    = [0.28, 0.35, 0.42, 1.0];  // Granite Island Relief
c_buoy_red   = [0.90, 0.15, 0.20, 1.0];  // Red Spar
c_frame      = [0.08, 0.10, 0.14, 1.0];  // Dark Charcoal Bezel

if (mode == "complete") {
    full_display();
} else if (mode == "backlit_faceplate") {
    backlit_faceplate();
} else if (mode == "lightbox_box") {
    lightbox_enclosure();
} else if (mode == "water_base") {
    color(c_water) water_plate();
} else if (mode == "mainland") {
    color(c_mainland) mainland_part();
} else if (mode == "islands") {
    color(c_islands) islands_part();
} else if (mode == "buoys") {
    color(c_buoy_red) buoys_part();
}

module water_plate() {
    cube([display_width, display_height, t_water_base]);
}

module mainland_part() {
    linear_extrude(height = t_mainland)
        import("layers/02_mainland.svg");
}

module islands_part() {
    linear_extrude(height = t_islands)
        import("layers/03_islands.svg");
}

module buoys_part() {
    linear_extrude(height = t_buoys)
        import("layers/04_buoys.svg");
}

module frame_rim() {
    difference() {
        cube([display_width, display_height, t_frame_lip]);
        translate([wall_thick, wall_thick, -1])
            cube([display_width - 2 * wall_thick, display_height - 2 * wall_thick, t_frame_lip + 2]);
    }
}

module full_display() {
    union() {
        color(c_water) water_plate();
        color(c_mainland) mainland_part();
        color(c_islands) islands_part();
        color(c_buoy_red) buoys_part();
        color(c_frame) frame_rim();
    }
}

module backlit_faceplate() {
    union() {
        water_plate();
        mainland_part();
        islands_part();
        buoys_part();
        frame_rim();
    }
}

module lightbox_enclosure() {
    outer_w = display_width + 1.2;
    outer_h = display_height + 1.2;
    
    difference() {
        cube([outer_w, outer_h, box_depth]);
        translate([wall_thick, wall_thick, wall_thick])
            cube([outer_w - 2 * wall_thick, outer_h - 2 * wall_thick, box_depth]);
        translate([wall_thick - 0.6, wall_thick - 0.6, box_depth - t_frame_lip])
            cube([display_width + 0.4, display_height + 0.4, t_frame_lip + 1]);
        translate([outer_w / 2, -1, wall_thick + cable_hole_dia / 2 + 2])
            rotate([-90, 0, 0])
                cylinder(r = cable_hole_dia / 2, h = wall_thick + 2, $fn = 32);
        translate([outer_w / 2, outer_h - 30, -1])
            cylinder(r = 5.0, h = wall_thick + 2, $fn = 32);
        translate([outer_w / 2 - 2.5, outer_h - 30, -1])
            cube([5.0, 10.0, wall_thick + 2]);
    }
}
