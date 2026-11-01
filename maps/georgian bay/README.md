# Georgian Bay Nautical Display & Lightbox

A 3D printable, backlit nautical chart and lightbox display covering the southeastern **Thirty Thousand Islands of Georgian Bay**, Ontario, spanning from **Longuissa Bay** in the north down to **South Bay Cove** in the south.

![Georgian Bay Display Preview](georgian_bay_display_preview.png)

![Georgian Bay Satellite Preview](georgian_bay_satellite_preview.png)

---

## 1. Data Sources & Attributions

This project integrates geographic, hydrographic, and satellite data from the following public and open sources:

1. **OpenStreetMap (OSM)**:
   * **License**: Open Database License (ODbL) © OpenStreetMap contributors.
   * **Usage**: Shoreline vector geometry, 414 archipelago islands (`place=island`, `place=islet`), inland lakes on Beausoleil Island (Fairy Lake, Goblin Lake), and place names.
   * **Location in Project**: Raw XML tiles stored in [`data/osm/`](data/osm/) (`tile_sw.osm`, `tile_nw.osm`, `tile_se.osm`, `tile_ne.osm`).

2. **Canadian Hydrographic Service (CHS) / Fisheries and Oceans Canada**:
   * **Sources**:
     * *Sailing Directions CEN 306 — Georgian Bay* ([`data/chs_cen306.pdf`](data/chs_cen306.pdf))
     * *Canadian Coast Guard List of Lights, Buoys and Fog Signals (Central & Arctic)* ([`data/list_of_lights.pdf`](data/list_of_lights.pdf))
     * *CHS Chart No. 1: Symbols, Abbreviations and Terms used on Canadian Nautical Charts*
   * **Usage**: Authentic IHO/CHS spar buoy topmark symbology (tilted ~20° starboard conical vs port cylindrical cans), buoy coordinates for the inside navigation channel, and verified anchorage symbols at Brown Bay, Longuissa Bay, and Bone Island Basin.

3. **Natural Resources Canada (NRCan) / CanVec**:
   * **Usage**: Elevation benchmarks and bedrock survey reference for Canadian Shield granite archipelago islands.

4. **Esri World Imagery (ArcGIS Online MapServer REST API)**:
   * **Service**: `https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/export`
   * **Usage**: Calibrated high-resolution space/aerial photograph strictly projected to bounds `[-79.9140, 44.8225, -79.7660, 44.9715]` matching the vector coordinates.
   * **Location in Project**: [`satellite_georgian_bay.png`](satellite_georgian_bay.png).

---

## 2. Project Architecture & Build System

The map pipeline is written entirely in **Go** using only standard library packages (`encoding/xml`, `math`, `os`, `path/filepath`, `strings`, `fmt`), ensuring zero external dependencies and fast compilation.

### Running the Build Pipeline

Execute the master build script:
```bash
./build.sh
```

To also compile the single-piece boolean union faceplate (which performs 3D CGAL Nef polyhedron intersection over 50,000 facets and takes ~2 minutes):
```bash
./build.sh --all
```

### Running Unit Tests

Run the Go unit test suite:
```bash
go test -v ./...
```
Tests cover:
* Coordinate projection, aspect ratios, and ISO scaling (`geo_test.go`)
* Round-trip conversions between lon/lat and SVG millimeters (`geo_test.go`)
* Ramer-Douglas-Peucker line simplification (`geo_test.go`)
* Polygon centroid and principal major axis rotation angle computation (`geo_test.go`)
* OSM XML element extraction and polygon assembly (`osm_test.go`)
* IHO/CHS spar buoy symbology, anchors, 16-facet compass rose, and title plaque generation (`symbols_test.go`)

---

## 3. Directory & File Layout

| File / Folder | Purpose |
| :--- | :--- |
| [`build.sh`](build.sh) | Automated script: runs unit tests, executes Go generator, renders PNGs, and compiles STLs |
| [`main.go`](main.go) | Master pipeline orchestrator and SVG/SCAD generator |
| [`geo.go`](geo.go) | Projection math, RDP simplification, and polygon orientation calculations |
| [`symbols.go`](symbols.go) | IHO/CHS spar buoys, anchors, 16-facet compass rose, and title block generators |
| [`osm.go`](osm.go) | Pure Go XML parser for OpenStreetMap tiles and shoreline extractor |
| [`georgian_bay_display.svg`](georgian_bay_display.svg) | Master vector display with native Inkscape layers, full-page bounds, and visible satellite layer |
| [`georgian_bay_satellite_display.svg`](georgian_bay_satellite_display.svg) | Photographic satellite edition with translucent vector overlays |
| [`georgian_bay_display.scad`](georgian_bay_display.scad) | Parametric OpenSCAD 3D CAD model |
| [`layers/`](layers/) | Full-page ($163.8 \times 228.6\text{ mm}$) component SVGs (`00_satellite.svg` to `04_buoys.svg`) |
| [`output/`](output/) | Pre-rendered ready-to-print 3D STL models |
| [`data/`](data/) | Raw reference PDFs, texts, and OSM XML tiles |

---

## 4. 3D Printing & Lightbox Fabrication (Bambu Lab H2C / AMS)

* **Dimensions**: $163.8\text{ mm} \times 228.6\text{ mm}$ (standard 9-inch lightbox format matching Bambu Lab specs).
* **Multi-Color / AMS Mode**:
  1. Open Bambu Studio and import `output/georgian_bay_water_base.stl`, `output/georgian_bay_mainland.stl`, `output/georgian_bay_islands.stl`, and `output/georgian_bay_buoys.stl` together as a single multi-part object.
  2. Assign Filaments:
     * Water base: Deep Nautical Blue / Cyan
     * Mainland: Muted Slate Charcoal
     * Islands: Canadian Shield Granite Beige / Brown
     * Spar Buoys: Crimson Red / Emerald Green
* **Backlit Lithophane Mode**:
  * Print `output/georgian_bay_backlit_faceplate.stl` in translucent white PLA (e.g., Bambu Jade White).
  * Layer thicknesses create natural light contrast: Water ($1.0\text{ mm}$, high transmission), Mainland ($2.2\text{ mm}$), Islands ($2.6\text{ mm}$), Buoys/Frame ($3.2\text{ mm}$ / $7.0\text{ mm}$).
* **Rear Enclosure**:
  * Print `output/georgian_bay_lightbox_box.stl` in opaque black PLA/PETG. Features an integrated $9\text{ mm}$ power cord grommet and keyhole wall mount.
