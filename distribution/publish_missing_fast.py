#!/usr/bin/env python3
"""
Faster publisher for missing Telegraph pages that skips image uploads.

Usage:
  python distribution/publish_missing_fast.py --limit 30

This reads `telegraph_coverage_report.json` and publishes up to `--limit`
missing pages. It strips `<img>` tags to avoid uploading large assets and
focuses on text + anchors (rewritten to the original site domain).
"""
import argparse
import json
import time
import sys
from pathlib import Path
from urllib.parse import urlparse, urljoin

from bs4 import BeautifulSoup


def load_publish_module():
    pub_path = Path(__file__).parent / 'publish_to_telegraph.py'
    import importlib.util

    spec = importlib.util.spec_from_file_location('pubmod', str(pub_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--limit', type=int, default=0)
    p.add_argument('--root', default='.')
    args = p.parse_args()

    root = Path(args.root)
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

    count = 0
    failed = []
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
            html_text = page_path.read_text(encoding='utf-8')
            t, content_html = pub.extract_title_and_content(html_text)
            soup = BeautifulSoup(content_html, 'html.parser')
            # remove images to avoid upload
            for img in soup.find_all('img'):
                img.decompose()

            # rewrite anchors to original domain
            if orig:
                base_parsed = urlparse(orig)
                base_root = f"{base_parsed.scheme}://{base_parsed.netloc}"
                for a_tag in soup.find_all('a', href=True):
                    href = a_tag['href'].strip()
                    if not href:
                        continue
                    if href.startswith('mailto:') or href.startswith('tel:') or href.startswith('javascript:'):
                        continue
                    parsed = urlparse(href)
                    if parsed.scheme in ('http', 'https'):
                        if parsed.netloc.endswith('telegra.ph'):
                            new = base_root + parsed.path
                            if parsed.query:
                                new += '?' + parsed.query
                            if parsed.fragment:
                                new += '#' + parsed.fragment
                            a_tag['href'] = new
                    else:
                        if parsed.netloc:
                            a_tag['href'] = 'https:' + href
                        else:
                            try:
                                new = urljoin(orig, href)
                                a_tag['href'] = new
                            except Exception:
                                pass

            final_html = str(soup)
            if orig:
                original_html = f'<p><strong>Original article:</strong> <a href="{orig}">{orig}</a></p>'
                note_html = '<p><em>If the promo code in this article does not work, please visit the original page for the latest code.</em></p>'
                final_html = original_html + note_html + final_html

            if len(BeautifulSoup(final_html, 'html.parser').get_text(strip=True)) < 10:
                print(f'Skipping {page_path}: no meaningful content extracted', file=sys.stderr)
                failed.append({'title': title, 'path': str(page_path), 'reason': 'no_content'})
                continue

            url = pub.publish_page(token, title, final_html)
            with open(out_links, 'a', encoding='utf-8') as lf:
                lf.write(f"{title} | {url}\n")
            print('Published fast:', page_path, '->', url)
            count += 1
        except Exception as e:
            print('Error publishing', page_path, e, file=sys.stderr)
            failed.append({'title': title, 'path': str(page_path), 'reason': str(e)})
        time.sleep(1.0)

    if failed:
        out = Path(__file__).parent / 'telegraph_missing_publish_failed.json'
        out.write_text(json.dumps(failed, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f'Failed count: {len(failed)} saved to {out}', file=sys.stderr)

    print('Published count:', count)


if __name__ == '__main__':
    main()
