#!/usr/bin/env python3
"""
Fix internal links in already-published Telegraph pages by editing pages to point
internal anchors back to the original site domain.

Usage:
  python distribution/fix_telegraph_internal_links.py --root . [--dry-run] [--limit N]

This script reads `distribution/telegraph_links.txt` (lines: "Title | https://telegra.ph/...")
matches each Title to a local HTML file (via sitemap), rebuilds the article HTML
(with image uploads as needed), rewrites anchor hrefs to the original site's domain,
then calls the Telegraph API `editPage/<path>` to update the page in-place.

Be careful: editing many pages can trigger FLOOD_WAIT rate limits; the script
supports a small sleep between requests and will save remaining work if a long
FLOOD_WAIT is encountered.
"""
import argparse
import json
import time
import sys
from pathlib import Path
from urllib.parse import urlparse, urljoin

#!/usr/bin/env python3
"""
Fix internal links in already-published Telegraph pages by editing pages to point
internal anchors back to the original site domain.

Usage:
  python distribution/fix_telegraph_internal_links.py --root . [--dry-run] [--limit N]

This script reads `distribution/telegraph_links.txt` (lines: "Title | https://telegra.ph/..."),
matches each Title to a local HTML file (via sitemap), rebuilds the article HTML
(with image uploads as needed), rewrites anchor hrefs to the original site's domain,
then calls the Telegraph API `editPage/<path>` to update the page in-place.

Be careful: editing many pages can trigger FLOOD_WAIT rate limits; the script
supports a small sleep between requests and will save remaining work if a long
FLOOD_WAIT is encountered.
"""
import argparse
import json
import time
import sys
from pathlib import Path
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup
import importlib.util

TELEGRAPH_API_BASE = 'https://api.telegra.ph'


