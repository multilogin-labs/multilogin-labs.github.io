#!/usr/bin/env python3
import os
import json
import time
import logging
from pathlib import Path
from datetime import datetime

import requests
from requests.exceptions import RequestException

TELEGRAPH_API_BASE = "https://api.telegra.ph"
TOKEN_FILE = ".telegraph_token"

COMMENTS_FILE = "multilogin_linkedin_comments_expert.txt"
OUTPUT_FILE = "multilogin_telegraph_links.txt"
COMMENTS_PER_PAGE = 50
MAX_CONTENT_BYTES = 60 * 1024  # safe 60KB limit per page

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent
OUTPUT_PATH = SCRIPT_DIR / OUTPUT_FILE
PUBLISHED_JSON = SCRIPT_DIR / "telegraph_published.json"

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')


def get_token():
    token = os.environ.get('TELEGRAPH_ACCESS_TOKEN')
    if token:
        return token
    # try repo-root then script dir
    if (REPO_ROOT / TOKEN_FILE).exists():
        return (REPO_ROOT / TOKEN_FILE).read_text().strip()
    if (SCRIPT_DIR / TOKEN_FILE).exists():
        return (SCRIPT_DIR / TOKEN_FILE).read_text().strip()
    # create account
    payload = {'short_name': 'multilogin-comments'}
    r = requests.post(f'{TELEGRAPH_API_BASE}/createAccount', data=payload, timeout=15)
    r.raise_for_status()
    resp = r.json()
    if resp.get('ok'):
        token = resp['result']['access_token']
        (SCRIPT_DIR / TOKEN_FILE).write_text(token)
        logging.info(f'Created Telegraph account and saved token to {SCRIPT_DIR / TOKEN_FILE}')
        return token
    raise RuntimeError(f'Failed to create account: {resp}')


class FloodWait(Exception):
    def __init__(self, seconds: int):
        super().__init__(f'FLOOD_WAIT_{seconds}')
        self.seconds = int(seconds)


def publish_page(token, title, content_nodes, retries=3):
    payload = {
        'access_token': token,
        'title': title,
        'author_name': 'SaaS Verdict',
        'content': json.dumps(content_nodes, ensure_ascii=False),
    }
    for attempt in range(1, retries + 1):
        try:
            r = requests.post(f'{TELEGRAPH_API_BASE}/createPage', data=payload, timeout=20)
            r.raise_for_status()
            resp = r.json()
            if resp.get('ok'):
                return resp['result']['url']
            # handle API-level errors
            err = resp.get('error')
            if isinstance(err, str) and err.startswith('FLOOD_WAIT'):
                # extract seconds
                import re
                m = re.search(r'FLOOD_WAIT_(\d+)', err)
                if m:
                    secs = int(m.group(1))
                    raise FloodWait(secs)
            raise RuntimeError(f'API error: {resp}')
        except FloodWait:
            # re-raise to be handled by caller (we don't sleep here because waits may be long)
            raise
        except RequestException as e:
            logging.warning(f'Network error publishing {title} attempt {attempt}: {e}')
            if attempt < retries:
                time.sleep(2 ** attempt)
                continue
            raise


def find_comments_file():
    cand = REPO_ROOT / COMMENTS_FILE
    if cand.exists():
        return cand
    cand2 = SCRIPT_DIR / COMMENTS_FILE
    if cand2.exists():
        return cand2
    raise RuntimeError(f'Comments file not found (tried {cand} and {cand2})')


def chunk_group_by_size(group):
    chunks = []
    current = []
    for c in group:
        candidate = current + [c]
        nodes = [{"tag": "p", "children": [x]} for x in candidate]
        size = len(json.dumps(nodes, ensure_ascii=False).encode('utf-8'))
        if size > MAX_CONTENT_BYTES:
            if not current:
                # single comment too large; publish it alone
                chunks.append([c])
                current = []
            else:
                chunks.append(current)
                current = [c]
        else:
            current.append(c)
    if current:
        chunks.append(current)
    return chunks


def load_published():
    if PUBLISHED_JSON.exists():
        try:
            data = json.loads(PUBLISHED_JSON.read_text(encoding='utf-8'))
            return data.get('published', [])
        except Exception:
            return []
    return []


def save_published(published_list):
    out = {"published": published_list, "summary": f"Published {len(published_list)} pages", "log_file": str(SCRIPT_DIR / 'telegraph_publish_log.txt')}
    PUBLISHED_JSON.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')


def append_link(title, url):
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open('a', encoding='utf-8') as f:
        f.write(f"{title} | {url}\n")
        f.flush()


