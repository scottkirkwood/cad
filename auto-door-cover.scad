// Cosmetic cover for my automatic door
length = 18*25.4;
height = 33;
thick = 5.8;
eps = 0.01;
num_cuts = 7;
rlb = 1; // 0=right, 1=left, 2=both
flip = 1; // I print flipped so the thicker base at bottom

rotate([0, 180*flip, 0]) {
  if (rlb == 2) {
    Piece(true);
    Piece(false);
  } else {
    Piece(rlb ? true: false);
  }
}

module Piece(left) {
  difference() {
    translate([0, 0, height/2])
      cube([length, thick, height], center=true);
    Taper();
    BottomBlock();
    CutoutBack();
    CutoutForBolts();
    Sawtooth(num_cuts, height, thick, left);
    CutRest(num_cuts, height, thick, left);
  }
}

module Taper() {
  ang = 90-88;
  offset = (height)*sin(ang);
  rotate([ang, 0, 0])
    translate([0, -thick+offset, height/2])
      cube([length+eps, thick, height+eps], center=true);
}

module BottomBlock() {
  bb_height = 15;
  bottom_taper = 1.3;
  lip = 2;
  translate([0, -thick+bottom_taper, height/2-bb_height])
    cube([length+eps, thick, height+eps], center=true);
  translate([0, -thick+bottom_taper+1, height/2-bb_height-lip])
    cube([length+eps, thick, height+eps], center=true);
}

module CutoutBack() {
  edge = 5;
  depth = 5;
  translate([0, thick/2, height/2])
    cube([length-edge, depth, height-edge], center=true);
}

module Sawtooth(num, total_height, thickness, reverse) {
  inset = total_height / num;
  bottom = -total_height/2 + inset/2;
  play = 0.1;
  flip = reverse ? inset: 0;
  tonum = reverse ? num-2 : num-1;
  rotate([0, 0, 0])
    translate([inset/2 - eps, 0, flip+total_height/2])
      rotate([90, 0, 0])
        for (y = [0: 2: tonum]) {
          translate([0, bottom + inset * y, 0])
            cube([inset, inset+2*eps+play, thickness+2*eps], center=true);
        }
}

module CutRest(num, total_height, thick, reverse) {
  inset = total_height/num;
  offset = reverse ? -length/4-eps: length/4+inset-2*eps;
  translate([offset, 0, height/2])
      cube([length/2, thick+2*eps, height+8*eps], center=true);
}

module CutoutForBolts() {
  from_edge_r = 52; // to center of bolt
  from_edge_l = 57;

  Bolt(1, from_edge_r);
  Bolt(-1, from_edge_l);
}

module Bolt(dir, from_edge) {
  bolt_width = 15; // really 11mm + some extra
  bolt_height = 10;

  translate([dir*(length/2-bolt_width/2-from_edge), -thick/4, -eps])
    cube([bolt_width, thick+eps, bolt_height]);
}
