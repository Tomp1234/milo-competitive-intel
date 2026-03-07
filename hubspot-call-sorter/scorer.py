#!/usr/bin/env python3
"""
HubSpot call-back scorer for Milo GTM pipeline.
Reads from data/hubspot_cache.json (produced by fetcher.py), scores contacts,
assigns tiers, and optionally creates call tasks in HubSpot.

Default mode is dry run. Pass --create-tasks to create tasks in HubSpot.
"""

import argparse
import json
import os
import time
from collections import Counter
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
CACHE_FILE = os.path.join(DATA_DIR, "hubspot_cache.json")
OUTPUT_FILE = os.path.join(DATA_DIR, "last_run.json")

BASE_URL = "https://api.hubapi.com"
OWNER_ID = "30769884"
MAX_TASKS = 40
MAX_RETRIES = 5

# ── ICP title scoring ────────────────────────────────────────────────────────

TITLE_SCORE_5 = [
    "head of innovation", "innovation director", "vp innovation",
    "coo", "chief operating officer",
]
TITLE_SCORE_4 = [
    "vp operations", "director of operations", "operations director",
    "commercial director",
]
TITLE_SCORE_3 = ["head of sales", "vp sales"]
TITLE_SCORE_3_CONTAINS = ["director"]
TITLE_SCORE_2 = ["ceo"]
TITLE_EXCLUDE_KEYWORDS = [
    "ai", "data", "bi", "business intelligence", "analytics",
    "insights", "engineering", "cto",
]

# Short keywords (<=3 chars) must match as whole words to avoid false positives
SHORT_KEYWORDS = {"ai", "bi", "cto"}


def score_title(title):
    """Return ICP score for a job title. -10 = hard exclude, 0 = no match."""
    if not title:
        return 0
    t = title.lower().strip()
    words = t.split()

    # Check exclusions first
    for kw in TITLE_EXCLUDE_KEYWORDS:
        if kw in SHORT_KEYWORDS:
            if kw in words:
                return -10
        else:
            if kw in t:
                return -10

    for phrase in TITLE_SCORE_5:
        if phrase in t:
            return 5
    for phrase in TITLE_SCORE_4:
        if phrase in t:
            return 4
    for phrase in TITLE_SCORE_3:
        if phrase in t:
            return 3
    # "Director" as a standalone or prefix (but not already matched as score 4)
    for phrase in TITLE_SCORE_3_CONTAINS:
        if phrase in t:
            return 3
    for phrase in TITLE_SCORE_2:
        if phrase in t:
            return 2
    return 0


# ── Skip dispositions ────────────────────────────────────────────────────────
# These are the disposition names as stored by fetcher.py (snake_case)

TERMINAL_DISPOSITIONS = {
    "connected_not_interested",
    "refused_call",
    "wrong_number",
    "retired",
    "left_company",
}

# Signals that indicate warm engagement (for P1)
WARM_SIGNALS = {"call_back", "left_live_message"}

# Signals that indicate never reached (for P2/P3)
COLD_SIGNALS = {"no_answer", "left_voicemail"}


# ── Helpers ───────────────────────────────────────────────────────────────────

def parse_ts(ts_str):
    """Parse an ISO timestamp string to a timezone-aware datetime."""
    if not ts_str:
        return None
    try:
        return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
    except ValueError:
        return None


def days_since(ts_str, now):
    """Return whole days between a timestamp string and now."""
    dt = parse_ts(ts_str)
    if dt is None:
        return 999
    return (now - dt).days


def date_only(ts_str):
    """Extract YYYY-MM-DD from a timestamp string."""
    if not ts_str:
        return None
    return ts_str[:10] if len(ts_str) >= 10 else ts_str


# ── Core scoring ──────────────────────────────────────────────────────────────

