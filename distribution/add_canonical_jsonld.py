#!/usr/bin/env python3
"""
Inject canonical link and Article JSON-LD into site HTML files referenced by sitemap.xml

Usage:
  python distribution/add_canonical_jsonld.py --root .

This will walk sitemap entries from `publish_to_telegraph.get_files_from_sitemap`,
skip non-HTML files, and insert a `<link rel="canonical">` and a minimal
`<script type="application/ld+json">` Article block if not already present.
"""
import argparse
import json
from pathlib import Path
from datetime import datetime

from bs4 import BeautifulSoup


def load_publish_module():
    pub_path = Path(__file__).parent / 'publish_to_telegraph.py'
    import importlib.util

    spec = importlib.util.spec_from_file_location('pubmod', str(pub_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def iso_date_from_timestamp(ts):
    return datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--root', default='.', help='site root')
    p.add_argument('--limit', type=int, default=0)
    p.add_argument('--dry-run', action='store_true')
    args = p.parse_args()

    root = Path(args.root)
    pub = load_publish_module()
    sitemap = pub.get_files_from_sitemap(root)
    if args.limit:
        sitemap = sitemap[: args.limit]

    updated = 0
    for fp, orig_url in sitemap:
        # only operate on HTML files
        if not fp.exists() or not fp.suffix.lower().endswith('.html'):
            continue
        try:
            html = fp.read_text(encoding='utf-8')
        except Exception:
            continue

        soup = BeautifulSoup(html, 'html.parser')

        head = soup.head
        if head is None:
            # create head if missing
            head = soup.new_tag('head')
            if soup.html:
                soup.html.insert(0, head)
            else:
                # wrap in minimal html
                newhtml = BeautifulSoup('<html></html>', 'html.parser')
                newhtml.html.append(head)
                newhtml.html.append(soup)
                soup = newhtml

        # canonical
        can = head.find('link', rel='canonical')
        if can:
            can['href'] = orig_url
        else:
            new_can = soup.new_tag('link', rel='canonical', href=orig_url)
            head.append(new_can)

        # skip if there is already an Article JSON-LD
        has_article_jsonld = False
        for s in head.find_all('script', type='application/ld+json'):
            txt = s.string or ''
            if '"@type"' in txt and 'Article' in txt:
                has_article_jsonld = True
                break

        if not has_article_jsonld:
            # build minimal JSON-LD
            # try to get title and published date
            try:
                title, _ = pub.extract_title_and_content(fp.read_text(encoding='utf-8'))
            except Exception:
                title = fp.stem

            # attempt to find time tag or meta in the page
            pub_date = None
            time_el = soup.find('time')
            if time_el and time_el.has_attr('datetime'):
                pub_date = time_el['datetime']

            if not pub_date:
                # fallback to file mtime
                try:
                    pub_date = iso_date_from_timestamp(fp.stat().st_mtime)
                except Exception:
                    pub_date = datetime.utcnow().strftime('%Y-%m-%d')

            jsonld = {
                "@context": "https://schema.org",
                "@type": "Article",
                "mainEntityOfPage": {"@type": "WebPage", "@id": orig_url},
                "headline": title,
                "datePublished": pub_date,
                "dateModified": pub_date,
                "author": {"@type": "Person", "name": "SaaS Verdict"},
                "publisher": {"@type": "Organization", "name": "SaaSVerdict"}
            }

            script = soup.new_tag('script', type='application/ld+json')
            script.string = json.dumps(jsonld, ensure_ascii=False)
            head.append(script)

        if args.dry_run:
            print('[dry] Would update:', fp)
        else:
            fp.write_text(str(soup), encoding='utf-8')
            updated += 1

    print('Updated files:', updated)


if __name__ == '__main__':
    main()
