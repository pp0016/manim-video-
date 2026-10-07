# 3D Motion Graphics Quality Calibration Baseline Specification

## 1. Executive Summary & Calibration Objective
This document defines the production-grade quality calibration baseline for procedural 3D motion graphics generated headlessly via Blender's Python API (`bpy`). The target application is high-retention cinematic typography for an audiobook hook ("How to Win Friends and Influence People"), engineered to match the aesthetic standards of broadcast title sequences, Apple product keynotes, and leading 3D motion design studios.

The baseline establishes mathematically precise specifications across typography geometry, procedural shader networks, 4-point studio lighting, optical camera simulation, kinetic overshoot easing, and Cycles CPU cloud rendering optimization.

---

## 2. Benchmark References & Motion Graphics Standards
To transcend rudimentary 3D extrusion, this calibration synthesizes proven techniques from open-source Blender motion graphic frameworks and studio production standards:
1. **Geometric Bevel Weighting**: Sharp 90-degree 3D text edges fail in raytraced rendering because they lack surface area to catch specular highlights. Curvature calibration requires multi-segment round bevels (`bevel_depth` 0.025–0.035, `bevel_resolution` $\ge 4$) to create realistic chamfered edge glints.
2. **Micro-Facet Specular Shading**: Dual-material contrast pairing high-reflectivity dielectric/metallic surfaces (Gold $I_R \approx 0.95$, Roughness 0.22) with intense high-energy emission accents (Neon Cyan $8.0$–$12.0\text{ W/m}^2$) to establish immediate visual hierarchy.
3. **Telephoto Focal Compression**: Wide-angle lenses (24mm–35mm) cause barrel distortion that warps typographic letterforms. Calibrated motion graphics use a 75mm–85mm telephoto focal length to flatten perspective, enforce orthogonal elegance, and isolate the subject with shallow depth of field.
4. **Physical Studio Lighting Rigs**: Synthetic ambient lighting produces flat, muddy visuals. A 4-point lighting system with distinct color temperatures (warm key, cool fill, vibrant rim, sweeping accent) introduces rich contrast and edge separation.
5. **Kinetic Overshoot Dynamics**: Linear or default cubic interpolation feels robotic. Professional motion design employs anticipation and overshoot damping ($108\% \to 100\%$) mimicking physical mass and elastic tension.

---

## 3. Typography Geometric Calibration

### 3.1 Curve Generation & Bevel Architecture
Procedural text in Blender is represented by 2D vector spline curves evaluated into 3D manifold meshes.
- **Line 1 (Hook Question)**:
  - Text: `"KABHI NOTICE KIYA?"`
  - Font Size: `0.9` Blender units
  - Extrusion: `0.12` Blender units
  - Bevel Depth: `0.025` Blender units
  - Bevel Resolution: `4` segments (yields 8 polygonal subdivisions along the chamfer)
  - Alignment: Horizontal `CENTER`, Vertical `CENTER`
  - World Position: Centered at $(0, 0, 0.8)$
- **Line 2 (Hook Impact Keyword)**:
  - Text: `"TRUST & RESPECT"`
  - Font Size: `1.3` Blender units ($1.44\times$ hierarchy ratio relative to Line 1)
  - Extrusion: `0.16` Blender units
  - Bevel Depth: `0.035` Blender units
  - Bevel Resolution: `4` segments
  - Alignment: Horizontal `CENTER`, Vertical `CENTER`
  - World Position: Centered at $(0, 0, -0.6)$

### 3.2 Spacing & Kerning Calibration
- Character spacing is calibrated to `1.05` to avoid clipping between adjacent extruded letterforms when beveled.
- Shear is set to `0.0` for structural stability.

---

## 4. Shading & Material Calibration (Principled BSDF v2)

All shaders are defined procedurally via Blender's node tree API (`bpy.types.ShaderNodeTree`) to eliminate external image texture dependencies.

### 4.1 Master Material 1: Pro Gold Metallic (`ProGoldMetal`)
Employed on Line 1 typography to impart prestige, weight, and metallic sheen.
- **Shader Node**: `Principled BSDF`
- **Base Color**: $\text{RGB}(1.0, 0.72, 0.18)$ with Alpha $1.0$ (Calibrated 24K gold spectrum)
- **Metallic**: $0.95$ (Near-total conductor conduction)
- **Roughness**: $0.22$ (Micro-polished surface providing sharp specular highlights with gentle falloff)
- **IOR**: $1.45$ (Standard physical refractive index)
- **Specular**: $0.5$