def process_contact(contact, now):
    """Score and tier a single contact. Returns a result dict."""
    cid = contact["contact_id"]
    firstname = contact.get("firstname", "")
    lastname = contact.get("lastname", "")
    jobtitle = contact.get("jobtitle", "")
    company = contact.get("company", "")
    phone = contact.get("phone", "")
    summary = contact.get("call_summary", {})
    open_tasks = contact.get("open_call_tasks", [])

    total_calls = summary.get("total_calls", 0)
    ever_meeting_booked = summary.get("ever_meeting_booked", False)
    best_signal = summary.get("best_signal")
    best_signal_date = summary.get("best_signal_date")
    last_disposition = summary.get("last_disposition")
    last_call_date = summary.get("last_call_date")

    icp_score = score_title(jobtitle)
    gap = days_since(last_call_date, now)

    result = {
        "contact_id": cid,
        "name": f"{firstname} {lastname}".strip(),
        "company": company,
        "jobtitle": jobtitle,
        "phone": phone,
        "icp_score": icp_score,
        "tier": None,
        "priority": None,
        "best_signal": best_signal,
        "best_signal_date": date_only(best_signal_date),
        "last_disposition": last_disposition,
        "last_call_date": date_only(last_call_date),
        "days_since_last_call": gap if gap != 999 else None,
        "total_calls": total_calls,
        "task_created": False,
        "skip_reason": None,
    }

    # ── Skip checks (order matters for skip reason reporting) ──

    if total_calls == 0 and icp_score < 4:
        result["skip_reason"] = "No call history (low ICP)"
        return result

    if ever_meeting_booked:
        result["skip_reason"] = "Meeting already booked"
        return result

    if last_disposition in TERMINAL_DISPOSITIONS:
        result["skip_reason"] = f"Terminal disposition: {last_disposition}"
        return result

    if icp_score == -10:
        result["skip_reason"] = f"Excluded title: {jobtitle}"
        return result

    if open_tasks:
        result["skip_reason"] = "Has open call tasks"
        return result

    if gap < 7:
        result["skip_reason"] = "Called within last 7 days"
        return result

    # ── Tier assignment (highest qualifying tier wins) ──

    # P1: Warm reactivation — had call_back or left_live_message, 14+ days ago
    if best_signal in WARM_SIGNALS and gap >= 14:
        result["tier"] = 1
        result["priority"] = "HIGH"
        return result

    # P2: High ICP never reached — score >= 4, only no_answer/left_voicemail, 7+ days
    if icp_score >= 4 and best_signal in COLD_SIGNALS and gap >= 7:
        result["tier"] = 2
        result["priority"] = "MEDIUM"
        return result

    # P3: Lower ICP never reached — score 2-3, only no_answer/left_voicemail, 14+ days
    if 2 <= icp_score <= 3 and best_signal in COLD_SIGNALS and gap >= 14:
        result["tier"] = 3
        result["priority"] = "MEDIUM"
        return result

    # P4: High ICP never called — score >= 4, zero call history
    if icp_score >= 4 and total_calls == 0:
        result["tier"] = 4
        result["priority"] = "MEDIUM"
        return result

    result["skip_reason"] = "No tier qualified"
    return result


# ── HubSpot task creation ────────────────────────────────────────────────────

