#!/usr/bin/env python3
"""Query Cloudflare D1 and write leaderboard.json."""

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone

ACCOUNT_ID  = "27f81d43eb028aafd002283332cff05a"
DATABASE_ID = "f4edf4d1-c57b-449c-9dcc-bc1a418824da"
API_BASE    = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/d1/database/{DATABASE_ID}"

TOKEN = os.environ.get("CF_API_TOKEN", "")
if not TOKEN:
    print("CF_API_TOKEN not set", file=sys.stderr)
    sys.exit(1)


def d1_query(sql: str) -> list[dict]:
    url  = f"{API_BASE}/query"
    body = json.dumps({"sql": sql}).encode()
    req  = urllib.request.Request(
        url, data=body, method="POST",
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as e:
        print(f"D1 HTTP error {e.code}: {e.read().decode()}", file=sys.stderr)
        sys.exit(1)

    if not data.get("success"):
        print(f"D1 error: {data}", file=sys.stderr)
        sys.exit(1)

    return data["result"][0].get("results", [])


def main() -> None:
    # ── closed mode: best result per (gpu_chip, profile, model_name) ──────────
    closed_entries = d1_query("""
        SELECT
            gpu_name,
            gpu_chip,
            gpu_vendor,
            vram_gb,
            profile,
            model_name,
            runtime,
            MAX(tokens_per_second) AS tokens_per_second,
            COUNT(*)               AS submission_count,
            MAX(submitted_at)      AS last_submitted_at
        FROM submissions
        WHERE tokens_per_second IS NOT NULL
          AND throttling_detected = 0
          AND mode = 'closed'
        GROUP BY gpu_chip, profile, model_name
        ORDER BY tokens_per_second DESC
        LIMIT 500
    """)

    # ── open mode: best result per (gpu_chip, model_name, profile) ────────────
    open_entries = d1_query("""
        SELECT
            gpu_name,
            gpu_chip,
            gpu_vendor,
            vram_gb,
            profile,
            model_name,
            runtime,
            MAX(tokens_per_second) AS tokens_per_second,
            COUNT(*)               AS submission_count,
            MAX(submitted_at)      AS last_submitted_at
        FROM submissions
        WHERE tokens_per_second IS NOT NULL
          AND throttling_detected = 0
          AND mode = 'open'
        GROUP BY gpu_chip, model_name, profile
        ORDER BY model_name ASC, tokens_per_second DESC
        LIMIT 1000
    """)

    totals = d1_query("SELECT COUNT(*) AS n FROM submissions")
    total  = totals[0]["n"] if totals else 0

    out = {
        "updated_at":        datetime.now(timezone.utc).isoformat(),
        "total_submissions": total,
        "closed_entries":    closed_entries,
        "open_entries":      open_entries,
    }

    with open("leaderboard.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
        f.write("\n")

    print(
        f"Written {len(closed_entries)} closed + {len(open_entries)} open entries, "
        f"{total} total submissions."
    )


if __name__ == "__main__":
    main()
