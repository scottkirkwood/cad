// Create a parametric box with lid
$fn = 50;
// Width
width = 100;
// Length
length = 50;
// Height
height = 40;
// Lid
has_lid = true;
// Has Drill Holes
has_drill_holes = true;
// Additional parameters
// Radius of corners, higher is more rounded
corner_radius = 5;
// Size of the screw hole
hole_diameter = 3;
// Thickness of each wall
wall_thickness = 4;
// Support post diameter
post_diameter = 10;
// How thick the lid should be
lid_thickness = 2;
// How much lip to have on the lid inset
lid_lip = 2;
// Lid is a little smaller than the opening
lid_tolerance = 0.8;

module posts(x, y, z, h, r) {
  translate([x, y, z]) {
    cylinder(r = r, h = h);
  }
  translate([-x, y, z]) {
    cylinder(r = r, h = h);
  }
   translate([-x, -y, z]) {
    cylinder(r = r, h = h);
  }
  translate([x, -y, z]) {
    cylinder(r = r, h = h);
  }
}

module filled_box(x, y, z, h) {
  hull() {
    posts(x, y, z, h, corner_radius);
  }
}

module hollowed_box() {
  difference() {
    // Box
    filled_box(
      x=width/2 - corner_radius,
      y=length/2 - corner_radius,
      z=0,
      h=height);
    // hollow
    filled_box(
      x=width/2 - corner_radius - wall_thickness,
      y=length/2 - corner_radius - wall_thickness,
      z=wall_thickness,
      h=height);
    // lip lid
    filled_box(
      x=width/2 - corner_radius - lid_lip,
      y=length/2 - corner_radius - lid_lip,
      z=height - lid_thickness,
      h=lid_thickness + 1);
  }
}

module support_posts() {
  difference() {
    posts(
      x=width/2 - wall_thickness/2 - post_diameter/2,
      y=length/2 - wall_thickness/2 - post_diameter/2,
      z=wall_thickness - 0.5,
      h=height - wall_thickness - lid_thickness + 0.5,
      r=post_diameter/2
    );
    // Holes
    posts(
      x=width/2 - wall_thickness/2 - post_diameter/2,
      y=length/2 - wall_thickness/2 - post_diameter/2,
      z=wall_thickness,
      h=height - wall_thickness - lid_thickness + 0.5,
      r=hole_diameter/2
    );
  }
}

module lid() {
  difference() {
    filled_box(
      x=width/2 - corner_radius - wall_thickness/2 - lid_tolerance,
      y=length/2 - corner_radius - wall_thickness/2 - lid_tolerance,
      z=height - lid_thickness,
      h=lid_thickness);
    if (has_drill_holes) {
      posts(
        x=width/2 - wall_thickness/2 - post_diameter/2,
        y=length/2 - wall_thickness/2 - post_diameter/2,
        z=height - lid_thickness,
        h=height - wall_thickness - lid_thickness + 0.5,
        r=hole_diameter/2 + 0.5
      );
    }
  }
}

hollowed_box();
if (has_drill_holes) {
  support_posts();
}
if (has_lid) {
  lid();
}