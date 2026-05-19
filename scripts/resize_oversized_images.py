#!/usr/bin/env python3
"""Resize images wider than MAX_WIDTH down to MAX_WIDTH in place.

Originals are backed up to images/_originals/<relative_path> so the operation
is reversible. After resizing, re-run scripts/build_work.py so the width/height
stamped on <img> tags matches the new pixel dimensions.

Why: oversized PNGs (e.g. 6160x3196) decode into ~75MB of bitmap RAM each,
which crashes iOS Safari tabs once a few accumulate on one page.
"""

import shutil
import struct
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
IMAGES = REPO / "images"
BACKUP = IMAGES / "_originals"
MAX_WIDTH = 2000


def png_dims(path: Path):
    try:
        with open(path, "rb") as f:
            header = f.read(24)
        if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
            return None
        return struct.unpack(">II", header[16:24])
    except (OSError, struct.error):
        return None


def jpeg_dims(path: Path):
    try:
        with open(path, "rb") as f:
            data = f.read()
        i = 2
        while i < len(data):
            while i < len(data) and data[i] != 0xFF:
                i += 1
            while i < len(data) and data[i] == 0xFF:
                i += 1
            if i >= len(data):
                return None
            marker = data[i]
            i += 1
            if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
                i += 3
                h = struct.unpack(">H", data[i : i + 2])[0]
                w = struct.unpack(">H", data[i + 2 : i + 4])[0]
                return (w, h)
            seg_len = struct.unpack(">H", data[i : i + 2])[0]
            i += seg_len
        return None
    except (OSError, struct.error):
        return None


def main():
    if not IMAGES.exists():
        print(f"no images dir at {IMAGES}", file=sys.stderr)
        return 1

    BACKUP.mkdir(parents=True, exist_ok=True)

    candidates = []
    for path in IMAGES.rglob("*"):
        if not path.is_file():
            continue
        if BACKUP in path.parents:
            continue
        suffix = path.suffix.lower()
        if suffix == ".png":
            dims = png_dims(path)
        elif suffix in (".jpg", ".jpeg"):
            dims = jpeg_dims(path)
        else:
            continue
        if not dims:
            continue
        w, h = dims
        if w > MAX_WIDTH:
            candidates.append((path, w, h))

    if not candidates:
        print("nothing to resize")
        return 0

    candidates.sort(key=lambda t: -t[1])
    print(f"resizing {len(candidates)} image(s) wider than {MAX_WIDTH}px:\n")

    for path, w, h in candidates:
        rel = path.relative_to(IMAGES)
        backup_path = BACKUP / rel
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        if not backup_path.exists():
            shutil.copy2(path, backup_path)

        new_h = round(h * MAX_WIDTH / w)
        print(f"  {w}x{h:<5} -> {MAX_WIDTH}x{new_h:<5}  {rel}")
        result = subprocess.run(
            ["sips", "--resampleWidth", str(MAX_WIDTH), str(path)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"    sips failed: {result.stderr.strip()}", file=sys.stderr)

    print(f"\noriginals backed up to {BACKUP.relative_to(REPO)}/")
    print("now run: python3 scripts/build_work.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
