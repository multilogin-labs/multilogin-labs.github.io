#!/usr/bin/env python3
"""Single entry point for all site maintenance (run before commit)."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

STEPS: list[tuple[str, list[str]]] = [
    ("Homepage perf guardrails", ["python3", "scripts/optimize_home.py"]),
    ("Affiliate URL sync (data/affiliate.json)", ["python3", "scripts/sync_affiliate_links.py"]),
    ("Inner site upgrade (rel, catalog, ai.txt)", ["python3", "scripts/upgrade_inner_site.py"]),
    ("Sitewide UX (announcement, CTA, prefetch)", ["python3", "scripts/upgrade_sitewide.py"]),
    ("Polish (footers, compare OG, meta)", ["python3", "scripts/upgrade_polish.py"]),
    ("Verify affiliate hop + homepage", ["python3", "scripts/verify_affiliate.py"]),
    ("Regenerate llms.txt", ["python3", "scripts/generate_llms_txt.py"]),
    ("Performance (remove blocking fonts)", ["python3", "scripts/optimize_perf.py"]),
    ("Inner pages perf (CLS, prefetch; skip homepage)", ["python3", "scripts/optimize_inner_pages.py"]),
    ("Upgrade promo detail pages (indexable)", ["python3", "scripts/upgrade_promo_pages.py"]),
    ("Affiliate funnel pages", ["python3", "scripts/aff_funnel.py"]),
    ("Enhance pages (OG, breadcrumbs, dates)", ["python3", "scripts/enhance_pages.py"]),
    ("SEO optimize (redirects, sitemap, links)", ["python3", "scripts/seo_optimize.py"]),
    ("Normalize + validate JSON-LD (skip homepage)", ["python3", "scripts/normalize_jsonld.py"]),
    ("Schema coverage report", ["python3", "scripts/schema_coverage.py"]),
    ("Sitewide a11y guard", ["python3", "scripts/a11y_check.py"]),
    ("Indexability audit (robots, canonical, sitemap)", ["python3", "scripts/indexability_audit.py"]),
    ("Index health report", ["python3", "scripts/index_health.py"]),
    ("Internal link audit", ["python3", "scripts/internal_link_audit.py"]),
    ("Content freshness report", ["python3", "scripts/content_freshness.py"]),
    ("Validate datasets", ["python3", "scripts/validate_data.py"]),
    ("Check internal links", ["python3", "scripts/check_links.py"]),
    ("IndexNow key file", ["python3", "scripts/indexnow.py", "--ensure-key"]),
]


def main() -> int:
    import os

    os.chdir(ROOT)
    failed = False
    for label, cmd in STEPS:
        print(f"\n==> {label}")
        result = subprocess.run(cmd, cwd=ROOT)
        if result.returncode != 0:
            print(f"FAILED: {' '.join(cmd)}", file=sys.stderr)
            failed = True
    if failed:
        return 1
    print("\nAll maintenance steps OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
