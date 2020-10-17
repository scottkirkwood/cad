// Renata's button to cover watch button

width=6;
length=10;
depth=2;
border=1;
brim=1.5;
brim_thick=0.5;
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
      translate([0, 0, brim_thick])
        RoundedBox([width, length, depth], 0.25);
      translate([border/2, border/2, depth+brim_thick-border-futz])
          RoundedBox([width - border, length - border, depth], 0.1);
  }
}

module Brim() {
  cs_r = 20;
  brim_up = 0.2;
  difference() {
    intersection() {
      translate([-brim/2, -brim/2, brim_up + futz*2]) {
        RoundedBox([width+brim, length+brim, brim_thick+brim_up+futz], 0.25);
      }
      BrimClipSphere(cs_r);
    }
    #BrimClipInnerSphere(cs_r, brim_up);
  }
}

module BrimClipSphere(radius) {
  cs_up = -brim_thick/2;
  translate([width/2, length/2, radius + cs_up])
    scale([1, length/width, 1])
      sphere(r=radius, $fn=75);
}

module BrimClipInnerSphere(radius, brim_up) {
  cs_up = brim_up - brim_thick/2;
  translate([width/2, length/2, radius + cs_up])
    scale([1, length/width, 1])
      sphere(r=radius - brim_thick + brim_up, $fn=75);
}

module CenterPunch() {
  cp_diameter = 2;
  cp_height = 2;
  cp_off_ground = 0.1;
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