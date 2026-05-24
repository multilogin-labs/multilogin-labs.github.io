#!/usr/bin/env python3
"""Align affiliate funnel pages: nav, OG image, perf hints, sticky CTA."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://multilogin-labs.github.io"
OG_PROMO = f"{BASE}/assets/img/multilogin-saas50-1200.webp"

AFF_NAV = """<nav aria-label="Main navigation" class="nav-links">
<a href="/">Home</a>
<a href="/#multilogin-price">Redeem steps</a>
<a href="/go/multilogin" rel="sponsored noopener noreferrer" target="_blank">Checkout</a>
<a href="/promo/">Other promos</a>
<a href="/compare/">Compare</a>
</nav>"""

STICKY = """
<aside class="aff-sticky" hidden id="aff-sticky">
<a class="btn btn-primary" href="/go/multilogin" rel="sponsored noopener noreferrer" target="_blank">SAAS50 — 50% off</a>
<button aria-label="Copy promo code SAAS50" class="btn btn-ghost aff-sticky-copy copy-code" data-copy-code="SAAS50" type="button">Copy SAAS50</button>
</aside>
"""

PERF_HINTS = """<link rel="dns-prefetch" href="https://multilogin.com"/>
<link rel="preconnect" href="https://multilogin.com" crossorigin/>
<link rel="preload" href="/assets/css/site.css" as="style"/>"""

NAV_RE = re.compile(
    r'<nav aria-label="Main navigation" class="nav-links">[\s\S]*?</nav>',
    re.I,
)

OG_SVG_RE = re.compile(
    r'<meta property="og:image" content="https://multilogin-labs\.github\.io/assets/img/og-lab\.svg"/>'
)


def add_body_class(text: str, cls: str) -> str:
    if cls in text:
        return text
    return text.replace("<body>", f'<body class="{cls}">', 1).replace(
        "<body\n", f'<body class="{cls}"\n', 1
    )


def add_perf_hints(text: str) -> str:
    if "dns-prefetch" in text and "multilogin.com" in text:
        return text
    if "<!-- mll-head -->" in text:
        return text.replace("<!-- mll-head -->", f"<!-- mll-head -->\n{PERF_HINTS}", 1)
    return text


def fix_og_image(text: str) -> str:
    text = OG_SVG_RE.sub(f'<meta property="og:image" content="{OG_PROMO}"/>', text)
    text = text.replace(
        'name="twitter:image" content="https://multilogin-labs.github.io/assets/img/og-lab.svg"',
        f'name="twitter:image" content="{OG_PROMO}"',
    )
    return text


def add_sticky(text: str) -> str:
    if "aff-sticky" in text:
        return text
    return text.replace("</footer>", STICKY + "\n</footer>", 1)


def patch_file(path: Path, body_class: str = "aff-page") -> bool:
    raw = path.read_text(encoding="utf-8")
    new = raw
    new = NAV_RE.sub(AFF_NAV, new, count=1)
    new = add_body_class(new, body_class)
    new = add_perf_hints(new)
    new = fix_og_image(new)
    new = add_sticky(new)
    if new != raw:
        path.write_text(new, encoding="utf-8")
        return True
    return False


def patch_promo_content(path: Path) -> bool:
    raw = path.read_text(encoding="utf-8")
    new = re.sub(
        r"<section class=\"section\">\s*<div class=\"panel\">\s*"
        r"<p class=\"section-kicker\">New Decision Layer</p>[\s\S]*?</section>\s*",
        "",
        raw,
        count=1,
    )
    new = new.replace(
        "<h1>Antidetect Browser Promo Verification Hub 2026</h1>",
        "<h1>Multilogin SAAS50 + MIN50 — plus 22 vendor promos</h1>",
        1,
    )
    new = new.replace(
        "Each vendor page now includes a dedicated risk model",
        "<strong>Start with Multilogin:</strong> SAAS50 for plans, MIN50 for cloud phone. "
        "Other vendors include a risk model",
        1,
    )
    if new == raw:
        return False
    path.write_text(new, encoding="utf-8")
    return True


def main() -> None:
    # Homepage is optimized separately (scripts/optimize_home.py) — do not patch index.html here.
    targets = [
        ROOT / "tools" / "multilogin-discount" / "index.html",
        ROOT / "promo" / "index.html",
        ROOT / "compare" / "multilogin-alternatives" / "index.html",
        ROOT / "tools" / "index.html",
    ]
    n = 0
    if patch_promo_content(ROOT / "promo" / "index.html"):
        n += 1
    for p in targets:
        if patch_file(p):
            n += 1
    print(f"Affiliate funnel patched: {n} pages")


if __name__ == "__main__":
    main()
