#!/usr/bin/env python3
"""
Generate CSV report of published Telegraph posts mapping back to local files.

Output: distribution/telegraph_publish_report.csv
Columns: title,telegraph_url,local_path,orig_url
"""
import argparse
import csv
from pathlib import Path


def load_publish_module():
    pub_path = Path(__file__).parent / 'publish_to_telegraph.py'
    import importlib.util

    spec = importlib.util.spec_from_file_location('pubmod', str(pub_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def normalize_title(t: str) -> str:
    return ' '.join(t.split()).strip().lower()


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
    p.add_argument('--root', default='.')
    args = p.parse_args()

    root = Path(args.root)
    pub = load_publish_module()
    sitemap = pub.get_files_from_sitemap(root)

    local_map = {}
    for fp, orig in sitemap:
        try:
            title, _ = pub.extract_title_and_content(fp.read_text(encoding='utf-8'))
            local_map[normalize_title(title)] = (str(fp.relative_to(root)), orig)
        except Exception:
            continue

    links = parse_links(Path(__file__).parent / 'telegraph_links.txt')
    out = Path(__file__).parent / 'telegraph_publish_report.csv'
    with open(out, 'w', newline='', encoding='utf-8') as cf:
        writer = csv.writer(cf)
        writer.writerow(['title', 'telegraph_url', 'local_path', 'orig_url'])
        for title, tele in links:
            norm = normalize_title(title)
            local_path, orig = local_map.get(norm, ('', ''))
            writer.writerow([title, tele, local_path, orig])

    print('Wrote report to', out)


if __name__ == '__main__':
    main()
