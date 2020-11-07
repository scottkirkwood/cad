// This is the backing plate for the automatic door It is just to bring the
// toothed piece in line with the edges of the door

length = 620;
length3 = length / 3;
height = 21;
thick = 4;
eps = 0.01;


//translate([0, height*1.5, 0])
//  Piece(false, true);
//translate([0, 0, 0])
//  Piece(true, true);
translate([0, -height*1.5, 0])
  Piece(true, false);

module Piece(left, right) {
  difference() {
    cube([length3, height, thick], center=true);
    if (right) {
      translate([length3/2, 0, 0])
        #Sawtooth(4, height, thick, false);
    }
    if (left) {
      translate([-length3/2, 0, 0])
        #Sawtooth(4, height, thick, true);
    }
  }
}

module Sawtooth(num, total_height, thickness, reverse) {
  inset = total_height / num;
  bottom = -total_height/2 + inset/2;
  flip = reverse ? 1: 0;
  right = reverse ? 1: -1;
  rotate([180*flip, 0, 0])
    translate([right*(inset/2 - eps), 0, 0])
      for (y = [0: 2: num-1]) {
        translate([0, bottom + inset * y, 0])
          cube([inset, inset+2*eps, thick+2*eps], center=true);
      }
}
