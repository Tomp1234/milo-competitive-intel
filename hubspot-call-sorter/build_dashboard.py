#!/usr/bin/env python3
"""Build an HTML dashboard from last_run.json scoring results."""

import argparse
import json
import os
import sys
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
LAST_RUN_FILE = os.path.join(DATA_DIR, "last_run.json")
CACHE_FILE = os.path.join(DATA_DIR, "hubspot_cache.json")
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "index.html")


def load_json(path):
    with open(path) as f:
        return json.load(f)


def get_cache_stats():
    """Get total contacts and fetch time from cache file."""
    if not os.path.exists(CACHE_FILE):
        return None, None
    data = load_json(CACHE_FILE)
    return len(data.get("contacts", [])), data.get("fetched_at")


def escape(text):
    """Escape HTML entities."""
    if text is None:
        return ""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def build_contact_card(contact):
    tier = contact["tier"]
    tier_colours = {1: "#DC2626", 2: "#D97706", 3: "#2563EB", 4: "#6B7280"}
    tier_labels = {
        1: "P1 — Warm Reactivation",
        2: "P2 — High ICP Not Reached",
        3: "P3 — Lower ICP Not Reached",
        4: "P4 — High ICP Never Called",
    }
    border_colour = tier_colours.get(tier, "#2A2A2A")

    name = escape(contact.get("name", "Unknown"))
    company = escape(contact.get("company", "—"))
    jobtitle = escape(contact.get("jobtitle", "—"))
    phone = escape(contact.get("phone", "—"))
    icp_score = contact.get("icp_score", 0)
    best_signal = escape(contact.get("best_signal") or "—")
    best_signal_date = escape(contact.get("best_signal_date") or "—")
    last_disp = escape(contact.get("last_disposition") or "—")
    last_call_date = escape(contact.get("last_call_date") or "—")
    days = contact.get("days_since_last_call") or "—"
    total_calls = contact.get("total_calls", 0)
    task_created = contact.get("task_created", False)
    skip_reason = contact.get("skip_reason")

    if task_created:
        badge = '<span class="badge badge-success">Task Created</span>'
    elif skip_reason:
        badge = f'<span class="badge badge-skip">{escape(skip_reason)}</span>'
    else:
        badge = '<span class="badge badge-skip">Dry Run</span>'

    return f"""<div class="card" style="border-left: 3px solid {border_colour}">
  <div class="card-header">
    <div>
      <div class="card-name">{name}</div>
      <div class="card-company">{company}</div>
    </div>
    {badge}
  </div>
  <div class="card-details">
    <div class="detail"><span class="detail-label">Title</span><span class="detail-value">{jobtitle}</span></div>
    <div class="detail"><span class="detail-label">Phone</span><span class="detail-value">{phone}</span></div>
    <div class="detail"><span class="detail-label">ICP Score</span><span class="detail-value">{icp_score}</span></div>
    <div class="detail"><span class="detail-label">Total Calls</span><span class="detail-value">{total_calls}</span></div>
    <div class="detail"><span class="detail-label">Best Signal</span><span class="detail-value">{best_signal}</span></div>
    <div class="detail"><span class="detail-label">Signal Date</span><span class="detail-value">{best_signal_date}</span></div>
    <div class="detail"><span class="detail-label">Last Disposition</span><span class="detail-value">{last_disp}</span></div>
    <div class="detail"><span class="detail-label">Last Call</span><span class="detail-value">{last_call_date}</span></div>
    <div class="detail"><span class="detail-label">Days Since Call</span><span class="detail-value">{days}</span></div>
  </div>
</div>"""


def build_tier_section(tier, contacts):
    tier_config = {
        1: {"label": "Priority 1 — Warm Reactivation", "colour": "#DC2626"},
        2: {"label": "Priority 2 — High ICP Not Reached", "colour": "#D97706"},
        3: {"label": "Priority 3 — Lower ICP Not Reached", "colour": "#2563EB"},
        4: {"label": "Priority 4 — High ICP Never Called", "colour": "#16A34A"},
    }
    cfg = tier_config[tier]
    tier_contacts = [c for c in contacts if c.get("tier") == tier]

    if not tier_contacts:
        cards = '<div class="empty-tier">No contacts in this tier this run.</div>'
    else:
        cards = "\n".join(build_contact_card(c) for c in tier_contacts)

    return f"""<section class="tier-section">
  <h2 class="tier-heading" style="border-left: 4px solid {cfg['colour']}; padding-left: 12px; color: {cfg['colour']}">{cfg['label']} <span class="tier-count">({len(tier_contacts)})</span></h2>
  <div class="card-grid">
    {cards}
  </div>
</section>"""


