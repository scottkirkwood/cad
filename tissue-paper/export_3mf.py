#!/usr/bin/env python3
"""
Helper script to bundle multiple STL meshes into a single multi-part 3MF file.
Compatible with Bambu Studio, OrcaSlicer, PrusaSlicer, etc.
"""

import sys
import os
import struct
import zipfile

def parse_stl(stl_path):
    verts = []
    tris = []
    vert_map = {}
    
    file_size = os.path.getsize(stl_path)
    
    with open(stl_path, 'rb') as f:
        header = f.read(80)
        num_triangles_bytes = f.read(4)
        if len(num_triangles_bytes) == 4:
            num_triangles = struct.unpack('<I', num_triangles_bytes)[0]
            expected_size = 84 + num_triangles * 50
            if file_size == expected_size:
                # Binary STL
                for _ in range(num_triangles):
                    data = f.read(50)
                    vals = struct.unpack('<12fH', data)
                    v_indices = []
                    for k in range(3):
                        pt = (round(vals[3 + k*3], 4), round(vals[4 + k*3], 4), round(vals[5 + k*3], 4))
                        if pt not in vert_map:
                            vert_map[pt] = len(verts)
                            verts.append(pt)
                        v_indices.append(vert_map[pt])
                    tris.append(tuple(v_indices))
                return verts, tris

    # Fallback: ASCII STL
    with open(stl_path, 'r', errors='ignore') as f:
        current_tri = []
        for line in f:
            line = line.strip()
            if line.startswith('vertex'):
                parts = line.split()
                pt = (round(float(parts[1]), 4), round(float(parts[2]), 4), round(float(parts[3]), 4))
                if pt not in vert_map:
                    vert_map[pt] = len(verts)
                    verts.append(pt)
                current_tri.append(vert_map[pt])
                if len(current_tri) == 3:
                    tris.append(tuple(current_tri))
                    current_tri = []
    return verts, tris

def create_multipart_3mf(parts, output_3mf_path):
    """
    parts: list of tuples (part_name, vertices_list, triangles_list)
    """
    xml_parts = [
        '<?xml version="1.0" encoding="utf-8"?>',
        '<model xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" unit="millimeter" xml:lang="en-US">',
        '  <resources>'
    ]
    
    obj_ids = []
    for idx, (name, verts, tris) in enumerate(parts, start=1):
        obj_ids.append(idx)
        xml_parts.append(f'    <object id="{idx}" name="{name}" type="model">')
        xml_parts.append('      <mesh>')
        xml_parts.append('        <vertices>')
        for v in verts:
            xml_parts.append(f'          <vertex x="{v[0]:.4f}" y="{v[1]:.4f}" z="{v[2]:.4f}" />')
        xml_parts.append('        </vertices>')
        xml_parts.append('        <triangles>')
        for t in tris:
            xml_parts.append(f'          <triangle v1="{t[0]}" v2="{t[1]}" v3="{t[2]}" />')
        xml_parts.append('        </triangles>')
        xml_parts.append('      </mesh>')
        xml_parts.append('    </object>')
        
    assembly_id = len(parts) + 1
    xml_parts.append(f'    <object id="{assembly_id}" name="TissueBoxCover" type="model">')
    xml_parts.append('      <components>')
    for oid in obj_ids:
        xml_parts.append(f'        <component objectid="{oid}" />')
    xml_parts.append('      </components>')
    xml_parts.append('    </object>')
    
    xml_parts.append('  </resources>')
    xml_parts.append('  <build>')
    xml_parts.append(f'    <item objectid="{assembly_id}" />')
    xml_parts.append('  </build>')
    xml_parts.append('</model>')
    
    model_xml = '\n'.join(xml_parts)
    
    content_types = """<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml" />
  <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml" />
</Types>"""

    rels = """<?xml version="1.0" encoding="utf-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel" Target="/3D/3dmodel.model" Id="rel0" />
</Relationships>"""

    with zipfile.ZipFile(output_3mf_path, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', content_types)
        z.writestr('_rels/.rels', rels)
        z.writestr('3D/3dmodel.model', model_xml)

def main():
    if len(sys.argv) < 4 or (len(sys.argv) - 2) % 2 != 0:
        print("Usage: export_3mf.py <output.3mf> <part1_name> <part1.stl> [<part2_name> <part2.stl> ...]")
        sys.exit(1)
        
    output_path = sys.argv[1]
    parts = []
    
    for i in range(2, len(sys.argv), 2):
        name = sys.argv[i]
        path = sys.argv[i+1]
        print(f"Reading {name} from {path}...")
        verts, tris = parse_stl(path)
        print(f"  -> {len(verts)} vertices, {len(tris)} triangles")
        parts.append((name, verts, tris))
        
    print(f"Writing multi-part 3MF to {output_path}...")
    create_multipart_3mf(parts, output_path)
    print(f"Done! {output_path} ({os.path.getsize(output_path)} bytes)")

if __name__ == '__main__':
    main()
