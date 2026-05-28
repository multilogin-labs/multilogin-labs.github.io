#!/usr/bin/env python3
"""Report stale indexable content by last modified time."""
from __future__ import annotations

from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "CONTENT-FRESHNESS.md"


def is_redirect(path: Path) -> bool:
    text = path.read_text(encoding="utf-8", errors="replace")
    return 'http-equiv="refresh"' in text.lower()


def section(path: Path) -> str:
    rel = path.parent.relative_to(ROOT).as_posix()
    if rel.startswith("guides"):
        return "guides"
    if rel.startswith("tools"):
        return "tools"
    if rel.startswith("compare"):
        return "compare"
    if rel.startswith("promo"):
        return "promo"
    return "other"


def main() -> int:
    rows: list[tuple[str, int, str]] = []
    for html in sorted(ROOT.rglob("index.html")):
        if ".git" in html.parts or html == ROOT / "index.html" or is_redirect(html):
            continue
        rel = html.parent.relative_to(ROOT).as_posix()
        url = "https://multilogin-labs.github.io/" if rel == "." else f"https://multilogin-labs.github.io/{rel}/"
        days = (date.today() - date.fromtimestamp(html.stat().st_mtime)).days
        rows.append((url, days, section(html)))

    stale30 = sorted([r for r in rows if r[1] > 30], key=lambda x: (-x[1], x[0]))
    stale60 = [r for r in rows if r[1] > 60]
    stale90 = [r for r in rows if r[1] > 90]

    lines = [
        "# Content Freshness",
        "",
        f"Updated: {date.today().isoformat()}",
        "",
        "## Snapshot",
        "",
        f"- Indexable HTML pages tracked: **{len(rows)}**",
        f"- Stale >30 days: **{len(stale30)}**",
        f"- Stale >60 days: **{len(stale60)}**",
        f"- Stale >90 days: **{len(stale90)}**",
        "",
        "## Stale Pages (>30 days)",
        "",
    ]
    lines.extend([f"- {u} — {d} days ({s})" for u, d, s in stale30[:120]] or ["- None"])
    lines.extend(
        [
            "",
            "## Refresh SLA",
            "",
            "- Tools and procurement pages: refresh if >30 days.",
            "- Guides and compare pages: refresh if >45 days.",
            "- Benchmark reports: monthly release cadence.",
            "",
        ]
    )
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
