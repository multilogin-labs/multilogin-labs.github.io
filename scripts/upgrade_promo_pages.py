#!/usr/bin/env python3
"""Generate indexable promo detail pages from former redirect stubs."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://multilogin-labs.github.io"
PROMO_SLUGS = [
    "adblogin-promo-code",
    "adspower-promo-code",
    "bitbrowser-promo-code",
    "dashnull-promo-code",
    "discloak-promo-code",
    "dolphin-anty-coupon",
    "ghost-browser-promo-code",
    "gologin-discount-code",
    "hidemyacc-promo-code",
    "incogniton-promo-code",
    "indigo-browser-promo-code",
    "kameleo-promo-code",
    "linkensphere-promo-code",
    "morelogin-promo-code",
    "nstbrowser-promo-code",
    "octo-browser-promo-code",
    "roxybrowser-promo-code",
    "undetectable-promo-code",
    "vektort13-promo-code",
    "vmlogin-promo-code",
    "wade-browser-promo-code",
    "whologin-promo-code",
]


def humanize(slug: str) -> str:
    return slug.replace("-promo-code", "").replace("-discount-code", "").replace("-", " ").title()


def load_checkout_html() -> str:
    path = ROOT / "data" / "affiliate.json"
    if not path.exists():
        return "/go/multilogin/"
    raw = json.loads(path.read_text(encoding="utf-8")).get("multilogin_checkout", "/go/multilogin/")
    return raw.replace("&", "&amp;")


def page_html(slug: str, checkout: str) -> str:
    vendor = humanize(slug)
    today = date.today().isoformat()
    canonical = f"{BASE}/promo/{slug}/"
    anchor = f"/promo/#vendor-{slug}"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<!-- mll-head -->
<link rel="dns-prefetch" href="https://multilogin.com"/>
<link rel="preconnect" href="https://multilogin.com" crossorigin/>
<link rel="sitemap" type="application/xml" title="Sitemap" href="/sitemap.xml"/>
<link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml"/>
<link rel="manifest" href="/site.webmanifest"/>
<meta name="theme-color" content="#2a9d8f"/>
<title>{vendor} Promo Code Review (2026) | Better path: Multilogin SAAS50</title>
<meta name="description" content="{vendor} promo page with evidence-first buying checklist, risk notes, and a faster benchmarked path to Multilogin SAAS50/MIN50."/>
<meta name="robots" content="index,follow,max-image-preview:large"/>
<link rel="canonical" href="{canonical}"/>
<meta property="og:title" content="{vendor} Promo Code Review (2026)"/>
<meta property="og:description" content="Before using {vendor} promo codes, run evidence checks and compare with Multilogin SAAS50 verified path."/>
<meta property="og:url" content="{canonical}"/>
<meta property="og:type" content="article"/>
<meta property="og:site_name" content="multilogin-labs"/>
<meta property="og:image" content="https://multilogin-labs.github.io/assets/img/multilogin-saas50-1200.webp"/>
<meta property="og:image:width" content="1200"/>
<meta property="og:image:height" content="630"/>
<meta name="twitter:card" content="summary_large_image"/>
<meta name="twitter:image" content="https://multilogin-labs.github.io/assets/img/multilogin-saas50-1200.webp"/>
<meta property="og:locale" content="en_US"/>
<link href="/assets/css/site.css" rel="stylesheet"/>
<script type="application/ld+json">{{
  "@context":"https://schema.org",
  "@graph":[
    {{
      "@type":"Article",
      "headline":"{vendor} promo code review and alternatives",
      "datePublished":"2026-05-27",
      "dateModified":"{today}",
      "mainEntityOfPage":"{canonical}",
      "author":{{"@type":"Organization","name":"multilogin-labs"}},
      "publisher":{{"@type":"Organization","name":"multilogin-labs"}}
    }},
    {{
      "@type":"BreadcrumbList",
      "itemListElement":[
        {{"@type":"ListItem","position":1,"name":"Home","item":"{BASE}/"}},
        {{"@type":"ListItem","position":2,"name":"Promo","item":"{BASE}/promo/"}},
        {{"@type":"ListItem","position":3,"name":"{vendor} promo code","item":"{canonical}"}}
      ]
    }}
  ]
}}</script>
</head>
<body class="aff-page">
<!-- mll-promo-indexable -->
<a class="skip-link" href="#main-content">Skip to main content</a>
<div class="site-announcement">SAAS50 = <strong>50% off</strong> plans · MIN50 = cloud phone — <a href="{checkout}" rel="sponsored noopener noreferrer" target="_blank">Multilogin pricing →</a></div>
<header class="site-header">
<div class="container nav-wrap">
<a class="logo" href="/">multi<span>login-labs</span></a>
<nav aria-label="Main navigation" class="nav-links">
<a href="/">Home</a>
<a href="/promo/">Promo hub</a>
<a href="/compare/">Compare</a>
<a href="{checkout}" rel="sponsored noopener noreferrer" target="_blank">Checkout</a>
</nav>
</div>
</header>
<main class="container" id="main-content">
<p class="breadcrumb"><a href="/">Home</a> / <a href="/promo/">Promo</a> / {vendor}</p>
<section class="hero">
<span class="badge">Promo review</span>
<h1>{vendor} promo code: should you use it?</h1>
<p class="lead">This page is maintained to catch intent for "{vendor} promo code". Before checkout, verify reliability evidence and compare long-term risk/cost against Multilogin SAAS50.</p>
<p class="hero-meta">Updated: {today} · Evidence-first recommendation path.</p>
</section>
<section class="section">
<div class="panel">
<p class="section-kicker">Fast path</p>
<h2>Recommended next step for most teams</h2>
<p class="small">If your priority is stable operations and predictable discount proof, use the Multilogin evidence workflow:</p>
<div class="hero-actions">
<a class="btn btn-primary" href="/tools/multilogin-discount/">Open SAAS50 + MIN50 verifier</a>
<a class="btn btn-primary" href="{checkout}" rel="sponsored noopener noreferrer" target="_blank">Open official Multilogin pricing</a>
<a class="btn btn-ghost" href="/compare/multilogin-alternatives/">Compare alternatives first</a>
</div>
</div>
</section>
<section class="section">
<p class="section-kicker">Decision checklist</p>
<h2>Before using any promo code (including {vendor})</h2>
<ol class="clean">
<li>Run fingerprint + leak tests on your real proxy/session setup.</li>
<li>Compare monthly/annual total cost with migration risk in your workflow.</li>
<li>Only proceed when checkout clearly shows promo rows and invoice proof.</li>
</ol>
<p class="small">Guides: <a href="/guides/detection-tests/">detection tests</a> · <a href="/guides/connection-leak-tests/">connection leak tests</a> · <a href="/guides/antidetection-ops-sop/">ops SOP</a>.</p>
</section>
<section class="section">
<div class="related-links" aria-label="Related links">
<a href="{anchor}">Back to promo hub section</a>
<a href="/promo/">Promo verification hub</a>
<a href="/tools/multilogin-discount/">Multilogin discount verifier</a>
<a href="/compare/multilogin-alternatives/">Multilogin alternatives</a>
</div>
</section>
</main>
<footer class="site-footer">
<div class="container footer-bottom-row">
<p class="small">© <span data-year></span> multilogin-labs</p>
<div class="footer-mini-links">
<a href="/site-map/">HTML sitemap</a>
<a href="/catalog/">Catalog</a>
<a href="/guides/">Guides</a>
</div>
</div>
</footer>
<script defer src="/assets/js/site.js"></script>
<script type="speculationrules">{{"prefetch":[{{"source":"document","where":{{"href_matches":"*multilogin.com/pricing*"}},"eagerness":"moderate"}}]}}</script>
</body>
</html>
"""


def main() -> None:
    checkout = load_checkout_html()
    changed = 0
    for slug in PROMO_SLUGS:
        path = ROOT / "promo" / slug / "index.html"
        path.parent.mkdir(parents=True, exist_ok=True)
        new = page_html(slug, checkout)
        old = path.read_text(encoding="utf-8") if path.exists() else ""
        if old != new:
            path.write_text(new, encoding="utf-8")
            changed += 1
    print(f"Upgraded promo pages: {changed}")


if __name__ == "__main__":
    main()
