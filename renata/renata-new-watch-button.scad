// Renata's button to cover the new watch button
// Use the spiral (vase) print, the top won't be printed.
// Also used the 0.1 (fine) print setting.

diameter=6.5;
thick=1.0;
depth=4.3;
futz=0.01;

module All() {
  difference() {
    Cylinder();
    CenterPunch();
  }
}

module Cylinder() {
    difference() {
      cylinder(h=depth, d=diameter+thick, $fn=80);
      translate([0, 0, -thick])
        cylinder(h=depth,d=diameter, $fn=80);
    }
}

module CenterPunch() {
  cp_off_ground=2;
  cp_diameter=1.8;
  translate([0, 0, cp_off_ground])
    cylinder(h=depth, d=cp_diameter, $fn=80);
}

All();
