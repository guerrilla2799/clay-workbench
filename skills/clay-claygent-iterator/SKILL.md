---
name: clay-claygent-iterator
description: Refine Claygent (Clay AI research agent) prompts through a structured 5 → 25 → 100 row iteration loop. Diagnoses fabrication, blanks, off-topic answers, source crawl bloat, and cost overruns. Returns a tuned prompt with verified coverage rate, hallucination rate, and credit cost per row. Mandatory before scaling any Claygent column past 25 rows. Triggers — "iterate Claygent prompt", "tune Claygent", "refine Claygent prompt", "Claygent quality", "Claygent prompt engineering", "Claygent test", "5/25/100 loop", "Claygent fabrication", "/clay-claygent-iterator".
---

# clay-claygent-iterator — Tune Claygent Prompts

The quality skill for **Claygent prompt iteration**. Loads when a Claygent column is being built, when an existing column is underperforming (blanks, hallucinations, off-topic, too expensive), or when the user is scaling a research workbook from sample to full run.

Inherits `clay-workbench/SKILL.md` master workflow but specializes the entire flow around prompt iteration, not workbook composition.

**Always run this before flipping a Claygent-heavy workbook to full-run mode.** Cost of skipping: 10x credits + fabrication at scale.

---

## Inputs Expected

- **Target column**: Claygent column being tuned (existing or new)
- **Column purpose**: what the column should output (one sentence)
- **Input fields**: what data the prompt receives (firmographics, name, content URL, etc.)
- **Existing prompt (if any)**: paste current ROLE/CONTEXT/TASK/FORMAT/FALLBACK text
- **Model**: sonnet (default) / opus (for high-leverage outputs like first lines)
- **Max sources**: how many web sources to allow Claygent to crawl (default 3, hard cap 10)
- **Budget per row**: credit ceiling for this column (e.g., 8 credits)
- **Sample dataset**: link to 5/25/100 row set OR Clay query that produces it

---

## The 5 / 25 / 100 Loop

### Stage 1 — 5 Rows (Hand-Validated)

```
Goal: verify prompt produces the RIGHT KIND of output on diverse inputs.

Steps:
1. Run prompt on 5 deliberately-diverse rows (mix big/small co, US/EU, common/edge title, etc.)
2. Read every single output by hand
3. Score each: PASS / BLANK / OFF-TOPIC / FABRICATED / TOO-LONG / TOO-VAGUE
4. Inspect token cost per row (Clay shows credits used)
5. If <4/5 PASS → revise the prompt (don't proceed to 25)

Iteration on prompt structure at this stage:
- Missing ROLE → add it
- Missing context fields → name them in CONTEXT block
- Vague TASK → tighten to one specific deliverable
- Missing FORMAT → add output structure constraint
- Missing FALLBACK → add the INSUFFICIENT_SIGNAL exit (THE most common fix)
- Source bloat → cap max_sources lower
- Hallucination → add "Cite the source URL inline for each claim" requirement
```

**Exit gate**: 4–5 of 5 PASS, cost ≤ budget per row, fallback fires at least once across 5 if any row has thin input.

### Stage 2 — 25 Rows (Pattern Validation)

```
Goal: surface failure modes that only appear at slightly higher N.

Steps:
1. Run tuned prompt on 25 rows
2. Tally outcome distribution: % PASS / % BLANK / % FABRICATED / % FALLBACK
3. Inspect ALL non-PASS outputs (not just PASS)
4. Confirm cost per row holds at budget × 25
5. Spot-check 5 random PASS rows — are they actually right, or do they just look right?

Iteration on prompt logic at this stage:
- BLANK rate > 5% → CONTEXT block missing required field OR fallback misfiring
- FABRICATED rate > 0% → STOP and add explicit "cite sources or return INSUFFICIENT_SIGNAL" rule
- FALLBACK rate > 40% → input gate is too loose (gate the column with a formula on input quality)
- TOO-LONG rate > 10% → tighten FORMAT word cap
- Cost > 1.5× budget → reduce max_sources, drop model from opus to sonnet
```

**Exit gate**: ≥85% PASS, 0% FABRICATED, fallback rate within expectation, cost within 20% of budget.

### Stage 3 — 100 Rows (Scale Validation)

```
Goal: prove the prompt holds at 4x volume before going to 500+/full.

Steps:
1. Run on 100 rows
2. Compute final scorecard: PASS %, BLANK %, FABRICATED %, FALLBACK %, mean credits/row, p95 credits/row
3. Manual spot-check: 10 random rows + 5 lowest-credit rows + 5 highest-credit rows
4. Calculate full-run projection: (100-row credit cost) × (full-row-count / 100) = full estimate

If projection > balance × 0.5 → DO NOT proceed. Tighten prompt further or reduce row count.
```

