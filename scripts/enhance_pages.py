#!/usr/bin/env python3
"""Add OG image, RSS, and crawl-discovery footer links to indexable pages."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OG_BLOCK = """
<meta property="og:image" content="https://multilogin-labs.github.io/assets/img/og-lab.svg"/>
<meta property="og:image:width" content="1200"/>
<meta property="og:image:height" content="630"/>
<meta name="twitter:image" content="https://multilogin-labs.github.io/assets/img/og-lab.svg"/>"""
RSS_LINK = '<link href="https://multilogin-labs.github.io/feeds/lab-updates.xml" rel="alternate" title="multilogin-labs Lab Updates RSS" type="application/rss+xml"/>'


def is_redirect(path: Path) -> bool:
    t = path.read_text(encoding="utf-8", errors="replace")
    return 'http-equiv="refresh"' in t


def add_og(text: str) -> str:
    if "og:image" in text:
        return text
    if 'property="og:site_name"' in text:
        return text.replace(
            'property="og:site_name"/>',
            'property="og:site_name"/>' + OG_BLOCK,
            1,
        )
    if 'name="description"' in text:
        return re.sub(
            r'(<meta content="[^"]*" name="description"/>)\s*',
            r"\1" + OG_BLOCK + "\n",
            text,
            count=1,
        )
    return text


def add_rss(text: str) -> str:
    if "lab-updates.xml" in text:
        return text
    if "<!-- mll-head -->" in text:
        return text.replace("<!-- mll-head -->", f"<!-- mll-head -->\n{RSS_LINK}", 1)
    return text.replace(
        '<link rel="sitemap"',
        RSS_LINK + '\n<link rel="sitemap"',
        1,
    ) if '<link rel="sitemap"' in text else text


def add_footer_discovery(text: str) -> str:
    if "footer-mini-links" not in text:
        return text
    if "/site-map/" in text and "/catalog/" in text:
        return text
    extra = ""
    if "/site-map/" not in text:
        extra += '<a href="/site-map/">HTML sitemap</a>\n'
    if "/catalog/" not in text:
        extra += '<a href="/catalog/">Catalog</a>\n'
    if not extra:
        return text
    return text.replace(
        '<div class="footer-mini-links">',
        '<div class="footer-mini-links">\n' + extra,
        1,
    )


def fix_author_org(text: str) -> str:
    return text.replace('"name": "multilogin-labs"', '"name": "multilogin-labs"').replace(
        '"@type": "Person", "name": "multilogin-labs"',
        '"@type": "Organization", "name": "multilogin-labs"',
    )


def patch_file(path: Path) -> bool:
    raw = path.read_text(encoding="utf-8")
    new = add_og(add_rss(add_footer_discovery(fix_author_org(raw))))
    if new != raw:
        path.write_text(new, encoding="utf-8")
        return True
    return False


def main() -> None:
    n = 0
    for html in ROOT.rglob("index.html"):
        if ".git" in html.parts or is_redirect(html):
            continue
        if patch_file(html):
            n += 1
    print(f"Enhanced {n} indexable pages")


if __name__ == "__main__":
    main()
