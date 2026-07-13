// --- PARAMETERS (All measurements in millimeters) ---
// Set part = 0 for full model, 1 for Left-Front, 2 for Left-Back, 3 for Middle, 4 for Right
part = 0; // [0: Full, 1: Left-Front, 2: Left-Back, 3: Middle, 4: Right]

$fn = 60; // Smoothness for rounded corners/edges
inch = 25.4;

// Floor Opening Dimensions (Inside fitting)
floor_length = 10.25 * inch; 
floor_width  = 4.125 * inch;
floor_depth  = 20; // How deep the collar inserts into the floor

// Vanity / Toe Kick Dimensions
vanity_clearance = 3.5 * inch; // Available height under the vanity floor (88.9 mm)
wall_thickness   = 2.0;        // Thickness of the printed duct walls

// Front Vent Dimensions (Exiting the kick plate)
front_width  = 10.0 * inch;
front_height = 2.5 * inch; 
exit_depth   = 2.0 * inch; // Depth of the duct manifold at the kickplate exit

// Positioning parameters based on the physical measurements in the image:
kickplate_offset = 0.5 * inch; // Distance from the front edge of the floor vent cutout to the inside face of the kickplate
kickplate_Y = -floor_length/2 - kickplate_offset;

// The hydraulics cutout is in the center of the vanity, to the right of the floor vent.
// Distance from the right edge of the floor vent cutout to the left edge of the hydraulics cutout is 10.25".
exit_center_x = floor_width/2 + 10.25 * inch + 2.0625 * inch; 

// The top of the outer duct shell must not exceed vanity_clearance (88.9 mm).
exit_center_z = vanity_clearance - front_height/2 - wall_thickness;

eps = 0.02;

// Split positions (X-coordinates) for printing on a CR-6 SE (max 235x235mm bed)
// This splits the 548.5mm wide duct into 3 sections along X.
// The left-most section (which contains the 264.4mm long floor collar) is further split along Y=0.
// This results in 4 parts that all fit comfortably within the 235x235mm print volume.
cut1_x = 130;
cut2_x = 310;

// --- GEOMETRY ---

// Bezier Control Points for the center path of the duct.
P0 = [0, 0, 0];
P1 = [0, 0, 45];
P2 = [exit_center_x, kickplate_Y + exit_depth/2 + 25, exit_center_z];
P3 = [exit_center_x, kickplate_Y + exit_depth/2, exit_center_z];

function bezier(t) = 
    (1-t)*(1-t)*(1-t)*P0 + 
    3*(1-t)*(1-t)*t*P1 + 
    3*(1-t)*t*t*P2 + 
    t*t*t*P3;

// Recursive binary search function to find the parameter t at a given X-coordinate cut plane
function find_t(target_x, low=0, high=1, steps=10) =
    steps == 0 ? (low + high) / 2 :
    (
        let(mid = (low + high) / 2,
            val = exit_center_x * (3*mid*mid - 2*mid*mid*mid))
        val > target_x ? find_t(target_x, low, mid, steps - 1) : find_t(target_x, mid, high, steps - 1)
    );

module collar(offset = 0) {
    // Rounded rectangular collar that fits into the floor cutout
    r = min(15, min(floor_width, floor_length)/2 - 1) + offset;
    translate([0, 0, -floor_depth/2 - offset/2])
        linear_extrude(height = floor_depth + offset + eps, center = true)
            offset(r = r)
                square([floor_width + 2*offset - 2*r, floor_length + 2*offset - 2*r], center = true);
}

// S-curve interpolation function (smoothstep) for dimensions transition
function s_curve(t) = t * t * (3 - 2 * t);

module slice(t, offset = 0) {
    p = bezier(t);
    
    // Slices remain axis-aligned to prevent height violations from 3D rotations,
    // which allows the duct to fit perfectly under the low vanity floor.
    dx = floor_width + (front_width - floor_width) * s_curve(t) + 2 * offset;
    dy = floor_length + (exit_depth - floor_length) * s_curve(t) + 2 * offset;
    dz = 2.0 + (front_height - 2.0) * s_curve(t) + 2 * offset;
    
    r = min(15, min(dx, dy)/2 - 1);
    
    translate(p)
        linear_extrude(height = dz, center = true)
            offset(r = r)
                square([dx - 2*r, dy - 2*r], center = true);
}

module solid_duct(offset = 0) {
    steps = 30;
    for (i = [0 : steps - 1]) {
        t1 = i / steps;
        t2 = (i + 1) / steps;
        hull() {
            slice(t1, offset);
            slice(t2, offset);
        }
    }
}

// Solid outer block of the entire duct (without hollowing)
module outer_solid(offset = wall_thickness) {
    union() {
        collar(offset);
        solid_duct(offset);
    }
}

// Inner hollow volume of the entire duct
module inner_hollow() {
    union() {
        collar(0);
        solid_duct(0);
    }
}

// --- ALIGNMENT JOINTS (X-cuts at X=130 and X=310) ---

