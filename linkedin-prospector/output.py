import csv
import html
import webbrowser
from pathlib import Path
from typing import List

from models import Prospect

BASE_DIR = Path(__file__).parent

PROSPECT_COLUMNS = [
    "name",
    "title",
    "company",
    "company_size",
    "industry",
    "score",
    "verdict",
    "reason",
    "pain_angle",
    "connection_message",
    "pushaway_message",
    "followup_dm",
    "linkedin_url",
    "email",
    "source",
]


def _prospect_to_row(p):
    """Convert a Prospect to a CSV row dict."""
    return {
        "name": p.full_name,
        "title": p.title,
        "company": p.company,
        "company_size": p.company_size or "",
        "industry": p.industry or "",
        "score": p.score or "",
        "verdict": p.verdict or "",
        "reason": p.reason or "",
        "pain_angle": p.pain_angle or "",
        "connection_message": p.connection_message or "",
        "pushaway_message": p.pushaway_message or "",
        "followup_dm": p.followup_dm or "",
        "linkedin_url": p.linkedin_url or "",
        "email": p.email or "",
        "source": p.source,
    }


def write_prospects_csv(prospects, filename="prospects.csv"):
    """
    Write prospects.csv — only TARGET and QUALIFY verdicts, sorted by score descending.
    Returns the filepath.
    """
    # Filter to TARGET and QUALIFY only
    output = [p for p in prospects if p.verdict in ("TARGET", "QUALIFY")]

    # Sort by score descending
    output.sort(key=lambda p: p.score or 0, reverse=True)

    filepath = BASE_DIR / filename

    # UTF-8 BOM for Excel compatibility
    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=PROSPECT_COLUMNS, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for p in output:
            writer.writerow(_prospect_to_row(p))

    print(f"\n[Output] Written: {filename} ({len(output)} prospects)")

    # Also write an HTML version that's easy to read and copy from
    html_path = write_prospects_html(output)
    print(f"[Output] Written: prospects.html (opening in browser...)")
    webbrowser.open(f"file://{html_path}")

    return str(filepath)


def write_prospects_html(prospects, filename="prospects.html"):
    """Write a clean HTML table that opens in any browser. Easy to read and copy."""
    filepath = BASE_DIR / filename
    e = html.escape

    rows_html = ""
    for p in prospects:
        li_link = f'<a href="{e(p.linkedin_url or "")}" target="_blank">{e(p.full_name)}</a>' if p.linkedin_url else e(p.full_name)
        badge = "TARGET" if p.verdict == "TARGET" else "QUALIFY"
        badge_color = "#22c55e" if p.verdict == "TARGET" else "#f59e0b"

        rows_html += f"""
        <tr>
          <td>{li_link}<br><small style="color:#666">{e(p.title)}</small></td>
          <td>{e(p.company)}<br><small style="color:#666">{e(p.company_size or '?')} employees · {e(p.industry or '?')}</small></td>
          <td style="text-align:center"><strong>{p.score}/10</strong><br><span style="background:{badge_color};color:#fff;padding:2px 8px;border-radius:4px;font-size:12px">{badge}</span></td>
          <td><small>{e(p.pain_angle or '')}</small></td>
          <td style="max-width:300px"><small>{e(p.connection_message or '')}</small></td>
          <td style="max-width:300px"><small>{e(p.pushaway_message or '')}</small></td>
          <td style="max-width:350px"><small>{e(p.followup_dm or '')}</small></td>
          <td><small>{e(p.email or '')}</small></td>
        </tr>"""

    page = f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<title>Prospects — {len(prospects)} results</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 20px; background: #f9fafb; }}
  h1 {{ font-size: 20px; }}
  table {{ border-collapse: collapse; width: 100%; background: #fff; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
  th {{ background: #1e293b; color: #fff; padding: 10px 12px; text-align: left; font-size: 13px; position: sticky; top: 0; }}
  td {{ padding: 10px 12px; border-bottom: 1px solid #e5e7eb; vertical-align: top; font-size: 13px; }}
  tr:hover {{ background: #f1f5f9; }}
  a {{ color: #2563eb; text-decoration: none; font-weight: 600; }}
  a:hover {{ text-decoration: underline; }}
  small {{ line-height: 1.4; display: block; }}
</style>
</head><body>
<h1>Prospects ({len(prospects)} results)</h1>
<table>
<tr>
  <th>Name / Title</th>
  <th>Company</th>
  <th>Score</th>
  <th>Pain Angle</th>
  <th>Connection Message</th>
  <th>Push-Away</th>
  <th>Follow-Up DM</th>
  <th>Email</th>
</tr>
{rows_html}
</table>
</body></html>"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(page)

    return str(filepath)


def print_summary(prospects):
    """Print a terminal summary of the run."""
    total = len(prospects)
    scored = [p for p in prospects if p.score is not None]
    targets = sum(1 for p in scored if p.verdict == "TARGET")
    qualifies = sum(1 for p in scored if p.verdict == "QUALIFY")
    skips = sum(1 for p in scored if p.verdict == "SKIP")
    messaged = sum(1 for p in prospects if p.connection_message)

    sources = {}
    for p in prospects:
        sources[p.source] = sources.get(p.source, 0) + 1

    source_str = ", ".join(f"{v} from {k}" for k, v in sources.items())

    print("\n" + "=" * 50)
    print("  SUMMARY")
    print("=" * 50)
    print(f"  Total found:  {total} ({source_str})")
    print(f"  Scored:       {len(scored)}")
    print(f"    TARGET:     {targets}")
    print(f"    QUALIFY:    {qualifies}")
    print(f"    SKIP:       {skips}")
    print(f"  Messages:     {messaged}")
    print(f"  Output:       prospects.csv")
    print("=" * 50)
