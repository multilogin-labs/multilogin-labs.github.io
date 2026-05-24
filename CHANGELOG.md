# Changelog

All notable changes to this repository are documented here.

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
