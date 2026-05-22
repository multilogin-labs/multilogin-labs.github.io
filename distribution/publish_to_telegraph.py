#!/usr/bin/env python3
"""
Simple script to publish site HTML files to telegra.ph.

Usage:
  python distribution/publish_to_telegraph.py --root . --dry-run

Requirements:
  pip install -r distribution/requirements-telegraph.txt

The script will:
  - find HTML files under `--root` (excluding `assets/` and `distribution/`)
  - extract a title and main content (prefers <article> or <main>)
  - upload local images to telegra.ph via the upload endpoint
  - create a Telegraph account (one-time) and store the access token in `.telegraph_token`
  - publish pages and print the resulting Telegraph URLs

This is a pragmatic, best-effort tool — tweak selectors as needed for your HTML structure.
"""
import argparse
import json
import os
import sys
from pathlib import Path

import requests
import time
from bs4 import BeautifulSoup, Comment
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, urljoin
from pathlib import Path as _Path

TELEGRAPH_API_BASE = "https://api.telegra.ph"
TELEGRAPH_UPLOAD = "https://telegra.ph/upload"
TOKEN_FILE = ".telegraph_token"


def token_from_env():
    """Return token from TELEGRAPH_ACCESS_TOKEN env var or None."""
    return os.environ.get('TELEGRAPH_ACCESS_TOKEN')


def find_html_files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        # skip assets and distribution directories
        parts = Path(dirpath).parts
        if "assets" in parts or "distribution" in parts:
            continue
        for fn in filenames:
            if fn.lower().endswith('.html'):
                yield Path(dirpath) / fn


def extract_title_and_content(html_text: str):
    soup = BeautifulSoup(html_text, 'html.parser')
    title = None
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
    h1 = soup.find('h1')
    if h1 and (not title or len(h1.get_text(strip=True)) > len(title)):
        title = h1.get_text(strip=True)

    # try a series of common selectors for main/article content and pick the largest one
    selectors = [
        'article',
        'main',
        "div[class*='article']",
        "div[class*='article-body']",
        "div[class*='post-content']",
        "div[class*='post-body']",
        "div[class*='entry-content']",
        "div[class*='content']",
        "section[itemprop='articleBody']",
        "div[itemprop='articleBody']",
        "div#content",
        "div[class*='page-content']",
        "section[role='main']",
        "div[class*='main']",
    ]

    best = None
    best_len = 0
    for sel in selectors:
        try:
            el = soup.select_one(sel)
        except Exception:
            el = None
        if el:
            txt_len = len(el.get_text(strip=True))
            if txt_len > best_len:
                best = el
                best_len = txt_len

    main = best or soup.body
    if main is None:
        return title or 'Untitled', ''

    # remove header/footer/nav/scripts/styles/forms/comments inside the main candidate
    for sel in ['header', 'footer', 'nav', 'script', 'style', 'form', 'noscript']:
        for node in main.select(sel):
            node.decompose()

    # remove HTML comments within main
    for element in main.find_all(string=lambda text: isinstance(text, Comment)):
        element.extract()

    # use inner HTML of the main element to preserve nested structure
    try:
        content_html = main.decode_contents().strip()
    except Exception:
        content_html = ''.join(str(child) for child in main.children).strip()

    return title or 'Untitled', content_html


def upload_image(local_path: Path):
    # skip very large files (Telegraph may reject large uploads)
    try:
        size = local_path.stat().st_size
        if size > 5 * 1024 * 1024:
            raise RuntimeError(f'Image too large (>5MB): {local_path} ({size} bytes)')
    except OSError:
        raise

    # robust upload with retries/backoff
    max_retries = 4
    backoff_factor = 2.0
    timeout = 30
    last_exc = None
    for attempt in range(1, max_retries + 1):
        try:
            with open(local_path, 'rb') as fh:
                filename = local_path.name
                files = {'file': (filename, fh)}
                r = requests.post(TELEGRAPH_UPLOAD, files=files, timeout=timeout)
            r.raise_for_status()
            data = r.json()
            if isinstance(data, list) and data and 'src' in data[0]:
                return 'https://telegra.ph' + data[0]['src']
            # unexpected but retry
            last_exc = RuntimeError(f'Unexpected upload response: {data}')
            print(f'Warning: unexpected upload response for {local_path}: {data}', file=sys.stderr)
        except Exception as e:
            last_exc = e
            print(f'Warning: upload attempt {attempt} failed for {local_path}: {e}', file=sys.stderr)

        if attempt < max_retries:
            sleep_time = backoff_factor ** (attempt - 1)
            time.sleep(sleep_time)
            continue
        # exhausted
        raise RuntimeError(f'Upload failed {local_path} after {max_retries} attempts: {last_exc}') from last_exc


