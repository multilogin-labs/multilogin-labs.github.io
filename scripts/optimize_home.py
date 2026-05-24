#!/usr/bin/env python3
"""Guardrails: homepage perf stack + JSON-LD validity."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"


def main() -> int:
    text = INDEX.read_text(encoding="utf-8")
    ok = True
    for needle in (
        "home.css",
        "home.js",
        "multilogin-promo-code-saas50-checkout-proof",
        "multilogin-saas50-redeem-video-thumb",
    ):
        if needle not in text:
            print(f"FAIL: index.html missing {needle}", file=sys.stderr)
            ok = False
    head = text.split("</head>", 1)[0]
    if '<link href="/assets/css/site.css" rel="stylesheet"/>' in head:
        print("FAIL: blocking site.css in <head>", file=sys.stderr)
        ok = False
    if "site.js" in text:
        print("FAIL: index should use home.js", file=sys.stderr)
        ok = False
    if "i.ytimg.com" in text:
        print("FAIL: use self-hosted video thumb, not i.ytimg.com", file=sys.stderr)
        ok = False
    m = re.search(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', text, re.S)
    if not m:
        print("FAIL: no JSON-LD", file=sys.stderr)
        ok = False
    else:
        try:
            data = json.loads(m.group(1))
            types = [n.get("@type") for n in data.get("@graph", [])]
            for want in ("FAQPage", "VideoObject", "ImageObject", "Offer", "HowTo"):
                if want not in types:
                    print(f"FAIL: JSON-LD missing @type {want}", file=sys.stderr)
                    ok = False
        except json.JSONDecodeError as e:
            print(f"FAIL: invalid JSON-LD: {e}", file=sys.stderr)
            ok = False
    if ok:
        print("OK homepage (perf + schema + assets)")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
