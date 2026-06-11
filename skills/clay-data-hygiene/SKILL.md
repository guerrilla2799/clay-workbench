---
name: clay-data-hygiene
description: Ongoing CRM-side data hygiene via Clay — recurring dedup, decay detection (email bounce / phone disconnect / role change), stale-record flagging, enrichment refresh scheduling, and freshness scoring. Different from /clay-list-clean (one-shot pre-Clay input cleanup) — this is the always-on health monitor for the CRM records flowing back to Clay. Triggers — "data hygiene", "CRM dedup", "decay detection", "stale records", "enrichment refresh", "data freshness", "dirty HubSpot", "Salesforce duplicates", "data decay", "refresh contacts", "/clay-data-hygiene".
---

# clay-data-hygiene — Ongoing CRM Data Health

The recurring hygiene skill. Use when the user needs the **always-on** health monitor for CRM records (HubSpot, Salesforce) — not the one-shot pre-Clay input cleanup.

Inherits `clay-workbench/SKILL.md` master workflow. Specializes step 3 (composition around dedup + decay + refresh) and step 5 (recurring schedule + CRM write-back).

**Difference from `/clay-list-clean`**: that's pre-Clay input hygiene, one-shot. This is post-Clay, CRM-resident, recurring.

**Difference from `/clay-troubleshoot`**: that's reactive (something broke). This is proactive (data is silently rotting).

---

## Why this matters

B2B contact data decays ~30% per year:
- ~12% job change rate annually (often higher in tech: 18–25%)
- ~6% email format change (company rebrand, M&A)
- ~4% phone disconnect (mobile churn, dept reorg)
- ~8% title/role drift (promotion, lateral, scope change)

Without ongoing hygiene, a CRM with 50k contacts will have ~15k materially stale records after 12 months. Outbound to stale records destroys sender reputation, wastes credits on re-enrichment fixes, and skews pipeline reporting.

---

## Inputs Expected

- **CRM**: HubSpot / Salesforce / both
- **Scope**: which CRM objects (contacts, accounts, leads, deals)
- **Volume**: row count to maintain
- **Cadence**:
  - Dedup: weekly (drift accumulates fast)
  - Decay scan: daily (catches bounces / disconnects early)
  - Stale flagging: weekly
  - Refresh enrichment: rolling — N records/day to spread cost
- **Refresh budget**: max credits/day for proactive re-enrichment
- **Write-back rules**: which fields update in CRM, which are advisory only
- **Suppression**: do-not-refresh list (high-value records hand-curated)

---

## Step 3 — Composition (Specialized)

### Core Tables (Recurring)

This skill builds 3 linked Clay tables, not one:

**Table A — `crm_record_health`** (always-on, append-only health record per CRM object)

| # | Column | Type | Source | Cost | Notes |
|---|--------|------|--------|------|-------|
| 1 | `crm_id` | text | CRM source | 0 | |
| 2 | `object_type` | text | CRM source | 0 | contact / account / lead |
| 3 | `last_enriched_at` | date | CRM custom field OR Clay log | 0 | |
| 4 | `enrichment_freshness_days` | formula | clayscript | 0 | TODAY() - last_enriched_at |
| 5 | `email_format_unchanged` | claygent OR formula | check current domain MX vs stored | 1–3 | |
| 6 | `email_deliverability` | enrichment | ZeroBounce / NeverBounce / Million Verifier | 1 | |
| 7 | `phone_connected_status` | enrichment | Cognism phone verifier / Datagma | 1–2 | |
| 8 | `linkedin_url_resolves` | claygent | quick HEAD check via Claygent | 1 | |
| 9 | `current_title_matches_stored` | claygent | LinkedIn current title vs stored | 5 | |
| 10 | `current_company_matches_stored` | claygent | LinkedIn current company vs stored | 5 | |
| 11 | `recent_job_change_detected` | enrichment | Champify / UserGems / Predictleads | 2–5 | |
| 12 | `freshness_score` | formula | clayscript (composite 0–10) | 0 | weighted across 4–11 |
| 13 | `decay_flag` | formula | clayscript | 0 | TRUE if freshness_score < threshold |
| 14 | `recommended_action` | formula | clayscript | 0 | REFRESH / FLAG_FOR_REVIEW / SUPPRESS / OK |

**Table B — `crm_duplicates`** (run weekly, dedup detection)

