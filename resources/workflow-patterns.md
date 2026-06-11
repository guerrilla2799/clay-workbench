# 5 Reusable Workflow Patterns

The 5 most common Clay workbook patterns. Each pattern is a composition of sub-skills + standard column shapes. Inspired by ColdIQ's pattern library, adapted to Brandon's GTM rigor.

When a user describes a workflow, recognize the pattern first, then drop into the relevant sub-skill.

---

## Pattern 1 — Trigger-Driven ABM (Net-New Outbound)

**Use when**: building a fresh outbound motion targeting accounts with a recent trigger event.

**Sub-skills**:
1. `/clay-abm-list` → account list with firmographic + trigger gating
2. `/clay-enrich-waterfall` → contacts at qualified accounts
3. `/clay-icp-score` → contact-level fit + intent score
4. `/clay-outbound` → personalized copy + sequencer push

**Flow**:
```
Source (Apollo URL / CSV / Sales Nav)
  ↓ ABM list workbook
  → pass_1 gate (industry, size, geo)
  → enrichment + trigger detection
  → ICP gate
  → account_tier classification
  → route_to T1/T2/T3 / drop
  ↓
T1 accounts → branched table
  → find-and-enrich-contacts-at-company (target titles)
  → email waterfall + verify
  → phone waterfall (optional)
  ↓
Contact-keyed table
  → contact-level ICP score
  → Claygent personalization
  → Sending Gate
  → SalesLoft / Outreach / 11x push
```

**Total credits per qualified contact**: ~25-30.
**Total time to build**: 60 min first time, 15 min on rebuild with subroutines.

**Best for**: Tier 1 enterprise outbound, conference attendee follow-up, signal-triggered campaigns.

---

## Pattern 2 — Inbound Demo Router (Real-Time)

**Use when**: every B2B SaaS — every inbound form should run this.

**Sub-skills**:
1. `/clay-inbound-routing` → webhook source + enrich + route
2. `/clay-icp-score` → composite Hot/Warm/Cold score
3. `/clay-outbound` (optional) → auto-prepare SDR sequence

**Flow**:
```
Demo form / contact-us / free signup webhook
  ↓ auto_run = TRUE
Inbound router workbook
  → parse payload, extract email/company
  → personal-email check (route to nurture)
  → pass_1 gate (industry, size, geo)
  → company + person enrichment
  → trigger event check
  → ICP score (10-point rubric)
  → suppression check
  → route_to:
       - Hot → SDR queue + Slack + SalesLoft cadence
       - Warm → Marketing nurture
       - Cold / Personal email → Self-serve
       - Suppressed → drop
```

**Total credits per form fill**: ~6-10 average.
**Total time to build**: 45 min including Phase 1+2 testing.

**Best for**: every B2B SaaS demo form. Sub-5-minute response multiplies connect rate 4-8x.

---

## Pattern 3 — Account Refresh / Stay-Current (CRM Hygiene)

**Use when**: existing CRM has stale firmographics, missing trigger events, decayed contact data.

**Sub-skills**:
1. `/clay-abm-list` (refresh variant) → re-enrich existing accounts
2. `/clay-icp-score` → recompute scores
3. `/clay-troubleshoot` → diagnose accounts that shouldn't be there

**Flow**:
```
HubSpot / Salesforce account view
  ↓ daily or weekly sync
Refresh workbook (auto_run = TRUE, freshness gate)
  → only re-enrich accounts where last_enriched > 30d
  → re-pull firmographics (Clay native, cheap)
  → check for new trigger events
  → recompute ICP score
  → flag account_tier changes
  → write-back to CRM
  → if tier changed Hot ← Cold or Cold ← Hot, Slack notify
```

**Total credits per account-refresh**: ~3-5 (cheap because we skip unchanged data).
**Total time to build**: 30 min.

**Best for**: keeping CRM scoring accurate without daily SDR re-research.

---

## Pattern 4 — Job Change Triggered Reach-Out

**Use when**: alumni from past meetings / closed-lost deals change jobs to a new ICP company.

**Sub-skills**:
1. `/clay-abm-list` (job-change variant)
2. `/clay-icp-score` (job-change weighted)
3. `/clay-outbound` (warm-re-engagement messaging)

