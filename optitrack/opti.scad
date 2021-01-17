
module Spine(len, rot) {
  rotate(rot) {
    cylinder(h=len, d1=7, d2=4);
  }
  rotate(rot)
    translate([0, 0, len-1])
      rotate([0, rot[1]/1.5, -rot[2]/2])
        cylinder(h=2, d=15);
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

module BaseWithCurve(txt) {
  diam=500;
  difference() {
    Base();
    Txt(txt);
    translate([0, 0, diam/2+2])
      rotate([90, 0, 90])
        cylinder(h=45, d=diam, center=true, $fa=1);
  }
}

module Txt(txt) {
  translate([12, 6, 1])
    rotate([180, 0, 90])
      linear_extrude(height=2)
        text(txt, size=5);
}

rotate([180, 0, 0]) {
  if (false) {
    BaseWithCurve("Left");
    Spine(50, [190, -45, 50]);
    Spine(40, [160, -30, -25]);
    Spine(45, [180, 40, 5]);
    Spine(38, [195, 45, -45]);
  } else {
    BaseWithCurve("Right");
    Spine(40, [190, -45, 25]);
    Spine(45, [160, -30, -25]);
    Spine(50, [180, 40, 5]);
    Spine(41, [195, 45, -45]);
  }
}