def build_html(data, cache_total, cache_fetched_at):
    summary = data.get("summary", {})
    tasks = data.get("tasks", [])
    run_at = data.get("run_at", "Unknown")
    dry_run = data.get("dry_run", True)

    mode_label = "DRY RUN" if dry_run else "LIVE"
    mode_class = "mode-dry" if dry_run else "mode-live"

    # Format timestamps
    try:
        run_dt = datetime.fromisoformat(run_at.replace("Z", "+00:00"))
        run_display = run_dt.strftime("%d %b %Y %H:%M UTC")
    except Exception:
        run_display = run_at

    cache_display = "—"
    if cache_fetched_at:
        try:
            cache_dt = datetime.fromisoformat(cache_fetched_at.replace("Z", "+00:00"))
            cache_display = cache_dt.strftime("%d %b %Y %H:%M UTC")
        except Exception:
            cache_display = cache_fetched_at

    contacts_processed = summary.get("contacts_processed", 0)
    contacts_eligible = summary.get("contacts_eligible", 0)
    tasks_created = summary.get("tasks_created", 0)
    contacts_skipped = summary.get("contacts_skipped", 0)

    tier_sections = "\n".join(build_tier_section(t, tasks) for t in [1, 2, 3, 4])

    cache_total_display = f"{cache_total:,}" if cache_total is not None else "—"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Milo GTM Call Prioritiser</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: #0A0A0A;
    color: #F9FAFB;
    min-height: 100vh;
    -webkit-font-smoothing: antialiased;
  }}

  .container {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 24px;
  }}

  /* Header */
  .header {{
    border-bottom: 1px solid #2A2A2A;
    padding: 20px 0;
  }}

  .header-inner {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
  }}

  .header-brand {{
    display: flex;
    align-items: baseline;
    gap: 10px;
  }}

  .header-logo {{
    font-size: 24px;
    font-weight: 700;
    color: #6B46C1;
    letter-spacing: -0.5px;
  }}

  .header-title {{
    font-size: 14px;
    font-weight: 500;
    color: #9CA3AF;
  }}

  .header-meta {{
    display: flex;
    align-items: center;
    gap: 16px;
    font-size: 13px;
    color: #9CA3AF;
  }}

  .mode-badge {{
    display: inline-flex;
    align-items: center;
    padding: 4px 10px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
  }}

  .mode-dry {{
    background: rgba(217, 119, 6, 0.15);
    color: #D97706;
    border: 1px solid rgba(217, 119, 6, 0.3);
  }}

  .mode-live {{
    background: rgba(5, 150, 105, 0.15);
    color: #059669;
    border: 1px solid rgba(5, 150, 105, 0.3);
  }}

  .run-btn {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 14px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
    color: #F9FAFB;
    background: #6B46C1;
    text-decoration: none;
    transition: background 0.15s;
  }}

  .run-btn:hover {{
    background: #7C5CD0;
  }}

  .run-btn svg {{
    width: 14px;
    height: 14px;
  }}

  /* Timestamps bar */
  .timestamps {{
    display: flex;
    gap: 24px;
    flex-wrap: wrap;
    padding: 12px 0;
    font-size: 12px;
    color: #9CA3AF;
    border-bottom: 1px solid #2A2A2A;
  }}

  .ts-item {{
    display: flex;
    align-items: center;
    gap: 6px;
  }}

  .ts-label {{
    color: #6B7280;
  }}

  .ts-value {{
    color: #D1D5DB;
    font-weight: 500;
  }}

  /* Stats */
  .stats-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    padding: 32px 0;
  }}

  @media (max-width: 640px) {{
    .stats-grid {{
      grid-template-columns: repeat(2, 1fr);
    }}
  }}

  .stat-box {{
    background: #1A1A1A;
    border: 1px solid #2A2A2A;
    border-radius: 8px;
    padding: 24px;
    text-align: center;
  }}

  .stat-number {{
    font-size: 36px;
    font-weight: 700;
    line-height: 1;
    margin-bottom: 6px;
    color: #F9FAFB;
  }}

  .stat-label {{
    font-size: 12px;
    font-weight: 500;
    color: #9CA3AF;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }}

  /* Tier sections */
  .tier-section {{
    margin-bottom: 40px;
  }}

  .tier-heading {{
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 16px;
    display: flex;
    align-items: baseline;
    gap: 8px;
  }}

  .tier-count {{
    font-size: 13px;
    font-weight: 400;
    color: #9CA3AF;
  }}

  .card-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
    gap: 12px;
  }}

  @media (max-width: 400px) {{
    .card-grid {{
      grid-template-columns: 1fr;
    }}
  }}

  .card {{
    background: #1A1A1A;
    border: 1px solid #2A2A2A;
    border-radius: 8px;
    padding: 16px;
    transition: border-color 0.15s;
  }}

  .card:hover {{
    border-color: #3A3A3A;
  }}

  .card-header {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 12px;
    gap: 8px;
  }}

  .card-name {{
    font-size: 15px;
    font-weight: 600;
    color: #F9FAFB;
    line-height: 1.3;
  }}

  .card-company {{
    font-size: 13px;
    color: #9CA3AF;
    margin-top: 2px;
  }}

  .badge {{
    display: inline-flex;
    align-items: center;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 500;
    white-space: nowrap;
    flex-shrink: 0;
  }}

  .badge-success {{
    background: rgba(5, 150, 105, 0.15);
    color: #059669;
    border: 1px solid rgba(5, 150, 105, 0.3);
  }}

  .badge-skip {{
    background: rgba(156, 163, 175, 0.1);
    color: #9CA3AF;
    border: 1px solid rgba(156, 163, 175, 0.2);
  }}

  .card-details {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
  }}

  .detail {{
    display: flex;
    flex-direction: column;
    gap: 2px;
  }}

  .detail-label {{
    font-size: 11px;
    color: #9CA3AF;
    text-transform: uppercase;
    letter-spacing: 0.3px;
  }}

  .detail-value {{
    font-size: 13px;
    color: #F9FAFB;
    font-weight: 500;
  }}

  .empty-tier {{
    background: #1A1A1A;
    border: 1px solid #2A2A2A;
    border-radius: 8px;
    padding: 32px;
    text-align: center;
    color: #9CA3AF;
    font-size: 14px;
  }}

  /* Footer */
  .footer {{
    border-top: 1px solid #2A2A2A;
    padding: 20px 0;
    margin-top: 40px;
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 8px;
    font-size: 12px;
    color: #9CA3AF;
  }}
