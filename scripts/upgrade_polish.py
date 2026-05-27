#!/usr/bin/env python3
"""Polish pass: footers, meta robots, data-year, compare OG, thin-page fixes."""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOMEPAGE = ROOT / "index.html"
CONFIG = ROOT / "data" / "affiliate.json"
OG_COMPARE = "https://multilogin-labs.github.io/assets/img/multilogin-saas50-1200.webp"
OG_LAB = "https://multilogin-labs.github.io/assets/img/og-lab.svg"

THIN_FOOTER = re.compile(
    r'<footer class="site-footer">\s*<div class="container">\s*'
    r'<p class="small">© <span data-year></span> multilogin-labs · '
    r'<a href="/site-map/">Sitemap</a></p>\s*</div>\s*</footer>',
    re.I,
)

FOOTER_MINI = """<footer class="site-footer">
<div class="container footer-bottom-row">
<p class="small">© <span data-year></span> multilogin-labs</p>
<div class="footer-mini-links">
<a href="/tools/multilogin-discount/">SAAS50 verifier</a>
<a href="/site-map/">Sitemap</a>
<a href="/catalog/">Catalog</a>
<a href="/feeds/lab-updates.xml">RSS</a>
<a href="/compare/">Compare</a>
<a href="/guides/">Guides</a>
</div>
</div>
</footer>"""

RSS = (
    '<link href="https://multilogin-labs.github.io/feeds/lab-updates.xml" '
    'rel="alternate" title="multilogin-labs Lab Updates RSS" type="application/rss+xml"/>'
)

SPEC = (
    '<script type="speculationrules">'
    '{"prefetch":[{"source":"document","where":{"href_matches":"*multilogin.com/pricing*"},'
    '"eagerness":"moderate"}]}</script>'
)


def is_redirect(text: str) -> bool:
    return 'http-equiv="refresh"' in text.lower()


def load_checkout_html() -> str:
    data = json.loads(CONFIG.read_text(encoding="utf-8"))
    return data["multilogin_checkout"].replace("&", "&amp;")


def fix_data_year(text: str) -> str:
    return text.replace('data-year=""', "data-year")


def fix_robots_preview(text: str) -> str:
    if "max-image-preview" in text:
        return text
    return text.replace(
        'content="index,follow" name="robots"',
        'content="index,follow,max-image-preview:large" name="robots"',
    )


def fix_viewport(text: str) -> str:
    return text.replace(
        'content="width=device-width, initial-scale=1.0" name="viewport"',
        'content="width=device-width, initial-scale=1" name="viewport"',
    )


def add_rss(text: str) -> str:
    if "lab-updates.xml" in text:
        return text
    if "</title>" in text:
        return text.replace("</title>", f"</title>\n{RSS}", 1)
    return text


def upgrade_compare_og(text: str, path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if not rel.startswith("compare/"):
        return text
    if rel == "compare/index.html":
        return text
    new = text.replace(OG_LAB, OG_COMPARE)
    new = new.replace(
        'content="https://multilogin-labs.github.io/assets/img/og-lab.svg"',
        f'content="{OG_COMPARE}"',
    )
    return new


def patch_explorer_footer(text: str) -> str:
    old = """<footer class="site-footer">
<div class="container footer-bottom-row">
<p class="small">© <span data-year=""></span> multilogin-labs</p>
<a href="https://github.com/multilogin-labs/multilogin-labs.github.io">GitHub</a>
</div>
</footer>"""
    if old not in text:
        return text
    explorer_footer = FOOTER_MINI.replace(
        '<a href="/guides/">Guides</a>',
        '<a href="/guides/">Guides</a>\n<a href="https://github.com/multilogin-labs/multilogin-labs.github.io">GitHub</a>',
    )
    return text.replace(old, explorer_footer)


def patch_explorer_note(text: str, html_url: str) -> str:
    needle = '<p class="comparison-note small">Next:'
    if needle not in text or "multilogin-discount" in text.split(needle, 1)[1][:200]:
        return text
    return text.replace(
        needle,
        f'<p class="comparison-note small"><a href="{html_url}" rel="sponsored noopener noreferrer" target="_blank">Multilogin pricing</a> · ',
        1,
    )


def patch_site_map(text: str) -> str:
    new = fix_viewport(text)
    new = fix_robots_preview(new)
    new = add_rss(new)
    if "application/ld+json" not in new and "</head>" in new:
        ld = {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "name": "HTML Sitemap — multilogin-labs",
            "url": "https://multilogin-labs.github.io/site-map/",
        }
        block = f'<script type="application/ld+json">\n{json.dumps(ld, indent=2)}\n</script>\n'
        new = new.replace("</head>", block + "</head>", 1)
    if "speculationrules" not in new:
        new = new.replace("</body>", SPEC + "\n</body>", 1)
    return new


def patch_file(path: Path, html_url: str) -> bool:
    if path.resolve() == HOMEPAGE.resolve():
        return False
    raw = path.read_text(encoding="utf-8")
    if is_redirect(raw):
        return False

    new = fix_data_year(raw)
    new = fix_robots_preview(new)
    new = fix_viewport(new)
    new = add_rss(new)
    new = upgrade_compare_og(new, path)

    if THIN_FOOTER.search(new):
        new = THIN_FOOTER.sub(FOOTER_MINI, new, count=1)

    if path.as_posix() == "tools/benchmark-explorer/index.html":
        new = patch_explorer_footer(new)
        new = patch_explorer_note(new, html_url)

    if path.as_posix() == "site-map/index.html":
        new = patch_site_map(new)

    if new != raw:
        path.write_text(new, encoding="utf-8")
        return True
    return False


def update_affiliate_json() -> bool:
    data = json.loads(CONFIG.read_text(encoding="utf-8"))
    today = date.today().isoformat()
    if data.get("updated") == today:
        return False
    data["updated"] = today
    CONFIG.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return True


def main() -> None:
    html_url = load_checkout_html()
    n = 0
    for html in sorted(ROOT.rglob("*.html")):
        if ".git" in html.parts:
            continue
        if patch_file(html, html_url):
            n += 1
    if update_affiliate_json():
        n += 1
    print(f"Polish upgrade: {n} files touched (homepage skipped)")


if __name__ == "__main__":
    main()
