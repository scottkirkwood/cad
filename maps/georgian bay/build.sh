#!/usr/bin/env bash
set -euo pipefail

# =========================================================================
# Build Script for Georgian Bay Nautical Display & Lightbox
# 1. Runs Go unit tests
# 2. Generates Master & Layer SVGs and OpenSCAD model using Go
# 3. Compiles 3D STL models using OpenSCAD
# =========================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

echo "========================================================"
echo "Step 1: Running Go Unit Tests..."
echo "========================================================"
go test -v ./...
echo "All Go unit tests passed!"

echo ""
echo "========================================================"
echo "Step 2: Generating Vector SVGs & CAD Model..."
echo "========================================================"
go run .

echo ""
echo "========================================================"
echo "Step 2b: Masking Out Water in Satellite Image..."
echo "========================================================"
if [ -f "scripts/mask_satellite.py" ]; then
    python3 scripts/mask_satellite.py
fi

echo ""
echo "========================================================"
echo "Step 3: Compiling OpenSCAD 3D STL Models..."
echo "========================================================"
mkdir -p output

if command -v openscad >/dev/null 2>&1; then
    echo "  -> Compiling water base plate (georgian_bay_water_base.stl)..."
    openscad -o output/georgian_bay_water_base.stl -D 'mode="water_base"' georgian_bay_display.scad

    echo "  -> Compiling navigation spar buoys (georgian_bay_buoys.stl)..."
    openscad -o output/georgian_bay_buoys.stl -D 'mode="buoys"' georgian_bay_display.scad

    echo "  -> Compiling mainland relief (georgian_bay_mainland.stl)..."
    openscad -o output/georgian_bay_mainland.stl -D 'mode="mainland"' georgian_bay_display.scad

    echo "  -> Compiling archipelago islands (georgian_bay_islands.stl)..."
    openscad -o output/georgian_bay_islands.stl -D 'mode="islands"' georgian_bay_display.scad

    echo "  -> Compiling lightbox rear housing (georgian_bay_lightbox_box.stl)..."
    openscad -o output/georgian_bay_lightbox_box.stl -D 'mode="lightbox_box"' georgian_bay_display.scad

    # Check if --all or FULL_BUILD=1 was requested for single-piece boolean union faceplate
    if [[ "${1:-}" == "--all" ]] || [[ "${FULL_BUILD:-0}" == "1" ]]; then
        echo "  -> Compiling single-piece backlit faceplate (georgian_bay_backlit_faceplate.stl) [takes ~2 mins]..."
        openscad -o output/georgian_bay_backlit_faceplate.stl -D 'mode="backlit_faceplate"' georgian_bay_display.scad
    else
        echo "  -> Note: Skipping single-piece faceplate boolean union by default (pass --all to build)."
        echo "     (Component STLs above are already ready for multi-color printing in Bambu Studio)."
    fi

    echo "OpenSCAD compilation complete!"
else
    echo "Notice: OpenSCAD not found in PATH, skipping STL export."
fi

echo ""
echo "========================================================"
echo "Build pipeline completed successfully!"
echo "========================================================"
