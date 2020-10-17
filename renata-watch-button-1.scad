// Renata's button to cover watch button

width=6;
length=10;
depth=3;
border=1;
brim_w=2.5;
brim_h=1;
brim_thick=1;
futz=0.01;

All();

module All() {
  difference() {
    Brim();
    CenterPunch();
  }
  difference() {
    Box();
    CenterPunch();
  }
}

module Box() {
  difference() {
      RoundedBox([width, length, depth], r=0.25);
      translate([border/2, border/2, border/2])
          RoundedBox([width - border, length - border, depth + border], r=0.1);
  }
}

module Brim() {
  difference() {
    intersection() {
      translate([-brim_h/2, -brim_w/2, -brim_thick]) {
        RoundedBox([width+brim_h, length+brim_w, 2*brim_thick+futz], 0.25);
      }
      BrimClipSphere(radius=12, down=-.5);
    }
    BrimClipSphere(radius=15, down=.4);
  }
}

module BrimClipSphere(radius, down) {
  cs_up = -brim_thick/2 + down;
  translate([width/2, length/2, radius + cs_up])
    scale([1, 1.25, 1])
      sphere(r=radius, $fn=75);
}

module CenterPunch() {
  cp_diameter = 3;
  cp_height = depth;
  cp_off_ground = -.1;
  translate([width/2, length/2, cp_off_ground])
    cylinder(h=cp_height, r=cp_diameter/2, $fn=80);
}

module RoundedBox(s, r) {
  translate(s/2) { // de-center
    cube(s - [2*r, 0, 0], center=true);
    cube(s - [0, 2*r, 0], center=true);
    for (x = [r - s[0]/2, -r + s[0]/2],
         y = [r - s[1]/2, -r + s[1]/2]) {
      translate([x, y, 0])
        cylinder(r=r, h=s[2], center=true, $fn=40);
    }
  }
}