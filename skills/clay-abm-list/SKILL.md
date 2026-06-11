---
name: clay-abm-list
description: Build an account-keyed Clay workbook for ABM target lists — Tier 1/2/3, expansion lists, signal-triggered account builds. Composes firmographic enrichment + trigger event detection + ICP gate + persona contact-finding readiness, exporting to CRM and/or sequencer. Triggers — "ABM list", "target accounts", "Tier 1 accounts", "build account list", "expansion list", "white space", "signal-triggered accounts", "intent accounts", "Clay account workbook", "/clay-abm-list".
---

# clay-abm-list — Build an ABM Account Workbook

Loads when the user is building an **account-keyed** Clay workbook — companies first, contacts later (or never, if the workbook hands off pre-contact to AEs).

Inherits `clay-workbench/SKILL.md` master workflow. Specializes step 3 (composition) and step 5 (execution).

---

## Inputs Expected

From intake (`resources/intake-questions.md`):
- **Source**: CSV / domain list / HubSpot view / Salesforce report / Apollo URL / Sales Nav URL
- **Tier criteria**: Industry whitelist, employee count band, revenue floor, geo, funding stage
- **Trigger requirement**: Yes/no — funding, hiring, job change, tech adoption, executive change
- **Output destination**: CRM (account create) and/or sequencer (account → contacts queued)
- **Contact-finding mode**: NONE (account-only workbook) / DEFERRED (build account, find contacts later) / EAGER (find contacts in same workbook)

---

## Step 3 — Composition (Specialized)

### Canonical Column Order (Left → Right)

| # | Column | Type | Source / Provider | Cost | Depends On |
|---|--------|------|-------------------|------|------------|
| 1 | `company_domain` | text | source (CSV / form / etc.) | 0 | — |
| 2 | `company_name` | text | source OR find-company | 0–1 | `company_domain` |
| 3 | `industry` | text | find-company | 1 | `company_domain` |
| 4 | `employee_count` | number | find-company | 1 | `company_domain` |
| 5 | `revenue_range` | text | find-company / People Data Labs | 1–2 | `company_domain` |
| 6 | `hq_country` | text | find-company | 1 | `company_domain` |
| 7 | `funding_stage` | text | find-company OR Predictleads | 1–2 | `company_domain` |
| 8 | `tech_stack_signals` | text[] | Wappalyzer (lite) OR BuiltWith (full) | 1–5 | `company_domain` |
| 9 | `trigger_event` | text | Predictleads / Champify / UserGems | 2 | `company_domain` |
| 10 | `trigger_recency_days` | number | formula on trigger_event | 0 | `trigger_event` |
| 11 | **`icp_gate_qualified`** | formula | clayscript | 0 | columns 3–10 |
| 12 | `account_tier` | formula | clayscript (T1/T2/T3) | 0 | gate columns |
| 13 | `suppression_check` | formula | lookup against suppression table | 0 | `company_domain` |
| 14 | `route_to` | formula | tier × suppression → CRM / Slack / SDR | 0 | columns 11–13 |

### `icp_gate_qualified` Formula Pattern

```clayscript
IF(
  AND(
    industry IN [{ICP_INDUSTRIES}],
    employee_count >= {MIN_EMPLOYEES},
    employee_count <= {MAX_EMPLOYEES},
    hq_country IN [{ICP_GEOS}],
    OR(
      {TRIGGER_REQUIRED} == FALSE,
      AND(trigger_event != NULL, trigger_recency_days <= 90)
    )
  ),
  TRUE,
  FALSE
)
```

Fill `{...}` placeholders from intake answers.

### `account_tier` Formula Pattern

```clayscript
IF(
  icp_gate_qualified == FALSE, "DISQUALIFIED",
  IF(
    AND(employee_count >= 1000, trigger_event != NULL), "T1",
    IF(
      OR(employee_count >= 250, trigger_event != NULL), "T2",
      "T3"
    )
  )
)
```

Adjust tier thresholds per intake.

### `route_to` Formula Pattern

```clayscript
IF(
  suppression_check == TRUE, "SUPPRESSED",
  IF(account_tier == "T1", "SDR_QUEUE_T1",
  IF(account_tier == "T2", "MARKETING_NURTURE",
  IF(account_tier == "T3", "PROGRAMMATIC",
  "DISQUALIFIED")))
)
```

---

## Step 5 — Execution (Specialized)

### Preferred Path: MCP

