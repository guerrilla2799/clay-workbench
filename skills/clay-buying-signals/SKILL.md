---
name: clay-buying-signals
description: Composite buying-signal detector that fuses MULTIPLE signal sources (intent data, web visits, content engagement, hiring triggers, funding events, tech adoption, leadership moves) into a single time-decaying "now is the moment" score per account. Extends /clay-signal-monitor with multi-signal correlation — a single signal is mostly noise; 2+ correlated signals in the same window is real intent. Triggers — "buying signals", "intent score", "composite signal", "multi-signal correlation", "show me hot accounts", "intent fusion", "G2 + 6sense", "Bombora", "intent surge", "in-market accounts", "warm accounts", "/clay-buying-signals".
---

# clay-buying-signals — Composite Multi-Signal Intent Detection

The intent-fusion skill. Use when the user wants a **single composite "now is the moment" score per account** that fuses 2+ signal sources, not single-signal alerting.

Inherits `clay-workbench/SKILL.md` master workflow. Specializes step 3 (composition — multi-source fusion + time decay) and step 5 (execution — historical backfill correlation validation).

**Difference from `/clay-signal-monitor`**: that emits alerts per signal type. This fuses signals across sources and emits one ranked score per account.

**Difference from `/clay-icp-score`**: that scores fit (firmographic + persona). This scores *timing* (intent intensity). Real ABM uses both — fit × intent.

**Core principle**: Single-signal intent is mostly noise (high false-positive rate). Two correlated signals in the same time window — a Bombora intent surge + a relevant LinkedIn hiring post in the same week — is far higher signal-to-noise than either alone.

---

## Inputs Expected

- **Signal sources to fuse** (choose any 2+):
  - **Intent data** (3rd party): 6sense, Bombora, G2 buyer intent, Demandbase, ZoomInfo intent
  - **Web behavior** (1st party): Clearbit Reveal, RB2B, Snitcher, HubSpot session data
  - **Content engagement**: Mutiny, HubSpot/Marketo email opens + clicks, ad engagement
  - **Hiring triggers**: Predictleads, LinkedIn jobs (Claygent), Champify
  - **Funding events**: Predictleads, Crunchbase, Harmonic
  - **Tech adoption**: BuiltWith delta, Wappalyzer
  - **Leadership moves**: Champify, UserGems
  - **Direct intent**: form fills, demo requests, pricing page visits
- **Account universe**: Tier 1 + Tier 2 ABM list / total addressable / customer expansion
- **Decay window**: how long a signal contributes (default 30d, with linear decay)
- **Correlation threshold**: minimum correlated signals to qualify as "HOT" (default 2)
- **Routing**: Slack channel(s) per severity, CRM update rules, sequencer triggers
- **Suppression**: current customers, opt-outs, recently-engaged (≤14d)

---

## Step 3 — Composition (Specialized)

### Canonical Column Order (Account-Keyed)

