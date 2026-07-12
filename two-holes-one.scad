// Cosmetic cover for my automatic door
$fn = 32;
length = 95;
separation = 60;
height = 20;
large_hole_radius = 7.6/2;
small_hole_radius = 4.25/2;
thick = 4;
eps = 0.01;
clearance = 0.1;

module Hole() {
  h = -2;
  translate([0, h, -eps]) {
    cylinder(h=thick+eps*2, r=large_hole_radius+clearance);
    translate([0, large_hole_radius+small_hole_radius, 0]) {
      cylinder(h=thick+eps*2, r=small_hole_radius+clearance);
      cylinder(h=thick/3, r=large_hole_radius);
    }
  }
  r2 = small_hole_radius*2;
  translate([-small_hole_radius+eps, h+1.9, -eps])
    cube([r2-eps, r2-eps, thick+eps*2]);
}

module Plate() {
  translate([-length/2, -height/2, 0])
    cube([length, height, thick]);
}

module Pin(pos) {
  translate(pos) {
    cylinder(h=thick*2+eps*2, r=small_hole_radius-clearance);
    translate([0, 0, thick*2])
      sphere(r=large_hole_radius);
  }
}

difference() {
  Plate();
  Hole();
}

Pin([-separation/2, -height/6, thick]);
Pin([separation/2, -height/6, thick]);

