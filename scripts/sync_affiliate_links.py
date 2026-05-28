#!/usr/bin/env python3
"""Sync Multilogin checkout URL sitewide from data/affiliate.json (skips homepage index.html)."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "data" / "affiliate.json"
HOMEPAGE = ROOT / "index.html"
GO_PAGE = ROOT / "go" / "multilogin" / "index.html"

OLD_REFRESH = re.compile(
    r'content="0;url=https://multilogin\.com/[^"]*"',
    re.I,
)
HREF_GO = re.compile(r'href="/go/multilogin/?"', re.I)
SPEC_GO = re.compile(
    r'"href_matches":"/go/multilogin\*"',
    re.I,
)


def load_checkout() -> tuple[str, str]:
    data = json.loads(CONFIG.read_text(encoding="utf-8"))
    raw = data["multilogin_checkout"].strip()
    html = raw.replace("&", "&amp;")
    return raw, html


def should_skip(path: Path, text: str) -> bool:
    if path.resolve() in (HOMEPAGE.resolve(), GO_PAGE.resolve()):
        return True
    return 'http-equiv="refresh"' in text.lower()


def write_go_page(raw_url: str, html_url: str) -> None:
    GO_PAGE.parent.mkdir(parents=True, exist_ok=True)
    GO_PAGE.write_text(
        f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta http-equiv="refresh" content="0;url={html_url}"/>
<link rel="canonical" href="https://multilogin-labs.github.io/go/multilogin/"/>
<title>Redirect to Multilogin pricing | multilogin-labs</title>
<meta name="robots" content="noindex,nofollow"/>
<script>location.replace({json.dumps(raw_url)});</script>
</head>
<body>
<p>Redirecting to <a href="{html_url}" rel="sponsored noopener noreferrer">Multilogin pricing</a>. Apply SAAS50 or MIN50 at checkout and confirm the discount line.</p>
<noscript><meta http-equiv="refresh" content="0;url={html_url}"/></noscript>
</body>
</html>
""",
        encoding="utf-8",
    )


def patch_html(text: str, raw_url: str, html_url: str) -> str:
    new = HREF_GO.sub(f'href="{html_url}"', text)
    new = new.replace(
        "https://multilogin-labs.github.io/go/multilogin/",
        raw_url,
    )
    new = SPEC_GO.sub('"href_matches":"*multilogin.com/pricing*"', new)
    return new


def patch_file(path: Path, raw_url: str, html_url: str) -> bool:
    raw = path.read_text(encoding="utf-8")
    if should_skip(path, raw):
        return False
    new = patch_html(raw, raw_url, html_url)
    if new != raw:
        path.write_text(new, encoding="utf-8")
        return True
    return False


def main() -> None:
    if not CONFIG.exists():
        raise SystemExit(f"Missing {CONFIG}")
    raw_url, html_url = load_checkout()
    write_go_page(raw_url, html_url)
    n = 0
    for html in sorted(ROOT.rglob("*.html")):
        if ".git" in html.parts:
            continue
        if patch_file(html, raw_url, html_url):
            n += 1
    print(f"Affiliate sync: go/multilogin rewritten; {n} HTML files updated (homepage skipped)")


if __name__ == "__main__":
    main()
