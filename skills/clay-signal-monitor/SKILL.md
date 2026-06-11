---
name: clay-signal-monitor
description: Stand up recurring trigger monitoring in Clay — job changes, hiring posture shifts, funding rounds, product launches, leadership changes, tech adoption, and intent surges — with auto-routing to Slack, CRM, and the right outbound play. Builds the always-on signal layer of an ABM motion. Triggers — "signal monitor", "job change monitor", "hiring trigger", "funding alerts", "intent monitor", "trigger watcher", "Champify", "UserGems", "Predictleads", "ongoing monitor", "recurring Clay workbook", "/clay-signal-monitor".
---

# clay-signal-monitor — Always-On Trigger Monitoring

The recurring-workflow skill. Use when the user needs a *monitor* (runs on a schedule) rather than a one-shot list build. Job changes, funding rounds, hiring spikes, new product launches, leadership departures, intent surges — anything that says "now is the moment to reach out."

Inherits `clay-workbench/SKILL.md` master workflow. Specializes step 3 (composition — schedule + signal source + dedup + routing) and step 5 (execution — `auto_run = TRUE` after qualification, not before).

**Difference from `/clay-abm-list`**: that builds a static list. This builds a *recurring* watcher that appends new qualifying rows over time.

---

## Inputs Expected

From intake:
- **Signal type(s)** — choose any combo:
  - **Job change** (Champify / UserGems / Predictleads) — alumni / champion leaves and lands somewhere new
  - **Hiring posture** (Predictleads / LinkedIn jobs scrape) — new role posted matching ICP triggers
  - **Funding round** (Predictleads / Crunchbase / Harmonic)
  - **Product launch** (Predictleads / Claygent news scan)
  - **Leadership change** (Champify / UserGems / Claygent)
  - **Tech adoption** (BuiltWith deltas / Wappalyzer)
  - **Intent surge** (G2 / Bombora / 6sense / Cognism)
- **Watch source(s)**: alumni list / target account list / customer roster / lookalike list / open-territory
- **Cadence**: daily / weekly / on-source-update
- **Routing rules**: Slack channel(s) by tier; HubSpot/Salesforce object update; sequencer push (with `/clay-outbound`)
- **Recipients**: which AE/SDR/exec gets which signal class
- **Suppression**: current customers; opt-outs; already-engaged-in-last-30d

---

## Step 3 — Composition (Specialized)

### Canonical Column Order

| # | Column | Type | Source / Provider | Cost | Depends On |
|---|--------|------|-------------------|------|------------|
| 1 | `watch_id` | text | source row ID | 0 | — |
| 2 | `signal_type` | text | source | 0 | — |
| 3 | `signal_payload` | json | source | 0 | — |
| 4 | `signal_date` | date | source | 0 | — |
| 5 | `signal_recency_days` | formula | clayscript | 0 | 4 |
| 6 | `person_linkedin_url` OR `company_domain` | text | parsed from payload | 0 | 3 |
| 7 | `dedup_key` | formula | clayscript hash(signal_type, person/company, date) | 0 | 2, 4, 6 |
| 8 | `is_duplicate` | formula | clayscript lookup against history table | 0 | 7 |
| 9 | **`pass_1_relevant`** | formula | clayscript (cheapest qualifiers) | 0 | 2, 6, 8 |
| 10 | `company_firmographics` | enrichment | find-and-enrich-company | 1–3 | 6 |
| 11 | `person_details` | enrichment | find-and-enrich-contact | 1–3 | 6 |
| 12 | `icp_gate_qualified` | formula | clayscript | 0 | 10, 11 |
| 13 | `suppression_check` | formula | clayscript lookup | 0 | 6 |
| 14 | `signal_classifier` | claygent | Claygent (route to play category) | 5–10 | 3, 10, 11 |
| 15 | `signal_severity` | formula | clayscript (Hot/Warm/Cold) | 0 | 14, 5 |
| 16 | `play_recommended` | formula | clayscript map (signal_type × severity → play_name) | 0 | 2, 15 |
| 17 | `assigned_to` | formula | clayscript routing table | 0 | 12, 13, 16 |
| 18 | `alert_payload` | claygent OR formula | Claygent first-pass message + context | 5–10 | 10, 11, 14, 16 |
| 19 | `route_to` | formula | clayscript | 0 | 12, 13, 15, 17 |

