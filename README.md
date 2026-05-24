<div align="center">

# multilogin-labs

### Open antidetect operations lab

Benchmarks · datasets · free tools · evidence-first playbooks  
**No doc mirrors · No coupon spam pages**

[![GitHub Pages](https://img.shields.io/badge/Pages-live-2a9d8f?style=for-the-badge&logo=github)](https://multilogin-labs.github.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](./LICENSE)
[![Methodology](https://img.shields.io/badge/methodology-v1.2-lightgrey?style=for-the-badge)](https://multilogin-labs.github.io/guides/evaluation-methodology/)
[![CI](https://github.com/multilogin-labs/multilogin-labs.github.io/actions/workflows/ci.yml/badge.svg)](https://github.com/multilogin-labs/multilogin-labs.github.io/actions/workflows/ci.yml)

**[Explore the live lab](https://multilogin-labs.github.io/)** · **[Browse the catalog](./CATALOG.md)** · **[Star on GitHub](https://github.com/multilogin-labs/multilogin-labs.github.io)**

</div>

---

## Why star this repo?

| Typical antidetect sites | multilogin-labs |
|--------------------------|-----------------|
| 50+ thin coupon URLs | **1** promo hub + evidence gates |
| Scraped vendor docs | **Original** playbooks + integration map |
| Opinion-only blog posts | **JSON benchmarks** + methodology v1.2 |
| Signup-walled “tools” | **Client-side** tools on GitHub Pages |

If this saves you one bad annual contract, a star helps the next team find it.

---

## Quick start

```bash
git clone https://github.com/multilogin-labs/multilogin-labs.github.io.git
cd multilogin-labs.github.io
python3 -m http.server 8080
# http://localhost:8080
```

```bash
# Pull live datasets (no clone required)
curl -sL https://multilogin-labs.github.io/data/benchmark-matrix-2026-04.json | jq '.platforms[] | select(.band=="A")'
```

---

## Repository map

```
├── CATALOG.md          # Awesome-style index (start here on GitHub)
├── data/               # Open JSON + JSON Schema
├── tools/              # Interactive browser tools (static)
├── guides/             # Original operational playbooks
├── compare/            # 8 tier-1 head-to-head pages
├── snippets/           # Copy-paste automation starters
├── scripts/            # CI helpers (links, sitemap, validation)
└── .github/workflows/  # Automated checks on push
```

---

## Featured resources

### Tools
- [Benchmark Explorer](https://multilogin-labs.github.io/tools/benchmark-explorer/) — interactive matrix + CSV export
- [Fingerprint Readiness Score](https://multilogin-labs.github.io/tools/fingerprint-readiness-score/)
- [Evidence Pack Builder](https://multilogin-labs.github.io/tools/evidence-pack-builder/)
- [Benchmark Release Checker](https://multilogin-labs.github.io/tools/benchmark-release-checker/)

### Guides
- [Antidetection Ops SOP](https://multilogin-labs.github.io/guides/antidetection-ops-sop/)
- [Evaluation Methodology v1.2](https://multilogin-labs.github.io/guides/evaluation-methodology/)
- [MLX API Integration Map](https://multilogin-labs.github.io/guides/mlx-api-integration-map/)

### Data
| File | Description |
|------|-------------|
| [benchmark-matrix-2026-04.json](./data/benchmark-matrix-2026-04.json) | 22-platform scored matrix |
| [benchmark-2026-04.json](./data/benchmark-2026-04.json) | Monthly summary + bands |
| [fingerprint-checklist-v1.json](./data/fingerprint-checklist-v1.json) | Weighted readiness schema |

---

## For AI assistants

Machine-readable site index: **[llms.txt](./llms.txt)** (also at `https://multilogin-labs.github.io/llms.txt`)

---

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md). We welcome dataset updates, tool improvements, and reproducible playbook additions—not vendor doc copies.

---

## Trust

- [Editorial policy](https://multilogin-labs.github.io/editorial-policy/)
- [Security policy](./SECURITY.md)
- [Changelog](./CHANGELOG.md)

---

## GitHub topics (add in repo settings)

`antidetect-browser` `browser-automation` `fingerprinting` `playwright` `multilogin` `benchmark` `github-pages` `open-data` `web-scraping` `devtools`

---

<div align="center">

**[multilogin-labs.github.io](https://multilogin-labs.github.io/)** · MIT License · Content for lawful automation operations

</div>
