import time
from typing import List, Tuple

import requests

from config import (
    APOLLO_BASE_URL,
    TARGET_TITLES,
    EXCLUDE_TITLE_KEYWORDS,
    EMPLOYEE_RANGE,
)
from models import Prospect


def _has_excluded_title(title):
    """Check if a title contains any excluded keywords."""
    if not title:
        return False
    title_upper = title.upper()
    for keyword in EXCLUDE_TITLE_KEYWORDS:
        # Match as whole word boundary — "Data" should match "Head of Data"
        # but not accidentally flag "Director of Operations Database"
        # Simple approach: check if keyword appears as a separate word
        if f" {keyword.upper()}" in f" {title_upper}" or title_upper.startswith(keyword.upper()):
            return True
    return False


def search_people(api_key, page=1, per_page=25):
    """
    Search Apollo for ICP-fit people. Free, no credits consumed.
    Returns (list of raw person dicts, total count).
    """
    url = f"{APOLLO_BASE_URL}/mixed_people/api_search"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
    }
    payload = {
        "person_titles": TARGET_TITLES,
        "organization_num_employees_ranges": [EMPLOYEE_RANGE],
        "person_locations": ["United Kingdom"],
        "person_seniorities": ["director", "vp", "c_suite"],
        "per_page": per_page,
        "page": page,
    }

    resp = requests.post(url, json=payload, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    people = data.get("people", [])
    total = data.get("pagination", {}).get("total_entries", 0)
    return people, total


def filter_excluded_titles(people):
    """
    Post-search filter: remove anyone whose title contains excluded keywords.
    Apollo's title filter is fuzzy — "Head of Data & Innovation" can slip through.
    """
    filtered = []
    skipped = []
    for person in people:
        title = person.get("title", "") or ""
        if _has_excluded_title(title):
            skipped.append(person)
        else:
            filtered.append(person)

    if skipped:
        print(f"  [Apollo] Filtered out {len(skipped)} excluded titles:")
        for p in skipped[:5]:
            print(f"    - {p.get('name', '?')} ({p.get('title', '?')})")
        if len(skipped) > 5:
            print(f"    ... and {len(skipped) - 5} more")

    return filtered


def _raw_to_prospect(person):
    """
    Convert an Apollo raw person dict to a Prospect object.
    Note: Free search returns obfuscated data (last_name_obfuscated, boolean flags).
    Full data comes after enrichment via people/match endpoint.
    """
    org = person.get("organization", {}) or {}
    first = person.get("first_name", "") or ""
    # Free search obfuscates last name; enrichment provides full last_name
    last = person.get("last_name", "") or ""
    title = person.get("title", "") or ""
    company = org.get("name", "") or ""

    return Prospect(
        first_name=first,
        last_name=last,
        full_name=f"{first} {last}".strip(),
        title=title,
        company=company,
        company_size=str(org.get("estimated_num_employees", "")) or None,
        linkedin_url=person.get("linkedin_url", "") or None,
        email=person.get("email", "") or None,
        industry=org.get("industry", "") or None,
        location=person.get("city", "") or person.get("country", "") or None,
        headline=person.get("headline", "") or None,
        source="apollo",
        apollo_id=person.get("id", "") or None,
    )


def enrich_single(api_key, prospect):
    """
    Enrich a single prospect via Apollo people/match using their Apollo ID.
    Costs 1 credit. Updates prospect in-place with full data.
    """
    if not prospect.apollo_id:
        return prospect

    url = f"{APOLLO_BASE_URL}/people/match"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
    }
    payload = {"id": prospect.apollo_id}

    resp = requests.post(url, json=payload, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    person = data.get("person")
    if not person:
        return prospect

    # Update all fields with full enriched data
    prospect.first_name = person.get("first_name", "") or prospect.first_name
    prospect.last_name = person.get("last_name", "") or prospect.last_name
    prospect.full_name = f"{prospect.first_name} {prospect.last_name}".strip()
    prospect.title = person.get("title", "") or prospect.title
    prospect.email = person.get("email", "") or prospect.email
    prospect.linkedin_url = person.get("linkedin_url", "") or prospect.linkedin_url
    prospect.location = person.get("city", "") or person.get("country", "") or prospect.location

    org = person.get("organization", {}) or {}
    prospect.company = org.get("name", "") or prospect.company
    if org.get("estimated_num_employees"):
        prospect.company_size = str(org["estimated_num_employees"])
    if org.get("industry"):
        prospect.industry = org["industry"]

    return prospect


def search_and_enrich(api_key, max_results=50):
    """
    Full Apollo pipeline: search, filter, confirm credits, enrich.
    Returns list of enriched Prospect objects.
    """
    all_people = []
    page = 1
    per_page = min(max_results, 100)

    print("\n[Apollo] Searching for ICP-fit prospects...")

    while len(all_people) < max_results:
        people, total = search_people(api_key, page=page, per_page=per_page)

        if not people:
            if page == 1:
                print("  [Apollo] No results found. Try broadening filters.")
            break

        if page == 1:
            print(f"  [Apollo] {total} total matches in Apollo. Fetching up to {max_results}...")

        all_people.extend(people)
        page += 1
        time.sleep(1)  # rate limit between pages

        if len(people) < per_page:
            break  # last page

    all_people = all_people[:max_results]
    print(f"  [Apollo] Fetched {len(all_people)} raw results")

    # Post-search title filter
    filtered = filter_excluded_titles(all_people)
    print(f"  [Apollo] {len(filtered)} prospects after title filtering")

    if not filtered:
        return []

    # Convert to Prospect objects
    prospects = [_raw_to_prospect(p) for p in filtered]

    # Enrichment confirmation
    credits_needed = len(prospects)
    print()
    print("  " + "=" * 40)
    print(f"  ENRICHMENT: This will use ~{credits_needed} Apollo credits.")
    print(f"  Without enrichment, scoring won't work well.")
    print("  " + "=" * 40)
    confirm = input("\n  Enrich these prospects? (y/n): ").strip().lower()
    if confirm != "y":
        print("  [Apollo] Skipping enrichment. Prospects will have limited data.")
        return prospects

    # Enrich one by one using Apollo person ID
    print(f"  [Apollo] Enriching {len(prospects)} prospects...")
    enriched = 0
    for i, prospect in enumerate(prospects):
        try:
            enrich_single(api_key, prospect)
            if prospect.email:
                enriched += 1
            print(f"  [{i+1}/{len(prospects)}] {prospect.full_name} ({prospect.title} at {prospect.company})")
        except requests.exceptions.RequestException as e:
            print(f"  [{i+1}/{len(prospects)}] [!] Enrichment failed: {e}")

        if i < len(prospects) - 1:
            time.sleep(1)  # rate limit between calls

    print(f"  [Apollo] Enrichment complete. {enriched}/{len(prospects)} have emails.")

    return prospects
