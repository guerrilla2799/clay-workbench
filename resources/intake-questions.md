# Clay Workbench — 8-Question Intake

Always run this intake BEFORE composing any workbook. Do not fabricate. If the user says "you decide," ask which dimension they want a recommendation on, then offer 2–3 options.

Source pattern: LirKonu/clay-campaign + Brandon's GTM rigor.

---

## The 8 Questions

### 1. Source
**Where does the data come from?**

Options:
- Upload CSV (file path)
- Domain or company-name list (paste)
- Webhook (form submission, n8n, Zapier)
- HubSpot view (CRM list ID)
- Salesforce report (SOQL or report ID)
- Apollo / Sales Nav search URL
- Existing Clay table (table ID to clone or feed)
- Other (specify)

### 2. Input Fields
**What columns does each row arrive with?**

Confirm the exact source fields. Match each to a Clay column type (text, URL, email, number, date). Flag missing-but-needed: e.g., "row arrives with email only → need to find Company Domain to enrich."

### 3. Enrichments Needed
**Which data points must each row carry by the time we export?**

Common categories — confirm each:
- Firmographics (industry, employee count, revenue, HQ, funding)
- Tech stack (BuiltWith / Wappalyzer / public stack signals)
- Persona contacts (titles to find at the company)
- Email + verification
- Phone (mobile / direct)
- LinkedIn URL
- Trigger event (job change, hiring, funding, tech adoption)
- Custom AI research (Claygent prompt)

### 4. Logic / Gates
**What disqualifies a row?**

Capture the ICP filter conditions:
- Industry whitelist / blacklist
- Employee count band
- Revenue floor / ceiling
- Geography
- Suppression rules (current customers, recent contacts, opt-outs)
- Trigger-event requirement (yes/no, recency window)

### 5. AI Columns
**Which decisions need a Claygent / AI column?**

Common AI uses:
- Pain-point research from website
- Hiring signal interpretation
- Trigger-event classification (real vs noise)
- ICP fit summary (1 sentence per row)
- Personalized first line for outbound

For each AI column: define the input (which other columns it reads) and the output shape (1 sentence / classification label / JSON).

### 6. Outputs
**Where does the final row go?**

Options:
- Sequencer (SalesLoft / Outreach / Apollo / 11x / Smartlead / Instantly) — specify which
- CRM (HubSpot / Salesforce) — create or update? Which object?
- Slack channel (notification on match)
- Webhook (n8n / Zapier / custom endpoint)
- CSV export only (manual download)
- Stay-in-Clay (no export)

### 7. Auto-Run
**Should new rows process automatically, or only when manually triggered?**

- **Auto-run ON**: New rows from source process immediately. Use for inbound forms, signal-triggered workflows.
- **Auto-run OFF**: Rows queue but only process when user clicks Run. Use for batch ABM lists, expensive enrichments, anything requiring review.

Default to **OFF** during construction to avoid burning credits before verification.

### 8. Sample Size
**How many sample rows for initial verification?**

Default: 5–10 rows. Run pre-flight (Rule #1: Gates Before Credits) against these to validate ICP fit logic, then 25 for waterfall match-rate validation, then full run.

---

## Intake Conversation Template

```
Before I build, I need 8 quick answers — this saves us credits and rework.

1. **Source**: Where does the input list come from?
2. **Input fields**: What columns arrive with each row?
3. **Enrichments**: What data must each row have by export?
4. **Gates**: What disqualifies a row?
5. **AI columns**: Which decisions need Claygent / AI?
6. **Outputs**: Where does the final row go?
7. **Auto-run**: Process new rows automatically, or manual trigger?
8. **Sample size**: How many rows for the verification run?

You can answer in one block. If "you decide" on any — tell me, I'll offer 2–3 options for that one.
```

---

## "You Decide" Decision Tree

If the user defers on a question, offer **2–3 concrete options** with tradeoffs. Never default silently.

| Question | If "you decide", offer |
|----------|-----------------------|
| Source | (a) Upload CSV — fastest, (b) HubSpot view — keeps CRM as source of truth, (c) Apollo search URL — best for net-new |
| Enrichments | (a) Lean: firmographics + email only, (b) Standard: + LinkedIn + persona, (c) Full: + phone + Claygent trigger |
| Gates | (a) Industry + employee count only, (b) + revenue + geo, (c) + trigger event requirement |
| AI columns | (a) None, (b) Pain-point researcher only, (c) + personalized first line |
| Outputs | (a) Sequencer, (b) CRM, (c) Both with sync logic |
| Auto-run | (a) ON for inbound speed, (b) OFF for credit safety (recommended for ABM) |
| Sample size | 5 → 25 → full (recommended graduated approach) |

---

## Anti-Patterns

❌ "I'll use reasonable defaults" — never. Ask.
❌ Assuming HubSpot when source isn't stated.
❌ Adding phone enrichment because "users usually want it."
❌ Setting auto-run ON by default — burns credits during construction.
❌ Skipping the gates question — leads to silent ICP drift.
