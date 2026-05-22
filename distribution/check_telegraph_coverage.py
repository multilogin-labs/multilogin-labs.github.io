#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
import importlib.util


def load_publish_module():
    pub_path = Path(__file__).parent / 'publish_to_telegraph.py'
    spec = importlib.util.spec_from_file_location('pubmod', str(pub_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def normalize_title(t: str) -> str:
    return ' '.join(t.split()).strip().lower()


def parse_telegraph_links(path: Path):
    if not path.exists():
        return []
    items = []
    for ln in path.read_text(encoding='utf-8').splitlines():
        ln = ln.strip()
        if not ln:
            continue
        if '|' in ln:
            title, url = ln.rsplit('|', 1)
            items.append((title.strip(), url.strip()))
        else:
            # fallback: whole line as title
            items.append((ln, ''))
    return items


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--root', default='.')
    args = p.parse_args()

    root = Path(args.root)
    pub = load_publish_module()

    sitemap = pub.get_files_from_sitemap(root)
    sitemap_map = {}
    for fp, orig in sitemap:
        try:
            html = fp.read_text(encoding='utf-8')
            title, _ = pub.extract_title_and_content(html)
            sitemap_map[normalize_title(title)] = {
                'title': title,
                'path': str(fp.relative_to(root)),
                'orig_url': orig,
            }
        except Exception:
            continue

    tele_links = parse_telegraph_links(Path(__file__).parent / 'telegraph_links.txt')
    tele_map = {}
    for title, url in tele_links:
        tele_map[normalize_title(title)] = {'title': title, 'url': url}

    sitemap_count = len(sitemap_map)
    published_count = len(tele_map)

    sitemap_titles = set(sitemap_map.keys())
    published_titles = set(tele_map.keys())

    missing = sorted(list(sitemap_titles - published_titles))
    extra = sorted(list(published_titles - sitemap_titles))

    report = {
        'sitemap_count': sitemap_count,
        'published_count': published_count,
        'missing_count': len(missing),
        'extra_count': len(extra),
        'missing_samples': [sitemap_map[k] for k in missing[:50]],
        'extra_samples': [tele_map[k] for k in extra[:50]],
    }

    out = Path(__file__).parent / 'telegraph_coverage_report.json'
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
