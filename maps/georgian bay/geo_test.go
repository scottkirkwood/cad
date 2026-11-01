package main

import (
	"math"
	"testing"
)

func TestNewMapConfig(t *testing.T) {
	cfg := NewMapConfig(44.8225, 44.9715, -79.9140, -79.7660, 163.8, 228.6, 3.0, 3.0)

	if math.Abs(cfg.MapW-157.8) > 1e-6 {
		t.Errorf("expected MapW 157.8, got %f", cfg.MapW)
	}
	if math.Abs(cfg.MapH-222.6) > 1e-6 {
		t.Errorf("expected MapH 222.6, got %f", cfg.MapH)
	}
	if cfg.IsoScale <= 0 {
		t.Errorf("expected positive IsoScale, got %f", cfg.IsoScale)
	}
	if cfg.OffsetX < cfg.MarginX || cfg.OffsetY < cfg.MarginY {
		t.Errorf("offset must be >= margin, got OffsetX=%f, OffsetY=%f", cfg.OffsetX, cfg.OffsetY)
	}
}

func TestGeoToSVG_RoundTrip(t *testing.T) {
	cfg := NewMapConfig(44.8225, 44.9715, -79.9140, -79.7660, 163.8, 228.6, 3.0, 3.0)

	testPoints := []struct {
		Lon float64
		Lat float64
	}{
		{-79.9140, 44.9715}, // top-left
		{-79.7660, 44.8225}, // bottom-right
		{-79.8400, 44.8970}, // center
		{-79.8895, 44.9635}, // Longuissa Bay
		{-79.7680, 44.8764}, // South Bay Cove
	}

	for _, pt := range testPoints {
		svgPt := cfg.GeoToSVG(pt.Lon, pt.Lat)
		reLon, reLat := cfg.SVGToGeo(svgPt.X, svgPt.Y)

		if math.Abs(reLon-pt.Lon) > 1e-7 {
			t.Errorf("lon round-trip failed: expected %f, got %f", pt.Lon, reLon)
		}
		if math.Abs(reLat-pt.Lat) > 1e-7 {
			t.Errorf("lat round-trip failed: expected %f, got %f", pt.Lat, reLat)
		}
	}
}

func TestSimplifyPoints(t *testing.T) {
	// Perfectly collinear points along a line
	collinear := []Point2D{
		{X: 0, Y: 0},
		{X: 10, Y: 10},
		{X: 20, Y: 20},
		{X: 30, Y: 30},
		{X: 40, Y: 40},
	}
	simplified := SimplifyPoints(collinear, 0.1)
	if len(simplified) != 2 {
		t.Errorf("expected 2 endpoints for collinear line, got %d", len(simplified))
	}

	// Line with an intentional sharp spike
	spike := []Point2D{
		{X: 0, Y: 0},
		{X: 20, Y: 25}, // 5 units above the line between (0,0) and (40,40)? (20,25) is off the diagonal
		{X: 40, Y: 40},
	}
	simSpike := SimplifyPoints(spike, 0.5)
	if len(simSpike) != 3 {
		t.Errorf("expected spike to be preserved with tolerance 0.5, got %d points", len(simSpike))
	}
}

func TestGetPolygonOrientation(t *testing.T) {
	// Horizontal rectangle: width = 20, height = 4
	horiz := []Point2D{
		{X: 0, Y: 0},
		{X: 20, Y: 0},
		{X: 20, Y: 4},
		{X: 0, Y: 4},
	}
	cx, cy, deg := GetPolygonOrientation(horiz)
	if math.Abs(cx-10.0) > 1e-4 || math.Abs(cy-2.0) > 1e-4 {
		t.Errorf("expected centroid (10, 2), got (%f, %f)", cx, cy)
	}
	if math.Abs(deg) > 1.0 {
		t.Errorf("expected horizontal orientation near 0 deg, got %f", deg)
	}

	// Vertical rectangle: width = 4, height = 20
	vert := []Point2D{
		{X: 0, Y: 0},
		{X: 4, Y: 0},
		{X: 4, Y: 20},
		{X: 0, Y: 20},
	}
	_, _, vdeg := GetPolygonOrientation(vert)
	if math.Abs(math.Abs(vdeg)-90.0) > 1.0 {
		t.Errorf("expected vertical orientation near ±90 deg, got %f", vdeg)
	}
}
