# Indexability Audit

- Indexable HTML pages: **73**
- Sitemap entries (HTML): **73**
- Sitemap entries (total): **84**
- Failures: **0**

## Failures
- None (every indexable page has robots, canonical, JSON-LD, title, description, and is in sitemap.xml).

## Coverage criteria

- `<meta name=robots>` with `max-image-preview:large`
- `<link rel=canonical>`
- At least one JSON-LD block
- Non-empty `<title>`
- `<meta name=description>` ≥ 30 chars
- URL present in `sitemap.xml`
- `robots.txt` lists the sitemap and does not block `/`
