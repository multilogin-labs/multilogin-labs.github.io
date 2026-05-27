#!/usr/bin/env python3
"""CI guard: affiliate hop + homepage checkout URLs match data/affiliate.json."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "data" / "affiliate.json"
HOMEPAGE = ROOT / "index.html"
GO_PAGE = ROOT / "go" / "multilogin" / "index.html"


def main() -> int:
    data = json.loads(CONFIG.read_text(encoding="utf-8"))
    url = data["multilogin_checkout"]
    ok = True

    go = GO_PAGE.read_text(encoding="utf-8")
    if url not in go and url.replace("&", "&amp;") not in go:
        print("FAIL: go/multilogin missing checkout URL", file=sys.stderr)
        ok = False
    if "location.replace" not in go:
        print("FAIL: go/multilogin missing JS redirect", file=sys.stderr)
        ok = False
    if "utm_source=multilogin-labs" in go:
        print("FAIL: go/multilogin still has old utm_source", file=sys.stderr)
        ok = False

    home = HOMEPAGE.read_text(encoding="utf-8")
    if url.replace("&", "&amp;") not in home:
        print("FAIL: homepage missing pricing checkout URL", file=sys.stderr)
        ok = False
    if 'href="/go/multilogin"' in home:
        print("FAIL: homepage still uses /go/multilogin href", file=sys.stderr)
        ok = False

    if ok:
        print("OK affiliate URLs (config, hop, homepage)")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
