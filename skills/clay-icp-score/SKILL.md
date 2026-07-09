---
name: clay-icp-score
description: Compose ICP fit + intent composite score columns in Clay workbooks — 10-point grading rubric, fit + intent decomposition, routing by score band. Generates Clayscript formulas, weighting rationale, and threshold logic. Triggers — "ICP score", "lead score", "fit score", "qualify leads", "10-point grade", "MQL", "PQL", "lead routing by score", "/clay-icp-score".
---

# clay-icp-score — Composite Lead Scoring

Builds the ICP fit + intent + behavioral composite score column for any Clay workbook. Based on Brandon's 10-point ICP rubric (fit dimensions × intent triggers).

Inherits master workflow. Specializes step 3 (scoring composition) and step 5 (validation against historical wins).

---

## Inputs Expected

From intake:
- **Scoring purpose**: MQL grading (route to sales) / PQL (product-led signal) / account prioritization (sales-led)
- **Fit dimensions**: which firmographic attributes count (industry, employees, revenue, geo, stack)
- **Intent signals available**: which triggers can we detect (form fill, email open, content download, job change, hiring, funding)
- **Historical win data**: do you have a CRM list of closed-won deals to back-test against?
- **Score output shape**: numeric 1–10 / letter A/B/C/D / band Hot/Warm/Cold
- **Routing thresholds**: which score gets which destination

---

## Step 3 — Composition (Specialized)

### The Brandon 10-Point Rubric

Two halves: 5 points for fit, 5 points for intent.

#### Fit (5 points)
- **In target industry/vertical**: 2 pts
- **Correct company size band**: 1 pt
- **Geo match**: 1 pt
- **Tech stack signal**: 1 pt (e.g., uses competitor / complementary tool)

#### Intent (5 points)
- **Trigger event present**: 2 pts (job change / funding / hiring / tech adoption)
- **Trigger recency < 90 days**: 1 pt (multiplier — only if trigger present)
- **Behavioral signal present**: 1 pt (visited /pricing, downloaded asset, attended event)
- **Budget authority / role match**: 1 pt (decision-maker title)

**8–10 = pursue immediately · 5–7 = qualify first · <5 = pass.**

### Column Spec

| # | Column | Type | Cost | Depends On |
|---|--------|------|------|-----------|
| 1 | `fit_industry` | formula | 0 | `industry` |
| 2 | `fit_size` | formula | 0 | `employee_count` |
| 3 | `fit_geo` | formula | 0 | `hq_country` |
| 4 | `fit_stack` | formula | 0 | `tech_stack_signals` |
| 5 | `fit_score` | formula (sum) | 0 | 1–4 |
| 6 | `intent_trigger` | formula | 0 | `trigger_event` |
| 7 | `intent_recency` | formula | 0 | `trigger_recency_days`, `intent_trigger` |
| 8 | `intent_behavior` | formula | 0 | source-system behavioral fields |
| 9 | `intent_role` | formula | 0 | `title`, `seniority` |
| 10 | `intent_score` | formula (sum) | 0 | 6–9 |
| 11 | `icp_score` | formula | 0 | `fit_score + intent_score` |
| 12 | `icp_band` | formula | 0 | `icp_score` → Hot/Warm/Cold |
| 13 | `route_to` | formula | 0 | `icp_band`, suppression |

### Formula Templates

```clayscript
// fit_industry
IF(industry IN [{ICP_INDUSTRIES}], 2, 0)

// fit_size
IF(AND(employee_count >= {MIN}, employee_count <= {MAX}), 1, 0)

// fit_geo
IF(hq_country IN [{GEOS}], 1, 0)

// fit_stack
IF(ANY(tech_stack_signals IN [{ICP_STACK}]), 1, 0)

// fit_score
fit_industry + fit_size + fit_geo + fit_stack

// intent_trigger
IF(trigger_event != NULL, 2, 0)

// intent_recency (only credits if trigger present)
IF(AND(intent_trigger > 0, trigger_recency_days <= 90), 1, 0)

// intent_behavior
IF(OR(visited_pricing == TRUE, downloaded_asset == TRUE, event_attended == TRUE), 1, 0)

// intent_role
IF(seniority IN ["VP", "C-level", "Director"], 1, 0)

// intent_score
intent_trigger + intent_recency + intent_behavior + intent_role

// icp_score
fit_score + intent_score

// icp_band
IF(icp_score >= 8, "Hot",
IF(icp_score >= 5, "Warm",
"Cold"))

// route_to
IF(suppression_check == TRUE, "SUPPRESSED",
IF(icp_band == "Hot", "SDR_QUEUE",
IF(icp_band == "Warm", "MARKETING_NURTURE",
"PROGRAMMATIC")))
```