### `dedup_key` Pattern

```clayscript
SHA256(CONCAT(signal_type, "-", LOWER(company_domain), "-", FORMAT_DATE(signal_date, "YYYY-MM-DD")))
```

Maintain a separate `signal_history` Clay table; the `is_duplicate` formula does a lookup before any paid column. Critical — Champify and Predictleads will re-fire on the same event without this.

### `pass_1_relevant` Formula

```clayscript
IF(
  AND(
    is_duplicate == FALSE,
    signal_recency_days <= {MAX_RECENCY_DAYS},
    signal_type IN [{WATCHED_SIGNAL_TYPES}]
  ),
  TRUE,
  FALSE
)
```

Default `MAX_RECENCY_DAYS = 14` for job change / hiring / funding; `MAX_RECENCY_DAYS = 7` for intent surges.

### `signal_severity` Formula

```clayscript
IF(
  AND(signal_recency_days <= 7, icp_gate_qualified == TRUE, signal_classifier IN ["urgent", "high"]),
  "HOT",
  IF(
    AND(signal_recency_days <= 30, icp_gate_qualified == TRUE),
    "WARM",
    "COLD"
  )
)
```

### `play_recommended` — Mapping Table

| Signal Type | HOT | WARM | COLD |
|------------|-----|------|------|
| Job change (champion) | SDR_NOW + exec note | AE_2WK_FOLLOWUP | NURTURE |
| Hiring (ICP role) | SDR_NOW with role context | AE_2WK_FOLLOWUP | MONITOR |
| Funding round | SDR_NOW + congrats angle | EXEC_NOTE | NURTURE |
| Product launch | AE_NOW with launch context | NURTURE | DROP |
| Leadership change | SDR_NOW (new exec) | AE_2WK_FOLLOWUP | MONITOR |
| Tech adoption (relevant stack) | AE_NOW with stack-fit angle | NURTURE | DROP |
| Intent surge | SDR_NOW | AE_2WK_FOLLOWUP | NURTURE |

Codify in clayscript as a CASE/IF chain.

### `route_to` Formula

```clayscript
IF(
  OR(suppression_check == TRUE, icp_gate_qualified == FALSE),
  "DROP",
  CONCAT(play_recommended, "::", assigned_to)
)
```

### Alert Output Templates (Slack-Ready)

```
🔥 HOT — {signal_type}
{full_name} ({title}) at {company_name}
Signal: {signal_payload_summary} · {signal_recency_days}d ago
Play: {play_recommended} → {assigned_to}
Context: {signal_classifier}
Open in Clay: {clay_row_url}
```

Build as a Slack action with the formula above as `text`. One channel per tier or per AE — don't single-channel-everything (channel fatigue kills response rate).

---

## Step 5 — Execution (Specialized)

### Schedule Setup

```
1. Source: connect Champify / UserGems / Predictleads / BuiltWith / 6sense / G2 to a Clay table as a watched source
2. Cadence:
   - Daily for job changes + hiring + intent
   - Weekly for funding + product launches + tech adoption
3. After full column build:
   - Run 25-row historical backfill first (`auto_run = false`)
   - Verify dedup correctness against signal_history
   - Verify routing logic against AE/SDR ownership
4. ONLY THEN set `auto_run = TRUE` on the table — for monitors specifically, auto_run is the point
```

### MCP Path

```
1. mcp__claude_ai_Clay__get-credits-available
2. mcp__claude_ai_Clay__list_subroutines → if "Signal Monitor" subroutine exists, prefer it
3. mcp__claude_ai_Clay__find-and-enrich-company / find-and-enrich-contact for backfill validation
4. mcp__claude_ai_Clay__query-objects on signal_history → confirm dedup hash logic before enabling auto_run
```

### Manual Fallback