**Exit gate**: ≥85% PASS, 0% FABRICATED in the 20-row spot-check, p95 credits/row ≤ 2× budget, full-run projection within 50% of balance.

If all three gates pass → cleared for full run.
If any gate fails → return to Stage 1 with the new failure mode.

---

## Prompt Anatomy (Required Structure)

Every Claygent prompt must include all 5 blocks. Missing any one is the most common cause of failure.

```
ROLE: <one sentence persona — gives Claygent a frame>
   Example: "Senior B2B GTM analyst preparing a one-line research summary for an AE."

CONTEXT: <name every input field by variable>
   Example:
   - Account: {company_name} ({industry}, {employee_count} employees)
   - Public website: {company_domain}
   - LinkedIn: {linkedin_company_url}

TASK: <single, specific deliverable — one sentence>
   Example: "Identify the company's top 3 stated strategic priorities for the current fiscal year."

FORMAT: <exact output structure + length constraint>
   Example: "3 bullets, max 25 words each. No preamble. Cite source URL inline after each bullet."

FALLBACK: <explicit exit condition when input is insufficient>
   Example: "If fewer than 2 strategic priorities can be sourced from public materials, return 'INSUFFICIENT_SIGNAL' and stop. Do not infer or invent."
```

The FALLBACK is the single most important block. Without it, Claygent fabricates on thin input rows.

---

## Common Failure Modes — Diagnoses & Fixes

| Failure Mode | Likely Cause | Fix |
|--------------|-------------|-----|
| All rows BLANK | Action key is `"ai"` instead of `"use-ai"` | Rebuild column from scratch — Clay quirk, can't edit in place |
| Some rows BLANK | CONTEXT field empty for those inputs | Gate the column or fix upstream input |
| FABRICATED claims (made-up news, fake quotes) | No source-citation requirement; no FALLBACK | Add "cite source URL inline" + INSUFFICIENT_SIGNAL fallback |
| Generic / vague outputs ("they prioritize growth and innovation") | TASK too broad | Constrain to ONE specific deliverable + named output structure |
| Off-topic outputs | Multiple TASKs in one prompt | Split into 2 columns |
| Too-long outputs | No word cap in FORMAT | Add hard length constraint ("max 50 words") |
| Cost 3x budget | Crawling too many sources / model = opus when sonnet works | Cap max_sources = 3; downgrade model |
| Inconsistent format across rows | FORMAT block weak or absent | Show an explicit example of desired output in FORMAT |
| Hallucinated URLs in output | Claygent invented citations | Require "Return only URLs Claygent visited. If none verifiable, return INSUFFICIENT_SIGNAL" |
| FALLBACK never fires | Gate too loose OR fallback condition mis-specified | Tighten FALLBACK to a quantifiable threshold (≥2 sources required) |
| Different output on same row when re-run | Temperature too high / no determinism guidance | Add "Return the SAME output if the same inputs are provided. Do not vary phrasing." |

---

## Step 5 — Execution

### MCP Path

```
1. mcp__claude_ai_Clay__get-credits-available
2. mcp__claude_ai_Clay__query-objects on the target Claygent column for sample rows
3. For each iteration:
   - Update the column's prompt in Clay UI (no MCP for prompt edits currently)
   - mcp__claude_ai_Clay__run_subroutine on the 5-row sample table
   - Pull outputs via query-objects
   - Score by hand → iterate prompt
4. When 5/5 PASS → expand to 25
5. mcp__claude_ai_Clay__get-task for cost per row
```

### Manual Walkthrough