def load_publish_module():
    pub_path = Path(__file__).parent / 'publish_to_telegraph.py'
    spec = importlib.util.spec_from_file_location('pubmod', str(pub_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def normalize_title(t: str) -> str:
    return ' '.join(t.split()).strip().lower()


def build_final_html(pub, page_path: Path, root: Path, original_url: str, strip_images: bool = False, excerpt_paragraphs: int = 0):
    html_text = page_path.read_text(encoding='utf-8')
    title, content_html = pub.extract_title_and_content(html_text)
    content_soup = BeautifulSoup(content_html, 'html.parser')
    # fallback similar to publish_to_telegraph.process_file
    if len(content_soup.get_text(strip=True)) < 40:
        full_soup = BeautifulSoup(html_text, 'html.parser')
        for sel in ['header', 'footer', 'nav', 'aside', 'script', 'style']:
            for node in full_soup.select(sel):
                node.decompose()
        block_tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'ul', 'ol', 'pre', 'blockquote', 'figure', 'table', 'section', 'div']
        candidates = [el for el in full_soup.find_all(block_tags) if len(el.get_text(strip=True)) > 60]
        if not candidates:
            candidates = [el for el in full_soup.find_all(block_tags) if len(el.get_text(strip=True)) > 20]
        if candidates:
            content_soup = BeautifulSoup(''.join(str(el) for el in candidates), 'html.parser')
        else:
            body = full_soup.body
            if body:
                content_soup = BeautifulSoup(''.join(str(child) for child in body.children), 'html.parser')

    # handle images: either strip (fast, avoids uploads) or upload to Telegraph
    if strip_images:
        for img in content_soup.find_all('img'):
            img.decompose()
    else:
        # replace_local_images will skip absolute http(s) urls
        pub.replace_local_images(content_soup, page_path, root, dry_run=False)

    # rewrite anchor hrefs so internal links point to the original site domain
    if original_url:
        base_parsed = urlparse(original_url)
        base_root = f"{base_parsed.scheme}://{base_parsed.netloc}"
        for a_tag in content_soup.find_all('a', href=True):
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
                    # scheme-less with netloc (//example.com/path)
                    a_tag['href'] = 'https:' + href
                else:
                    try:
                        new = urljoin(original_url, href)
                        a_tag['href'] = new
                    except Exception:
                        pass

    # prepend original link and a short note (helps Google associate the source)
    original_html = ''
    note_html = ''
    if original_url:
        original_html = f'<p><strong>Original article:</strong> <a href="{original_url}">{original_url}</a></p>'
        note_html = '<p><em>If the promo code in this article does not work, please visit the original page for the latest code.</em></p>'

    if excerpt_paragraphs and excerpt_paragraphs > 0:
        # build an excerpt from the first N paragraphs (fallback to text snippet)
        ps = content_soup.find_all('p')
        if ps:
            excerpt_html = ''.join(str(p) for p in ps[:excerpt_paragraphs])
        else:
            txt = content_soup.get_text(separator=' ', strip=True)
            excerpt_html = (txt[:600] + '...') if len(txt) > 600 else txt
        final_html = original_html + note_html + excerpt_html
    else:
        final_html = original_html + note_html + str(content_soup)

    return final_html


def parse_telegraph_links(path: Path):
    if not path.exists():
        print(f'No telegraph links file: {path}', file=sys.stderr)
        return []
    entries = []
    for ln in path.read_text(encoding='utf-8').splitlines():
        ln = ln.strip()
        if not ln:
            continue
        if '|' not in ln:
            continue
        title, tele = ln.split('|', 1)
        entries.append((title.strip(), tele.strip()))
    return entries


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--root', default='.', help='site root to scan')
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--limit', type=int, default=0)
    p.add_argument('--sleep', type=float, default=1.5, help='seconds between edits')
    p.add_argument('--strip-images', action='store_true', help='remove <img> tags instead of uploading')
    p.add_argument('--excerpt-paragraphs', type=int, default=0, help='if >0, replace content with first N paragraphs')
    p.add_argument('--account-name', default='saasverdict')
    args = p.parse_args()

    root = Path(args.root)
    pub = load_publish_module()

    links_file = Path(__file__).parent / 'telegraph_links.txt'
    entries = parse_telegraph_links(links_file)
    if args.limit:
        entries = entries[: args.limit]

    # build lookup of local files by normalized title
    sitemap = pub.get_files_from_sitemap(root)
    local_map = {}
    for fp, orig_url in sitemap:
        try:
            html = fp.read_text(encoding='utf-8')
            t, _ = pub.extract_title_and_content(html)
            local_map[normalize_title(t)] = (fp, orig_url)
        except Exception:
            continue

    token = pub.create_account_if_needed(args.account_name)

    remaining = []
    successes = 0
    for title, tele_url in entries:
        norm = normalize_title(title)
        if norm not in local_map:
            print(f'No local file found for title: {title}', file=sys.stderr)
            continue
        fp, orig_url = local_map[norm]
        print(f'Preparing edit for: {fp} -> {tele_url}')
        final_html = build_final_html(pub, fp, root, orig_url, strip_images=args.strip_images, excerpt_paragraphs=args.excerpt_paragraphs)
        if args.dry_run:
            print(f'[dry] Would edit {tele_url} with updated internal links')
            continue

        # perform editPage
        parsed = urlparse(tele_url)
        page_path = parsed.path.lstrip('/')
        edit_url = f"{TELEGRAPH_API_BASE}/editPage/{page_path}"
        payload = {
            'access_token': token,
            'title': title,
            'author_name': 'SaaS Verdict',
            'html_content': final_html,
        }

        try:
            r = requests.post(edit_url, data=payload, timeout=60)
            r.raise_for_status()
            resp = r.json()
            if resp.get('ok'):
                print(f'Edited {tele_url} successfully')
                successes += 1
                time.sleep(args.sleep)
                continue
            err = resp.get('error', '')

            # If server rejects html_content, try sending content as Telegraph Node JSON
            if isinstance(err, str) and ('CONTENT_REQUIRED' in err or 'CONTENT_FORMAT_INVALID' in err):
                # convert final_html to node array
                def html_to_nodes(html: str):
                    soup = BeautifulSoup(html, 'html.parser')
                    from bs4 import NavigableString, Tag

                    def render_node(n):
                        if isinstance(n, NavigableString):
                            s = str(n)
                            return s if s.strip() else None
                        if isinstance(n, Tag):
                            name = n.name.lower()
                            if name in ('script', 'style'):
                                return None
                            if name == 'a':
                                href = n.get('href') or ''
                                text = n.get_text(separator=' ', strip=True)
                                node = {'tag': 'a', 'attrs': {'href': href}, 'children': [text] if text else []}
                                return node
                            if name == 'img':
                                src = n.get('src') or n.get('data-src') or n.get('data-lazy-src')
                                if not src:
                                    return None
                                attrs = {'src': src}
                                alt = n.get('alt')
                                if alt:
                                    attrs['alt'] = alt
                                return {'tag': 'img', 'attrs': attrs}
                            children = []
                            for c in n.children:
                                r = render_node(c)
                                if r is None:
                                    continue
                                if isinstance(r, list):
                                    children.extend(r)
                                else:
                                    children.append(r)
                            if not children:
                                return None
                            if len(children) == 1 and isinstance(children[0], str):
                                return children[0]
                            return children
                        return None

                    nodes = []
                    for el in soup.find_all(['p', 'h1', 'h2', 'h3', 'li', 'blockquote'], recursive=True):
                        children = []
                        for c in el.children:
                            r = render_node(c)
                            if r is None:
                                continue
                            if isinstance(r, list):
                                children.extend(r)
                            else:
                                children.append(r)
                        if not children:
                            txt = el.get_text(separator=' ', strip=True)
                            if txt:
                                children = [txt]
                        if children:
                            nodes.append({'tag': 'p', 'children': children})

                    if not nodes:
                        txt = soup.get_text(separator=' ', strip=True)
                        if txt:
                            nodes.append({'tag': 'p', 'children': [txt]})
                    return nodes

                content_nodes = html_to_nodes(final_html)
                if not content_nodes:
                    print(f'Could not extract nodes for {tele_url}', file=sys.stderr)
                else:
                    payload2 = {
                        'access_token': token,
                        'title': title,
                        'author_name': 'SaaS Verdict',
                        'content': json.dumps(content_nodes, ensure_ascii=False),
                    }
                    r2 = requests.post(edit_url, data=payload2, timeout=60)
                    r2.raise_for_status()
                    resp2 = r2.json()
                    if resp2.get('ok'):
                        print(f'Edited {tele_url} successfully (node fallback)')
                        successes += 1
                        time.sleep(args.sleep)
                        continue
                    else:
                        print(f'Fallback node edit failed for {tele_url}: {resp2}', file=sys.stderr)
                        # fall through to general error handling below

            # handle flood wait
            if isinstance(err, str) and 'FLOOD_WAIT' in err:
                # parse seconds
                import re

                m = re.search(r'FLOOD_WAIT_(\d+)', err)
                secs = int(m.group(1)) if m else 0
                if secs and secs <= 300:
                    print(f'Encountered FLOOD_WAIT {secs}s, sleeping...', file=sys.stderr)
                    time.sleep(secs + 5)
                    # retry once
                    r2 = requests.post(edit_url, data=payload, timeout=60)
                    r2.raise_for_status()
                    resp2 = r2.json()
                    if resp2.get('ok'):
                        print(f'Edited {tele_url} after wait')
                        successes += 1
                        time.sleep(args.sleep)
                        continue
                # long wait: save remaining and exit
                print(f'Long FLOOD_WAIT ({err}), saving remaining and aborting', file=sys.stderr)
                remaining.append((title, tele_url))
                break

            # other errors: try once more after short sleep
            print(f'Error editing {tele_url}: {resp}', file=sys.stderr)
            time.sleep(2)
            r3 = requests.post(edit_url, data=payload, timeout=60)
            r3.raise_for_status()
            resp3 = r3.json()
            if resp3.get('ok'):
                print(f'Edited {tele_url} on retry')
                successes += 1
                time.sleep(args.sleep)
                continue
            print(f'Failed to edit {tele_url}: {resp3}', file=sys.stderr)
        except Exception as e:
            print(f'Exception while editing {tele_url}: {e}', file=sys.stderr)
            remaining.append((title, tele_url))
            break

    # save remaining work if any
    if remaining:
        out = Path(__file__).parent / 'telegraph_fix_remaining.json'
        out.write_text(json.dumps(remaining, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f'Saved {len(remaining)} remaining edits to {out}', file=sys.stderr)

    print(f'Done. Edited: {successes}, Remaining saved: {len(remaining)}')


if __name__ == '__main__':
    main()
