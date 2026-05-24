# Changelog

All notable changes to this repository are documented here.

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
