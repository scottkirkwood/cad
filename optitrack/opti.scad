left = false;

module Spine(len, rot) {
  rotate(rot) {
    cylinder(h=len, d1=7, d2=4, $fn=50);
  }
  rotate(rot)
    translate([0, 0, len])
      Sphere(15);
}

module Sphere(d) {
  difference() {
    sphere(d=15, $fn=60);
    translate([0, 0, 1])
      cylinder(h=d/2, d=d, $fn=50);
  }
}

module Base(txt) {
  diameter=15;
  rect = 45;
  thick = 3;

  difference() {
    translate([0, 0, diameter/8])
      cube([rect, rect, thick], center=true);
      Txt(txt);
  }
}

module SphereBase() {
  diameter=15;
  rect = 45;

  difference() {
    sphere(d=diameter, $fn=60);
    translate([0, 0, diameter/3])
      cube([rect, rect, diameter/2], center=true);
  }
}

module BaseWithCurve(txt) {
  diam=500;
  difference() {
    Base(txt);
    translate([0, 0, diam/2+2])
      rotate([90, 0, 90])
        cylinder(h=45, d=diam, center=true, $fa=1);
  }
}

module Txt(txt) {
  translate([12, 5, 1.5])
    rotate([180, 0, 90])
      linear_extrude(height=3)
        text(txt, size=6);
}

rotate([180, 0, 0]) {
  if (left) {
    Base("Left");
    translate([10, 10, 0]) {
      SphereBase();
      Spine(50, [180, -40, 40]);
    }
    translate([10, -10, 0]) {
      SphereBase();
      Spine(30, [160, -30, -25]);
    }
    translate([-10, 0, 0]) {
      SphereBase();
      Spine(40, [180, 40, 5]);
    }
  } else {
    Base("Right");
    translate([10, 10, 0]) {
      SphereBase();
      Spine(25, [220, 0, 25]);
    }
    translate([10, -10, 0]) {
      SphereBase();
      Spine(35, [160, -30, -25]);
    }
    translate([-10, 0, 0]) {
      SphereBase();
      Spine(45, [180, 40, 5]);
    }
  }
}
