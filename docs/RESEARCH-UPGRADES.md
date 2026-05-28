# Research-driven upgrade log

Auto-maintained notes from sitewide audit passes. Run: `python3 scripts/automate_site.py`

## Site model (locked)

| Layer | Role | Do not |
|-------|------|--------|
| `/` | Affiliate LCP funnel (`home.css` only) | Add `site.css`, async theme |
| Inner pages | Lab + compare + tools (`site.css`) | Duplicate 50+ coupon URLs |
| `/go/multilogin/` | Noindex hop + JS redirect | Delete without GSC proof |
| `data/affiliate.json` | Single checkout URL source | Hardcode UTMs in HTML |

## Audit findings (2026-05-27)

1. **Affiliate** — Central config + sitewide pricing links; sponsored `rel` on monetized CTAs.
2. **Perf** — No Google Fonts; speculation prefetch to `multilogin.com/pricing`; dns-prefetch on inner pages.
3. **UX** — Announcement bar on guides/tools/compare; toast on copy-code pages; lab CTA on editorial pages without checkout block.
4. **SEO** — `max-image-preview:large` on indexable pages; compare pages use SAAS50 OG image; breadcrumbs via `enhance_pages.py`.
5. **Discovery** — `llms.txt`, `ai.txt`, RSS, 62-url sitemap including JSON datasets.

## Next research candidates

- GSC: which redirect stubs get 0 impressions → delete after 2027-05
- PageSpeed inner compare pages (target 90+ mobile)
- Ship full **June 2026** benchmark matrix (not preview)
- Optional: WebP OG for compare pages under 1200px width

## Scripts map

| Script | Purpose |
|--------|---------|
| `index_health.py` | Sitemap vs indexable coverage report (`docs/INDEX-HEALTH.md`) |
| `internal_link_audit.py` | Inlink/outlink graph summary (`docs/INTERNAL-LINK-AUDIT.md`) |
| `content_freshness.py` | Stale content SLA report (`docs/CONTENT-FRESHNESS.md`) |
| `normalize_jsonld.py` | Parse + revalidate + reformat every JSON-LD block (skip homepage) |
| `schema_coverage.py` | Sitewide schema audit (`docs/SCHEMA-COVERAGE.md`) |
| `a11y_check.py` | Sitewide a11y guard (lang, h1, skip-link, alt) |
| `upgrade_promo_pages.py` | Indexable promo detail pages with per-vendor research + cross-links |
| `indexability_audit.py` | Hard gate: robots + canonical + JSON-LD + title + description + sitemap |
| `link_safety.py` | Hard gate: sponsored on revenue anchors, noopener on target=_blank |
| `og_audit.py` | Hard gate: og:*, twitter:*, same-origin asset existence |
| `add_reading_time.py` | Reading-time meta + `timeRequired` schema on 25 guides |
| `sync_affiliate_links.py` | Checkout URL + `/go/` hop |
| `upgrade_inner_site.py` | sponsored rel, catalog, ai.txt |
| `upgrade_sitewide.py` | announcement, prefetch, lab CTA |
| `upgrade_polish.py` | footers, OG compare, meta polish |
| `enhance_pages.py` | OG, breadcrumbs, dates |
| `optimize_home.py` | Homepage guardrails only |

## Auto-generated reports

- `docs/INDEX-HEALTH.md`
- `docs/INTERNAL-LINK-AUDIT.md`
- `docs/CONTENT-FRESHNESS.md`
- `docs/SCHEMA-COVERAGE.md`
- `docs/INDEXABILITY.md`
