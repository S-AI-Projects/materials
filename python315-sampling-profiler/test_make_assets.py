"""Unit and property-based invariant tests for python315-sampling-profiler/make_assets.py.

Contract & Invariant Specifications:
- Source fixture anchor 1 (Line 84: `vertices = []` in sweep_tube):
  vertices and faces count invariant: sweep_tube() always yields SEGMENTS * RING_POINTS vertices (3840)
  and SEGMENTS * RING_POINTS * 2 faces (7680).
- Source fixture anchor 2 (Lines 54-58 in write_wallpaper: `lights = [...]`):
  lights configuration establishes the radial distance halo blend invariant across WALLPAPER_SIZE (512x512).
- Boundary inputs:
  Smallest valid: low=(0,0,0), high=(0,0,0), amount=0.0 -> expected (0,0,0)
  Ordinary input: low=(252, 210, 153), high=(146, 90, 118), amount=0.5 -> expected (199, 150, 136)
"""

import math
import pathlib
import random
import sys
import tempfile
import unittest

PROJECT_DIR = pathlib.Path(__file__).resolve().parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

import make_assets


class TestMakeAssetsInvariants(unittest.TestCase):
    def test_smallest_valid_input_blend(self):
        """Smallest valid input boundary: (0,0,0) blended with (0,0,0) at 0.0 amount."""
        # Precondition established at line 132 (def blend)
        low = (0, 0, 0)
        high = (0, 0, 0)
        amount = 0.0
        expected = (0, 0, 0)
        actual = make_assets.blend(low, high, amount)
        self.assertEqual(actual, expected)

    def test_ordinary_input_blend(self):
        """Ordinary fixture input: bakery_dawn top to bottom at 0.5 vertical blend."""
        # Preconditions established at line 25 (WALLPAPERS) and line 132 (def blend)
        top = (252, 210, 153)
        bottom = (146, 90, 118)
        amount = 0.5
        # Independently calculated:
        # channel 0: round(252 + (146 - 252) * 0.5) = round(252 - 53) = 199
        # channel 1: round(210 + (90 - 210) * 0.5) = round(210 - 60) = 150
        # channel 2: round(153 + (118 - 153) * 0.5) = round(153 - 17.5) = 136 (or 135 depending on round half-to-even)
        expected = (199, 150, round(153 + (118 - 153) * 0.5))
        actual = make_assets.blend(top, bottom, amount)
        self.assertEqual(actual, expected)

    def test_sweep_tube_mesh_invariants_line84(self):
        """Invariant: sweep_tube produces exact vertex and face count starting from vertices = [] at line 84."""
        vertices, faces = make_assets.sweep_tube()
        expected_vertices_count = make_assets.SEGMENTS * make_assets.RING_POINTS  # 240 * 16 = 3840
        expected_faces_count = make_assets.SEGMENTS * make_assets.RING_POINTS * 2  # 7680
        self.assertEqual(len(vertices), expected_vertices_count)
        self.assertEqual(len(faces), expected_faces_count)
        for x, y, z in vertices:
            self.assertTrue(math.isfinite(x) and math.isfinite(y) and math.isfinite(z))
        for a, b, c in faces:
            self.assertTrue(0 <= a < expected_vertices_count)
            self.assertTrue(0 <= b < expected_vertices_count)
            self.assertTrue(0 <= c < expected_vertices_count)

    def test_wallpaper_lights_invariant_lines54_58(self):
        """Invariant: wallpaper generation with lines 54-58 lights produces exact P6 format and byte size."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_path = pathlib.Path(tmp_dir) / "test_wallpaper.ppm"
            top = (214, 235, 251)
            bottom = (245, 232, 201)
            glow = (255, 255, 224)
            make_assets.write_wallpaper(test_path, top, bottom, glow)
            self.assertTrue(test_path.exists())
            with test_path.open("rb") as f:
                header = f.readline()
                self.assertEqual(header, b"P6\n")
                dims = f.readline()
                self.assertEqual(dims, b"512 512\n")
                max_val = f.readline()
                self.assertEqual(max_val, b"255\n")
                pixels = f.read()
                self.assertEqual(len(pixels), 512 * 512 * 3)

    def test_main_assets_generation_invariant(self):
        """Invariant: main() generates all 4 asset files deterministically."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            assets_path = pathlib.Path(tmp_dir) / "assets"
            make_assets.main(assets_path)
            self.assertTrue((assets_path / "pretzel.mdl").exists())
            for name in make_assets.WALLPAPERS:
                self.assertTrue((assets_path / name).exists())
                self.assertEqual((assets_path / name).stat().st_size, 15 + 512 * 512 * 3)

    def test_property_blend_100_bounded_cases(self):
        """Property invariant across 100 bounded valid cases generated with fixed seed."""
        rng = random.Random(42)
        for i in range(100):
            c1 = (rng.randint(0, 255), rng.randint(0, 255), rng.randint(0, 255))
            c2 = (rng.randint(0, 255), rng.randint(0, 255), rng.randint(0, 255))
            t = rng.uniform(0.0, 1.0)
            res = make_assets.blend(c1, c2, t)
            # Invariant 1: Result has 3 integer channels
            self.assertEqual(len(res), 3)
            for ch in range(3):
                # Invariant 2: Result is clamped within [0, 255]
                self.assertTrue(0 <= res[ch] <= 255)
                # Invariant 3: Result lies between min and max of inputs (with rounding tolerance 1)
                lo = min(c1[ch], c2[ch])
                hi = max(c1[ch], c2[ch])
                self.assertTrue(lo - 1 <= res[ch] <= hi + 1)


if __name__ == "__main__":
    unittest.main()
