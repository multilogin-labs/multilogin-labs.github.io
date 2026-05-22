# multilogin-labs datasets

Machine-readable artifacts referenced by [benchmark reports](https://multilogin-labs.github.io/guides/benchmark-reports/) and lab tools.

| File | Description |
|------|-------------|
| [benchmark-2026-04.json](./benchmark-2026-04.json) | April 2026 summary bands and drift patterns (methodology v1.2) |
| [fingerprint-checklist-v1.json](./fingerprint-checklist-v1.json) | Weighted checklist schema for readiness scoring |

## Usage

```bash
curl -sL https://multilogin-labs.github.io/data/benchmark-2026-04.json | jq .
```

## Changelog

- **2026-05-22** — Initial published datasets for GitHub repo + Pages dual use.