module x_joint_block(cut_x, side) {
    // Generate solid blocks that go deep into the duct wall to avoid gaps on curved slopes
    // side = "left" (X < cut_x) or "right" (X > cut_x)
    t = find_t(cut_x);
    p = bezier(t);
    dx = floor_width + (front_width - floor_width) * s_curve(t);
    dy = floor_length + (exit_depth - floor_length) * s_curve(t);
    dz = 2.0 + (front_height - 2.0) * s_curve(t);
    
    y1 = p[1] - dy/2 + 20;
    z1 = p[2] + dz/2;
    
    y2 = p[1] + dy/2 - 20;
    z2 = p[2] + dz/2;
    
    y3 = p[1] + dy/2;
    z3 = p[2];
    
    x_offset = (side == "left") ? -10 : 0;
    
    // Top-Front Block (extends 8mm deep into Z to prevent gaps on slope)
    translate([cut_x + x_offset, y1 - 6, z1 - 8])
        cube([10, 12, 12]);
        
    // Top-Back Block
    translate([cut_x + x_offset, y2 - 6, z2 - 8])
        cube([10, 12, 12]);
        
    // Back-Middle Block (extends 8mm deep into Y to prevent gaps on slope)
    translate([cut_x + x_offset, y3 - 8, z3 - 6])
        cube([10, 12, 12]);
}

module x_joint_pin(cut_x) {
    // Cylindrical pins extending from the left side of the cut to the right side
    t = find_t(cut_x);
    p = bezier(t);
    dx = floor_width + (front_width - floor_width) * s_curve(t);
    dy = floor_length + (exit_depth - floor_length) * s_curve(t);
    dz = 2.0 + (front_height - 2.0) * s_curve(t);
    
    y1 = p[1] - dy/2 + 20;
    z1 = p[2] + dz/2;
    y2 = p[1] + dy/2 - 20;
    z2 = p[2] + dz/2;
    y3 = p[1] + dy/2;
    z3 = p[2];
    
    // Pins: 3mm diameter, 4mm length (centered inside the 12mm high blocks)
    // Top-Front Pin
    translate([cut_x, y1, z1 - 2])
        rotate([0, 90, 0])
            cylinder(d=3, h=4, $fn=12);
            
    // Top-Back Pin
    translate([cut_x, y2, z2 - 2])
        rotate([0, 90, 0])
            cylinder(d=3, h=4, $fn=12);
            
    // Back-Middle Pin
    translate([cut_x, y3 - 2, z3])
        rotate([0, 90, 0])
            cylinder(d=3, h=4, $fn=12);
}

module x_joint_hole(cut_x) {
    // Matching sockets with 0.4mm printer clearance for assembly tolerance
    t = find_t(cut_x);
    p = bezier(t);
    dx = floor_width + (front_width - floor_width) * s_curve(t);
    dy = floor_length + (exit_depth - floor_length) * s_curve(t);
    dz = 2.0 + (front_height - 2.0) * s_curve(t);
    
    y1 = p[1] - dy/2 + 20;
    z1 = p[2] + dz/2;
    y2 = p[1] + dy/2 - 20;
    z2 = p[2] + dz/2;
    y3 = p[1] + dy/2;
    z3 = p[2];
    
    // Holes: 3.4mm diameter, 5mm depth
    // Top-Front Hole
    translate([cut_x - 0.1, y1, z1 - 2])
        rotate([0, 90, 0])
            cylinder(d=3.4, h=5, $fn=12);
            
    // Top-Back Hole
    translate([cut_x - 0.1, y2, z2 - 2])
        rotate([0, 90, 0])
            cylinder(d=3.4, h=5, $fn=12);
            
    // Back-Middle Hole
    translate([cut_x - 0.1, y3 - 2, z3])
        rotate([0, 90, 0])
            cylinder(d=3.4, h=5, $fn=12);
}

// --- ALIGNMENT JOINTS (Y-cut at Y=0 for Left Part) ---

module y_joint_block(side) {
    // Places blocks at the Y=0 plane on the left part (X < cut1_x)
    // side = "front" (Y < 0) or "back" (Y > 0)
    y_offset = (side == "front") ? -10 : 0;
    
    // 1. Top of the duct at X=30
    t_30 = find_t(30);
    p_30 = bezier(t_30);
    dz_30 = 2.0 + (front_height - 2.0) * s_curve(t_30);
    z_30 = p_30[2] + dz_30/2;
    translate([30 - 6, y_offset, z_30 - 8])
        cube([12, 10, 12]);
        
    // 2. Top of the duct at X=90
    t_90 = find_t(90);
    p_90 = bezier(t_90);
    dz_90 = 2.0 + (front_height - 2.0) * s_curve(t_90);
    z_90 = p_90[2] + dz_90/2;
    translate([90 - 6, y_offset, z_90 - 8])
        cube([12, 10, 12]);
        
    // 3. Left wall of the collar at X = -floor_width/2 - wall_thickness
    cx = -floor_width/2 - wall_thickness;
    translate([cx - 4, y_offset, -15])
        cube([10, 10, 12]);
}

