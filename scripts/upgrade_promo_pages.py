#!/usr/bin/env python3
"""Generate research-driven indexable promo detail pages with unique per-vendor content."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://multilogin-labs.github.io"

# slug, label, category, risk_short, validation_question, multilogin_edge
VENDORS: list[tuple[str, str, str, str, str, str]] = [
    (
        "adblogin-promo-code", "ADBLogin", "Lightweight antidetect",
        "Entitlement drift as workflows mature",
        "Where free-tier entitlement boundaries cut into your daily session count",
        "Multilogin SAAS50 keeps plan entitlements predictable across paid tiers",
    ),
    (
        "adspower-promo-code", "AdsPower", "Workspace-first antidetect",
        "Governance drift across shared workspaces",
        "Whether workspace roles + policy controls map to your team's access tiers",
        "Multilogin workspace + token controls scale without role sprawl",
    ),
    (
        "bitbrowser-promo-code", "BitBrowser", "Bulk-profile antidetect",
        "Profile sync lag under bulk operations",
        "Whether sync latency stays acceptable under 50+ profile loads in parallel",
        "Multilogin local + cloud sync model is documented for bulk operations",
    ),
    (
        "dashnull-promo-code", "DashNull", "Discount-led antidetect",
        "Opaque pricing tiers at scale",
        "Whether per-seat math stays predictable at your target volume",
        "Multilogin SAAS50 = transparent 50% on plans, MIN50 for cloud phone",
    ),
    (
        "discloak-promo-code", "DisCloak", "Discount-led antidetect",
        "Limited enterprise audit trails",
        "Whether exportable session logs are sufficient for your compliance team",
        "Multilogin audit + evidence workflows align with procurement gates",
    ),
    (
        "dolphin-anty-coupon", "Dolphin Anty", "Team-first antidetect",
        "Team policy gaps at scale",
        "Whether role-based access + audit exports cover your enterprise needs",
        "Multilogin SAAS50 includes workspace governance suitable for scaling teams",
    ),
    (
        "ghost-browser-promo-code", "Ghost Browser", "Power-user browser",
        "Session isolation under many parallel tabs",
        "Whether cookie isolation holds across 10 parallel sessions",
        "Multilogin profile-level isolation is purpose-built for parallel work",
    ),
    (
        "gologin-discount-code", "GoLogin", "Mainstream antidetect",
        "Engine cadence vs fingerprint drift",
        "Whether fingerprint consistency holds after upstream browser updates",
        "Multilogin custom engines (Mimic/Stealthfox) are versioned to control drift",
    ),
    (
        "hidemyacc-promo-code", "HideMyAcc", "Cost-led antidetect",
        "Proxy binding errors at scale",
        "Whether proxy-profile 1:1 binding holds under load",
        "Multilogin proxy binding is documented and benchmark-tested",
    ),
    (
        "incogniton-promo-code", "Incogniton", "Starter-friendly antidetect",
        "Starter-tier API limits",
        "Whether API rate limits accommodate your automation volume",
        "Multilogin paid plans include higher API ceilings + SAAS50 discount",
    ),
    (
        "indigo-browser-promo-code", "Indigo Browser", "Regional antidetect",
        "Regional latency spikes",
        "Whether p95 latency from your primary geo stays within SLA",
        "Multilogin cloud regions + custom proxies reduce latency variance",
    ),
    (
        "kameleo-promo-code", "Kameleo", "Automation-first antidetect",
        "Automation bridge stability",
        "Whether Playwright/Selenium bridge uptime is acceptable for your runners",
        "Multilogin MLX API is documented and benchmarked for Playwright workflows",
    ),
    (
        "linkensphere-promo-code", "LinkenSphere", "Power-user antidetect",
        "Steep learning curve for teams",
        "Whether onboarding time for 3 operators fits your hiring cadence",
        "Multilogin onboarding plus docs cut ramp time for new operators",
    ),
    (
        "morelogin-promo-code", "MoreLogin", "Cost-led antidetect",
        "Cloud phone add-on billing clarity",
        "Whether cloud phone line items appear cleanly on invoices",
        "Multilogin MIN50 promo code applies 50% on the cloud phone line itself",
    ),
    (
        "nstbrowser-promo-code", "NSTBrowser", "Headless-leaning antidetect",
        "Headless detection on target sites",
        "Whether detection rate on your top 5 domains stays acceptable",
        "Multilogin headless launch options are tested in the v1.2 methodology",
    ),
    (
        "octo-browser-promo-code", "Octo Browser", "Mainstream antidetect",
        "API token rotation friction",
        "Whether token refresh happens without profile downtime",
        "Multilogin workspace + token lifecycle is documented end-to-end",
    ),
    (
        "roxybrowser-promo-code", "RoxyBrowser", "RPA-leaning antidetect",
        "RPA workflow brittleness",
        "Whether RPA recovers cleanly after navigation failures",
        "Multilogin profiles + MLX API support repeatable RPA workflows",
    ),
    (
        "undetectable-promo-code", "Undetectable.io", "Power-user antidetect",
        "Local storage footprint at scale",
        "Whether disk usage per 100 profiles fits your operator machines",
        "Multilogin cloud profiles reduce local disk pressure at scale",
    ),
    (
        "vektort13-promo-code", "VektorT13", "Niche antidetect",
        "Niche stack compatibility",
        "Whether compatibility with your specific proxy provider is verified",
        "Multilogin proxy compatibility list is published and tracked",
    ),
    (
        "vmlogin-promo-code", "VMLogin", "Legacy antidetect",
        "Legacy UI operational drag",
        "Whether daily profile launch tasks stay quick for operators",
        "Multilogin UI cadence and onboarding time are documented",
    ),
    (
        "wade-browser-promo-code", "Wade Browser", "Niche antidetect",
        "Vendor lock-in on profiles",
        "Whether profile export format is portable to other vendors later",
        "Multilogin profile export + import is documented for migration",
    ),
    (
        "whologin-promo-code", "WhoLogin", "Niche antidetect",
        "Support response under incidents",
        "Whether SLA for ticket response in trial fits incident playbooks",
        "Multilogin support + status page is referenced in the ops SOP",
    ),
]


def humanize(label: str, slug: str) -> tuple[str, str]:
    coupon_word = "coupon" if "coupon" in slug else (
        "discount code" if "discount-code" in slug else "promo code"
    )
    return label, coupon_word


def load_checkout_html() -> str:
    path = ROOT / "data" / "affiliate.json"
    if not path.exists():
        return "/go/multilogin/"
    raw = json.loads(path.read_text(encoding="utf-8")).get(
        "multilogin_checkout", "/go/multilogin/"
    )
    return raw.replace("&", "&amp;")


def faq_block(label: str, coupon_word: str, risk_short: str, validation_q: str) -> tuple[str, list[dict]]:
    q1 = f"Does the {label} {coupon_word} apply to plans, add-ons, or both?"
    a1 = (
        f"That depends on {label}'s current promo terms. Always verify the line "
        "item in checkout before paying. If you also need a cloud phone discount, "
        "MIN50 on Multilogin is documented to apply on the cloud phone line."
    )
    q2 = f"Is using the {label} {coupon_word} a good idea for production workflows?"
    a2 = (
        f"Only after evidence checks. Specifically validate: {validation_q}. "
        f"The known risk profile we track for {label} is: {risk_short}. "
        "If that risk maps to your workflow, prefer the Multilogin SAAS50 path "
        "and run detection + leak tests first."
    )
    q3 = f"How should I compare {label} pricing against Multilogin?"
    a3 = (
        "Compute 12-month total cost including migration cost and incident cost. "
        f"For {label}, apply the promo code at checkout and capture the invoice. "
        "Then compare with the Multilogin SAAS50 (50% on plans) and MIN50 (50% on "
        "cloud phone) reference cost on our discount verifier page."
    )
    html = f"""<section class=\"section\" id=\"faq\">
