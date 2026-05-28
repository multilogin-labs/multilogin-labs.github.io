#!/usr/bin/env python3
"""SEO pass: redirects, internal links, head tags, HTML sitemap, sitemap lastmod."""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from redirect_html import REDIRECT_HTML

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://multilogin-labs.github.io"
TODAY = date.today().isoformat()

COMPARE_KEEP = {
    "multilogin-alternatives",
    "multilogin-vs-gologin",
    "multilogin-vs-adspower",
    "multilogin-vs-dolphin-anty",
    "multilogin-vs-incogniton",
    "multilogin-vs-kameleo",
    "multilogin-vs-octo-browser",
    "multilogin-vs-undetectable",
}

SITEMAP_LINK = '<link rel="sitemap" type="application/xml" title="Sitemap" href="/sitemap.xml"/>'

PROMO_SLUGS = [
    "adblogin-promo-code", "adspower-promo-code", "bitbrowser-promo-code",
    "dashnull-promo-code", "discloak-promo-code", "dolphin-anty-coupon",
    "ghost-browser-promo-code", "gologin-discount-code", "hidemyacc-promo-code",
    "incogniton-promo-code", "indigo-browser-promo-code", "kameleo-promo-code",
    "linkensphere-promo-code", "morelogin-promo-code", "nstbrowser-promo-code",
    "octo-browser-promo-code", "roxybrowser-promo-code", "undetectable-promo-code",
    "vektort13-promo-code", "vmlogin-promo-code", "wade-browser-promo-code",
    "whologin-promo-code",
]


def is_redirect(path: Path) -> bool:
    if path.name != "index.html":
        return False
    text = path.read_text(encoding="utf-8", errors="replace")
    return 'http-equiv="refresh"' in text or "http-equiv='refresh'" in text


def fix_promo_redirects():
    for slug in PROMO_SLUGS:
        p = ROOT / "promo" / slug / "index.html"
        if not p.exists():
            continue
        raw = p.read_text(encoding="utf-8", errors="replace")
        # Keep enriched promo pages when explicitly marked indexable.
        if "mll-promo-indexable" in raw:
            continue
        url = f"/promo/#vendor-{slug}"
        p.write_text(
            REDIRECT_HTML.format(
                url=url,
                canonical=f"{BASE}/promo/",
                title=slug.replace("-", " ").title(),
                link_label="Promo verification hub",
            ),
            encoding="utf-8",
        )


def fix_legacy_root_redirects():
    """Root paths that moved into /tools/ or /go/."""
    stubs = [
        (
            ROOT / "antidetect-browsers" / "index.html",
            "/tools/antidetect-browsers/",
            f"{BASE}/tools/antidetect-browsers/",
            "Antidetect browsers ranking",
            "Tools ranking page",
        ),
    ]
    for path, url, canonical, title, label in stubs:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            REDIRECT_HTML.format(
                url=url, canonical=canonical, title=title, link_label=label
            ),
            encoding="utf-8",
        )


def fix_compare_redirects():
    compare_dir = ROOT / "compare"
    for child in compare_dir.iterdir():
        if not child.is_dir() or child.name in COMPARE_KEEP:
            continue
        p = child / "index.html"
        url = "/compare/"
        p.write_text(
            REDIRECT_HTML.format(
                url=url,
                canonical=f"{BASE}/compare/",
                title=child.name.replace("-", " ").title(),
                link_label="Compare hub",
            ),
            encoding="utf-8",
        )


def fix_internal_links(text: str) -> str:
    for slug in PROMO_SLUGS:
        promo_path = ROOT / "promo" / slug / "index.html"
        is_indexable_promo = promo_path.exists() and "mll-promo-indexable" in promo_path.read_text(
            encoding="utf-8", errors="replace"
        )
        if is_indexable_promo:
            continue
        text = text.replace(f'"/promo/{slug}/"', f'"/promo/#vendor-{slug}"')
        text = text.replace(f"'/promo/{slug}/'", f"'/promo/#vendor-{slug}'")
        text = text.replace(f">{BASE}/promo/{slug}/<", f">{BASE}/promo/#vendor-{slug}<")

    for child in (ROOT / "compare").iterdir():
        if not child.is_dir() or child.name in COMPARE_KEEP:
            continue
        slug = child.name
        text = text.replace(f'"/compare/{slug}/"', '"/compare/multilogin-alternatives/"')
        text = text.replace(f"'/compare/{slug}/'", "'/compare/multilogin-alternatives/'")

    return text


def add_sitemap_link(text: str) -> str:
    if SITEMAP_LINK in text or "noindex" in text[:800]:
        return text
    if "<!-- mll-head -->" in text:
        return text.replace("<!-- mll-head -->", f"<!-- mll-head -->\n{SITEMAP_LINK}", 1)
    needle = '<meta content="width=device-width, initial-scale=1.0" name="viewport"/>'
    if needle in text:
        return text.replace(needle, needle + "\n" + SITEMAP_LINK, 1)
    return text


