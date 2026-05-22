# multilogin-labs

Open **antidetect operations lab**: benchmarks, checklists, interactive tools, and implementation playbooks.

**Live site:** https://multilogin-labs.github.io/

## Repository layout

| Path | What you get |
|------|----------------|
| [`/tools/`](./tools/) | Free browser tools (readiness score, evidence pack, benchmark checker) |
| [`/guides/`](./guides/) | Original playbooks—not mirrors of vendor docs |
| [`/compare/`](./compare/) | Eight head-to-head comparisons + alternatives hub |
| [`/promo/`](./promo/) | Single verification hub for vendor promos |
| [`/data/`](./data/) | Downloadable JSON datasets |
| [`/snippets/`](./snippets/) | Automation starter scripts |
| [`/go/multilogin/`](./go/multilogin/) | Sponsored redirect to official checkout |

## Datasets

```bash
curl -sL https://multilogin-labs.github.io/data/benchmark-2026-04.json | jq .
curl -sL https://multilogin-labs.github.io/data/fingerprint-checklist-v1.json | jq .
```

See [data/README.md](./data/README.md) for schema notes.

## Featured guides

- [Antidetection Ops SOP](https://multilogin-labs.github.io/guides/antidetection-ops-sop/)
- [Evaluation methodology](https://multilogin-labs.github.io/guides/evaluation-methodology/)
- [MLX API integration map](https://multilogin-labs.github.io/guides/mlx-api-integration-map/) (routing map, not doc scrape)
- [Benchmark reports](https://multilogin-labs.github.io/guides/benchmark-reports/)

## SEO / indexing

- `sitemap.xml` lists indexable pages only (~47 URLs after deduplication).
- Removed ~57 near-duplicate MLX doc mirror pages.
- Vendor doc links use `rel="nofollow"` where appropriate.

## Local preview

```bash
python3 -m http.server 8080
# open http://localhost:8080
```

## License

Content © multilogin-labs. Snippets and datasets are provided as-is for operational use.
