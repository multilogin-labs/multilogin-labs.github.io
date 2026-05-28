# Maintainers

This document is for people with merge rights on this repository.

## Responsibilities

- Keep the homepage performance lock intact (no `site.css` / `site.js` on `/`).
- Review PRs against `CONTRIBUTING.md` ground rules (no scraped vendor docs, client-side only).
- Run `python3 scripts/automate_site.py` before publishing benchmark months.
- Ensure CI is green before merging to `main`.

## Release cadence

| Cadence | Action |
|---------|--------|
| Per commit | `automate_site.py` (CI runs it; locally optional) |
| Monthly | Publish new `data/benchmark-2026-MM.json` + matrix |
| Quarterly | Refresh `data/affiliate.json` UTM if vendor changes |
| Yearly | Review noindex redirect stubs against GSC impressions |

## Local environment

```bash
python3 -m pip install --user ruff==0.5.7   # match CI version
python3 -m ruff check scripts                # lint
python3 scripts/automate_site.py             # full pipeline
```

## Homepage policy (locked)

| Aspect | Allowed | Forbidden |
|--------|---------|-----------|
| CSS | `assets/css/home.css` only | `site.css` (caused CLS ~0.39) |
| JS | `assets/js/home.js` only | `site.js` |
| Schema | FAQPage, VideoObject, ImageObject, Offer, HowTo | New types without `optimize_home.py` update |
| Affiliate | direct Multilogin pricing URL | `/go/multilogin` hop |

Any homepage edit must keep `python3 scripts/optimize_home.py` green and not
trip `automate_site.py`'s fingerprint diff.

## Decision log

Architectural decisions live in [`docs/DECISIONS.md`](./docs/DECISIONS.md).
Audit findings + research candidates in [`docs/RESEARCH-UPGRADES.md`](./docs/RESEARCH-UPGRADES.md).

## Communication

- Public discussion: GitHub Discussions
- Sensitive: `admin@multilogin-labs.github.io` (see `SECURITY.md`)
