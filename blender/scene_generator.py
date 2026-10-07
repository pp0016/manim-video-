"""Procedural 3D Typography Engine for Blender (bpy).

Generates high-end kinetic 3D typography scenes featuring:
- Procedural beveled text curves with dual hierarchy
- Advanced PBR materials (Gold Metallic, Neon Cyan Emission, Obsidian Floor)
- 4-point studio lighting rig with dynamic moving glint light
- 75mm camera rig with Track-To constraint and Depth of Field (DoF) bokeh
- Keyframed overshoot easing curves
- Floating geometric accent particles with rotational drift
- Cycles CPU engine optimization with OpenImageDenoise (OIDN)
- Full CLI argument parsing for headless matrix rendering
"""

import sys
import math
import argparse
import bpy


def parse_args(args=None):
    """Parse CLI arguments supporting both Blender native flags and script-specific args."""
    if args is None:
        args = sys.argv

    config = {
        "start": 1,
        "end": 60,
        "output": "//output/frame_#####",
        "samples": 32,
        "text1": "KABHI NOTICE KIYA?",
        "text2": "TRUST & RESPECT",
        "render": False,
    }

    # 1. Scan sys.argv for flags passed directly to Blender
    i = 0
    n = len(args)
    while i < n:
        arg = args[i]
        if arg in ("-s", "--frame-start", "--start"):
            if i + 1 < n and not args[i + 1].startswith("-"):
                config["start"] = int(args[i + 1])
                i += 1
        elif arg in ("-e", "--frame-end", "--end"):
            if i + 1 < n and not args[i + 1].startswith("-"):
                config["end"] = int(args[i + 1])
                i += 1
        elif arg in ("-o", "--render-output", "--output"):
            if i + 1 < n and not args[i + 1].startswith("-"):
                config["output"] = args[i + 1]
                i += 1
        elif arg == "--samples":
            if i + 1 < n and not args[i + 1].startswith("-"):
                config["samples"] = int(args[i + 1])
                i += 1
        elif arg == "--text1":
            if i + 1 < n:
                config["text1"] = args[i + 1]
                i += 1
        elif arg == "--text2":
            if i + 1 < n:
                config["text2"] = args[i + 1]
                i += 1
        elif arg == "--render":
            config["render"] = True
        i += 1

    # 2. If '--' separator is present, allow explicit trailing arguments to override
    if "--" in args:
        sub_args = args[args.index("--") + 1:]
        parser = argparse.ArgumentParser(description="Procedural 3D Typography Engine")
        parser.add_argument("-s", "--start", type=int, default=config["start"])
        parser.add_argument("-e", "--end", type=int, default=config["end"])
        parser.add_argument("-o", "--output", type=str, default=config["output"])
        parser.add_argument("--samples", type=int, default=config["samples"])
        parser.add_argument("--text1", type=str, default=config["text1"])
        parser.add_argument("--text2", type=str, default=config["text2"])
        parser.add_argument("--render", action="store_true", default=config["render"])

        parsed, _ = parser.parse_known_args(sub_args)
        config["start"] = parsed.start
        config["end"] = parsed.end
        config["output"] = parsed.output
        config["samples"] = parsed.samples
        config["text1"] = parsed.text1
        config["text2"] = parsed.text2
        config["render"] = parsed.render

    return config


def set_socket_value(node, socket_name, value):
    """Safely set a socket value on a shader node across Blender versions."""
    if socket_name in node.inputs:
        node.inputs[socket_name].default_value = value
    elif socket_name == "Specular" and "Specular IOR Level" in node.inputs:
        node.inputs["Specular IOR Level"].default_value = value
    elif socket_name == "Emission Color" and "Emission" in node.inputs:
        node.inputs["Emission"].default_value = value


def get_all_fcurves(obj):
    """Extract all fcurves across Blender 3.x/4.x (legacy) and Blender 5.x (layered/slotted actions)."""
    fcurves = []
    if not obj.animation_data or not obj.animation_data.action:
        return fcurves
    action = obj.animation_data.action
    if hasattr(action, "fcurves") and action.fcurves is not None:
        fcurves.extend(action.fcurves)
    if hasattr(action, "layers"):
        for layer in action.layers:
            if hasattr(layer, "strips"):
                for strip in layer.strips:
                    if hasattr(strip, "channelbags"):
                        for bag in strip.channelbags:
                            if hasattr(bag, "fcurves"):
                                fcurves.extend(bag.fcurves)
    return fcurves


