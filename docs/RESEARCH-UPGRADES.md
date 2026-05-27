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
| `sync_affiliate_links.py` | Checkout URL + `/go/` hop |
| `upgrade_inner_site.py` | sponsored rel, catalog, ai.txt |
| `upgrade_sitewide.py` | announcement, prefetch, lab CTA |
| `upgrade_polish.py` | footers, OG compare, meta polish |
| `enhance_pages.py` | OG, breadcrumbs, dates |
| `optimize_home.py` | Homepage guardrails only |
