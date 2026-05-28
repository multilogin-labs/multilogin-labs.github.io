#!/usr/bin/env python3
"""Sitewide OG card sanity audit.

Asserts every indexable HTML page has:
  - og:title, og:description, og:url, og:type
  - og:image with og:image:width + og:image:height
  - twitter:card = summary_large_image
  - og:image points to an asset that exists in repo (if same-origin)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {"scripts", "node_modules", ".git", "__pycache__"}
BASE = "https://multilogin-labs.github.io"

ROBOTS_A = re.compile(r'<meta\b(?=[^>]*\bname=["\']robots["\'])[^>]*\bcontent=["\']([^"\']+)["\']', re.I)
ROBOTS_B = re.compile(r'<meta\b(?=[^>]*\bcontent=["\']([^"\']+)["\'])[^>]*\bname=["\']robots["\']', re.I)


def _meta(tag_attr: str, key: str, text: str) -> str | None:
    """Find <meta {tag_attr}=key ... content=...>  (handles either order)."""
    a = re.search(
        rf'<meta\b(?=[^>]*\b{tag_attr}=["\']{re.escape(key)}["\'])[^>]*\bcontent=["\']([^"\']+)["\']',
        text,
        re.I,
    )
    if a:
        return a.group(1)
    b = re.search(
        rf'<meta\b(?=[^>]*\bcontent=["\']([^"\']+)["\'])[^>]*\b{tag_attr}=["\']{re.escape(key)}["\']',
        text,
        re.I,
    )
    return b.group(1) if b else None


def og(text: str, key: str) -> str | None:
    return _meta("property", key, text)


def name_meta(text: str, key: str) -> str | None:
    return _meta("name", key, text)


def is_indexable(text: str) -> bool:
    m = ROBOTS_A.search(text) or ROBOTS_B.search(text)
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


def url_for(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix().removesuffix("index.html").rstrip("/")
    return f"/{rel}/" if rel else "/"


def main() -> int:
    failures: list[str] = []
    audited = 0
    for path in iter_html():
        text = path.read_text(encoding="utf-8")
        if not is_indexable(text):
            continue
        audited += 1
        url = url_for(path)
        required = ("og:title", "og:description", "og:url", "og:type", "og:image")
        for k in required:
            if not og(text, k):
                failures.append(f"{url}: missing {k}")
        # twitter
        tw_card = name_meta(text, "twitter:card")
        if tw_card != "summary_large_image":
            failures.append(f"{url}: twitter:card != summary_large_image ({tw_card})")
        if not name_meta(text, "twitter:image"):
            failures.append(f"{url}: missing twitter:image")
        # og:image dimensions
        if og(text, "og:image") and not og(text, "og:image:width"):
            failures.append(f"{url}: og:image:width missing")
        if og(text, "og:image") and not og(text, "og:image:height"):
            failures.append(f"{url}: og:image:height missing")
        # og:image asset exists if same-origin
        og_img = og(text, "og:image")
        if og_img and og_img.startswith(BASE):
            rel_asset = og_img.removeprefix(BASE)
            asset = ROOT / rel_asset.lstrip("/")
            if not asset.exists():
                failures.append(f"{url}: og:image asset not found in repo: {rel_asset}")
    print(f"og_audit: indexable={audited} failures={len(failures)}")
    if failures:
        for f in failures[:30]:
            print(f"  FAIL {f}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
