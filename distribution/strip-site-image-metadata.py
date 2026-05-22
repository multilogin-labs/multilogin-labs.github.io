from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError


RASTER_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".gif",
    ".bmp",
    ".tif",
    ".tiff",
    ".avif",
}


def clean_svg_metadata(path: Path) -> bool:
    raw = path.read_text(encoding="utf-8", errors="ignore")
    updated = re.sub(r"(?is)<!--.*?-->", "", raw)
    updated = re.sub(r"(?is)<metadata\\b[^>]*>.*?</metadata>", "", updated)
    if updated != raw:
        path.write_text(updated, encoding="utf-8")
        return True
    return False


def strip_raster_metadata(path: Path) -> None:
    ext = path.suffix.lower()
    with Image.open(path) as img:
        img.load()
        orientation = img.getexif().get(274)
        if orientation:
            img = ImageOps.exif_transpose(img)

        if ext in {".jpg", ".jpeg"}:
            if img.mode not in {"RGB", "L"}:
                img = img.convert("RGB")
            img.save(
                path,
                format="JPEG",
                quality=95,
                optimize=True,
                progressive=True,
            )
            return

        if ext == ".png":
            if img.mode == "P":
                img = img.convert("RGBA")
            img.save(path, format="PNG", optimize=True)
            return

        if ext == ".webp":
            img.save(path, format="WEBP", lossless=True, quality=100, method=6)
            return

        if ext == ".gif":
            if img.mode != "P":
                img = img.convert("P", palette=Image.ADAPTIVE)
            img.save(path, format="GIF", optimize=True)
            return

        if ext == ".bmp":
            img.save(path, format="BMP")
            return

        if ext in {".tif", ".tiff"}:
            img.save(path, format="TIFF", compression="tiff_lzw")
            return

        if ext == ".avif":
            img.save(path, format="AVIF", quality=100)
            return


def main() -> int:
    parser = argparse.ArgumentParser(description="Strip image metadata under a root folder.")
    parser.add_argument("--root", required=True, help="Root folder to process.")
    parser.add_argument(
        "--refresh-timestamps",
        action="store_true",
        help="Refresh LastWriteTime for all processed files.",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        print(f"error=root_not_found:{root}")
        return 1

    all_files = [p for p in root.rglob("*") if p.is_file()]
    image_files = [p for p in all_files if p.suffix.lower() in RASTER_EXTENSIONS or p.suffix.lower() == ".svg"]

    processed = 0
    failed = 0
    svg_cleaned = 0

    for file_path in image_files:
        try:
            ext = file_path.suffix.lower()
            if ext == ".svg":
                if clean_svg_metadata(file_path):
                    svg_cleaned += 1
            else:
                strip_raster_metadata(file_path)

            if args.refresh_timestamps:
                os.utime(file_path, None)

            processed += 1
        except (UnidentifiedImageError, OSError, ValueError) as exc:
            failed += 1
            print(f"failed={file_path}::{exc}")

    print(f"image_root={root}")
    print(f"files_total={len(image_files)}")
    print(f"files_processed={processed}")
    print(f"files_failed={failed}")
    print(f"svg_metadata_blocks_cleaned={svg_cleaned}")
    print(f"timestamps_refreshed={1 if args.refresh_timestamps else 0}")
    print("tool_used=python-pillow")
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    sys.exit(main())