| # | Column | Type | Source / Provider | Cost | Depends On |
|---|--------|------|-------------------|------|------------|
| 1 | `account_id` | text | source | 0 | — |
| 2 | `company_domain` | text | source | 0 | — |
| 3 | `account_tier` | formula | from `/clay-abm-list` output | 0 | 2 |
| 4 | `firmographics` | enrichment | find-company | 1–3 | 2 |
| 5 | `pass_1_relevant` | formula | clayscript (cheap pre-gate) | 0 | 3, 4 |
| 6 | `intent_score_6sense` | enrichment | 6sense | 1–2 | 2 |
| 7 | `intent_score_bombora` | enrichment | Bombora | 1–2 | 2 |
| 8 | `intent_score_g2` | enrichment | G2 buyer intent | 1–2 | 2 |
| 9 | `web_visit_recent_30d` | enrichment | Clearbit Reveal / RB2B / Snitcher | 1–2 | 2 |
| 10 | `content_engagement_recent` | enrichment | HubSpot / Marketo / Mutiny | 1 | 2 |
| 11 | `hiring_signal_relevant` | enrichment OR claygent | Predictleads / LinkedIn | 2–10 | 2 |
| 12 | `funding_signal_recent` | enrichment | Predictleads / Crunchbase | 2–3 | 2 |
| 13 | `tech_adoption_signal` | enrichment | BuiltWith delta | 1–5 | 2 |
| 14 | `leadership_signal_recent` | enrichment | Champify / UserGems | 2–5 | 2 |
| 15 | `direct_intent_recent` | formula | CRM lookup (form fill, demo, pricing visit) | 0 | 2 |
| 16 | `suppression_check` | formula | clayscript lookup | 0 | 2 |
| 17 | `signal_count_active_30d` | formula | clayscript (count of 6–15 with active signal) | 0 | 6–15 |
| 18 | `signals_correlated` | formula | clayscript (≥2 distinct categories firing in same 14d window) | 0 | 6–15 |
| 19 | **`composite_intent_score`** | formula | clayscript (weighted + time-decayed) | 0 | 6–15, 17, 18 |
| 20 | `intent_classification` | formula | clayscript (HOT / WARM / COOL / COLD) | 0 | 19, 18, 16 |
| 21 | `top_signals_summary` | claygent OR formula | clayscript (which signals contributed most) | 0–5 | 6–15 |
| 22 | `recommended_play` | formula | clayscript (intent_class × tier × fit) | 0 | 3, 20 |
| 23 | `route_to` | formula | clayscript | 0 | 16, 20, 22 |

### `composite_intent_score` Formula (Weighted + Time-Decayed)

```clayscript
SUM(
  // Each signal contributes max points × decay
  // decay = MAX(0, 1 - (days_since_signal / decay_window))

  MULTIPLY(IF(intent_score_6sense >= {INTENT_THRESHOLD}, 3, 0), decay_6sense),
  MULTIPLY(IF(intent_score_bombora >= {INTENT_THRESHOLD}, 3, 0), decay_bombora),
  MULTIPLY(IF(intent_score_g2 >= {INTENT_THRESHOLD}, 3, 0), decay_g2),
  MULTIPLY(IF(web_visit_recent_30d > 0, 4, 0), decay_web),
  MULTIPLY(IF(content_engagement_recent > 0, 2, 0), decay_content),
  MULTIPLY(IF(hiring_signal_relevant == TRUE, 3, 0), decay_hiring),
  MULTIPLY(IF(funding_signal_recent == TRUE, 2, 0), decay_funding),
  MULTIPLY(IF(tech_adoption_signal == TRUE, 3, 0), decay_tech),
  MULTIPLY(IF(leadership_signal_recent == TRUE, 3, 0), decay_leadership),
  MULTIPLY(IF(direct_intent_recent > 0, 6, 0), decay_direct),

  // Correlation bonus — 2+ categories firing in same 14d window
  IF(signals_correlated == TRUE, 5, 0)
)
```

Max possible ≈ 34. Tune `{INTENT_THRESHOLD}` per provider (Bombora 60+, 6sense 70+, G2 ≥medium).

### `intent_classification`

```clayscript
CASE(
  suppression_check == TRUE, "SUPPRESSED",
  AND(composite_intent_score >= 15, signals_correlated == TRUE), "HOT",
  composite_intent_score >= 10, "WARM",
  composite_intent_score >= 5, "COOL",
  TRUE, "COLD"
)
```

### `recommended_play` Mapping

| Tier × Intent | T1 | T2 | T3 |
|---------------|----|----|----|
| HOT  | EXEC_OUTREACH_NOW + 1:1 ABM ad burst | SDR_NOW + targeted ad layer | INBOUND_NURTURE + retarget |
| WARM | AE_OUTREACH_WK + programmatic touch | SDR_2WK + nurture | NURTURE |
| COOL | NURTURE + monitor | NURTURE | DROP_TO_PROGRAMMATIC |
| COLD | MONITOR | MONITOR | DROP |