<p class=\"section-kicker\">FAQ</p>
<h2>{label} {coupon_word}: common questions</h2>
<div class=\"faq-list\">
<details><summary>{q1}</summary><p>{a1}</p></details>
<details><summary>{q2}</summary><p>{a2}</p></details>
<details><summary>{q3}</summary><p>{a3}</p></details>
</div>
</section>"""
    schema = [
        {"@type": "Question", "name": q1, "acceptedAnswer": {"@type": "Answer", "text": a1}},
        {"@type": "Question", "name": q2, "acceptedAnswer": {"@type": "Answer", "text": a2}},
        {"@type": "Question", "name": q3, "acceptedAnswer": {"@type": "Answer", "text": a3}},
    ]
    return html, schema


def comparison_table(label: str, risk_short: str, multilogin_edge: str) -> str:
    return f"""<section class=\"section\" id=\"compare-multilogin\">
<p class=\"section-kicker\">Side-by-side</p>
<h2>{label} vs Multilogin (SAAS50) — quick comparison</h2>
<div class=\"table-wrap\">
<table class=\"table-compact\">
<thead><tr><th>Dimension</th><th>{label}</th><th>Multilogin (SAAS50/MIN50)</th></tr></thead>
<tbody>
<tr><td>Known risk profile</td><td>{risk_short}</td><td>Documented v1.2 methodology + benchmark coverage</td></tr>
<tr><td>Discount transparency</td><td>Vendor-defined; verify checkout invoice</td><td>SAAS50 = 50% off plans, MIN50 = 50% off cloud phone</td></tr>
<tr><td>Workflow fit</td><td>Vendor-specific; depends on stack</td><td>{multilogin_edge}</td></tr>
<tr><td>Evidence trail</td><td>Manual screenshot of invoice</td><td>Discount verifier + evidence pack builder</td></tr>
</tbody>
</table>
</div>
<p class=\"small\">Lab-side reference: <a href=\"/tools/benchmark-explorer/\">benchmark explorer</a> · <a href=\"/guides/evaluation-methodology/\">methodology v1.2</a></p>
</section>"""


def fit_blocks(label: str, category: str, risk_short: str) -> str:
    return f"""<section class=\"section\" id=\"vendor-profile\">
