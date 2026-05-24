#!/usr/bin/env python3
"""Single entry point for all site maintenance (run before commit)."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

STEPS: list[tuple[str, list[str]]] = [
    ("Enhance pages (OG, breadcrumbs, dates)", ["python3", "scripts/enhance_pages.py"]),
    ("SEO optimize (redirects, sitemap, links)", ["python3", "scripts/seo_optimize.py"]),
    ("Validate datasets", ["python3", "scripts/validate_data.py"]),
    ("Check internal links", ["python3", "scripts/check_links.py"]),
    ("IndexNow key file", ["python3", "scripts/indexnow.py", "--ensure-key"]),
]


def main() -> int:
    import os

    os.chdir(ROOT)
    failed = False
    for label, cmd in STEPS:
        print(f"\n==> {label}")
        result = subprocess.run(cmd, cwd=ROOT)
        if result.returncode != 0:
            print(f"FAILED: {' '.join(cmd)}", file=sys.stderr)
            failed = True
    if failed:
        return 1
    print("\nAll maintenance steps OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