def configure_engine_and_color_management(scene, config):
    """Configure Cycles CPU rendering, denoising, sampling, and AgX/Filmic color management."""
    # Engine & Device
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.render.threads_mode = 'AUTO'

    # Performance & Geometry Caching
    scene.render.use_persistent_data = True

    # Sampling & Adaptive Thresholds
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.adaptive_threshold = 0.05
    scene.cycles.samples = config.get("samples", 32)

    # Intel OpenImageDenoise
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = 'OPENIMAGEDENOISE'

    # Clamped Ray Bounces
    scene.cycles.max_bounces = 4
    scene.cycles.diffuse_bounces = 2
    scene.cycles.glossy_bounces = 2
    scene.cycles.transmission_bounces = 2
    scene.cycles.volume_bounces = 0
    scene.cycles.transparent_max_bounces = 8

    # Resolution & Output Settings
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.fps = 30
    scene.frame_start = config.get("start", 1)
    scene.frame_end = config.get("end", 60)
    scene.render.filepath = config.get("output", "//output/frame_#####")

    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.image_settings.color_depth = '8'
    scene.render.image_settings.compression = 15

    # Color Management (AgX if available, fallback to Filmic)
    try:
        view_transforms = [
            item.identifier for item in scene.view_settings.bl_rna.properties['view_transform'].enum_items
        ]
        if 'AgX' in view_transforms:
            scene.view_settings.view_transform = 'AgX'
            scene.view_settings.look = 'Punchy'
        elif 'Filmic' in view_transforms:
            scene.view_settings.view_transform = 'Filmic'
            scene.view_settings.look = 'Medium High Contrast'
    except Exception as e:
        print(f"Color management config note: {e}")


def create_procedural_materials():
    """Create advanced procedural materials: Gold Metallic, Neon Cyan Glow, Obsidian Floor, Particle Luminescence."""
    materials = {}

    def ensure_node_tree(mat):
        if hasattr(mat, "node_tree") and mat.node_tree is None:
            try:
                mat.use_nodes = True
            except Exception:
                pass
        return mat

    # 1. Pro Gold Metallic Material
    mat_gold = ensure_node_tree(bpy.data.materials.new("ProGoldMetal"))
    bsdf_gold = mat_gold.node_tree.nodes.get("Principled BSDF") if mat_gold.node_tree else None
    if bsdf_gold:
        set_socket_value(bsdf_gold, "Base Color", (1.0, 0.72, 0.18, 1.0))
        set_socket_value(bsdf_gold, "Metallic", 0.95)
        set_socket_value(bsdf_gold, "Roughness", 0.22)
        set_socket_value(bsdf_gold, "IOR", 1.45)
        set_socket_value(bsdf_gold, "Specular", 0.5)
    materials["gold"] = mat_gold

    # 2. Pro Neon Cyan Glow Material
    mat_glow = ensure_node_tree(bpy.data.materials.new("ProCyanGlow"))
    bsdf_glow = mat_glow.node_tree.nodes.get("Principled BSDF") if mat_glow.node_tree else None
    if bsdf_glow:
        set_socket_value(bsdf_glow, "Base Color", (0.0, 0.85, 1.0, 1.0))
        set_socket_value(bsdf_glow, "Emission Color", (0.0, 0.85, 1.0, 1.0))
        set_socket_value(bsdf_glow, "Emission Strength", 8.0)
        set_socket_value(bsdf_glow, "Metallic", 0.10)
        set_socket_value(bsdf_glow, "Roughness", 0.15)
    materials["glow"] = mat_glow

    # 3. Reflective Obsidian Floor Material
    mat_floor = ensure_node_tree(bpy.data.materials.new("ObsidianFloor"))
    bsdf_floor = mat_floor.node_tree.nodes.get("Principled BSDF") if mat_floor.node_tree else None
    if bsdf_floor:
        set_socket_value(bsdf_floor, "Base Color", (0.015, 0.015, 0.02, 1.0))
        set_socket_value(bsdf_floor, "Metallic", 0.85)
        set_socket_value(bsdf_floor, "Roughness", 0.28)
        set_socket_value(bsdf_floor, "Specular", 0.60)
    materials["floor"] = mat_floor

    # 4. Floating Particle Luminescence
    mat_particle = ensure_node_tree(bpy.data.materials.new("ParticleGlow"))
    bsdf_part = mat_particle.node_tree.nodes.get("Principled BSDF") if mat_particle.node_tree else None
    if bsdf_part:
        set_socket_value(bsdf_part, "Base Color", (0.0, 0.90, 1.0, 1.0))
        set_socket_value(bsdf_part, "Emission Color", (0.0, 0.90, 1.0, 1.0))
        set_socket_value(bsdf_part, "Emission Strength", 12.0)
    materials["particle"] = mat_particle

    return materials


