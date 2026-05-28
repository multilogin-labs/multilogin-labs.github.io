#!/usr/bin/env python3
"""Report JSON-LD schema coverage across indexable pages."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {"scripts", "node_modules", ".git", "__pycache__"}

JSONLD = re.compile(
    r'<script\s+type="application/ld\+json"[^>]*>([\s\S]*?)</script>',
    re.IGNORECASE,
)
ROBOTS = re.compile(r'<meta[^>]+name="robots"[^>]+content="([^"]+)"', re.IGNORECASE)


def types_in(blocks: list[str]) -> set[str]:
    found: set[str] = set()
    for raw in blocks:
        try:
            data = json.loads(raw.strip())
        except json.JSONDecodeError:
            continue
        graph = data.get("@graph") if isinstance(data, dict) else None
        items = graph if isinstance(graph, list) else [data]
        for item in items:
            if isinstance(item, dict):
                t = item.get("@type")
                if isinstance(t, str):
                    found.add(t)
                elif isinstance(t, list):
                    found.update(x for x in t if isinstance(x, str))
    return found


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


def url_for(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix().removesuffix("index.html").rstrip("/")
    return f"/{rel}/" if rel else "/"


def main() -> int:
    files = iter_html()
    rows: list[tuple[str, list[str]]] = []
    missing_breadcrumb: list[str] = []
    missing_any: list[str] = []
    type_counts: dict[str, int] = {}
    indexable_total = 0
    for path in files:
        text = path.read_text(encoding="utf-8")
        if not is_indexable(text):
            continue
        indexable_total += 1
        blocks = JSONLD.findall(text)
        url = url_for(path)
        types = types_in(blocks)
        rows.append((url, sorted(types)))
        if not types:
            missing_any.append(url)
        if types and "BreadcrumbList" not in types and url not in {"/"}:
            missing_breadcrumb.append(url)
        for t in types:
            type_counts[t] = type_counts.get(t, 0) + 1

    lines: list[str] = ["# Schema Coverage", ""]
    lines.append(f"- Indexable HTML pages: **{indexable_total}**")
    lines.append(f"- Pages with no JSON-LD: **{len(missing_any)}**")
    lines.append(f"- Pages missing BreadcrumbList: **{len(missing_breadcrumb)}**")
    lines.append("")
    lines.append("## Type distribution")
    for t, c in sorted(type_counts.items(), key=lambda kv: -kv[1]):
        lines.append(f"- {t}: {c}")
    lines.append("")
    lines.append("## Pages missing JSON-LD")
    if not missing_any:
        lines.append("- None")
    else:
        for u in missing_any:
            lines.append(f"- {u}")
    lines.append("")
    lines.append("## Pages missing BreadcrumbList")
    if not missing_breadcrumb:
        lines.append("- None")
    else:
        for u in missing_breadcrumb:
            lines.append(f"- {u}")
    out = "\n".join(lines) + "\n"
    (ROOT / "docs" / "SCHEMA-COVERAGE.md").write_text(out, encoding="utf-8")
    print(
        f"schema_coverage: indexable={indexable_total} "
        f"no-schema={len(missing_any)} no-breadcrumb={len(missing_breadcrumb)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
