#!/usr/bin/env python3
"""OG/Twitter meta, RSS, breadcrumbs, dateModified, footer discovery."""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://multilogin-labs.github.io"
OG_BLOCK = """
<meta property="og:image" content="https://multilogin-labs.github.io/assets/img/og-lab.svg"/>
<meta property="og:image:width" content="1200"/>
<meta property="og:image:height" content="630"/>
<meta name="twitter:image" content="https://multilogin-labs.github.io/assets/img/og-lab.svg"/>"""
RSS_LINK = (
    '<link href="https://multilogin-labs.github.io/feeds/lab-updates.xml" '
    'rel="alternate" title="multilogin-labs Lab Updates RSS" type="application/rss+xml"/>'
)
LOCALE_META = '<meta property="og:locale" content="en_US"/>'
TWITTER_DEFAULTS = """
<meta content="summary_large_image" name="twitter:card"/>
<meta content="@multilogin-labs" name="twitter:site"/>"""

SECTION_LABELS = {
    "guides": "Guides",
    "tools": "Tools",
    "compare": "Compare",
    "promo": "Promo",
    "data": "Data",
    "snippets": "Snippets",
    "catalog": "Catalog",
    "site-map": "Sitemap",
    "about": "About",
    "contact": "Contact",
}


def is_redirect(path: Path) -> bool:
    t = path.read_text(encoding="utf-8", errors="replace")
    return 'http-equiv="refresh"' in t


def humanize_slug(slug: str) -> str:
    return slug.replace("-", " ").replace("_", " ").title()


def extract_title(text: str) -> str | None:
    m = re.search(r"<title>([^<|]+)", text, re.I)
    if m:
        return m.group(1).strip()
    m = re.search(r"<h1[^>]*>([^<]+)", text, re.I)
    if m:
        return re.sub(r"\s+", " ", m.group(1)).strip()
    return None


def extract_h1(text: str) -> str | None:
    m = re.search(r"<h1[^>]*>([^<]+)", text, re.I)
    if m:
        return re.sub(r"\s+", " ", m.group(1)).strip()
    return None


def extract_canonical(text: str) -> str | None:
    m = re.search(r'<link href="([^"]+)" rel="canonical"', text)
    return m.group(1) if m else None


def extract_description(text: str) -> str | None:
    m = re.search(r'<meta content="([^"]*)" name="description"', text)
    return m.group(1) if m else None


def url_path_from_file(html_path: Path) -> str:
    rel = html_path.parent.relative_to(ROOT).as_posix()
    return "/" if rel == "." else f"/{rel}/"


def build_breadcrumb(path: str, page_title: str | None) -> dict | None:
    parts = [p for p in path.strip("/").split("/") if p]
    if not parts:
        return None
    items: list[dict] = [
        {
            "@type": "ListItem",
            "position": 1,
            "name": "Home",
            "item": f"{BASE}/",
        }
    ]
    acc = ""
    for i, part in enumerate(parts):
        acc += f"/{part}"
        is_last = i == len(parts) - 1
        if is_last and page_title:
            name = page_title
        else:
            name = SECTION_LABELS.get(part, humanize_slug(part))
        item: dict = {"@type": "ListItem", "position": i + 2, "name": name}
        if not is_last:
            item["item"] = f"{BASE}{acc}/"
        items.append(item)
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": items,
    }


def add_og(text: str) -> str:
    if "og:image" in text:
        if "og:image:width" not in text:
            text = text.replace(
                'content="https://multilogin-labs.github.io/assets/img/og-lab.svg"/>',
                'content="https://multilogin-labs.github.io/assets/img/og-lab.svg"/>\n'
                '<meta property="og:image:width" content="1200"/>\n'
                '<meta property="og:image:height" content="630"/>',
                1,
            )
        return text
    if 'property="og:site_name"' in text:
        return text.replace('property="og:site_name"/>', 'property="og:site_name"/>' + OG_BLOCK, 1)
    if 'name="description"' in text:
        return re.sub(
            r'(<meta content="[^"]*" name="description"/>)\s*',
            r"\1" + OG_BLOCK + "\n",
            text,
            count=1,
        )
    return text


