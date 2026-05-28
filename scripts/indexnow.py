#!/usr/bin/env python3
"""IndexNow key file + optional ping for Bing/Yandex crawlers."""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://multilogin-labs.github.io"
HOST = "multilogin-labs.github.io"
KEY = "mll7f3a9c2e1b4d6085a2f9e0c7b3d6e8"
KEY_FILE = ROOT / f"{KEY}.txt"
INDEXNOW_API = "https://api.indexnow.org/indexnow"
NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}


def ensure_key_file() -> None:
    KEY_FILE.write_text(KEY + "\n", encoding="utf-8")


def urls_from_sitemap(limit: int = 200) -> list[str]:
    sm = ROOT / "sitemap.xml"
    if not sm.exists():
        return []
    root = ET.parse(sm).getroot()
    urls = []
    for el in root.iter():
        if el.tag.endswith("loc") and el.text:
            urls.append(el.text.strip())
    return urls[:limit]


def ping(urls: list[str], dry_run: bool = False) -> bool:
    if not urls:
        print("No URLs to ping")
        return True
    payload = {
        "host": HOST,
        "key": KEY,
        "keyLocation": f"{BASE}/{KEY}.txt",
        "urlList": urls,
    }
    if dry_run:
        print(f"IndexNow dry-run: would ping {len(urls)} URLs")
        print(json.dumps(payload, indent=2)[:500] + "...")
        return True
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        INDEXNOW_API,
        data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            print(f"IndexNow OK ({resp.status}): {len(urls)} URLs")
            return True
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:200]
        print(f"IndexNow HTTP {e.code}: {body}", file=sys.stderr)
        return False
    except urllib.error.URLError as e:
        print(f"IndexNow error: {e}", file=sys.stderr)
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="IndexNow for multilogin-labs.github.io")
    parser.add_argument("--ensure-key", action="store_true", help="Write key verification file")
    parser.add_argument("--from-sitemap", action="store_true", help="Ping all sitemap URLs")
    parser.add_argument("--url", action="append", default=[], help="Ping specific URL(s)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=100)
    args = parser.parse_args()

    ensure_key_file()

    urls: list[str] = list(args.url)
    if args.from_sitemap:
        urls = urls_from_sitemap(args.limit)

    if not urls and not args.ensure_key:
        parser.print_help()
        return 0

    if urls:
        ok = ping(urls, dry_run=args.dry_run)
        return 0 if ok else 1
    print(f"Key file ready: /{KEY}.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
