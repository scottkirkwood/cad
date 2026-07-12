// --- PARAMETERS (All measurements in millimeters) ---

$fn = 60; // Smoothness for rounded corners/edges
inch = 25.4;

// Floor Opening Dimensions (Inside fitting)
floor_length = 10.25 * inch; 
floor_width  = 4.125 * inch;
floor_depth  = 20; // How deep the lip inserts into the floor

// Vanity / Toe Kick Dimensions
vanity_clearance = 3.5 * inch; // Available height under the vanity floor
kick_plate_depth = 21 * inch;  // Total distance from back wall to front kick plate
wall_thickness   = 2.0;        // Thickness of the printed duct walls

// Front Vent Dimensions (Exiting the kick plate)
front_width  = 10.0 * inch;
front_height = 2.5 * inch; // Keep this under vanity_clearance

/* [Hidden] */
// Internal calculation offsets to maintain consistent wall thickness
eps = 0.02;

module solid_duct() {
    // 1. The floor insertion collar
    translate([-floor_width/2, -floor_length/2, -floor_depth])
        cube([floor_width, floor_length, floor_depth + eps]);
    
    // 2. The transition boot (Hulling the floor profile to the start of the front channel)
    hull() {
        translate([-floor_width/2, -floor_length/2, 0])
            cube([floor_width, floor_length, eps]);
        
        // Transition to a forward-facing profile slightly shifted toward the front
        translate([-front_width/2, -floor_length/2 + 10, vanity_clearance - front_height])
            cube([front_width, eps, front_height]);
    }
    
    // 3. The straight run to the toe kick
    // Computes the remaining length needed to reach the front plate
    remain_length = kick_plate_depth - (floor_length/2); 
    translate([-front_width/2, -floor_length/2 + 10, vanity_clearance - front_height])
        cube([front_width, remain_length, front_height]);
}

module hollow_duct() {
    difference() {
        // Outer shell
        minkowski() {
            solid_duct();
            // Gives us rounded outer edges and creates the wall thickness
            sphere(r = wall_thickness);
        }
        
        // Core removal
        solid_duct();
        
        // Clean up the open ends (Minkowski caps the ends, so we slice them open)
        // Floor opening clear
        translate([-(floor_width+5), -(floor_length+5), -(floor_depth + wall_thickness + 1)])
            cube([floor_width*2, floor_length*2, wall_thickness + 1]);
            
        // Front opening clear
        translate([-(front_width+5), kick_plate_depth - (floor_length/2) - 1, vanity_clearance - front_height - 5])
            cube([front_width*2, wall_thickness * 3, front_height * 2]);
    }
}

// Render the final hollowed model
hollow_duct();