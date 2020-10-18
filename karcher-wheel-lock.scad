// This is Karsher wheel lock

$fn=75;

diameter=17.2;
wall_thick=1.2;
height=5; // smaler to print faster 62;
disk_thick=1; // smaller to print faster 3.8;
disk_diameter=28.5;
s_diameter=3; // small cylinder
s_thick=0.6; // small cylinder thickness
r_thick=0.7; // ridge thickness

futz=0.01;

All();

module All() {
  CenterCylinder();
  Cap();
  for (a=[80, -80]) {
    Clip(a);
  }
  little_angle=12;
  ExtraLine(rotate=little_angle, length=22);
  for (a=[0:2]) {
    ExtraLine(rotate=120*a - little_angle, length=12);
  }
  for (a=[0:2]) {
    LittleCylinder(120*a - little_angle);
    LittleCylinder(120*a + little_angle);
  }
}

module Cap() {
  difference() {
    cylinder(h=disk_thick+futz, r=disk_diameter/2);
    CapDivot();
  }
}

module CapDivot() {
  divot_size=7;
  translate([-disk_diameter+divot_size*2-disk_thick, 0, divot_size/2])
    rotate([0, 45, 0])
      cube(size=divot_size, center=true);
}

module CenterCylinder() {
  difference() {
    translate([0, 0, disk_thick])
      cylinder(h=height, r=diameter/2);
    translate([0, 0, disk_thick+futz])
      cylinder(h=height, r=diameter/2-wall_thick);
  }
}

module LittleCylinder(rotate) {
  r_embed=0.1; // how far to embed in cylinder

  rotate([0, 0, rotate]) {
    union() {
      translate([diameter/2+s_diameter/2, 0, disk_thick-futz]) {
        difference() {
          cylinder(h=height, r=s_diameter/2);
          cylinder(h=height+futz, r=s_diameter/2-   s_thick);
        }

      }
      translate([diameter/2+s_diameter-r_embed, -r_thick/2, disk_thick-futz])
        cube([r_thick, r_thick, height]);
    }
  }
}

// There's a few extra thick lines for support
module ExtraLine(rotate, length) {
  el_thick=disk_diameter/2 - diameter/2 - s_diameter; // extra line thickness

  rotate([0, 0, rotate]) {
      translate([diameter/2+s_diameter, -r_thick/2, futz])
        #cube([el_thick, r_thick, length]);    
  }
}

module Clip(rotate) {
  ClipSupport(rotate);
  union() {
    ClipBump(rotate);
    intersection() {
      ClipStraight(rotate);
      ClipSphere(rotate);
    }
  }
}

// The sphere trims the clip a bit.
module ClipSphere(rotate) {
  s_distance = 29;

  translate([-cos(rotate)*s_distance, -sin(rotate)*s_distance, 5.5])
    sphere(r=s_distance*1.5);
}

// The little lip at the end of the clip
module ClipBump(rotate) {
  cb_width = 5; // same as c_width
  cb_diameter = 2;
  rotate([0, 0, rotate])
    translate([disk_diameter/2, cb_width/2, 14])
      rotate([90, 0, 0])
        cylinder(h=cb_width, r=cb_diameter/2);
}

// The triangle to support the clip
module ClipSupport(rotate) {
  cs_width = 9;
  cs_thick = 1.5;
  rotate([0, 0, rotate])
    translate([disk_diameter/2, 0, 0])
      rotate([90, 0, 180])
        right_triangle(base=cs_width, height=cs_width, thick=cs_thick);
}

module right_triangle(base, height, thick) {
  linear_extrude(height=thick, center=true)
    polygon(points=[
      [0, 0],
      [base, 0],
      [0, height]],
      paths=[[0,1,2]]);
}

module ClipStraight(rotate) {
  c_length = 14; // Approx how tall it should be.
  c_radius = 70; // how far we sweep (smaller is more curved)
  c_sweep = atan2(c_length, c_radius);
  c_width = 5;
  c_thick = 1;
  c_tilt_back = 5; // degrees
  c_offset_up = sin(c_tilt_back)*disk_diameter/2;

  rotate([0, c_tilt_back, rotate])
    translate([-c_radius + disk_diameter/2 - c_thick, c_width/2, c_offset_up])
      rotate([90, 0, 0]) // flip up
        rotate_extrude(angle = c_sweep, convexity = 2) 
          translate([c_radius, 0, 0])
            square([c_thick, c_width]);
}