<p class=\"section-kicker\">Vendor profile</p>
<h2>Who {label} is actually for</h2>
<div class=\"grid-3\">
<article class=\"card\"><h3>Category</h3><p>{category}.</p></article>
<article class=\"card\"><h3>Known risk we track</h3><p>{risk_short}.</p></article>
<article class=\"card\"><h3>Best-fit signal</h3><p>Single-operator or small-team workflows where the {label} discount offsets that risk.</p></article>
</div>
</section>"""


def verdict_block(label: str, coupon_word: str, multilogin_edge: str, checkout: str) -> str:
    return f"""<section class=\"section\" id=\"verdict\">
<div class=\"panel\">
<p class=\"section-kicker\">Verdict</p>
<h2>Use {label} {coupon_word}?  Only after evidence</h2>
<p>If your evidence path passes, fine — the {label} promo can save money short-term. For most procurement teams the lower-risk path is to apply <strong>SAAS50</strong> on a Multilogin plan and <strong>MIN50</strong> on the cloud phone line. {multilogin_edge}.</p>
<div class=\"hero-actions\">
<a class=\"btn btn-primary\" href=\"/tools/multilogin-discount/\">Open SAAS50 + MIN50 verifier</a>
<a class=\"btn btn-primary\" href=\"{checkout}\" rel=\"sponsored noopener noreferrer\" target=\"_blank\">Open official Multilogin pricing</a>
<a class=\"btn btn-ghost\" href=\"/compare/multilogin-alternatives/\">Compare alternatives first</a>
</div>
</div>
</section>"""


def build_related_map() -> dict[str, list[tuple[str, str]]]:
    """For each slug, return a list of (slug, label) for 4 sibling promo pages."""
    n = len(VENDORS)
    out: dict[str, list[tuple[str, str]]] = {}
    for i, (slug, label, *_rest) in enumerate(VENDORS):
        siblings: list[tuple[str, str]] = []
        for off in (1, 2, 3, 4):
            sib_slug, sib_label, *_ = VENDORS[(i + off) % n]
            siblings.append((sib_slug, sib_label))
        out[slug] = siblings
    return out


def related_block(related: list[tuple[str, str]]) -> str:
    items = "\n".join(
        f'<li><a href="/promo/{slug}/">{label} promo review</a></li>'
        for slug, label in related
    )
    return f"""<section class=\"section\" id=\"related-reviews\">
