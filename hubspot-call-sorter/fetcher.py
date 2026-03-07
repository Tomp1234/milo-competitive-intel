#!/usr/bin/env python3
"""
HubSpot data fetcher for Milo GTM pipeline.
Pulls contacts (Tom's, UK +44 only), calls, and tasks into a local JSON cache.
Computes call_summary per contact for fast downstream scoring.
"""

import argparse
import json
import os
import random
import time
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("HUBSPOT_API_KEY")
if not API_KEY:
    raise SystemExit("HUBSPOT_API_KEY environment variable not set")

BASE_URL = "https://api.hubapi.com"
OWNER_ID = "30769884"
CALLS_CUTOFF = "2025-10-01T00:00:00Z"
BATCH_SIZE = 100
BATCH_DELAY = 0.1
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
CACHE_FILE = os.path.join(DATA_DIR, "hubspot_cache.json")
MAX_RETRIES = 5

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

# ── Disposition mapping ──────────────────────────────────────────────────────

DISPOSITION_MAP = {
    "f240bbac-87c9-4f6e-bf70-924b57d47db7": "connected",
    "6a417e0b-31b7-4e24-833c-70fe6e20bd1d": "call_back",
    "a4c4c377-d246-4b32-a13b-75a56a4cd0ff": "left_live_message",
    "b2cf5968-551e-4856-9783-52b3da59a7d0": "left_voicemail",
    "73a0d17f-1163-4015-bdd5-ec830791da20": "no_answer",
    "244de1e7-909d-4963-a0f7-fbf440829375": "connected_not_interested",
    "524da1e5-424a-4acf-8912-f08deb998d7b": "meeting_booked",
    "ec424166-56ef-427a-914f-f5387b150b47": "hung_up",
    "1da01b20-748b-4fe6-8c45-7e0574c43168": "refused_call",
    "17b47fee-58de-441e-a44c-c6300d46f273": "wrong_number",
    "0996a28c-f40b-45d6-8cf1-69dc6d99e36f": "retired",
    "61bf8804-55ff-435a-a913-154837448940": "left_company",
}

# These dispositions are treated as if the call never happened
IGNORED_DISPOSITIONS = {"connected", "hung_up"}

MEETING_BOOKED_UUID = "524da1e5-424a-4acf-8912-f08deb998d7b"

# Signal hierarchy — higher number = better signal
SIGNAL_RANK = {
    "call_back": 4,
    "left_live_message": 3,
    "no_answer": 2,
    "left_voicemail": 1,
}


# ── API helpers ──────────────────────────────────────────────────────────────

def api_request(method, url, **kwargs):
    """Make an API request with retry on 429."""
    for attempt in range(MAX_RETRIES):
        resp = requests.request(method, url, headers=HEADERS, **kwargs)
        if resp.status_code == 429:
            wait = 2 ** attempt
            print(f"  Rate limited, waiting {wait}s...")
            time.sleep(wait)
            continue
        if resp.status_code >= 400:
            print(f"\n  API ERROR: {method} {url}")
            print(f"  Status: {resp.status_code}")
            print(f"  Response: {resp.text[:500]}")
            resp.raise_for_status()
        return resp.json()
    raise SystemExit(f"Failed after {MAX_RETRIES} retries: {url}")


# ── Fetch contacts ───────────────────────────────────────────────────────────

def fetch_contacts():
    """Fetch all contacts owned by Tom that have a phone number."""
    print("Fetching contacts...", end=" ", flush=True)
    contacts = []
    after_value = None
    properties = [
        "firstname", "lastname", "jobtitle", "company",
        "phone", "hubspot_owner_id",
    ]

    while True:
        body = {
            "filterGroups": [
                {
                    "filters": [
                        {
                            "propertyName": "hubspot_owner_id",
                            "operator": "EQ",
                            "value": OWNER_ID,
                        },
                        {
                            "propertyName": "phone",
                            "operator": "HAS_PROPERTY",
                        },
                    ]
                }
            ],
            "properties": properties,
            "limit": 100,
        }
        if after_value is not None:
            body["after"] = after_value

        data = api_request("POST", f"{BASE_URL}/crm/v3/objects/contacts/search", json=body)
        results = data.get("results", [])
        contacts.extend(results)

        paging = data.get("paging")
        if paging and paging.get("next"):
            after_value = paging["next"]["after"]
        else:
            break

    total_before_filter = len(contacts)
    print(f"{total_before_filter:,} found", flush=True)

    # Filter to UK +44 numbers only
    uk_contacts = []
    for c in contacts:
        phone = (c.get("properties", {}).get("phone") or "").strip()
        if phone.startswith("+44"):
            uk_contacts.append(c)

    print(f"  Filtered to +44 (UK): {len(uk_contacts):,} contacts")
    return uk_contacts, total_before_filter


