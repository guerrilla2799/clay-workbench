---
name: clay-troubleshoot
description: Diagnose broken, expensive, or under-performing Clay workbooks. Root-causes high credit burn, low match rates, formula errors, silent failures, dedup issues, sequencer push failures, and ICP drift. Returns a 4-part diagnostic — symptom → root cause → fix → cost savings estimate. Triggers — "Clay is expensive", "match rate is low", "Clay error", "credits burning", "wrong rows enriched", "Clay broken", "Claygent blank", "Sending Gate skipped", "Clay troubleshoot", "/clay-troubleshoot".
---

# clay-troubleshoot — Diagnose & Fix

The diagnostic skill. Run this when something is wrong with an existing Clay workbook — costs too high, match rates too low, formulas misbehaving, sequencer pushing the wrong rows.

Inherits master workflow but specializes: skips intake (focuses on diagnosis), specializes step 3 (root cause) and step 5 (fix execution).

---

## Inputs Expected

- **Symptom**: what's broken? (cost / match rate / data quality / push failure / wrong destination)
- **Table or subroutine ID**: the offender
- **Recent change**: any column added or condition changed in last 7 days?
- **Volume baseline**: rows in last run, rows historically

---

## Diagnostic Framework

Use this triage tree:

```
Symptom: "Clay is too expensive"
├── Is there an ICP gate before paid columns?
│   ├── NO → Root cause: Global Rule #1 violation. Fix: add two-pass gate.
│   └── YES → Continue
├── Is the gate using cheap signals first?
│   ├── NO (running BuiltWith before industry filter) → Fix: reorder columns
│   └── YES → Continue
├── Is auto_run = TRUE during construction?
│   ├── YES → Fix: turn off until verified
│   └── NO → Continue
├── Are enrichments running on already-enriched rows?
│   ├── YES → Fix: add freshness check (skip if enriched < 30d)
│   └── NO → Continue
├── Are waterfalls graceful-exiting?
│   ├── NO (running every step always) → Fix: add run conditions
│   └── YES → Continue
└── Are Claygent prompts crawling >5 sources each?
    └── Fix: cap max_sources in prompt

Symptom: "Match rate is low"
├── Is input data clean?
│   ├── Test 25 rows by hand. Match rate <30% suggests dirty input
│   └── If dirty: fix at source (most often domain parsing / name format)
├── Is the waterfall provider mix wrong for the ICP?
│   ├── US-skewed providers on EU list → swap for Datagma/Dropcontact
│   ├── SMB-skewed providers on enterprise list → add ZoomInfo own-key path
│   └── Etc.
├── Are providers running in parallel instead of waterfall?
│   └── Fix: add run conditions for graceful exit
└── Is verification rejecting good emails?
    └── ZeroBounce may flag catch-all valid as "unknown" — review threshold

Symptom: "Wrong rows being enriched"
├── ICP gate formula is incorrect → review and re-test
├── Source list has bad data → pre-clean before Clay
└── Suppression list out of date → refresh customer/opt-out tables

Symptom: "Claygent returns blank"
└── Almost always: action key `"ai"` instead of `"use-ai"` (silent input drop)

Symptom: "Sequencer push not running"
├── Sending Gate filter not set on action?
├── auto_run = FALSE on action?
├── Sequencer API key expired or rate limited?
└── Filter formula returns FALSE for all rows?

Symptom: "Slack alert not firing"
├── Wrong channel name (must be exact)?
├── Slack integration disconnected?
└── Filter formula too strict?

Symptom: "HubSpot duplicates"
└── Dedup key not set OR set to both ID and email (use ONE)

Symptom: "Webhook source not appending rows"
├── Webhook URL changed after save → regenerate
├── Auth header mismatch → check headers
└── Payload structure changed at source → re-map fields

Symptom: "Formula column returns NULL silently"
└── Empty formula OR syntax error in formula → re-open editor and validate
```

---

## Standard Diagnostic Output Format

When the user runs this skill, return:

```
## Symptom
{user-reported problem}

## Diagnosis
- {root cause 1 — most likely}
- {root cause 2 — secondary suspect}
- {root cause 3 — edge case}

## Verification Steps (in order)
1. {check this first — cheapest to verify}
2. {check this next}
3. {check this last — most expensive to verify}

## Fix Recipe
{specific Clay UI steps OR MCP calls to repair}

## Cost / Match-Rate Impact Estimate
- Before: {current state}
- After fix: {expected state}
- Annualized savings (if cost issue): {$ estimate}
- Match-rate gain (if quality issue): {% estimate}

## Prevention
{which Global Rule applies; how to prevent this category of issue}
```

---

## Step 3 — Common Diagnoses with Fix Recipes

### Diagnosis 1: "Burning credits on disqualified rows"

**Symptoms**: Total credits / qualified rows ratio is 5x+ what you expected.

**Root cause**: No two-pass gate. Paid enrichment running before ICP filter.

