---
name: meeting-processor
description: "Use this skill whenever the user pastes a meeting transcript, discovery call notes, POC check-in notes, or customer meeting recording summary. Also trigger when the user says 'process this meeting', 'log this call', 'extract insights from this transcript', or pastes text that looks like a Granola transcript or meeting notes. This skill extracts structured insights, produces a HubSpot-ready note, and updates the knowledge base."
---

# Meeting Processor

Processes meeting transcripts (from Granola, manual notes, etc.) into structured insights, HubSpot-ready notes, and knowledge base updates.

## Required Info

If not clear from the transcript, ask:
1. **Meeting type:** Discovery / Secondary / POC Check-in / Partnership
2. **Company name**
3. **Attendees and titles**

## What to Extract

### Core Fields

| Field | Value |
|-------|-------|
| Date | |
| Company | |
| Person | Name, Title |
| Type | Discovery / Secondary / POC Check-in / Partnership |
| Source | Cold call / Email sequence / Inbound / Partnership / Referral |
| Outcome | |

### Insights

1. **Key Quote** - One verbatim quote (max 2 sentences) that captures their pain or situation
2. **Pain Points** - In their words, not ours. What's broken and how it feels.
3. **Objections** - Exact language + how handled + outcome
4. **Competitors/Existing Tools** - What they mentioned, what they said about it
5. **Buying Signals** - Interest level, timeline, budget discussed, next step agreed
6. **Red Flags** - Why this might not close
7. **Follow-Up** - What was agreed, who owns it, when

## Output

### 1. HubSpot Note (Copy-Paste Ready)

```
MEETING: [Company] - [Date]
Type: [Type] | Source: [Source] | Attendees: [Names + Titles]

KEY POINTS:
- [Bullets - max 5]

PAIN: "[Best quote]"

NEXT: [Action] - [Owner] - [Date]

FLAGS: [If any]
```

### 2. Knowledge Base Updates

**Always read `meeting-patterns.md` first** to check existing patterns. Then:

- Add new entry to `meeting-log-full.md` following the established format (see existing entries for structure)
- Update `meeting-patterns.md` if new buying signals, disqualification signals, objections, or quotes emerged
- If an active project exists in `projects/[company]/`, update `context.md`

### 3. Flags to Watch and Raise

- Champion cooling - engagement dropping, responses slowing
- Technical blocker - needs Philip for data connection or security question
- Decision maker absent - champion engaged but budget holder not involved
- Timeline slipped - agreed dates missed without explanation
- Builder signals - engineering team, internal AI projects, "we could build this"
- Data/Analytics-only POC team - same pattern that killed Raptive. Push for business users.
- Title red flag - AI/Data/BI title as primary contact (0% conversion)

### 4. Cross-Reference

After processing, check:
- Does this company match ICP signals from `meeting-patterns.md`?
- Are there disqualification signals that should flag this as nurture-only?
- Does the pain language match anything in the quote bank worth adding?
- Is the POC user group right? (Business users, not just data team)
