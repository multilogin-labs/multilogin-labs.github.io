# multilogin-labs datasets

Machine-readable artifacts referenced by [benchmark reports](https://multilogin-labs.github.io/guides/benchmark-reports/) and lab tools.

| File | Description |
|------|-------------|
| [benchmark-2026-04.json](./benchmark-2026-04.json) | April 2026 summary bands and drift patterns (methodology v1.2) |
| [benchmark-matrix-2026-04.json](./benchmark-matrix-2026-04.json) | 22-platform scored matrix with blockers |
| [benchmark-matrix-2026-05.json](./benchmark-matrix-2026-05.json) | May 2026 preview matrix |
| [benchmark-2026-05.json](./benchmark-2026-05.json) | May 2026 summary (preview) |
| [index.json](./index.json) | Dataset discovery manifest for tools/API |
| [fingerprint-checklist-v1.json](./fingerprint-checklist-v1.json) | Weighted checklist schema for readiness scoring |

Schemas: [`schemas/benchmark-v1.schema.json`](./schemas/benchmark-v1.schema.json) · [`schemas/checklist-v1.schema.json`](./schemas/checklist-v1.schema.json)

## Usage

```bash
curl -sL https://multilogin-labs.github.io/data/benchmark-2026-04.json | jq .
```

## Changelog

- **2026-05-24** — May summary preview + manifest update.
- **2026-05-22** — Initial published datasets for GitHub repo + Pages dual use.
