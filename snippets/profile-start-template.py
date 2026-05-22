#!/usr/bin/env python3
"""
Template: start a Multilogin profile via local API (adjust host/port/token).
See guides/mlx-api-integration-map/ for rollout gates before production scale.
"""

import os
import requests

API_BASE = os.environ.get("MLX_API_BASE", "https://api.multilogin.com")
TOKEN = os.environ.get("MLX_API_TOKEN", "")

def start_profile(profile_id: str, folder_id: str) -> dict:
    if not TOKEN:
        raise SystemExit("Set MLX_API_TOKEN")
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    payload = {"profile_id": profile_id, "folder_id": folder_id}
    # Endpoint path varies by MLX API version — confirm in official docs.
    url = f"{API_BASE}/v1/profile/start"
    resp = requests.post(url, json=payload, headers=headers, timeout=60)
    resp.raise_for_status()
    return resp.json()

if __name__ == "__main__":
    print(start_profile(os.environ["MLX_PROFILE_ID"], os.environ["MLX_FOLDER_ID"]))
