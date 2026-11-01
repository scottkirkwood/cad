#!/usr/bin/env python3
"""
Unit tests for the parametric Kleenex box cover OpenSCAD model.
Verifies parsing, manifold geometry, and 3MF packaging.
"""

import os
import subprocess
import tempfile
import unittest
import zipfile

DIR = os.path.dirname(os.path.abspath(__file__))
SCAD_FILE = os.path.join(DIR, "tissue-paper.scad")

class TestKleenexBoxModel(unittest.TestCase):

    def test_file_exists(self):
        self.assertTrue(os.path.exists(SCAD_FILE))

    def test_compilation_all_patterns(self):
        patterns = ["none", "wave_vertical", "wave_horizontal"]
        for pat in patterns:
            with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
                cmd = [
                    "openscad", "-o", tmp.name,
                    "-D", f'pattern_type="{pat}"',
                    "-D", 'part="all"',
                    "--render=true",
                    SCAD_FILE
                ]
                res = subprocess.run(cmd, capture_output=True, text=True)
                self.assertEqual(res.returncode, 0, f"Failed rendering pattern: {pat}\n{res.stderr}")
                self.assertIn("Simple:        yes", res.stderr)

    def test_compilation_color_modes(self):
        for mode in ["cap", "inlay"]:
            with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
                cmd = [
                    "openscad", "-o", tmp.name,
                    "-D", f'color_mode="{mode}"',
                    "-D", 'part="preview"',
                    "--render=true",
                    SCAD_FILE
                ]
                res = subprocess.run(cmd, capture_output=True, text=True)
                self.assertEqual(res.returncode, 0, f"Failed rendering color mode: {mode}\n{res.stderr}")
                self.assertIn("Simple:        yes", res.stderr)

    def test_export_parts(self):
        for part in ["top", "sides"]:
            with tempfile.NamedTemporaryFile(suffix=".stl") as tmp:
                cmd = [
                    "openscad", "-o", tmp.name,
                    "-D", f'part="{part}"',
                    SCAD_FILE
                ]
                res = subprocess.run(cmd, capture_output=True, text=True)
                self.assertEqual(res.returncode, 0, f"Failed exporting part {part}")
                self.assertGreater(os.path.getsize(tmp.name), 1000)

    def test_3mf_packaging(self):
        dual_3mf = os.path.join(DIR, "tissue-paper-dual.3mf")
        self.assertTrue(os.path.exists(dual_3mf), "tissue-paper-dual.3mf does not exist")
        self.assertTrue(zipfile.is_zipfile(dual_3mf))
        with zipfile.ZipFile(dual_3mf, 'r') as z:
            names = z.namelist()
            self.assertIn("3D/3dmodel.model", names)
            self.assertIn("[Content_Types].xml", names)
            model_xml = z.read("3D/3dmodel.model").decode('utf-8')
            self.assertIn('name="Top"', model_xml)
            self.assertIn('name="Sides"', model_xml)
            self.assertIn('name="TissueBoxCover"', model_xml)

if __name__ == '__main__':
    unittest.main()