---

## Step 5 — Execution (Specialized)

### Back-Test Protocol (Critical)

Before deploying the score in production routing, **back-test against historical wins**:

```
1. Pull last 12 months of closed-won deals from CRM.
2. Add the deal IDs into a temporary Clay table.
3. Run all 13 scoring columns against them.
4. Distribution check:
   - >70% of closed-won should land in "Hot" or "Warm"
   - <10% of closed-won in "Cold" → rubric is wrong if higher
5. False positive check:
   - Pull a sample of 100 "Hot" prospects that NEVER closed.
   - Look for the systematic mis-classification (usually: wrong industry weighting, or trigger event over-credited).
6. Adjust weights until back-test passes.
```

If back-test data unavailable: ship the rubric **observably** (mark all scores in CRM but don't route on them) for 4 weeks, then back-test on that period.

### Preferred Path: Tier 1 (official Agent Plugin) — see resources/execution-surface.md

```
1. clay credits — balance pre-flight (formula columns are free; back-test enrichment isn't)
2. clay tables rows / clay tables query — pull existing scored rows for validation
3. Apply the 13-column scoring as formula columns — table column formulas are
   still UI-only (Tier 3); walk the user through the Manual Fallback steps below
4. table MCP tool — natural-language check:
   "Show score distribution by band and route_to destination"
5. Validate distribution against expectations.
```

Tier 2 (connector) fallback: `query-objects` for scored rows, `ask-question-about-accounts` for the distribution check.

### Manual Fallback (Tier 3)

1. In the existing table, + Add Column → Formula → paste each column formula above.
2. Order matters — `fit_score` depends on `fit_industry` etc.; place left-to-right.
3. Test on 10 known rows manually — score each by hand, compare to formula output.
4. Adjust thresholds and weights.
5. Set `route_to` action filter on push-to-CRM / push-to-SalesLoft / Slack-notify.

---

## Routing Logic by Band

| Band | Score | Default Destination | Justification |
|------|-------|--------------------|--------------| 
| Hot | 8–10 | SDR queue, Slack #pipeline-alerts | High intent + high fit = pursue immediately |
| Warm | 5–7 | Marketing nurture sequence, lifecycle email | Fit OR intent strong, not both |
| Cold | 0–4 | Programmatic, low-touch retargeting | Investment too high for unclear ROI |
| Suppressed | — | Drop | Customer, opt-out, recent contact, etc. |

---

## Variants

### Weighted Score (when uniform 1-2pt weights don't match observed behavior)

```clayscript
// Example: industry is more predictive than size in this ICP
icp_score = (fit_industry * 1.5) + fit_size + fit_geo + fit_stack + intent_score
```

Validate weight changes via back-test.

### Account-Level vs Contact-Level

| Level | When |
|-------|------|
| Account | ABM motions, account-keyed routing, account-tier alignment |
| Contact | PLG (user score per signup), inbound (form-fill scoring) |

For combined: `icp_score = (account_score * 0.6) + (contact_score * 0.4)` — tune via back-test.

### PLG Behavioral Score

For product-led motions, replace `fit_*` with:
- `signed_up_with_business_email` (2 pts)
- `invited_teammates` (2 pts)
- `reached_aha_moment` (3 pts)
- `crossed_usage_threshold` (3 pts)

Total: 10 points behavioral. Combine with firmographic fit as separate column.

---

## Anti-Patterns

❌ Scoring before back-testing — pushes wrong leads to sales, erodes trust.
❌ Equal weights across all dimensions when one is clearly more predictive.
❌ Including recency without conditioning on trigger present (you'd credit "trigger 3 days ago" when there's no trigger).
❌ Letting "Cold" band route somewhere costly (SDR queue, paid retargeting).
❌ Not refreshing the rubric quarterly — ICPs drift; scores drift with them.
❌ Hiding the score from sales — sales must see the components, not just the band, to trust it.

---

## Related

- Inputs come from `/clay-abm-list` (account fit) + behavioral source (HubSpot / product events)
- Outputs route into `/clay-outbound` (Hot → SDR) or `/clay-inbound-routing` (form-driven scoring)
- Score drift diagnostics → `/clay-troubleshoot`
