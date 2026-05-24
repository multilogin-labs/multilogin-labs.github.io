# Google indexing checklist (multilogin-labs)

Use after every deploy to `main` on GitHub Pages.

## 1. Search Console setup

1. Add property: `https://multilogin-labs.github.io/`
2. Verify via DNS or HTML file (`google*.html` in repo root)
3. Submit sitemap: `https://multilogin-labs.github.io/sitemap.xml`
4. Submit URL inspection for:
   - `/` (home)
   - `/site-map/` (HTML sitemap hub)
   - `/tools/benchmark-explorer/`
   - `/guides/evaluation-methodology/`
   - `/data/benchmark-matrix-2026-04.json`

## 2. What we index vs not

| Indexed (`index,follow`) | Not indexed (`noindex`) |
|--------------------------|-------------------------|
| ~47 HTML articles/tools/guides | `/go/multilogin/` (affiliate) |
| JSON datasets in sitemap | Legacy `/promo/*/` redirects |
| `/llms.txt` (optional) | Legacy `/compare/multilogin-vs-*` redirects |
| | `404.html` |

Redirect pages keep `noindex,follow` so Google consolidates signals to hub URLs.

## 3. Internal linking rules

- Promo vendors → `/promo/#vendor-{slug}` only
- Removed compares → `/compare/multilogin-alternatives/` or `/compare/`
- Every indexable page links to `/sitemap.xml` via `<link rel="sitemap">`
- HTML sitemap: `/site-map/`

## 4. Maintenance commands

```bash
python3 scripts/seo_optimize.py   # noindex redirects, fix links, refresh sitemaps
python3 scripts/check_links.py
python3 scripts/validate_data.py
```

## 5. Monthly content for crawl freshness

- Publish new `data/benchmark-matrix-YYYY-MM.json`
- Update `/guides/benchmark-reports/YYYY-MM/`
- Add option in Benchmark Explorer dataset dropdown
- Re-run `seo_optimize.py` (updates `lastmod` from file mtimes)

## 6. Avoid indexation drops

- Do not re-add thin per-vendor promo/compare HTML pages
- Do not duplicate Multilogin official docs
- Keep unique methodology + dataset + tool UX
