"""Tier 1 Test Suite: Opaque-Box Feature Coverage.

Verifies:
1. Python syntax & compilation of blender/scene_generator.py.
2. CLI argument parsing (default configuration, standard flags, '--' overrides, mixed flags).
3. Procedural typography curves (Bevel, Extrude, Resolution, Spacing).
4. Procedural PBR materials (Principled BSDF node connections, Metallic, Roughness, Emission).
5. 4-point studio lighting rig (Key, Fill, Rim, Glint light sources).
6. Camera rig (75mm focal length, DoF f/2.2, Track-To constraint, Dolly push-in).
7. Cycles CPU engine settings (OIDN denoiser, adaptive sampling threshold 0.05, clamped bounces).
"""

import os
import sys
import json
import py_compile
import unittest
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tests.test_helpers import (
    find_blender_binary,
    get_blender_version,
    run_blender_script_eval,
)
import unittest.mock

# Allow importing parse_args in standard Python environments without native bpy
if "bpy" not in sys.modules:
    sys.modules["bpy"] = unittest.mock.MagicMock()

from blender.scene_generator import parse_args


class TestTier1FeatureCoverage(unittest.TestCase):
    """Tier 1: Feature Coverage and Interface Contract Tests."""

    @classmethod
    def setUpClass(cls):
        """Run a single headless Blender scene introspection pass to inspect live bpy state."""
        cls.blender_bin = find_blender_binary()
        if not cls.blender_bin:
            raise unittest.SkipTest("Blender binary not discovered on system.")

        introspection_script = """
import sys, json, bpy
sys.path.insert(0, '.')
import blender.scene_generator as sg

config = sg.parse_args(['--start', '1', '--end', '60', '--samples', '32'])
scene = sg.build_scene(config)

# 1. Curves Introspection
c1 = bpy.data.curves.get('TextCurveL1')
c2 = bpy.data.curves.get('TextCurveL2')
curves_data = {
    'l1': {
        'size': c1.size,
        'extrude': c1.extrude,
        'bevel_depth': c1.bevel_depth,
        'bevel_resolution': c1.bevel_resolution,
        'body': c1.body,
        'space_char': c1.space_character,
        'align_x': c1.align_x,
        'align_y': c1.align_y,
    },
    'l2': {
        'size': c2.size,
        'extrude': c2.extrude,
        'bevel_depth': c2.bevel_depth,
        'bevel_resolution': c2.bevel_resolution,
        'body': c2.body,
        'space_char': c2.space_character,
        'align_x': c2.align_x,
        'align_y': c2.align_y,
    }
}

# 2. Materials Introspection
def get_bsdf_inputs(mat_name):
    mat = bpy.data.materials.get(mat_name)
    if not mat or not mat.node_tree:
        return {}
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    if not bsdf:
        return {}
    res = {}
    for inp in bsdf.inputs:
        val = inp.default_value
        if hasattr(val, '__iter__'):
            val = list(val)
        res[inp.name] = val
    return res

materials_data = {
    'gold': get_bsdf_inputs('ProGoldMetal'),
    'glow': get_bsdf_inputs('ProCyanGlow'),
    'floor': get_bsdf_inputs('ObsidianFloor'),
    'particle': get_bsdf_inputs('ParticleGlow'),
}

# 3. Lights Introspection
lights_data = {}
for name in ['KeyLight', 'FillLight', 'RimLight', 'SweepLight']:
    l = bpy.data.lights.get(name)
    lights_data[name] = {
        'type': l.type,
        'energy': l.energy,
        'color': list(l.color),
    }

# 4. Camera & Constraints Introspection
cam = bpy.data.cameras.get('CinemaCamera')
cam_obj = bpy.data.objects.get('CinemaCameraObj')
track_constraint = None
if cam_obj:
    for c in cam_obj.constraints:
        if c.type == 'TRACK_TO':
            track_constraint = {
                'type': c.type,
                'target': c.target.name if c.target else None,
                'track_axis': c.track_axis,
                'up_axis': c.up_axis,
            }

cam_data = {
    'lens': cam.lens,
    'dof_enabled': cam.dof.use_dof,
    'fstop': cam.dof.aperture_fstop,
    'focus_target': cam.dof.focus_object.name if cam.dof.focus_object else None,
    'track_constraint': track_constraint,
}

# 5. Engine & Render Settings Introspection
engine_data = {
    'engine': scene.render.engine,
    'device': scene.cycles.device,
    'persistent_data': scene.render.use_persistent_data,
    'adaptive_sampling': scene.cycles.use_adaptive_sampling,
    'adaptive_threshold': scene.cycles.adaptive_threshold,
    'samples': scene.cycles.samples,
    'denoiser': scene.cycles.denoiser,
    'max_bounces': scene.cycles.max_bounces,
    'diffuse_bounces': scene.cycles.diffuse_bounces,
    'glossy_bounces': scene.cycles.glossy_bounces,
    'transmission_bounces': scene.cycles.transmission_bounces,
    'volume_bounces': scene.cycles.volume_bounces,
    'resolution': [scene.render.resolution_x, scene.render.resolution_y],
    'fps': scene.render.fps,
    'color_mode': scene.render.image_settings.color_mode,
    'file_format': scene.render.image_settings.file_format,
}

# 6. Objects in scene
objects_list = [o.name for o in scene.objects]

payload = {
    'curves': curves_data,
    'materials': materials_data,
    'lights': lights_data,
    'camera': cam_data,
    'engine': engine_data,
    'objects': objects_list,
}

print('===INTROSPECTION_START===')
print(json.dumps(payload))
print('===INTROSPECTION_END===')
"""
        rc, out, err = run_blender_script_eval(
            introspection_script, blender_path=cls.blender_bin, timeout=45, cwd=str(PROJECT_ROOT)
        )
        if rc != 0:
            raise RuntimeError(f"Headless Blender introspection failed (code {rc}):\n{err}\n{out}")

        start_tag = "===INTROSPECTION_START==="
        end_tag = "===INTROSPECTION_END==="
        if start_tag not in out or end_tag not in out:
            raise ValueError(f"Could not parse introspection tags from Blender output:\n{out}")

        json_text = out.split(start_tag)[1].split(end_tag)[0].strip()
        cls.bpy_state = json.loads(json_text)

    # -------------------------------------------------------------
    # 1. Compilation & Syntax
    # -------------------------------------------------------------
    def test_01_script_syntax_and_compilation(self):
        """Verify that blender/scene_generator.py compiles cleanly without syntax errors."""
        script_path = PROJECT_ROOT / "blender" / "scene_generator.py"
        self.assertTrue(script_path.is_file(), f"Script missing at {script_path}")
        try:
            py_compile.compile(str(script_path), doraise=True)
        except py_compile.PyCompileError as e:
            self.fail(f"Syntax compilation error in scene_generator.py: {e}")

    # -------------------------------------------------------------
    # 2. CLI Argument Parsing
    # -------------------------------------------------------------
    def test_02_cli_parsing_defaults(self):
        """Verify default configuration values when no CLI flags are supplied."""
        cfg = parse_args(["script.py"])
        self.assertEqual(cfg["start"], 1)
        self.assertEqual(cfg["end"], 60)
        self.assertEqual(cfg["output"], "//output/frame_#####")
        self.assertEqual(cfg["samples"], 32)
        self.assertEqual(cfg["text1"], "KABHI NOTICE KIYA?")
        self.assertEqual(cfg["text2"], "TRUST & RESPECT")
        self.assertFalse(cfg["render"])

    def test_03_cli_parsing_native_flags(self):
        """Verify standard native Blender CLI flags: -s, -e, -o, --samples, --render."""
        args = [
            "blender", "-b", "-P", "scene_generator.py",
            "-s", "10",
            "-e", "40",
            "-o", "//custom_out/f_###",
            "--samples", "16",
            "--text1", "HOOK QUESTION",
            "--text2", "BIG PUNCHLINE",
            "--render",
        ]
        cfg = parse_args(args)
        self.assertEqual(cfg["start"], 10)
        self.assertEqual(cfg["end"], 40)
        self.assertEqual(cfg["output"], "//custom_out/f_###")
        self.assertEqual(cfg["samples"], 16)
        self.assertEqual(cfg["text1"], "HOOK QUESTION")
        self.assertEqual(cfg["text2"], "BIG PUNCHLINE")
        self.assertTrue(cfg["render"])

    def test_04_cli_parsing_trailing_args_override(self):
        """Verify that arguments passed after '--' properly override preceding flags."""
        args = [
            "blender", "-b", "-P", "scene_generator.py",
            "-s", "5", "-e", "25",
            "--",
            "--start", "12",
            "--end", "48",
            "--output", "//override/path_#####",
            "--samples", "8",
            "--text1", "TRAIL LINE 1",
            "--text2", "TRAIL LINE 2",
        ]
        cfg = parse_args(args)
        self.assertEqual(cfg["start"], 12)
        self.assertEqual(cfg["end"], 48)
        self.assertEqual(cfg["output"], "//override/path_#####")
        self.assertEqual(cfg["samples"], 8)
        self.assertEqual(cfg["text1"], "TRAIL LINE 1")
        self.assertEqual(cfg["text2"], "TRAIL LINE 2")

    # -------------------------------------------------------------
    # 3. Procedural Typography Geometry & Curves
    # -------------------------------------------------------------
    def test_05_procedural_typography_curves(self):
        """Verify 3D curve parameters: bevel, extrusion, size, and character spacing."""
        c_data = self.bpy_state["curves"]

        # Line 1 Verification
        l1 = c_data["l1"]
        self.assertAlmostEqual(l1["size"], 0.9, places=2)
        self.assertAlmostEqual(l1["extrude"], 0.12, places=2)
        self.assertAlmostEqual(l1["bevel_depth"], 0.025, places=3)
        self.assertEqual(l1["bevel_resolution"], 4)
        self.assertAlmostEqual(l1["space_char"], 1.05, places=2)
        self.assertEqual(l1["align_x"], "CENTER")
        self.assertEqual(l1["align_y"], "CENTER")

        # Line 2 Verification
        l2 = c_data["l2"]
        self.assertAlmostEqual(l2["size"], 1.3, places=2)
        self.assertAlmostEqual(l2["extrude"], 0.16, places=2)
        self.assertAlmostEqual(l2["bevel_depth"], 0.035, places=3)
        self.assertEqual(l2["bevel_resolution"], 4)
        self.assertAlmostEqual(l2["space_char"], 1.05, places=2)
        self.assertEqual(l2["align_x"], "CENTER")
        self.assertEqual(l2["align_y"], "CENTER")

        # Check hierarchical scale ratio (Line 2 should be larger than Line 1)
        self.assertGreater(l2["size"], l1["size"])
        self.assertGreater(l2["extrude"], l1["extrude"])
        self.assertGreater(l2["bevel_depth"], l1["bevel_depth"])

    # -------------------------------------------------------------
    # 4. Procedural PBR Shaders & Materials
    # -------------------------------------------------------------
    def test_06_pbr_gold_metallic_material(self):
        """Verify ProGoldMetal Principled BSDF node parameters (Gold sheen)."""
        gold = self.bpy_state["materials"]["gold"]
        self.assertTrue(bool(gold), "ProGoldMetal Principled BSDF not found or empty")

        # Base Color: Warm 24K Gold (approx 1.0, 0.72, 0.18)
        color = gold.get("Base Color", [0, 0, 0, 1])
        self.assertAlmostEqual(color[0], 1.0, places=2)
        self.assertAlmostEqual(color[1], 0.72, places=2)
        self.assertAlmostEqual(color[2], 0.18, places=2)

        # Metallic: 0.95
        self.assertAlmostEqual(gold.get("Metallic", 0), 0.95, places=2)
        # Roughness: 0.22
        self.assertAlmostEqual(gold.get("Roughness", 0), 0.22, places=2)
        # IOR: 1.45
        self.assertAlmostEqual(gold.get("IOR", 0), 1.45, places=2)

    def test_07_pbr_neon_cyan_glow_material(self):
        """Verify ProCyanGlow Principled BSDF node parameters (High-energy emission)."""
        glow = self.bpy_state["materials"]["glow"]
        self.assertTrue(bool(glow), "ProCyanGlow Principled BSDF not found or empty")

        # Base Color: Vibrant Electric Cyan (0.0, 0.85, 1.0)
        color = glow.get("Base Color", [0, 0, 0, 1])
        self.assertAlmostEqual(color[0], 0.0, places=2)
        self.assertAlmostEqual(color[1], 0.85, places=2)
        self.assertAlmostEqual(color[2], 1.0, places=2)

        # Emission Strength: 8.0
        self.assertAlmostEqual(glow.get("Emission Strength", 0), 8.0, places=1)
        # Metallic: 0.10, Roughness: 0.15
        self.assertAlmostEqual(glow.get("Metallic", 0), 0.10, places=2)
        self.assertAlmostEqual(glow.get("Roughness", 0), 0.15, places=2)

    def test_08_pbr_reflective_floor_material(self):
        """Verify ObsidianFloor Principled BSDF node parameters (Reflective obsidian ground)."""
        floor = self.bpy_state["materials"]["floor"]
        self.assertTrue(bool(floor), "ObsidianFloor Principled BSDF not found or empty")

        self.assertAlmostEqual(floor.get("Metallic", 0), 0.85, places=2)
        self.assertAlmostEqual(floor.get("Roughness", 0), 0.28, places=2)

    def test_09_pbr_particle_glow_material(self):
        """Verify ParticleGlow Principled BSDF node parameters (Accent point glints)."""
        part = self.bpy_state["materials"]["particle"]
        self.assertTrue(bool(part), "ParticleGlow Principled BSDF not found or empty")
        self.assertAlmostEqual(part.get("Emission Strength", 0), 12.0, places=1)

    # -------------------------------------------------------------
    # 5. Four-Point Studio Lighting Rig
    # -------------------------------------------------------------
    def test_10_studio_lighting_rig(self):
        """Verify 4-point lighting system: Key (900W), Fill (300W), Rim (1400W), Sweep (600W)."""
        lights = self.bpy_state["lights"]

        # 1. Warm Key Light
        key = lights.get("KeyLight", {})
        self.assertEqual(key.get("type"), "AREA")
        self.assertAlmostEqual(key.get("energy"), 900.0, places=1)
        k_color = key.get("color", [0, 0, 0])
        self.assertAlmostEqual(k_color[0], 1.0, places=2)
        self.assertAlmostEqual(k_color[1], 0.94, places=2)
        self.assertAlmostEqual(k_color[2], 0.82, places=2)

        # 2. Cool Fill Light
        fill = lights.get("FillLight", {})
        self.assertEqual(fill.get("type"), "AREA")
        self.assertAlmostEqual(fill.get("energy"), 300.0, places=1)
        f_color = fill.get("color", [0, 0, 0])
        self.assertAlmostEqual(f_color[0], 0.70, places=2)
        self.assertAlmostEqual(f_color[1], 0.85, places=2)
        self.assertAlmostEqual(f_color[2], 1.00, places=2)

        # 3. Vibrant Neon Cyan Rim Kicker Light
        rim = lights.get("RimLight", {})
        self.assertEqual(rim.get("type"), "AREA")
        self.assertAlmostEqual(rim.get("energy"), 1400.0, places=1)
        r_color = rim.get("color", [0, 0, 0])
        self.assertAlmostEqual(r_color[0], 0.0, places=2)
        self.assertAlmostEqual(r_color[1], 0.85, places=2)
        self.assertAlmostEqual(r_color[2], 1.0, places=2)

        # 4. Animated Glint Sweep Light
        sweep = lights.get("SweepLight", {})
        self.assertEqual(sweep.get("type"), "POINT")
        self.assertAlmostEqual(sweep.get("energy"), 600.0, places=1)

    # -------------------------------------------------------------
    # 6. Cinematic Camera & Optics
    # -------------------------------------------------------------
    def test_11_cinematic_camera_rig(self):
        """Verify 75mm lens, DoF bokeh at f/2.2, and Track-To constraint."""
        cam = self.bpy_state["camera"]
        self.assertAlmostEqual(cam.get("lens"), 75.0, places=1)
        self.assertTrue(cam.get("dof_enabled"))
        self.assertAlmostEqual(cam.get("fstop"), 2.2, places=2)
        self.assertEqual(cam.get("focus_target"), "CameraTarget")

        track = cam.get("track_constraint")
        self.assertIsNotNone(track, "TRACK_TO constraint missing on CinemaCameraObj")
        self.assertEqual(track.get("target"), "CameraTarget")
        self.assertEqual(track.get("track_axis"), "TRACK_NEGATIVE_Z")
        self.assertEqual(track.get("up_axis"), "UP_Y")

    # -------------------------------------------------------------
    # 7. Cycles CPU Engine & Optimization
    # -------------------------------------------------------------
    def test_12_cycles_cpu_settings(self):
        """Verify Cycles CPU engine configuration, OIDN denoiser, and clamped bounces."""
        engine = self.bpy_state["engine"]
        self.assertEqual(engine.get("engine"), "CYCLES")
        self.assertEqual(engine.get("device"), "CPU")
        self.assertTrue(engine.get("persistent_data"))
        self.assertTrue(engine.get("adaptive_sampling"))
        self.assertAlmostEqual(engine.get("adaptive_threshold"), 0.05, places=3)
        self.assertEqual(engine.get("samples"), 32)
        self.assertEqual(engine.get("denoiser"), "OPENIMAGEDENOISE")

        # Clamped Ray Bounces
        self.assertEqual(engine.get("max_bounces"), 4)
        self.assertEqual(engine.get("diffuse_bounces"), 2)
        self.assertEqual(engine.get("glossy_bounces"), 2)
        self.assertEqual(engine.get("transmission_bounces"), 2)
        self.assertEqual(engine.get("volume_bounces"), 0)

        # Resolution & Output format
        self.assertEqual(engine.get("resolution"), [1920, 1080])
        self.assertEqual(engine.get("fps"), 30)
        self.assertEqual(engine.get("color_mode"), "RGBA")
        self.assertEqual(engine.get("file_format"), "PNG")


if __name__ == "__main__":
    unittest.main()
