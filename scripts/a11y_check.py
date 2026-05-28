#!/usr/bin/env python3
"""Sitewide a11y guard: alt text, single H1, skip link, lang attribute, robots."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {"scripts", "node_modules", ".git", "__pycache__"}

ROBOTS = re.compile(r'<meta[^>]+name="robots"[^>]+content="([^"]+)"', re.I)
HTML_LANG = re.compile(r'<html[^>]*\blang="', re.I)
SKIP_LINK = re.compile(r'class="skip-link"|class="[^"]*skip-link', re.I)
H1 = re.compile(r"<h1\b", re.I)
IMG = re.compile(r"<img\b[^>]*>", re.I)
ALT = re.compile(r"\balt=", re.I)


def is_indexable(text: str) -> bool:
    m = ROBOTS.search(text)
    if not m:
        return True
    return "noindex" not in m.group(1).lower()


def iter_html() -> list[Path]:
    out: list[Path] = []
    for p in ROOT.rglob("*.html"):
        rel = p.relative_to(ROOT)
        parts = set(rel.parts)
        if parts & SKIP_DIRS:
            continue
        out.append(p)
    return out


def main() -> int:
    failures: list[str] = []
    for path in iter_html():
        text = path.read_text(encoding="utf-8")
        if not is_indexable(text):
            continue
        rel = str(path.relative_to(ROOT))
        if not HTML_LANG.search(text):
            failures.append(f"{rel}: <html> missing lang=")
        h1_count = len(H1.findall(text))
        if h1_count == 0:
            failures.append(f"{rel}: no <h1>")
        elif h1_count > 1:
            failures.append(f"{rel}: multiple <h1> ({h1_count})")
        if not SKIP_LINK.search(text):
            failures.append(f"{rel}: missing .skip-link")
        for img in IMG.finditer(text):
            tag = img.group(0)
            if not ALT.search(tag):
                failures.append(f"{rel}: <img> missing alt — {tag[:90]}")
    if failures:
        print(f"a11y_check: {len(failures)} failure(s)", file=sys.stderr)
        for f in failures[:50]:
            print(f"  {f}", file=sys.stderr)
        return 1
    print("a11y_check: OK (lang, h1, skip-link, img alt)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