module y_joint_pin() {
    // Pins extending from Y=0 in the +Y direction (from Front to Back)
    // 1. Top at X=30
    t_30 = find_t(30);
    p_30 = bezier(t_30);
    dz_30 = 2.0 + (front_height - 2.0) * s_curve(t_30);
    z_30 = p_30[2] + dz_30/2;
    translate([30, 0, z_30 - 2])
        rotate([-90, 0, 0])
            cylinder(d=3, h=4, $fn=12);
            
    // 2. Top at X=90
    t_90 = find_t(90);
    p_90 = bezier(t_90);
    dz_90 = 2.0 + (front_height - 2.0) * s_curve(t_90);
    z_90 = p_90[2] + dz_90/2;
    translate([90, 0, z_90 - 2])
        rotate([-90, 0, 0])
            cylinder(d=3, h=4, $fn=12);
            
    // 3. Collar at Left Wall
    cx = -floor_width/2 - wall_thickness;
    translate([cx + 1, 0, -9])
        rotate([-90, 0, 0])
            cylinder(d=3, h=4, $fn=12);
}

module y_joint_hole() {
    // Matching sockets in the back part (Y > 0)
    // 1. Top at X=30
    t_30 = find_t(30);
    p_30 = bezier(t_30);
    dz_30 = 2.0 + (front_height - 2.0) * s_curve(t_30);
    z_30 = p_30[2] + dz_30/2;
    translate([30, -0.1, z_30 - 2])
        rotate([-90, 0, 0])
            cylinder(d=3.4, h=5, $fn=12);
            
    // 2. Top at X=90
    t_90 = find_t(90);
    p_90 = bezier(t_90);
    dz_90 = 2.0 + (front_height - 2.0) * s_curve(t_90);
    z_90 = p_90[2] + dz_90/2;
    translate([90, -0.1, z_90 - 2])
        rotate([-90, 0, 0])
            cylinder(d=3.4, h=5, $fn=12);
            
    // 3. Collar at Left Wall
    cx = -floor_width/2 - wall_thickness;
    translate([cx + 1, -0.1, -9])
        rotate([-90, 0, 0])
            cylinder(d=3.4, h=5, $fn=12);
}

// --- CUTTERS FOR EXIT HOLES ---
module exit_cutters() {
    // Floor collar opening
    translate([-floor_width, -floor_length, -floor_depth - wall_thickness - 2])
        cube([floor_width * 2, floor_length * 2, 2.5]);
        
    // Kickplate front exit
    z_min = exit_center_z - front_height/2;
    translate([exit_center_x - front_width/2 - 10, kickplate_Y - wall_thickness - 2, z_min - 10])
        cube([front_width + 20, wall_thickness + 3, front_height + 20]);
}

// --- RENDER LOGIC ---
if (part == 0) {
    difference() {
        outer_solid(wall_thickness);
        inner_hollow();
        exit_cutters();
    }
} else if (part == 1) {
    // Render Left-Front Part: X < cut1_x, Y < 0
    difference() {
        union() {
            intersection() {
                outer_solid(wall_thickness);
                translate([-500, -500, -500]) cube([500 + cut1_x, 500, 1000]);
            }
            x_joint_block(cut1_x, "left");
            x_joint_pin(cut1_x);
            
            y_joint_block("front");
            y_joint_pin();
        }
        inner_hollow();
        exit_cutters();
        
        translate([cut1_x, -500, -500]) cube([500, 1000, 1000]);
        translate([-500, 0, -500]) cube([1000, 500, 1000]);
    }
} else if (part == 2) {
    // Render Left-Back Part: X < cut1_x, Y > 0
    difference() {
        union() {
            intersection() {
                outer_solid(wall_thickness);
                translate([-500, 0, -500]) cube([500 + cut1_x, 500, 1000]);
            }
            x_joint_block(cut1_x, "left");
            x_joint_pin(cut1_x);
            
            y_joint_block("back");
        }
        inner_hollow();
        exit_cutters();
        y_joint_hole();
        
        translate([cut1_x, -500, -500]) cube([500, 1000, 1000]);
        translate([-500, -500, -500]) cube([1000, 500, 1000]);
    }
} else if (part == 3) {
    // Render Middle Part: cut1_x < X < cut2_x
    difference() {
        union() {
            intersection() {
                outer_solid(wall_thickness);
                translate([cut1_x, -500, -500]) cube([cut2_x - cut1_x, 1000, 1000]);
            }
            x_joint_block(cut1_x, "right");
            x_joint_block(cut2_x, "left");
            x_joint_pin(cut2_x);
        }
        inner_hollow();
        exit_cutters();
        x_joint_hole(cut1_x);
        
        translate([-500, -500, -500]) cube([500 + cut1_x, 1000, 1000]);
        translate([cut2_x, -500, -500]) cube([500, 1000, 1000]);
    }
} else if (part == 4) {
    // Render Right Part: X > cut2_x
    difference() {
        union() {
            intersection() {
                outer_solid(wall_thickness);
                translate([cut2_x, -500, -500]) cube([500, 1000, 1000]);
            }
            x_joint_block(cut2_x, "right");
        }
        inner_hollow();
        exit_cutters();
        x_joint_hole(cut2_x);
        
        translate([-500, -500, -500]) cube([500 + cut2_x, 1000, 1000]);
    }
}