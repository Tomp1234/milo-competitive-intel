import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

from dotenv import load_dotenv

# --- Paths ---
BASE_DIR = Path(__file__).parent
ENV_PATH = BASE_DIR / ".env"
LIMITS_PATH = BASE_DIR / "daily_limits.json"

# --- API constants ---
APIFY_ACTOR_ID = "scraping_solutions/linkedin-posts-engagers-likers-and-commenters-no-cookies"
APIFY_BASE_URL = "https://api.apify.com/v2"
APOLLO_BASE_URL = "https://api.apollo.io/api/v1"
CLAUDE_MODEL = "claude-sonnet-4-20250514"

# --- Daily limits ---
DAILY_APIFY_LIMIT = 80
DAILY_APIFY_WARNING = 60

# --- ICP constants ---
TARGET_TITLES = [
    "COO",
    "Chief Operating Officer",
    "VP Operations",
    "Director of Operations",
    "Operations Director",
    "Head of Innovation",
    "Innovation Director",
    "VP Innovation",
    "Commercial Director",
    "Head of Sales",
    "VP Sales",
]

EXCLUDE_TITLE_KEYWORDS = [
    "AI",
    "Data",
    "BI",
    "Business Intelligence",
    "Analytics",
    "Insights",
    "Engineering",
    "CTO",
    "Data Science",
]

TARGET_VERTICALS = [
    "eCommerce",
    "DTC",
    "SaaS",
    "Agency",
    "Logistics",
    "AdTech",
    "Event Ticketing",
]

EMPLOYEE_RANGE = "101,500"

# --- UK timezone ---
UK_TZ = timezone(timedelta(hours=0))  # UTC approximation for midnight reset


class DailyLimitExceeded(Exception):
    pass


def load_config():
    """Load .env and validate all required API keys are present."""
    load_dotenv(ENV_PATH)

    required_keys = ["APIFY_API_KEY", "ANTHROPIC_API_KEY", "APOLLO_API_KEY"]
    config = {}
    missing = []

    for key in required_keys:
        val = os.getenv(key, "").strip()
        if not val:
            missing.append(key)
        config[key] = val

    if missing:
        print(f"\n  Missing API keys in {ENV_PATH}:")
        for k in missing:
            print(f"    - {k}")
        print()
        sys.exit(1)

    return config


def _today_uk():
    """Return today's date string in UK timezone (ISO format)."""
    return datetime.now(UK_TZ).strftime("%Y-%m-%d")


def _read_limits():
    """Read daily_limits.json, return dict. Create if missing/corrupt."""
    if not LIMITS_PATH.exists():
        return {}
    try:
        with open(LIMITS_PATH, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def _write_limits(data):
    """Write daily_limits.json."""
    with open(LIMITS_PATH, "w") as f:
        json.dump(data, f, indent=2)


def get_daily_usage():
    """Return today's Apify usage count."""
    limits = _read_limits()
    return limits.get(_today_uk(), 0)


def increment_daily_usage(count):
    """Add count to today's usage. Warn at 60, raise at 80. Returns new total."""
    limits = _read_limits()
    today = _today_uk()
    current = limits.get(today, 0)
    new_total = current + count

    if new_total > DAILY_APIFY_LIMIT:
        raise DailyLimitExceeded(
            f"Daily Apify limit would be exceeded: {new_total}/{DAILY_APIFY_LIMIT}. "
            f"Try again tomorrow."
        )

    limits[today] = new_total
    _write_limits(limits)

    if new_total >= DAILY_APIFY_WARNING:
        print(f"  [!] Apify daily usage: {new_total}/{DAILY_APIFY_LIMIT} — approaching limit")

    return new_total


def can_use_apify(needed):
    """Check if we can use `needed` more Apify lookups today."""
    current = get_daily_usage()
    return (current + needed) <= DAILY_APIFY_LIMIT
