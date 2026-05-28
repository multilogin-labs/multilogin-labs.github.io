#!/usr/bin/env python3
"""Find every JSON-LD block on every HTML page, validate JSON, re-emit with 2-space indent.

Goals:
- Fix runaway-indent corruption introduced by successive regex patches.
- Surface JSON parse errors early (CI fail).
- Keep payload semantically identical (same dict/list structure).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {"scripts", "node_modules", ".git", "__pycache__"}
SKIP_FILES = {ROOT / "index.html"}  # homepage is performance-locked

JSONLD = re.compile(
    r'(<script\s+type="application/ld\+json"[^>]*>)([\s\S]*?)(</script>)',
    re.IGNORECASE,
)


def iter_html() -> list[Path]:
    out: list[Path] = []
    for p in ROOT.rglob("*.html"):
        rel = p.relative_to(ROOT)
        parts = set(rel.parts)
        if parts & SKIP_DIRS:
            continue
        if p.resolve() in {f.resolve() for f in SKIP_FILES}:
            continue
        out.append(p)
    return out


def normalize_text(text: str, source: str) -> tuple[str, bool, list[str]]:
    errors: list[str] = []
    changed = False

    def replace(match: re.Match) -> str:
        nonlocal changed
        opening = match.group(1)
        body = match.group(2)
        closing = match.group(3)
        stripped = body.strip()
        if not stripped:
            return match.group(0)
        try:
            data = json.loads(stripped)
        except json.JSONDecodeError as exc:
            errors.append(f"{source}: invalid JSON-LD ({exc.msg} at line {exc.lineno})")
            return match.group(0)
        pretty = json.dumps(data, indent=2, ensure_ascii=False)
        new_block = f"{opening}\n{pretty}\n{closing}"
        if new_block != match.group(0):
            changed = True
        return new_block

    new_text = JSONLD.sub(replace, text)
    return new_text, changed, errors


def main() -> int:
    files = iter_html()
    total_changed = 0
    all_errors: list[str] = []
    for path in files:
        raw = path.read_text(encoding="utf-8")
        new, changed, errors = normalize_text(raw, str(path.relative_to(ROOT)))
        all_errors.extend(errors)
        if changed and not errors:
            path.write_text(new, encoding="utf-8")
            total_changed += 1
    print(f"normalize_jsonld: files normalized = {total_changed}")
    if all_errors:
        for err in all_errors:
            print(f"  ERROR {err}", file=sys.stderr)
        print(f"normalize_jsonld: {len(all_errors)} invalid JSON-LD block(s)", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
