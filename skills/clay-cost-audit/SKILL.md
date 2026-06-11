---
name: clay-cost-audit
description: Portfolio-level audit across ALL running Clay workbooks for Global Rules violations, credit waste, and ROI underperformance. Different from /clay-troubleshoot (one workbook, reactive) — this is proactive, periodic, cross-workbook. Returns a ranked violation list with fix recipes and projected savings. Run monthly or before any Clay tier renewal. Triggers — "Clay cost audit", "audit all workbooks", "Clay portfolio review", "Global Rules audit", "Clay waste audit", "where is credit going", "monthly Clay review", "Clay tier renewal prep", "Clay efficiency review", "/clay-cost-audit".
---

# clay-cost-audit — Portfolio-Wide Cost & Rules Audit

The portfolio-level audit skill. Use when the user wants a **proactive sweep across every Clay workbook** — find Global Rules violations, hidden burn, ROI laggards, and stale auto-runs across the whole account.

Inherits `clay-workbench/SKILL.md` master workflow. Specializes around enumeration → scoring → ranking, not single-workbook composition.

**Difference from `/clay-troubleshoot`**: single workbook, reactive ("X is broken, fix it"). This is portfolio-wide, periodic ("nothing's broken, but where is leverage?").

**Difference from `/clay-credits`**: forecasting and provider comparison are about decisions. This is about discovery.

Run cadence: monthly, plus before any tier renewal or budget review.

---

## Inputs Expected

- **Scope**: all workbooks / all in workspace X / specific tag / specific date range
- **Audit window**: trailing 30d (default) / 90d / since last audit
- **Output mode**: executive summary (1 page) / engineering deep-dive (10+ pages) / Slack digest
- **Threshold for "violation"**: default sensitivity (high) / strict (catch more) / loose (flag only major)
- **Audience**: just Brandon / client stakeholder / ops team

---

## The 12 Audit Checks

Run all 12 against every workbook in scope. Each returns: PASS / WARN / FAIL with severity + estimated impact.

| # | Check | What It Catches | Severity Default |
|---|-------|-----------------|------------------|
| 1 | Two-pass gate present | Paid columns running before any ICP filter | HIGH |
| 2 | Sending Gate present | Sequencer push without `sending_gate_eligible = TRUE` filter | CRITICAL |
| 3 | Free-before-paid order | Cheap signals (industry, employee_count) NOT running before paid (BuiltWith, ZoomInfo) | HIGH |
| 4 | auto_run hygiene | Tables with `auto_run = TRUE` that haven't been verified in last 90d | MEDIUM |
| 5 | Claygent prompt hygiene | Claygent columns missing FALLBACK block / over-sourcing / opus where sonnet works | MEDIUM |
| 6 | Suppression freshness | Customer/opt-out suppression list referenced but not refreshed in last 14d | HIGH |
| 7 | Cost outliers | Workbook in top quartile of $/qualified-row vs portfolio median | MEDIUM |
| 8 | Stale workbooks | Workbook with `auto_run = TRUE` but no downstream conversion (CRM / sequencer) in 60d | HIGH |
| 9 | Duplicate workbook detection | Two workbooks doing materially the same job | MEDIUM |
| 10 | Provider mix correctness | Provider used doesn't match ICP geo / size (e.g., Apollo-only on EU enterprise) | MEDIUM |
| 11 | Dedup hygiene | Signal monitor without dedup_key history table → re-firing alerts | HIGH |
| 12 | ROI ranking | Workbook with $/qualified > 5× portfolio median AND no strategic carve-out | MEDIUM |

### Per-Workbook Violation Output

```
## Workbook: {name} (ID: {id})

| Check | Status | Severity | Detail | Est. Impact (credits/mo) | Fix Recipe |
|-------|--------|----------|--------|--------------------------|------------|
| 1     | FAIL   | HIGH     | BuiltWith runs before icp_gate_qualified | ~8,000 | Add two-pass gate (see /clay-troubleshoot Diagnosis 1) |
| 2     | PASS   | —        | Sending Gate present, filter on push action verified | — | — |
| ...   | ...    | ...      | ...    | ...                      | ...        |

**Workbook subtotal — credits/mo wasted by failed checks**: {N}
**Recommended action**: {FIX | KILL | RE-GATE | OK_AS_IS}
```

### Portfolio Roll-Up

```
## Portfolio Cost Audit — {audit_window}

### Totals
- Workbooks audited: {N}
- Total credits spent: {N} (~${$})
- Total credits estimated wasted: {N} (~${$})
- Waste as % of spend: {X}%

### Critical Findings (CRITICAL severity, must fix this week)
1. {workbook} — {check failed} — {fix} — saves {N} credits/mo
2. ...

### High-Severity Findings (HIGH, fix this month)
1. ...
2. ...

### Medium-Severity Findings (MEDIUM, address next planning cycle)
- {count} workbooks with auto_run stale → review and either re-verify or turn off
- {count} workbooks with Claygent FALLBACK missing → see /clay-claygent-iterator
- ...

### Kill List Candidates
| Workbook | Reason | Last Conversion | Credits/Mo | Recommendation |
|----------|--------|-----------------|------------|----------------|
| ...      | ...    | ...             | ...        | KILL / RE-GATE |

### Quick Wins (sorted by credits saved / time to fix)
1. {fix} → saves {N} credits/mo → {minutes} to apply
2. ...

### Projected Savings
- If CRITICAL fixed: ${X}/mo
- If HIGH fixed:     ${Y}/mo (cumulative ${X+Y})
- If MEDIUM fixed:   ${Z}/mo (cumulative ${X+Y+Z})

### Tier Recommendation
- Current tier: {tier}
- Current monthly burn (post-fix projection): ${$}
- Recommended tier: {same / upgrade / downgrade}
- Estimated own-API-key savings opportunity: ${$}
```

