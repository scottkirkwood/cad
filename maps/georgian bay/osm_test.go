package main

import (
	"os"
	"path/filepath"
	"testing"
)

func TestLoadOSMData_Sample(t *testing.T) {
	// Create a minimal sample OSM XML
	sampleXML := `<?xml version="1.0" encoding="UTF-8"?>
<osm version="0.6">
  <node id="101" lat="44.850" lon="-79.850">
    <tag k="name" v="Point A"/>
  </node>
  <node id="102" lat="44.851" lon="-79.850"/>
  <node id="103" lat="44.851" lon="-79.849"/>
  <way id="201">
    <nd ref="101"/>
    <nd ref="102"/>
    <nd ref="103"/>
    <nd ref="101"/>
    <tag k="place" v="island"/>
    <tag k="name" v="Sample Island"/>
  </way>
  <relation id="301">
    <member type="way" ref="201" role="inner"/>
    <tag k="type" v="multipolygon"/>
  </relation>
</osm>`

	tmpDir := t.TempDir()
	sampleFile := filepath.Join(tmpDir, "sample.osm")
	if err := os.WriteFile(sampleFile, []byte(sampleXML), 0644); err != nil {
		t.Fatalf("failed to write sample OSM: %v", err)
	}

	data, err := LoadOSMData(filepath.Join(tmpDir, "*.osm"))
	if err != nil {
		t.Fatalf("LoadOSMData returned error: %v", err)
	}

	if len(data.Nodes) != 3 {
		t.Errorf("expected 3 nodes, got %d", len(data.Nodes))
	}
	if len(data.Ways) != 1 {
		t.Errorf("expected 1 way, got %d", len(data.Ways))
	}
	if len(data.Relations) != 1 {
		t.Errorf("expected 1 relation, got %d", len(data.Relations))
	}

	cfg := NewMapConfig(44.80, 44.90, -79.90, -79.80, 163.8, 228.6, 3.0, 3.0)
	islands, _ := data.ExtractIslands(cfg)
	if len(islands) != 1 {
		t.Errorf("expected 1 extracted island, got %d", len(islands))
	}
	if islands[0].Name != "Sample Island" {
		t.Errorf("expected island name 'Sample Island', got '%s'", islands[0].Name)
	}
}