def replace_local_images(soup: BeautifulSoup, page_path: Path, root: Path, dry_run: bool = True):
    for img in soup.find_all('img'):
        # support lazy attributes
        src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
        # prefer srcset first candidate
        if not src and img.get('srcset'):
            srcset = img.get('srcset')
            # pick first url in srcset
            src = srcset.split(',')[0].strip().split(' ')[0]
        if not src:
            continue
        if src.startswith('http://') or src.startswith('https://'):
            continue
        # resolve local image path: handle absolute (/assets/...) and relative paths
        if src.startswith('/'):
            img_path = (root / src.lstrip('/')).resolve()
        else:
            img_path = (page_path.parent / src).resolve()
        if not img_path.exists():
            # try repo-root assets fallback (handles pages that reference assets/ from site root)
            alt = (root / src.lstrip('/')).resolve()
            if alt.exists():
                img_path = alt
            else:
                print(f'Warning: image not found {img_path} (tried root {alt})', file=sys.stderr)
                continue
        if dry_run:
            print(f'[dry] would upload image: {img_path}')
            continue
        try:
            tele_url = upload_image(img_path)
            img['src'] = tele_url
        except Exception as e:
            print(f'Warning: failed to upload {img_path}: {e}', file=sys.stderr)
            # leave original src if upload fails
            continue


def get_files_from_sitemap(root: Path):
    sitemap = root / 'sitemap.xml'
    if not sitemap.exists():
        return []
    try:
        tree = ET.parse(sitemap)
    except Exception:
        return []
    root_elem = tree.getroot()
    urls = []
    for elem in root_elem.iter():
        if elem.tag.endswith('loc') and elem.text:
            urls.append(elem.text.strip())
    results = []
    for u in urls:
        parsed = urlparse(u)
        p = parsed.path or '/'
        candidates = []
        if p.endswith('/'):
            candidates.append(root / p.lstrip('/') / 'index.html')
        else:
            candidates.append(root / p.lstrip('/'))
            candidates.append(root / p.lstrip('/') / 'index.html')
            candidates.append(root / (p.lstrip('/') + '.html'))
        found = None
        for c in candidates:
            if c.exists():
                found = c
                break
        if found:
            results.append((found, u))
    return results


def create_account_if_needed(short_name='site'):
    # prefer environment variable (useful to supply your own token)
    env_tok = token_from_env()
    if env_tok:
        return env_tok
    if Path(TOKEN_FILE).exists():
        return Path(TOKEN_FILE).read_text().strip()
    payload = {'short_name': short_name}
    r = requests.post(f'{TELEGRAPH_API_BASE}/createAccount', data=payload)
    r.raise_for_status()
    resp = r.json()
    if resp.get('ok'):
        token = resp['result']['access_token']
        Path(TOKEN_FILE).write_text(token)
        print(f'Created Telegraph account; token saved to {TOKEN_FILE}')
        return token
    raise RuntimeError(f'Failed to create account: {resp}')


def publish_page(token: str, title: str, html_content: str, author_name: str = 'SaaS Verdict'):
    # Prefer sending the full sanitized HTML first so posts match original articles (clickable links, formatting)
    err = None
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        for s in soup(['script', 'style', 'iframe']):
            s.decompose()
        safe_html = str(soup)
        payload_html = {
            'access_token': token,
            'title': title,
            'author_name': author_name,
            'html_content': safe_html,
        }
        r = requests.post(f'{TELEGRAPH_API_BASE}/createPage', data=payload_html)
        r.raise_for_status()
        resp = r.json()
        if resp.get('ok'):
            return resp['result']['url']
        err = resp.get('error')
    except Exception as e:
        err = str(e)

    # Fallback: convert to Telegraph node JSON (preserve anchors/images if possible)
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

    content_nodes = html_to_nodes(html_content)
    if not content_nodes:
        raise RuntimeError('No content extracted for Telegraph page')

    payload = {
        'access_token': token,
        'title': title,
        'author_name': author_name,
        'content': json.dumps(content_nodes, ensure_ascii=False),
    }
    r2 = requests.post(f'{TELEGRAPH_API_BASE}/createPage', data=payload)
    r2.raise_for_status()
    resp2 = r2.json()
    if resp2.get('ok'):
        return resp2['result']['url']

    raise RuntimeError(f'Failed to create page (html attempt err={err}): {resp2}')


