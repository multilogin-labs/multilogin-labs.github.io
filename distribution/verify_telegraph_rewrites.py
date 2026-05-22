#!/usr/bin/env python3
"""
Verify Telegraph posts contain the excerpt marker added by edits.

Writes `distribution/telegraph_verify_report.json` with summary and samples.
"""
import argparse
import json
import time
from pathlib import Path

import requests


def parse_links(path: Path):
    items = []
    if not path.exists():
        return items
    for ln in path.read_text(encoding='utf-8').splitlines():
        ln = ln.strip()
        if not ln:
            continue
        if '|' in ln:
            title, url = ln.rsplit('|', 1)
            items.append((title.strip(), url.strip()))
        else:
            items.append((ln, ''))
    return items


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--links', default='distribution/telegraph_links.txt')
    p.add_argument('--limit', type=int, default=0)
    p.add_argument('--timeout', type=int, default=15)
    p.add_argument('--wait', type=float, default=0.5)
    args = p.parse_args()

    links = parse_links(Path(args.links))
    if args.limit:
        links = links[: args.limit]

    rewritten = []
    not_rewritten = []

    for title, url in links:
        if not url:
            not_rewritten.append({'title': title, 'url': url, 'reason': 'no_url'})
            continue
        try:
            r = requests.get(url, timeout=args.timeout, headers={'User-Agent': 'Mozilla/5.0'})
            if r.status_code != 200:
                not_rewritten.append({'title': title, 'url': url, 'reason': f'status_{r.status_code}'})
            else:
                txt = r.text
                if 'Original article:' in txt or 'If the promo code in this article does not work' in txt:
                    rewritten.append({'title': title, 'url': url})
                else:
                    not_rewritten.append({'title': title, 'url': url, 'reason': 'marker_missing', 'len': len(txt)})
        except Exception as e:
            not_rewritten.append({'title': title, 'url': url, 'reason': f'error:{e}'})
        time.sleep(args.wait)

    out = Path('distribution/telegraph_verify_report.json')
    report = {
        'checked': len(links),
        'rewritten': len(rewritten),
        'not_rewritten': len(not_rewritten),
        'not_samples': not_rewritten[:50],
    }
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Checked {report['checked']}: rewritten={report['rewritten']} not_rewritten={report['not_rewritten']}. Report: {out}")


if __name__ == '__main__':
    main()
