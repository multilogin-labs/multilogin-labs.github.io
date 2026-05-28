#!/usr/bin/env python3
"""Sitewide UX/perf patches: announcement, toast, prefetch, lab CTA (skips homepage)."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "data" / "affiliate.json"
HOMEPAGE = ROOT / "index.html"
GO_PAGE = ROOT / "go" / "multilogin" / "index.html"

SKIP_CTA_TAIL = {
    "privacy-policy",
    "terms",
    "editorial-policy",
    "site-map",
    "report-template",
}
SKIP_ANNOUNCE = SKIP_CTA_TAIL | {"snippets", "catalog"}

SPEC_RULES = (
    '<script type="speculationrules">'
    '{"prefetch":[{"source":"document","where":{"href_matches":"*multilogin.com/pricing*"},'
    '"eagerness":"moderate"}]}</script>'
)
TOAST = '<div aria-live="polite" class="toast" id="site-toast"></div>'
PERF = """<link rel="dns-prefetch" href="https://multilogin.com"/>
<link rel="preconnect" href="https://multilogin.com" crossorigin/>"""


def load_checkout() -> tuple[str, str]:
    data = json.loads(CONFIG.read_text(encoding="utf-8"))
    raw = data["multilogin_checkout"].strip()
    return raw, raw.replace("&", "&amp;")


def is_redirect(text: str) -> bool:
    return 'http-equiv="refresh"' in text.lower()


def announcement(html_url: str) -> str:
    return (
        f'<div class="site-announcement">SAAS50 = <strong>50% off</strong> plans · '
        f'MIN50 = cloud phone — <a href="{html_url}" rel="sponsored noopener noreferrer" '
        f'target="_blank">Multilogin pricing →</a></div>'
    )


def lab_cta(html_url: str) -> str:
    return f"""
<section class="section lab-cta">
<div class="panel">
<p class="section-kicker">Multilogin offers</p>
<h2>SAAS50 + MIN50 verification</h2>
<p class="small"><a href="/tools/multilogin-discount/">Discount verifier</a> · <a href="{html_url}" rel="sponsored noopener noreferrer" target="_blank">Official pricing</a> · <a href="/#multilogin-price">Redeem steps (home)</a></p>
</div>
</section>
"""


def insert_after_skip_link(text: str, block: str) -> str:
    m = re.search(r'(<a class="skip-link"[^>]*>[^<]*</a>)', text, re.I)
    if m:
        pos = m.end()
        return text[:pos] + "\n" + block + text[pos:]
    return text.replace("<body>", "<body>\n" + block, 1)


def patch_file(path: Path, raw_url: str, html_url: str) -> bool:
    text = path.read_text(encoding="utf-8")
    if is_redirect(text):
        return False
    if path.resolve() == HOMEPAGE.resolve():
        return False

    new = text
    slug = path.parent.name

    if slug not in SKIP_ANNOUNCE and "site-announcement" not in new:
        new = insert_after_skip_link(new, announcement(html_url))

    if "data-copy-code" in new and "site-toast" not in new:
        new = insert_after_skip_link(new, TOAST)

    if "dns-prefetch" not in new and "<!-- mll-head -->" in new:
        new = new.replace("<!-- mll-head -->", f"<!-- mll-head -->\n{PERF}", 1)

    if "speculationrules" not in new and "</body>" in new:
        new = new.replace("</body>", SPEC_RULES + "\n</body>", 1)

    if (
        slug not in SKIP_CTA_TAIL
        and "lab-cta" not in new
        and "</main>" in new
        and "multilogin.com/pricing" not in new
    ):
        new = new.replace("</main>", lab_cta(html_url) + "\n</main>", 1)

    if new != text:
        path.write_text(new, encoding="utf-8")
        return True
    return False


def patch_guides_hub() -> bool:
    path = ROOT / "guides" / "index.html"
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    links = [
        ('href="/guides/procurement-evidence-gate/"', "Procurement evidence gate"),
        ('href="/guides/benchmark-reports/2026-05/"', "May 2026 benchmark preview"),
    ]
    new = text
    for href, label in links:
        if href not in new:
            needle = '<a href="/guides/evaluation-methodology/">'
            new = new.replace(
                needle,
                f'<a {href[1:-1]}>{label}</a>\n<a href="/guides/evaluation-methodology/">',
                1,
            )
    if new != text:
        path.write_text(new, encoding="utf-8")
        return True
    return False


def main() -> None:
    raw_url, html_url = load_checkout()
    n = 0
    for html in sorted(ROOT.rglob("index.html")):
        if ".git" in html.parts:
            continue
        if patch_file(html, raw_url, html_url):
            n += 1
    if patch_guides_hub():
        n += 1
    print(f"Sitewide upgrade: {n} files updated (homepage skipped)")


if __name__ == "__main__":
    main()