def add_social_meta(text: str, canonical: str | None, title: str | None, desc: str | None) -> str:
    if "twitter:card" not in text:
        if 'rel="canonical"' in text:
            text = text.replace('rel="canonical"/>', 'rel="canonical"/>' + TWITTER_DEFAULTS, 1)
        elif "<!-- mll-head -->" in text:
            text = text.replace("<!-- mll-head -->", f"<!-- mll-head -->{TWITTER_DEFAULTS}", 1)

    if "og:locale" not in text:
        if LOCALE_META not in text and 'name="twitter:card"' in text:
            text = text.replace('name="twitter:card"/>', 'name="twitter:card"/>' + "\n" + LOCALE_META, 1)

    if canonical and 'property="og:url"' not in text:
        og_url = f'<meta content="{canonical}" property="og:url"/>\n'
        if LOCALE_META in text:
            text = text.replace(LOCALE_META, LOCALE_META + "\n" + og_url, 1)
        elif 'rel="canonical"' in text:
            text = text.replace('rel="canonical"/>', 'rel="canonical"/>\n' + og_url, 1)

    if title and 'property="og:title"' not in text:
        clean = re.sub(r"\s*\|\s*multilogin-labs\s*$", "", title, flags=re.I).strip()
        text = text.replace('name="description"/>', f'name="description"/>\n<meta content="{clean}" property="og:title"/>', 1)

    if desc and 'property="og:description"' not in text and 'property="og:title"' in text:
        esc = desc.replace('"', "&quot;")[:300]
        text = text.replace(
            'property="og:title"/>',
            f'property="og:title"/>\n<meta content="{esc}" property="og:description"/>',
            1,
        )

    if title and "twitter:title" not in text and "twitter:card" in text:
        clean = re.sub(r"\s*\|\s*multilogin-labs\s*$", "", title, flags=re.I).strip()
        text = text.replace(
            'name="twitter:card"/>',
            f'name="twitter:card"/>\n<meta content="{clean}" name="twitter:title"/>',
            1,
        )
    if desc and "twitter:description" not in text and "twitter:title" in text:
        esc = desc.replace('"', "&quot;")[:300]
        text = text.replace(
            'name="twitter:title"/>',
            f'name="twitter:title"/>\n<meta content="{esc}" name="twitter:description"/>',
            1,
        )
    return text


def add_rss(text: str) -> str:
    if "lab-updates.xml" in text:
        return text
    if "<!-- mll-head -->" in text:
        return text.replace("<!-- mll-head -->", f"<!-- mll-head -->\n{RSS_LINK}", 1)
    return (
        text.replace('<link rel="sitemap"', RSS_LINK + '\n<link rel="sitemap"', 1)
        if '<link rel="sitemap"' in text
        else text
    )


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
    return text.replace('<div class="footer-mini-links">', '<div class="footer-mini-links">\n' + extra, 1)


def fix_author_org(text: str) -> str:
    return text.replace(
        '"@type": "Person", "name": "multilogin-labs"',
        '"@type": "Organization", "name": "multilogin-labs"',
    )


def inject_breadcrumb_ld(text: str, path: str) -> str:
    if "BreadcrumbList" in text or path == "/":
        return text
    h1 = extract_h1(text)
    bc = build_breadcrumb(path, h1)
    if not bc:
        return text
    script = (
        '<script type="application/ld+json">\n'
        + json.dumps(bc, indent=2)
        + "\n</script>\n"
    )
    if "</head>" in text:
        return text.replace("</head>", script + "</head>", 1)
    return text


def sync_date_modified(text: str, mtime_iso: str) -> str:
    if '"dateModified"' not in text:
        if '"datePublished"' in text and ("TechArticle" in text or '"Article"' in text):
            text = re.sub(
                r'("datePublished":\s*"[^"]+")',
                rf'\1,\n  "dateModified": "{mtime_iso}"',
                text,
                count=1,
            )
        return text

    def repl(m: re.Match[str]) -> str:
        old = m.group(1)
        if old >= mtime_iso:
            return f'"dateModified": "{old}"'
        return f'"dateModified": "{mtime_iso}"'

    return re.sub(r'"dateModified":\s*"([^"]+)"', repl, text)


def patch_file(path: Path) -> bool:
    raw = path.read_text(encoding="utf-8")
    mtime_iso = date.fromtimestamp(path.stat().st_mtime).isoformat()
    url_path = url_path_from_file(path)
    title = extract_title(raw)
    canonical = extract_canonical(raw)
    desc = extract_description(raw)

    new = raw
    new = fix_author_org(new)
    new = add_og(new)
    new = add_social_meta(new, canonical, title, desc)
    new = add_rss(new)
    new = add_footer_discovery(new)
    new = inject_breadcrumb_ld(new, url_path)
    new = sync_date_modified(new, mtime_iso)

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
