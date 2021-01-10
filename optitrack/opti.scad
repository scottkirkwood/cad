
module Spine(len, rot) {
  rotate(rot) {
    cylinder(h=len, d1=7, d2=4);
    translate([0, 0, len])
      cylinder(h=2, d=15);
  }
}

module Base() {
  diameter=15;
  rect = 45;
  thick = 3;

  translate([0, 0, diameter/8])
    cube([rect, rect, thick], center=true);
  difference() {
    sphere(d=diameter);
    translate([0, 0, diameter/3])
      cube([rect, rect, diameter/2], center=true);
  }
}

module BaseWithCurve() {
  diam=500;
  difference() {
    Base();
    translate([0, 0, diam/2+2])
      rotate([90, 0, 90])
        cylinder(h=45, d=diam, center=true, $fa=1);
  }
}

rotate([180, 0, 0]) {
  BaseWithCurve();
  Spine(40, [190, -45, 25]);
  Spine(45, [160, -30, -25]);
  Spine(50, [180, 40, 5]);
}
