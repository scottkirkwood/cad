package main

import (
	"strings"
	"testing"
)

func TestPointsToPath(t *testing.T) {
	pts := []Point2D{
		{X: 10, Y: 20},
		{X: 30, Y: 40},
		{X: 50, Y: 60},
	}
	pathClosed := PointsToPath(pts, true)
	if !strings.HasPrefix(pathClosed, "M 10.000 20.000") {
		t.Errorf("unexpected path start: %s", pathClosed)
	}
	if !strings.HasSuffix(pathClosed, "Z") {
		t.Errorf("expected closed path to end with Z: %s", pathClosed)
	}

	pathOpen := PointsToPath(pts, false)
	if strings.HasSuffix(pathOpen, "Z") {
		t.Errorf("open path should not end with Z: %s", pathOpen)
	}
}

func TestCHSSparBuoySVG(t *testing.T) {
	redSVG := CHSSparBuoySVG(50.0, 75.0, "red")
	if !strings.Contains(redSVG, "#e63946") {
		t.Errorf("red spar buoy must contain red color #e63946")
	}
	if !strings.Contains(redSVG, "<polygon") {
		t.Errorf("red spar buoy must have conical polygon topmark")
	}
	if !strings.Contains(redSVG, "rotate(20, 0, 0)") {
		t.Errorf("spar buoy must be tilted right ~20 degrees")
	}

	greenSVG := CHSSparBuoySVG(60.0, 85.0, "green")
	if !strings.Contains(greenSVG, "#06d6a0") {
		t.Errorf("green spar buoy must contain green color #06d6a0")
	}
	if !strings.Contains(greenSVG, "<rect") {
		t.Errorf("green spar buoy must have cylindrical can topmark")
	}
}

func TestSubtleAnchorSVG(t *testing.T) {
	anchorSVG := SubtleAnchorSVG(100.0, 120.0, 0.32)
	if !strings.Contains(anchorSVG, "translate(100.000, 120.000)") {
		t.Errorf("anchor symbol must be positioned at (100, 120)")
	}
	if !strings.Contains(anchorSVG, "scale(0.320)") {
		t.Errorf("anchor symbol must reflect scale 0.32")
	}
	if !strings.Contains(anchorSVG, "#ffd166") {
		t.Errorf("anchor symbol must use nautical gold color #ffd166")
	}
}

func TestRefinedNauticalCompassSVG(t *testing.T) {
	compassSVG := RefinedNauticalCompassSVG(140.0, 20.0, 9.5)
	if !strings.Contains(compassSVG, `id="compass_rose"`) {
		t.Errorf("compass rose must have id='compass_rose'")
	}
	if !strings.Contains(compassSVG, "fill=\"#d90429\"") {
		t.Errorf("compass rose North point must contain crimson #d90429")
	}
	if !strings.Contains(compassSVG, "fill=\"#ffd166\"") {
		t.Errorf("compass rose North point must contain gold #ffd166")
	}
	// Verify cardinal letters N, S, E, W
	for _, letter := range []string{">N<", ">S<", ">E<", ">W<"} {
		if !strings.Contains(compassSVG, letter) {
			t.Errorf("compass rose missing cardinal letter %s", letter)
		}
	}
}

func TestMasterTitleBlockSVG(t *testing.T) {
	titleSVG := MasterTitleBlockSVG(85.0, 215.0)
	if !strings.Contains(titleSVG, "GEORGIAN BAY") {
		t.Errorf("title block missing primary title 'GEORGIAN BAY'")
	}
	if !strings.Contains(titleSVG, "THIRTY THOUSAND ISLANDS") {
		t.Errorf("title block missing subtitle 'THIRTY THOUSAND ISLANDS'")
	}
	if !strings.Contains(titleSVG, `rx="1.2"`) {
		t.Errorf("title block should have rounded plaque border")
	}
}
