#!/usr/bin/env python3
"""Guardrails: homepage must use home.css + home.js (not blocking site.css in head)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"


def main() -> int:
    text = INDEX.read_text(encoding="utf-8")
    ok = True
    for needle in ("home.css", "home.js", "multilogin-promo-code-saas50-checkout-proof"):
        if needle not in text:
            print(f"FAIL: index.html missing {needle}", file=sys.stderr)
            ok = False
    if '<link href="/assets/css/site.css" rel="stylesheet"/>' in text.split("</head>")[0]:
        print("FAIL: blocking site.css in <head> — use async load only", file=sys.stderr)
        ok = False
    if "site.js" in text:
        print("FAIL: index should use home.js not site.js", file=sys.stderr)
        ok = False
    if ok:
        print("OK homepage perf stack")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
