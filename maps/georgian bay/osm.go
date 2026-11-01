package main

import (
	"encoding/xml"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strconv"
)

// Raw OSM XML structs
type OSMNodeXML struct {
	ID   string `xml:"id,attr"`
	Lat  string `xml:"lat,attr"`
	Lon  string `xml:"lon,attr"`
	Tags []struct {
		K string `xml:"k,attr"`
		V string `xml:"v,attr"`
	} `xml:"tag"`
}

type OSMWayXML struct {
	ID  string `xml:"id,attr"`
	NDs []struct {
		Ref string `xml:"ref,attr"`
	} `xml:"nd"`
	Tags []struct {
		K string `xml:"k,attr"`
		V string `xml:"v,attr"`
	} `xml:"tag"`
}

type OSMMember struct {
	Type string `xml:"type,attr"`
	Ref  string `xml:"ref,attr"`
	Role string `xml:"role,attr"`
}

type OSMRelationXML struct {
	ID      string      `xml:"id,attr"`
	Members []OSMMember `xml:"member"`
	Tags    []struct {
		K string `xml:"k,attr"`
		V string `xml:"v,attr"`
	} `xml:"tag"`
}

type OSMWay struct {
	ID   string
	NDs  []string
	Tags map[string]string
}

type OSMRelation struct {
	ID      string
	Members []OSMMember
	Tags    map[string]string
}

// OSMData holds all parsed OSM elements.
type OSMData struct {
	Nodes     map[string]Point2D // lon, lat stored as X=lon, Y=lat
	Ways      map[string]*OSMWay
	Relations map[string]*OSMRelation
}

// LoadOSMData parses all .osm XML files matching the glob pattern.
func LoadOSMData(pattern string) (*OSMData, error) {
	files, err := filepath.Glob(pattern)
	if err != nil {
		return nil, err
	}
	if len(files) == 0 {
		return nil, fmt.Errorf("no OSM files found matching pattern: %s", pattern)
	}

	data := &OSMData{
		Nodes:     make(map[string]Point2D),
		Ways:      make(map[string]*OSMWay),
		Relations: make(map[string]*OSMRelation),
	}

	for _, filename := range files {
		f, err := os.Open(filename)
		if err != nil {
			return nil, fmt.Errorf("failed to open %s: %w", filename, err)
		}

		decoder := xml.NewDecoder(f)
		for {
			token, err := decoder.Token()
			if err != nil {
				if err == io.EOF {
					break
				}
				f.Close()
				return nil, fmt.Errorf("XML decode error in %s: %w", filename, err)
			}

			switch se := token.(type) {
			case xml.StartElement:
				if se.Name.Local == "node" {
					var nx OSMNodeXML
					if err := decoder.DecodeElement(&nx, &se); err == nil {
						lat, _ := strconv.ParseFloat(nx.Lat, 64)
						lon, _ := strconv.ParseFloat(nx.Lon, 64)
						data.Nodes[nx.ID] = Point2D{X: lon, Y: lat}
					}
				} else if se.Name.Local == "way" {
					var wx OSMWayXML
					if err := decoder.DecodeElement(&wx, &se); err == nil {
						tags := make(map[string]string)
						for _, t := range wx.Tags {
							tags[t.K] = t.V
						}
						nds := make([]string, len(wx.NDs))
						for i, nd := range wx.NDs {
							nds[i] = nd.Ref
						}
						data.Ways[wx.ID] = &OSMWay{
							ID:   wx.ID,
							NDs:  nds,
							Tags: tags,
						}
					}
				} else if se.Name.Local == "relation" {
					var rx OSMRelationXML
					if err := decoder.DecodeElement(&rx, &se); err == nil {
						tags := make(map[string]string)
						for _, t := range rx.Tags {
							tags[t.K] = t.V
						}
						data.Relations[rx.ID] = &OSMRelation{
							ID:      rx.ID,
							Members: rx.Members,
							Tags:    tags,
						}
					}
				}
			}
		}
		f.Close()
	}

	return data, nil
}

