---
name: cold-call-analyzer
description: "Use this skill whenever the user pastes a cold call transcript, asks to analyze a call, score a call, review call performance, or says anything like 'analyze this call', 'score this call', 'how did this call go', or 'cold call analysis'. Also trigger when a transcript is pasted with context suggesting it's from a phone call or cold outreach. This skill scores calls against the Benjamin Dennehy framework and extracts patterns for the library."
---

# Cold Call Analyzer

Analyzes cold call transcripts to score Benjamin Dennehy adherence, identify what's working, and build the pattern library over time.

## When You Receive a Transcript

### 1. Score Benjamin Adherence (X/10)

| Element | Score | What to Look For |
|---------|-------|------------------|
| Pattern interrupt | /2 | Did they use one? How did prospect respond? |
| Gave the choice | /1 | "30 seconds or hang up" - prospect felt in control |
| Pain-led not feature-led | /2 | Which pain resonated? Did they pitch before uncovering pain? |
| Objection handling (curiosity) | /2 | Challenged with curiosity vs accommodated? |
| Emotional depth reached | /2 | Surface / Moderate / Deep (see below) |
| Clean close | /1 | Push-away used? Or did they chase? |

### 2. Pain Depth Assessment

- **Surface** - Acknowledged problem exists ("yeah, that's an issue")
- **Moderate** - Gave specifics or examples ("we wait about 3 days for any report")
- **Deep** - Expressed frustration, cost, or resignation ("I'm absolutely done with it")

Deep is the goal. If the call stayed at Surface, note what question could have pushed deeper using the Emotional Grinder sequence: Elaborate > When first recognized > Actions taken > Cost/impact > Personal feelings > Resignation.

### 3. Extract for Pattern Library

**Hooks that landed:**
> "[Exact words used]" - [Their reaction]

**Objections heard:**
> "[Their objection]" - [Response given] - [Outcome]

**Pain language they used (in their words):**
> "[Their words]" - [Context]

### 4. Output Format

```
CALL: [Company] - [Title] - [Industry]
OUTCOME: [Meeting booked / Not interested / Callback / etc.]

BENJAMIN SCORE: X/10
PAIN DEPTH: Surface / Moderate / Deep

WHAT WORKED:
- [Specific moment that landed]

WHAT TO TRY NEXT:
- [One concrete adjustment for next call]

ADD TO LIBRARY:
- Hook: [phrase that landed]
- Objection: [response that worked]
- Pain language: [their words to reuse]
```

### 5. Flag These

After scoring, flag if:
- Features were pitched before pain was uncovered (Benjamin violation)
- Prospect was accommodated rather than challenged on objections
- Call targeted an AI/Data/BI title (0% conversion - should have been skipped)
- Call stayed at Surface pain depth with no attempt to go deeper
- No push-away close was attempted

### 6. Update Knowledge Base

After analysis, append the entry to `meeting-log-full.md` if it was a substantive call (meeting booked, strong insights, or notable pattern). Update `meeting-patterns.md` if new signals, objections, or personas emerged.