### 4.2 Master Material 2: Pro Neon Cyan Glow (`ProCyanGlow`)
Employed on Line 2 typography to draw immediate viewer focus with high-energy luminance.
- **Shader Node**: `Principled BSDF`
- **Base Color**: $\text{RGB}(0.0, 0.85, 1.0)$ with Alpha $1.0$ (Vibrant electric cyan)
- **Emission Color**: $\text{RGB}(0.0, 0.85, 1.0)$
- **Emission Strength**: $8.0$ (Calibrated for Cycles ray emission onto floor and camera sensor)
- **Roughness**: $0.15$
- **Metallic**: $0.10$

### 4.3 Master Material 3: Reflective Obsidian Ground (`ObsidianFloor`)
Employed on the infinity floor plane ($40\times 40$ units) located at $Z = -1.8$.
- **Shader Node**: `Principled BSDF`
- **Base Color**: $\text{RGB}(0.015, 0.015, 0.020)$ with Alpha $1.0$ (Deep basalt/obsidian tone)
- **Metallic**: $0.85$ (Simulates dark coated polished stone)
- **Roughness**: $0.28$ (Diffuses typography reflections without becoming mirror-sharp)
- **Specular**: $0.60$

### 4.4 Master Material 4: Kinetic Particle Luminescence (`ParticleGlow`)
Employed on geometric accent floating diamonds.
- **Shader Node**: `Principled BSDF`
- **Base Color / Emission Color**: $\text{RGB}(0.0, 0.90, 1.0)$
- **Emission Strength**: $12.0$ (Produces localized point-source glints and specular reflections)

---

## 5. Color Management & Dynamic Range Calibration

Blender 4.0+ and 5.x default to modern Academy Color Encoding System (ACES) and OpenColorIO AgX transformations:
- **View Transform**: `AgX` (Wide dynamic range preventing color clipping in high-emission cyan areas) with fallback to `Filmic`.
- **Look**: `Punchy` for AgX, or `Medium High Contrast` for Filmic.
- **Exposure**: `0.0`
- **Gamma**: `1.0`
- **Color Space**: `sRGB` display device.

---

## 6. Four-Point Studio Lighting Rig Specification

Lighting is designed to produce 3-dimensional contouring, separation from dark background, and an active sweeping light glint across the beveled text.

```
                   [Back / -Y, +Z]
                   
           (Cyan Rim Kicker)
           Energy: 1400W Area
           (-3.0, 4.0, 2.5)
                   \
                    \
       [Line 1]  [Line 2]  <--- Sweep Light (Animated Glint)
                    /           Frame 20 (-6.0, -2.0, 0.8) -> Frame 50 (+6.0, -2.0, 0.8)
                   /
   (Cool Fill Light)          (Warm Key Light)
   Energy: 300W Area          Energy: 900W Area
   (-5.5, -5.0, 2.5)          (4.5, -5.5, 4.0)
                   
                   [Front Camera]
```

1. **Key Light (`KeyLight`)**:
   - Type: `AREA`, Shape: Square, Size: $4.0\text{ m}$
   - Energy: $900.0\text{ W}$
   - Color: $\text{RGB}(1.0, 0.94, 0.82)$ (Warm 3200K tungsten studio warmth)
   - Location: $(4.5, -5.5, 4.0)$, Rotation: $(0.90, 0.30, 0.60)$ rad
2. **Fill Light (`FillLight`)**:
   - Type: `AREA`, Shape: Square, Size: $6.0\text{ m}$
   - Energy: $300.0\text{ W}$ ($3:1$ Key-to-Fill ratio)
   - Color: $\text{RGB}(0.70, 0.85, 1.00)$ (Cool 6500K ambient daylight fill)
   - Location: $(-5.5, -5.0, 2.5)$, Rotation: $(1.00, -0.30, -0.80)$ rad
3. **Rim Kicker Light (`RimLight`)**:
   - Type: `AREA`, Shape: Rectangle, Size: $6.0\text{ m}$
   - Energy: $1400.0\text{ W}$ (High-intensity contour backlight)
   - Color: $\text{RGB}(0.0, 0.85, 1.0)$ (Neon cyan rim accent)
   - Location: $(-3.0, 4.0, 2.5)$, Rotation: $(-1.10, 0.40, 3.00)$ rad
