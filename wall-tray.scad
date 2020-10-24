// This is a tray to hold my modem a little higher
// For better reception
$fn=50;
width = 105;
height = width;
thick = 1.5;
support_height = height/2;
support_width = 10;
wall_support_thick = thick*2;
eps=0.01;

Tray();
for (x = [-1, 1]) {
  Arm(x);
}

module Tray() {
  difference() {
    cube([width, height, thick], center=true);

    for (x = [-1, 0, 1]) {
      TrayCutout(x);
    }
  }
}

// The TrayCutout is two ovals and a square put together
// Dir is -1, 0, 1 for the left oval, square, right oval.
module TrayCutout(dir) {
  circle_r = height/2;
  translate_x = 1/8;
  transform_x = 1;
  transform_y = 1/2;
  new_w = width*translate_x*2;
  if (dir == 0) {
    translate([0, circle_r, 0])
      cube([new_w, circle_r*transform_y, thick*2], center=true);
  } else {
    translate([dir*width*translate_x, height/2, 0])
      scale([transform_x, transform_y, 1])
        linear_extrude(height=thick*2, center=true)
          circle(d=circle_r);
  }
}

// The arms are -1, 1 for the left and right triangles
// They include the wall support in the back.
module Arm(dir) {
  difference() {
    Triangle(dir);
    TriangleCutout(dir);
  }
  difference() {
    WallSupport(dir);
    for (x = [-1, 1]) { 
      for (y = [0, 1]) {
        DrillHole(x, y);
      }
    }
  }
}

module Triangle(dir) {
  translate([dir*(width/2 - thick/2), height/2, 0])
    rotate([-90, 0, 90])
      linear_extrude(height=thick, center=true)
        polygon(points=[
          [0, 0],
          [0, -support_height],
          [-width, 0]],
          paths=[[0,1,2]]);
}

// TriangleCutout is a rotated ellipse and a block.
// Had to eyeball a lot of it.
module TriangleCutout(dir) {
  radius = 10;
  eyeball_x = 5;
  eyeball_height = 10.25;
  eyeball_angle = 25;
  translate([dir*width/2, -width/4+eyeball_x, height/8+eyeball_height])
    rotate([0, -90, 0])
      cube([width/4, height/4, thick*3], center=true);
  translate([dir*width/2, 10, height/3])
    rotate([eyeball_angle, 0, 0])
      scale([1, 4, 2])
        rotate([0, 90, 0])
          linear_extrude(height=3*thick, center=true)
            circle(r=radius);
}

module WallSupport(dir) {
  translate([dir*(width/2 - support_width/2), height/2,
      support_height/2 ])
    rotate([90, 0, 0])
      cube([support_width, support_height+thick, wall_support_thick], center=true);
}

module DrillHole(x, y) {
  radius=6/2;
  hole_thick=wall_support_thick+2*eps;
  translate([
      x * (width/2 - radius*2), 
      width/2+hole_thick/2, 
      height/2 - radius*2 - (y*height/6)])
    rotate([90, 0, 0])
      cylinder(h=hole_thick, r1=radius*2/3, r2=radius);
}