def create_typography(text1, text2, materials):
    """Create dual hierarchy 3D typography with beveled curves and overshoot kinetic animation."""
    # Line 1: Hook Question ("KABHI NOTICE KIYA?")
    curve_l1 = bpy.data.curves.new("TextCurveL1", type='FONT')
    curve_l1.body = text1
    curve_l1.size = 0.9
    curve_l1.extrude = 0.12
    curve_l1.bevel_depth = 0.025
    curve_l1.bevel_resolution = 4
    curve_l1.align_x = 'CENTER'
    curve_l1.align_y = 'CENTER'
    curve_l1.space_character = 1.05

    obj_l1 = bpy.data.objects.new("ObjTextL1", curve_l1)
    bpy.context.collection.objects.link(obj_l1)
    obj_l1.data.materials.append(materials["gold"])
    obj_l1.location = (0.0, 0.0, 0.8)

    # Line 2: Hook Impact Keyword ("TRUST & RESPECT")
    curve_l2 = bpy.data.curves.new("TextCurveL2", type='FONT')
    curve_l2.body = text2
    curve_l2.size = 1.3
    curve_l2.extrude = 0.16
    curve_l2.bevel_depth = 0.035
    curve_l2.bevel_resolution = 4
    curve_l2.align_x = 'CENTER'
    curve_l2.align_y = 'CENTER'
    curve_l2.space_character = 1.05

    obj_l2 = bpy.data.objects.new("ObjTextL2", curve_l2)
    bpy.context.collection.objects.link(obj_l2)
    obj_l2.data.materials.append(materials["glow"])
    obj_l2.location = (0.0, 0.0, -0.6)

    # Keyframed Kinetic Overshoot Animation
    # Line 1: Scale entry with +8% overshoot
    obj_l1.scale = (0.001, 0.001, 0.001)
    obj_l1.keyframe_insert("scale", frame=1)
    obj_l1.scale = (1.08, 1.08, 1.08)
    obj_l1.keyframe_insert("scale", frame=18)
    obj_l1.scale = (1.0, 1.0, 1.0)
    obj_l1.keyframe_insert("scale", frame=24)

    # Line 2: Staggered entry with +10% overshoot
    obj_l2.scale = (0.001, 0.001, 0.001)
    obj_l2.keyframe_insert("scale", frame=15)
    obj_l2.scale = (1.10, 1.10, 1.10)
    obj_l2.keyframe_insert("scale", frame=32)
    obj_l2.scale = (1.0, 1.0, 1.0)
    obj_l2.keyframe_insert("scale", frame=38)

    # Set interpolation curves to BEZIER
    for obj in (obj_l1, obj_l2):
        for fcurve in get_all_fcurves(obj):
            for kp in fcurve.keyframe_points:
                kp.interpolation = 'BEZIER'

    return obj_l1, obj_l2


def create_reflective_floor(materials):
    """Create reflective obsidian floor backdrop quad plane."""
    plane_data = bpy.data.meshes.new("FloorMesh")
    verts = [(-25.0, -25.0, -1.8), (25.0, -25.0, -1.8), (25.0, 25.0, -1.8), (-25.0, 25.0, -1.8)]
    faces = [(0, 1, 2, 3)]
    plane_data.from_pydata(verts, [], faces)
    plane_data.update()

    floor_obj = bpy.data.objects.new("FloorObj", plane_data)
    bpy.context.collection.objects.link(floor_obj)
    floor_obj.data.materials.append(materials["floor"])
    return floor_obj