def ensure_article_dates(text: str) -> str:
    if '"datePublished"' in text or '"@type": "Article"' not in text:
        return text
    if '"dateModified"' in text and '"datePublished"' not in text:
        text = re.sub(
            r'("dateModified":\s*"[^"]+")',
            r'"datePublished": "2026-04-11", \1',
            text,
            count=1,
        )
    return text


def patch_indexable_files():
    n = 0
    for html in ROOT.rglob("index.html"):
        if ".git" in html.parts or is_redirect(html):
            continue
        raw = html.read_text(encoding="utf-8")
        new = fix_internal_links(raw)
        new = add_sitemap_link(new)
        new = ensure_article_dates(new)
        if new != raw:
            html.write_text(new, encoding="utf-8")
            n += 1
    return n


def collect_indexable_paths() -> list[tuple[str, str, str]]:
    """Return (path, lastmod, priority) for sitemap."""
    from migrate_site import collect_indexable_urls  # noqa: WPS433

    return collect_indexable_urls()


def write_html_sitemap(urls: list[tuple[str, str, str]]) -> None:
    sections: dict[str, list[tuple[str, str]]] = {
        "Core": [],
        "Tools": [],
        "Guides": [],
        "Compare": [],
        "Data": [],
        "Other": [],
    }
    for loc, lastmod, _pri in urls:
        path = loc.replace(BASE, "")
        name = path.strip("/").replace("/", " › ") or "Home"
        entry = (name, path or "/")
        if path.startswith("/tools/"):
            sections["Tools"].append(entry)
        elif path.startswith("/guides/"):
            sections["Guides"].append(entry)
        elif path.startswith("/compare/"):
            sections["Compare"].append(entry)
        elif path.startswith("/data/"):
            sections["Data"].append(entry)
        elif path in ("/", "/promo/", "/about/", "/contact/", "/catalog/"):
            sections["Core"].append(entry)
        else:
            sections["Other"].append(entry)

    body = []
    for title, items in sections.items():
        if not items:
            continue
        body.append(f'<section class="section"><h2>{title}</h2><ul class="clean sitemap-list">')
        for name, path in sorted(items, key=lambda x: x[0].lower()):
            body.append(f'<li><a href="{path}">{name}</a></li>')
        body.append("</ul></section>")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<!-- mll-head -->
<link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml"/>
<link rel="manifest" href="/site.webmanifest"/>
<meta name="theme-color" content="#2a9d8f"/>
{SITEMAP_LINK}
<title>HTML Sitemap — All Indexable Pages | multilogin-labs</title>
<meta content="Complete HTML sitemap of indexable multilogin-labs pages for crawlers and readers. Updated {TODAY}." name="description"/>
<meta content="index,follow,max-image-preview:large" name="robots"/>
<link href="{BASE}/site-map/" rel="canonical"/>
<meta content="HTML Sitemap — All Indexable Pages | multilogin-labs" property="og:title"/>
<meta content="Reader-facing index of every URL we intend Google to index. Updated {TODAY}." property="og:description"/>
<meta content="{BASE}/site-map/" property="og:url"/>
<meta content="website" property="og:type"/>
<meta content="multilogin-labs" property="og:site_name"/>
<meta content="{BASE}/assets/img/og-lab.svg" property="og:image"/>
<meta content="1200" property="og:image:width"/>
<meta content="630" property="og:image:height"/>
<meta content="en_US" property="og:locale"/>
<meta content="summary_large_image" name="twitter:card"/>
<meta content="{BASE}/assets/img/og-lab.svg" name="twitter:image"/>
<link href="{BASE}/assets/css/site.css" rel="stylesheet"/>
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@graph": [
    {{
      "@type": "CollectionPage",
      "name": "multilogin-labs HTML sitemap",
      "url": "{BASE}/site-map/",
      "description": "Reader-facing index of every URL we intend Google to index.",
      "isPartOf": {{"@type": "WebSite", "url": "{BASE}/"}}
    }},
    {{
      "@type": "BreadcrumbList",
      "itemListElement": [
        {{"@type": "ListItem", "position": 1, "name": "Home", "item": "{BASE}/"}},
        {{"@type": "ListItem", "position": 2, "name": "HTML sitemap", "item": "{BASE}/site-map/"}}
      ]
    }}
  ]
}}
</script>
</head>
<body>
<a class="skip-link" href="#main-content">Skip to main content</a>
<header class="site-header"><div class="container nav-wrap">
<a class="logo" href="/">multi<span>login-labs</span></a>
<nav class="nav-links"><a href="/guides/">Guides</a><a href="/tools/">Tools</a><a href="/catalog/">Catalog</a></nav>
</div></header>
<main class="container" id="main-content">
<section class="hero">
<span class="badge">SEO</span>
<h1>HTML sitemap</h1>
<p class="lead">All pages we intend Google to index ({len(urls)} URLs). Machine list: <a href="/sitemap.xml">sitemap.xml</a>.</p>
<p class="hero-meta">Updated: {TODAY}</p>
</section>
{"".join(body)}
</main>
<footer class="site-footer"><div class="container footer-bottom-row">
<p class="small">© multilogin-labs · <a href="/sitemap.xml">XML sitemap</a></p>
</div></footer>
<script defer src="/assets/js/site.js"></script>
</body>
</html>
"""
    out = ROOT / "site-map" / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")


def write_sitemap_with_mtime():
    import migrate_site

    urls: list[tuple[str, str, str]] = []
    seen: set[str] = set()

    def add(path: str, priority: str):
        loc = BASE + path if path.startswith("/") else f"{BASE}/{path}"
        if loc in seen:
            return
        seen.add(loc)
        rel = path.strip("/")
        file_path = ROOT / rel / "index.html" if rel and not path.endswith(".json") and not path.endswith(".xml") and not path.endswith(".txt") else ROOT / rel.lstrip("/")
        if file_path.is_dir():
            file_path = file_path / "index.html"
        mtime = (
            date.fromtimestamp(file_path.stat().st_mtime).isoformat()
            if file_path.exists()
            else TODAY
        )
        urls.append((loc, mtime, priority))

    # Reuse logic from migrate_site
    migrate_site.ROOT = ROOT
    migrate_site.TODAY = TODAY
    for loc, _old_mod, pri in migrate_site.collect_indexable_urls():
        path = loc.replace(BASE, "")
        add(path or "/", pri)

    urls.sort(key=lambda x: (-float(x[2]), x[0]))
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, lastmod, priority in urls:
        lines += [
            "  <url>",
            f"    <loc>{loc}</loc>",
            f"    <lastmod>{lastmod}</lastmod>",
            "    <changefreq>weekly</changefreq>",
            f"    <priority>{priority}</priority>",
            "  </url>",
        ]
    lines.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return urls


def clean_compare_index():
    path = ROOT / "compare" / "index.html"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    text = re.sub(
        r'<section class="section">\s*<p class="section-kicker">Compare Library</p>[\s\S]*?'
        r'<section class="section">\s*<div class="panel">\s*<p class="section-kicker">Evidence Discipline</p>',
        '<section class="section">\n<div class="panel">\n<p class="section-kicker">Evidence Discipline</p>',
        text,
        count=1,
    )
    thead_fix = """<thead>
