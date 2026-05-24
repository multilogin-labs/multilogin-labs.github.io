# Locked decisions (auto policy)

These rules apply without per-change approval. Maintenance: `python3 scripts/site_maintenance.py`.

## Homepage (affiliate-first)

| Decision | Choice |
|----------|--------|
| Primary goal | **Multilogin SAAS50 / MIN50 conversion** via `/go/multilogin/` |
| On home | Promo hero, proof, pricing, FAQ, compare teasers |
| Off home (kept at URLs) | Tools, guides, datasets — linked from footer/promo only |
| Lab GitHub CTA on home | **Removed** — not part of aff funnel |
| Home performance | System fonts, responsive WebP srcset, `content-visibility`, deferred gtag |
| Home SEO | Single JSON-LD `@graph`, `Offer` + `FAQPage`, no `keywords` meta |
| Sitewide fonts | **Removed** Google Fonts — `optimize_perf.py` on every build |
| Aff funnel pages | Home, promo, discount proof, alternatives, tools hub — sticky CTA + unified nav |

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
| Validate + SEO | `site_maintenance.py` |
| IndexNow ping | `indexnow.py --from-sitemap` on push to `main` |
| Commit | **Human only** (not automated) |

## Data

| Decision | Choice |
|----------|--------|
| April 2026 matrix | **Published baseline** — do not overwrite |
| May 2026 | **Preview** until full report ships |
| Schema breaks | Bump `benchmark/v1` → `v2`, keep old files |

See also: [FILE-CLEANUP.md](./FILE-CLEANUP.md) · [GOOGLE-INDEXING.md](./GOOGLE-INDEXING.md)