**Fix**:
```
1. Identify the cheapest signals: industry, employee_count, hq_country (all from Clay native).
2. Add a `pass_1_qualified` formula column right after these.
3. On EVERY paid enrichment column, add Run Condition: `pass_1_qualified = TRUE`.
4. Add `icp_gate_qualified` after the expensive enrichments.
5. On Claygent, AI, and downstream columns, Run Condition: `icp_gate_qualified = TRUE`.
6. Re-run on 100-row sample. Compare credits-spent to pre-fix.
```

**Typical impact**: 40–60% credit reduction.

### Diagnosis 2: "Email match rate ~30% on big-name accounts"

**Symptoms**: Big-company contacts (Stripe, Salesforce, Atlassian) returning no email even though contacts exist.

**Root cause**: Apollo / Findymail under-index on large public companies due to GDPR + opt-outs. Need premium providers.

**Fix**:
```
1. Add Dropcontact as final waterfall step → match rate boosts ~15%.
2. Or add LinkedIn Sales Nav own-key path → ~25% boost (best for >5k employee accounts).
3. For target accounts specifically: route to manual Claygent research → "find email format for {company_name} → construct + verify."
```

### Diagnosis 3: "Claygent returns empty / blank"

**Symptoms**: AI columns show blank for every row.

**Root cause**: Action key typo — `"ai"` instead of `"use-ai"`. Silent input drop.

**Fix**:
```
1. Open the column → Settings → Inspect raw JSON.
2. Confirm actionKey is "use-ai".
3. If "ai", rebuild the column from the Claygent template (don't try to edit in place — Clay quirks).
4. Re-run on 5-row sample.
```

### Diagnosis 4: "Sequencer pushing unqualified rows"

**Symptoms**: SDRs reporting bad-fit prospects in their sequence.

**Root cause**: Sending Gate filter not set on the push action.

**Fix**:
```
1. Open the push action in Clay.
2. Settings → Run Condition → set to `sending_gate_eligible = TRUE`.
3. Verify the sending_gate_eligible column exists and is well-formed.
4. Pull the last 50 pushed rows; verify they all had sending_gate_eligible = TRUE.
5. If some had FALSE, manually pause those in the sequencer.
```

### Diagnosis 5: "Workbook randomly fails"

**Symptoms**: Random rows error out, no clear pattern.

**Root cause**: Usually one of: (a) rate limit on a provider, (b) malformed input in source data, (c) Claygent timeout on heavy crawls.

**Fix**:
```
1. mcp__claude_ai_Clay__get-task on the failing job.
2. Look at error_message field in failed rows.
3. Rate limit → throttle or upgrade provider tier.
4. Malformed input → add input validation formula column upstream.
5. Claygent timeout → cap max_sources, simplify prompt.
```

### Diagnosis 6: "Costs spiking unexpectedly"

**Symptoms**: Daily credit burn jumped 3x with no obvious cause.

**Root cause investigation**:
```
1. Identify which workbook caused the spike (Clay analytics dashboard).
2. Compare row count vs historical — is auto_run pulling more inbound than usual?
3. Check if a previously-gated column had its gate removed.
4. Check if a Claygent prompt was changed to crawl more sources.
5. Check if a source list contains test data or duplicates.
```

**Fix** depends on root cause but commonly: re-add the gate, reduce Claygent source cap, dedup the source.

### Diagnosis 7: "ICP score distribution skewed"

**Symptoms**: Suddenly everyone is "Hot" or "Cold" — distribution unrecognizable.

**Root cause**: Either ICP definition shifted, suppression list outdated, or trigger source returning false positives.

**Fix**:
```
1. mcp__claude_ai_Clay__query-objects on the score column for last 30d.
2. Compare distribution to baseline 90d ago.
3. Identify which sub-score component shifted (fit_industry, intent_trigger, etc.).
4. Inspect the upstream — is the input data changing shape?
5. Recalibrate the formula or fix the input.
6. Run back-test on closed-won deals to verify rubric still discriminates.
```

---

## Step 5 — Execution

```
1. mcp__claude_ai_Clay__query-objects on the offending table
2. Pull representative sample of problem rows
3. Apply triage tree above
4. Output diagnostic in standard format
5. Offer to apply fix (if MCP-supported) or walk through manually
```

---

## Quick Reference — Symptom-to-Cause

| Symptom | First Suspect |
|---------|--------------|
| Expensive | Two-pass gate missing |
| Low match rate | Wrong provider mix for ICP |
| Claygent blank | Action key typo `"ai"` not `"use-ai"` |
| Sequencer bad rows | Sending Gate not set on action |
| Random failures | Provider rate limit or malformed input |
| HubSpot duplicates | Dedup key misconfig |
| Webhook silent | URL changed or auth header wrong |
| Slack silent | Channel name typo or filter too strict |
| Score skewed | Input shape change or suppression stale |
| Spike in costs | Lost gate or Claygent prompt grew |

---

## Related

- After fix → re-validate via the original sub-skill's verify-and-handoff checklist.
- For systemic issues across many workbooks → review `resources/global-rules.md` enforcement.
- For provider-specific quirks → see `providers/enrichment/*.md`.