def process_file(path: Path, token: str, root: Path, dry_run: bool = True, original_url: str = None, force_publish: bool = False):
    html_text = path.read_text(encoding='utf-8')
    title, content_html = extract_title_and_content(html_text)

    # parse content_html to replace images; if content is empty or tiny, attempt richer fallbacks
    content_soup = BeautifulSoup(content_html, 'html.parser')
    # fallback: if content_soup is empty or too small, try to collect meaningful blocks (headings, lists, tables, etc.)
    if len(content_soup.get_text(strip=True)) < 40:
        full_soup = BeautifulSoup(html_text, 'html.parser')
        # remove header/footer/nav/aside/scripts/styles
        for sel in ['header', 'footer', 'nav', 'aside', 'script', 'style']:
            for node in full_soup.select(sel):
                node.decompose()

        # prefer a range of block-level tags that commonly contain article content
        block_tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'ul', 'ol', 'pre', 'blockquote', 'figure', 'table', 'section', 'div']
        # pick reasonably-sized blocks first
        candidates = [el for el in full_soup.find_all(block_tags) if len(el.get_text(strip=True)) > 60]
        if not candidates:
            # relax threshold if nothing found
            candidates = [el for el in full_soup.find_all(block_tags) if len(el.get_text(strip=True)) > 20]

        if candidates:
            content_soup = BeautifulSoup(''.join(str(el) for el in candidates), 'html.parser')
        else:
            # as last resort, use body inner HTML
            body = full_soup.body
            if body:
                content_soup = BeautifulSoup(''.join(str(child) for child in body.children), 'html.parser')

    replace_local_images(content_soup, path, root, dry_run=dry_run)
    # rewrite anchor hrefs so internal links point to the original site domain
    if original_url:
        base_parsed = urlparse(original_url)
        base_root = f"{base_parsed.scheme}://{base_parsed.netloc}"
        for a_tag in content_soup.find_all('a', href=True):
            href = a_tag['href'].strip()
            if not href:
                continue
            # skip mailto/tel/javascript
            if href.startswith('mailto:') or href.startswith('tel:') or href.startswith('javascript:'):
                continue
            parsed = urlparse(href)
            # absolute http(s) links
            if parsed.scheme in ('http', 'https'):
                # if link points to telegra.ph (or is relative), replace domain with original
                if parsed.netloc.endswith('telegra.ph'):
                    new = base_root + parsed.path
                    if parsed.query:
                        new += '?' + parsed.query
                    if parsed.fragment:
                        new += '#' + parsed.fragment
                    a_tag['href'] = new
                # else: external link, leave as-is
            else:
                # handle scheme-less netloc (//example.com/path)
                if parsed.netloc:
                    a_tag['href'] = 'https:' + href
                else:
                    # relative link -> join with original_url
                    try:
                        new = urljoin(original_url, href)
                        a_tag['href'] = new
                    except Exception:
                        # leave as-is on error
                        pass

    final_html = str(content_soup)
    
    # prepend original link and a note about promo codes (if provided)
    if original_url:
        original_html = f'<p><strong>Original article:</strong> <a href="{original_url}">{original_url}</a></p>'
        note_html = '<p><em>If the promo code in this article does not work, please visit the original page for the latest code.</em></p>'
        final_html = original_html + note_html + final_html
    if len(content_soup.get_text(strip=True)) < 10:
        # nothing meaningful extracted — skip unless forced
        if not force_publish:
            print(f'Skipping {path}: no meaningful content extracted', file=sys.stderr)
            return None

    if dry_run:
        print(f'[dry] Would publish: {path} -> "{title}"')
        return None

    try:
        url = publish_page(token, title, final_html)
        print(f'Published {path} -> {url}')
        return title, url
    except Exception:
        # re-raise for caller logging
        raise


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--root', default='.', help='site root to scan')
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--limit', type=int, default=0, help='limit number of pages (0 = all)')
    p.add_argument('--account-name', default='saasverdict', help='short name for Telegraph account')
    p.add_argument('--force', action='store_true', help='force publish pages even with small content')
    args = p.parse_args()

    root = Path(args.root)
    token = None
    if not args.dry_run:
        token = create_account_if_needed(args.account_name)

    # prefer sitemap order if available
    sitemap_entries = get_files_from_sitemap(root)
    if sitemap_entries:
        files = sitemap_entries
    else:
        files = [(p, None) for p in list(find_html_files(root))]

    if args.limit:
        files = files[: args.limit]

    print(f'Found {len(files)} HTML files to consider (using sitemap: {bool(sitemap_entries)})')

    links_out = Path(__file__).parent / 'telegraph_links.txt'
    for fp, orig_url in files:
        try:
            res = process_file(fp, token, root, dry_run=args.dry_run, original_url=orig_url, force_publish=args.force)
            if res and not args.dry_run:
                title, url = res
                # append link record
                with open(links_out, 'a', encoding='utf-8') as lf:
                    lf.write(f"{title} | {url}\n")
        except Exception as e:
            print(f'Error processing {fp}: {e}', file=sys.stderr)


if __name__ == '__main__':
    main()
