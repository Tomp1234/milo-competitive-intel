---
name: poc-management
description: "Use this skill whenever the user is managing a POC (proof of concept), checking in on a trial customer, reviewing POC health, planning a POC cadence, deciding whether to escalate a POC, or discussing activation signals. Also trigger when the user mentions a specific POC account by name (See Tickets, Coolr, Black Sheep Coffee, Aardvark, etc.) in the context of usage, check-ins, or conversion. This skill provides the playbook for turning POCs into paying customers, including chaos agent activation and red flag detection."
---

# POC Management Playbook

The goal of every POC is to reach one bar: **the customer can answer questions live in management meetings instead of waiting a week for an analyst.** That's what Greta at Perlas described, and it's what separates POCs that convert from POCs that die.

## The Core Lesson

Technical-only POCs fail. Raptive had 3-4 internal AI projects and a strong engineering team - their POC was a technical evaluation, not a business value proof. The data team stress-tested queries. No business user ever asked a real question. It died.

Black Sheep Coffee is showing early signs of the same pattern - all Data/Analytics titles on the kickoff, business users scheduled for "phase 2." Phase 2 often never comes.

The fix: get non-technical business users asking real questions in week 1, not later.

---

## POC Phases

### Week 0: Setup (Before Data Is Connected)

- Confirm POC scope and success criteria with the champion
- Identify at least 2-3 non-technical "chaos agents" who will use Milo during the POC
- Get chaos agents named and committed before data connection starts
- Set check-in cadence (weekly for active POCs)
- Philip handles data connection (~1 week typical)

**The chaos agent conversation:** "For this POC to actually prove value, we need a couple of people outside the data team using it - someone who normally waits for reports or asks the analysts for answers. Who in your org is most frustrated by how long it takes to get data? That's who we want in week 1."

### Week 1: Activation

- Data connected, basic validation done with technical team
- Chaos agents get access and a 15-minute orientation ("just ask it questions like you'd ask an analyst")
- First check-in call: focus on whether chaos agents have logged in and asked real questions
- Watch for first "aha moment" - someone gets an answer they'd normally wait days for

**What good looks like:** A non-technical user asks a real business question unprompted and gets a useful answer. They tell someone about it.

**What bad looks like:** Only the data team has logged in. They're testing edge cases and querying wrong tables. No business user has touched it.

### Week 2: Momentum

- Second check-in: focus on usage breadth, not just depth
- Are multiple people using it? Are questions getting more sophisticated?
- Any usage without prompting? (Someone opened it on their own, not because you asked)
- Champion sharing results or screenshots internally?
- Start documenting specific questions answered and time saved

**What good looks like:** Usage spreading beyond initial group. Someone asks a question in a meeting and Milo answers it. Champion mentions it in a team standup or Slack.

**What bad looks like:** Only original users logging in. Usage flat or declining. Champion going quiet on responses.

### Week 3-4: Conversion Decision

- Third check-in: shift to value conversation, not technical
- Present back: "Here's what your team asked, here's what they would have waited for, here's the time saved"
- Push for decision: "Based on what you've seen, is this something you want to keep?"
- If positive: transition to commercial discussion
- If lukewarm: diagnose what's missing (usually: wrong users, data quality, or champion cooling)

---

## Check-In Structure

Keep check-ins short (15-20 mins) and focused. The agenda is always:

1. **Usage update** - Who's using it? How often? What are they asking?
2. **Wins** - Any moments where Milo answered something that would have taken days?
3. **Issues** - Anything broken, confusing, or frustrating?
4. **Next step** - What needs to happen before next check-in?

Ask the champion directly: "On a scale of 1-10, how confident are you that this becomes a permanent tool?" Anything below 7 needs diagnosis.

---

## Chaos Agent Activation

Chaos agents are non-technical but inquisitive business users who will test Milo with real questions - not stress-test queries, but actual "I need this for my meeting tomorrow" questions.

