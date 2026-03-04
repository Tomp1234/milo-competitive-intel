import time
from typing import List
from urllib.parse import quote

import requests

from config import (
    APIFY_ACTOR_ID,
    APIFY_BASE_URL,
    DAILY_APIFY_LIMIT,
    can_use_apify,
    get_daily_usage,
    increment_daily_usage,
    DailyLimitExceeded,
)
from models import Prospect


def _parse_headline(headline):
    """
    Best-effort split of a LinkedIn headline into (title, company).
    Examples:
      "COO at Coolr | Helping brands grow" → ("COO", "Coolr")
      "Acme Corp - Chief Operating Officer" → ("Chief Operating Officer", "Acme Corp")
      "Operations Leader" → ("Operations Leader", "")

    Falls back to (full headline, "") if no pattern matches.
    """
    if not headline:
        return ("", "")

    # Try "Title at Company" (most common)
    if " at " in headline:
        parts = headline.split(" at ", 1)
        title = parts[0].strip()
        company = parts[1].split("|")[0].split("·")[0].strip()
        return (title, company)

    # Try "Company - Title" pattern
    if " - " in headline:
        parts = headline.split(" - ", 1)
        # Heuristic: if first part looks like a company (shorter, no common title words)
        # this is imperfect but better than nothing
        return (parts[1].strip(), parts[0].strip())

    # Try pipe separator — take first segment as title
    if " | " in headline:
        title = headline.split(" | ")[0].strip()
        return (title, "")

    return (headline.strip(), "")


def _normalize_engager(raw, source_label="apify"):
    """Convert a raw Apify engager dict to a Prospect object."""
    name = raw.get("name", "") or raw.get("fullName", "") or ""
    headline = raw.get("headline", "") or raw.get("title", "") or ""
    profile_url = raw.get("profileUrl", "") or raw.get("url", "") or raw.get("profileLink", "") or None

    if not name:
        return None

    parts = name.strip().split(" ", 1)
    first = parts[0] if parts else ""
    last = parts[1] if len(parts) > 1 else ""

    title, company = _parse_headline(headline)

    return Prospect(
        first_name=first,
        last_name=last,
        full_name=name.strip(),
        title=title,
        company=company,
        headline=headline,
        linkedin_url=profile_url,
        source=source_label,
    )


def scrape_post_engagers(post_url, api_key, max_results=80):
    """
    Scrape engagers (likers/commenters) from a LinkedIn post via Apify.
    Returns list of Prospect objects.
    """
    current_usage = get_daily_usage()
    available = DAILY_APIFY_LIMIT - current_usage
    print(f"  [Apify] Daily usage: {current_usage}/{DAILY_APIFY_LIMIT} ({available} remaining)")

    if available <= 0:
        raise DailyLimitExceeded(
            f"Daily Apify limit reached ({current_usage}/{DAILY_APIFY_LIMIT}). Try again tomorrow."
        )

    fetch_count = min(max_results, available)

    actor_id_encoded = quote(APIFY_ACTOR_ID, safe="")
    url = f"{APIFY_BASE_URL}/acts/{actor_id_encoded}/run-sync-get-dataset-items"

    params = {"token": api_key}
    payload = {
        "url": post_url,
        "type": "likes",
        "count": fetch_count,
    }

    print(f"  [Apify] Scraping up to {fetch_count} engagers from post...")
    print(f"  [Apify] This may take 30-60 seconds...")

    try:
        resp = requests.post(url, json=payload, params=params, timeout=300)
        resp.raise_for_status()
    except requests.exceptions.Timeout:
        print("  [!] Apify request timed out (5 min). Post may have too many engagers.")
        print("  [!] Try a post with fewer reactions.")
        return []
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response is not None else "?"
        if status == 402:
            print("  [!] Apify credits exhausted. Top up at https://console.apify.com/billing")
        elif status == 400:
            body = e.response.text[:500] if e.response is not None else ""
            print(f"  [!] Apify rejected the input. The actor may expect different field names.")
            print(f"  [!] Response: {body}")
            print(f"  [!] Check: https://apify.com/{APIFY_ACTOR_ID}")
        else:
            print(f"  [!] Apify error (HTTP {status}): {e}")
        return []

    raw_results = resp.json() if isinstance(resp.json(), list) else []
    print(f"  [Apify] Got {len(raw_results)} raw engagers")

    if not raw_results:
        print("  [Apify] No engagers found. The post may be private, too new, or have no engagement.")
        return []

    # Track daily usage
    try:
        increment_daily_usage(len(raw_results))
    except DailyLimitExceeded as e:
        print(f"  [!] {e}")

    # Normalize to Prospect objects
    prospects = []
    skipped = 0
    for raw in raw_results:
        prospect = _normalize_engager(raw)
        if prospect:
            prospects.append(prospect)
        else:
            skipped += 1

    print(f"  [Apify] Parsed {len(prospects)} prospects ({skipped} had no usable data)")
    return prospects
