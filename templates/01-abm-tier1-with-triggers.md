# Golden Workbook 01 — ABM Tier 1 with Triggers

A production-ready Clay workbook for building a tiered ABM target account list with trigger-event qualification, route-to logic, and SDR queue handoff. Mirrors the pattern used in the Dodge ENT ABM cadence.

**Use when**: building a net-new account list for outbound (ABM), expansion list, or signal-driven account workflow.

**Complete time to build (manual)**: ~25 minutes.
**Complete time (MCP-assisted)**: ~5 minutes for a saved subroutine reuse.

---

## Intake Answers (Example)

| Question | Answer |
|----------|--------|
| Source | Apollo Search URL — Enterprise B2B SaaS, 250-2500 employees, US/UK/CA |
| Input fields | company_domain, company_name |
| Enrichments | Industry, employee_count, revenue_range, funding_stage, tech_stack, trigger_event |
| Gates | Industry ∈ [B2B SaaS, Fintech, MarTech]; emp 250–2500; geo US/UK/CA; trigger required (recency ≤90d) |
| AI columns | One Claygent — pain-point research from website + funding announcement |
| Outputs | HubSpot (account create) + Slack to #abm-tier1 |
| Auto-run | OFF during build, ON after Phase 2 verification |
| Sample size | 5 → 25 → full |

---

## Column-by-Column Spec

| # | Column | Type | Provider | Credits | Run Condition |
|---|--------|------|----------|---------|---------------|
| 1 | `company_domain` | text | Apollo source | 0 | — |
| 2 | `company_name` | text | Apollo source | 0 | — |
| 3 | `industry` | enrichment | Clay native | 1 | — |
| 4 | `employee_count` | enrichment | Clay native | 1 | — |
| 5 | `hq_country` | enrichment | Clay native | 1 | — |
| 6 | **`pass_1_qualified`** | formula | — | 0 | — |
| 7 | `revenue_range` | enrichment | People Data Labs | 2 | `pass_1_qualified = TRUE` |
| 8 | `funding_stage` | enrichment | Predictleads | 2 | `pass_1_qualified = TRUE` |
| 9 | `funding_last_round_date` | enrichment | Predictleads | included | `pass_1_qualified = TRUE` |
| 10 | `tech_stack_signals` | enrichment | Wappalyzer (lite) | 1 | `pass_1_qualified = TRUE` |
| 11 | `trigger_event` | enrichment | Predictleads | 2 | `pass_1_qualified = TRUE` |
| 12 | `trigger_recency_days` | formula | — | 0 | — |
| 13 | **`icp_gate_qualified`** | formula | — | 0 | — |
| 14 | `account_tier` | formula | — | 0 | — |
| 15 | `pain_research` | Claygent | use-ai | 5 | `icp_gate_qualified = TRUE` |
| 16 | `suppression_check` | lookup | customer table | 0 | — |
| 17 | `route_to` | formula | — | 0 | — |
| 18 | `assigned_sdr` | formula (round-robin) | — | 0 | `route_to = "SDR_QUEUE_T1"` |
| 19 | `slack_message` | formula | — | 0 | `account_tier = "T1"` |

**Estimated cost per qualified row**: ~14 credits (most rows disqualify at pass_1; survivors burn the full stack).
**Estimated cost on 1,000 source list**: ~3,500 credits (assuming 25% pass_1 rate).

---

## Formulas

### `pass_1_qualified`

```clayscript
IF(
  AND(
    industry IN ["Software", "SaaS", "Fintech", "MarTech"],
    employee_count >= 250,
    employee_count <= 2500,
    hq_country IN ["United States", "United Kingdom", "Canada"]
  ),
  TRUE,
  FALSE
)
```

### `trigger_recency_days`

```clayscript
IF(trigger_event != NULL,
  DAYS_BETWEEN(NOW(), trigger_event_date),
  NULL
)
```

### `icp_gate_qualified`

```clayscript
IF(
  AND(
    pass_1_qualified == TRUE,
    revenue_range IN ["$10M-$50M", "$50M-$100M", "$100M-$250M"],
    trigger_event IS NOT NULL,
    trigger_recency_days <= 90
  ),
  TRUE,
  FALSE
)
```

### `account_tier`

```clayscript
IF(icp_gate_qualified == FALSE, "DISQUALIFIED",
IF(
  AND(employee_count >= 1000, trigger_event IN ["funding", "exec_change"]),
  "T1",
IF(
  OR(employee_count >= 500, trigger_event != NULL),
  "T2",
  "T3"
)))
```

### `route_to`

```clayscript
IF(suppression_check == TRUE, "SUPPRESSED",
IF(account_tier == "T1", "SDR_QUEUE_T1",
IF(account_tier == "T2", "MARKETING_NURTURE",
IF(account_tier == "T3", "PROGRAMMATIC",
"DISQUALIFIED"))))
```

### `assigned_sdr` (round-robin pool of 3)

```clayscript
sdr_pool = ["sdr_alice_id", "sdr_bob_id", "sdr_carla_id"]
sdr_pool[MOD(ROW_INDEX, 3)]
```

### Claygent: `pain_research` Prompt

