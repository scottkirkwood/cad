// Renata's button to cover the new watch button
// Use the spiral (vase) print, the top won't be printed.
// Also used the 0.1 (fine) print setting.

diameter=6.9;
thick=1.0;
depth=4.3;
futz=0.01;

module All() {
  union() {
    Cylinder();
  }
}

module Plane() {
  translate([0, 0, 0])
    cylinder(h=thick/2, d=diameter+5*thick, $fn=80);
}

module Cylinder() {
    difference() {
      union() {
        cylinder(h=depth, d=diameter+thick, $fn=80);
        Plane();
      }
      translate([0, 0, -thick])
        cylinder(h=depth+thick*2,d=diameter, $fn=80);
    }
}

module CenterPunch() {
  cp_off_ground=2;
  cp_diameter=1.8;
  translate([0, 0, cp_off_ground])
    cylinder(h=depth, d=cp_diameter, $fn=80);
}

All();
