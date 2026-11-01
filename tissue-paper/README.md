# Parametric Kleenex Box Cover with Mathematical Textures & Multi-Color Support

A 3D printable cover designed to slip over standard rectangular cardboard tissue boxes (open at the bottom).

## Features

1. **Preserved Perfect Fit**:
   - Internal cavity dimensions remain exactly **108 mm (W) x 228 mm (L) x 70.4 mm (H)** with an open bottom, ensuring it slips over standard Kleenex boxes smoothly.
   - Any added wave amplitude or extra wall thickness expands outward, preventing binding.

2. **Mathematical Wall Designs (`pattern_type`)**:
   - `wave_vertical` *(default)*: Classical vertical sinusoidal fluting around the perimeter ($x(u) = A \cdot \frac{1 - \cos(2\pi \cdot n \cdot u)}{2}$), with smooth corner fillets.
   - `wave_horizontal`: Horizontal ripple swells undulating along the height ($z$).
   - `none`: Clean smooth walls matching the original box.
   - Full parametric control over wave amplitude (`wave_amp`), wave counts (`waves_len`, `waves_depth`), and wavelength (`wave_wavelength_z`).

3. **Multi-Color Printing for Bambu Lab Printers (`color_mode`)**:
   - `cap` *(recommended)*: Splits the model at the top layer boundary ($Z = \text{top\_thick}$).
     - **Huge advantage for Bambu Studio / AMS**: Requires **only 1 filament swap** during the entire print! The printer prints the top face in Color 1, switches once to Color 2, and prints the remaining 98% of the height with zero purging or waste.
   - `inlay`: Vertical side walls extend all the way down to form an exterior rim around the top face, with the top face sitting as an inlay inside.
     - Exterior sides are 100% Color 2 from bottom to top rim.
   - `unified`: Combines into a single solid for single-filament printing.

## Quick Start / Build Script

Run the build script to run the unit test suite and generate all files:
```bash
./build.sh
```

This generates:
- `tissue-paper-dual.3mf`: Multi-part 3MF file ready for Bambu Studio.
- `tissue-paper-top.stl`: Top dispenser plate.
- `tissue-paper-sides.stl`: Vertical walls.
- `tissue-paper-single.stl`: Single solid model.
- `preview_perspective.png` & `preview_top_face.png`: High-resolution rendered previews.

## Printing on Bambu Lab (Bambu Studio / OrcaSlicer)

### Method 1: Using the `.3mf` (Fastest)
1. Drag and drop `tissue-paper-dual.3mf` directly into Bambu Studio.
2. In the left panel under **Process -> Objects**, expand the object.
3. Select `Top` and assign your preferred filament (e.g. Filament 1).
4. Select `Sides` and assign your side filament (e.g. Filament 2).
5. Slice and print!

### Method 2: Using the separate `.stl` files
1. Drag both `tissue-paper-top.stl` and `tissue-paper-sides.stl` into Bambu Studio at the same time.
2. When prompted: *"Load these files as a single object with multiple parts?"*, click **Yes**.
3. Assign filament colors to `Top` and `Sides` under the Objects list.
