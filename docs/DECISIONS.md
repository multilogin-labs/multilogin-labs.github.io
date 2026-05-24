# Locked decisions (auto policy)

These rules apply without per-change approval. Maintenance: `python3 scripts/site_maintenance.py`.

## Homepage only (`index.html`)

| Decision | Choice |
|----------|--------|
| Goal | **SAAS50 / MIN50** → `/go/multilogin/` |
| Stack | `home.css` + `home.js` only — **no `site.css`** (async `site.css` caused CLS ~0.39) |
| DOM | Slim: hero → 3 steps → pricing cards → FAQ → CTA |
| CI | `optimize_home.py` blocks regressions (no `site.css` / `site.js` on `/`) |
| Other scripts | `enhance_pages` / `aff_funnel` / `optimize_inner_pages` **do not modify** `/` |

## Inner pages (all other indexable HTML)

| Decision | Choice |
|----------|--------|
| Stack | Blocking `site.css` + deferred `site.js` (system fonts only) |
| CLS | No `content-visibility` on sections; sticky padding only when bar visible (`site.js`) |
| Maintenance | `optimize_inner_pages.py` — prefetch `/go/multilogin`, normalize CSS URLs, skip `/` |

## Content & SEO

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Vendor doc mirrors | **Never** | Duplicate content / deindex risk |
| Coupon / compare thin pages | **One hub each** + `noindex` redirects | Index only unique URLs |
| Tier-1 compare pages | **Keep 8 + alternatives** | High-intent, original methodology |
| Google verification | **Meta tag on home only** | Remove legacy `google*.html` files |
| Display ads | **No** | Removed `ads.txt` from clone |
| Sitemap | **~59 indexable URLs** | No redirect stubs, no `/go/` |

## Redirect stubs (~47 HTML files)

| Decision | Choice |
|----------|--------|
| Delete promo/compare redirects? | **No** — GitHub Pages has no server redirects |
| Template | **Single** `scripts/redirect_html.py` (`noindex,follow`) |
| Regenerate | `seo_optimize.py` on every maintenance run |
| Review for deletion | **Not before 2027-05** unless GSC shows zero hits 6+ months |

## Repo layout

| Decision | Choice |
|----------|--------|
| `CATALOG.md` + `/catalog/` | **Keep both** | GitHub discovery vs live site |
| `docs/GROWTH-PLAYBOOK.md` | **Keep** | Repo growth, not in sitemap |
| `docs/REPO_SETUP.md` | **Canonical** setup checklist |
| `scripts/inject_head.py` | **Removed** — one-shot done |
| `security.txt` | **Root only** (no `.well-known` duplicate) |
| IndexNow key | **Keep** `mll7f3a9c2e1b4d6085a2f9e0c7b3d6e8.txt` |

## CI / deploy

| Step | Tool |
|------|------|
| Full automation | `automate_site.py` (maintenance + llms + funnel; verifies `/` unchanged) |
| Validate + SEO | `site_maintenance.py` |
| LLM manifest | `generate_llms_txt.py` |
| IndexNow ping | `indexnow.py --from-sitemap` on push to `main` |
| Commit | **Human only** (not automated) |

## Data

| Decision | Choice |
|----------|--------|
| April 2026 matrix | **Published baseline** — do not overwrite |
| May 2026 | **Preview** until full report ships |
| Schema breaks | Bump `benchmark/v1` → `v2`, keep old files |

See also: [FILE-CLEANUP.md](./FILE-CLEANUP.md) · [GOOGLE-INDEXING.md](./GOOGLE-INDEXING.md)
