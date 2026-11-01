package main

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

func main() {
	fmt.Println("Georgian Bay 3D Nautical Display Generator (Go Edition)")

	cfg := NewMapConfig(
		44.8225, // MinLat
		44.9715, // MaxLat
		-79.9140, // MinLon
		-79.7660, // MaxLon (Right edge where South Bay Cove ends!)
		163.8,   // TargetWidth (mm)
		228.6,   // TargetHeight (mm)
		3.0,     // MarginX (mm)
		3.0,     // MarginY (mm)
	)

	fmt.Printf("Loading OSM data from data/osm/*.osm ...\n")
	osmData, err := LoadOSMData("data/osm/*.osm")
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error loading OSM data: %v\n", err)
		os.Exit(1)
	}

	islands, inlandLakes := osmData.ExtractIslands(cfg)
	fmt.Printf("Extracted %d crisp archipelago islands.\n", len(islands))

	mainlandPoly := osmData.ExtractMainlandPoly(cfg)
	fmt.Printf("Extracted mainland shoreline polygon (%d vertices).\n", len(mainlandPoly))

	// Classify inland lakes: mainland lakes vs island lakes
	var mainlandLakes [][]Point2D
	var islandLakes [][]Point2D
	for _, lPts := range inlandLakes {
		if len(lPts) > 0 && PointInPolygon(lPts[0], mainlandPoly) {
			mainlandLakes = append(mainlandLakes, lPts)
		} else {
			islandLakes = append(islandLakes, lPts)
		}
	}
	fmt.Printf("Extracted %d inland water bodies (%d on mainland, %d on islands).\n",
		len(inlandLakes), len(mainlandLakes), len(islandLakes))

	// Build mainland compound path with all mainland lakes carved via evenodd
	var mainlandD strings.Builder
	mainlandD.WriteString(PointsToPath(mainlandPoly, true))
	for _, lPts := range mainlandLakes {
		mainlandD.WriteString(" ")
		mainlandD.WriteString(PointsToPath(lPts, true))
	}
	mainlandCompoundD := mainlandD.String()

	// Associate island lakes with their parent island (e.g. Goblin Lake & Fairy Lake on Beausoleil)
	islandLakesMap := make(map[string][][]Point2D)
	for _, lPts := range islandLakes {
		if len(lPts) == 0 {
			continue
		}
		matched := false
		for _, isl := range islands {
			if PointInPolygon(lPts[0], isl.Pts) {
				islandLakesMap[isl.ID] = append(islandLakesMap[isl.ID], lPts)
				matched = true
				break
			}
		}
		if !matched {
			islandLakesMap["unassigned"] = append(islandLakesMap["unassigned"], lPts)
		}
	}

	// Buoys data
	rawBuoys := []struct {
		Type string
		Lon  float64
		Lat  float64
	}{
		// Starboard (Red) Spars
		{"red", -79.8235, 44.8580},
		{"red", -79.8240, 44.8620},
		{"red", -79.8222, 44.8655},
		{"red", -79.8800, 44.9220}, // Penetang Rock
		{"red", -79.8850, 44.9340},
		{"red", -79.8860, 44.9410},
		{"red", -79.8895, 44.9610}, // Longuissa Point
		{"red", -79.7900, 44.8730}, // South Bay
		{"red", -79.8100, 44.8730}, // South Bay
		// Port (Green) Spars
		{"green", -79.8245, 44.8690}, // C75 Turning Island
		{"green", -79.8185, 44.8740}, // Inner Channel
		{"green", -79.8185, 44.8780}, // Inner Channel North
		{"green", -79.8780, 44.9190},
		{"green", -79.8820, 44.9290},
		{"green", -79.8840, 44.9380},
		{"green", -79.8870, 44.9570},
		{"green", -79.8000, 44.8725},
	}

	var buoys []BuoyData
	for _, b := range rawBuoys {
		buoys = append(buoys, BuoyData{
			Type:   b.Type,
			Lat:    b.Lat,
			Lon:    b.Lon,
			SVGPos: cfg.GeoToSVG(b.Lon, b.Lat),
		})
	}

	// Anchorages
	rawAnchors := []struct {
		Name string
		Lon  float64
		Lat  float64
	}{
		{"Brown Bay Anchorage", -79.8891, 44.9485},
		{"Longuissa Bay Anchorage", -79.8895, 44.9635},
		{"Bone Island Anchorage", -79.8550, 44.9280},
	}

	var anchors []AnchorSpot
	for _, a := range rawAnchors {
		anchors = append(anchors, AnchorSpot{
			Name:   a.Name,
			Lat:    a.Lat,
			Lon:    a.Lon,
			SVGPos: cfg.GeoToSVG(a.Lon, a.Lat),
		})
	}

	// Index islands by ID
	islandMap := make(map[string]Island)
	for _, isl := range islands {
		islandMap[isl.ID] = isl
	}

	// Computed island labels
	optLittleB := 80.3
	optWebber := 84.7
	optMinni := -69.3

	labelConfigs := []IslandLabelConfig{
		{Name: "BEAUSOLEIL ISLAND", X: 49.5, Y: 168.0, Angle: 99.5, Size: 3.0},
		{Name: "ROBERTS ISLAND", X: 86.0, Y: 168.0, Angle: -77.8, Size: 2.1},
		{Name: "LITTLE BEAUSOLEIL I.", ID: "118832581", AngleOverride: &optLittleB, Size: 1.6},
		{Name: "WEBBER ISLAND", ID: "118778024", AngleOverride: &optWebber, Size: 1.6},
		{Name: "MINNICOGNASHENE I.", ID: "118832737", AngleOverride: &optMinni, Size: 1.5},
		{Name: "BONE ISLAND", ID: "bone_island", Size: 2.8},
		{Name: "TOMAHAWK ISLAND", ID: "118777995", Size: 1.8},
		{Name: "DEER ISLAND", ID: "118832716", Size: 1.8},
		{Name: "MERMAID ISLAND", ID: "118832865", Size: 1.6},
		{Name: "QUARRY ISLAND", ID: "118744916", Size: 1.7},
		{Name: "GOVERNOR ISLAND", ID: "118832658", Size: 1.5},
		{Name: "ARTHUR ISLAND", ID: "118811665", Size: 1.5},
		{Name: "PICNIC ISLAND", ID: "118744790", Size: 1.4},
		{Name: "ROYAL ISLAND", ID: "118744848", Size: 1.4},
		{Name: "PRESENT ISLAND", Lon: -79.8510, Lat: 44.8255, Angle: 15.0, Size: 1.4, HasPos: true},
		{Name: "BURNT ISLAND", ID: "118832697", Size: 1.7},
	}

	type ComputedLabel struct {
		Name  string
		X     float64
		Y     float64
		Angle float64
		Size  float64
	}

	var computedLabels []ComputedLabel
	for _, lcfg := range labelConfigs {
		if lcfg.X != 0 && lcfg.Y != 0 {
			computedLabels = append(computedLabels, ComputedLabel{
				Name:  lcfg.Name,
				X:     lcfg.X,
				Y:     lcfg.Y,
				Angle: lcfg.Angle,
				Size:  lcfg.Size,
			})
		} else if lcfg.ID != "" {
			if isl, exists := islandMap[lcfg.ID]; exists {
				cx, cy, deg := GetPolygonOrientation(isl.Pts)
				angle := deg
				if lcfg.AngleOverride != nil {
					angle = *lcfg.AngleOverride
				}
				computedLabels = append(computedLabels, ComputedLabel{
					Name:  lcfg.Name,
					X:     cx,
					Y:     cy,
					Angle: angle,
					Size:  lcfg.Size,
				})
			}
		} else if lcfg.HasPos {
			svgPt := cfg.GeoToSVG(lcfg.Lon, lcfg.Lat)
			computedLabels = append(computedLabels, ComputedLabel{
				Name:  lcfg.Name,
				X:     svgPt.X,
				Y:     svgPt.Y,
				Angle: lcfg.Angle,
				Size:  lcfg.Size,
			})
		}
	}

	// Area labels
	areaLabels := []AreaLabel{
		{Name: "HONEY HARBOUR", Lon: -79.8116, Lat: 44.8740, Size: 1.5, Weight: "bold", Color: "#ffffff", Align: "start", OffsetX: 2.0, OffsetY: 0.4},
		{Name: "SOUTH BAY COVE", Lon: -79.7680, Lat: 44.8764, Size: 1.5, Weight: "bold", Color: "#ffffff", Align: "end", OffsetX: -2.0, OffsetY: -1.0},
		{Name: "BROWN BAY", Lon: -79.8891, Lat: 44.9485, Size: 1.4, Weight: "600", Color: "#a8dadc", Align: "end", OffsetX: -3.0, OffsetY: 0.4},
		{Name: "LONGUISSA BAY", Lon: -79.8895, Lat: 44.9635, Size: 1.4, Weight: "bold", Color: "#ffffff", Align: "start", OffsetX: 3.0, OffsetY: 0.4},
		{Name: "COGNASHENE", Lon: -79.9050, Lat: 44.9450, Size: 1.7, Weight: "600", Color: "#e0e1dd", Align: "middle", OffsetX: 0, OffsetY: 0},
	}
	for i := range areaLabels {
		areaLabels[i].SVGPos = cfg.GeoToSVG(areaLabels[i].Lon, areaLabels[i].Lat)
	}

	// -------------------------------------------------------------------------
	// Build Master SVG (georgian_bay_display.svg)
	// -------------------------------------------------------------------------
	fmt.Println("Generating georgian_bay_display.svg ...")

	// Pre-build island paths with lakes carved out
	type IslandRenderInfo struct {
		ID string
		D  string
	}
	var renderedIslands []IslandRenderInfo
	for _, isl := range islands {
		islD := PointsToPath(isl.Pts, true)
		if lakes, ok := islandLakesMap[isl.ID]; ok && len(lakes) > 0 {
			var sb strings.Builder
			sb.WriteString(islD)
			for _, l := range lakes {
				sb.WriteString(" ")
				sb.WriteString(PointsToPath(l, true))
			}
			islD = sb.String()
		}
		renderedIslands = append(renderedIslands, IslandRenderInfo{ID: isl.ID, D: islD})
	}

	// Build land clip path content (mainland + all islands, with lakes carved out via evenodd)
	var landClipSB strings.Builder
	landClipSB.WriteString(fmt.Sprintf(`        <path d="%s" clip-rule="evenodd"/>`+"\n", mainlandCompoundD))
	for _, isl := range renderedIslands {
		landClipSB.WriteString(fmt.Sprintf(`        <path d="%s" clip-rule="evenodd"/>`+"\n", isl.D))
	}

	// Build shoreline strokes over satellite imagery
	var satStrokesSB strings.Builder
	for _, isl := range renderedIslands {
		satStrokesSB.WriteString(fmt.Sprintf(`        <path d="%s" stroke-width="0.06" fill-rule="evenodd"/>`+"\n", isl.D))
	}
	for _, lPts := range islandLakesMap["unassigned"] {
		satStrokesSB.WriteString(fmt.Sprintf(`        <path d="%s" stroke-width="0.06"/>`+"\n", PointsToPath(lPts, true)))
	}

	var masterSB strings.Builder
	masterSB.WriteString(fmt.Sprintf(`<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
     xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
     width="%.1fmm" height="%.1fmm"
     viewBox="0 0 %.1f %.1f">
<defs>
    <clipPath id="mapClip">
        <rect x="%.1f" y="%.1f" width="%.1f" height="%.1f"/>
    </clipPath>
    <clipPath id="landClip" clip-rule="evenodd">
%s    </clipPath>
</defs>

<style>
    .water-bg { fill: #0b1d30; }
    .mainland { fill: #18232c; stroke: #18222d; stroke-width: 0.12; stroke-linejoin: miter; }
    .island { fill: #243447; stroke: #18222d; stroke-width: 0.06; stroke-linejoin: miter; stroke-miterlimit: 4; }
    .inland-lake { fill: #0b1d30; stroke: #18222d; stroke-width: 0.06; stroke-linejoin: miter; }
    
    .island-label { font-family: 'Helvetica Neue', Arial, sans-serif; font-weight: bold; fill: #e0e1dd; letter-spacing: 0.35px; opacity: 0.90; }
    .area-label { font-family: 'Helvetica Neue', Arial, sans-serif; fill: #ffffff; letter-spacing: 0.4px; }
    .title-primary { font-family: 'Cinzel', 'Trajan Pro', 'Georgia', serif; font-weight: bold; fill: #ffd166; letter-spacing: 1.5px; }
    .title-sub { font-family: 'Helvetica Neue', Arial, sans-serif; font-weight: 600; fill: #f1faee; letter-spacing: 1.2px; }
</style>

<!-- WATER -->
<g inkscape:groupmode="layer" id="layer_water" inkscape:label="Water">
    <rect id="water_background" x="0" y="0" width="%.1f" height="%.1f" class="water-bg"/>
</g>

<!-- MAINLAND -->
<g inkscape:groupmode="layer" id="layer_mainland" inkscape:label="Mainland">
    <g clip-path="url(#mapClip)">
        <path id="mainland_shore" d="%s" class="mainland" fill-rule="evenodd"/>
    </g>
</g>

<!-- ISLANDS -->
<g inkscape:groupmode="layer" id="layer_islands" inkscape:label="Islands">
    <g clip-path="url(#mapClip)">
`,
		cfg.TargetWidth, cfg.TargetHeight,
		cfg.TargetWidth, cfg.TargetHeight,
		cfg.MarginX, cfg.MarginY, cfg.MapW, cfg.MapH,
		landClipSB.String(),
		cfg.TargetWidth, cfg.TargetHeight,
		mainlandCompoundD,
	))

	for _, isl := range renderedIslands {
		masterSB.WriteString(fmt.Sprintf(`    <path id="%s" d="%s" class="island" fill-rule="evenodd"/>`+"\n", isl.ID, isl.D))
	}
	for i, lPts := range islandLakesMap["unassigned"] {
		masterSB.WriteString(fmt.Sprintf(`    <path id="inland_lake_%d" d="%s" class="inland-lake"/>`+"\n", i, PointsToPath(lPts, true)))
	}
	masterSB.WriteString("  </g>\n</g>\n\n")

	// SATELLITE (Positioned above landmasses, clipped to land so water is 100% masked out)
	masterSB.WriteString(fmt.Sprintf(`<!-- SATELLITE (Clipped to Landmasses; Water Masked Out) -->
<g inkscape:groupmode="layer" id="layer_satellite" inkscape:label="Satellite" style="display:none;" opacity="1.0">
    <g id="satellite_land" clip-path="url(#landClip)">
        <image id="satellite_image" href="satellite_georgian_bay.png" x="%.3f" y="%.3f" width="%.3f" height="%.3f" preserveAspectRatio="none"/>
    </g>
    <!-- Crisp Granite Shoreline Outlines over Satellite Land -->
    <g clip-path="url(#mapClip)" fill="none" stroke="#18222d" stroke-linejoin="miter" pointer-events="none">
        <path d="%s" stroke-width="0.12" fill-rule="evenodd"/>
%s    </g>
</g>

`,
		cfg.SatX, cfg.SatY, cfg.SatW, cfg.SatH,
		mainlandCompoundD,
		satStrokesSB.String(),
	))

	// Layer: Buoys
	masterSB.WriteString(`<!-- BUOYS -->
<g inkscape:groupmode="layer" id="layer_buoys" inkscape:label="Buoys">
`)
	for _, b := range buoys {
		masterSB.WriteString(fmt.Sprintf("    %s\n", CHSSparBuoySVG(b.SVGPos.X, b.SVGPos.Y, b.Type)))
	}
	masterSB.WriteString("</g>\n\n")

	// Layer: Anchorages
	masterSB.WriteString(`<!-- ANCHORAGES -->
<g inkscape:groupmode="layer" id="layer_anchorages" inkscape:label="Anchorages">
`)
	for _, a := range anchors {
		masterSB.WriteString(fmt.Sprintf("    %s\n", SubtleAnchorSVG(a.SVGPos.X, a.SVGPos.Y, 0.32)))
	}
	masterSB.WriteString("</g>\n\n")

	// Layer: Island labels
	masterSB.WriteString(`<!-- ISLAND LABELS -->
<g inkscape:groupmode="layer" id="layer_island_labels" inkscape:label="Island Labels">
`)
	for _, lbl := range computedLabels {
		masterSB.WriteString(fmt.Sprintf(`    <text transform="translate(%.2f, %.2f) rotate(%.1f)" class="island-label" font-size="%.2f" text-anchor="middle" dominant-baseline="central">%s</text>`+"\n",
			lbl.X, lbl.Y, lbl.Angle, lbl.Size, lbl.Name))
	}
	masterSB.WriteString("</g>\n\n")

	// Layer: Cartography & Frame
	masterSB.WriteString(fmt.Sprintf(`<!-- CARTOGRAPHY -->
<g inkscape:groupmode="layer" id="layer_cartography" inkscape:label="Cartography">
    <rect id="frame_outer" x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="#ffd166" stroke-width="0.45"/>
    <rect id="frame_inner" x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="#415a77" stroke-width="0.2"/>
`, cfg.MarginX, cfg.MarginY, cfg.MapW, cfg.MapH,
		cfg.MarginX+0.7, cfg.MarginY+0.7, cfg.MapW-1.4, cfg.MapH-1.4))
	for _, al := range areaLabels {
		masterSB.WriteString(fmt.Sprintf(`    <text x="%.2f" y="%.2f" class="area-label" font-size="%.2f" font-weight="%s" fill="%s" text-anchor="%s" dominant-baseline="central">%s</text>`+"\n",
			al.SVGPos.X+al.OffsetX, al.SVGPos.Y+al.OffsetY, al.Size, al.Weight, al.Color, al.Align, al.Name))
	}
	// Compass rose
	masterSB.WriteString(RefinedNauticalCompassSVG(cfg.TargetWidth-cfg.MarginX-16.0, cfg.MarginY+18.0, 9.5) + "\n")
	// Title block
	masterSB.WriteString(MasterTitleBlockSVG(cfg.TargetWidth/2.0+8.0, cfg.TargetHeight-cfg.MarginY-7.5) + "\n")
	masterSB.WriteString("</g>\n</svg>\n")

	masterSVG := masterSB.String()
	if err := os.WriteFile("georgian_bay_display.svg", []byte(masterSVG), 0644); err != nil {
		fmt.Fprintf(os.Stderr, "Error writing georgian_bay_display.svg: %v\n", err)
		os.Exit(1)
	}

	// -------------------------------------------------------------------------
	// Build Individual Component Layer SVGs in layers/
	// -------------------------------------------------------------------------
	fmt.Println("Writing full-page layer SVGs into layers/ ...")
	_ = os.MkdirAll("layers", 0755)

	makeLayerSVG := func(filename, innerContent string) {
		content := fmt.Sprintf(`<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     width="%.1fmm" height="%.1fmm"
     viewBox="0 0 %.1f %.1f">
  <defs>
    <clipPath id="mapClip">
      <rect x="%.1f" y="%.1f" width="%.1f" height="%.1f"/>
    </clipPath>
    <clipPath id="landClip" clip-rule="evenodd">
%s    </clipPath>
  </defs>
%s
</svg>`, cfg.TargetWidth, cfg.TargetHeight, cfg.TargetWidth, cfg.TargetHeight,
			cfg.MarginX, cfg.MarginY, cfg.MapW, cfg.MapH, landClipSB.String(), innerContent)
		_ = os.WriteFile(filepath.Join("layers", filename), []byte(content), 0644)
	}

	// Layer 0: Satellite (clipped to land; water masked out)
	makeLayerSVG("00_satellite.svg", fmt.Sprintf(`  <g clip-path="url(#landClip)">
    <image id="satellite_image" href="../satellite_georgian_bay.png" x="%.3f" y="%.3f" width="%.3f" height="%.3f" preserveAspectRatio="none"/>
  </g>`, cfg.SatX, cfg.SatY, cfg.SatW, cfg.SatH))

	// Layer 1: Water
	makeLayerSVG("01_water_base.svg", fmt.Sprintf(`  <rect id="water_background" x="0" y="0" width="%.1f" height="%.1f" fill="#0b1d30"/>`, cfg.TargetWidth, cfg.TargetHeight))

	// Layer 2: Mainland (with all mainland lakes cut out down to water plate)
	makeLayerSVG("02_mainland.svg", fmt.Sprintf(`  <g clip-path="url(#mapClip)">
    <path id="mainland_shore" d="%s" fill="#18232c" fill-rule="evenodd"/>
  </g>`, mainlandCompoundD))

	// Layer 3: Islands (with Beausoleil & other island lakes cut out down to water plate)
	var islandsSB strings.Builder
	islandsSB.WriteString(`  <g clip-path="url(#mapClip)">` + "\n")
	for _, isl := range islands {
		islD := PointsToPath(isl.Pts, true)
		if lakes, ok := islandLakesMap[isl.ID]; ok && len(lakes) > 0 {
			var sb strings.Builder
			sb.WriteString(islD)
			for _, l := range lakes {
				sb.WriteString(" ")
				sb.WriteString(PointsToPath(l, true))
			}
			islD = sb.String()
		}
		islandsSB.WriteString(fmt.Sprintf(`    <path id="%s" d="%s" fill="#243447" fill-rule="evenodd"/>`+"\n", isl.ID, islD))
	}
	islandsSB.WriteString("  </g>")
	makeLayerSVG("03_islands.svg", islandsSB.String())

	// Layer 4: Buoys
	var buoysSB strings.Builder
	for _, b := range buoys {
		col := "#e63946"
		if b.Type == "green" {
			col = "#06d6a0"
		}
		buoysSB.WriteString(fmt.Sprintf(`    <circle cx="%.3f" cy="%.3f" r="0.6" fill="%s"/>`+"\n", b.SVGPos.X, b.SVGPos.Y, col))
	}
	for _, a := range anchors {
		buoysSB.WriteString(fmt.Sprintf(`    <circle cx="%.3f" cy="%.3f" r="1.0" fill="#ffd166"/>`+"\n", a.SVGPos.X, a.SVGPos.Y))
	}
	makeLayerSVG("04_buoys.svg", buoysSB.String())

	// Multi-color Bambu SVG
	bambuSVG := fmt.Sprintf(`<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg"
     width="%.1fmm" height="%.1fmm"
     viewBox="0 0 %.1f %.1f">
  <defs>
    <clipPath id="mapClip">
      <rect x="%.1f" y="%.1f" width="%.1f" height="%.1f"/>
    </clipPath>
  </defs>
  
  <g id="color_1_water" fill="#003566">
    <rect x="0" y="0" width="%.1f" height="%.1f"/>
  </g>
  
  <g id="color_2_mainland" fill="#18232c" clip-path="url(#mapClip)">
    <path d="%s" fill-rule="evenodd"/>
  </g>
  
  <g id="color_3_islands" fill="#2d3748" clip-path="url(#mapClip)">
%s
  </g>
  
  <g id="color_4_buoys">
%s
  </g>
</svg>`,
		cfg.TargetWidth, cfg.TargetHeight,
		cfg.TargetWidth, cfg.TargetHeight,
		cfg.MarginX, cfg.MarginY, cfg.MapW, cfg.MapH,
		cfg.TargetWidth, cfg.TargetHeight,
		mainlandCompoundD,
		islandsSB.String(),
		buoysSB.String(),
	)
	_ = os.WriteFile(filepath.Join("layers", "bambu_lightbox_multicolor.svg"), []byte(bambuSVG), 0644)

	// -------------------------------------------------------------------------
	// Write OpenSCAD Model
	// -------------------------------------------------------------------------
	fmt.Println("Writing georgian_bay_display.scad ...")
	scadContent := fmt.Sprintf(`// =========================================================================
// GEORGIAN BAY 3D DISPLAY & LIGHTBOX (Refined v4)
// Longuissa Bay to South Bay Cove, Thirty Thousand Islands, Georgian Bay
// Designed for Bambu Lab 3D Printers (H2C, X1C, P1S, A1) & AMS multi-color
// All layers share the exact page dimensions (%.1f x %.1f mm)
// =========================================================================

mode = "complete"; // [complete, backlit_faceplate, lightbox_box, water_base, mainland, islands, buoys]

display_width  = %.1f;  // %.1f mm (standard Bambu lightbox size)
display_height = %.1f; // %.1f mm (9.0 inches)

t_water_base   = 1.0;  // 1.0 mm (translucent light transmission)
t_mainland     = 2.2;  // 2.2 mm muted mainland
t_islands      = 2.6;  // 2.6 mm crisp raised islands
t_buoys        = 3.2;  // 3.2 mm raised navigation spar markers
t_frame_lip    = 7.0;  // 7.0 mm perimeter snap-lip for lightbox housing

box_depth      = 38.0; // 38 mm box depth for LED strip
wall_thick     = 2.4;  // 2.4 mm sturdy housing wall
cable_hole_dia = 9.0;  // 9 mm hole for DC / USB-C power cord

c_water      = [0.05, 0.20, 0.35, 0.95]; // Deep Nautical Blue
c_mainland   = [0.18, 0.22, 0.25, 1.0];  // Muted Slate Charcoal
c_islands    = [0.28, 0.35, 0.42, 1.0];  // Granite Island Relief
c_buoy_red   = [0.90, 0.15, 0.20, 1.0];  // Red Spar
c_frame      = [0.08, 0.10, 0.14, 1.0];  // Dark Charcoal Bezel

if (mode == "complete") {
    full_display();
} else if (mode == "backlit_faceplate") {
    backlit_faceplate();
} else if (mode == "lightbox_box") {
    lightbox_enclosure();
} else if (mode == "water_base") {
    color(c_water) water_plate();
} else if (mode == "mainland") {
    color(c_mainland) mainland_part();
} else if (mode == "islands") {
    color(c_islands) islands_part();
} else if (mode == "buoys") {
    color(c_buoy_red) buoys_part();
}

module water_plate() {
    cube([display_width, display_height, t_water_base]);
}

module mainland_part() {
    linear_extrude(height = t_mainland)
        import("layers/02_mainland.svg");
}

module islands_part() {
    linear_extrude(height = t_islands)
        import("layers/03_islands.svg");
}

module buoys_part() {
    linear_extrude(height = t_buoys)
        import("layers/04_buoys.svg");
}

module frame_rim() {
    difference() {
        cube([display_width, display_height, t_frame_lip]);
        translate([wall_thick, wall_thick, -1])
            cube([display_width - 2 * wall_thick, display_height - 2 * wall_thick, t_frame_lip + 2]);
    }
}

module full_display() {
    union() {
        color(c_water) water_plate();
        color(c_mainland) mainland_part();
        color(c_islands) islands_part();
        color(c_buoy_red) buoys_part();
        color(c_frame) frame_rim();
    }
}

module backlit_faceplate() {
    union() {
        water_plate();
        mainland_part();
        islands_part();
        buoys_part();
        frame_rim();
    }
}

module lightbox_enclosure() {
    outer_w = display_width + 1.2;
    outer_h = display_height + 1.2;
    
    difference() {
        cube([outer_w, outer_h, box_depth]);
        translate([wall_thick, wall_thick, wall_thick])
            cube([outer_w - 2 * wall_thick, outer_h - 2 * wall_thick, box_depth]);
        translate([wall_thick - 0.6, wall_thick - 0.6, box_depth - t_frame_lip])
            cube([display_width + 0.4, display_height + 0.4, t_frame_lip + 1]);
        translate([outer_w / 2, -1, wall_thick + cable_hole_dia / 2 + 2])
            rotate([-90, 0, 0])
                cylinder(r = cable_hole_dia / 2, h = wall_thick + 2, $fn = 32);
        translate([outer_w / 2, outer_h - 30, -1])
            cylinder(r = 5.0, h = wall_thick + 2, $fn = 32);
        translate([outer_w / 2 - 2.5, outer_h - 30, -1])
            cube([5.0, 10.0, wall_thick + 2]);
    }
}
`,
		cfg.TargetWidth, cfg.TargetHeight,
		cfg.TargetWidth, cfg.TargetWidth,
		cfg.TargetHeight, cfg.TargetHeight,
	)

	_ = os.WriteFile("georgian_bay_display.scad", []byte(scadContent), 0644)
	fmt.Println("Build completed successfully!")
}
