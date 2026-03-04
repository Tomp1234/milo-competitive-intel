---
name: apollo-hubspot-workflow
description: "Use this skill whenever the user wants to find prospects, search Apollo, add contacts to HubSpot, build a prospecting list, enrich contacts, add prospects to sequences, or set up calling tasks. Also trigger when the user says 'find me people to call', 'build a list', 'prospect for [vertical/title]', 'add to HubSpot', 'add to sequence', or asks about ICP-fit companies to target."
---

# Apollo-HubSpot Prospecting Workflow

Search Apollo → enrich → dedupe → create in HubSpot → optionally add to sequences.

**Before doing anything:** read `icp.md` for title rules, company filters, and disqualification criteria. Apply ICP rules at every step.

---

## Step 0: Pre-Flight (Run in Parallel)

1. `apollo_users_api_profile` with `include_credit_usage: true` — report remaining credits. Warn if low.
2. `hubspot__get_user_details` — confirm contact read+write permissions, get ownerId.

Stop and report if either fails.

---

## Step 1: Search (Free — No Credits)

### People Search

`apollo_mixed_people_api_search` — **does NOT return emails or phone numbers.** Must enrich in Step 3.

```
person_titles: [<target titles from icp.md>]
organization_num_employees_ranges: ["101,500"]
organization_locations: ["United Kingdom", "Germany", "France", "Netherlands"]
person_seniorities: ["director", "vp", "c_suite"]
per_page: 25
page: 1
```

Add `q_organization_keyword_tags` for verticals, `currently_using_any_of_technology_uids` for tech stack (e.g. `["bigquery", "snowflake", "redshift"]` = likely ICP fit).

For CEOs: cap `organization_num_employees_ranges` at `["101,200"]`.

### Company-First Search

`apollo_mixed_companies_search` with same ICP filters, then `apollo_mixed_people_api_search` with `organization_ids` from results.

### Post-Search Review

Apollo's `person_titles` filter is fuzzy — results may include excluded titles like "Head of Data & Innovation". Check every result against icp.md hard-exclude list.

Present as table with ICP Fit column (✅ / ⚠️ / ❌ + reason).

---

## Step 2: Dedupe (Before Spending Credits)

1. `apollo_contacts_search` with `q_keywords` = person's name. Skip if already an Apollo contact.
2. `hubspot__search_crm_objects` — search by name or email:
   ```
   objectType: "contacts"
   query: "firstname lastname"
   properties: ["firstname", "lastname", "email", "jobtitle", "company", "hs_lead_status"]
   ```
   If exists, ask user: update existing or skip?

---

## Step 3: Enrich (Costs Credits — Confirm First)

Always state credit cost and get confirmation.

- **Single:** `apollo_people_match` — include `domain` or `organization_name` for best match.
- **Batch (max 10):** `apollo_people_bulk_match` — for larger lists, batch in 10s with confirmation between.
- **Company validation:** `apollo_organizations_enrich` / `apollo_organizations_bulk_enrich` (up to 10) — verify employee count, industry, tech stack against ICP.

If no email AND no phone returned: flag as "needs LinkedIn approach", don't push to HubSpot.

---

## Step 4: Create in HubSpot

`hubspot__manage_crm_objects` — **must show proposed changes table and get user confirmation first.**

### Contact Properties
```
firstname, lastname, email, jobtitle, company
phone: direct_phone preferred, mobilephone if available
hubspot_owner_id: <see below>
lead_type: "Apollo"
hs_lead_status: "NEW"
```

### Owner Assignment
| Person | ID | Default For |
|--------|----|-------------|
| Liam | 31643251 | New cold prospects (default) |
| Tom | 30769884 | Strategic accounts |
| Christina | 30772485 | Event/LinkedIn-sourced only |

### Call Tasks

Create after contact, associated to it:
```
objectType: "tasks"
hs_task_subject: "Cold call - <Name> (<Company>)"
hs_task_type: "CALL", hs_task_status: "NOT_STARTED", hs_task_priority: "MEDIUM"
hubspot_owner_id: <same as contact>
associations: [{ targetObjectId: <contact_id>, targetObjectType: "contacts" }]
```

---

## Step 5 (Optional): Add to Apollo Sequence

1. `apollo_emailer_campaigns_search` — find sequence by name
2. `apollo_email_accounts_index` — get email account ID
3. `apollo_contacts_create` for each person (search results aren't contacts yet) — use `run_dedupe: true`
4. `apollo_emailer_campaigns_add_contact_ids`:
   ```
   id: <sequence_id>
   emailer_campaign_id: <same as sequence_id>
   contact_ids: [<apollo_contact_ids>]
   send_email_from_email_account_id: <from step 2>
   ```

---

## Step 6: Report

Summarize with counts: searched → ICP passed → dupes skipped → enriched (credits used) → created in HubSpot → tasks created → added to sequence. List skipped prospects with reasons.

---

## Quick Commands

| Request | Steps |
|---------|-------|
| "Find me 20 people to call in [vertical]" | 1-4, Liam as default owner |
| "Enrich [name] at [company]" | 3 only |
| "Check if [company] is ICP fit" | `apollo_organizations_enrich` + check against icp.md |
| "Add these to [sequence]" | 5 only |
| "How many credits left?" | `apollo_users_api_profile` only |
| "Search for [title] at [company type]" | 1 only, present with ICP assessment |

---

## Guardrails

- Never enrich without confirming credit cost
- Never create HubSpot records without showing proposed table
- Always dedupe before creating (Apollo + HubSpot)
- Flag any title containing AI/Data/BI/Analytics even if it passed search filter
- No email AND no phone = don't create in HubSpot
- Batch enrichments in groups of 10, confirm between batches
