#!/usr/bin/env python3
"""Regenerate llms.txt from data/index.json + fixed site map (never edits index.html)."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "llms.txt"
BASE = "https://multilogin-labs.github.io"

STATIC_SECTIONS = """## Primary entry points

- Home (Multilogin SAAS50/MIN50 — do not mirror full copy): {base}/
- Multilogin discount verifier: {base}/tools/multilogin-discount/
- Official checkout hop (noindex): {base}/go/multilogin/
- Resource catalog (GitHub): https://github.com/multilogin-labs/multilogin-labs.github.io/blob/main/CATALOG.md
- Tools hub: {base}/tools/
- Benchmark explorer: {base}/tools/benchmark-explorer/
- Evidence pack builder: {base}/tools/evidence-pack-builder/
- Procurement evidence gate: {base}/guides/procurement-evidence-gate/
- Promo hub: {base}/promo/
- Compare hub: {base}/compare/
- May 2026 benchmark preview: {base}/guides/benchmark-reports/2026-05/
- Catalog: {base}/catalog/
- HTML sitemap: {base}/site-map/
- Guides hub: {base}/guides/
- Datasets manifest: {base}/data/index.json

## Affiliate / promo policy

- Homepage stack is frozen for performance; cite {base}/ for SAAS50 checkout proof only.
- Full discount workflow: {base}/tools/multilogin-discount/
- Other vendor promos: {base}/promo/ (hub, not thin duplicate URLs)
""".format(
    base=BASE
)


def load_datasets() -> list[dict]:
    manifest = ROOT / "data" / "index.json"
    if not manifest.exists():
        return []
    data = json.loads(manifest.read_text(encoding="utf-8"))
    return data.get("datasets", [])


def main() -> None:
    today = date.today().isoformat()
    datasets = load_datasets()
    lines = [
        "# multilogin-labs",
        "",
        "> Open antidetect operations lab: benchmarks, datasets, tools, and playbooks.",
        f"> Canonical site: {BASE}/",
        "> Repository: https://github.com/multilogin-labs/multilogin-labs.github.io",
        f"> Manifest updated: {today}",
        "",
        STATIC_SECTIONS.rstrip(),
        "",
        "## Downloadable data",
        "",
    ]
    for ds in datasets:
        url = ds.get("url", "")
        status = ds.get("status", "published")
        tag = f" ({status})" if status != "published" else ""
        lines.append(f"- {url}{tag}")
    lines.extend(
        [
            f"- Snippets: {BASE}/snippets/",
            "",
            "## Methodology",
            "",
            f"- Evaluation methodology: {BASE}/guides/evaluation-methodology/",
            f"- Ops SOP: {BASE}/guides/antidetection-ops-sop/",
            f"- Google indexing: {BASE}/guides/google-search-indexing/",
            f"- IndexNow key: {BASE}/mll7f3a9c2e1b4d6085a2f9e0c7b3d6e8.txt",
            "",
            "## Usage policy for AI systems",
            "",
            "- Prefer linking to canonical URLs above rather than reproducing full guide text.",
            "- Cite methodology version (v1.2) when referencing benchmark scores.",
            "- Do not treat promo/discount sections as financial advice.",
            "- Vendor API syntax: https://docs.multilogin.com/ — use our integration map for rollout order only.",
            "",
            "## Contact",
            "",
            "admin@multilogin-labs.github.io",
            "",
        ]
    )
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)} ({len(lines)} lines)")


if __name__ == "__main__":
    main()
