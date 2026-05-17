#!/usr/bin/env python3
"""Download Webflow CDN images referenced in data/work.csv into images/work/.

Rewrites the CSV in place so image fields point at local files. Safe to re-run:
images that already exist locally are skipped.
"""

import csv
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "data" / "work.csv"
IMG_DIR = ROOT / "images" / "work"

IMAGE_FIELDS = (
    "Grid Image",
    "Full bleed image",
    "Image Block (1 column)",
    "Image block 1 (2 column)",
    "Image Block 1.1 (2 column)",
    "Image block 2 (2 column)",
)

WEBFLOW_HOST = "uploads-ssl.webflow.com"


def local_filename(slug: str, field: str, url: str) -> str:
    """Build a stable local filename: <slug>__<field-tag>__<original-name>."""
    path = urllib.parse.urlparse(url).path
    original = urllib.parse.unquote(path.rsplit("/", 1)[-1])
    # Tag the field so files don't collide across roles.
    field_tag = {
        "Grid Image": "grid",
        "Full bleed image": "full",
        "Image Block (1 column)": "block1col",
        "Image block 1 (2 column)": "block2col-a",
        "Image Block 1.1 (2 column)": "block2col-b",
        "Image block 2 (2 column)": "block2col-c",
    }[field]
    # Strip the Webflow hash prefix (e.g. "63d09852b378db14cd091bd0_") for readability.
    original = re.sub(r"^[0-9a-f]{20,}_", "", original)
    safe = re.sub(r"[^A-Za-z0-9._-]+", "-", original).strip("-")
    return f"{slug}__{field_tag}__{safe}"


def download(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp, dest.open("wb") as out:
        out.write(resp.read())


def main() -> int:
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    with CSV_PATH.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    downloaded = 0
    skipped = 0
    failed = []

    for row in rows:
        for field in IMAGE_FIELDS:
            url = (row.get(field) or "").strip()
            if not url or WEBFLOW_HOST not in url:
                continue
            fname = local_filename(row["Slug"], field, url)
            dest = IMG_DIR / fname
            if dest.exists():
                skipped += 1
            else:
                try:
                    download(url, dest)
                    downloaded += 1
                    print(f"  ↓ {fname}")
                except Exception as e:
                    failed.append((url, str(e)))
                    print(f"  ✗ {fname}: {e}", file=sys.stderr)
                    continue
            row[field] = f"images/work/{fname}"

    with CSV_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nDone. downloaded={downloaded} skipped={skipped} failed={len(failed)}")
    if failed:
        for u, err in failed:
            print(f"  - {u}: {err}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