### Who Makes a Good Chaos Agent
- Operations managers who run weekly team meetings
- Sales leaders who need pipeline answers fast
- Finance people who build board packs from multiple systems
- Anyone who currently Slacks the BI team with "can you pull this?"

### Who Does NOT Make a Good Chaos Agent
- Data analysts (they evaluate technically, not practically)
- Engineers (they'll try to break it, not use it)
- Anyone whose job Milo could threaten (they'll look for reasons to reject it)

### How to Get Them In

The champion needs to introduce chaos agents, not you. Frame it as:

> "We've connected your data. The technical team has validated it works. Now we need 2-3 people from [ops/sales/finance] to try asking the questions they'd normally email the data team about. No training needed - just ask it like you'd ask a colleague."

If the champion resists ("let's wait until the data team has fully tested it"), push back gently:

> "I understand the instinct to perfect it first. But in our experience, the POCs that convert are the ones where business users see value early. The data team will always find edge cases - the question is whether the people who actually need answers are getting them."

---

## Trust Signals (Things Going Right)

| Signal | What It Means |
|--------|---------------|
| Usage without prompting | Users coming back on their own, not because you asked |
| Questions getting more sophisticated | They're exploring, not just testing |
| Expanding to new question types | Moving beyond the original use case |
| Champion sharing screenshots/results internally | Organic advocacy happening |
| "Can we add [another data source]?" | They want more, not less |
| Using it in meetings | The gold standard - answering questions live |
| Asking about pricing/terms proactively | They're planning to keep it |
| New users appearing without you adding them | Word of mouth inside the org |

## Red Flags (Things Going Wrong)

| Flag | What It Means | Action |
|------|---------------|--------|
| Only data team using it | Technical evaluation, not business proof | Push for chaos agents immediately |
| Champion going quiet | They've lost interest or hit a blocker | Direct outreach: "Hey, noticed things have gone quiet - is something off?" |
| Usage dropping week over week | Novelty wore off, value not proven | Diagnose: wrong users? wrong data? wrong questions? |
| "We need more time" | Stalling, often means it's not working | Pin down what specifically needs more time and set a deadline |
| Data quality complaints dominating | The conversation is about setup, not value | Fix data issues fast (Philip), but refocus on business questions |
| "The team is busy right now" | Deprioritised, momentum lost | Suggest a specific 15-min session to re-engage |
| Only one person using it | Single point of failure - if they leave or get busy, POC dies | Get at least 2-3 active users |
| Asking about technical architecture more than business value | Builder evaluation mindset | Flag as potential builder company, check ICP fit |

---

## Escalation Triggers

Escalate to Andy or flag in weekly review when:

1. **Champion has gone silent for >5 business days** during active POC
2. **Zero chaos agent usage after week 1** - POC is on a path to fail
3. **Technical blocker Philip can't resolve in 48 hours** - data connection, security, or integration issue
4. **Budget holder hasn't been involved by week 3** - champion engaged but no commercial authority
5. **Competitor mentioned as alternative** - urgency to differentiate
6. **Security/compliance blocker** (like Aardvark's SOC/ISO or Kromek's defense standards) - needs strategic decision on timeline investment

---

## Current POC Status Reference

Check `gtm-context.md` and the customer table in `CLAUDE.md` for current POC status. Key ones to watch:

- ~~**See Tickets**~~ - Lost. Parent company blocked deal despite strong local fit and CEO champion. Validates: check parent company governance early.
- **Black Sheep Coffee** - POC Confirmed, NDA/legal in progress. Red flag: data team only so far. Push for business users.
- **Coolr** - POC Agreed. Strong fit. Send POC requirements, set up reference call.
- **Aardvark** - POC Active. Blocked on SOC/ISO certification. Not a usage problem, compliance problem.

---

## The Bar for Success

Keep coming back to Greta's quote from Perlas:

> "I just want to answer questions live in management meetings instead of waiting a week for an analyst."

If the POC hasn't reached a moment where someone answers a real question in a real meeting using Milo - the POC hasn't proven its value yet. That's the moment to engineer, not hope for.