# ── Batch association fetching ───────────────────────────────────────────────

def batch_fetch_associations(object_ids, from_type, to_type, label):
    """Fetch associations in batches of 100 using Associations v4 batch API."""
    batches = [object_ids[i:i + BATCH_SIZE] for i in range(0, len(object_ids), BATCH_SIZE)]
    total_batches = len(batches)
    all_associations = {}

    for idx, batch in enumerate(batches, 1):
        print(f"  Fetching {label} associations batch {idx}/{total_batches}...", end=" ", flush=True)

        body = {
            "inputs": [{"id": oid} for oid in batch],
        }

        data = api_request(
            "POST",
            f"{BASE_URL}/crm/v4/associations/{from_type}/{to_type}/batch/read",
            json=body,
        )

        batch_found = 0
        for result in data.get("results", []):
            from_id = str(result["from"]["id"])
            to_ids = [str(assoc["toObjectId"]) for assoc in result.get("to", [])]
            if to_ids:
                batch_found += len(to_ids)
            all_associations[from_id] = to_ids

        print(f"done ({batch_found} found)", flush=True)
        if idx < total_batches:
            time.sleep(BATCH_DELAY)

    total_found = sum(len(ids) for ids in all_associations.values())
    print(f"  Total {label} associations: {total_found:,}")
    return all_associations


# ── Batch object fetching ────────────────────────────────────────────────────

def batch_fetch_objects(object_ids, object_type, properties, label):
    """Fetch object details in batches of 100 using batch read API."""
    if not object_ids:
        print(f"  Fetching {label}... none to fetch")
        return {}

    batches = [object_ids[i:i + BATCH_SIZE] for i in range(0, len(object_ids), BATCH_SIZE)]
    total_batches = len(batches)
    all_objects = {}

    for idx, batch in enumerate(batches, 1):
        print(f"  Fetching {label} batch {idx}/{total_batches}...", end=" ", flush=True)

        body = {
            "inputs": [{"id": oid} for oid in batch],
            "properties": properties,
        }

        data = api_request(
            "POST",
            f"{BASE_URL}/crm/v3/objects/{object_type}/batch/read",
            json=body,
        )

        for result in data.get("results", []):
            all_objects[result["id"]] = result.get("properties", {})

        print("done", flush=True)
        if idx < total_batches:
            time.sleep(BATCH_DELAY)

    return all_objects


# ── Call summary computation ─────────────────────────────────────────────────

def compute_call_summary(calls):
    """
    Compute call_summary from a list of call dicts.
    Each call dict has: disposition_uuid, timestamp, disposition_name.
    Calls with ignored dispositions (connected, hung_up) are excluded.
    """
    if not calls:
        return {
            "total_calls": 0,
            "ever_meeting_booked": False,
            "best_signal": None,
            "best_signal_date": None,
            "last_disposition": None,
            "last_call_date": None,
            "all_dispositions": [],
        }

    # Filter out ignored dispositions
    valid_calls = [c for c in calls if c["disposition_name"] not in IGNORED_DISPOSITIONS]

    if not valid_calls:
        return {
            "total_calls": 0,
            "ever_meeting_booked": False,
            "best_signal": None,
            "best_signal_date": None,
            "last_disposition": None,
            "last_call_date": None,
            "all_dispositions": [],
        }

    # Sort chronologically by timestamp
    valid_calls.sort(key=lambda c: c["timestamp"] or "")

    total_calls = len(valid_calls)
    ever_meeting_booked = any(c["disposition_uuid"] == MEETING_BOOKED_UUID for c in valid_calls)

    # Best signal
    best_signal = None
    best_signal_date = None
    best_rank = 0
    for c in valid_calls:
        rank = SIGNAL_RANK.get(c["disposition_name"], 0)
        if rank > best_rank:
            best_rank = rank
            best_signal = c["disposition_name"]
            best_signal_date = c["timestamp"]

    # Last call
    last_call = valid_calls[-1]
    last_disposition = last_call["disposition_name"]
    last_call_date = last_call["timestamp"]

    # All dispositions in chronological order
    all_dispositions = [c["disposition_name"] for c in valid_calls]

    return {
        "total_calls": total_calls,
        "ever_meeting_booked": ever_meeting_booked,
        "best_signal": best_signal,
        "best_signal_date": best_signal_date,
        "last_disposition": last_disposition,
        "last_call_date": last_call_date,
        "all_dispositions": all_dispositions,
    }


