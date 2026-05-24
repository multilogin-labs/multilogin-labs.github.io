#!/usr/bin/env python3
"""Check internal root-relative links in HTML point to existing paths."""
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
HREF_RE = re.compile(r'''href=["']([^"']+)["']''', re.I)
SKIP_PREFIXES = ("http://", "https://", "mailto:", "tel:", "javascript:", "#")
SKIP_PATHS = {"/go/multilogin"}


def resolve(target: str) -> Path | None:
    parsed = urlparse(target)
    path = parsed.path
    if not path or path in SKIP_PATHS:
        return None
    if path.endswith("/"):
        candidate = ROOT / path.lstrip("/") / "index.html"
    else:
        candidate = ROOT / path.lstrip("/")
        if candidate.is_dir():
            candidate = candidate / "index.html"
    return candidate


def main() -> int:
    broken: list[str] = []
    for html in ROOT.rglob("*.html"):
        if ".git" in html.parts:
            continue
        text = html.read_text(encoding="utf-8", errors="replace")
        for href in HREF_RE.findall(text):
            if href.startswith(SKIP_PREFIXES):
                continue
            if href.startswith("//"):
                continue
            target = resolve(href.split("#")[0])
            if target is None:
                continue
            if not target.exists():
                broken.append(f"{html.relative_to(ROOT)} -> {href}")
    if broken:
        print("Broken internal links:", file=sys.stderr)
        for line in sorted(set(broken))[:50]:
            print(f"  {line}", file=sys.stderr)
        if len(broken) > 50:
            print(f"  ... and {len(broken) - 50} more", file=sys.stderr)
        return 1
    print(f"OK — checked HTML under {ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
