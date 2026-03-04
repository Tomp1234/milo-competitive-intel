import json
import re
import time
from typing import List

import anthropic

from config import CLAUDE_MODEL
from models import Prospect, ScoringResult


SCORING_SYSTEM_PROMPT = """You are an ICP scoring engine for Milo, an AI-powered conversational business intelligence platform.

Score each prospect on a 1-10 scale against the following ICP:

TARGET PROFILE:
- Business leaders at 100-500 employee companies who WAIT for data
- Best titles (with real conversion data):
  * Innovation titles: 100% conversion rate (5/5 calls) — PRIMARY TARGET
  * COO / VP Operations: 83% conversion rate (5/6 calls) — PRIMARY TARGET
  * Director (general business): 75% conversion rate (3/4 calls) — GOOD TARGET
  * CEO at companies under 200 employees: 43% conversion rate — QUALIFY HARDER
  * Head of Sales / VP Sales: Worth targeting, no conversion data yet
- Target verticals: eCommerce/DTC, Event Ticketing, SaaS, Agencies, Logistics, AdTech
- Target geography: UK/Europe with local decision-making authority

HARD EXCLUSIONS (score 1-2, verdict SKIP):
- Any title with AI, Data, BI, Business Intelligence, Analytics, Insights, Engineering, CTO, Data Science as primary function — 0% conversion from 13 calls
- Companies with 50+ engineers / "builder" culture
- Pre-Series A startups, Enterprise 1000+ employees
- UK subsidiaries where decisions are made in US
- iGaming vertical (deprioritised)

SCORING GUIDE:
- 9-10: Perfect ICP (right title, 100-500 employees, target vertical, UK/Europe)
- 7-8: Strong match with one soft flag (e.g. CEO at 300 employees, unknown vertical)
- 5-6: Possible fit, needs qualification (unclear title, borderline size, unknown industry)
- 3-4: Weak fit (wrong vertical, too large, technical-adjacent title)
- 1-2: Hard exclusion (AI/Data/BI title, builder company, too small/large)

VERDICT RULES:
- TARGET: score >= 8
- QUALIFY: score 5-7
- SKIP: score <= 4

PAIN ANGLE — pick the most likely fit based on their role:
- analyst_bottleneck: They wait days for data answers (Ops, Commercial, Sales leaders)
- chatgpt_security: Staff uploading sensitive data to personal ChatGPT (COO, CEO, compliance-adjacent)
- bi_failure: Power BI / Tableau gathering dust, nobody uses it (anyone who's tried BI before)
- manual_reporting: 20-30 KPIs pulled manually every month (Operations, Innovation)
- ip_risk: IP/patent data leaking via ChatGPT (Defense, Manufacturing, Pharma)

Return ONLY valid JSON. No markdown, no explanation, just the JSON object."""


def _build_scoring_prompt(prospect):
    """Build the user prompt for scoring a single prospect."""
    return f"""Score this prospect:
Name: {prospect.full_name}
Title: {prospect.title}
Headline: {prospect.headline or prospect.title}
Company: {prospect.company}
Company Size: {prospect.company_size or 'Unknown'} employees
Industry: {prospect.industry or 'Unknown'}
Location: {prospect.location or 'Unknown'}
LinkedIn: {prospect.linkedin_url or 'N/A'}
Source: {prospect.source}"""


def _extract_result(data):
    """Extract ScoringResult from a parsed JSON dict, handling field name variations."""
    reason = data.get("reason") or data.get("reasoning") or data.get("explanation") or ""
    pain = data.get("best_pain_angle") or data.get("pain_angle") or data.get("pain") or "analyst_bottleneck"
    return ScoringResult(
        score=int(data["score"]),
        verdict=data["verdict"].upper(),
        reason=reason,
        best_pain_angle=pain,
    )


def _parse_scoring_response(text):
    """
    Extract ScoringResult from Claude's response text.
    Handles raw JSON, markdown-wrapped JSON, and fallback.
    """
    # Try direct JSON parse
    try:
        return _extract_result(json.loads(text.strip()))
    except (json.JSONDecodeError, KeyError, ValueError, TypeError):
        pass

    # Try extracting JSON from markdown code block
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        try:
            return _extract_result(json.loads(match.group(1)))
        except (json.JSONDecodeError, KeyError, ValueError, TypeError):
            pass

    # Try finding any JSON object in the text
    match = re.search(r"\{[^{}]*\"score\"[^{}]*\}", text, re.DOTALL)
    if match:
        try:
            return _extract_result(json.loads(match.group(0)))
        except (json.JSONDecodeError, KeyError, ValueError, TypeError):
            pass

    # Fallback
    print(f"    [!] Could not parse scoring response. Defaulting to QUALIFY.")
    return ScoringResult(
        score=5,
        verdict="QUALIFY",
        reason="Scoring parse failed — manual review needed",
        best_pain_angle="analyst_bottleneck",
    )


def score_prospect(client, prospect):
    """Score a single prospect using Claude API. Returns ScoringResult."""
    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=300,
        system=SCORING_SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": _build_scoring_prompt(prospect)}
        ],
    )

    text = response.content[0].text
    return _parse_scoring_response(text)


def score_batch(api_key, prospects):
    """
    Score all prospects. Updates each prospect in-place with score/verdict/reason/pain_angle.
    Returns the updated list.
    """
    if not prospects:
        return prospects

    client = anthropic.Anthropic(api_key=api_key)

    print(f"\n[Scoring] Scoring {len(prospects)} prospects against ICP...")

    for i, prospect in enumerate(prospects):
        label = f"{prospect.full_name} ({prospect.title} at {prospect.company})"
        try:
            result = score_prospect(client, prospect)
            prospect.score = result.score
            prospect.verdict = result.verdict
            prospect.reason = result.reason
            prospect.pain_angle = result.best_pain_angle

            icon = {"TARGET": "+", "QUALIFY": "~", "SKIP": "-"}.get(result.verdict, "?")
            print(f"  [{i+1}/{len(prospects)}] [{icon}] {label} → {result.verdict} ({result.score}/10)")

        except anthropic.APIError as e:
            print(f"  [{i+1}/{len(prospects)}] [!] {label} → API error: {e}")
            prospect.score = 5
            prospect.verdict = "QUALIFY"
            prospect.reason = "Scoring failed — manual review needed"
            prospect.pain_angle = "analyst_bottleneck"
        except Exception as e:
            print(f"  [{i+1}/{len(prospects)}] [!] {label} → Error: {e}")
            prospect.score = 5
            prospect.verdict = "QUALIFY"
            prospect.reason = "Scoring failed — manual review needed"
            prospect.pain_angle = "analyst_bottleneck"

        # Rate limit: 0.5s between calls
        if i < len(prospects) - 1:
            time.sleep(0.5)

    # Summary
    targets = sum(1 for p in prospects if p.verdict == "TARGET")
    qualifies = sum(1 for p in prospects if p.verdict == "QUALIFY")
    skips = sum(1 for p in prospects if p.verdict == "SKIP")
    print(f"  [Scoring] Results: {targets} TARGET, {qualifies} QUALIFY, {skips} SKIP")

    return prospects
