# Meeting Insights - Full Call Log

**Purpose:** Complete write-ups of all 11 analyzed calls with full context, quotes, signals, and assessments. Only load this file when processing a new transcript, doing deep analysis on a specific deal, or reviewing a customer's history.

**For patterns and quick reference:** See `meeting-patterns.md` (load by default).

**Last Updated:** 26 February 2026

---

## Call #1: Switch365

**Date:** 26 November 2025
**Person:** Ian (Head of Operations), Andy (CEO - mentioned)
**Outcome:** POC agreed - but weak fit

### Company Context
- Business: Call center / sales operation
- Tech Stack: Custom CRM (T-SQL), Tonx dialer (PostgreSQL), Python, third-party dashboards
- Current AI: Personal ChatGPT accounts (Ian pays £20/month personally)

### Why They Took The Call
LinkedIn post on ChatGPT security "struck a chord" - internal conversation already happening about data risk.

### The Real Problem
- **Security concern is primary** - employees using personal ChatGPT with company data
- **NOT looking for reporting** - "We've kind of got what we need"
- Ian: "It is more of a security thing really than actually, we need you guys to go and build a load of reporting"

### Key Objection
**Losing ChatGPT history:** "I've got all my history of everything that it's learned over the last year. As soon as I turn that off, I'm starting from scratch."

### Assessment
**Weak fit.** Primary driver is "lock down ChatGPT" not "get insights from data." If they just want secure ChatGPT without the BI layer, Copilot or enterprise ChatGPT might be sufficient.

### Lesson
**Security-only driver without BI need = weak fit.** Probe whether they actually want insights or just security.

---

## Call #2: Toy Manufacturer (David)

**Date:** 27 November 2025
**Person:** David (Supply Chain/Operations - NEW TO ROLE)
**Outcome:** Did not convert

### Company Context
- Business: Toy manufacturer, imports from China, sells UK/Europe/North America
- Tech Stack: Microsoft Business Central (single ERP)
- Data Quality: Good - "issue doesn't tend to be data integrity"
- Current Solution: Hired data analyst 3 months ago, building Power BI

### Why They Took The Call
- New to role (4 weeks)
- Knows Power BI is "old hat"
- "More of a look see in terms of what you guys do"

### Why It Didn't Convert
1. **New to role** - Can't champion anything yet
2. **Exploratory mindset** - "If it forms part of our plan"
3. **Already solving it** - Data analyst hired 3 months ago "making good progress"
4. **No authority** - "I just need to discuss it internally"

### Disqualification Signals (Missed)

| Signal | What He Said | Should Have Asked |
|--------|--------------|-------------------|
| New to role | "About four weeks now" | "Do you have authority to bring in new tools?" |
| Already solving | "Employed data analyst 3 months ago" | "What's still not working?" |
| Exploratory | "More of a look see" | "What would make this a priority?" |

### Assessment
**Looks like ICP, isn't ready to buy.** Should have been nurtured, not POC'd.

### Lesson
**"New to role" + "Just exploring" + "Already have someone working on it" = Nurture, don't pursue.**

---

## Call #3: KFC Franchise (Dave)

**Date:** 3 December 2025
**Person:** Dave (Operations/Information Systems)
**Outcome:** Second meeting booked - Stalled (jury duty) - Reconnected Feb 2026, next meeting March

### Company Context
- Business: KFC Franchisee - 23 stores
- Tech Stack: Excel (primary), SAGE for invoices, KFC Atlas portal (read-only)
- Moving to larger franchise in February 2026

### Why This Is Strong Fit
1. **Operational leader with P&L responsibility** - Franchise = makes/loses money directly
2. **Can't build internally** - "Excel based, nothing particularly technical"
3. **Multi-location complexity** - 23 stores, needs pattern recognition
4. **Clear articulated pain** - Knows exactly what he wants
5. **Self-aware** - "I need to make sure I don't end up that dinosaur"
6. **Buying trigger** - Moving to bigger role, "planning seeds now"