def main(test_pages=None):
    token = get_token()
    # Resume mode: if a remaining-file exists, prefer that to avoid reposting
    rem_path = SCRIPT_DIR / "telegraph_remaining.json"
    if rem_path.exists():
        try:
            rem_data = json.loads(rem_path.read_text(encoding='utf-8'))
            remaining_groups = rem_data.get('remaining', []) or []
        except Exception:
            remaining_groups = []
        if remaining_groups:
            logging.info(f"Resuming publish from {rem_path} with {len(remaining_groups)} groups")
            published = load_published()
            total = 0
            for idx, sg in enumerate(remaining_groups, 1):
                title = f"Multilogin LinkedIn Comments (resumed) #{idx}"
                content_nodes = [{"tag": "p", "children": [c]} for c in sg]
                try:
                    url = publish_page(token, title, content_nodes)
                    logging.info(f"Published: {title} | {url}")
                    append_link(title, url)
                    published.append({"title": title, "url": url, "count": len(sg), "timestamp": datetime.utcnow().isoformat()})
                    save_published(published)
                    total += len(sg)
                except FloodWait as fw:
                    logging.error(f"Flood wait {fw.seconds}s encountered while resuming at group {idx}")
                    # save remaining groups starting from this idx
                    new_remaining = remaining_groups[idx-1:]
                    rem_path.write_text(json.dumps({"remaining": new_remaining, "created": datetime.utcnow().isoformat()}, ensure_ascii=False, indent=2), encoding='utf-8')
                    logging.info(f"Saved {len(new_remaining)} remaining groups to {rem_path}; exit resume.")
                    return
                except Exception as e:
                    logging.error(f"Failed to publish resumed group {idx}: {e}")
                time.sleep(2)
            # resume succeeded, remove remaining file
            try:
                rem_path.unlink()
            except Exception:
                pass
            logging.info(f"Resume complete. Published {total} comments from {rem_path}")
            return
    comments_path = find_comments_file()
    comments = [line.strip() for line in comments_path.read_text(encoding='utf-8').splitlines() if line.strip()]
    pages = [comments[i:i+COMMENTS_PER_PAGE] for i in range(0, len(comments), COMMENTS_PER_PAGE)]
    published = load_published()
    total = 0
    for idx, group in enumerate(pages, 1):
        title_base = f"Multilogin LinkedIn Comments #{idx}"
        # ensure page is below size limit by chunking
        subgroups = chunk_group_by_size(group)
        for sub_idx, sg in enumerate(subgroups, 1):
            title = title_base if len(subgroups) == 1 else f"{title_base} Part {sub_idx}"
            content_nodes = [{"tag": "p", "children": [c]} for c in sg]
            try:
                url = publish_page(token, title, content_nodes)
                logging.info(f"Published: {title} | {url}")
                append_link(title, url)
                published.append({"title": title, "url": url, "count": len(sg), "timestamp": datetime.utcnow().isoformat()})
                save_published(published)
                total += len(sg)
            except FloodWait as fw:
                logging.error(f"Flood wait {fw.seconds}s encountered while publishing {title}")
                # If short wait, sleep and retry once. If long, save remaining pages and exit.
                if fw.seconds <= 600:
                    wait = fw.seconds + 5
                    logging.info(f"Sleeping {wait}s then retrying {title} once")
                    time.sleep(wait)
                    try:
                        url = publish_page(token, title, content_nodes)
                        logging.info(f"Published after wait: {title} | {url}")
                        append_link(title, url)
                        published.append({"title": title, "url": url, "count": len(sg), "timestamp": datetime.utcnow().isoformat()})
                        save_published(published)
                        total += len(sg)
                        continue
                    except Exception as e2:
                        logging.error(f"Retry after flood-wait failed: {e2}")
                # For long waits or failed retry, save remaining and exit.
                remaining = []
                # include current subgroup and rest of subgroups for this page
                for rest_s in subgroups[sub_idx-1:]:
                    remaining.append(rest_s)
                # include subsequent pages (chunked)
                for j in range(idx, len(pages)):
                    pg = pages[j]
                    next_subs = chunk_group_by_size(pg)
                    for ns in next_subs:
                        remaining.append(ns)
                rem_path = SCRIPT_DIR / "telegraph_remaining.json"
                rem_data = {"remaining": remaining, "created": datetime.utcnow().isoformat(), "note": "Resume later to continue publishing"}
                rem_path.write_text(json.dumps(rem_data, ensure_ascii=False, indent=2), encoding='utf-8')
                logging.info(f"Saved {len(remaining)} remaining page groups to {rem_path}; exiting.")
                save_published(published)
                return
            except Exception as e:
                logging.error(f"Failed to publish {title}: {e}")
            time.sleep(2)
        # optional: small pause between pages
        time.sleep(1)
        if test_pages and idx >= test_pages:
            logging.info("Test limit reached, stopping early.")
            break
    logging.info(f"Done. Published {len(published)} pages, total comments published {total}. Links saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    # You can pass an env var TEST_PAGES to limit how many page groups to run (useful for testing)
    tp = os.environ.get('TEST_PAGES')
    main(test_pages=int(tp) if tp and tp.isdigit() else None)
