left = true;

module Spine(len, rot) {
  rotate(rot) {
    cylinder(h=len, d1=7, d2=4, $fn=50);
  }
  rotate(rot)
    translate([0, 0, len])
      rotate(rot/20)
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
    Spine(50, [180, -40, 40]);
    Spine(40, [160, -30, -25]);
    Spine(45, [180, 40, 5]);
    Spine(35, [195, 45, -45]);
  } else {
    Base("Right");
    Spine(30, [190, -45, 25]);
    Spine(40, [160, -30, -25]);
    Spine(50, [180, 40, 5]);
    Spine(45, [195, 45, -45]);
  }
}
