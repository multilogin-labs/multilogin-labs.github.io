#!/usr/bin/env bash
# Quick env check before MLX API scripts — see profile-start-template.py
set -euo pipefail
required=(MLX_API_TOKEN MLX_PROFILE_ID MLX_FOLDER_ID)
missing=0
for v in "${required[@]}"; do
  if [[ -z "${!v:-}" ]]; then
    echo "MISSING: $v" >&2
    missing=1
  else
    echo "OK: $v is set"
  fi
done
exit "$missing"