```
ROLE: B2B SaaS sales analyst doing pre-call account research.

CONTEXT:
- Company: {company_name}
- Industry: {industry}, {employee_count} employees, {hq_country}
- Funding: {funding_stage}, last round {funding_last_round_date}
- Trigger: {trigger_event}
- Tech: {tech_stack_signals}

SOURCES TO CHECK (max 3):
1. Their website /about, /careers, /pricing
2. Their LinkedIn company page
3. Recent press release or blog about {trigger_event}

TASK:
Identify ONE specific operational pain or strategic initiative that:
- Is publicly stated or strongly implied
- Connects to the trigger event
- Maps to a category our product helps with: [GTM, ops, finance, eng]

Return EXACTLY this JSON:
{
  "pain": "string (15-25 words)",
  "evidence_url": "string",
  "category": "GTM|ops|finance|eng",
  "confidence": "high|medium|low"
}

FALLBACK:
If no clear pain is publicly evident, return confidence: "low" and pain: "Trigger event present but pain undeclared — needs human review."
```

### Slack Alert Template

```
🎯 *T1 Account — {company_name}* ({industry}, {employee_count} emp)
Trigger: {trigger_event} ({trigger_recency_days}d ago)
Pain hypothesis: {pain_research.pain}
Evidence: {pain_research.evidence_url} (confidence: {pain_research.confidence})
Assigned: <@{assigned_sdr}>
HubSpot: {hubspot_account_url}

SLA: SDR to find 3 contacts + queue email-1 in next 48h.
```

---

## Build Sequence (Manual Walkthrough)

1. Create table → name `"ABM Tier 1 + Triggers — {date}"`.
2. Source → Apollo URL → paste search URL → confirm import (start with 100 rows for first build).
3. Add columns 3–5 (industry, employee_count, hq_country) → Clay native enrichment, run on all.
4. Add column 6 `pass_1_qualified` → Formula → paste template.
5. Add columns 7–11 (revenue, funding, tech, trigger) → set Run Condition `pass_1_qualified = TRUE` on each.
6. Add column 12 `trigger_recency_days` → Formula.
7. Add column 13 `icp_gate_qualified` → Formula.
8. Add column 14 `account_tier` → Formula.
9. Add column 15 `pain_research` → Claygent → paste prompt, max_sources=3, model=Claude Sonnet, Run Condition `icp_gate_qualified = TRUE`.
10. Add column 16 `suppression_check` → Lookup against your customer/opt-out table.
11. Add columns 17–19 (route_to, assigned_sdr, slack_message) → Formula columns.
12. Add Actions:
    - **HubSpot upsert** → push-hubspot, filter `route_to != "DISQUALIFIED" AND route_to != "SUPPRESSED"`
    - **Slack notify** → channel `#abm-tier1`, filter `account_tier = "T1"`
13. **`auto_run = FALSE`** during all of build.
14. Run on 5 rows → verify enrichment + gate + tier + route_to.
15. Run on 25 rows → validate trigger match rate (~25–35% expected for this ICP).
16. Run on 100 rows → check Slack alert formatting.
17. Run full source list.
18. Optional: flip `auto_run = TRUE` if this becomes a recurring weekly account refresh.

---

## Verification Checklist

- [ ] 5-row sample: industry/size/geo enrich (>80% success)
- [ ] `pass_1_qualified` matches manual judgment on 5/5
- [ ] 25-row sample: trigger event match rate ≥ 25%
- [ ] Tier distribution: T1 ~5–10%, T2 ~20–30%, T3 ~remainder, DISQUALIFIED appropriately large
- [ ] Suppression check correctly catches a known customer (test by adding one to source)
- [ ] Slack alert formats correctly (test with a known T1)
- [ ] HubSpot upsert dedups correctly (no duplicates on second run)
- [ ] Total credits per qualified account ≤ 15

---

## Cost Optimization Variants

| Variant | Change | Impact |
|---------|--------|--------|
| Drop tech stack column | Remove `tech_stack_signals` if not used in gate | Save 1 credit per pass_1 row |
| Skip Claygent on T3 | Add `account_tier IN ["T1", "T2"]` to pain_research run condition | Save 5 credits on T3 rows |
| Use Predictleads only on T1 candidates | Move trigger_event after a preliminary `tier_candidate` formula | Save 2 credits on rows that won't make T1/T2 anyway |
| Refresh-only mode | Skip rows where `last_enriched < 30d` | Save full re-enrichment cost on stable accounts |

---

## What Could Go Wrong

| Risk | Mitigation |
|------|-----------|
| Apollo source returns out-of-ICP rows | Pass_1 gate catches; verify on first 25 |
| Trigger event provider returns stale data | Set recency window tight (≤90d); spot-check trigger_event_date |
| Claygent returns low-confidence pain on too many rows | Reduce max_sources to 2 OR require trigger_event_recency ≤ 30d for pain_research run |
| SDR overload on T1 spikes | Cap Slack alerts to 10/day; route excess to T2 nurture |
| HubSpot duplicates | Set dedup key to `company_domain` only |

---

## Related Templates

- For contact-finding off this account list → see template `03-cold-outbound-multi-provider-waterfall.md`.
- For scoring once contacts are found → `/clay-icp-score`.
- For inbound from these accounts later → template `02-inbound-demo-enricher-router.md`.
