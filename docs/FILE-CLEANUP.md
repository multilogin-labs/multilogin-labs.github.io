# File cleanup guide

> **Auto policy:** see [DECISIONS.md](./DECISIONS.md) for locked choices (no approval needed).

What is safe to remove vs what must stay for SEO and old URLs.

## Safe to delete (already removed or one-off)

| File | Why |
|------|-----|
| `google17f3fdf209583844.html`, `google8cd87d8809c625dc.html` | Old Search Console file verification; site uses `<meta name="google-site-verification">` on `index.html` |
| `scripts/inject_head.py` | One-shot migration; all pages have `<!-- mll-head -->` |
| `scripts/__pycache__/` | Python cache; not in repo |
| `.well-known/security.txt` | Duplicate of root `security.txt` |
| `ads.txt` | AdSense from old clone; lab does not run display ads |

## Do not delete (unless you accept broken links)

| Pattern | Count | Role |
|---------|-------|------|
| `promo/*/index.html` (except `promo/index.html`) | 22 | `noindex` redirect → `/promo/#vendor-*` for legacy coupon URLs |
| `compare/multilogin-vs-*/index.html` (non tier-1) | ~30 | `noindex` redirect → `/compare/` or alternatives |
| `go/multilogin/index.html` | 1 | Affiliate hop (`noindex`) |
| `antidetect-browsers/index.html` | 1 | Redirect → `/tools/antidetect-browsers/` |
| `mll7f3a9c2e1b4d6085a2f9e0c7b3d6e8.txt` | 1 | **Required** for IndexNow |

GitHub Pages has no server-side redirects; these tiny HTML files are the correct pattern.

## Optional (repo-only, not served)

Keep on GitHub for contributors; not in sitemap:

- `docs/GROWTH-PLAYBOOK.md` — star/awesome strategy
- `docs/REPO_SETUP.md` — repo settings checklist
- `CATALOG.md` — mirrors `/catalog/`

## Auto decision (2026-05-24)

**Keep all ~47 redirect stubs until at least 2027-05.** Do not delete to “save files” — GitHub Pages needs them.

## If you want fewer files later

Only after 6–12 months with Search Console showing zero traffic on legacy paths:

1. Remove a redirect folder and accept **404** for that URL, or
2. Move to a host that supports bulk redirects (not native on GitHub Pages).

Do not delete tier-1 compare pages, guides, tools, or `/data/*.json`.
