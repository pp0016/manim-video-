"""Test Helpers and Verification Utilities.

Provides discovery, execution, binary validation, and mathematical oracles
for testing Blender procedural 3D typography and parallel render farm pipelines.
"""

import os
import sys
import math
import shutil
import struct
import json
import tempfile
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple


def find_blender_binary() -> Optional[str]:
    """Discover local Blender executable across standard installation paths."""
    # 1. Environment variable override
    env_blender = os.environ.get("BLENDER_PATH")
    if env_blender and os.path.isfile(env_blender):
        return env_blender

    # 2. Known Windows installations
    candidates = [
        r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe",
    ]
    for candidate in candidates:
        if os.path.isfile(candidate):
            return candidate

    # 3. System PATH
    on_path = shutil.which("blender")
    if on_path:
        return on_path

    return None


def get_blender_version(blender_path: Optional[str] = None) -> Optional[str]:
    """Retrieve the version string of the discovered Blender executable."""
    if blender_path is None:
        blender_path = find_blender_binary()
    if not blender_path:
        return None

    try:
        proc = subprocess.run(
            [blender_path, "--version"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
            check=False,
        )
        for line in proc.stdout.splitlines():
            if "Blender" in line:
                return line.strip()
    except Exception:
        pass
    return None


def find_ffmpeg_binary() -> Optional[str]:
    """Discover FFmpeg executable on system PATH."""
    return shutil.which("ffmpeg")


def find_ffprobe_binary() -> Optional[str]:
    """Discover FFprobe executable on system PATH."""
    return shutil.which("ffprobe")


def run_blender_script_eval(
    python_script_body: str,
    blender_path: Optional[str] = None,
    timeout: int = 60,
    cwd: Optional[str] = None,
) -> Tuple[int, str, str]:
    """Execute arbitrary Python code headlessly inside Blender via a temporary script.
    
    Avoids Windows cmd/powershell quote escaping issues.
    """
    if blender_path is None:
        blender_path = find_blender_binary()
    if not blender_path:
        raise FileNotFoundError("Blender executable not found on system.")

    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as f:
        f.write(python_script_body)
        temp_script = f.name

    try:
        cmd = [blender_path, "-b", "-P", temp_script]
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            cwd=cwd,
            check=False,
        )
        return proc.returncode, proc.stdout, proc.stderr
    finally:
        try:
            os.remove(temp_script)
        except OSError:
            pass


