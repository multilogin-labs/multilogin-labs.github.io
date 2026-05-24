#!/usr/bin/env python3
"""Align affiliate funnel pages: nav, OG image, perf hints, sticky CTA, proof blocks."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://multilogin-labs.github.io"
OG_PROMO = f"{BASE}/assets/img/multilogin-saas50-1200.webp"
OG_CHECKOUT = f"{BASE}/assets/img/multilogin-promo-code-saas50-checkout-proof-1024.webp"

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

DISCOUNT_PROOF_BLOCK = """
<section class="section" id="checkout-proof">
<div class="panel">
<p class="section-kicker">Checkout proof</p>
<h2>SAAS50 on official Multilogin billing</h2>
<figure class="hero-media">
<img alt="Multilogin checkout with SAAS50 applied showing 50 percent discount on order summary" decoding="async" height="729" loading="lazy" sizes="(max-width:720px) 100vw, min(92vw, 640px)" src="/assets/img/multilogin-promo-code-saas50-checkout-proof-800.webp" srcset="/assets/img/multilogin-promo-code-saas50-checkout-proof-480.webp 480w, /assets/img/multilogin-promo-code-saas50-checkout-proof-800.webp 800w, /assets/img/multilogin-promo-code-saas50-checkout-proof-1024.webp 1024w" width="1024"/>
<figcaption>Example: €9 → €4.50 subtotal — confirm your invoice shows the same promo line.</figcaption>
</figure>
<p class="small">Short redeem walkthrough: <a href="/#redeem-video">video on homepage</a> · <a href="https://www.youtube.com/watch?v=pBd_7lASYdM" rel="noopener noreferrer" target="_blank">YouTube</a></p>
</div>
</section>
<section class="section" id="redeem-video">
<div class="panel">
<p class="section-kicker">Video</p>
<h2>How to redeem SAAS50 at checkout</h2>
<a class="video-facade" href="https://www.youtube.com/watch?v=pBd_7lASYdM" rel="noopener noreferrer" target="_blank" title="Watch Multilogin SAAS50 redeem tutorial">
<img alt="Video thumbnail: redeem Multilogin SAAS50 at checkout" decoding="async" height="360" loading="lazy" src="/assets/img/multilogin-saas50-redeem-video-thumb.webp" width="480"/>
<span class="play-badge" aria-hidden="true"><span class="play-icon">▶</span> Watch on YouTube</span>
</a>
</div>
</section>
"""

PROMO_BENCHMARK_CALLOUT = """
<section class="section" id="lab-benchmark-may">
<div class="panel">
<p class="section-kicker">Open data</p>
<h2>May 2026 benchmark preview is live</h2>
<p class="small">Explore the <a href="/guides/benchmark-reports/2026-05/">May 2026 report preview</a> or load matrices in the <a href="/tools/benchmark-explorer/">Benchmark Explorer</a> (methodology v1.2).</p>
</div>
</section>
"""

NAV_RE = re.compile(
    r'<nav aria-label="Main navigation" class="nav-links">[\s\S]*?</nav>',
    re.I,
)

OG_SVG_RE = re.compile(
    r'<meta property="og:image" content="https://multilogin-labs\.github\.io/assets/img/og-lab\.svg"/>'
)

SCORE_CARD_TYPO = re.compile(
    r'<div class="score-card"><b>50%</b><span>></span></div>',
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


def fix_og_image(text: str, image_url: str = OG_PROMO) -> str:
    text = OG_SVG_RE.sub(f'<meta property="og:image" content="{image_url}"/>', text)
    text = text.replace(
        'name="twitter:image" content="https://multilogin-labs.github.io/assets/img/og-lab.svg"',
        f'name="twitter:image" content="{image_url}"',
    )
    if "og:image:width" not in text and "checkout-proof" in image_url:
        text = text.replace(
            f'<meta property="og:image" content="{image_url}"/>',
            f'<meta property="og:image" content="{image_url}"/>\n'
            f'<meta property="og:image:width" content="1024"/>\n'
            f'<meta property="og:image:height" content="729"/>',
            1,
        )
    return text


def add_sticky(text: str) -> str:
    if "aff-sticky" in text:
        return text
    return text.replace("</footer>", STICKY + "\n</footer>", 1)


def patch_discount_extras(text: str) -> str:
    new = SCORE_CARD_TYPO.sub(
        '<div class="score-card"><b>50%</b><span>Plan discount with SAAS50</span></div>',
        text,
    )
    if 'id="checkout-proof"' not in new:
        new = new.replace(
            "</section>\n<section class=\"section\">\n<div class=\"panel grid-2\">",
            "</section>\n" + DISCOUNT_PROOF_BLOCK + "\n<section class=\"section\">\n<div class=\"panel grid-2\">",
            1,
        )
    return new


def patch_file(path: Path, body_class: str = "aff-page", og_image: str = OG_PROMO) -> bool:
    raw = path.read_text(encoding="utf-8")
    new = raw
    new = NAV_RE.sub(AFF_NAV, new, count=1)
    new = add_body_class(new, body_class)
    new = add_perf_hints(new)
    new = fix_og_image(new, og_image)
    new = add_sticky(new)
    if path.name == "index.html" and "multilogin-discount" in path.as_posix():
        new = patch_discount_extras(new)
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
    if 'id="lab-benchmark-may"' not in new:
        marker = '<p class="section-kicker">Directory</p>'
        if marker in new:
            new = new.replace(
                marker,
                PROMO_BENCHMARK_CALLOUT.strip() + "\n" + marker,
                1,
            )
    if new == raw:
        return False
    path.write_text(new, encoding="utf-8")
    return True


def main() -> None:
    # Homepage is optimized separately (scripts/optimize_home.py) — do not patch index.html here.
    targets = [
        (ROOT / "tools" / "multilogin-discount" / "index.html", OG_CHECKOUT),
        (ROOT / "promo" / "index.html", OG_PROMO),
        (ROOT / "compare" / "multilogin-alternatives" / "index.html", OG_PROMO),
        (ROOT / "tools" / "index.html", OG_PROMO),
    ]
    n = 0
    if patch_promo_content(ROOT / "promo" / "index.html"):
        n += 1
    for path, og in targets:
        if patch_file(path, og_image=og):
            n += 1
    print(f"Affiliate funnel patched: {n} pages")


if __name__ == "__main__":
    main()
