import json
import re
import time
from typing import List

import anthropic

from config import CLAUDE_MODEL
from models import Prospect


MESSAGING_SYSTEM_PROMPT = """You are Tom Pickett, Head of GTM at Milo. You write LinkedIn connection requests and DMs.

About Milo: ChatGPT for business, but safe. Lets business users ask questions about their data in plain English and get answers with explanations in seconds. Connects to BigQuery, Snowflake, Salesforce.

YOUR VOICE:
- Direct, no corporate speak, slightly challenging, curious not pushy
- Short sentences. Full stops not commas.
- Benjamin Dennehy style: challenge rather than accommodate
- Reference their specific role and likely pain
- End with a question, never a CTA or pitch
- NEVER mention Milo, NEVER pitch features, NEVER use words like "solution" or "platform"
- Lead with THEIR pain, not your product

PAIN ANGLES (use the one specified):
- analyst_bottleneck: "Waiting days for answers that should take minutes." Reference management meetings where they can't answer questions live.
- chatgpt_security: "Staff uploading company data to personal ChatGPT accounts." Reference the fear of what's already been shared.
- bi_failure: "Power BI dashboards gathering dust." Reference the gap between what BI tools promise and what teams actually use.
- manual_reporting: "20-30 KPIs pulled manually every month from different systems." Reference the wasted hours stitching reports together.
- ip_risk: "Sensitive data uploaded to ChatGPT — can't patent it anymore." Reference IP exposure risk.

CUSTOMER QUOTES you can weave in naturally (don't force them):
- "I just want to answer questions live in management meetings instead of waiting a week" — a COO we work with
- "They're not supposed to be, but they are" — on staff using ChatGPT at work
- "I'm done. I'm absolutely done." — on manual data pulling
- "We spent a huge amount on Power BI. Then required constant manual updating and everything was just horrible." — a COO at a retail company

PUSH-AWAY STYLE (for pushaway_message):
- Start with a deliberate pull-back: "Probably not relevant to you but...", "This likely doesn't apply...", "I might be wrong here but...", "You've probably already solved this..."
- Make them feel like you're walking away, not chasing
- Slightly challenging — implies they might not be good enough to have this problem
- Still end with a question

Generate EXACTLY this JSON structure, nothing else:
{
    "connection_message": "<under 300 characters>",
    "pushaway_message": "<under 300 characters>",
    "followup_dm": "<under 500 characters>"
}

CHARACTER LIMITS ARE STRICT. Count carefully. Connection request and push-away MUST be under 300 characters. DM under 500."""


def _build_messaging_prompt(prospect):
    """Build the user prompt for message generation."""
    return f"""Generate messages for:
Name: {prospect.first_name}
Title: {prospect.title}
Company: {prospect.company}
Company Size: {prospect.company_size or 'Unknown'} employees
Industry: {prospect.industry or 'Unknown'}
Pain angle: {prospect.pain_angle}
Score reason: {prospect.reason}
Headline: {prospect.headline or prospect.title}

Remember: connection_message and pushaway_message MUST be under 300 characters each. followup_dm MUST be under 500 characters. Count the characters."""


def _parse_messaging_response(text):
    """Extract message dict from Claude's response. Returns dict with 3 keys."""
    # Try direct JSON parse
    try:
        data = json.loads(text.strip())
        return _validate_messages(data)
    except (json.JSONDecodeError, KeyError):
        pass

    # Try markdown code block
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(1))
            return _validate_messages(data)
        except (json.JSONDecodeError, KeyError):
            pass

    # Try finding any JSON object
    match = re.search(r"\{[^{}]*\"connection_message\"[^{}]*\}", text, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(0))
            return _validate_messages(data)
        except (json.JSONDecodeError, KeyError):
            pass

    print(f"    [!] Could not parse messaging response.")
    return None


def _validate_messages(data):
    """Validate and truncate messages to character limits."""
    result = {
        "connection_message": data.get("connection_message", ""),
        "pushaway_message": data.get("pushaway_message", ""),
        "followup_dm": data.get("followup_dm", ""),
    }

    # Truncate at last complete sentence before limit
    limits = {
        "connection_message": 300,
        "pushaway_message": 300,
        "followup_dm": 500,
    }

    for key, limit in limits.items():
        msg = result[key]
        if len(msg) > limit:
            # Find last sentence ending before limit
            truncated = msg[:limit]
            last_period = truncated.rfind(".")
            last_question = truncated.rfind("?")
            cut_point = max(last_period, last_question)
            if cut_point > limit // 2:
                result[key] = msg[:cut_point + 1]
            else:
                result[key] = truncated.rstrip() + "..."
            print(f"    [!] {key} truncated from {len(msg)} to {len(result[key])} chars")

    return result


def generate_messages(client, prospect):
    """Generate all 3 messages for a single prospect. Updates prospect in-place."""
    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=500,
        system=MESSAGING_SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": _build_messaging_prompt(prospect)}
        ],
    )

    text = response.content[0].text
    messages = _parse_messaging_response(text)

    if messages:
        prospect.connection_message = messages["connection_message"]
        prospect.pushaway_message = messages["pushaway_message"]
        prospect.followup_dm = messages["followup_dm"]

    return prospect


def generate_messages_batch(api_key, prospects):
    """
    Generate messages for all prospects with score >= 7.
    Updates prospects in-place. Returns the full list.
    """
    eligible = [p for p in prospects if p.score and p.score >= 7]

    if not eligible:
        print("\n[Messages] No prospects scored 7+ — skipping message generation.")
        return prospects

    client = anthropic.Anthropic(api_key=api_key)

    print(f"\n[Messages] Generating outreach for {len(eligible)} prospects (score 7+)...")

    success = 0
    for i, prospect in enumerate(eligible):
        label = f"{prospect.full_name} ({prospect.title})"
        try:
            generate_messages(client, prospect)
            if prospect.connection_message:
                success += 1
                print(f"  [{i+1}/{len(eligible)}] {label} — done")
            else:
                print(f"  [{i+1}/{len(eligible)}] {label} — parse failed")

        except anthropic.APIError as e:
            print(f"  [{i+1}/{len(eligible)}] [!] {label} — API error: {e}")
        except Exception as e:
            print(f"  [{i+1}/{len(eligible)}] [!] {label} — Error: {e}")

        # Rate limit: 0.5s between calls
        if i < len(eligible) - 1:
            time.sleep(0.5)

    print(f"  [Messages] Generated messages for {success}/{len(eligible)} prospects")

    return prospects