**Flow**:
```
Job change signal source (Champify / The Swarm / Predictleads)
  → match against prior contacts CSV (closed-lost, prior meetings, customer alumni)
  → only keep matches AND new company is in ICP
  ↓
Workbook
  → enrich new company firmographics
  → verify person at new company (LinkedIn check)
  → ICP gate on new company
  → check old company relationship type
  → route_to based on (relationship × new_company_tier):
       - Closed-lost AE → "their AE re-engages"
       - Prior meeting attendee → "marketing re-engages"
       - Alumni → "founder-led warm intro request"
  → Slack notify the relevant rep
  → push to sequencer with warm re-engagement copy
```

**Total credits per job change**: ~10.
**Total time to build**: 45 min.

**Best for**: high-converting motion. Warm pipeline at <50% the cost of cold.

---

## Pattern 5 — Persona-Specific Multi-Step Cadence

**Use when**: targeting a specific persona (e.g., "VPs of Revenue Operations at 500-2500 employee B2B SaaS") with a 4-step cadence.

**Sub-skills**:
1. `/clay-enrich-waterfall` → email + phone + LinkedIn for the persona
2. `/clay-outbound` → 4-step cadence with per-step eligibility

**Flow**:
```
Persona definition + target account list (from /clay-abm-list)
  ↓
Contact-keyed workbook
  → find-and-enrich-contacts-at-company (title filter strict)
  → email waterfall + verify
  → phone (optional)
  → LinkedIn URL
  ↓
Per-step eligibility:
  step_1_eligible (email + first_line + sending_gate)
  step_2_eligible (step_1 sent + 3-10d window + no reply)
  step_3_eligible (step_2 sent + 5d + no reply)
  linkedin_step_eligible (LinkedIn URL + sending_gate)
  ↓
Sequencer push with per-step filters (step_1_eligible, step_2_eligible, etc.)
```

**Total credits per contact**: ~12-18.
**Total time to build**: 35 min.

**Best for**: long-cycle enterprise sales where 1 touch is never enough.

---

## Pattern Selection Decision Tree

```
What is the user trying to do?

Goal: Build a fresh target list for outbound
  └── Pattern 1 — Trigger-Driven ABM

Goal: Route inbound demo / contact-us submissions
  └── Pattern 2 — Inbound Demo Router

Goal: Keep existing CRM scoring fresh
  └── Pattern 3 — Account Refresh

Goal: Re-engage relationships when person changes jobs
  └── Pattern 4 — Job Change Reach-Out

Goal: Multi-step cadence for a specific persona
  └── Pattern 5 — Persona Cadence
```

If the user's goal doesn't match any of these, compose from sub-skills directly — but most workflows ARE one of these patterns.

---

## Pattern Sizing

| Pattern | Best Volume | Underperforms At |
|---------|-------------|------------------|
| 1 — Trigger ABM | 100-2000 accounts | <50 accounts (sample too small for triggers) |
| 2 — Inbound Router | Any (1+ inbound/day) | <1 inbound/week (auto_run wasted) |
| 3 — Account Refresh | 500-50,000 accounts | <100 accounts (manual refresh easier) |
| 4 — Job Change | 100-1000 prior contacts | <50 prior contacts (low base rate) |
| 5 — Persona Cadence | 200-5000 contacts | <50 contacts (cadence overhead) |

---

## Combined Patterns

Some setups combine patterns:

- **Pattern 1 + Pattern 5**: ABM list build → persona cadence per tier
- **Pattern 2 + Pattern 4**: Inbound router with job-change suppression / boost
- **Pattern 3 + Pattern 4**: Account refresh + job-change detection in same daily run
- **Pattern 1 + Pattern 4**: Trigger ABM enhanced with job-change-as-trigger

When the user describes their goal, ask "which pieces" rather than fitting to one pattern. Hybrid is common at scale.

---

## Related

- For pattern-specific column shapes, see the corresponding sub-skill SKILL.md and templates/.
- For execution costs by pattern, see `credit-cost-table.md`.
- For diagnosing under-performing patterns, see `clay-troubleshoot`.
