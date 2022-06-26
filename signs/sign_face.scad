// Sign front-face generator V3 - bigclivedotcom
// All variables must match the sign body sizes
letter = "A"; // Sign character to make
style = "Arial"; // See "Help" and "Font List"
size = 50; // Size of character
$fn=100; // Curve facets - higher is smoother
walls = 2; // Side wall thickness
face = 1; // Face thickness
fit = 0.5; // Slight shrink of face for easier fitting

// Don't change variables below here
sized=size-(2*walls);
linear_extrude(height=face)
minkowski() {
    text(letter,sized,style);
    circle((walls/2)-fit/2);
}
