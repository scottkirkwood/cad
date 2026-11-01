package main

import (
	"fmt"
	"math"
	"strings"
)

// PointsToPath converts a slice of Point2D into an SVG path d attribute string.
func PointsToPath(pts []Point2D, closed bool) string {
	if len(pts) == 0 {
		return ""
	}
	var sb strings.Builder
	sb.WriteString(fmt.Sprintf("M %.3f %.3f", pts[0].X, pts[0].Y))
	for _, p := range pts[1:] {
		sb.WriteString(fmt.Sprintf(" L %.3f %.3f", p.X, p.Y))
	}
	if closed {
		sb.WriteString(" Z")
	}
	return sb.String()
}

// CHSSparBuoySVG produces an authentic IHO / CHS Chart No. 1 spar buoy symbol:
// - Base circle at charted water coordinates
// - Slender mast tilted ~20 degrees to the right
// - Conical topmark for Red (Starboard) / Cylindrical can topmark for Green (Port)
func CHSSparBuoySVG(x, y float64, buoyType string) string {
	col := "#e63946"
	if buoyType == "green" {
		col = "#06d6a0"
	}

	if buoyType == "red" {
		return fmt.Sprintf(`<g transform="translate(%.3f, %.3f)">`+
			`<circle cx="0" cy="0" r="0.22" fill="%s" stroke="#111" stroke-width="0.08"/>`+
			`<g transform="rotate(20, 0, 0)">`+
			`<line x1="0" y1="0" x2="0" y2="-0.45" stroke="#111" stroke-width="0.14"/>`+
			`<polygon points="0,-1.45 -0.26,-0.45 0.26,-0.45" fill="%s" stroke="#111" stroke-width="0.06"/>`+
			`</g></g>`, x, y, col, col)
	}

	return fmt.Sprintf(`<g transform="translate(%.3f, %.3f)">`+
		`<circle cx="0" cy="0" r="0.22" fill="%s" stroke="#111" stroke-width="0.08"/>`+
		`<g transform="rotate(20, 0, 0)">`+
		`<line x1="0" y1="0" x2="0" y2="-0.45" stroke="#111" stroke-width="0.14"/>`+
		`<rect x="-0.22" y="-1.35" width="0.44" height="0.9" fill="%s" stroke="#111" stroke-width="0.06"/>`+
		`</g></g>`, x, y, col, col)
}

// SubtleAnchorSVG produces a clean, subtle nautical anchor symbol for anchorages.
func SubtleAnchorSVG(x, y, scale float64) string {
	return fmt.Sprintf(`<g transform="translate(%.3f, %.3f) scale(%.3f)">`+
		`<circle cx="0" cy="-3.6" r="1.0" fill="none" stroke="#ffd166" stroke-width="0.7"/>`+
		`<line x1="-2.4" y1="-2.4" x2="2.4" y2="-2.4" stroke="#ffd166" stroke-width="0.8" stroke-linecap="round"/>`+
		`<line x1="0" y1="-2.8" x2="0" y2="3.0" stroke="#ffd166" stroke-width="0.8" stroke-linecap="round"/>`+
		`<path d="M -3.2 0.8 C -2.8 3.4 2.8 3.4 3.2 0.8" fill="none" stroke="#ffd166" stroke-width="0.8" stroke-linecap="round"/>`+
		`<polygon points="-3.7,0.4 -2.5,1.0 -3.1,1.6" fill="#ffd166"/>`+
		`<polygon points="3.7,0.4 2.5,1.0 3.1,1.6" fill="#ffd166"/>`+
		`</g>`, x, y, scale)
}