def create_floating_particles(materials, end_frame=60):
    """Create floating geometric octahedron accent particles with rotational tumble and z-drift."""
    particle_coords = [
        (-4.5, -1.0, 1.8),
        (-3.2, 0.5, -0.8),
        (4.2, -0.5, 1.2),
        (3.8, 0.8, -1.0),
        (-2.0, -1.5, 2.2),
        (2.5, -1.2, 2.0),
    ]

    particles = []
    for idx, (px, py, pz) in enumerate(particle_coords):
        mesh_p = bpy.data.meshes.new(f"ParticleMesh_{idx}")
        # 3D diamond (octahedron) geometry
        d_verts = [
            (0.0, 0.0, 0.14),
            (0.0, 0.0, -0.14),
            (0.10, 0.0, 0.0),
            (-0.10, 0.0, 0.0),
            (0.0, 0.10, 0.0),
            (0.0, -0.10, 0.0),
        ]
        d_faces = [
            (0, 2, 4), (0, 4, 3), (0, 3, 5), (0, 5, 2),
            (1, 4, 2), (1, 3, 4), (1, 5, 3), (1, 2, 5),
        ]
        mesh_p.from_pydata(d_verts, [], d_faces)
        mesh_p.update()

        p_obj = bpy.data.objects.new(f"ParticleObj_{idx}", mesh_p)
        bpy.context.collection.objects.link(p_obj)
        p_obj.data.materials.append(materials["particle"])
        p_obj.location = (px, py, pz)

        # Subtle location drift
        p_obj.keyframe_insert("location", frame=1)
        dx = 0.35 * (1 if idx % 2 == 0 else -1)
        p_obj.location = (px + dx, py, pz + 0.45)
        p_obj.keyframe_insert("location", frame=end_frame)

        # Rotational tumble
        p_obj.rotation_euler = (0.0, 0.0, 0.0)
        p_obj.keyframe_insert("rotation_euler", frame=1)
        p_obj.rotation_euler = (0.8 + idx * 0.1, 1.2 + idx * 0.15, 0.5 + idx * 0.2)
        p_obj.keyframe_insert("rotation_euler", frame=end_frame)

        particles.append(p_obj)

    return particles


def create_studio_lighting_rig(end_frame=60):
    """Create 4-point studio lighting rig with animated sweeping glint light."""
    lights = {}

    # 1. Warm Soft Key Light
    key_l = bpy.data.lights.new("KeyLight", type='AREA')
    key_l.energy = 900.0
    key_l.size = 4.0
    key_l.color = (1.0, 0.94, 0.82)
    key_obj = bpy.data.objects.new("KeyObj", key_l)
    key_obj.location = (4.5, -5.5, 4.0)
    key_obj.rotation_euler = (0.9, 0.3, 0.6)
    bpy.context.collection.objects.link(key_obj)
    lights["key"] = key_obj

    # 2. Cool Ambient Fill Light
    fill_l = bpy.data.lights.new("FillLight", type='AREA')
    fill_l.energy = 300.0
    fill_l.size = 6.0
    fill_l.color = (0.7, 0.85, 1.0)
    fill_obj = bpy.data.objects.new("FillObj", fill_l)
    fill_obj.location = (-5.5, -5.0, 2.5)
    fill_obj.rotation_euler = (1.0, -0.3, -0.8)
    bpy.context.collection.objects.link(fill_obj)
    lights["fill"] = fill_obj

    # 3. Vibrant Neon Cyan Rim Kicker Light
    rim_l = bpy.data.lights.new("RimLight", type='AREA')
    rim_l.energy = 1400.0
    rim_l.size = 6.0
    rim_l.color = (0.0, 0.85, 1.0)
    rim_obj = bpy.data.objects.new("RimObj", rim_l)
    rim_obj.location = (-3.0, 4.0, 2.5)
    rim_obj.rotation_euler = (-1.1, 0.4, 3.0)
    bpy.context.collection.objects.link(rim_obj)
    lights["rim"] = rim_obj

    # 4. Animated Sweeping Glint / Accent Light
    sweep_l = bpy.data.lights.new("SweepLight", type='POINT')
    sweep_l.energy = 600.0
    sweep_l.color = (1.0, 0.9, 0.7)
    sweep_obj = bpy.data.objects.new("SweepObj", sweep_l)
    bpy.context.collection.objects.link(sweep_obj)

    sweep_start = max(1, min(20, end_frame - 10))
    sweep_end = max(sweep_start + 1, min(50, end_frame))
    sweep_obj.location = (-6.0, -2.0, 0.8)
    sweep_obj.keyframe_insert("location", frame=sweep_start)
    sweep_obj.location = (6.0, -2.0, 0.8)
    sweep_obj.keyframe_insert("location", frame=sweep_end)
    lights["sweep"] = sweep_obj

    return lights


