difference() {
  import("Blank_Plug.stl", convexity=3);

  translate([-34, -43, 28])
    rotate([90, 0, 0])
      linear_extrude(height=5, center=false, convexity=10)
        text("Rena", 20, font="Roboto:style=Black");
}
