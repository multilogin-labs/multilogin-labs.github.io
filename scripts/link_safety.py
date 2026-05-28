#!/usr/bin/env python3
"""Sitewide outbound link safety + affiliate disclosure gate.

Rules:
  R1. Any anchor to `multilogin.com/pricing` or `/go/multilogin` (revenue path)
      must declare `rel="sponsored"`.
  R2. Any anchor with `target="_blank"` must include `noopener` (or `noreferrer`)
      in rel — prevents reverse-tabnabbing.
  R3. Anchors to `docs.multilogin.com` / `app.multilogin.com` (non-revenue) are
      considered nav links; `rel="nofollow"` is acceptable.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {"scripts", "node_modules", ".git", "__pycache__"}

A_TAG = re.compile(r"<a\b[^>]*>", re.I)
HREF = re.compile(r'\bhref=["\']([^"\']+)["\']', re.I)
REL = re.compile(r'\brel=["\']([^"\']+)["\']', re.I)
TARGET = re.compile(r'\btarget=["\']([^"\']+)["\']', re.I)

REVENUE_HOSTS = ("multilogin.com/pricing", "/go/multilogin")
DOCS_HOSTS = ("docs.multilogin.com", "app.multilogin.com", "support.multilogin.com")


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
    revenue_links = 0
    blank_links = 0
    for path in iter_html():
        text = path.read_text(encoding="utf-8")
        rel_path = str(path.relative_to(ROOT))
        for m in A_TAG.finditer(text):
            tag = m.group(0)
            href_m = HREF.search(tag)
            if not href_m:
                continue
            href = href_m.group(1)
            rel_attr = (REL.search(tag).group(1).lower() if REL.search(tag) else "")
            target_attr = (TARGET.search(tag).group(1).lower() if TARGET.search(tag) else "")

            is_revenue = any(h in href for h in REVENUE_HOSTS)
            is_docs = any(h in href for h in DOCS_HOSTS)
            opens_new_tab = target_attr == "_blank"

            if is_revenue:
                revenue_links += 1
                if "sponsored" not in rel_attr:
                    failures.append(f"{rel_path}: revenue anchor missing rel=sponsored — {tag[:140]}")
            elif is_docs:
                if "nofollow" not in rel_attr and "sponsored" not in rel_attr:
                    failures.append(f"{rel_path}: docs anchor missing rel=nofollow — {tag[:140]}")

            if opens_new_tab:
                blank_links += 1
                if "noopener" not in rel_attr and "noreferrer" not in rel_attr:
                    failures.append(f"{rel_path}: target=_blank missing rel=noopener — {tag[:140]}")

    print(f"link_safety: revenue_anchors={revenue_links} target_blank={blank_links} failures={len(failures)}")
    if failures:
        for f in failures[:40]:
            print(f"  FAIL {f}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
