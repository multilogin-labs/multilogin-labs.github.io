#!/usr/bin/env python3
"""Inner-site upgrades: sponsored rel, announcements, catalog, ai.txt, prefetch hints."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "data" / "affiliate.json"
HOMEPAGE = ROOT / "index.html"
AI_TXT = ROOT / "ai.txt"
CATALOG = ROOT / "catalog" / "index.html"

ANNOUNCE_RE = re.compile(r'<div class="site-announcement">[\s\S]*?</div>', re.I)
PRICING_A = re.compile(
    r'(<a\s(?=[^>]*href="https://multilogin\.com/pricing/)[^>]*?)rel="noopener noreferrer"',
    re.I,
)
PERF_BLOCK = """<link rel="dns-prefetch" href="https://multilogin.com"/>
<link rel="preconnect" href="https://multilogin.com" crossorigin/>"""

CATALOG_MLX_CARD = """<article class="card"><h3>Multilogin SAAS50</h3><p>Discount verifier + checkout proof.</p><a href="/tools/multilogin-discount/">Open</a></article>
"""

CATALOG_GUIDE_LINKS = """<a href="/guides/procurement-evidence-gate/">Procurement evidence gate</a>
<a href="/guides/benchmark-reports/2026-05/">May 2026 benchmark preview</a>
"""


def load_urls() -> tuple[str, str]:
    data = json.loads(CONFIG.read_text(encoding="utf-8"))
    raw = data["multilogin_checkout"].strip()
    return raw, raw.replace("&", "&amp;")


def announcement(html_url: str) -> str:
    return (
        f'<div class="site-announcement">SAAS50 = <strong>50% off</strong> plans · '
        f'MIN50 = cloud phone — <a href="{html_url}" rel="sponsored noopener noreferrer" '
        f'target="_blank">Multilogin pricing →</a></div>'
    )


def write_ai_txt(raw_url: str) -> None:
    AI_TXT.write_text(
        f"""# ai.txt — multilogin-labs
# Canonical machine-readable index: https://multilogin-labs.github.io/llms.txt

site: https://multilogin-labs.github.io/
llms: https://multilogin-labs.github.io/llms.txt
checkout: {raw_url}
discount-proof: https://multilogin-labs.github.io/tools/multilogin-discount/
data: https://multilogin-labs.github.io/data/index.json
contact: admin@multilogin-labs.github.io
""",
        encoding="utf-8",
    )


def patch_catalog() -> bool:
    if not CATALOG.exists():
        return False
    text = CATALOG.read_text(encoding="utf-8")
    new = text
    if "multilogin-discount" not in new:
        new = new.replace(
            '<div class="grid-3">\n<article class="card"><h3>Benchmark Explorer</h3>',
            '<div class="grid-3">\n' + CATALOG_MLX_CARD + '<article class="card"><h3>Benchmark Explorer</h3>',
            1,
        )
    new = new.replace(
        "<p>Live JSON matrix with CSV export.</p>",
        "<p>May 2026 preview + April baseline matrix.</p>",
        1,
    )
    if "procurement-evidence-gate" not in new and '<p class="section-kicker">Guides</p>' in new:
        new = new.replace(
            '<div class="related-links">',
            '<div class="related-links">\n' + CATALOG_GUIDE_LINKS,
            1,
        )
    if new != text:
        CATALOG.write_text(new, encoding="utf-8")
        return True
    return False


def patch_html(path: Path, raw_url: str, html_url: str) -> bool:
    if path.resolve() == HOMEPAGE.resolve():
        return False
    text = path.read_text(encoding="utf-8")
    if 'http-equiv="refresh"' in text.lower():
        return False
    new = text
    if ANNOUNCE_RE.search(new):
        new = ANNOUNCE_RE.sub(announcement(html_url), new, count=1)
    new = PRICING_A.sub(r'\1rel="sponsored noopener noreferrer"', new)
    if "multilogin.com/pricing" in new and "dns-prefetch" not in new and "<!-- mll-head -->" in new:
        new = new.replace("<!-- mll-head -->", f"<!-- mll-head -->\n{PERF_BLOCK}", 1)
    if new != text:
        path.write_text(new, encoding="utf-8")
        return True
    return False


def main() -> None:
    raw_url, html_url = load_urls()
    write_ai_txt(raw_url)
    n = 0
    for html in sorted(ROOT.rglob("*.html")):
        if ".git" in html.parts:
            continue
        if patch_html(html, raw_url, html_url):
            n += 1
    if patch_catalog():
        n += 1
    print(f"Inner site upgrade: ai.txt + {n} files touched (homepage skipped)")


if __name__ == "__main__":
    main()
