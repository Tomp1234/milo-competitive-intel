# Session Start Sanity Check

## Overview

Quick health check to run at the start of each working session. Catches stale docs, missing files, upcoming deadlines, and context from recent work.

---

## How to Use

Say: "Session check" or "Start session" or "What did I miss?"

---

## What I Check

### 1. File Health

**Required project files:**
- `CLAUDE.md` - Master operating doc
- `gtm-context.md` - Current state snapshot
- `icp.md` - ICP with conversion data
- `gtm-plan.md` - Strategy and targets
- `meeting-patterns.md` - Buying signals, objections, quote bank (lean reference)
- `meeting-log-full.md` - Full call write-ups (deep analysis only)
- `linkedin-patterns.md` - Winning formulas, hooks, what works/doesn't (lean reference)
- `linkedin-log-full.md` - All posts with performance data (deep analysis only)

**Required skills** (in `/mnt/skills/user/`):
- `cold-call-scripts` - Persona-specific scripts
- `cold-call-analyzer` - Call scoring framework
- `meeting-processor` - Transcript processing
- `linkedin-content` - Post creation with proven formulas
- `poc-management` - POC cadence, chaos agents, red flags
- `apollo-hubspot-workflow` - Prospecting and HubSpot tagging

**Check for:**
- Missing files → Flag immediately
- "Last Updated" dates → Flag if >7 days old
- Conflicts between docs (e.g., different targets, outdated team info, title targeting contradictions)

### 2. Memory vs Docs Alignment

Compare what's in my memory context against project files:
- Team changes (new hires, departures)
- Target numbers (Q1 goals, pipeline)
- Customer status (paying, POC, churned)
- Key dates (events, deadlines)

Flag any mismatches.

### 3. Current Priorities

Pull from CLAUDE.md "This Week's Focus" section:
- Priority 1, 2, 3
- Blockers/Flags
- Upcoming deadlines

### 4. POC/Customer Status

Quick scan of POC tracker:
- Any decisions due this week?
- Trust scores changed?
- Risk flags?

### 5. Recent Activity

Check `meeting-patterns.md` and `gtm-context.md`:
- Any new calls logged since last session?
- Anything left unfinished?
- Any flags or follow-ups noted?

---

## Output Format

```
SESSION CHECK - [Date]

📁 FILES
✅ All present | ⚠️ Missing: [file] | 🔄 Stale: [file] (X days)

📅 THIS WEEK
• [Priority 1]
• [Priority 2]
• [Key deadline/event]

🎯 PIPELINE
• [X] POCs active
• Decisions due: [Company] by [date]
• ⚠️ [Any risk flags]

💬 RECENT ACTIVITY
• [Latest calls/meetings logged]
• [Any unfinished items]

⚠️ FLAGS
• [Any conflicts between memory and docs]
• [Anything that needs attention]
```

---

## When to Run

- **Every session start** - Default, takes 30 seconds
- **After extended break** - Definitely run it
- **If something feels off** - Quick sanity check

---

## If Files Missing

1. Flag for rebuild from CLAUDE.md (source of truth)
2. Offer to recreate from available context

---

## Maintenance

When session check reveals stale docs:
- Offer to update them
- Don't just flag - fix if possible

When memory conflicts with docs:
- Docs are source of truth
- Update memory edits if needed

---

## Example Output

```
SESSION CHECK - 17 February 2026

📁 FILES
✅ All present, CLAUDE.md updated today

📅 THIS WEEK
• Book 4 meetings/week (pipeline math)
• See Tickets POC - monitor usage
• Coolr - send POC requirements, reference call
• Black Sheep Coffee - NDA/legal, push for business users
• Kromek follow-up 27 Feb

🎯 PIPELINE
• 4/12 Q1 deals closed (BetGames, Perlas, Orbio, 7Bet)
• 3 POCs active (See Tickets, Aardvark, Black Sheep Coffee)
• Pipeline: Coolr, Kromek, Karsten, TicketShare
• ⚠️ Aardvark blocked on security cert

👥 TEAM
• Liam: Fully ramped, 400-500 calls/week, booking meetings via email
• Christina: Events & LinkedIn support

⚠️ FLAGS
• Gmail signup decision unresolved
```

---

## Trigger Phrases

Any of these should trigger the check:
- "Session check"
- "Start session"
- "What's the status?"
- "What did I miss?"
- "Catch me up"
- "Morning check"

---

*Created: 9 January 2026*