```
1. mcp__claude_ai_Clay__get-credits-available
2. mcp__claude_ai_Clay__list_subroutines
   → If an "ABM List Build" subroutine exists, prefer that
3. If subroutine exists:
   mcp__claude_ai_Clay__get_subroutine_input_options
   → Map intake answers to required inputs
   → mcp__claude_ai_Clay__run_subroutine
4. If no subroutine:
   For sample of 5 rows:
     mcp__claude_ai_Clay__find-and-enrich-company (per domain)
   → Show enrichment results
   → Confirm gate logic against sample
   → Proceed to full run on confirmation
```

### Manual Fallback

If MCP can't compose the table from scratch (current limitation):

1. **Create table in Clay UI**: New Table → name `"ABM Build — {ICP descriptor} — {date}"`.
2. **Add source**: Source → CSV / HubSpot view / Sales Nav URL (per intake).
3. **Add columns 1–10** in order from spec. For each:
   - Click + Add Column → Enrichment → select provider → map `company_domain` as input.
4. **Add `icp_gate_qualified`**:
   - + Add Column → Formula → paste formula from above with placeholders filled.
5. **Add `account_tier`, `suppression_check`, `route_to`**:
   - Same pattern — Formula columns, paste templates.
6. **Set Run Conditions** on every paid column (industry through trigger_event):
   - Column settings → Run Condition → `icp_gate_qualified = TRUE` ... wait, that's circular. Resolve:
   - Use a **two-pass gate**: Pass 1 runs cheap signals (industry, employee_count) — Pass 2 runs expensive signals (tech_stack, trigger_event) gated by Pass 1.
7. **Set `auto_run = false`** during construction.
8. **Run on 5-row sample** → verify gate, tier, and route_to logic.
9. **Run on 25-row sample** → verify trigger event match rate (~30% expected).
10. **Full run** only after sample passes.

---

## Two-Pass Gate Pattern (Important Detail)

```
Pass 1 (cheap):
  - industry, employee_count, hq_country
  - Gate column: `pass_1_qualified` = formula on these three

Pass 2 (paid, conditional on Pass 1):
  - revenue_range, funding_stage, tech_stack, trigger_event
  - Run condition: `pass_1_qualified = TRUE`
  - Gate column: `icp_gate_qualified` = formula on Pass 1 + Pass 2 outputs

Pass 3 (downstream):
  - All paid contact-finding / Claygent / outbound prep
  - Run condition: `icp_gate_qualified = TRUE`
```

This pattern is the #1 credit saver — typically cuts burn by 40–60% on broad source lists.

---

## Verify-and-Handoff Checklist

- [ ] 5-row sample: industry/size/geo enrichments resolve correctly (>80% success)
- [ ] 5-row sample: `icp_gate_qualified` matches manual assessment (validate by hand)
- [ ] 25-row sample: trigger event match rate ≥ 25% (if trigger required)
- [ ] 25-row sample: `account_tier` distribution reasonable (T1: 5–15%, T2: 20–40%, T3: remainder)
- [ ] Suppression table connected and `suppression_check` returns TRUE for known customers
- [ ] `route_to` routes correctly to the right destination per intake spec
- [ ] CRM/Slack push actions filter on `route_to != "DISQUALIFIED"` and `route_to != "SUPPRESSED"`
- [ ] Cost-per-qualified-account documented (total credits / qualified count)

---

## Common ABM Workbook Variants

| Use Case | Adjustments |
|----------|------------|
| Net-new outbound list | All columns above + push to `clay-enrich-waterfall` for contact finding |
| Expansion / white space | Source = current customers' lookalikes (Ocean.io) + suppress current customers themselves |
| Reactivation | Source = closed-lost CRM list; add `last_touch_days` column; trigger required = TRUE |
| Conference attendee list | Source = uploaded attendee CSV; trigger = "attending {conference}"; gate adjusted to focus on title + company size |
| Account scoring refresh | Source = existing CRM accounts; only re-enrich accounts >30 days stale |

---

## Anti-Patterns

❌ Running tech stack enrichment on every row before gate (5 credits × 1000 = 5000 wasted).
❌ Setting `auto_run = TRUE` during build — burns credits during column iteration.
❌ Single-pass gate — paying for trigger events on rows you'd drop on industry alone.
❌ Pushing all rows to SDR queue — destroys signal-to-noise. Always filter on tier + gate.
❌ Skipping suppression — embarrassing to enrich and route a current customer.

---

## Related

- After this workbook is built and qualified accounts are identified → invoke `/clay-enrich-waterfall` to find contacts at qualified accounts.
- For scoring qualified accounts → invoke `/clay-icp-score`.
- For burn audits on running workbooks → invoke `/clay-troubleshoot`.
