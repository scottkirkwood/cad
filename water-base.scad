include <MCAD/boxes.scad>

difference() { 
  cube([150, 150 , 25], center=true);
  translate([0, 0, 14])
    roundedBox([159, 150 - 6*2, 20],  radius=10);
}