| # | Column | Type | Source | Cost |
|---|--------|------|--------|------|
| 1 | `dup_cluster_id` | text | clayscript hash | 0 |
| 2 | `crm_ids` | array | CRM query | 0 |
| 3 | `match_method` | text | email_exact / domain+name_fuzzy / linkedin_url / phone | 0 |
| 4 | `match_confidence` | formula | clayscript | 0 |
| 5 | `survivor_crm_id` | formula | clayscript (highest-engagement / oldest / opt-in source) | 0 |
| 6 | `merge_recommended` | formula | clayscript (boolean) | 0 |
| 7 | `merge_blockers` | formula | clayscript (open deals on multiple records, etc.) | 0 |

**Table C — `refresh_queue`** (rolling, prioritized)

| # | Column | Type | Source | Cost |
|---|--------|------|--------|------|
| 1 | `crm_id` | text | from Table A | 0 |
| 2 | `priority_score` | formula | clayscript | 0 |
| 3 | `last_engaged_days` | formula | clayscript on CRM activity | 0 |
| 4 | `account_tier` | formula | clayscript (T1/T2/T3) | 0 |
| 5 | `is_in_active_opp` | formula | clayscript | 0 |
| 6 | `queue_position` | formula | clayscript rank | 0 |
| 7 | `refresh_eligible_today` | formula | clayscript (queue_position ≤ daily_budget) | 0 |

### `freshness_score` Composite (0–10)

```clayscript
SUM(
  IF(email_format_unchanged == TRUE, 2, 0),
  IF(email_deliverability IN ["valid", "catch_all_valid"], 2, IF(email_deliverability == "unknown", 1, 0)),
  IF(phone_connected_status == "connected", 1, 0),
  IF(linkedin_url_resolves == TRUE, 1, 0),
  IF(current_title_matches_stored == TRUE, 2, 0),
  IF(current_company_matches_stored == TRUE, 2, 0)
)
```

8–10 = fresh · 5–7 = aging · ≤4 = decayed.

### `recommended_action` Logic

```clayscript
CASE(
  recent_job_change_detected == TRUE AND current_company_matches_stored == FALSE, "REFRESH_AND_FLAG_JOB_CHANGE",
  email_deliverability IN ["invalid", "hard_bounce"], "SUPPRESS_EMAIL",
  freshness_score < 5, "REFRESH",
  freshness_score < 8 AND enrichment_freshness_days > 180, "REFRESH",
  AND(current_title_matches_stored == FALSE, account_tier IN ["T1", "T2"]), "FLAG_FOR_REVIEW",
  TRUE, "OK"
)
```

### `priority_score` Logic (Refresh Queue)

```clayscript
SUM(
  IF(account_tier == "T1", 4, IF(account_tier == "T2", 2, 0)),
  IF(is_in_active_opp == TRUE, 3, 0),
  IF(last_engaged_days <= 30, 2, 0),
  IF(recent_job_change_detected == TRUE, 3, 0),
  IF(enrichment_freshness_days > 365, 2, IF(enrichment_freshness_days > 180, 1, 0))
)
```

### Write-Back Rules

