#!/usr/bin/env python3
"""Build internal link graph summary for indexable pages."""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://multilogin-labs.github.io"
OUT = ROOT / "docs" / "INTERNAL-LINK-AUDIT.md"
HREF_RE = re.compile(r'''href=["']([^"']+)["']''', re.I)


def is_redirect(path: Path) -> bool:
    text = path.read_text(encoding="utf-8", errors="replace")
    return 'http-equiv="refresh"' in text.lower()


def url_for(path: Path) -> str:
    rel = path.parent.relative_to(ROOT).as_posix()
    return BASE + ("/" if rel == "." else f"/{rel}/")


def normalize(href: str) -> str | None:
    if href.startswith(BASE):
        return href.split("#", 1)[0]
    if href.startswith("/"):
        h = href.split("#", 1)[0]
        if h.endswith(".json") or h.endswith(".xml") or h.endswith(".txt"):
            return BASE + h
        return BASE + (h if h.endswith("/") else h + "/")
    return None


def main() -> int:
    files = [
        p
        for p in sorted(ROOT.rglob("index.html"))
        if ".git" not in p.parts and p != ROOT / "index.html" and not is_redirect(p)
    ]
    urls = {url_for(f) for f in files}
    inbound = {u: 0 for u in urls}
    outbound = {u: 0 for u in urls}
    for html in files:
        src = url_for(html)
        seen: set[str] = set()
        text = html.read_text(encoding="utf-8", errors="replace")
        for href in HREF_RE.findall(text):
            dst = normalize(href)
            if not dst or dst == src or dst in seen or dst not in urls:
                continue
            seen.add(dst)
            outbound[src] += 1
            inbound[dst] += 1

    top = sorted(inbound.items(), key=lambda x: (-x[1], x[0]))[:20]
    low = sorted((u, i, outbound[u]) for u, i in inbound.items() if i < 2)
    lines = [
        "# Internal Link Audit",
        "",
        f"Updated: {date.today().isoformat()}",
        "",
        "## Snapshot",
        "",
        f"- Indexable HTML URLs: **{len(urls)}**",
        f"- Low inlink URLs (<2): **{len(low)}**",
        "",
        "## Top Inlinked URLs",
        "",
    ]
    lines.extend([f"- {u} — {n} inlinks" for u, n in top] or ["- None"])
    lines.extend(["", "## Low Inlink URLs", ""])
    lines.extend([f"- {u} — {i} in / {o} out" for u, i, o in low[:80]] or ["- None"])
    lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
