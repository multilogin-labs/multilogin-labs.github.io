#!/usr/bin/env python3
"""
Publish missing pages listed in `telegraph_coverage_report.json`.
This script reads the coverage report, finds `missing_samples` with local paths,
and publishes each using the existing `process_file` (with force_publish=True).
"""
import json
import time
import sys
from pathlib import Path
import importlib.util
import argparse


def load_publish_module():
    pub_path = Path(__file__).parent / 'publish_to_telegraph.py'
    spec = importlib.util.spec_from_file_location('pubmod', str(pub_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--limit', type=int, default=0, help='limit number of missing pages to publish (0=all)')
    args = p.parse_args()

    root = Path('.')
    report_path = Path(__file__).parent / 'telegraph_coverage_report.json'
    if not report_path.exists():
        print('Coverage report not found:', report_path, file=sys.stderr)
        sys.exit(1)
    report = json.loads(report_path.read_text(encoding='utf-8'))
    missing = report.get('missing_samples', [])
    if args.limit:
        missing = missing[: args.limit]
    if not missing:
        print('No missing samples to publish.')
        return

    pub = load_publish_module()
    token = pub.create_account_if_needed('saasverdict')
    out_links = Path(__file__).parent / 'telegraph_links.txt'
    failed = []
    count = 0

    for item in missing:
        rel = item.get('path')
        orig = item.get('orig_url')
        title = item.get('title')
        page_path = root / rel
        if not page_path.exists():
            print('Missing local file, skipping:', page_path, file=sys.stderr)
            failed.append({'title': title, 'path': str(page_path), 'reason': 'local_missing'})
            continue
        try:
            res = pub.process_file(page_path, token, root, dry_run=False, original_url=orig, force_publish=True)
            if res:
                t,u = res
                with open(out_links, 'a', encoding='utf-8') as lf:
                    lf.write(f"{t} | {u}\n")
                print('Published missing:', page_path, '->', u)
                count += 1
            else:
                print('Publish returned no result for', page_path, file=sys.stderr)
                failed.append({'title': title, 'path': str(page_path), 'reason': 'no_result'})
        except Exception as e:
            print('Error publishing', page_path, e, file=sys.stderr)
            failed.append({'title': title, 'path': str(page_path), 'reason': str(e)})
        time.sleep(1.2)

    if failed:
        out = Path(__file__).parent / 'telegraph_missing_publish_failed.json'
        out.write_text(json.dumps(failed, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f'Failed count: {len(failed)} saved to {out}', file=sys.stderr)

    print('Published count:', count)

if __name__ == '__main__':
    main()
