// Shaun the Sheep Toilet Paper Roll Tube - 120mm Custom Version
// Designed for toilet paper rolls with smaller core diameter (<= 40mm)
// Compatible with the Shaun the Sheep toilet paper holder model (Printables #914431 / MakerWorld).

// --- Parameters ---
$fn = 180;                  // Smooth circular facets

total_length       = 120.0; // Total length of tube (mm) - lengthened from 110mm
tube_od            = 40.0;  // Outer diameter of tube body (mm) - reduced from 42mm
flange_od          = 50.0;  // Outer diameter of front flange (mm)
flange_thickness   = 2.5;   // Thickness of front flange (mm)

head_hole_d        = 20.0;  // Diameter of front head peg socket (mm)
head_hole_depth    = 22.5;  // Depth of front head peg socket (mm)
head_hole_offset_y = -4.0;  // Eccentric center offset for head socket (mm)

tail_socket_d      = 39.0;  // Inner diameter for tail plug fit (mm) - matches tail
tail_socket_depth  = 25.0;  // Depth of tail plug socket (mm) - tail plug is ~19.3mm

// Bore style:
// "reinforced" = 39mm socket for tail (25mm depth), 36mm bore with 2.0mm wall below
// "uniform"    = 39mm bore throughout (0.5mm wall throughout)
bore_style         = "reinforced"; // ["reinforced", "uniform"]
body_bore_d        = 36.0;         // Inner diameter of reinforced body (mm)

module shaun_tube(style = bore_style) {
    difference() {
        union() {
            // Front Flange
            cylinder(d = flange_od, h = flange_thickness);
            
            // Main Tube Body
            cylinder(d = tube_od, h = total_length - 1.5);
            
            // Subtle lead-in bevel at top (tail end) for easier roll sliding
            translate([0, 0, total_length - 1.5])
                cylinder(d1 = tube_od, d2 = tube_od - 0.4, h = 1.5);
        }
        union() {
            // Head peg hole at base
            translate([0, head_hole_offset_y, -1])
                cylinder(d = head_hole_d, h = head_hole_depth + 1);
                
            if (style == "uniform") {
                // Uniform 39mm bore throughout
                translate([0, 0, head_hole_depth])
                    cylinder(d = tail_socket_d, h = total_length - head_hole_depth + 1);
            } else {
                // Reinforced body bore
                transition_start = total_length - tail_socket_depth - 3.0; // 92mm
                transition_end   = total_length - tail_socket_depth;       // 95mm
                
                // Lower body bore (36mm ID -> 2.0mm wall thickness)
                translate([0, 0, head_hole_depth])
                    cylinder(d = body_bore_d, h = transition_start - head_hole_depth);
                    
                // Smooth 45-degree internal taper (printable without support)
                translate([0, 0, transition_start])
                    cylinder(d1 = body_bore_d, d2 = tail_socket_d, h = transition_end - transition_start);
                    
                // Top tail socket (39mm ID -> fits 39mm tail plug)
                translate([0, 0, transition_end])
                    cylinder(d = tail_socket_d, h = total_length - transition_end + 1);
            }
        }
    }
}

// Render default
shaun_tube(bore_style);