Codify as clayscript CASE.

### `top_signals_summary` (Claygent Optional)

```
ROLE: Senior B2B GTM strategist explaining WHY this account is showing intent.
CONTEXT:
  - Account: {company_name}
  - Active signals (30d): {list_of_signals_with_dates}
  - Composite score: {composite_intent_score}/34
TASK: In 1 sentence, explain the dominant 1–2 signals driving this score, in plain language an AE can act on.
FORMAT: Single sentence, <30 words, no preamble.
FALLBACK: If signal_count_active_30d < 2, return "WEAK_SINGLE_SIGNAL — monitor only" and stop.
```

Skip Claygent if cost-constrained — formula-based version works fine.

---

## Step 5 — Execution (Specialized)

### Schedule Setup

```
Cadence: daily refresh of intent scores; weekly full recompute of composite

Backfill protocol (CRITICAL — single-signal noise is the #1 failure):
  1. Run all signal-source columns on 100 known historical accounts (50 closed-won, 50 closed-lost)
  2. Compute composite_intent_score retrospectively for each
  3. Check distribution:
     - Did closed-won accounts score HOT/WARM in the 30–60d before close? (Should be ≥70%)
     - Did closed-lost accounts score COLD/COOL? (Should be ≥60%)
  4. If discrimination is weak → tune signal weights, INTENT_THRESHOLD, correlation requirement
  5. Re-run backfill until discrimination is reasonable

Without backfill validation, this skill produces a vanity score, not a useful one.
```

### Preferred Path: Tier 1 (official Agent Plugin) — see resources/execution-surface.md

```
1. clay credits — balance pre-flight (this skill is expensive; see Credit Pre-Flight below)
2. clay routines list → check for a "Buying Signal Composite" routine; clay routines runs for status
3. mcp__claude_ai_Clay__find-and-enrich-company for sample (Tier 2 — connector)
4. Build columns 1–23 per spec — table columns are still UI-built (Tier 3); walk the user through
5. Run 100-account historical backfill (closed-won + closed-lost mix)
6. clay tables rows / clay tables query (or the table MCP tool) → read back scores, compute discrimination metrics
7. Tune weights
8. Once discrimination ≥ thresholds → flip auto_run = TRUE on daily refresh
9. Pipe HOT-tier alerts to Slack via /clay-signal-monitor's alert pattern
```

### Manual Fallback (Tier 3)

1. New table → `"Buying Signals Composite — {account_universe}"`
2. Source → ABM Tier 1+2 account list (from `/clay-abm-list`)
3. Connect each signal source integration (6sense, Bombora, G2, web reveal, Predictleads, Champify, etc.)
4. Build columns 1–5 (firmographics + gate) first
5. Add signal-source columns 6–15 individually — confirm each returns expected data on 5 accounts
6. Add formula columns 17–22
7. Backfill 100 historical accounts (mix won/lost) — DO NOT skip
8. Tune weights based on discrimination test
9. Add routing/Slack actions
10. Schedule daily refresh
11. Flip `auto_run = TRUE` only after backfill validation passes

---

## Credit Pre-Flight (Mandatory)

```
Per account (FULL fusion of 8+ signal sources):
  - Firmographics:           ~3 credits
  - Intent (3 providers):    ~6 credits
  - Web reveal:              ~2 credits
  - Content engagement:      ~1 credit (CRM lookup, ~free)
  - Hiring/funding/tech/leadership: ~10–20 credits
  - Claygent summary (optional): ~5 credits
  Total: ~25–40 credits per account per refresh

Daily refresh on 5,000 T1+T2 accounts: 125k–200k credits/day = 3.75M–6M/month (~$37k–60k)

Cost is real. Default suggestion: scope to T1 only for first 90 days, prove discrimination, then expand to T2. Or refresh weekly (not daily) on T2.

Cheaper alternatives if budget-constrained:
- Use 2 signal sources, not 8 (cut cost ~70%)
- Refresh weekly instead of daily
- Only run on accounts with composite > COOL in last refresh
```

