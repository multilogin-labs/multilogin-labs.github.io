# Changelog

All notable changes to this repository are documented here.

## [2026.05.27c] — Research polish pass

### Added
- `scripts/upgrade_polish.py` — footers, compare OG (SAAS50 image), robots preview, `data-year` fix
- `docs/RESEARCH-UPGRADES.md` — audit log + script map for maintainers

## [2026.05.27d] — Indexing observability automation

### Added
- `scripts/index_health.py` → `docs/INDEX-HEALTH.md` (sitemap coverage, orphan URLs, low inlinks)
- `scripts/internal_link_audit.py` → `docs/INTERNAL-LINK-AUDIT.md` (link graph summary)
- `scripts/content_freshness.py` → `docs/CONTENT-FRESHNESS.md` (staleness SLA)

### Changed
- `scripts/site_maintenance.py` now runs all 3 reports every cycle
- `docs/RESEARCH-UPGRADES.md` includes new scripts + report outputs

### Changed
- Thin-footers (procurement, catalog, …) → mini discovery links
- Tier-1 **compare/** pages: OG/Twitter image → `multilogin-saas50-1200.webp`
- ~45 pages: `data-year=""` → `data-year` (site.js fills year)
- `site-map/`: viewport, JSON-LD, robots preview, speculation rules
- `benchmark-explorer/`: footer links + pricing CTA in table note

## [2026.05.27b] — Sitewide UX upgrade

### Added
- `scripts/upgrade_sitewide.py` — announcement bar, lab CTA, toast, dns-prefetch, speculation rules on ~32 pages

### Changed
- Guides, about, contact, benchmark reports, tools hub: unified SAAS50 announcement + end-of-page lab CTA
- `site.css` — `.lab-cta` panel styling
- Skipped: homepage, privacy/terms, site-map, redirect stubs

## [2026.05.27] — Inner site upgrade batch

### Added
- `ai.txt` — pointer to llms.txt + canonical checkout URL
- `scripts/upgrade_inner_site.py` — sponsored rel, announcement bar, catalog cards, dns-prefetch

### Changed
- Compare/tools pages: `rel="sponsored"` on pricing links; unified announcement bar
- `/catalog/` — Multilogin discount card, May matrix note, procurement links
- Sitemap: `ai.txt`, `data/affiliate.json`
- `llms.txt` — full checkout URL from affiliate.json

## [2026.05.24m] — Affiliate pricing URL sitewide

### Added
- `data/affiliate.json` — single source for Multilogin pricing checkout URL
- `scripts/sync_affiliate_links.py` + `verify_affiliate.py` — sync inner pages; CI guard

### Changed
- `/go/multilogin/` — meta refresh + `location.replace()` to pricing URL (fixes stale hop)
- 23 inner pages: `/go/multilogin` → direct `multilogin.com/pricing` affiliate link
- Homepage unchanged (already direct pricing links)

## [2026.05.24k] — Homepage audit pass

### Changed (index.html only)
- CLS fix: checkout image `aspect-ratio` 1024×729, `object-fit: contain`
- Self-hosted YouTube thumb; removed i.ytimg.com on LCP path
- JSON-LD: BreadcrumbList, ImageObject, 5 FAQ items aligned with page, WebPage→FAQ link
- Proof strip (€9→€4.50), figcaption, clickable SAAS50 in H1, nav CTA pill
- Trimmed compare section; footer links; copy feedback on buttons

## [2026.05.24j] — Checkout proof image + YouTube redeem

### Added
- `multilogin-promo-code-saas50-checkout-proof` (jpg + webp 480/800/1024) — live SAAS50 screenshot
- Homepage: YouTube redeem tutorial ([youtu.be/pBd_7lASYdM](https://youtu.be/pBd_7lASYdM)) + VideoObject schema

## [2026.05.24i] — Homepage-only perf + SEO slim

### Added
- `assets/css/home.css` — critical CSS (~4KB) for first paint
- `assets/js/home.js` — copy codes, sticky CTA, idle-loaded gtag
- `scripts/optimize_home.py` — CI guardrails for home stack

### Changed
- `index.html` rebuilt: ~40% less DOM, async `site.css`, responsive LCP preload
- FAQ schema trimmed; enhance/aff scripts skip homepage

## [2026.05.24h] — Sitewide perf + aff funnel

### Added
- `scripts/optimize_perf.py` — strip Google Fonts + keywords meta (46 pages)
- `scripts/aff_funnel.py` — unified aff nav, sticky CTA, OG promo image
- Mobile sticky bar: Copy SAAS50 + checkout (home, promo, discount, alternatives)

### Changed
- System font stack sitewide (faster LCP on all pages)
- Promo hub + tools hub lead with Multilogin codes
- `site_maintenance.py` runs perf + aff scripts

## [2026.05.24g] — Homepage speed + SEO

### Added
- Responsive hero WebP (`multilogin-saas50-480/800/1200.webp`) — ~73% smaller LCP vs original
- Schema `Offer` (SAAS50/MIN50), `primaryImageOfPage`, `dateModified`
- Speculation Rules prefetch for `/go/multilogin`

### Changed
- No Google Fonts on home (system UI stack)
- gtag loads after first paint; preload LCP image + CSS
- `content-visibility: auto` on below-fold sections
- Removed duplicate JSON-LD Article block and `keywords` meta

## [2026.05.24f] — Homepage affiliate-first

### Changed
- Home repositioned: Multilogin SAAS50/MIN50 hero, checkout CTAs, proof FAQ
- Removed lab resources / GitHub star block from home (tools/guides remain at their URLs)
- Nav + footer tuned for promo → checkout → compare funnel

## [2026.05.24e] — Auto decisions locked

### Added
- `docs/DECISIONS.md` — policy log (redirects, SEO, data, CI)
- `scripts/site_maintenance.py` — one command for all checks
- `scripts/redirect_html.py` — single redirect template

### Changed
- `migrate_site.py` no longer overwrites redirects without `noindex`
- CI runs `site_maintenance.py`; `REPO_SETUP` → `docs/REPO_SETUP.md`
- `seo_optimize.py` normalizes `/antidetect-browsers/` redirect stub

## [2026.05.24d] — Repo cleanup

### Removed
- Legacy Google verification HTML files (meta tag on home is canonical)
- `ads.txt` (unused AdSense from clone)
- `scripts/inject_head.py` (one-shot, completed)
- Duplicate `.well-known/security.txt`
- `scripts/__pycache__/`

### Added
- `docs/FILE-CLEANUP.md` — what must stay vs safe to delete
- `.gitignore` — Python cache

## [2026.05.24c] — IndexNow, structured data, social meta

### Added
- `scripts/indexnow.py` + key file for Bing/Yandex instant crawl
- CI job: IndexNow ping on push to `main`
- Auto `BreadcrumbList` JSON-LD on pages missing it
- Full Twitter/OG tags on all indexable pages

### Changed
- `enhance_pages.py` syncs `dateModified` from file mtime
- `robots.txt` allows `/.well-known/`, `/humans.txt`
- Sitemap includes `/humans.txt`

## [2026.05.24b] — Social, discovery, indexing guide

### Added
- `scripts/enhance_pages.py` — OG image, RSS link, footer sitemap/catalog on all indexable pages
- Guide: `/guides/google-search-indexing/`
- `data/benchmark-2026-05.json` summary · `snippets/env-check.sh`
- `security.txt` (RFC 9116)

### Changed
- Snippets hub expanded · 404 links to HTML sitemap · RSS feed updated

## [2026.05.24] — Google indexing pass

### Added
- `scripts/seo_optimize.py` — noindex redirects, internal link fixes, HTML sitemap
- `/site-map/` HTML sitemap (55 indexable URLs)
- `docs/GOOGLE-INDEXING.md` Search Console checklist

### Changed
- All redirect stubs: `noindex,follow` + canonical to hub
- Internal links: promo anchors `#vendor-*`, dead compares → alternatives
- `sitemap.xml` uses per-file `lastmod` + `changefreq`
- 48 pages: `<link rel="sitemap">` discovery tag
- `compare/` hub: removed duplicate 22-page library block

## [2026.05.22c] — Benchmark Explorer + catalog

### Added
- Interactive **Benchmark Explorer** tool (`/tools/benchmark-explorer/`)
- `data/benchmark-matrix-2026-05.json` (preview) and `data/index.json` manifest
- `/catalog/` site index · Discussion template for benchmark requests
- `.github/REPO_SETUP.md` checklist

### Fixed
- Benchmark release checker form label typo

## [2026.05.22b] — Professional GitHub + lab polish

### Added
- `CATALOG.md` awesome-style index for GitHub discovery
- `llms.txt`, `humans.txt`, `site.webmanifest`, favicon + OG lab image
- `benchmark-matrix-2026-04.json` and JSON Schemas under `data/schemas/`
- MIT `LICENSE`, `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`
- GitHub Actions CI (link check + JSON validation)
- Issue/PR templates, `docs/GROWTH-PLAYBOOK.md`
- `/snippets/` index page

### Changed
- README redesigned for stars and quick-start
- Homepage GitHub CTA, metric strip, lab-focused Open Graph tags

## [2026.05.22] — Lab rebrand and deduplication

### Added
- Open datasets under `/data/` with JSON Schema definitions
- MLX API integration map (single canonical page, no doc mirrors)
- `/snippets/` automation starters
- `/go/multilogin/` sponsored checkout redirect
- `CATALOG.md` resource index for GitHub discovery
- `llms.txt` machine-readable site map for AI assistants
- GitHub Actions link validation workflow

### Changed
- Homepage positioned as **Antidetect Operations Lab**
- Promo hub consolidated to one indexable URL with vendor anchors
- Compare hub reduced to eight tier-1 head-to-head pages
- Brand unified to **multilogin-labs** (removed legacy clone branding)
- `sitemap.xml` trimmed to ~46 indexable URLs

### Removed
- 57 near-duplicate MLX API mirror pages (~59MB scraped assets)
- Cloned `antidetect.md` affiliate list from third-party source
