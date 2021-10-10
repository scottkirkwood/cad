// Renata's button to cover the new watch button

diameter=6.8;
thick=0.9;
depth=4.3;
futz=0.01;

module All() {
  difference() {
    Cylinder();
    #CenterPunch();
  }
}

module Cylinder() {
    difference() {
      cylinder(h=depth, r=(diameter+thick)/2, $fn=80);
      translate([0, 0, -thick])
        cylinder(h=depth,r=diameter/2, $fn=80);
    }
}

module CenterPunch() {
  cp_off_ground=2;
  cp_diameter=1.8;
  translate([0, 0, cp_off_ground])
    cylinder(h=depth, r=cp_diameter/2, $fn=80);
}

All();
