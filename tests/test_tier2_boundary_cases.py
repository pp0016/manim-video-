"""Tier 2 Test Suite: Boundary and Corner Cases.

Verifies:
1. Single-frame render parameters (start=1, end=1).
2. Custom text strings (special characters, long text > 100 chars, Hindi/Hinglish unicode).
3. Low and high sampling limits (1 sample minimum, 64-128 samples).
4. Nested and relative output paths (//output/nested/..., ./custom_out/...).
5. Non-overlapping frame chunks parameter validation (boundary consistency, ceiling logic, gap/overlap detection).
"""

import os
import sys
import json
import unittest
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tests.test_helpers import (
    find_blender_binary,
    run_blender_script_eval,
    calculate_chunks_oracle,
    verify_chunks_invariants,
)

import unittest.mock
if "bpy" not in sys.modules:
    sys.modules["bpy"] = unittest.mock.MagicMock()

from blender.scene_generator import parse_args


class TestTier2BoundaryCases(unittest.TestCase):
    """Tier 2: Boundary, Corner Case, and Stress Tests."""

    @classmethod
    def setUpClass(cls):
        cls.blender_bin = find_blender_binary()
        if not cls.blender_bin:
            raise unittest.SkipTest("Blender binary not discovered on system.")

    def test_01_single_frame_parameters(self):
        """Verify boundary condition: single frame render (start=1, end=1, samples=1)."""
        args = ["blender", "-b", "-P", "scene_generator.py", "-s", "1", "-e", "1", "--samples", "1"]
        cfg = parse_args(args)
        self.assertEqual(cfg["start"], 1)
        self.assertEqual(cfg["end"], 1)
        self.assertEqual(cfg["samples"], 1)

        # Execute headless scene evaluation in Blender to verify scene limits
        script = """
import sys, json, bpy
sys.path.insert(0, '.')
import blender.scene_generator as sg

cfg = sg.parse_args(['--start', '1', '--end', '1', '--samples', '1'])
scene = sg.build_scene(cfg)
print('RESULT:' + json.dumps({
    'frame_start': scene.frame_start,
    'frame_end': scene.frame_end,
    'samples': scene.cycles.samples,
    'sweep_keyframes': len(bpy.data.objects['SweepObj'].animation_data.action.fcurves) if hasattr(bpy.data.objects['SweepObj'].animation_data.action, 'fcurves') else 1
}))
"""
        rc, out, err = run_blender_script_eval(script, blender_path=self.blender_bin, timeout=30, cwd=str(PROJECT_ROOT))
        self.assertEqual(rc, 0, f"Blender single-frame evaluation failed: {err}")
        self.assertIn("RESULT:", out)
        res = json.loads(out.split("RESULT:")[1].splitlines()[0])
        self.assertEqual(res["frame_start"], 1)
        self.assertEqual(res["frame_end"], 1)
        self.assertEqual(res["samples"], 1)

    def test_02_custom_text_special_characters(self):
        """Verify handling of special punctuation, ASCII symbols, and escape sequences."""
        special_text1 = "!@#$%^&*()_+-=[]{}|;':\",.<>?/~`"
        special_text2 = "QUOTES: \"Double\" & 'Single' / Backslash \\"

        args = ["blender", "--", "--text1", special_text1, "--text2", special_text2]
        cfg = parse_args(args)
        self.assertEqual(cfg["text1"], special_text1)
        self.assertEqual(cfg["text2"], special_text2)

        script = f"""
import sys, json, bpy
sys.path.insert(0, '.')
import blender.scene_generator as sg

cfg = sg.parse_args(['--', '--text1', {json.dumps(special_text1)}, '--text2', {json.dumps(special_text2)}])
scene = sg.build_scene(cfg)
c1 = bpy.data.curves.get('TextCurveL1')
c2 = bpy.data.curves.get('TextCurveL2')
print('RESULT:' + json.dumps({{'c1_body': c1.body, 'c2_body': c2.body}}))
"""
        rc, out, err = run_blender_script_eval(script, blender_path=self.blender_bin, timeout=30, cwd=str(PROJECT_ROOT))
        self.assertEqual(rc, 0, f"Special characters test failed: {err}")
        self.assertIn("RESULT:", out)
        res = json.loads(out.split("RESULT:")[1].splitlines()[0])
        self.assertEqual(res["c1_body"], special_text1)
        self.assertEqual(res["c2_body"], special_text2)

    def test_03_custom_text_long_strings(self):
        """Verify handling of long text strings (> 100 characters) without buffer overflow."""
        long_line1 = "THIS IS AN EXTREMELY LONG HOOK QUESTION DESIGNED TO TEST STRING BUFFER LIMITS AND TEXT CURVE BOUNDARIES ACCROSS 3D"
        long_line2 = "SECONDARY IMPACT STATEMENT WITH EXTENDED KERNING GEOMETRY AND ADVANCED PROCEDURAL BEVELING STRESS TESTING"

        script = f"""
import sys, json, bpy
sys.path.insert(0, '.')
import blender.scene_generator as sg

cfg = sg.parse_args(['--', '--text1', {json.dumps(long_line1)}, '--text2', {json.dumps(long_line2)}])
scene = sg.build_scene(cfg)
c1 = bpy.data.curves.get('TextCurveL1')
c2 = bpy.data.curves.get('TextCurveL2')
print('RESULT:' + json.dumps({{'c1_len': len(c1.body), 'c2_len': len(c2.body)}}))
"""
        rc, out, err = run_blender_script_eval(script, blender_path=self.blender_bin, timeout=30, cwd=str(PROJECT_ROOT))
        self.assertEqual(rc, 0, f"Long string test failed: {err}")
        self.assertIn("RESULT:", out)
        res = json.loads(out.split("RESULT:")[1].splitlines()[0])
        self.assertEqual(res["c1_len"], len(long_line1))
        self.assertEqual(res["c2_len"], len(long_line2))

    def test_04_custom_text_hindi_hinglish_unicode(self):
        """Verify support for Hindi Devanagari unicode script and Hinglish transliterations."""
        hindi_line1 = "क्या आपने कभी ध्यान दिया?"
        hinglish_line2 = "TRUST & RESPECT: भरोसा और सम्मान"

        script = f"""
import sys, json, bpy
sys.path.insert(0, '.')
import blender.scene_generator as sg

cfg = sg.parse_args(['--', '--text1', {json.dumps(hindi_line1)}, '--text2', {json.dumps(hinglish_line2)}])
scene = sg.build_scene(cfg)
c1 = bpy.data.curves.get('TextCurveL1')
c2 = bpy.data.curves.get('TextCurveL2')
print('RESULT:' + json.dumps({{'c1': c1.body, 'c2': c2.body}}))
"""
        rc, out, err = run_blender_script_eval(script, blender_path=self.blender_bin, timeout=30, cwd=str(PROJECT_ROOT))
        self.assertEqual(rc, 0, f"Hindi/Hinglish unicode test failed: {err}")
        self.assertIn("RESULT:", out)
        res = json.loads(out.split("RESULT:")[1].splitlines()[0])
        self.assertEqual(res["c1"], hindi_line1)
        self.assertEqual(res["c2"], hinglish_line2)

    def test_05_sampling_limits(self):
        """Verify low and high sampling limits (1 sample draft to 64-128 samples)."""
        # Low limit
        cfg_low = parse_args(["blender", "--samples", "1"])
        self.assertEqual(cfg_low["samples"], 1)

        # High limit
        cfg_high = parse_args(["blender", "--samples", "64"])
        self.assertEqual(cfg_high["samples"], 64)

        # Extreme limit
        cfg_extreme = parse_args(["blender", "--", "--samples", "128"])
        self.assertEqual(cfg_extreme["samples"], 128)

    def test_06_nested_and_relative_output_paths(self):
        """Verify nested and relative output template paths."""
        paths_to_test = [
            "//output/nested/subfolder/frame_#####",
            "./renders/custom/hook_#####",
            "output/batch_1/f_###",
        ]
        for p in paths_to_test:
            cfg = parse_args(["blender", "-o", p])
            self.assertEqual(cfg["output"], p)

    def test_07_chunk_boundary_coverage_and_invariants(self):
        """Verify mathematical invariants of chunk partitioning across varied workloads."""
        test_cases = [
            (120, 30),   # Exact divisible: 4 chunks
            (100, 30),   # Non-divisible: 4 chunks (30, 30, 30, 10)
            (1, 30),     # Single frame: 1 chunk
            (30, 30),    # Single exact chunk: 1 chunk
            (31, 30),    # Minimal remainder: 2 chunks (30, 1)
            (300, 50),   # Large workload: 6 chunks
            (7, 2),      # Small chunks: 4 chunks (2, 2, 2, 1)
        ]

        for total, chunk_sz in test_cases:
            chunks = calculate_chunks_oracle(total, chunk_sz)
            # Verify mathematical invariants: no gaps, no overlaps, starts at 1, ends at total
            self.assertTrue(
                verify_chunks_invariants(chunks, total),
                f"Invariant violation for total={total}, chunk_sz={chunk_sz}",
            )
            # Verify ceiling logic
            expected_num_chunks = -(-total // chunk_sz)  # integer ceiling division
            self.assertEqual(len(chunks), expected_num_chunks)

    def test_08_invalid_chunk_parameters(self):
        """Verify error handling on non-positive total_frames or chunk_size."""
        with self.assertRaises(ValueError):
            calculate_chunks_oracle(0, 30)

        with self.assertRaises(ValueError):
            calculate_chunks_oracle(-10, 30)

        with self.assertRaises(ValueError):
            calculate_chunks_oracle(100, 0)

        with self.assertRaises(ValueError):
            calculate_chunks_oracle(100, -5)


if __name__ == "__main__":
    unittest.main()