def create_hubspot_task(api_key, task, now):
    """Create a call task in HubSpot and associate it to the contact."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    subject = f"Call back - {task['name']} ({task['company']})"
    due_date = now.strftime("%Y-%m-%dT%H:%M:%S.000Z")

    body = {
        "properties": {
            "hs_task_subject": subject,
            "hs_task_type": "CALL",
            "hs_task_status": "NOT_STARTED",
            "hs_task_priority": task["priority"],
            "hubspot_owner_id": OWNER_ID,
            "hs_timestamp": due_date,
        },
        "associations": [
            {
                "to": {"id": task["contact_id"]},
                "types": [
                    {
                        "associationCategory": "HUBSPOT_DEFINED",
                        "associationTypeId": 204,
                    }
                ],
            }
        ],
    }

    for attempt in range(MAX_RETRIES):
        resp = requests.post(
            f"{BASE_URL}/crm/v3/objects/tasks",
            headers=headers,
            json=body,
        )
        if resp.status_code == 429:
            wait = 2 ** attempt
            print(f"    Rate limited, waiting {wait}s...")
            time.sleep(wait)
            continue
        resp.raise_for_status()
        return resp.json()

    raise RuntimeError(f"Failed to create task after {MAX_RETRIES} retries for {task['name']}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Score contacts and create HubSpot call tasks")
    parser.add_argument("--create-tasks", action="store_true",
                        help="Create tasks in HubSpot (default is dry run)")
    args = parser.parse_args()

    dry_run = not args.create_tasks

    # Load cache
    if not os.path.exists(CACHE_FILE):
        raise SystemExit(f"Cache file not found: {CACHE_FILE}\nRun fetcher.py first.")

    with open(CACHE_FILE) as f:
        cache = json.load(f)

    contacts = cache.get("contacts", [])
    now = datetime.now(timezone.utc)

    print("=" * 60)
    print("Milo Call-Back Scorer")
    print(f"Mode: {'DRY RUN — no tasks created' if dry_run else 'LIVE — creating tasks'}")
    print(f"Cache: {len(contacts):,} contacts (fetched {cache.get('fetched_at', '?')})")
    print("=" * 60)
    print()

    # Validate API key early if creating tasks
    api_key = None
    if not dry_run:
        api_key = os.environ.get("HUBSPOT_API_KEY")
        if not api_key:
            raise SystemExit("HUBSPOT_API_KEY environment variable not set")

    # Score all contacts
    print("Scoring contacts...", end=" ", flush=True)
    results = [process_contact(c, now) for c in contacts]
    print("done")
    print()

    skipped = [r for r in results if r["skip_reason"]]
    eligible = [r for r in results if r["tier"] is not None]

    # Sort eligible: by tier ascending, then by days_since_last_call descending (longest wait first)
    eligible.sort(key=lambda r: (r["tier"], -(r["days_since_last_call"] or 0)))

    # Cap at MAX_TASKS
    to_action = eligible[:MAX_TASKS]
    overflow = len(eligible) - len(to_action)

    # Tier counts (for actioned tasks)
    tier_counts = Counter(r["tier"] for r in to_action)

    # ── Terminal summary ──

    print(f"Contacts processed:   {len(results):,}")
    print(f"Contacts skipped:     {len(skipped):,}")
    print(f"Contacts eligible:    {len(eligible):,}")
    print(f"Tasks to create:      {len(to_action):,}")
    print()
    print(f"  Priority 1 (warm reactivation):      {tier_counts.get(1, 0)}")
    print(f"  Priority 2 (high ICP, not reached):  {tier_counts.get(2, 0)}")
    print(f"  Priority 3 (lower ICP, not reached): {tier_counts.get(3, 0)}")
    print(f"  Priority 4 (high ICP, never called): {tier_counts.get(4, 0)}")
    print()

    # Top 5 skip reasons
    skip_reasons = Counter(r["skip_reason"] for r in skipped)
    print("Top skip reasons:")
    for reason, count in skip_reasons.most_common(5):
        print(f"  {count:>5}  {reason}")
    print()

    if overflow > 0:
        print(f"  ** {overflow} contacts were eligible but not actioned due to {MAX_TASKS}-task cap **")
        print()

    # Print task list
    if to_action:
        print("-" * 90)
        print(f"{'Tier':<5} {'Name':<25} {'Company':<20} {'Title':<20} {'Days':<6} {'Signal'}")
        print("-" * 90)
        for r in to_action:
            name = r["name"][:24]
            comp = (r["company"] or "")[:19]
            title = (r["jobtitle"] or "")[:19]
            days = r["days_since_last_call"] or "?"
            sig = r["best_signal"] or "-"
            print(f"P{r['tier']:<4} {name:<25} {comp:<20} {title:<20} {days:<6} {sig}")
        print("-" * 90)
        print()

    # ── Task creation ──

    if not dry_run and to_action:
        print(f"Creating {len(to_action)} tasks in HubSpot...")
        created = 0
        for i, r in enumerate(to_action, 1):
            try:
                create_hubspot_task(api_key, r, now)
                r["task_created"] = True
                created += 1
                print(f"  [{i}/{len(to_action)}] {r['name']} — done")
            except Exception as e:
                print(f"  [{i}/{len(to_action)}] {r['name']} — FAILED: {e}")
            time.sleep(0.05)
        print()
        print(f"Tasks created: {created}/{len(to_action)}")
    elif dry_run:
        print("Dry run — no tasks created. Use --create-tasks to go live.")

    # ── Write output JSON ──

    output = {
        "run_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "dry_run": dry_run,
        "summary": {
            "contacts_processed": len(results),
            "contacts_skipped": len(skipped),
            "contacts_eligible": len(eligible),
            "tasks_created": len(to_action),
            "by_tier": {
                "priority_1": tier_counts.get(1, 0),
                "priority_2": tier_counts.get(2, 0),
                "priority_3": tier_counts.get(3, 0),
                "priority_4": tier_counts.get(4, 0),
            },
        },
        "tasks": to_action,
    }

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print()
    print(f"Output written to: {OUTPUT_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()