1. Pick 5 rows that span the input diversity (don't all be Tier 1 US tech — include EU SMB and edge cases)
2. Open the Claygent column → edit prompt
3. Paste the 5-block structure with placeholders for inputs
4. Run column on 5 rows (`auto_run = false`, manually trigger)
5. Open every output → score (PASS / BLANK / OFF-TOPIC / FABRICATED / TOO-LONG / TOO-VAGUE)
6. Note credits spent
7. Iterate prompt → re-run → re-score
8. Once 4–5 PASS → repeat at 25 rows → repeat at 100 rows

---

## Output Format (Standard Deliverable)

Return this scorecard when the loop concludes:

```
## Claygent Iteration Report — {column_name}

### Final Prompt
{full 5-block prompt}

### Configuration
- Model: {sonnet|opus}
- Max sources: {n}
- Run condition: {formula}

### Scorecard
| Stage | Rows | PASS % | BLANK % | FABRICATED % | FALLBACK % | Mean credits/row | p95 credits/row |
|-------|------|--------|---------|--------------|------------|------------------|-----------------|
| 5     |   5  | ...    | ...     | ...          | ...        | ...              | ...             |
| 25    |  25  | ...    | ...     | ...          | ...        | ...              | ...             |
| 100   | 100  | ...    | ...     | ...          | ...        | ...              | ...             |

### Full-Run Projection
- Estimated credits for full run ({N} rows): {X}
- ≈ ${Y} at current tier
- Current balance: {Z}
- Cleared for full run? {Y/N}

### Known Failure Modes Remaining
{list any not-fully-resolved issues + recommended mitigation}

### Sample Outputs
- 3 PASS samples (representative)
- All FABRICATED / OFF-TOPIC samples from 100-row run
```

---

## Verify-and-Handoff Checklist

- [ ] Stage 1 (5 rows): ≥4/5 PASS, hand-validated
- [ ] Stage 2 (25 rows): ≥85% PASS, 0% FABRICATED, fallback fires at least once
- [ ] Stage 3 (100 rows): ≥85% PASS, 0% FABRICATED in spot-check, cost within 20% of budget
- [ ] Full-run projection within 50% of balance
- [ ] Final prompt includes all 5 blocks (ROLE / CONTEXT / TASK / FORMAT / FALLBACK)
- [ ] Source citation requirement present
- [ ] Determinism guidance present (for prompts that should not vary)
- [ ] Iteration report stored in workbook notes / Notion (so future tuning has history)

---

## Common Prompt Templates (Starting Points)

### Account fact-finding (factual)

```
ROLE: Senior B2B research analyst pulling verified public facts.
CONTEXT: Company: {company_name} ({company_domain}). Industry: {industry}.
TASK: Identify the company's current CEO and their tenure in role (months).
FORMAT: "Name: <name> · Tenure: <months>m · Source: <url>". One line, no preamble.
FALLBACK: If CEO cannot be verified from at least 2 sources, return "INSUFFICIENT_SIGNAL" and stop.
```

### Strategic synthesis (interpretive)

```
ROLE: Senior B2B GTM strategist preparing a one-pager for an executive ABM play.
CONTEXT: Account: {company_name}. Recent news: {recent_news_90d}. Hiring: {hiring_posture}. Leadership: {leadership_team}.
TASK: Generate the most likely entry-point hypothesis (one champion + one pain + one proof point).
FORMAT: 3 bullets, max 30 words each. No preamble.
FALLBACK: If fewer than 2 inputs contain useful data, return "INSUFFICIENT_SIGNAL — recommend manual research" and stop.
```

### First-line personalization (highest-leverage)

```
ROLE: Senior B2B GTM strategist drafting the first line of a cold message that earns a reply.
CONTEXT: Prospect: {full_name}, {title} at {company_name}. Recent LinkedIn: {recent_posts_90d}. Public POVs: {recent_public_content}.
TASK: Write ONE personalized opening line referencing something specific they said or did publicly in the last 90d.
FORMAT: Single line, <25 words. Avoid: "I came across", "I saw your post on", "loved your insight on", "your work in X is impressive".
FALLBACK: If no specific public artifact in last 90d, return "NO_HOOK — fall back to account-level angle" and stop.
```

---

## Anti-Patterns

❌ Skipping the 5-row stage and going straight to 25 — fabrications hide in volume.
❌ Skipping the FALLBACK block — thin input rows fabricate confidently.
❌ Opus for every column — sonnet is fine 80% of the time; opus is for first-line and exec-prep columns.
❌ Allowing max_sources > 5 unless absolutely needed — cost grows linearly.
❌ "Trust me, it's working" without the scorecard — hallucinations are invisible without spot-checks.
❌ Editing prompt in place when output is consistently blank — Clay sometimes caches; rebuild the column.
❌ Iterating on the prompt without changing one variable at a time — you don't learn what worked.

---

## Related

- Every research-heavy sub-skill should call this BEFORE scaling past 25 rows: `/clay-account-research`, `/clay-prospect-research`, `/clay-outbound` (for personalization columns).
- For broken Claygent columns (blanks, errors) → `/clay-troubleshoot` (faster diagnosis).
- For burn-rate audit after iteration → `/clay-troubleshoot`.