// ExtractIslands extracts crisp, simplified island polygons within the map bounds.
func (data *OSMData) ExtractIslands(cfg *MapConfig) ([]Island, [][]Point2D) {
	innerMembers := make(map[string]bool)
	if rel, ok := data.Relations["1205151"]; ok {
		for _, m := range rel.Members {
			if m.Role == "inner" {
				innerMembers[m.Ref] = true
			}
		}
	}

	var islands []Island

	// 1. Beausoleil Island (Ways 118832495 & 1571158879)
	w1, ok1 := data.Ways["118832495"]
	w2, ok2 := data.Ways["1571158879"]
	if ok1 && ok2 {
		var rawNodes []Point2D
		for _, n := range w1.NDs {
			if pt, exists := data.Nodes[n]; exists {
				rawNodes = append(rawNodes, pt)
			}
		}
		for i, n := range w2.NDs {
			if i == 0 {
				continue
			}
			if pt, exists := data.Nodes[n]; exists {
				rawNodes = append(rawNodes, pt)
			}
		}
		if len(rawNodes) > 0 {
			svgPts := make([]Point2D, len(rawNodes))
			for i, p := range rawNodes {
				svgPts[i] = cfg.GeoToSVG(p.X, p.Y)
			}
			sim := SimplifyPoints(svgPts, 0.005)
			islands = append(islands, Island{
				ID:   "beausoleil_island",
				Name: "Beausoleil Island",
				Pts:  sim,
			})
		}
	}

	// Extract all inland lakes and ponds (mainland and islands) to carve as water
	var inlandLakes [][]Point2D
	excludeLakeWays := map[string]bool{
		"118891587": true, "118854934": true, "118811515": true, "118811612": true, "118778440": true,
		"118778442": true, "118748660": true, "118729396": true, "1350706397": true, "1350706396": true,
	}

	seenLakeWays := make(map[string]bool)
	for wid := range excludeLakeWays {
		seenLakeWays[wid] = true
	}

	// 1. Closed ways with natural=water / water=lake/pond/reservoir
	for wid, w := range data.Ways {
		if seenLakeWays[wid] {
			continue
		}
		if w.Tags["natural"] == "water" || w.Tags["water"] == "lake" || w.Tags["water"] == "pond" || w.Tags["water"] == "reservoir" {
			seenLakeWays[wid] = true
			nds := w.NDs
			if len(nds) >= 3 && nds[0] == nds[len(nds)-1] {
				var rawNodes []Point2D
				for _, n := range nds {
					if pt, exists := data.Nodes[n]; exists {
						rawNodes = append(rawNodes, pt)
					}
				}
				if len(rawNodes) < 3 {
					continue
				}

				minLat, maxLat := rawNodes[0].Y, rawNodes[0].Y
				minLon, maxLon := rawNodes[0].X, rawNodes[0].X
				for _, p := range rawNodes[1:] {
					if p.Y < minLat {
						minLat = p.Y
					}
					if p.Y > maxLat {
						maxLat = p.Y
					}
					if p.X < minLon {
						minLon = p.X
					}
					if p.X > maxLon {
						maxLon = p.X
					}
				}

				if maxLat < cfg.MinLat || minLat > cfg.MaxLat || maxLon < cfg.MinLon || minLon > cfg.MaxLon {
					continue
				}

				svgPts := make([]Point2D, len(rawNodes))
				for i, p := range rawNodes {
					svgPts[i] = cfg.GeoToSVG(p.X, p.Y)
				}
				sim := SimplifyPoints(svgPts, 0.005)
				if len(sim) >= 3 {
					inlandLakes = append(inlandLakes, sim)
				}
			}
		}
	}

	// 2. Multipolygon lake relations (e.g. McCrae Lake, Bearshead Lake, Gibson Lake, Bear Lake, Fairy Lake)
	for rid, rel := range data.Relations {
		if rid == "1205151" || rid == "1124369" || rid == "18637401" || rid == "9503693" || rid == "11801609" {
			continue
		}
		if rel.Tags["type"] == "multipolygon" && (rel.Tags["natural"] == "water" || rel.Tags["water"] == "lake" || rel.Tags["water"] == "pond" || rel.Tags["water"] == "reservoir") {
			for _, m := range rel.Members {
				if (m.Role == "outer" || m.Role == "") && m.Type == "way" {
					if seenLakeWays[m.Ref] {
						continue
					}
					seenLakeWays[m.Ref] = true
					if w, ok := data.Ways[m.Ref]; ok {
						nds := w.NDs
						if len(nds) >= 3 && nds[0] == nds[len(nds)-1] {
							var rawNodes []Point2D
							for _, n := range nds {
								if pt, exists := data.Nodes[n]; exists {
									rawNodes = append(rawNodes, pt)
								}
							}
							if len(rawNodes) < 3 {
								continue
							}

							minLat, maxLat := rawNodes[0].Y, rawNodes[0].Y
							minLon, maxLon := rawNodes[0].X, rawNodes[0].X
							for _, p := range rawNodes[1:] {
								if p.Y < minLat {
									minLat = p.Y
								}
								if p.Y > maxLat {
									maxLat = p.Y
								}
								if p.X < minLon {
									minLon = p.X
								}
								if p.X > maxLon {
									maxLon = p.X
								}
							}

							if maxLat < cfg.MinLat || minLat > cfg.MaxLat || maxLon < cfg.MinLon || minLon > cfg.MaxLon {
								continue
							}

							svgPts := make([]Point2D, len(rawNodes))
							for i, p := range rawNodes {
								svgPts[i] = cfg.GeoToSVG(p.X, p.Y)
							}
							sim := SimplifyPoints(svgPts, 0.005)
							if len(sim) >= 3 {
								inlandLakes = append(inlandLakes, sim)
							}
						}
					}
				}
			}
		}
	}

	// 2. Bone Island
	if wBone, ok := data.Ways["118780853"]; ok {
		var rawNodes []Point2D
		for _, n := range wBone.NDs {
			if pt, exists := data.Nodes[n]; exists {
				rawNodes = append(rawNodes, pt)
			}
		}
		if len(rawNodes) > 0 {
			svgPts := make([]Point2D, len(rawNodes))
			for i, p := range rawNodes {
				svgPts[i] = cfg.GeoToSVG(p.X, p.Y)
			}
			islands = append(islands, Island{
				ID:   "bone_island",
				Name: "Bone Island",
				Pts:  SimplifyPoints(svgPts, 0.005),
			})
		}
	}

	// 3. All other islands
	excludeIDs := map[string]bool{
		"118832495":  true,
		"1571158879": true,
		"118780853":  true,
	}

	for wid, w := range data.Ways {
		if excludeIDs[wid] {
			continue
		}
		isIsland := innerMembers[wid] || w.Tags["place"] == "island" || w.Tags["place"] == "islet"
		if !isIsland {
			continue
		}
		nds := w.NDs
		if len(nds) >= 3 && nds[0] == nds[len(nds)-1] {
			var rawNodes []Point2D
			for _, n := range nds {
				if pt, exists := data.Nodes[n]; exists {
					rawNodes = append(rawNodes, pt)
				}
			}
			if len(rawNodes) < 3 {
				continue
			}

			// Bounding check
			minLat, maxLat := rawNodes[0].Y, rawNodes[0].Y
			minLon, maxLon := rawNodes[0].X, rawNodes[0].X
			for _, p := range rawNodes[1:] {
				if p.Y < minLat {
					minLat = p.Y
				}
				if p.Y > maxLat {
					maxLat = p.Y
				}
				if p.X < minLon {
					minLon = p.X
				}
				if p.X > maxLon {
					maxLon = p.X
				}
			}

			if maxLat < cfg.MinLat || minLat > cfg.MaxLat || maxLon < cfg.MinLon || minLon > cfg.MaxLon {
				continue
			}

			svgPts := make([]Point2D, len(rawNodes))
			for i, p := range rawNodes {
				svgPts[i] = cfg.GeoToSVG(p.X, p.Y)
			}
			sim := SimplifyPoints(svgPts, 0.005)
			if len(sim) >= 3 {
				islands = append(islands, Island{
					ID:   wid,
					Name: w.Tags["name"],
					Pts:  sim,
				})
			}
		}
	}

	return islands, inlandLakes
}