4. **Moving Sweep / Glint Light (`SweepLight`)**:
   - Type: `POINT`
   - Energy: $600.0\text{ W}$
   - Color: $\text{RGB}(1.0, 0.90, 0.70)$ (Golden glint)
   - Animation: Keyframed translation across the typography bevels:
     - Frame 20: Location $(-6.0, -2.0, 0.8)$
     - Frame 50: Location $(+6.0, -2.0, 0.8)$

---

## 7. Optical Camera Physics & Cinematography Calibration

- **Focal Length**: $75.0\text{ mm}$ (Telephoto optical compression creates geometric authority)
- **Sensor Size**: $36.0\text{ mm}$ (Full frame $35\text{mm}$ standard)
- **Target Tracking**: Dedicated empty tracking target `CameraTarget` positioned at $(0, 0, 0.1)$.
- **Constraint**: `TRACK_TO` constraint with `TRACK_NEGATIVE_Z` and `UP_Y`.
- **Depth of Field (DoF)**:
  - Enabled: `cam.dof.use_dof = True`
  - Focus Target: `CameraTarget`
  - Aperture F-Stop: $f/2.2$ (Shallow depth of field producing cinematic foreground/background bokeh)
- **Dolly Push-in Animation**:
  - Frame 1: Location $(0.8, -8.5, 1.8)$ (Offset perspective)
  - Frame 60 (or Frame End): Location $(0.0, -6.8, 1.1)$ (Smooth optical glide closing distance by $\sim 20\%$)

---

## 8. Kinetic Motion & Overshoot Easing Curves

Professional kinetic typography demands spring-like overshoot easing. 

### 8.1 Line 1 Animation (Frames 1–24)
- Frame 1: Scale $(0.001, 0.001, 0.001)$ (Hidden)
- Frame 18: Scale $(1.08, 1.08, 1.08)$ ($+8\%$ Overshoot peak)
- Frame 24: Scale $(1.00, 1.00, 1.00)$ (Settled equilibrium)

### 8.2 Line 2 Animation (Frames 15–38)
Staggered by 15 frames to establish visual pacing:
- Frame 15: Scale $(0.001, 0.001, 0.001)$ (Hidden)
- Frame 32: Scale $(1.10, 1.10, 1.10)$ ($+10\%$ Overshoot peak)
- Frame 38: Scale $(1.00, 1.00, 1.00)$ (Settled equilibrium)

### 8.3 Accent Particles Drift & Tumble (Frames 1–60+)
Six 3D geometric octahedrons/diamonds distributed symmetrically:
- Initial positions spread across $X \in [-4.5, 4.2]$, $Y \in [-1.5, 0.8]$, $Z \in [-1.0, 2.2]$
- Keyframed location drift: $\Delta X = \pm 0.3$, $\Delta Z = +0.4$
- Keyframed rotation tumble: Euler $(0, 0, 0) \to (0.8, 1.2, 0.5)$ rad across duration.

---

## 9. Cycles CPU Engine & Cloud Render Optimization

To run deterministically on headless GitHub Actions runners without physical GPUs:
- **Engine**: `CYCLES`
- **Device**: `CPU`
- **Threads**: `AUTO` (Maximizes multi-core utilization)
- **Adaptive Sampling**:
  - `use_adaptive_sampling = True`
  - `adaptive_threshold = 0.05` (Stops sampling noise-free pixels early)
  - `samples = 32` (or 64 for final master)
- **Denoising**:
  - `use_denoising = True`
  - `denoiser = 'OPENIMAGEDENOISE'` (Intel OIDN operates natively on CPU SIMD instructions)
- **Light Bounces (Clamped Ray Depth)**:
  - Total Max Bounces: $4$
  - Diffuse Bounces: $2$
  - Glossy Bounces: $2$
  - Transmission Bounces: $2$
  - Volume Bounces: $0$
  - Transparent Bounces: $8$
- **Memory & BVH Caching**:
  - `use_persistent_data = True` (Retains scene BVH structure between animation frames, saving 25–35% CPU frame setup time)
- **Output Standard**: Lossless 8-bit PNG RGBA @ 1920x1080, 30.0 fps.