### The Pain (His Words)
- "Every manager plus me, sitting down and trawling through the same data"
- Wants "action driven rather than data mining"
- "By the time you get the answer, you've already moved on"
- "I'm done" with manual process

### What He Wants Milo To Do
1. Morning prompts: "Morning Dave, yesterday these stores had issues..."
2. Daily performance: "Which of my worst three stores yesterday?"
3. Pattern recognition: Surface unknowns
4. Push notifications: WhatsApp alerts on thresholds
5. Monthly reporting: Summary for store manager meetings

### QSR-Specific Insight
KFC chicken takes 20 minutes to cook (vs McDonald's 3-minute burgers). If forecast is wrong at noon, stockout cascade lasts until 8pm. Data problems = operational disasters.

### Why It Stalled
- Two-week gap to second meeting (too long)
- Jury duty interrupted momentum
- Classic pattern: strong call - life happens - dies

### Recovery Strategy
He's moving to larger franchise in February. Reconnected February 2026 - next meeting scheduled for March.

### Assessment
**Strong fit. Should convert.** Re-engaged February 2026.

---

## Call #4: See Tickets

**Date:** 13 January 2026
**Person:** Rob Wilmshurst, Group CEO
**Outcome:** Lost - POC ran but parent company blocked deal from proceeding

### Company Context
- Business: Ticketing platform (competitor to Ticketmaster)
- Tech Stack: Postgres
- Decision Maker: CEO directly engaged

### Why This Is Strong Fit
1. **CEO on the call** - Budget holder, can make decisions
2. **Specific differentiation use case** - Client-facing analytics as competitive advantage
3. **No objections** - Actively looking for solution
4. **Data architect involved** - Technical validation happening in parallel

### The Pain
- Analyst team drowning in client requests
- Can't provide real-time client-facing analytics
- Ticketmaster competition pressure

### Key Quote
> "If we can put client-facing analytics in front of our customers, that's a differentiator against Ticketmaster"

### Follow-Up
- Friday 17 Jan, 11am - setup call with Rob + data architect
- Postgres connection setup
- NDA signed via DocuSign
- Commercial: £1,490/month

### Assessment
**Was a strong fit locally.** CEO engaged, specific use case, no blockers at the local level. Ultimately lost because parent company blocked them from proceeding — a governance/authority issue, not a product or champion issue.

### Lesson
**CEO + specific differentiation use case + no objections = fast mover.** But also: **validate parent company governance early.** Local buying authority doesn't matter if a parent company can veto. Add "who needs to approve this?" to early qualification.

---

## Call #5: Kellanova

**Date:** 13 January 2026
**Person:** Ankur Shah, VP BI/Analytics
**Outcome:** NURTURE - Post-M&A paralysis (Mars acquisition Dec 2025)

### Company Context
- Business: CPG (snacks/cereals - Pringles, Cheez-It, etc.)
- Recent Event: Mars acquired Kellanova Dec 11, 2025 ($35.9B)
- Current State: Organization in flux, budget decisions on hold

### Why It Didn't Convert
1. **Post-M&A paralysis** - Mars acquisition creating uncertainty
2. **Budget frozen** - No new vendor decisions during integration
3. **Title red flag** - VP BI/Analytics (0% conversion title)

### Key Quote
> "Every meeting is derailed with data questions nobody can answer in real time"

### Follow-Up
- Check back Q2 2026 when integration settles
- Send CPG-focused deck via LinkedIn for future reference

### Assessment
**Pain is real, timing is wrong.** Post-M&A companies are frozen. Nurture for 6+ months.

### Lesson
**Recent acquisition = automatic nurture.** Also confirms VP BI/Analytics title pattern - even with genuine pain, wrong persona.

---

## Call #6: Orbian

**Date:** 21 January 2026
**Person:** Abner (Business & Change Manager)
**Outcome:** No go (Feb 2026) - POC initially agreed but did not proceed after Operations MD presentation

### Company Context
- Business: Supply chain finance (supplier payments)
- Tech Stack: In-house Java system, SAP ECC 6, Salesforce, Monday.com, Power BI
- Data State: No data management pillars, reactive approach, data lives in different systems
- Current AI: Personal ChatGPT usage ("guilty of it")

### Why They Took The Call
Cold call converted. Interested in the data + AI combination.

### The Pain (His Words)
1. **IT ticket bottleneck** - "Two days minimum" for any data request, IT capacity maxed out
2. **Data scattered across systems** - "No one place where it comes together"
3. **Reactive not strategic** - "We've been very reactive"
4. **Power BI limitations** - "Can't do comparisons quarter by quarter"
5. **Basic analysis only** - Monthly reports are "very basic"
6. **ChatGPT guilt** - Using it but knows it's a risk

### What He Wants Milo To Do
1. Unified data access without IT tickets
2. Replace/complement Power BI for ad-hoc questions
3. Approved AI agent for the organization
4. Potentially white-label for external suppliers/clients

### Key Quotes
> "We open an IT ticket and request the data... it could be two days at minimum. It's never immediate."

> "I shouldn't say, but quite guilty of it. Sometimes it's just that tool that makes it more effective and efficient."

> "There's an opportunity for us to get an AI agent approved in the organization, which brings some comfort that we're not sneaking information there."

> "I don't think we appreciate how important data can be right now. We've been very reactive."

### Follow-Up
- Send deck before 29 Jan
- POC pricing: £250-500 for 2-week proof of concept
- Full pricing: ~£1,400/month
- Meeting with Operations MD: 29 January 2026

### Assessment
**Was a strong fit on paper.** Classic Milo buyer signals: operational role, IT bottleneck, ChatGPT guilt, reactive data culture, Power BI frustration. Did not proceed after Operations MD presentation — no go as of Feb 2026. Nurture.

### Lesson
**"Sneaking information" = gold framing.** The security angle isn't about compliance - it's about giving people permission to use AI without guilt. Also: champion engagement doesn't guarantee deal — budget holder buy-in is the gate.

---

## Call #7: TicketShare

**Date:** 29 January 2026
**Person:** Dom (VP of Solutions, 4 months in role)
**Outcome:** Partnership exploration - follow-up with technical team scheduled

### Company Context
- Business: Ticketing for cultural institutions (museums, immersive experiences)
- Tech Stack: Moving to Snowflake, currently have old internal reporting tools
- Data State: Per-client siloed data, raw-level data in Snowflake
- Team: Engineering and data team, technical company at heart

### The Conversation
Partnership exploration, not pain discovery. Dom is thinking about:
1. Internal use for TicketShare
2. Self-serve analytics for their clients
3. Potentially bundling Milo into their platform
4. White-label possibility

### Key Questions From Dom
> "If the data comes in and it's not in an optimal format... how much does that impact the quality of the results?"

> "Do you guys have any other engagements where it's like, we license this out as a platform for another platform that can bundle it together?"

### Pricing Discussed
- Full: $2,100/month
- POC: $1,500 USD for 3-4 weeks

### Internal Debrief Notes
Tom's feedback to Liam:
- Didn't do proper upfront contract
- Need to breathe more, not rush
- Demo looked too rehearsed
- Should have pressed harder on emotional pain

### Assessment
**Partnership exploration, not a direct sale.** White-label angle interesting (second ticketing company showing interest).

### Lesson
**Partnership conversations need different qualification.** "How can I offer this to MY customers" is different from "how does this solve MY pain."

---

## Call #8: Karsten (via Evolution Partnership)

**Date:** 29 January 2026
**Source:** Evolution partnership (BeNeLux reseller)
**Attendees:** Doron (Head of IT), Daniel (IT Manager), Martin (Product Owner, Business Central/Power BI), Ton (Evolution)
**Outcome:** Evaluating internally - will come back "quite quickly"

### Company Context
- Business: Dutch company, ~200 employees
- Tech Stack: Business Central (financial/logistics), Power BI, internal tooling
- Current AI: "A lot of AI tools being used across the board... but in infancy state"

### Pain Points
- Dashboards aren't self-serving - all developer-created
- Martin is single point for all dashboard changes
- Quality inconsistency across teams

### Key Quotes
> "Try to make Karsten a future proof digital organization... working on improving data quality, translating data into actionable insights." — Doron

> "Having an environment where people can gain insights themselves. So democratize and self service BI. And potentially also agentic BI." — Doron

> "Looks really promising. Looks good." — Doron (after demo)

### Pricing Discussed (Evolution Partnership Rates)
- Pilot: €2,500/month for up to 3 data sources
- Enterprise: ~€3,000/month for company this size

### Assessment
**Warm lead via Evolution partnership.** Strategic modernization buyer, not pain-driven. Three stakeholders aligned.

### Lesson
**Partnership-sourced leads come warmer.** For strategic/transformation buyers, focus on capability demonstration and future vision rather than emotional pain discovery.

---

## Call #9: Coolr

**Date:** 16 February 2026
**Person:** Alex (COO, 6 months in role)
**Source:** Email sequence (booked by Liam)
**Outcome:** POC verbally agreed - needs internal approval + reference call first

### Company Context
- Business: Social media agency, ~150 people, ~£20M revenue
- Location: London (Canary Wharf)
- Tech Stack: HubSpot, Productive, Hi Bob, Team Tailor, SharePoint, spreadsheets
- Failed Investment: Power BI - abandoned after constant manual updating
- Current AI: Staff using personal ChatGPT/Claude ("they're not supposed to be, but they are")
- No in-house data/IT team

### The Pain (His Words)
1. **Systems don't talk to each other** - HubSpot, Productive, Hi Bob, Team Tailor, SharePoint all siloed
2. **Power BI failure** - "Spent a huge amount of money... constant manual updating"
3. **No data team** - "I'm herding the cats... nobody owning tech strategy"
4. **Manual board reporting** - core business metrics from different departments
5. **Manual revenue tracking** - spreadsheets to finance to systems
6. **ChatGPT security** - staff using personal accounts
7. **SharePoint mess** - "our data on the back end of stuff is horrible"

### What He Wants Milo To Do
1. Board reporting - push a button, all department metrics
2. CEO self-service - interrogate data without "messing up a formula"
3. Leading/predictive metrics
4. Replace failed Power BI
5. Department-level dashboards with role-based access

### Key Quotes
> "It's like having a data engineering team. I used to have a bloke who was proper geeky and he did all this stuff for me. So this is like having that but better, isn't it?"

> "They're not supposed to be, but they are." (on staff using ChatGPT)

> "I'd like to get to a go/no-go as quickly as possible."

### Pricing Discussed
- POC: £1,000 for 2-4 weeks
- Full: £1,500/month
- No pushback

### Concerns to Watch
- No single tech admin - connector setup may be slower
- Internal availability - "quite good at saying we want to go ahead... then nobody's available"
- Data quality - "our data on the back end is horrible"

### Follow-Up Actions
- Set up reference customer call
- Send POC requirements email
- Liam to correspond
- Potential in-person meeting in London

### Assessment
**Strong fit.** Classic Milo buyer: COO with no data team, multiple disconnected systems, failed Power BI, ChatGPT security concern, budget cycle timing.

### Lesson
**Failed Power BI = best pre-qualification signal.** Budget exists, need validated, alternative didn't work. Email campaigns CAN work when timing is right. COO at 6 months is sweet spot.

---

## Call #10: Kromek

**Date:** 12 February 2026
**Person:** Ben Cantwell (senior commercial/operations)
**Source:** Cold call converted
**Outcome:** Follow-up call 27 Feb 10am

### Company Context
- Business: Radiation and biological detectors, PLC on AIM
- Tech Stack: Sage, HubSpot, Microsoft 365, ISO system on SharePoint, isolated production/furnace networks
- Internal AI: Data division (4-5 people) building AI for cancer detection and biological threats (product AI, not business BI)
- Current AI for Business: Microsoft Copilot (encouraged), personal ChatGPT (discouraged)
- Security: Cyber Essentials Plus, US Defense standards
- Creates significant IP (patents)

### The Pain (His Words)
1. **Manual record trawling** - "would really help"
2. **Can't get insights beyond graphs** - "What can we infer beyond just plotting a graph?"
3. **Manual KPI reporting** - 20-30 KPIs across company, monthly
4. **Disparate data sources** - Sage, HubSpot, SharePoint, production, furnace data
5. **ChatGPT/IP risk** - "Can't get a patent on it anymore"
6. **Copilot as glorified search engine** - Not connected to business data
7. **Non-technical staff locked out** - "people who aren't mathematically savvy"

### Key Quotes
> "What I don't want happening is people uploading something to ChatGPT or whatever, and then it's out there because we can't get a patent on it anymore."

> "What are the trends that we're seeing and what can we infer from this information beyond just plotting a graph?"

> "Different groups are having to report certain amount of data every month. And if that were able to be automated a bit more, that would save a lot of time."

### Signals
- Positive: Interested in data siloing, price OK, agreed to follow-up, will send security standards, wants to bring decision makers
- Concern: Not budget holder, defense compliance could block, isolated networks, PLC procurement process

### Assessment
**Interested but longer sales cycle.** IP/patent angle is strong variant of security. Defense compliance may genuinely block. Expect 2-3 month cycle minimum.

### Lesson
**IP/patent protection is the sharpest security angle.** "Can't get a patent on it anymore" is more concrete than generic data security. Defense compliance can be real blocker - get specific standards early.

---

## Call #11: Black Sheep Coffee

**Date:** 13 February 2026
**Type:** POC Kickoff / Product Demo & Technical Discussion
**Source:** Email sequence (booked by Liam)
**Attendees:** Gabby (Head of Data & Analytics, 3 years), Dylan (Data Analyst), Amy (Data Engineer, 1 month)
**Outcome:** POC confirmed - NDA and legal review in progress

### Company Context
- Business: Coffee chain
- Tech Stack: Microsoft SQL Server, Power BI (semantic models)
- Data State: Hundreds of datasets, thousands of tables
- Team: Data & Analytics team (Gabby, Dylan, Amy)

### Implementation Plan
- Database: Microsoft SQL Server direct connection
- Business logic: Export Power BI semantic models
- Access control: Dedicated database user with restricted table access

### User Rollout Plan
1. **Phase 1:** Gabby, Dylan, Amy (data team testing)
2. **Phase 2:** "Chaos agents" - non-technical but inquisitive users
3. **Phase 3:** Gradual scaling

### Signals
- Positive: POC confirmed, technically engaged, "chaos agents" terminology shows understanding
- **Concern: ALL attendees are Data/Analytics titles** - 0% conversion title category
- **Concern: No business user on kickoff** - same pattern as Raptive
- Concern: Amy 1 month in role, COO approval needed but not on call, legal review bottleneck

### Follow-Up Actions
- Tom to send NDA and POC documentation
- Dylan to coordinate legal review and COO approval
- Technical setup calls once NDA cleared

### Assessment
**POC is moving, but user group is a red flag.** Every person on this call is Data/Analytics. The "chaos agents" rollout (phase 2) is the critical success factor. If only the data team uses Milo during POC, this becomes a technical evaluation - the same pattern that killed Raptive. The COO needs to see value early.

### Lesson
**POC user group matters more than POC agreement.** Data teams evaluate technically, business users evaluate practically. Push hard to get "chaos agents" in week 1, not phase 2.

---

## To Add More Entries

When you have a new transcript, paste it and extract:
- Key quotes
- Pain points identified
- Objections and how handled
- Buying signals / red flags
- Assessment and lessons
- Update to patterns

Then add the summary here (not the raw transcript - too long and not useful once processed).
