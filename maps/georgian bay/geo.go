package main

import (
	"math"
)

// NewMapConfig initializes the map configuration and computes projection parameters.
func NewMapConfig(minLat, maxLat, minLon, maxLon, targetWidth, targetHeight, marginX, marginY float64) *MapConfig {
	cfg := &MapConfig{
		MinLat:       minLat,
		MaxLat:       maxLat,
		MinLon:       minLon,
		MaxLon:       maxLon,
		TargetWidth:  targetWidth,
		TargetHeight: targetHeight,
		MarginX:      marginX,
		MarginY:      marginY,
	}

	cfg.MapW = targetWidth - 2*marginX
	cfg.MapH = targetHeight - 2*marginY

	midLat := (minLat + maxLat) / 2.0
	cfg.CosLat = math.Cos(midLat * math.Pi / 180.0)

	cfg.Dlon = maxLon - minLon
	cfg.Dlat = maxLat - minLat

	scaleX := cfg.MapW / (cfg.Dlon * cfg.CosLat)
	scaleY := cfg.MapH / cfg.Dlat
	cfg.IsoScale = math.Min(scaleX, scaleY)

	cfg.OffsetX = marginX + (cfg.MapW-(cfg.Dlon*cfg.CosLat*cfg.IsoScale))/2.0
	cfg.OffsetY = marginY + (cfg.MapH-(cfg.Dlat*cfg.IsoScale))/2.0

	cfg.SatX = cfg.OffsetX
	cfg.SatY = cfg.OffsetY
	cfg.SatW = cfg.Dlon * cfg.CosLat * cfg.IsoScale
	cfg.SatH = cfg.Dlat * cfg.IsoScale

	return cfg
}

// GeoToSVG projects longitude and latitude in degrees to SVG millimeters.
func (cfg *MapConfig) GeoToSVG(lon, lat float64) Point2D {
	x := cfg.OffsetX + (lon-cfg.MinLon)*cfg.CosLat*cfg.IsoScale
	y := cfg.OffsetY + (cfg.MaxLat-lat)*cfg.IsoScale
	return Point2D{X: x, Y: y}
}

// SVGToGeo maps SVG millimeter coordinates back to geographic lon, lat.
func (cfg *MapConfig) SVGToGeo(x, y float64) (lon, lat float64) {
	lon = cfg.MinLon + (x-cfg.OffsetX)/(cfg.CosLat*cfg.IsoScale)
	lat = cfg.MaxLat - (y-cfg.OffsetY)/cfg.IsoScale
	return lon, lat
}

// perpendicularDistance calculates the perpendicular distance from point p to line segment (a, b).
func perpendicularDistance(p, a, b Point2D) float64 {
	dx := b.X - a.X
	dy := b.Y - a.Y
	denom := math.Hypot(dx, dy)
	if denom == 0 {
		return math.Hypot(p.X-a.X, p.Y-a.Y)
	}
	return math.Abs(dy*p.X - dx*p.Y + b.X*a.Y - b.Y*a.X) / denom
}

// SimplifyPoints performs Ramer-Douglas-Peucker polygonal simplification.
func SimplifyPoints(pts []Point2D, tolerance float64) []Point2D {
	if len(pts) <= 2 {
		return pts
	}

	first := pts[0]
	last := pts[len(pts)-1]

	maxDist := 0.0
	maxIndex := 0

	for i := 1; i < len(pts)-1; i++ {
		d := perpendicularDistance(pts[i], first, last)
		if d > maxDist {
			maxDist = d
			maxIndex = i
		}
	}

	if maxDist > tolerance {
		left := SimplifyPoints(pts[:maxIndex+1], tolerance)
		right := SimplifyPoints(pts[maxIndex:], tolerance)
		result := make([]Point2D, 0, len(left)+len(right)-1)
		result = append(result, left[:len(left)-1]...)
		result = append(result, right...)
		return result
	}

	return []Point2D{first, last}
}

// GetPolygonOrientation computes the centroid and principal major axis angle (in degrees) of a polygon.
func GetPolygonOrientation(pts []Point2D) (cx, cy, angleDeg float64) {
	if len(pts) == 0 {
		return 0, 0, 0
	}

	// Centroid
	sumX, sumY := 0.0, 0.0
	for _, p := range pts {
		sumX += p.X
		sumY += p.Y
	}
	n := float64(len(pts))
	cx = sumX / n
	cy = sumY / n

	// Second central moments (covariance matrix)
	var u20, u02, u11 float64
	for _, p := range pts {
		dx := p.X - cx
		dy := p.Y - cy
		u20 += dx * dx
		u02 += dy * dy
		u11 += dx * dy
	}

	// Angle of principal major axis
	theta := 0.5 * math.Atan2(2.0*u11, u20-u02)
	deg := theta * 180.0 / math.Pi

	// Normalize angle so text is easily readable (between -90 and 90)
	if deg > 90.0 {
		deg -= 180.0
	} else if deg < -90.0 {
		deg += 180.0
	}

	return cx, cy, deg
}

// PointInPolygon tests if a point lies inside a 2D polygon using ray casting.
func PointInPolygon(pt Point2D, poly []Point2D) bool {
	inside := false
	for i, j := 0, len(poly)-1; i < len(poly); j, i = i, i+1 {
		if ((poly[i].Y > pt.Y) != (poly[j].Y > pt.Y)) &&
			(pt.X < (poly[j].X-poly[i].X)*(pt.Y-poly[i].Y)/(poly[j].Y-poly[i].Y)+poly[i].X) {
			inside = !inside
		}
	}
	return inside
}
