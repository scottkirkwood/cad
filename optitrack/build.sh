#!/bin/sh
echo "Outputting opti-left.stl"
#openscad -o opti-left.stl -D left=true opti.scad
echo "Outputting opti-right.stl"
#openscad -o opti-right.stl -D left=false opti.scad
echo "Slicing opt-left-petg.gcode"
config='PrusaSlicer_petg_config_bundle.ini'
prusa-slicer --load "$config" --output opti-left-petg.gcode --gcode opti-left.stl
echo "Slicing opt-right-petg.gcode"
prusa-slicer --load "$config" --output opti-right-petg.gcode --gcode opti-right.stl
