#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
SCAD_FILE="$DIR/tissue-paper.scad"

echo "=== Running Tests ==="
python3 "$DIR/test_models.py"

echo ""
echo "=== Building Production 3D Models ==="

# 1. Export STLs
echo "[1/4] Exporting Top Part (tissue-paper-top.stl)..."
openscad -o "$DIR/tissue-paper-top.stl" -D 'part="top"' "$SCAD_FILE"

echo "[2/4] Exporting Sides Part (tissue-paper-sides.stl)..."
openscad -o "$DIR/tissue-paper-sides.stl" -D 'part="sides"' "$SCAD_FILE"

echo "[3/4] Exporting Single Solid (tissue-paper-single.stl)..."
openscad -o "$DIR/tissue-paper-single.stl" -D 'part="all"' "$SCAD_FILE"

# 2. Create Multi-Part 3MF for Bambu Studio
echo "[4/4] Generating Multi-Part 3MF (tissue-paper-dual.3mf)..."
python3 "$DIR/export_3mf.py" "$DIR/tissue-paper-dual.3mf" \
    "Top" "$DIR/tissue-paper-top.stl" \
    "Sides" "$DIR/tissue-paper-sides.stl"

# 3. Generate High-Res Previews
echo "Rendering Preview Images..."
openscad -o "$DIR/preview_perspective.png" \
    --render=true \
    --camera=0,0,36,55,0,25,500 \
    --colorscheme=Tomorrow \
    --imgsize=1000,750 \
    "$SCAD_FILE"

openscad -o "$DIR/preview_top_face.png" \
    --render=true \
    --camera=0,0,36,135,0,25,500 \
    --colorscheme=Tomorrow \
    --imgsize=1000,750 \
    "$SCAD_FILE"

echo "=== Build Complete! ==="
ls -lh "$DIR"/tissue-paper* "$DIR"/preview*.png
