---
name: clay-credits
description: Standalone Clay credit + cost forecasting and provider comparison. Returns current balance, projected burn at current cadence, cost-per-qualified-row by workbook, provider-mix cost comparison for a given job, and ROI per workbook. Use BEFORE building, scaling, or signing a new Clay contract — not reactively. Triggers — "Clay credits", "Clay balance", "credit forecast", "credit burn projection", "provider cost comparison", "cost per qualified row", "Clay ROI", "compare Apollo vs Findymail", "should I upgrade Clay plan", "/clay-credits".
---

# clay-credits — Credit Forecasting & Provider Cost Comparison

The proactive cost skill. Use when the user wants to **plan, forecast, or compare** — not when something is already burning (that's `/clay-troubleshoot`).

Use cases:
- Pre-flight a new workbook design at scale
- Decide between provider mixes for the same job (Apollo vs Findymail + Dropcontact, etc.)
- Forecast monthly burn for budget conversations
- Compute cost-per-qualified-row across multiple workbooks for ROI ranking
- Decide whether to upgrade Clay tier or change own-API-key allocations

Inherits `clay-workbench/SKILL.md` master workflow but specializes around forecasting + comparison, not workbook composition.

---

## Inputs Expected

For **forecasting**:
- Workbook ID or table descriptor (existing or planned)
- Row count for the run (or rows/day for recurring)
- Cadence (one-shot, daily, weekly, on-source-update)
- Column-by-column spec (or pull from existing workbook)
- Tier (Starter / Pro / Enterprise / own-API-key mix)

For **comparison**:
- The job: "enrich N emails", "find N phones", "research N accounts", etc.
- Constraints: ICP geo, ICP size band, match-rate threshold, Clay-managed vs own-API-key
- Candidate provider mixes (or let this skill propose them)

For **ROI**:
- List of workbook IDs to compare
- Conversion data: qualified rows / meetings / pipeline / closed-won attributable
- Time window for the comparison

---

## Forecast Output Format

```
## Credit Forecast — {workbook_name}

### Current State
- Balance: {N} credits (~${$})
- Tier: {Starter|Pro|Enterprise} (~${$}/mo)
- Burn last 30d: {N} credits/day average · {N} peak
- Days until exhaustion at current cadence: {N}

### Workbook Forecast
| Column | Cost/Row | Run Condition | Effective Cost/Source Row |
|--------|----------|---------------|--------------------------|
| ...    | ...      | ...           | ...                      |
| **TOTAL** |       |               | {X} credits/row          |

### Run Projection
- Row count: {N}
- Cost per run: {X} credits ≈ ${Y}
- Cadence: {one-shot|daily|weekly}
- Monthly cost at this cadence: ${Z}

### Pre-Flight Verdict
- {PROCEED | TIGHTEN GATES | UPGRADE TIER | DO NOT RUN}
- Reason: {one sentence}
```

---

## Comparison Output Format

```
## Provider Mix Comparison — {job description}

### Constraints
- Job: {find emails for N contacts | research N accounts | etc.}
- ICP: {geo, size, industry}
- Required match rate: ≥ {X}%
- Clay-managed only OR own-API-key allowed

### Candidate Mixes

| Mix # | Providers (waterfall order) | Expected match rate | Credits/row | $/row at tier | Notes |
|-------|----------------------------|---------------------|-------------|---------------|-------|
| A     | Apollo → Findymail         | ~70%                | ~3          | ~$0.03        | US-skewed |
| B     | Apollo → Findymail → Dropcontact | ~82%          | ~5          | ~$0.05        | Better EU |
| C     | ZoomInfo (own-key) → Apollo | ~88%               | ~1 (Clay) + own-key cost | varies | Best large-enterprise |

### Recommendation
{which mix, why, when to switch}

### Cost @ Volume
| Mix | 1k rows | 10k rows | 100k rows |
|-----|---------|----------|-----------|
| A   | ...     | ...      | ...       |
| B   | ...     | ...      | ...       |
| C   | ...     | ...      | ...       |
```

---

## ROI Output Format

```
## Workbook ROI — last {window}

| Workbook | Credits Spent | $ Cost | Qualified Rows | $/Qualified | Meetings | Pipeline ($) | Pipeline / $ Spent |
|----------|---------------|--------|----------------|-------------|----------|--------------|--------------------|
| ABM-T1   | 12,400        | $124   | 87             | $1.43       | 14       | $420k        | 3,387×             |
| Inbound  | 8,200         | $82    | 230            | $0.36       | 22       | $180k        | 2,195×             |
| Outbound | 31,000        | $310   | 412            | $0.75       | 18       | $90k         | 290×               |

### Top Performer
{workbook + reason}

### Underperformer
{workbook + recommended action — kill / re-gate / re-target}

### Reallocation Recommendation
- Cut: {what to stop}
- Reinvest in: {what to expand}
- Estimated next-quarter ROI lift: {X}×
```

---

## Step 5 — Execution

### MCP Path

```
1. mcp__claude_ai_Clay__get-credits-available → current balance
2. mcp__claude_ai_Clay__list_subroutines → enumerate workbooks
3. For each workbook in scope:
   - mcp__claude_ai_Clay__get-task on recent runs → credits actually spent
   - mcp__claude_ai_Clay__query-objects → qualified-row count + downstream conversion data
4. Cross-reference with resources/credit-cost-table.md for per-column estimates
5. Compute forecast / comparison / ROI tables per output format above
```

### Manual Walkthrough

If MCP credit usage history is unavailable per-column:

```
1. Open Clay analytics dashboard
2. Filter by workbook + time window
3. Export credit-usage CSV
4. Map credits-per-column to resources/credit-cost-table.md
5. Cross-reference with CRM pipeline data (HubSpot / Salesforce) for attributed conversion
6. Build the comparison or ROI table above
```

---

## Key Decision Frameworks

### When to upgrade tier
- Current monthly burn ≥80% of plan ceiling for 2+ consecutive months
- OR forecasted burn for next planned workbook would push >100% of ceiling
- OR own-API-key migration for ≥1 high-volume provider would be cheaper than tier upgrade (calculate both)

### When to switch from Clay-managed to own-API-key
- A single provider accounts for >40% of monthly burn
- Own-key license cost < (provider's Clay-managed cost × monthly volume × 0.8)
- User has internal resources to manage rate limits and key rotation

### When to kill a workbook
- $/qualified row > 5× the median across portfolio AND no strategic justification
- Pipeline / $ spent < 50× AND running > 90 days
- Conversion data missing entirely (can't measure → can't justify)

### When to tighten gates instead of killing
- $/qualified row in top quartile but match rate also high → likely gate issue, not workbook concept
- Trigger event recency too loose → tighten to ≤14d
- ICP size band too broad → narrow before recommending kill

---

## Verify-and-Handoff Checklist

- [ ] Current Clay balance pulled fresh (not stale)
- [ ] Per-column cost estimates cross-referenced with resources/credit-cost-table.md
- [ ] Forecast accounts for two-pass gates (don't multiply paid cost × all source rows)
- [ ] Comparison mixes include "do nothing / status quo" baseline
- [ ] ROI numerator (pipeline / closed-won) sourced from CRM, not estimated
- [ ] Recommendation is opinionated (one mix, one verdict — not a buffet)
- [ ] Output destination noted (board deck / Slack share / internal note)

---

## Common Comparison Scenarios

| Job | Default Mix | Premium Mix | Budget Mix |
|-----|-------------|-------------|------------|
| Email find, US SMB | Apollo → Findymail | + Dropcontact | Apollo only |
| Email find, US enterprise | Apollo → Findymail → ZoomInfo (own) | + Lusha (own) | Apollo only |
| Email find, EU | Dropcontact → Datagma → Findymail | + Cognism (own) | Dropcontact only |
| Phone find | Cognism (own) → Lusha (own) | + Datagma | Apollo only |
| Account firmographics | find-company (Clay native) | + People Data Labs | find-company only |
| Trigger events | Predictleads | + Champify + UserGems | none — Claygent only |
| Tech stack | Wappalyzer | BuiltWith full | Claygent only |
| Intent | none — too noisy alone | 6sense + G2 + Bombora | none |

Tier columns assume Pro tier pricing — recalc per user's actual tier.

---

## Anti-Patterns

❌ Forecasting without two-pass gates — paid cost × every source row is always wrong; use cost × qualified-after-pass-1.
❌ ROI ranking on credits spent only — without conversion data the ranking is fictional.
❌ Recommending tier upgrade without calculating own-API-key alternative first.
❌ "Do nothing" baseline missing from comparison — without it, every mix wins by definition.
❌ Comparing providers for a job their tier doesn't actually win at (US SMB vs EU enterprise have totally different winning mixes).
❌ Stale balance — always pull fresh; reading from memory is wrong as soon as a run fires.

---

## Related

- For reactive cost diagnosis on a running workbook → `/clay-troubleshoot`.
- For portfolio-wide audit of Global Rules violations driving cost → `/clay-cost-audit`.
- For pre-Clay list hygiene that reduces forecast cost upstream → `/clay-list-clean`.
- For Claygent-specific cost tuning → `/clay-claygent-iterator`.