Default config:
- **Auto-update CRM**: email_deliverability bounces, phone disconnects, recent_job_change → flag fields
- **Advisory only (don't auto-write)**: title/company changes (require human confirm), dedup merge recommendations
- **Never write back**: low-confidence Claygent inferences

User can override per field at intake.

---

## Step 5 — Execution (Specialized)

### Schedule Setup

```
Table A (health monitor):
  - Cadence: daily
  - Process N records/day = total_records / 30 (full sweep monthly)
  - auto_run = TRUE after backfill validation

Table B (dedup):
  - Cadence: weekly (Sundays)
  - Full scan
  - auto_run = TRUE after manual review of first 3 weekly runs

Table C (refresh queue):
  - Cadence: daily
  - Take top `refresh_eligible_today` from queue → trigger re-enrichment via /clay-enrich-waterfall subroutine
  - auto_run = TRUE after backfill validation
```

### MCP Path

```
1. mcp__claude_ai_Clay__get-credits-available
2. mcp__claude_ai_Clay__list_subroutines → confirm refresh subroutine exists
3. Connect CRM source (HubSpot or Salesforce) → 3 Clay tables
4. Build columns per spec
5. Run 25-row backfill on Table A → eyeball freshness_score distribution against intuition
6. Run weekly Table B → manually merge or flag 5 duplicate clusters before flipping auto_run
7. Queue first day of Table C → review priority_score top 20 by hand
8. Flip auto_run = TRUE on each table only after its respective review
```

### Manual Fallback

1. Create 3 tables in Clay UI per the column specs
2. Connect CRM source(s); make sure CRM permission scope includes write-back if auto-update is on
3. Build columns per spec
4. Backfill validate per cadence
5. Schedule recurring run on each table
6. Pipe Table B dedup recommendations into a Slack channel for human merge approval
7. Pipe Table A decay flags into a CRM list view for AE/CSM review

---

## Credit Pre-Flight (Mandatory)

```
Table A (health monitor) — daily rolling:
  Per row: ~10–25 credits (depending on Claygent depth)
  Daily processing: (total_records / 30) × per-row cost
  Monthly: full-sweep cost ≈ total_records × per-row cost

Table B (dedup) — weekly:
  Mostly formula columns (cheap)
  Per scan: ~1–2 credits per duplicate cluster found

Table C (refresh queue) — daily:
  Per row: cost of /clay-enrich-waterfall (~5–15 credits/row)
  Daily: refresh_budget × per-row cost

Example: 50k contact CRM, mid-tier Claygent
  Table A: ~50k × 15 = 750k credits/month (~$7.5k)
  Table C: 200 refreshes/day × 10 credits = 60k/month (~$600)
  Total ongoing: ~$8k/month

Often cheaper than the cost of decayed-data damage (sender reputation, wasted SDR time on bad leads, skewed pipeline) — but always present this estimate explicitly.
```

If estimate is shocking, default suggestion: shrink scope (T1 + T2 accounts only) before broadening.

---

## Verify-and-Handoff Checklist

- [ ] 25-row backfill on Table A: freshness_score distribution matches gut feel (mostly 7–9 for fresh, occasional 3–5 for older records)
- [ ] 25-row backfill on Table B: dedup clusters look real, not false positives
- [ ] First weekly dedup run: ≤10 high-confidence merge recommendations → manually merge first 5, validate
- [ ] First daily refresh queue: top 20 priority_score records make sense to the AE
- [ ] CRM write-back permissions correct; test fields update via Clay
- [ ] Slack channel for dedup approval connected
- [ ] CRM list view for decay flag review live
- [ ] Cost per month documented; tracks within 20% of estimate over first 30 days
- [ ] auto_run only flipped TRUE per-table after that table's review

---

## Use-Case Variants

| Scenario | Adjustments |
|----------|-------------|
| Tier 1 ABM accounts only | Scope to Tier 1 account contacts; weekly health check (not daily) |
| Customer base (CS hygiene) | Add CSM-owned write-back; flag role/company changes for renewal risk signal |
| Outbound list maintenance | Tighter SUPPRESS threshold on email_deliverability; immediate suppress on bounce |
| M&A / rebrand event | One-shot full sweep; turn off auto_run after, return to daily mode |
| Compliance / GDPR refresh cycle | Add `consent_freshness_days` column; refresh consent records every 12 months |

---

## Anti-Patterns

❌ Daily full-sweep on a 100k CRM — wastes credits on records that haven't aged. Use rolling 30-day sweep.
❌ Auto-writing title/company changes without human confirm — Claygent inferences can be wrong, and changing role in CRM cascades to ICP scoring + routing.
❌ No suppression list for hand-curated VIPs — auto-refresh can overwrite a manually-tuned record.
❌ Auto-merging duplicates without checking for open opps on both records — destroys revenue attribution.
❌ Treating freshness_score < 5 as immediate refresh trigger without budget gate — burns the daily credit budget on day 1.
❌ Skipping CRM write-back permission test — discover at scale that fields don't update.
❌ Running this on a CRM that hasn't had `/clay-list-clean` style hygiene first — garbage in, garbage compounding.

---

## Related

- For one-shot pre-Clay input cleanup → `/clay-list-clean` (different scope, different timing).
- For the refresh enrichment action triggered by Table C → `/clay-enrich-waterfall` (the subroutine called from refresh_queue).
- For ongoing trigger monitoring that pairs with role-change detection → `/clay-signal-monitor`.
- For Claygent prompt tuning on the title/company match columns → `/clay-claygent-iterator`.
- For portfolio-wide cost audit of this skill's recurring runs → `/clay-cost-audit`.
