#!/usr/bin/env python3
"""
Create a site page that lists all Telegraph posts (from distribution/telegraph_links.txt)
and add the page to sitemap.xml so Google can discover Telegraph URLs via your site.

Usage:
  python distribution/create_telegraph_index.py --root .
"""
import argparse
import html
from pathlib import Path
from datetime import datetime


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--root', default='.', help='site root')
    args = p.parse_args()

    root = Path(args.root)
    links_file = Path(__file__).parent / 'telegraph_links.txt'
    if not links_file.exists():
        print('Missing telegraph_links.txt')
        return

    items = []
    for ln in links_file.read_text(encoding='utf-8').splitlines():
        ln = ln.strip()
        if not ln:
            continue
        if '|' in ln:
            title, url = ln.rsplit('|', 1)
            items.append((title.strip(), url.strip()))
        else:
            items.append((ln, ''))

    # build HTML index
    list_items = []
    for title, url in items:
        t = html.escape(title)
        if url:
            list_items.append(f'<li><a href="{url}" rel="noopener" target="_blank">{t}</a></li>')
        else:
            list_items.append(f'<li>{t}</li>')

    html_page = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Telegraph posts index — SaaSVerdict</title>
</head>
<body>
  <h1>Telegraph posts</h1>
  <p>This page lists posts we published to telegra.ph (external hosting).</p>
  <ul>
    {''.join(list_items)}
  </ul>
</body>
</html>
"""

    out = root / 'telegraph-index.html'
    out.write_text(html_page, encoding='utf-8')
    print('Wrote', out)

    # update sitemap.xml: add a url entry if not present
    sitemap = root / 'sitemap.xml'
    if not sitemap.exists():
        print('No sitemap.xml found; skipping sitemap update')
        return

    sitemap_text = sitemap.read_text(encoding='utf-8')
    loc = 'https://saasverdict.com/telegraph-index.html'
    if loc in sitemap_text:
        print('sitemap already contains telegraph-index')
        return

    # append new <url> entry before closing </urlset>
    lastmod = datetime.utcnow().strftime('%Y-%m-%d')
    new_entry = f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{lastmod}</lastmod>\n    <priority>0.50</priority>\n  </url>\n"
    sitemap_text = sitemap_text.replace('</urlset>', new_entry + '</urlset>')
    sitemap.write_text(sitemap_text, encoding='utf-8')
    print('Updated sitemap.xml')


if __name__ == '__main__':
    main()