// ExtractMainlandPoly extracts and clips the mainland shoreline polygon.
func (data *OSMData) ExtractMainlandPoly(cfg *MapConfig) []Point2D {
	outerRefs := []string{
		"118891587", "118854934", "118811515", "118811612", "118778440",
		"118778442", "118748660", "118729396", "1350706397", "1350706396",
	}

	var shoreRaw []Point2D
	for _, ref := range outerRefs {
		if w, ok := data.Ways[ref]; ok {
			var ptsThis []Point2D
			for _, n := range w.NDs {
				if pt, exists := data.Nodes[n]; exists {
					ptsThis = append(ptsThis, pt)
				}
			}
			if len(ptsThis) == 0 {
				continue
			}
			if len(shoreRaw) == 0 {
				shoreRaw = append(shoreRaw, ptsThis...)
			} else {
				last := shoreRaw[len(shoreRaw)-1]
				if ptsThis[0] == last {
					shoreRaw = append(shoreRaw, ptsThis[1:]...)
				} else if ptsThis[len(ptsThis)-1] == last {
					for j := len(ptsThis) - 2; j >= 0; j-- {
						shoreRaw = append(shoreRaw, ptsThis[j])
					}
				} else {
					shoreRaw = append(shoreRaw, ptsThis...)
				}
			}
		}
	}

	xmin := cfg.MarginX
	xmax := cfg.TargetWidth - cfg.MarginX
	ymin := cfg.MarginY
	ymax := cfg.TargetHeight - cfg.MarginY

	var mainShore []Point2D
	startIdx := 1400

	// Interpolate entry at left border (X = xmin)
	for i := 1300; i < 1500 && i < len(shoreRaw)-1; i++ {
		p1 := cfg.GeoToSVG(shoreRaw[i].X, shoreRaw[i].Y)
		p2 := cfg.GeoToSVG(shoreRaw[i+1].X, shoreRaw[i+1].Y)
		if p1.X < xmin && p2.X >= xmin {
			t := (xmin - p1.X) / (p2.X - p1.X)
			yInt := p1.Y + t*(p2.Y-p1.Y)
			if yInt < ymin {
				yInt = ymin
			} else if yInt > ymax {
				yInt = ymax
			}
			mainShore = append(mainShore, Point2D{X: xmin, Y: yInt})
			startIdx = i + 1
			break
		}
	}

	// Trace shoreline down to bottom border (Y = ymax)
	for i := startIdx; i < len(shoreRaw)-1; i++ {
		p1 := cfg.GeoToSVG(shoreRaw[i].X, shoreRaw[i].Y)
		p2 := cfg.GeoToSVG(shoreRaw[i+1].X, shoreRaw[i+1].Y)
		if p1.Y <= ymax && p2.Y > ymax {
			t := (ymax - p1.Y) / (p2.Y - p1.Y)
			xInt := p1.X + t*(p2.X-p1.X)
			clampX := p1.X
			if clampX < xmin {
				clampX = xmin
			} else if clampX > xmax {
				clampX = xmax
			}
			clampY := p1.Y
			if clampY < ymin {
				clampY = ymin
			} else if clampY > ymax {
				clampY = ymax
			}
			mainShore = append(mainShore, Point2D{X: clampX, Y: clampY})

			clampXInt := xInt
			if clampXInt < xmin {
				clampXInt = xmin
			} else if clampXInt > xmax {
				clampXInt = xmax
			}
			mainShore = append(mainShore, Point2D{X: clampXInt, Y: ymax})
			break
		}

		clampX := p1.X
		if clampX < xmin {
			clampX = xmin
		} else if clampX > xmax {
			clampX = xmax
		}
		clampY := p1.Y
		if clampY < ymin {
			clampY = ymin
		} else if clampY > ymax {
			clampY = ymax
		}
		mainShore = append(mainShore, Point2D{X: clampX, Y: clampY})
	}

	simShore := SimplifyPoints(mainShore, 0.005)
	mainlandPoly := append(simShore,
		Point2D{X: xmax, Y: ymax},
		Point2D{X: xmax, Y: ymin},
		Point2D{X: xmin, Y: ymin},
	)

	return mainlandPoly
}