---

## Step 5 — Execution

### MCP Path

```
1. mcp__claude_ai_Clay__get-credits-available → current balance
2. mcp__claude_ai_Clay__list_subroutines → enumerate every running workbook + subroutine in scope
3. For each workbook:
   - mcp__claude_ai_Clay__get-task on recent runs → credits spent
   - mcp__claude_ai_Clay__query-objects on the workbook's qualified-row column → conversion counts
   - Inspect column-by-column spec (where MCP allows)
4. Run 12-check audit per workbook
5. Aggregate into portfolio roll-up
6. Cross-reference cost data with resources/credit-cost-table.md
```

### Manual Walkthrough

If MCP introspection is limited:

```
1. Open Clay dashboard → analytics view → trailing 30d
2. Export per-workbook credit usage to CSV
3. For each workbook in top 50% of spend:
   - Open in Clay UI
   - Manually walk the 12 checks
   - Note violations + estimated impact
4. Aggregate findings in markdown
5. Cross-reference workbook outputs with CRM/sequencer pipeline data for ROI ranking
```

---

## Severity Scoring Rules

```
CRITICAL — Active rule violation causing immediate harm (sender reputation, compliance risk, customer-facing error)
HIGH     — Active waste >2,000 credits/mo OR will cause harm if scaled
MEDIUM   — Active waste 500–2,000 credits/mo OR clear quality risk
LOW      — Minor inefficiency, advisory only
```

### Auto-escalation rules

- Any sequencer-push action without Sending Gate → CRITICAL regardless of volume.
- auto_run = TRUE on a workbook touching customer suppression list that hasn't refreshed in 30d → CRITICAL.
- More than 25% of monthly burn going to a single workbook with no measurable downstream conversion → HIGH.

---

## Deliverable Formats

### Executive Summary (1 page)

```
- Portfolio spend: ${X} | Wasted: ${Y} ({Z}%)
- Critical: {N} | High: {N} | Medium: {N}
- Top 3 fixes → save ${$}/mo
- Recommendation: {fix / upgrade / downgrade / restructure}
```

### Engineering Deep-Dive (10+ pages)

Full per-workbook section with all 12 checks, fix recipes, and credit-savings math. Shareable with the team that will do the work.

### Slack Digest

```
🧾 Monthly Clay Audit — {date}

📊 ${X} spent · ${Y} wasted ({Z}%)
🔴 {N} critical · 🟠 {N} high · 🟡 {N} medium

Top fixes this week:
1. {fix} → ${$}/mo · {workbook}
2. {fix} → ${$}/mo · {workbook}
3. {fix} → ${$}/mo · {workbook}

Full report: {link}
```

---

## Verify-and-Handoff Checklist

- [ ] Every workbook in scope was actually checked (no silent skips)
- [ ] Credit-spend totals reconcile against Clay's own analytics dashboard
- [ ] Conversion data sourced from CRM, not estimated
- [ ] Each violation has an estimated impact in credits/mo (not just "high")
- [ ] Each violation has a fix recipe (link to relevant sub-skill section)
- [ ] Critical findings have an owner + due date assigned in deliverable
- [ ] Quick Wins list is sorted by leverage (savings / time)
- [ ] Tier recommendation backed by post-fix forecast, not pre-fix spend
- [ ] Stored: {timestamp, audit_window, total_findings, projected_savings} so trend can be tracked over months

---

## Use-Case Variants

| Cadence / Use Case | Adjustments |
|--------------------|-------------|
| Monthly recurring | Default — full 12 checks, executive summary + engineering deep-dive |
| Pre-tier-renewal | Add tier-comparison sub-section; model 12-month cost at current vs upgraded/downgraded tier |
| Pre-board / pre-investor review | Executive summary only; emphasize ROI + Pipeline / $ Spent |
| Post-team-transition (new ops owner) | Add stale-workbook section + owner mapping |
| Annual GTM planning | Pair with `/clay-credits` ROI ranking + workbook-kill recommendations |
| Quarterly cleanup sprint | Filter to MEDIUM + HIGH only; produce work-tracker import file |

---

## Anti-Patterns

❌ Auditing without conversion data — turns into a credit-spend report, not an ROI report.
❌ Flagging every Claygent column missing FALLBACK as CRITICAL — it's HIGH unless live customer-facing.
❌ Recommending tier downgrade based on pre-fix spend — savings won't materialize if violations aren't fixed first.
❌ Skipping the manual cross-check on Clay's dashboard totals — MCP-side aggregation can lag.
❌ Treating duplicate-workbook findings as automatic kills — sometimes intentional (different clients, A/B test).
❌ Running audit silently in the background — always confirm scope with user before sweeping all workbooks (some are intentionally lightweight / experimental).

---

## Related

- For fixing a flagged workbook → `/clay-troubleshoot` (per-workbook diagnostic + fix recipe).
- For provider-mix comparison flagged in checks 3 + 10 → `/clay-credits`.
- For Claygent-prompt fixes flagged in check 5 → `/clay-claygent-iterator`.
- For suppression-list freshness check 6 → `/clay-data-hygiene` (the always-on health monitor).
- For dedup hygiene flagged in check 11 → `/clay-signal-monitor` (signal_history table pattern).
- For saving a fixed workbook as a reusable golden template → `/clay-template-library`.
