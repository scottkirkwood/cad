height=71;
depth=110;
len=230;
thick=2;
cw=20;
module smooth_box() {
  cutout_d=65;
  cutout_thick=20;
  difference() {
    box(thick=0);
    scale([1, 2, 1])
      translate([0, 0, -cutout_thick*2])
        cylinder(h=cutout_thick, d=cutout_d);
    box(thick=thick);
  }
}

module box(thick) {
  cutout_d=65;
  cutout_thick=20;
  translate([0, 0, thick]) {
    difference() {
      cube([depth-thick, len-thick, height+thick], center=true);
      y_cylinder();
    }
  }
}

module y_cylinder() {
  cd=155;
  cyl_thick=6;
  difference() {
    translate([0, 0, -height/2+cd/3])
      rotate([90, 90, 0])
        cylinder(len+2, d=cd, center=true, $fn=200);
    translate([0, 0, -height/2+cd/3])
      rotate([90, 90, 0])
        cylinder(len+2, d=cd-cyl_thick, center=true, $fn=200);
  }
}

smooth_box();
