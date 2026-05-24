#!/usr/bin/env python3
"""One-shot site migration: branding, redirects, sitemap."""
from __future__ import annotations

import os
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://multilogin-labs.github.io"
TODAY = date.today().isoformat()

COMPARE_KEEP = {
    "multilogin-alternatives",
    "multilogin-vs-gologin",
    "multilogin-vs-adspower",
    "multilogin-vs-dolphin-anty",
    "multilogin-vs-incogniton",
    "multilogin-vs-kameleo",
    "multilogin-vs-octo-browser",
    "multilogin-vs-undetectable",
}

PROMO_VENDORS = [
    ("adblogin", "ADBLogin", "entitlement drift as workflows mature", "free-tier entitlement boundaries"),
    ("adspower", "AdsPower", "governance drift across shared workspaces", "workspace roles and policy controls"),
    ("bitbrowser", "BitBrowser", "profile sync lag under bulk operations", "sync latency under 50+ profile loads"),
    ("dashnull", "DashNull", "opaque pricing tiers at scale", "per-seat math at your target volume"),
    ("discloak", "DisCloak", "limited enterprise audit trails", "exportable session logs for compliance"),
    ("dolphin-anty", "Dolphin Anty", "team policy gaps at scale", "role-based access and audit exports"),
    ("ghost-browser", "Ghost Browser", "session isolation under parallel tabs", "cookie isolation across 10 parallel sessions"),
    ("gologin", "GoLogin", "engine cadence vs fingerprint drift", "fingerprint consistency after browser updates"),
    ("hidemyacc", "HideMyAcc", "proxy binding errors at scale", "proxy-profile 1:1 binding under load"),
    ("incogniton", "Incogniton", "starter-tier API limits", "API rate limits for your automation volume"),
    ("indigo-browser", "Indigo Browser", "regional latency spikes", "p95 latency from your primary geo"),
    ("kameleo", "Kameleo", "automation bridge stability", "Playwright/Selenium bridge uptime"),
    ("linkensphere", "LinkenSphere", "steep learning curve for teams", "onboarding time for 3 operators"),
    ("morelogin", "MoreLogin", "cloud phone add-on billing clarity", "cloud phone line items in invoice"),
    ("nstbrowser", "NSTBrowser", "headless detection on target sites", "detection rate on your top 5 domains"),
    ("octo-browser", "Octo Browser", "API token rotation friction", "token refresh without profile downtime"),
    ("roxybrowser", "RoxyBrowser", "RPA workflow brittleness", "RPA recovery after navigation failures"),
    ("undetectable", "Undetectable.io", "local storage footprint at scale", "disk usage per 100 profiles"),
    ("vektort13", "VektorT13", "niche stack compatibility", "compatibility with your proxy provider"),
    ("vmlogin", "VMLogin", "legacy UI operational drag", "task time for daily profile launch"),
    ("wade-browser", "Wade Browser", "vendor lock-in on profiles", "profile export format portability"),
    ("whologin", "WhoLogin", "support response under incidents", "SLA for ticket response in trial"),
]

