#!/usr/bin/env python3
"""Inject reading-time meta + timeRequired into guide pages.

Counts visible text words inside <main>, converts to ISO 8601 duration (PT5M etc.)
and adds:
  - <meta name="twitter:label1"> / data1 = "Reading time"
  - merges `timeRequired` into the first Article/HowTo/TechArticle JSON-LD block
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUIDES = ROOT / "guides"

WPM = 220
TAG = re.compile(r"<[^>]+>")
SCRIPT_STYLE = re.compile(r"<(script|style)\b[^>]*>.*?</\1>", re.S | re.I)
MAIN = re.compile(r"<main\b[^>]*>(.*?)</main>", re.S | re.I)
JSONLD = re.compile(
    r'(<script\s+type="application/ld\+json"[^>]*>)([\s\S]*?)(</script>)',
    re.IGNORECASE,
)
EXISTING_LABEL = re.compile(r'name=["\']twitter:label1["\']', re.I)


def word_count(html: str) -> int:
    m = MAIN.search(html)
    body = m.group(1) if m else html
    body = SCRIPT_STYLE.sub("", body)
    text = TAG.sub(" ", body)
    return len([w for w in text.split() if w.strip()])


def minutes(words: int) -> int:
    return max(1, round(words / WPM))


TW_IMG_TAG = re.compile(r'(<meta\b[^>]*\bname=["\']twitter:image["\'][^>]*>)', re.I)


def inject_twitter_label(text: str, mins: int) -> str:
    if EXISTING_LABEL.search(text):
        return text
    meta = (
        f'<meta name="twitter:label1" content="Reading time"/>\n'
        f'<meta name="twitter:data1" content="{mins} min read"/>'
    )
    m = TW_IMG_TAG.search(text)
    if m:
        return text[: m.end()] + "\n" + meta + text[m.end():]
    if "</head>" in text:
        return text.replace("</head>", meta + "\n</head>", 1)
    return text


def inject_time_required(text: str, mins: int) -> str:
    changed = False

    def replace(match: re.Match) -> str:
        nonlocal changed
        opening, body, closing = match.group(1), match.group(2), match.group(3)
        try:
            data = json.loads(body.strip())
        except json.JSONDecodeError:
            return match.group(0)
        graph = data.get("@graph") if isinstance(data, dict) else None
        items = graph if isinstance(graph, list) else [data]
        target_types = {"Article", "TechArticle", "HowTo"}
        updated = False
        for item in items:
            if not isinstance(item, dict):
                continue
            t = item.get("@type")
            t_set = {t} if isinstance(t, str) else (set(t) if isinstance(t, list) else set())
            if t_set & target_types and "timeRequired" not in item:
                item["timeRequired"] = f"PT{mins}M"
                updated = True
                break
        if not updated:
            return match.group(0)
        changed = True
        pretty = json.dumps(data, indent=2, ensure_ascii=False)
        return f"{opening}\n{pretty}\n{closing}"

    new = JSONLD.sub(replace, text)
    return new if changed else text


def main() -> None:
    n_total = 0
    n_changed = 0
    for path in sorted(GUIDES.rglob("index.html")):
        text = path.read_text(encoding="utf-8")
        n_total += 1
        words = word_count(text)
        mins = minutes(words)
        new = inject_twitter_label(text, mins)
        new = inject_time_required(new, mins)
        if new != text:
            path.write_text(new, encoding="utf-8")
            n_changed += 1
    print(f"add_reading_time: guides={n_total} updated={n_changed}")


if __name__ == "__main__":
    main()
