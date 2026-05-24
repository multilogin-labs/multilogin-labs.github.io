# Antidetect Operations Catalog

> Curated index of **original** lab resources—benchmarks, tools, playbooks, and datasets.  
> Live site: **https://multilogin-labs.github.io/** · Repo: **https://github.com/multilogin-labs/multilogin-labs.github.io**

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-live-2a9d8f?style=flat-square)](https://multilogin-labs.github.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue?style=flat-square)](./LICENSE)
[![Datasets](https://img.shields.io/badge/datasets-JSON-orange?style=flat-square)](./data/)
[![Methodology](https://img.shields.io/badge/methodology-v1.2-lightgrey?style=flat-square)](https://multilogin-labs.github.io/guides/evaluation-methodology/)

---

## Why this catalog exists

Most antidetect content online is **coupon spam** or **doc mirrors**. multilogin-labs is structured as an **evidence-first lab**: reproducible methodology, downloadable data, and client-side tools you can fork.

---

## Interactive tools (free, no signup)

| Tool | Purpose |
|------|---------|
| [Benchmark Explorer](https://multilogin-labs.github.io/tools/benchmark-explorer/) | Live JSON matrix, filters, CSV export |
| [Fingerprint Readiness Score](https://multilogin-labs.github.io/tools/fingerprint-readiness-score/) | Pre-procurement risk band before annual contracts |
| [Evidence Pack Builder](https://multilogin-labs.github.io/tools/evidence-pack-builder/) | Exportable approval trail for procurement |
| [Benchmark Release Checker](https://multilogin-labs.github.io/tools/benchmark-release-checker/) | Validate report version vs methodology |
| [Antidetect Browser Rankings](https://multilogin-labs.github.io/tools/antidetect-browsers/) | 2026 weighted index overview |
| [Multilogin Discount Verifier](https://multilogin-labs.github.io/tools/multilogin-discount/) | SAAS50 / MIN50 proof workflow |

---

## Datasets (machine-readable)

| File | Schema | Description |
|------|--------|-------------|
| [benchmark-2026-04.json](./data/benchmark-2026-04.json) | [benchmark-v1](./data/schemas/benchmark-v1.schema.json) | April summary bands + drift patterns |
| [benchmark-matrix-2026-04.json](./data/benchmark-matrix-2026-04.json) | benchmark-v1 | Per-platform scores (22 platforms) |
| [benchmark-matrix-2026-05.json](./data/benchmark-matrix-2026-05.json) | benchmark-v1 | May preview matrix |
| [index.json](./data/index.json) | — | Dataset discovery manifest |
| [fingerprint-checklist-v1.json](./data/fingerprint-checklist-v1.json) | [checklist-v1](./data/schemas/checklist-v1.schema.json) | Weighted readiness checklist |

```bash
# One-liners
curl -sL https://multilogin-labs.github.io/data/benchmark-matrix-2026-04.json | jq '.platforms[:3]'
```

---

## Core playbooks

| Guide | Audience |
|-------|----------|
| [Antidetection Ops SOP](https://multilogin-labs.github.io/guides/antidetection-ops-sop/) | Team leads defining go/no-go gates |
| [Evaluation Methodology](https://multilogin-labs.github.io/guides/evaluation-methodology/) | Scoring, blockers, evidence levels |
| [Detection Tests](https://multilogin-labs.github.io/guides/detection-tests/) | Pre-scale signal validation |
| [Connection Leak Tests](https://multilogin-labs.github.io/guides/connection-leak-tests/) | Proxy rotation leak checks |
| [MLX API Integration Map](https://multilogin-labs.github.io/guides/mlx-api-integration-map/) | Rollout order (not vendor doc clone) |
| [OpenMultilogin Risk Guide](https://multilogin-labs.github.io/guides/openmultilogin-risk-and-migration-guide/) | Fork risk and migration |
| [Benchmark Reports](https://multilogin-labs.github.io/guides/benchmark-reports/) | Monthly reliability previews |

---

## Compare (tier-1 only)

| Page | Focus |
|------|-------|
| [Alternatives matrix](https://multilogin-labs.github.io/compare/multilogin-alternatives/) | Shortlist by cost + risk |
| [vs GoLogin](https://multilogin-labs.github.io/compare/multilogin-vs-gologin/) | Engine cadence |
| [vs AdsPower](https://multilogin-labs.github.io/compare/multilogin-vs-adspower/) | Workspace governance |
| [vs Dolphin Anty](https://multilogin-labs.github.io/compare/multilogin-vs-dolphin-anty/) | Team policy |
| [vs Incogniton](https://multilogin-labs.github.io/compare/multilogin-vs-incogniton/) | API limits |
| [vs Kameleo](https://multilogin-labs.github.io/compare/multilogin-vs-kameleo/) | Automation bridges |
| [vs Octo Browser](https://multilogin-labs.github.io/compare/multilogin-vs-octo-browser/) | Token lifecycle |
| [vs Undetectable](https://multilogin-labs.github.io/compare/multilogin-vs-undetectable/) | Local footprint |

---

## Snippets

| File | Stack |
|------|-------|
| [profile-start-template.py](./snippets/profile-start-template.py) | Python + MLX API (env config) |

---

## Trust & governance

- [Editorial policy](https://multilogin-labs.github.io/editorial-policy/)
- [Methodology changelog](https://multilogin-labs.github.io/guides/methodology-changelog/)
- [RSS lab updates](https://multilogin-labs.github.io/feeds/lab-updates.xml)

---

## Star this repo if you use it

GitHub stars help other operators discover **evidence-based** resources instead of duplicate coupon farms.  
**https://github.com/multilogin-labs/multilogin-labs.github.io**

---

## Suggested GitHub topics

`antidetect-browser` `browser-automation` `fingerprinting` `playwright` `multilogin` `benchmark` `github-pages` `open-data` `web-scraping-ops` `devtools`
