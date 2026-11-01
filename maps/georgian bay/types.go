package main

// Point2D represents a 2D coordinate in millimeters (or degrees).
type Point2D struct {
	X float64
	Y float64
}

// MapConfig stores the geographic bounds and target display dimensions.
type MapConfig struct {
	MinLat float64
	MaxLat float64
	MinLon float64
	MaxLon float64

	TargetWidth  float64
	TargetHeight float64
	MarginX      float64
	MarginY      float64

	MapW     float64
	MapH     float64
	CosLat   float64
	Dlon     float64
	Dlat     float64
	IsoScale float64
	OffsetX  float64
	OffsetY  float64

	SatX float64
	SatY float64
	SatW float64
	SatH float64
}

// Island represents an island entity with its SVG path polygon.
type Island struct {
	ID   string
	Name string
	Pts  []Point2D
}

// BuoyData represents a navigational spar buoy.
type BuoyData struct {
	Type   string   // "red" (starboard) or "green" (port)
	Lat    float64
	Lon    float64
	SVGPos Point2D
}

// AnchorSpot represents an anchorage location.
type AnchorSpot struct {
	Name   string
	Lat    float64
	Lon    float64
	SVGPos Point2D
}

// IslandLabelConfig holds configuration for placing an island label.
type IslandLabelConfig struct {
	Name          string
	ID            string
	X             float64
	Y             float64
	Angle         float64
	AngleOverride *float64
	Size          float64
	Lat           float64
	Lon           float64
	HasPos        bool
}

// AreaLabel holds area text configuration.
type AreaLabel struct {
	Name    string
	Lat     float64
	Lon     float64
	Size    float64
	Weight  string
	Color   string
	Align   string
	OffsetX float64
	OffsetY float64
	SVGPos  Point2D
}
