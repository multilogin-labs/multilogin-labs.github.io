#!/usr/bin/env python3
"""Validate /data JSON files against local schemas (stdlib only)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def require(obj: dict, key: str, ctx: str) -> None:
    if key not in obj:
        raise ValueError(f"{ctx}: missing required field '{key}'")


def validate_benchmark(path: Path) -> None:
    obj = load(path)
    require(obj, "schema", path.name)
    if obj["schema"] != "multilogin-labs/benchmark/v1":
        raise ValueError(f"{path.name}: invalid schema")
    require(obj, "report_id", path.name)
    require(obj, "methodology_version", path.name)
    if "platforms" in obj:
        for p in obj["platforms"]:
            for k in ("id", "name", "score", "band", "evidence_level"):
                require(p, k, f"{path.name} platform {p.get('id', '?')}")
            if not (0 <= p["score"] <= 10):
                raise ValueError(f"{path.name}: score out of range for {p['id']}")
    print(f"OK {path.relative_to(ROOT)}")


def validate_checklist(path: Path) -> None:
    obj = load(path)
    require(obj, "schema", path.name)
    if obj["schema"] != "multilogin-labs/checklist/v1":
        raise ValueError(f"{path.name}: invalid schema")
    require(obj, "items", path.name)
    total = sum(i.get("weight", 0) for i in obj["items"])
    if total != 100:
        raise ValueError(f"{path.name}: item weights must sum to 100 (got {total})")
    print(f"OK {path.relative_to(ROOT)}")


def validate_index(path: Path) -> None:
    obj = load(path)
    require(obj, "datasets", path.name)
    require(obj, "base_url", path.name)
    if not isinstance(obj["datasets"], list) or not obj["datasets"]:
        raise ValueError(f"{path.name}: datasets must be non-empty list")
    print(f"OK {path.relative_to(ROOT)}")


def main() -> int:
    errors = 0
    for path in sorted(DATA.glob("*.json")):
        try:
            if path.name == "affiliate.json":
                print(f"OK {path.relative_to(ROOT)}")
            elif path.name == "index.json":
                validate_index(path)
            elif "checklist" in path.name:
                validate_checklist(path)
            else:
                validate_benchmark(path)
        except (ValueError, json.JSONDecodeError) as exc:
            print(f"FAIL {path.name}: {exc}", file=sys.stderr)
            errors += 1
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