REDIRECT_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta http-equiv="refresh" content="0;url={url}"/>
<link rel="canonical" href="{canonical}"/>
<title>Redirecting… | multilogin-labs</title>
</head>
<body>
<p>Page moved. <a href="{url}">Continue to {label}</a>.</p>
</body>
</html>
"""


def text_replacements(content: str) -> str:
    content = content.replace("SaaS<span>Verdict</span>", "multi<span>login-labs</span>")
    content = content.replace("SaaS<span>></span>", "multi<span>login-labs</span>")
    content = content.replace("SaaS Verdict", "multilogin-labs")
    content = content.replace("/guides/mlx-api-hub/", "/guides/mlx-api-integration-map/")
    content = content.replace("/guides/mlx-api-hub", "/guides/mlx-api-integration-map")
    return content


def patch_files():
    exts = {".html", ".xml", ".md", ".css", ".js", ".json"}
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.suffix.lower() not in exts:
            continue
        if path.parts[0] == "scripts" and path.name == "migrate_site.py":
            continue
        raw = path.read_text(encoding="utf-8", errors="replace")
        new = text_replacements(raw)
        if new != raw:
            path.write_text(new, encoding="utf-8")


def write_redirect(dir_path: Path, target: str, canonical: str, label: str):
    dir_path.mkdir(parents=True, exist_ok=True)
    html = REDIRECT_HTML.format(url=target, canonical=canonical, label=label)
    (dir_path / "index.html").write_text(html, encoding="utf-8")


def consolidate_compare():
    compare_dir = ROOT / "compare"
    for child in compare_dir.iterdir():
        if not child.is_dir():
            continue
        slug = child.name
        if slug in COMPARE_KEEP:
            continue
        write_redirect(
            child,
            "/compare/",
            f"{BASE}/compare/",
            "compare hub",
        )


def consolidate_promo():
    promo_dir = ROOT / "promo"
    for child in promo_dir.iterdir():
        if not child.is_dir():
            continue
        slug = child.name
        anchor = f"#vendor-{slug}"
        write_redirect(
            child,
            f"/promo/{anchor}",
            f"{BASE}/promo/",
            "promo hub",
        )


def collect_indexable_urls() -> list[tuple[str, str, str]]:
    """Return (loc, lastmod, priority) sorted by priority desc."""
    urls: list[tuple[str, str, str]] = []

    def add(path: str, priority: str, lastmod: str = TODAY):
        loc = BASE + path if path.startswith("/") else f"{BASE}/{path}"
        urls.append((loc, lastmod, priority))

    add("/", "1.00")
    for section, pri in [
        ("tools", "0.93"),
        ("compare", "0.92"),
        ("guides", "0.91"),
        ("promo", "0.88"),
        ("about", "0.55"),
        ("contact", "0.50"),
        ("editorial-policy", "0.52"),
    ]:
        p = ROOT / section / "index.html"
        if p.exists():
            add(f"/{section}/", pri)

    for tool in [
        "multilogin-discount",
        "fingerprint-readiness-score",
        "evidence-pack-builder",
        "benchmark-release-checker",
        "benchmark-explorer",
        "antidetect-browsers",
    ]:
        if (ROOT / "tools" / tool / "index.html").exists():
            add(f"/tools/{tool}/", "0.87")

    if (ROOT / "snippets" / "index.html").exists():
        add("/snippets/", "0.55")
    if (ROOT / "catalog" / "index.html").exists():
        add("/catalog/", "0.54")
    if (ROOT / "site-map" / "index.html").exists():
        add("/site-map/", "0.53")

    for slug in sorted(COMPARE_KEEP):
        if (ROOT / "compare" / slug / "index.html").exists():
            add(f"/compare/{slug}/", "0.86")

    guide_dirs = sorted(
        p.parent.relative_to(ROOT).as_posix()
        for p in ROOT.glob("guides/**/index.html")
        if p.parent.name != "guides"
    )
    for g in guide_dirs:
        add(f"/{g}/", "0.84")

    add("/feeds/lab-updates.xml", "0.40")
    add("/llms.txt", "0.38")
    add("/humans.txt", "0.30")
    for data_file in (
        "index.json",
        "benchmark-2026-04.json",
        "benchmark-matrix-2026-04.json",
        "benchmark-matrix-2026-05.json",
        "benchmark-2026-05.json",
        "fingerprint-checklist-v1.json",
    ):
        if (ROOT / "data" / data_file).exists():
            add(f"/data/{data_file}", "0.36")
    add("/privacy-policy/", "0.35")
    add("/terms/", "0.35")
    urls.sort(key=lambda x: (-float(x[2]), x[0]))
    return urls


def write_sitemap():
    urls = collect_indexable_urls()
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for loc, lastmod, priority in urls:
        lines.extend(
            [
                "  <url>",
                f"    <loc>{loc}</loc>",
                f"    <lastmod>{lastmod}</lastmod>",
                f"    <priority>{priority}</priority>",
                "  </url>",
            ]
        )
    lines.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    os.chdir(ROOT)
    consolidate_compare()
    consolidate_promo()
    patch_files()
    write_sitemap()
    print("Migration complete.")
    print(f"Sitemap URLs: {len(collect_indexable_urls())}")


if __name__ == "__main__":
    main()
