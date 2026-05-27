#!/usr/bin/env python3
"""Sitewide perf patches for all HTML except homepage (index.html) and redirect stubs."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOMEPAGE = ROOT / "index.html"
BASE_CSS = "https://multilogin-labs.github.io/assets/css/site.css"
SPECULATION = (
    '<script type="speculationrules">'
    '{"prefetch":[{"source":"document","where":{"href_matches":"*multilogin.com/pricing*"},'
    '"eagerness":"moderate"}]}</script>'
)
ABS_SITE_CSS = re.compile(
    rf'<link href="{re.escape(BASE_CSS)}" rel="stylesheet"/>',
    re.I,
)
VIEWPORT_10 = re.compile(
    r'<meta content="width=device-width, initial-scale=1\.0" name="viewport"/>',
    re.I,
)
AFF_STICKY_OPEN = re.compile(
    r'<aside class="aff-sticky"(?! hidden)(\s+id="aff-sticky")',
    re.I,
)


def is_redirect(text: str) -> bool:
    return 'http-equiv="refresh"' in text.lower()


def is_skipped(path: Path) -> bool:
    if path.resolve() == HOMEPAGE.resolve():
        return True
    rel = path.relative_to(ROOT).as_posix()
    if rel == "go/multilogin/index.html":
        return True
    return False


def patch_html(text: str) -> str:
    new = ABS_SITE_CSS.sub('<link href="/assets/css/site.css" rel="stylesheet"/>', text)
    new = VIEWPORT_10.sub(
        '<meta content="width=device-width, initial-scale=1" name="viewport"/>',
        new,
    )
    new = AFF_STICKY_OPEN.sub(r'<aside class="aff-sticky" hidden\1', new)
    if "multilogin.com/pricing" in new and "speculationrules" not in new:
        new = new.replace("</body>", f"{SPECULATION}\n</body>", 1)
    return new


def patch_file(path: Path) -> bool:
    raw = path.read_text(encoding="utf-8")
    if is_redirect(raw):
        return False
    new = patch_html(raw)
    if new != raw:
        path.write_text(new, encoding="utf-8")
        return True
    return False


def main() -> None:
    n = 0
    for html in sorted(ROOT.rglob("*.html")):
        if ".git" in html.parts or is_skipped(html):
            continue
        if patch_file(html):
            n += 1
    # Guard: homepage must never be written by this script
    assert HOMEPAGE.read_text(encoding="utf-8"), "homepage missing"
    print(f"Optimized {n} inner pages (homepage untouched)")


if __name__ == "__main__":
    main()