</style>
</head>
<body>
  <header class="header">
    <div class="container header-inner">
      <div class="header-brand">
        <span class="header-logo">Milo</span>
        <span class="header-title">GTM Call Prioritiser</span>
      </div>
      <div class="header-meta">
        <span class="mode-badge {mode_class}">{mode_label}</span>
        <a href="https://github.com/Tomp1234/milo-competitive-intel/actions/workflows/prioritise.yml" target="_blank" rel="noopener" class="run-btn">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="5 3 19 12 5 21 5 3"/></svg>
          Run Workflow
        </a>
      </div>
    </div>
  </header>

  <main class="container">
    <div class="timestamps">
      <div class="ts-item"><span class="ts-label">Data fetched:</span> <span class="ts-value">{cache_display}</span></div>
      <div class="ts-item"><span class="ts-label">Scored:</span> <span class="ts-value">{run_display}</span></div>
    </div>

    <div class="stats-grid">
      <div class="stat-box">
        <div class="stat-number">{contacts_processed:,}</div>
        <div class="stat-label">Contacts Processed</div>
      </div>
      <div class="stat-box">
        <div class="stat-number">{contacts_eligible:,}</div>
        <div class="stat-label">Eligible</div>
      </div>
      <div class="stat-box">
        <div class="stat-number">{tasks_created:,}</div>
        <div class="stat-label">Tasks Created</div>
      </div>
      <div class="stat-box">
        <div class="stat-number">{contacts_skipped:,}</div>
        <div class="stat-label">Skipped</div>
      </div>
    </div>

    {tier_sections}
  </main>

  <footer class="footer">
    <div class="container" style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;width:100%">
      <span>Cache: {cache_total_display} contacts</span>
      <span>Data fetched: {cache_display}</span>
    </div>
  </footer>
</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(description="Build HTML dashboard from scoring results")
    parser.add_argument("--output", default=OUTPUT_FILE, help="Output path for index.html")
    args = parser.parse_args()

    if not os.path.exists(LAST_RUN_FILE):
        print(f"Error: {LAST_RUN_FILE} not found. Run scorer.py first.", file=sys.stderr)
        sys.exit(1)

    data = load_json(LAST_RUN_FILE)
    cache_total, cache_fetched_at = get_cache_stats()

    html = build_html(data, cache_total, cache_fetched_at)

    output_path = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w") as f:
        f.write(html)

    print(f"Dashboard written to: {output_path}")


if __name__ == "__main__":
    main()