<tr>
<th>Comparison</th>
<th>Focus</th>
<th>Next step</th>
<th>Read time</th>
</tr>
</thead>"""
    text = re.sub(
        r"<thead>\s*<tr>\s*<th>Question</th>[\s\S]*?</thead>",
        thead_fix,
        text,
        count=1,
    )
    tier1 = """
<section class="section">
<p class="section-kicker">Head-to-head pages</p>
<h2>Tier-1 comparisons (indexable)</h2>
<div class="grid-3">
<article class="card"><h3>Alternatives matrix</h3><p>Shortlist by cost and risk bands.</p><a href="/compare/multilogin-alternatives/">Open</a></article>
<article class="card"><h3>vs GoLogin</h3><p>Engine cadence and fingerprint drift.</p><a href="/compare/multilogin-vs-gologin/">Open</a></article>
<article class="card"><h3>vs AdsPower</h3><p>Workspace governance at scale.</p><a href="/compare/multilogin-vs-adspower/">Open</a></article>
<article class="card"><h3>vs Dolphin Anty</h3><p>Team policy and audit exports.</p><a href="/compare/multilogin-vs-dolphin-anty/">Open</a></article>
<article class="card"><h3>vs Incogniton</h3><p>Starter API limits vs scale needs.</p><a href="/compare/multilogin-vs-incogniton/">Open</a></article>
<article class="card"><h3>vs Kameleo</h3><p>Automation bridge stability.</p><a href="/compare/multilogin-vs-kameleo/">Open</a></article>
<article class="card"><h3>vs Octo Browser</h3><p>Token rotation and API lifecycle.</p><a href="/compare/multilogin-vs-octo-browser/">Open</a></article>
<article class="card"><h3>vs Undetectable.io</h3><p>Local footprint and profile density.</p><a href="/compare/multilogin-vs-undetectable/">Open</a></article>
</div>
<p class="comparison-note small">Legacy compare URLs use <code>noindex</code> redirects to this hub.</p>
<p class="small"><a href="/site-map/">HTML sitemap</a> · <a href="/promo/">Promo hub</a></p>
</section>
"""
    if "Tier-1 comparisons (indexable)" not in text:
        text = text.replace(
            "</div>\n</section>\n<section class=\"section\">\n<p class=\"section-kicker\">Quick Routing</p>",
            "</div>\n</section>" + tier1 + "\n<section class=\"section\">\n<p class=\"section-kicker\">Quick Routing</p>",
            1,
        )
    path.write_text(text, encoding="utf-8")


def main():
    fix_promo_redirects()
    fix_compare_redirects()
    fix_legacy_root_redirects()
    clean_compare_index()
    n = patch_indexable_files()
    urls = write_sitemap_with_mtime()
    write_html_sitemap(urls)
    # Add site-map to migrate list manually in migrate_site
    print(f"Patched {n} indexable HTML files")
    print(f"Sitemap URLs: {len(urls)}")
    print("HTML sitemap: /site-map/")


if __name__ == "__main__":
    main()
