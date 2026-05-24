#!/usr/bin/env python3
"""Sitewide performance: remove render-blocking Google Fonts from HTML."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FONT_PRECONNECT = re.compile(
    r'\s*<link href="https://fonts\.googleapis\.com" rel="preconnect"/>\s*'
    r'<link crossorigin="" href="https://fonts\.gstatic\.com" rel="preconnect"/>\s*',
    re.I,
)
FONT_PRECONNECT_LOOSE = re.compile(
    r'\s*<link rel="preconnect" href="https://fonts\.googleapis\.com"[^>]*>\s*'
    r'<link rel="preconnect" href="https://fonts\.gstatic\.com"[^>]*>\s*',
    re.I,
)
FONT_CSS = re.compile(
    r'\s*<link href="https://fonts\.googleapis\.com/css2[^"]*" rel="stylesheet"/>\s*',
    re.I,
)
FONT_CSS_LOOSE = re.compile(
    r'\s*<link href="https://fonts\.googleapis\.com/css2[^"]*" rel="stylesheet"[^>]*>\s*',
    re.I,
)
KEYWORDS_META = re.compile(
    r'\s*<meta content="[^"]*" name="keywords"/>\s*',
    re.I,
)


def patch_html(path: Path) -> bool:
    raw = path.read_text(encoding="utf-8")
    new = FONT_PRECONNECT.sub("\n", raw)
    new = FONT_PRECONNECT_LOOSE.sub("\n", new)
    new = FONT_CSS.sub("\n", new)
    new = FONT_CSS_LOOSE.sub("\n", new)
    new = KEYWORDS_META.sub("\n", new)
    if new != raw:
        path.write_text(new, encoding="utf-8")
        return True
    return False


def main() -> None:
    n = 0
    for html in ROOT.rglob("*.html"):
        if ".git" in html.parts:
            continue
        if patch_html(html):
            n += 1
    print(f"Optimized {n} HTML files (fonts/keywords removed)")


if __name__ == "__main__":
    main()