// RefinedNauticalCompassSVG generates a 16-facet 3D relief nautical star compass rose:
// - Dual concentric rings with degree tick marks every 5, 15, and 30 degrees
// - 16 faceted light/shadow relief triangles across all 8 cardinal and ordinal points
// - Distinctive North point in Crimson (#d90429) & Gold (#ffd166) with finial arrowhead
// - Multi-stage concentric polished brass center boss and classic serif lettering
func RefinedNauticalCompassSVG(cx, cy, r float64) string {
	var sb strings.Builder
	sb.WriteString(fmt.Sprintf(`<g transform="translate(%.2f, %.2f)" id="compass_rose">`+"\n", cx, cy))

	// Outer background disc & rings
	sb.WriteString(fmt.Sprintf(`  <circle cx="0" cy="0" r="%.2f" fill="#09131d" fill-opacity="0.96" stroke="#ffd166" stroke-width="0.45"/>`+"\n", r))
	sb.WriteString(fmt.Sprintf(`  <circle cx="0" cy="0" r="%.2f" fill="none" stroke="#2a3f55" stroke-width="0.15"/>`+"\n", r*0.91))
	sb.WriteString(fmt.Sprintf(`  <circle cx="0" cy="0" r="%.2f" fill="none" stroke="#ffd166" stroke-width="0.22"/>`+"\n", r*0.80))

	// Degree tick marks around the outer bezel
	for deg := 0; deg < 360; deg += 5 {
		rad := float64(deg) * math.Pi / 180.0
		var rIn float64
		var sw string
		var col string

		if deg%90 == 0 {
			rIn = r * 0.76
			sw = "0.32"
			col = "#ffd166"
		} else if deg%30 == 0 {
			rIn = r * 0.80
			sw = "0.20"
			col = "#ffd166"
		} else if deg%15 == 0 {
			rIn = r * 0.84
			sw = "0.14"
			col = "#778da9"
		} else {
			rIn = r * 0.87
			sw = "0.09"
			col = "#415a77"
		}

		x1 := rIn * math.Sin(rad)
		y1 := -rIn * math.Cos(rad)
		x2 := r * 0.91 * math.Sin(rad)
		y2 := -r * 0.91 * math.Cos(rad)
		sb.WriteString(fmt.Sprintf(`  <line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" stroke-width="%s"/>`+"\n", x1, y1, x2, y2, col, sw))
	}

	// Faceted 8-point star geometry
	rCard := r * 0.78 // Main cardinal radius
	rOrd := r * 0.52  // Ordinal radius
	rIn := r * 0.20   // Inner valley radius

	sin45 := 0.7071
	cos45 := 0.7071

	// Ordinal Points (NE, SE, SW, NW) - 2-tone light and dark facets
	// NE
	sb.WriteString(fmt.Sprintf(`  <polygon points="0,0 %.2f,%.2f %.2f,%.2f" fill="#3b5066"/>`+"\n", rOrd*sin45, -rOrd*cos45, rIn*0.35, -rIn*0.93))
	sb.WriteString(fmt.Sprintf(`  <polygon points="0,0 %.2f,%.2f %.2f,%.2f" fill="#1b2838"/>`+"\n", rOrd*sin45, -rOrd*cos45, rIn*0.93, -rIn*0.35))
	// SE
	sb.WriteString(fmt.Sprintf(`  <polygon points="0,0 %.2f,%.2f %.2f,%.2f" fill="#3b5066"/>`+"\n", rOrd*sin45, rOrd*cos45, rIn*0.93, rIn*0.35))
	sb.WriteString(fmt.Sprintf(`  <polygon points="0,0 %.2f,%.2f %.2f,%.2f" fill="#1b2838"/>`+"\n", rOrd*sin45, rOrd*cos45, rIn*0.35, rIn*0.93))
	// SW
	sb.WriteString(fmt.Sprintf(`  <polygon points="0,0 %.2f,%.2f %.2f,%.2f" fill="#3b5066"/>`+"\n", -rOrd*sin45, rOrd*cos45, -rIn*0.35, rIn*0.93))
	sb.WriteString(fmt.Sprintf(`  <polygon points="0,0 %.2f,%.2f %.2f,%.2f" fill="#1b2838"/>`+"\n", -rOrd*sin45, rOrd*cos45, -rIn*0.93, rIn*0.35))
	// NW
	sb.WriteString(fmt.Sprintf(`  <polygon points="0,0 %.2f,%.2f %.2f,%.2f" fill="#3b5066"/>`+"\n", -rOrd*sin45, -rOrd*cos45, -rIn*0.93, -rIn*0.35))
	sb.WriteString(fmt.Sprintf(`  <polygon points="0,0 %.2f,%.2f %.2f,%.2f" fill="#1b2838"/>`+"\n", -rOrd*sin45, -rOrd*cos45, -rIn*0.35, -rIn*0.93))

	// Cardinal East (facing +X)
	sb.WriteString(fmt.Sprintf(`  <polygon points="0,0 %.2f,0 %.2f,%.2f" fill="#e0e1dd"/>`+"\n", rCard*0.90, rIn, -rIn*0.38))
	sb.WriteString(fmt.Sprintf(`  <polygon points="0,0 %.2f,0 %.2f,%.2f" fill="#3b5066"/>`+"\n", rCard*0.90, rIn, rIn*0.38))

	// Cardinal West (facing -X)
	sb.WriteString(fmt.Sprintf(`  <polygon points="0,0 %.2f,0 %.2f,%.2f" fill="#e0e1dd"/>`+"\n", -rCard*0.90, -rIn, -rIn*0.38))
	sb.WriteString(fmt.Sprintf(`  <polygon points="0,0 %.2f,0 %.2f,%.2f" fill="#3b5066"/>`+"\n", -rCard*0.90, -rIn, rIn*0.38))

	// Cardinal South (facing +Y)
	sb.WriteString(fmt.Sprintf(`  <polygon points="0,0 0,%.2f %.2f,%.2f" fill="#e0e1dd"/>`+"\n", rCard*0.90, -rIn*0.38, rIn))
	sb.WriteString(fmt.Sprintf(`  <polygon points="0,0 0,%.2f %.2f,%.2f" fill="#3b5066"/>`+"\n", rCard*0.90, rIn*0.38, rIn))

	// Cardinal North (facing -Y) - Vivid Crimson and Polished Gold
	sb.WriteString(fmt.Sprintf(`  <polygon points="0,0 0,%.2f %.2f,%.2f" fill="#ffd166"/>`+"\n", -rCard, -rIn*0.38, -rIn))
	sb.WriteString(fmt.Sprintf(`  <polygon points="0,0 0,%.2f %.2f,%.2f" fill="#d90429"/>`+"\n", -rCard, rIn*0.38, -rIn))
	// North Arrowhead Finial / Spearhead accent
	sb.WriteString(fmt.Sprintf(`  <polygon points="0,%.2f %.2f,%.2f 0,%.2f" fill="#ffd166"/>`+"\n", -rCard*1.08, -0.7, -rCard*0.82, -rCard*0.88))
	sb.WriteString(fmt.Sprintf(`  <polygon points="0,%.2f %.2f,%.2f 0,%.2f" fill="#d90429"/>`+"\n", -rCard*1.08, 0.7, -rCard*0.82, -rCard*0.88))

	// Center multi-stage brass hub
	sb.WriteString(`  <circle cx="0" cy="0" r="1.30" fill="#ffd166" stroke="#09131d" stroke-width="0.25"/>` + "\n")
	sb.WriteString(`  <circle cx="0" cy="0" r="0.70" fill="#b38f38" stroke="#09131d" stroke-width="0.15"/>` + "\n")
	sb.WriteString(`  <circle cx="0" cy="0" r="0.30" fill="#09131d"/>` + "\n")

	// Cardinal Lettering
	sb.WriteString(fmt.Sprintf(`  <text x="0" y="%.2f" fill="#ffd166" font-family="'Cinzel', 'Georgia', serif" font-size="2.8" font-weight="bold" text-anchor="middle" dominant-baseline="central">N</text>`+"\n", -r*1.18))
	sb.WriteString(fmt.Sprintf(`  <text x="0" y="%.2f" fill="#8da3b8" font-family="'Helvetica Neue', Arial, sans-serif" font-size="1.5" font-weight="600" text-anchor="middle" dominant-baseline="central">S</text>`+"\n", r*1.15))
	sb.WriteString(fmt.Sprintf(`  <text x="%.2f" y="0" fill="#8da3b8" font-family="'Helvetica Neue', Arial, sans-serif" font-size="1.5" font-weight="600" text-anchor="middle" dominant-baseline="central">E</text>`+"\n", r*1.15))
	sb.WriteString(fmt.Sprintf(`  <text x="%.2f" y="0" fill="#8da3b8" font-family="'Helvetica Neue', Arial, sans-serif" font-size="1.5" font-weight="600" text-anchor="middle" dominant-baseline="central">W</text>`+"\n", -r*1.15))

	sb.WriteString("</g>")
	return sb.String()
}

// MasterTitleBlockSVG generates the solid opaque title block, centered vertically and horizontally.
func MasterTitleBlockSVG(titleX, titleY float64) string {
	return fmt.Sprintf(`    <!-- Master Title Block (Opaque, Clean, Centered) -->
    <g transform="translate(%.2f, %.2f)" id="title_block">
        <rect x="-42" y="-6.0" width="84" height="12.0" fill="#09131d" fill-opacity="1.0" rx="1.2" stroke="#ffd166" stroke-width="0.45"/>
        <line x1="-38" y1="-4.6" x2="38" y2="-4.6" stroke="#415a77" stroke-width="0.2"/>
        <line x1="-38" y1="4.6" x2="38" y2="4.6" stroke="#415a77" stroke-width="0.2"/>
        
        <text x="0" y="-1.5" class="title-primary" font-size="4.0" text-anchor="middle" dominant-baseline="central">GEORGIAN BAY</text>
        <text x="0" y="2.2" class="title-sub" font-size="1.9" text-anchor="middle" dominant-baseline="central">THIRTY THOUSAND ISLANDS</text>
    </g>`, titleX, titleY)
}