---

## Backfill Discrimination Test (CRITICAL)

This is the most important section of this skill. Run it before flipping auto_run.

```
1. Pull 50 closed-won + 50 closed-lost accounts from CRM (matched window: last 12 months)
2. For each, reconstruct what their composite_intent_score WOULD have been in the 30–60d before close (or lost-date)
3. Compute:
   - HOT-rate among closed-won (target: ≥70%)
   - HOT-rate among closed-lost (target: ≤20%)
   - Lift: HOT-rate(won) / HOT-rate(lost) — target ≥3x

If lift <2x: the score is not discriminating. Either:
- Signal weights are wrong (tune)
- Correlation threshold too loose (require 3 signals instead of 2)
- Signal sources are wrong-fit for the ICP (swap providers)
- ICP is too broad (segment scores by ICP type)

If lift ≥3x: cleared to flip auto_run = TRUE.
```

---

## Verify-and-Handoff Checklist

- [ ] All chosen signal-source integrations connected and returning data
- [ ] 5-account sample: every column returns plausible values
- [ ] 100-account historical backfill complete
- [ ] Discrimination lift ≥ 3x (HOT-rate among closed-won vs closed-lost)
- [ ] HOT-tier alert volume reasonable for AE bandwidth (≤5/day per AE)
- [ ] Slack channel per severity / per owner connected
- [ ] CRM intent-score field write-back configured
- [ ] Sequencer trigger gated on `intent_classification == "HOT" AND suppression_check == FALSE`
- [ ] Suppression list (customers + recently-engaged) current
- [ ] auto_run = TRUE only after backfill discrimination test passes
- [ ] Monthly drift check scheduled — re-run backfill quarterly to catch model decay

---

## Use-Case Variants

| Use Case | Adjustments |
|----------|-------------|
| Tier 1 ABM only | Tighter correlation (require 3 signals) + opus on top_signals_summary |
| Inbound MQL acceleration | Heavier weight on direct_intent + web_visit; faster decay (14d window) |
| Customer expansion | Replace direct_intent with product usage data; signal-source mix includes CSM-flagged risk |
| Field event targeting | Add `is_in_target_geo` × `is_active_in_intent` for event-attendee shortlist |
| Founder-led sales pre-PMF | Skip 3rd-party intent (too noisy at low volume); fuse Champify + LinkedIn + web reveal only |
| Long-cycle enterprise | Extend decay window to 60–90d; weight leadership_signal higher |

---

## Anti-Patterns

❌ Treating single-signal intent as HOT — Bombora alone is mostly noise; require correlation.
❌ Flipping auto_run = TRUE without backfill discrimination test — produces vanity scores, not useful ones.
❌ Equal weight across signal types — direct_intent and leadership_signal should outweigh tech_adoption.
❌ No time decay — 90-day-old intent is fundamentally not the same as 7-day-old intent.
❌ Running on cold open-territory list — without firmographic + ICP context, intent score is noise.
❌ Single Slack channel for HOT alerts across the entire AE team — channel fatigue kills response rate.
❌ Letting composite_intent_score replace `/clay-icp-score` — fit and timing are different things; use both.
❌ Skipping suppression — alerting on current customers as "HOT" is embarrassing.

---

## Related

- For single-signal alerting (no fusion) → `/clay-signal-monitor`.
- For fit scoring (the orthogonal axis to this skill's intent scoring) → `/clay-icp-score`.
- For the Tier 1+2 account universe this skill scores → `/clay-abm-list`.
- For deep account context to attach to a HOT alert → `/clay-account-research`.
- For the outbound play triggered by HOT classification → `/clay-outbound`.
- For ongoing cost audit of this skill's recurring runs (it's expensive) → `/clay-cost-audit`.
- For Claygent prompt tuning on top_signals_summary → `/clay-claygent-iterator`.
