#!/usr/bin/env python3
"""Inject favicon, manifest, and theme-color into all HTML heads."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKER = "<!-- mll-head -->"
BLOCK = """<!-- mll-head -->
<link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml"/>
<link rel="manifest" href="/site.webmanifest"/>
<meta name="theme-color" content="#2a9d8f"/>
"""


def patch(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        return False
    needle = '<meta content="width=device-width, initial-scale=1.0" name="viewport"/>'
    alt = '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
    if needle in text:
        text = text.replace(needle, needle + "\n" + BLOCK, 1)
    elif alt in text:
        text = text.replace(alt, alt + "\n" + BLOCK, 1)
    else:
        return False
    path.write_text(text, encoding="utf-8")
    return True


def main() -> None:
    n = 0
    for html in ROOT.rglob("*.html"):
        if ".git" in html.parts:
            continue
        if patch(html):
            n += 1
    print(f"Injected head block into {n} files")


if __name__ == "__main__":
    main()