# ── Diagnose ─────────────────────────────────────────────────────────────────

def diagnose_cache():
    """Sample 20 contacts from the cache and compare call counts against live HubSpot."""
    if not os.path.exists(CACHE_FILE):
        raise SystemExit(f"Cache file not found: {CACHE_FILE}\nRun fetcher.py first.")

    with open(CACHE_FILE) as f:
        cache = json.load(f)

    contacts = cache.get("contacts", [])
    if not contacts:
        raise SystemExit("Cache has zero contacts.")

    # Sample 20: mix of contacts with and without calls
    with_calls = [c for c in contacts if c["call_summary"]["total_calls"] > 0]
    without_calls = [c for c in contacts if c["call_summary"]["total_calls"] == 0]

    sample = []
    if with_calls:
        sample.extend(random.sample(with_calls, min(10, len(with_calls))))
    if without_calls:
        sample.extend(random.sample(without_calls, min(10, len(without_calls))))

    n_with = min(10, len(with_calls))
    n_without = min(10, len(without_calls))

    print("=" * 70)
    print("DIAGNOSE MODE — Comparing cache vs live HubSpot")
    print(f"Sampling {len(sample)} contacts ({n_with} with calls, {n_without} without)")
    print("=" * 70)
    print()

    cutoff_dt = datetime.fromisoformat(CALLS_CUTOFF.replace("Z", "+00:00"))
    mismatches = 0
    matches = 0

    for c in sample:
        cid = c["contact_id"]
        name = f"{c.get('firstname', '')} {c.get('lastname', '')}".strip() or "(no name)"
        cache_count = c["call_summary"]["total_calls"]

        # Get call associations from live HubSpot
        try:
            data = api_request(
                "POST",
                f"{BASE_URL}/crm/v4/associations/contacts/calls/batch/read",
                json={"inputs": [{"id": cid}]},
            )
        except Exception as e:
            print(f"  {name} (ID {cid}): API ERROR — {e}")
            continue

        live_call_ids = []
        for result in data.get("results", []):
            live_call_ids = [str(a["toObjectId"]) for a in result.get("to", [])]

        # Fetch call details and count valid outbound calls
        live_valid_count = 0
        if live_call_ids:
            call_data = api_request(
                "POST",
                f"{BASE_URL}/crm/v3/objects/calls/batch/read",
                json={
                    "inputs": [{"id": cid} for cid in live_call_ids],
                    "properties": ["hs_call_direction", "hs_timestamp", "hs_call_disposition"],
                },
            )
            for r in call_data.get("results", []):
                props = r.get("properties", {})
                if props.get("hs_call_direction") != "OUTBOUND":
                    continue
                ts = props.get("hs_timestamp", "")
                if ts:
                    try:
                        call_dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                        if call_dt < cutoff_dt:
                            continue
                    except ValueError:
                        continue
                # Check disposition — skip ignored
                disp_uuid = props.get("hs_call_disposition", "")
                disp_name = DISPOSITION_MAP.get(disp_uuid, disp_uuid)
                if disp_name in IGNORED_DISPOSITIONS:
                    continue
                live_valid_count += 1

        match = "OK" if cache_count == live_valid_count else "MISMATCH"
        if cache_count != live_valid_count:
            mismatches += 1
        else:
            matches += 1

        print(f"  {match:<10} {name:<30} cache={cache_count:<4} live={live_valid_count:<4} (total assocs: {len(live_call_ids)})")
        time.sleep(0.1)

    print()
    print("-" * 70)
    print(f"Matches: {matches}/{len(sample)}   Mismatches: {mismatches}/{len(sample)}")
    if mismatches == 0:
        print("Cache is consistent with live HubSpot.")
    else:
        print("WARNING: Cache is out of sync with live HubSpot.")
        print("Re-run fetcher.py (without --diagnose) to refresh the cache.")
    print("-" * 70)


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Fetch HubSpot contacts, calls, and tasks into local cache")
    parser.add_argument("--diagnose", action="store_true",
                        help="Compare cached call counts vs live HubSpot for a sample of 20 contacts")
    args = parser.parse_args()

    if args.diagnose:
        diagnose_cache()
        return

    print("=" * 50)
    print("Milo HubSpot Data Fetcher")
    print("=" * 50)
    print()

    # 1. Fetch contacts (Tom's, with phone, filtered to +44)
    uk_contacts, total_with_phone = fetch_contacts()
    contact_ids = [c["id"] for c in uk_contacts]

    if not contact_ids:
        print("No UK (+44) contacts found. Exiting.")
        return

    # 2. Fetch call associations (batch)
    print()
    call_assocs = batch_fetch_associations(contact_ids, "contacts", "calls", "call")

    # Collect all unique call IDs
    all_call_ids = list({cid for ids in call_assocs.values() for cid in ids})

    # 3. Fetch call details
    print()
    call_properties = ["hs_call_disposition", "hs_timestamp", "hs_call_direction"]
    call_details = batch_fetch_objects(all_call_ids, "calls", call_properties, "call details")

    # 4. Fetch task associations (batch)
    print()
    task_assocs = batch_fetch_associations(contact_ids, "contacts", "tasks", "task")

    # Collect all unique task IDs
    all_task_ids = list({tid for ids in task_assocs.values() for tid in ids})

    # 5. Fetch task details
    print()
    task_properties = ["hs_task_type", "hs_task_status"]
    task_details = batch_fetch_objects(all_task_ids, "tasks", task_properties, "task details")

    # 6. Assemble output
    print()
    print("Assembling data...", end=" ", flush=True)

    cutoff_dt = datetime.fromisoformat(CALLS_CUTOFF.replace("Z", "+00:00"))
    contacts_with_calls = 0
    contacts_without_calls = 0
    total_valid_calls = 0
    total_tasks = 0

    contacts_out = []
    for contact in uk_contacts:
        props = contact.get("properties", {})
        cid = contact["id"]

        # Build call list: outbound only, after cutoff
        contact_calls = []
        for call_id in call_assocs.get(cid, []):
            call = call_details.get(call_id)
            if not call:
                continue
            if call.get("hs_call_direction") != "OUTBOUND":
                continue
            ts = call.get("hs_timestamp", "")
            if ts:
                try:
                    call_dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    if call_dt < cutoff_dt:
                        continue
                except ValueError:
                    continue

            disp_uuid = call.get("hs_call_disposition", "")
            disp_name = DISPOSITION_MAP.get(disp_uuid, disp_uuid)

            contact_calls.append({
                "disposition_uuid": disp_uuid,
                "disposition_name": disp_name,
                "timestamp": ts,
            })

        # Compute call summary (handles ignored dispositions internally)
        call_summary = compute_call_summary(contact_calls)

        if call_summary["total_calls"] > 0:
            contacts_with_calls += 1
        else:
            contacts_without_calls += 1
        total_valid_calls += call_summary["total_calls"]

        # Filter tasks: CALL type, NOT_STARTED only
        contact_tasks = []
        for task_id in task_assocs.get(cid, []):
            task = task_details.get(task_id)
            if not task:
                continue
            if task.get("hs_task_type") != "CALL":
                continue
            if task.get("hs_task_status") != "NOT_STARTED":
                continue
            contact_tasks.append({
                "task_id": task_id,
                "task_type": "CALL",
                "task_status": "NOT_STARTED",
            })

        total_tasks += len(contact_tasks)

        contacts_out.append({
            "contact_id": cid,
            "firstname": props.get("firstname", ""),
            "lastname": props.get("lastname", ""),
            "jobtitle": props.get("jobtitle", ""),
            "company": props.get("company", ""),
            "phone": props.get("phone", ""),
            "owner_id": props.get("hubspot_owner_id", ""),
            "call_summary": call_summary,
            "open_call_tasks": contact_tasks,
        })

    print("done")

    output = {
        "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "contacts": contacts_out,
    }

    # Write cache
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print()
    print("=" * 50)
    print(f"Contacts fetched (with phone):  {total_with_phone:,}")
    print(f"Contacts with +44 (UK):         {len(contacts_out):,}")
    print(f"Outbound calls (valid):         {total_valid_calls:,}")
    print(f"Contacts with >= 1 call:        {contacts_with_calls:,}")
    print(f"Contacts with zero calls:       {contacts_without_calls:,}")
    print(f"Open call tasks:                {total_tasks:,}")
    print(f"Cache written to:               {CACHE_FILE}")
    print("=" * 50)


if __name__ == "__main__":
    main()
