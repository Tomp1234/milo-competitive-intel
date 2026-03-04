#!/usr/bin/env python3
"""
LinkedIn Prospecting Intelligence Tool
Finds ICP-fit prospects, scores them, and generates personalised messages.

Usage: python run.py
"""

import sys
import os

# Add project root to path so imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import load_config, DailyLimitExceeded
from sources.apify import scrape_post_engagers
from sources.apollo import search_and_enrich
from scoring import score_batch
from messaging import generate_messages_batch
from output import write_prospects_csv, print_summary


def deduplicate_prospects(prospects):
    """Remove duplicates across sources by LinkedIn URL or full name."""
    seen_urls = set()
    seen_names = set()
    unique = []

    for p in prospects:
        # Prefer dedup by LinkedIn URL
        if p.linkedin_url:
            if p.linkedin_url in seen_urls:
                continue
            seen_urls.add(p.linkedin_url)
        else:
            # Fall back to name dedup
            name_key = p.full_name.lower().strip()
            if name_key in seen_names:
                continue
            seen_names.add(name_key)

        unique.append(p)

    return unique


def get_source_choice():
    """Ask user which source to use."""
    print("\nWhich source?")
    print("  [1] LinkedIn post engagers (Apify)")
    print("  [2] Apollo prospect search")
    print("  [3] Both")
    print()

    while True:
        choice = input("  > ").strip()
        if choice in ("1", "2", "3"):
            return int(choice)
        print("  Enter 1, 2, or 3.")


def get_post_url():
    """Ask user for a LinkedIn post URL."""
    print("\nLinkedIn post URL:")
    while True:
        url = input("  > ").strip()
        if "linkedin.com" in url:
            return url
        print("  Enter a valid LinkedIn URL (must contain linkedin.com).")


def get_apollo_max_results():
    """Ask user how many Apollo results to fetch."""
    print("\nHow many Apollo results to search? (default: 50)")
    val = input("  > ").strip()
    if not val:
        return 50
    try:
        n = int(val)
        return min(max(n, 10), 200)
    except ValueError:
        return 50


def main():
    print("\n" + "=" * 50)
    print("  LINKEDIN PROSPECTING INTELLIGENCE")
    print("=" * 50)

    # Load config and validate API keys
    config = load_config()

    # Get user input
    source_choice = get_source_choice()

    post_url = None
    apollo_max = 50

    if source_choice in (1, 3):
        post_url = get_post_url()
    if source_choice in (2, 3):
        apollo_max = get_apollo_max_results()

    # Collect prospects from selected sources
    all_prospects = []

    if source_choice in (1, 3):
        print("\n" + "-" * 40)
        try:
            apify_prospects = scrape_post_engagers(
                post_url=post_url,
                api_key=config["APIFY_API_KEY"],
            )
            all_prospects.extend(apify_prospects)
        except DailyLimitExceeded as e:
            print(f"  [!] {e}")
            if source_choice == 1:
                print("  No other source selected. Exiting.")
                return
            print("  Continuing with Apollo source...")

    if source_choice in (2, 3):
        print("\n" + "-" * 40)
        try:
            apollo_prospects = search_and_enrich(
                api_key=config["APOLLO_API_KEY"],
                max_results=apollo_max,
            )
            all_prospects.extend(apollo_prospects)
        except Exception as e:
            print(f"  [!] Apollo error: {e}")
            if source_choice == 2:
                print("  No other source available. Exiting.")
                return

    if not all_prospects:
        print("\n  No prospects found from any source. Nothing to do.")
        return

    # Deduplicate across sources
    if source_choice == 3:
        before = len(all_prospects)
        all_prospects = deduplicate_prospects(all_prospects)
        dupes = before - len(all_prospects)
        if dupes:
            print(f"\n  [Dedup] Removed {dupes} duplicates across sources. {len(all_prospects)} unique.")

    # Score all prospects
    all_prospects = score_batch(config["ANTHROPIC_API_KEY"], all_prospects)

    # Generate messages for score >= 7
    all_prospects = generate_messages_batch(config["ANTHROPIC_API_KEY"], all_prospects)

    # Write CSV
    write_prospects_csv(all_prospects)

    # Print summary
    print_summary(all_prospects)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Interrupted. Partial results may not have been saved.")
        sys.exit(1)
    except Exception as e:
        print(f"\n  [Fatal] Unexpected error: {e}")
        print("  Check your API keys and network connection.")
        sys.exit(1)