def validate_png_header(file_path: str) -> Dict[str, Any]:
    """Inspect low-level binary PNG signature and parse the IHDR chunk.
    
    Returns parsed metadata dictionary or raises ValueError on corruption.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"PNG file not found: {file_path}")

    with open(file_path, "rb") as f:
        header = f.read(33)

    if len(header) < 33:
        raise ValueError(f"File too short to be a valid PNG: {len(header)} bytes")

    # 1. Magic byte signature: 0x89 50 4E 47 0D 0A 1A 0A
    expected_magic = b"\x89PNG\r\n\x1a\n"
    if header[:8] != expected_magic:
        raise ValueError(f"Invalid PNG magic signature: {header[:8]!r}")

    # 2. IHDR Chunk Length & Type
    ihdr_len = struct.unpack(">I", header[8:12])[0]
    ihdr_type = header[12:16]
    if ihdr_type != b"IHDR" or ihdr_len != 13:
        raise ValueError(f"Corrupted IHDR header: type={ihdr_type!r}, len={ihdr_len}")

    # 3. IHDR Fields (Big-Endian unsigned)
    width, height = struct.unpack(">II", header[16:24])
    bit_depth = header[24]
    color_type = header[25]
    compression = header[26]
    filter_method = header[27]
    interlace = header[28]

    # Map color type to standard name
    color_type_names = {
        0: "Grayscale",
        2: "RGB",
        3: "Palette",
        4: "Grayscale+Alpha",
        6: "RGBA",
    }

    return {
        "valid_signature": True,
        "width": width,
        "height": height,
        "bit_depth": bit_depth,
        "color_type": color_type,
        "color_mode": color_type_names.get(color_type, f"Unknown({color_type})"),
        "compression": compression,
        "filter_method": filter_method,
        "interlace": interlace,
        "file_size": os.path.getsize(file_path),
    }


def validate_png_file(
    file_path: str,
    expected_width: int = 1920,
    expected_height: int = 1080,
    expected_mode: str = "RGBA",
    min_size_bytes: int = 500000,
) -> Dict[str, Any]:
    """Comprehensive PNG validation checking binary header, file size, and PIL decode."""
    meta = validate_png_header(file_path)

    if meta["file_size"] < min_size_bytes:
        raise ValueError(
            f"File size {meta['file_size']} bytes is less than expected minimum {min_size_bytes} bytes"
        )

    if meta["width"] != expected_width or meta["height"] != expected_height:
        raise ValueError(
            f"Dimensions mismatch: got ({meta['width']}, {meta['height']}), "
            f"expected ({expected_width}, {expected_height})"
        )

    if meta["color_mode"] != expected_mode:
        raise ValueError(
            f"Color mode mismatch: got {meta['color_mode']}, expected {expected_mode}"
        )

    # Optional cross-check with Pillow
    try:
        from PIL import Image

        with Image.open(file_path) as im:
            if im.size != (expected_width, expected_height):
                raise ValueError(f"PIL size mismatch: {im.size}")
            if im.format != "PNG":
                raise ValueError(f"PIL format mismatch: {im.format}")
            meta["pil_mode"] = im.mode
    except ImportError:
        pass

    return meta


def calculate_chunks_oracle(total_frames: int, chunk_size: int) -> List[Dict[str, Any]]:
    """Authoritative mathematical reference implementation for matrix chunk partitioning.
    
    Divides total_frames into sequential non-overlapping chunks with exact ceiling count.
    """
    if total_frames <= 0:
        raise ValueError(f"total_frames must be positive, got {total_frames}")
    if chunk_size <= 0:
        raise ValueError(f"chunk_size must be positive, got {chunk_size}")

    num_chunks = math.ceil(total_frames / chunk_size)
    chunks = []
    for i in range(num_chunks):
        start = i * chunk_size + 1
        end = min((i + 1) * chunk_size, total_frames)
        chunks.append({
            "id": f"{i:02d}",
            "start": start,
            "end": end,
            "count": end - start + 1,
        })
    return chunks


def verify_chunks_invariants(chunks: List[Dict[str, Any]], total_frames: int) -> bool:
    """Verify core mathematical invariants of a matrix chunk partitioning list:
    1. First chunk starts at 1
    2. Last chunk ends at total_frames
    3. No frame gaps between chunks (chunk[i].start == chunk[i-1].end + 1)
    4. No frame overlaps
    5. Sum of chunk counts equals total_frames
    """
    if not chunks:
        return total_frames == 0

    if chunks[0]["start"] != 1:
        raise AssertionError(f"First chunk must start at 1, got {chunks[0]['start']}")

    if chunks[-1]["end"] != total_frames:
        raise AssertionError(
            f"Last chunk must end at {total_frames}, got {chunks[-1]['end']}"
        )

    total_accounted = 0
    for idx, chunk in enumerate(chunks):
        start = chunk["start"]
        end = chunk["end"]
        count = chunk.get("count", end - start + 1)

        if start > end:
            raise AssertionError(f"Chunk {idx} has invalid range: start={start} > end={end}")

        if idx > 0:
            prev_end = chunks[idx - 1]["end"]
            if start != prev_end + 1:
                raise AssertionError(
                    f"Frame discontinuity at chunk {idx}: previous ended at {prev_end}, "
                    f"current starts at {start}"
                )

        total_accounted += (end - start + 1)

    if total_accounted != total_frames:
        raise AssertionError(
            f"Sum of frames ({total_accounted}) does not match total_frames ({total_frames})"
        )

    return True


def probe_video(video_path: str) -> Dict[str, Any]:
    """Execute ffprobe to extract stream, codec, resolution, and container metadata."""
    ffprobe_bin = find_ffprobe_binary()
    if not ffprobe_bin:
        raise FileNotFoundError("ffprobe not found on system PATH")

    cmd = [
        ffprobe_bin,
        "-v", "error",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        video_path,
    ]
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
        timeout=15,
    )
    return json.loads(proc.stdout)


def verify_video_faststart(video_path: str) -> bool:
    """Check whether the MP4 file has the 'moov' atom positioned before the 'mdat' atom.
    
    This verifies that '-movflags +faststart' was applied for progressive web streaming.
    """
    if not os.path.isfile(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    moov_pos = -1
    mdat_pos = -1

    with open(video_path, "rb") as f:
        offset = 0
        file_size = os.path.getsize(video_path)
        while offset < file_size - 8:
            f.seek(offset)
            size_bytes = f.read(4)
            type_bytes = f.read(4)
            if len(size_bytes) < 4 or len(type_bytes) < 4:
                break
            box_size = struct.unpack(">I", size_bytes)[0]
            box_type = type_bytes.decode("latin1", errors="ignore")

            if box_type == "moov" and moov_pos == -1:
                moov_pos = offset
            elif box_type == "mdat" and mdat_pos == -1:
                mdat_pos = offset

            if box_size == 1:  # 64-bit large size
                large_size_bytes = f.read(8)
                box_size = struct.unpack(">Q", large_size_bytes)[0]
            elif box_size == 0:  # Box extends to EOF
                break

            if box_size < 8:
                break
            offset += box_size

    # Faststart requires moov to appear before mdat
    if moov_pos != -1 and mdat_pos != -1:
        return moov_pos < mdat_pos
    return False
