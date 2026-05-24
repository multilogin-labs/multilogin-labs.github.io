# Contributing to multilogin-labs

Thank you for helping improve the open antidetect operations lab.

## What we accept

| Type | Examples |
|------|----------|
| **Datasets** | New benchmark months, checklist schema updates with version bump |
| **Tools** | Client-side calculators that work on GitHub Pages (no backend) |
| **Guides** | Original playbooks with reproducible steps—not vendor doc copies |
| **Fixes** | Broken links, accessibility, schema validation, typos |

## What we do not accept

- Scraped or rewritten vendor documentation (duplicate content risk)
- Affiliate-only landing pages without methodology or evidence gates
- Malware, circumvention tooling, or policy-violating automation

## Pull request checklist

1. Run local preview: `python3 -m http.server 8080`
2. `python3 scripts/automate_site.py` (recommended; locks homepage) or `python3 scripts/site_maintenance.py`
3. If you changed URL inventory only, `python3 scripts/migrate_site.py` then re-run maintenance
4. Add an entry to `CHANGELOG.md` under `[Unreleased]` or the current date tag
5. For new JSON in `/data/`, include or update schema under `/data/schemas/`

## Dataset versioning

- Bump `schema` field (e.g. `multilogin-labs/benchmark/v1` → `v2`) on breaking changes
- Keep prior month files; do not overwrite published benchmark IDs

## Code style

- Static HTML: match existing class names in `assets/css/site.css`
- Python snippets: type hints optional; include env-var configuration
- Commit messages: imperative mood, explain *why*

## Questions

Open a [GitHub issue](https://github.com/multilogin-labs/multilogin-labs.github.io/issues) with the `question` label.