def create_cinematic_camera_rig(scene, end_frame=60):
    """Create 75mm cinematic camera with DoF bokeh, Track-To constraint, and dolly push-in animation."""
    # Focus target
    cam_target = bpy.data.objects.new("CameraTarget", None)
    cam_target.location = (0.0, 0.0, 0.1)
    bpy.context.collection.objects.link(cam_target)

    # Camera optics
    cam_data = bpy.data.cameras.new("CinemaCamera")
    cam_data.lens = 75.0  # Telephoto compression
    cam_data.dof.use_dof = True
    cam_data.dof.focus_object = cam_target
    cam_data.dof.aperture_fstop = 2.2  # Shallow depth of field

    cam_obj = bpy.data.objects.new("CinemaCameraObj", cam_data)
    cam_obj.location = (0.8, -8.5, 1.8)
    bpy.context.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    # Track to target
    track = cam_obj.constraints.new(type='TRACK_TO')
    track.target = cam_target
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'

    # Camera Dolly Push-in Animation
    cam_obj.keyframe_insert("location", frame=1)
    cam_obj.location = (0.0, -6.8, 1.1)
    cam_obj.keyframe_insert("location", frame=end_frame)

    return cam_obj, cam_target


def build_scene(config=None):
    """Procedurally build the complete 3D typography motion graphics scene."""
    if config is None:
        config = parse_args()

    # Reset to factory empty scene
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene

    # 1. Engine & Output Configuration
    configure_engine_and_color_management(scene, config)

    # 2. Materials
    materials = create_procedural_materials()

    # 3. Typography
    obj_l1, obj_l2 = create_typography(
        config.get("text1", "KABHI NOTICE KIYA?"),
        config.get("text2", "TRUST & RESPECT"),
        materials,
    )

    # 4. Reflective Floor
    floor_obj = create_reflective_floor(materials)

    # 5. Floating Accent Particles
    particles = create_floating_particles(materials, end_frame=config.get("end", 60))

    # 6. Four-Point Lighting Rig
    lights = create_studio_lighting_rig(end_frame=config.get("end", 60))

    # 7. Cinematic Camera Rig
    cam_obj, cam_target = create_cinematic_camera_rig(scene, end_frame=config.get("end", 60))

    print(
        f"Procedural 3D Scene successfully built: "
        f"L1='{config.get('text1')}', L2='{config.get('text2')}', "
        f"Frames={config.get('start')}-{config.get('end')}, "
        f"Samples={config.get('samples')}, Output='{scene.render.filepath}'"
    )

    return scene


def main():
    """Main execution entrypoint for headless Blender scripting."""
    config = parse_args()
    scene = build_scene(config)

    # If --render was explicitly requested and not invoked via Blender CLI flags (-f or -a)
    has_blender_render_flag = any(f in sys.argv for f in ("-f", "-a", "--render-frame", "--render-anim"))
    if config.get("render", False) and not has_blender_render_flag:
        print(f"Triggering render from Python: frames {scene.frame_start} to {scene.frame_end}...")
        bpy.ops.render.render(animation=True)
        print("Render finished.")


if __name__ == "__main__":
    main()
