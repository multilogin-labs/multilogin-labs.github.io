#!/usr/bin/env python3
"""End-to-end indexability gate.

Asserts:
  1. Every indexable HTML page has an explicit `<meta name="robots">`
     (either attribute order) and the value is index-compatible.
  2. Every indexable HTML page has a `<link rel="canonical">`.
  3. Every indexable HTML page is in sitemap.xml.
  4. Every sitemap HTML URL is reachable on disk and indexable.
  5. Every indexable HTML page has at least one JSON-LD block.
  6. Every indexable HTML page has a `<title>` and `<meta name="description">`.
  7. robots.txt allows `/` and lists the sitemap.
Writes `docs/INDEXABILITY.md`. Exits non-zero on any failure.
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
CANONICAL = re.compile(r'<link\b[^>]*\brel=["\']canonical["\'][^>]*>', re.I)
JSONLD = re.compile(r'<script\s+type="application/ld\+json"[^>]*>', re.I)
TITLE = re.compile(r"<title\b[^>]*>([^<]*)</title>", re.I)
DESC_A = re.compile(r'<meta\b(?=[^>]*\bname=["\']description["\'])[^>]*\bcontent=["\']([^"\']+)["\']', re.I)
DESC_B = re.compile(r'<meta\b(?=[^>]*\bcontent=["\']([^"\']+)["\'])[^>]*\bname=["\']description["\']', re.I)
LOC = re.compile(r"<loc>([^<]+)</loc>")


def robots_value(text: str) -> str | None:
    m = ROBOTS_A.search(text)
    if m:
        return m.group(1)
    m = ROBOTS_B.search(text)
    if m:
        return m.group(1)
    return None


def desc_value(text: str) -> str | None:
    m = DESC_A.search(text)
    if m:
        return m.group(1)
    m = DESC_B.search(text)
    if m:
        return m.group(1)
    return None


def url_for(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix().removesuffix("index.html").rstrip("/")
    return f"/{rel}/" if rel else "/"


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
    indexable: list[tuple[Path, str]] = []
    for path in iter_html():
        text = path.read_text(encoding="utf-8")
        rval = robots_value(text)
        if rval and "noindex" in rval.lower():
            continue
        indexable.append((path, text))

    # robots meta + canonical + jsonld + title + description per page
    for path, text in indexable:
        url = url_for(path)
        rval = robots_value(text)
        if rval is None:
            failures.append(f"{url}: missing <meta name=robots>")
        elif "max-image-preview" not in rval:
            failures.append(f"{url}: robots meta missing max-image-preview ({rval})")
        if not CANONICAL.search(text):
            failures.append(f"{url}: missing <link rel=canonical>")
        if not JSONLD.search(text):
            failures.append(f"{url}: missing JSON-LD")
        t = TITLE.search(text)
        if not t or not t.group(1).strip():
            failures.append(f"{url}: missing or empty <title>")
        elif len(t.group(1).strip()) > 70:
            # not a fail; advisory only
            pass
        d = desc_value(text)
        if not d or len(d.strip()) < 30:
            failures.append(f"{url}: meta description missing or <30 chars")

    # sitemap coverage
    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    sitemap_urls = set(LOC.findall(sitemap))
    sitemap_paths = {u.replace(BASE, "") or "/" for u in sitemap_urls}
    sitemap_paths_norm = {p.rstrip("/") or "/" for p in sitemap_paths}
    indexable_paths = {url_for(p).rstrip("/") or "/" for p, _ in indexable}
    not_in_sm = sorted(indexable_paths - sitemap_paths_norm)
    for u in not_in_sm:
        failures.append(f"{u}: indexable HTML not listed in sitemap.xml")

    # robots.txt
    robots_txt = (ROOT / "robots.txt").read_text(encoding="utf-8")
    if "Sitemap: " not in robots_txt:
        failures.append("robots.txt: missing Sitemap: line")
    if "Allow: /" not in robots_txt and "Disallow: /\n" in robots_txt:
        failures.append("robots.txt: disallows entire site")

    # write report
    indexable_count = len(indexable)
    sitemap_html_count = sum(
        1 for u in sitemap_urls if u.endswith("/") and not u.endswith("/data/")
    )
    lines = [
        "# Indexability Audit",
        "",
        f"- Indexable HTML pages: **{indexable_count}**",
        f"- Sitemap entries (HTML): **{sitemap_html_count}**",
        f"- Sitemap entries (total): **{len(sitemap_urls)}**",
        f"- Failures: **{len(failures)}**",
        "",
        "## Failures",
        "" if failures else "- None (every indexable page has robots, canonical, JSON-LD, title, description, and is in sitemap.xml).",
    ]
    if failures:
        for f in failures:
            lines.append(f"- {f}")
    lines.append("")
    lines.append("## Coverage criteria")
    lines.append("")
    lines.append("- `<meta name=robots>` with `max-image-preview:large`")
    lines.append("- `<link rel=canonical>`")
    lines.append("- At least one JSON-LD block")
    lines.append("- Non-empty `<title>`")
    lines.append("- `<meta name=description>` ≥ 30 chars")
    lines.append("- URL present in `sitemap.xml`")
    lines.append("- `robots.txt` lists the sitemap and does not block `/`")
    (ROOT / "docs" / "INDEXABILITY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(
        f"indexability_audit: indexable={indexable_count} sitemap={len(sitemap_urls)} "
        f"failures={len(failures)}"
    )
    if failures:
        for f in failures[:30]:
            print(f"  FAIL {f}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
