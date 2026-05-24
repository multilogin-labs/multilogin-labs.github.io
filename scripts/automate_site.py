#!/usr/bin/env python3
"""One-shot automation: maintenance + llms.txt + affiliate funnel (skips homepage)."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOMEPAGE = ROOT / "index.html"
SNAPSHOT_BEFORE = ""


def run(cmd: list[str]) -> int:
    print(f"\n==> {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=ROOT).returncode


def homepage_fingerprint() -> str:
    head = HOMEPAGE.read_text(encoding="utf-8").split("</head>", 1)[0]
    return (
        f"home.css={'home.css' in head}|"
        f"home.js={'home.js' in HOMEPAGE.read_text(encoding='utf-8')}|"
        f"no_site_css={'site.css' not in head}"
    )


def main() -> int:
    global SNAPSHOT_BEFORE
    if not HOMEPAGE.exists():
        print("FAIL: index.html missing", file=sys.stderr)
        return 1
    SNAPSHOT_BEFORE = homepage_fingerprint()
    if "site.css" in SNAPSHOT_BEFORE.split("|")[2]:
        print("WARN: homepage already references site.css", file=sys.stderr)

    steps: list[list[str]] = [
        ["python3", "scripts/generate_llms_txt.py"],
        ["python3", "scripts/site_maintenance.py"],
        ["python3", "scripts/aff_funnel.py"],
    ]
    failed = False
    for cmd in steps:
        if run(cmd) != 0:
            failed = True

    after = homepage_fingerprint()
    if after != SNAPSHOT_BEFORE:
        print("FAIL: homepage changed during automation", file=sys.stderr)
        print(f"  before: {SNAPSHOT_BEFORE}", file=sys.stderr)
        print(f"  after:  {after}", file=sys.stderr)
        return 1

    if failed:
        return 1
    print("\nAutomate site OK (homepage fingerprint unchanged).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