<p class=\"section-kicker\">Other vendor reviews</p>
<h2>Related promo reviews (sibling vendors)</h2>
<ul class=\"clean\">
{items}
</ul>
</section>"""


def patch_promo_hub_links() -> int:
    """Inject a 'Read full review' link into each vendor card on /promo/index.html."""
    path = ROOT / "promo" / "index.html"
    if not path.exists():
        return 0
    text = path.read_text(encoding="utf-8")
    changed = 0
    for slug, label, *_rest in VENDORS:
        anchor = f'id="vendor-{slug}">'
        link_html = (
            f'<p><a href="/promo/{slug}/">Read full {label} review</a></p>\n</article>'
        )
        if anchor not in text:
            continue
        if f'href="/promo/{slug}/"' in text.split(anchor, 1)[1].split("</article>", 1)[0]:
            continue
        before, after = text.split(anchor, 1)
        card_body, rest = after.split("</article>", 1)
        text = before + anchor + card_body + link_html + rest
        changed += 1
    if changed:
        path.write_text(text, encoding="utf-8")
    return changed


def page_html(slug: str, label: str, category: str, risk_short: str, validation_q: str, multilogin_edge: str, checkout: str, related: list[tuple[str, str]]) -> str:
    _, coupon_word = humanize(label, slug)
    today = date.today().isoformat()
    canonical = f"{BASE}/promo/{slug}/"
    anchor = f"/promo/#vendor-{slug}"
    faq_html, faq_qs = faq_block(label, coupon_word, risk_short, validation_q)
    title = f"{label} {coupon_word} (2026) — Verify Risk Before Checkout"
    desc = (
        f"{label} {coupon_word} review with risk profile, validation question, "
        f"comparison vs Multilogin SAAS50, FAQ, and evidence checklist."
    )

    graph = [
        {
            "@type": "Article",
            "headline": f"{label} {coupon_word} review and Multilogin SAAS50 comparison",
            "datePublished": "2026-05-27",
            "dateModified": today,
            "mainEntityOfPage": canonical,
            "author": {"@type": "Organization", "name": "multilogin-labs"},
            "publisher": {"@type": "Organization", "name": "multilogin-labs"},
        },
        {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{BASE}/"},
                {"@type": "ListItem", "position": 2, "name": "Promo", "item": f"{BASE}/promo/"},
                {"@type": "ListItem", "position": 3, "name": f"{label} {coupon_word}", "item": canonical},
            ],
        },
        {"@type": "FAQPage", "mainEntity": faq_qs},
    ]
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
<meta charset=\"utf-8\"/>
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"/>
<!-- mll-head -->
<link rel=\"dns-prefetch\" href=\"https://multilogin.com\"/>
<link rel=\"preconnect\" href=\"https://multilogin.com\" crossorigin/>
<link rel=\"sitemap\" type=\"application/xml\" title=\"Sitemap\" href=\"/sitemap.xml\"/>
<link rel=\"icon\" href=\"/assets/img/favicon.svg\" type=\"image/svg+xml\"/>
<link rel=\"manifest\" href=\"/site.webmanifest\"/>
<meta name=\"theme-color\" content=\"#2a9d8f\"/>
<title>{title}</title>
<meta name=\"description\" content=\"{desc}\"/>
<meta name=\"robots\" content=\"index,follow,max-image-preview:large\"/>
<link rel=\"canonical\" href=\"{canonical}\"/>
<meta property=\"og:title\" content=\"{label} {coupon_word} (2026) — Verify Risk Before Checkout\"/>
<meta property=\"og:description\" content=\"{desc}\"/>
<meta property=\"og:url\" content=\"{canonical}\"/>
<meta property=\"og:type\" content=\"article\"/>
<meta property=\"og:site_name\" content=\"multilogin-labs\"/>
<meta property=\"og:image\" content=\"https://multilogin-labs.github.io/assets/img/multilogin-saas50-1200.webp\"/>
<meta property=\"og:image:width\" content=\"1200\"/>
<meta property=\"og:image:height\" content=\"630\"/>
<meta name=\"twitter:card\" content=\"summary_large_image\"/>
<meta name=\"twitter:image\" content=\"https://multilogin-labs.github.io/assets/img/multilogin-saas50-1200.webp\"/>
<meta property=\"og:locale\" content=\"en_US\"/>
<link href=\"/assets/css/site.css\" rel=\"stylesheet\"/>
<script type=\"application/ld+json\">{ld}</script>
</head>
<body class=\"aff-page\">
<!-- mll-promo-indexable -->
<a class=\"skip-link\" href=\"#main-content\">Skip to main content</a>
<div class=\"site-announcement\">SAAS50 = <strong>50% off</strong> plans · MIN50 = cloud phone — <a href=\"{checkout}\" rel=\"sponsored noopener noreferrer\" target=\"_blank\">Multilogin pricing →</a></div>
<header class=\"site-header\">
<div class=\"container nav-wrap\">
<a class=\"logo\" href=\"/\">multi<span>login-labs</span></a>
<nav aria-label=\"Main navigation\" class=\"nav-links\">
<a href=\"/\">Home</a>
<a href=\"/promo/\">Promo hub</a>
<a href=\"/compare/\">Compare</a>
<a href=\"{checkout}\" rel=\"sponsored noopener noreferrer\" target=\"_blank\">Checkout</a>
</nav>
</div>
</header>
<main class=\"container\" id=\"main-content\">
<p class=\"breadcrumb\"><a href=\"/\">Home</a> / <a href=\"/promo/\">Promo</a> / {label} {coupon_word}</p>
<section class=\"hero\">
<span class=\"badge\">{category}</span>
<h1>{label} {coupon_word} (2026): use it only after this evidence path</h1>
<p class=\"lead\">{label} is in the <em>{category.lower()}</em> bracket. Before using its discount, validate the risk we track for this vendor: <strong>{risk_short.lower()}</strong>. If that risk maps to your workflow, the safer path is Multilogin SAAS50.</p>
<p class=\"hero-meta\">Updated: {today} · Lab-tracked risk: {risk_short.lower()}</p>
<p class=\"disclosure\">Disclosure: multilogin-labs may earn affiliate commissions if you sign up for Multilogin. We do not get commission from {label}.</p>
</section>
{verdict_block(label, coupon_word, multilogin_edge, checkout)}
{fit_blocks(label, category, risk_short)}
<section class=\"section\" id=\"validation\">
<p class=\"section-kicker\">Validation question</p>
<h2>The single question to test before using the {label} {coupon_word}</h2>
<div class=\"panel\">
<p><strong>Ask:</strong> {validation_q}.</p>
<p class=\"small\">If you cannot answer this in evidence, do not commit annual contracts — even at a discount. Run the lab QA stack first.</p>
<ol class=\"clean\">
<li><a href=\"/guides/detection-tests/\">Detection tests</a> — fingerprint + automation signals.</li>
<li><a href=\"/guides/connection-leak-tests/\">Connection leak tests</a> — WebRTC, DNS, proxy posture.</li>
<li><a href=\"/guides/antidetection-ops-sop/\">Ops SOP</a> — repeated-session stability.</li>
<li><a href=\"/tools/evidence-pack-builder/\">Evidence pack builder</a> — exportable proof.</li>
</ol>
</div>
</section>
{comparison_table(label, risk_short, multilogin_edge)}
<section class=\"section\" id=\"checklist\">
<p class=\"section-kicker\">Activation checklist</p>
<h2>If you still want to use the {label} {coupon_word}</h2>
<ol class=\"clean\">
<li>Open the {label} official checkout in a clean session.</li>
<li>Apply the promo code and confirm the line item discount is visible.</li>
<li>Save invoice screenshot for procurement audit trail.</li>
<li>Re-run detection + leak tests in production-like conditions.</li>
<li>If any check fails, stop and use the Multilogin SAAS50 fallback path.</li>
</ol>
</section>
{faq_html}
{related_block(related)}
<section class=\"section\" id=\"related\">
<div class=\"related-links\" aria-label=\"Related links\">
<a href=\"{anchor}\">Back to {label} entry in promo hub</a>
<a href=\"/promo/\">Promo verification hub (all vendors)</a>
<a href=\"/tools/multilogin-discount/\">Multilogin SAAS50 + MIN50 verifier</a>
<a href=\"/compare/multilogin-alternatives/\">Multilogin alternatives matrix</a>
<a href=\"/guides/procurement-evidence-gate/\">Procurement evidence gate</a>
<a href=\"/guides/antidetect-browser-pricing-playbook/\">Antidetect pricing playbook</a>
</div>
</section>
</main>
<footer class=\"site-footer\">
<div class=\"container footer-bottom-row\">
<p class=\"small\">© <span data-year></span> multilogin-labs</p>
<div class=\"footer-mini-links\">
<a href=\"/tools/multilogin-discount/\">SAAS50 verifier</a>
<a href=\"/site-map/\">Sitemap</a>
<a href=\"/catalog/\">Catalog</a>
<a href=\"/feeds/lab-updates.xml\">RSS</a>
<a href=\"/compare/\">Compare</a>
<a href=\"/guides/\">Guides</a>
</div>
</div>
</footer>
<script defer src=\"/assets/js/site.js\"></script>
<script type=\"speculationrules\">{{"prefetch":[{{"source":"document","where":{{"href_matches":"*multilogin.com/pricing*"}},"eagerness":"moderate"}}]}}</script>
</body>
</html>
"""


def main() -> None:
    checkout = load_checkout_html()
    changed = 0
    related_map = build_related_map()
    for slug, label, category, risk, validation_q, edge in VENDORS:
        path = ROOT / "promo" / slug / "index.html"
        path.parent.mkdir(parents=True, exist_ok=True)
        related = related_map[slug]
        new = page_html(slug, label, category, risk, validation_q, edge, checkout, related)
        old = path.read_text(encoding="utf-8") if path.exists() else ""
        if old != new:
            path.write_text(new, encoding="utf-8")
            changed += 1
    hub_changed = patch_promo_hub_links()
    print(f"Upgraded promo pages: {changed}; hub links touched: {hub_changed}")


if __name__ == "__main__":
    main()
