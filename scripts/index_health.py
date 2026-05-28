#!/usr/bin/env python3
"""Generate index coverage health report from sitemap + local files."""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://multilogin-labs.github.io"
SITEMAP = ROOT / "sitemap.xml"
OUT = ROOT / "docs" / "INDEX-HEALTH.md"
LOC_RE = re.compile(r"<loc>(.*?)</loc>")
HREF_RE = re.compile(r'''href=["']([^"']+)["']''', re.I)


def is_redirect(path: Path) -> bool:
    text = path.read_text(encoding="utf-8", errors="replace")
    return 'http-equiv="refresh"' in text.lower()


def to_url(path: Path) -> str:
    rel = path.parent.relative_to(ROOT).as_posix()
    return BASE + ("/" if rel == "." else f"/{rel}/")


def sitemap_urls() -> set[str]:
    text = SITEMAP.read_text(encoding="utf-8")
    return {m.group(1).strip() for m in LOC_RE.finditer(text)}


def indexable_html() -> list[Path]:
    out: list[Path] = []
    for html in sorted(ROOT.rglob("index.html")):
        if ".git" in html.parts or html == ROOT / "index.html" or is_redirect(html):
            continue
        out.append(html)
    return out


def normalized(href: str) -> str | None:
    if href.startswith(BASE):
        return href.split("#", 1)[0]
    if href.startswith("/"):
        h = href.split("#", 1)[0]
        if h.endswith(".json") or h.endswith(".xml") or h.endswith(".txt"):
            return BASE + h
        return BASE + (h if h.endswith("/") else h + "/")
    return None


def main() -> int:
    sitemap = sitemap_urls()
    files = indexable_html()
    urls = {to_url(f) for f in files}
    orphans = sorted(u for u in urls if u not in sitemap)

    inlinks = {u: 0 for u in urls}
    for html in files:
        seen: set[str] = set()
        text = html.read_text(encoding="utf-8", errors="replace")
        for href in HREF_RE.findall(text):
            u = normalized(href)
            if not u or u in seen or u not in inlinks:
                continue
            seen.add(u)
            inlinks[u] += 1
    low = sorted((u, c) for u, c in inlinks.items() if c < 2)

    lines = [
        "# Index Health Report",
        "",
        f"Updated: {date.today().isoformat()}",
        "",
        "## Snapshot",
        "",
        f"- Sitemap URLs: **{len(sitemap)}**",
        f"- Indexable HTML URLs: **{len(urls)}**",
        f"- Orphan indexable URLs: **{len(orphans)}**",
        f"- Low inlink URLs (<2): **{len(low)}**",
        "",
        "## Orphan Indexable URLs",
        "",
    ]
    lines.extend([f"- {u}" for u in orphans[:50]] or ["- None"])
    lines.extend(["", "## Low Inlink URLs", ""])
    lines.extend([f"- {u} — {c} inlinks" for u, c in low[:80]] or ["- None"])
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Redirect stubs and `/go/` hop are intentionally excluded.",
            "- Goal is full indexation of intentional URLs, not every file in repo.",
            "",
        ]
    )
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
