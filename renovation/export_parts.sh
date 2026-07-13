#!/bin/bash

# Exit on any error
set -e

echo "Exporting vanity vent parts to STL (4-part split for CR-6 SE)..."

# Part 1: Left-Front Part
echo "Exporting Part 1 (Left-Front)..."
openscad -D "part=1" -o vanity_vent_part1.stl vanity-vent.scad

# Part 2: Left-Back Part
echo "Exporting Part 2 (Left-Back)..."
openscad -D "part=2" -o vanity_vent_part2.stl vanity-vent.scad

# Part 3: Middle Part
echo "Exporting Part 3 (Middle)..."
openscad -D "part=3" -o vanity_vent_part3.stl vanity-vent.scad

# Part 4: Right Part
echo "Exporting Part 4 (Right)..."
openscad -D "part=4" -o vanity_vent_part4.stl vanity-vent.scad

echo "Export complete! Generated files:"
ls -lh vanity_vent_part*.stl