1. New table → `"Signal Monitor — {signal_class} — {watch_source}"`
2. Connect source integration → set incremental sync
3. Build columns 1–9 first (free / cheap) — verify dedup hits
4. Add columns 10–11 with Run Condition `pass_1_relevant == TRUE`
5. Add columns 12–19 with Run Condition `icp_gate_qualified == TRUE`
6. Build a separate `signal_history` table — append every signal_id + dedup_key after action fires
7. Slack action → Run Condition `route_to NOT IN ("DROP", "MONITOR")`
8. CRM action → Run Condition by play_recommended mapping
9. Backfill 25 rows with `auto_run = FALSE` → eyeball every alert
10. Flip `auto_run = TRUE` only after a clean 25-row backfill

---

## Credit Pre-Flight (Mandatory)

```
Per qualifying row (after dedup + ICP gate):
  - Firmographics:           ~2 credits
  - Person enrichment:       ~2 credits
  - signal_classifier:       ~5–10 credits (Claygent)
  - alert_payload:           ~5–10 credits (Claygent)
  Total: ~15–25 credits per qualified signal

Volume estimate per cadence:
  - 1000-account watch, daily, ~2% trigger rate: ~20 qualified/day × 20 = 400 credits/day = 12k/month
  - Plus dedup miss tail: budget +30%
```

If user provisions monitor across 5 signal types and 5000 accounts, pre-flight every signal class separately. Default suggestion: start with ONE signal class on the highest-value account list, prove ROI, expand.

---

## Verify-and-Handoff Checklist

- [ ] 25-row backfill: signal_payload parsed correctly per signal_type
- [ ] 25-row backfill: dedup_key produces no false-positive duplicates
- [ ] 25-row backfill: pass_1_relevant gates ~70% of historical events as not-relevant (otherwise gate is too loose)
- [ ] 25-row backfill: signal_classifier outputs read sensibly (manual review)
- [ ] 25-row backfill: assigned_to maps to a real owner for every play_recommended
- [ ] Slack channels exist, Clay integration connected, formatted alert renders in test channel
- [ ] CRM action filtered by play_recommended; no duplicates created
- [ ] Suppression list current (customers + 30d-recent-engaged)
- [ ] signal_history table connected; auto_run only flipped TRUE after backfill review
- [ ] First-week alert volume documented vs benchmark (Hot ≤5/day per AE; if higher, tighten gate)

---

## Cadence-Type Variants

| Signal Class | Cadence | Recency Gate | Severity Threshold |
|--------------|---------|-------------|-------------------|
| Champion job change | Daily | ≤14d | HOT if ≤7d at qualifying new co |
| ICP hiring posture | Daily | ≤30d | HOT if new ICP role posted ≤7d |
| Funding round | Weekly | ≤45d | HOT if Series A/B at named ICP firm ≤14d |
| Product launch | Weekly | ≤30d | WARM by default — usually nurture not now |
| Leadership change | Daily | ≤14d | HOT if new exec at named target account |
| Tech adoption | Weekly | ≤45d | HOT if added relevant tool ≤14d at qualifying acct |
| Intent surge | Daily | ≤7d | HOT only on multi-signal correlation |

---

## Anti-Patterns

❌ Single Slack channel for all signal types — channel fatigue, AEs tune out.
❌ Routing every signal as HOT — "everything is urgent" = nothing is urgent.
❌ Skipping dedup — Champify will re-fire on the same job change 3+ times.
❌ Flipping `auto_run = TRUE` before backfilling 25 rows by hand — alerts get sent live with broken logic.
❌ Letting `signal_history` grow unbounded — partition by month or your dedup lookups slow to a crawl.
❌ Running intent-surge monitor without correlating ≥2 sources — single-signal intent is mostly noise.
❌ Triggering outbound from a HOT signal without checking suppression and 30d-recent-engaged.

---

## Related

- For one-shot list builds (not recurring) → `/clay-abm-list`.
- For pairing signal with deep account context before alerting → `/clay-account-research`.
- For pairing signal with person-level entry hook → `/clay-prospect-research`.
- For the outbound play triggered by a HOT signal → `/clay-outbound`.
- For burn-rate audits on long-running monitors → `/clay-troubleshoot`.
