---
name: clay-enrich-waterfall
description: Build contact-keyed enrichment waterfalls in Clay — email discovery, verification, phone, LinkedIn URL — across multiple providers with graceful exit and pre-flight cost estimation. Composes the optimal provider chain for the user's budget and target match rate. Triggers — "enrich contacts", "find emails", "email waterfall", "contact enrichment", "phone enrichment", "Clay waterfall", "Datagma Findymail Apollo Hunter", "waterfall match rate", "/clay-enrich-waterfall".
---

# clay-enrich-waterfall — Multi-Provider Enrichment

Loads when the user wants to build or optimize a **contact-keyed** enrichment chain. Finds email + verifies + (optionally) phone + LinkedIn URL across multiple providers with graceful exit on first success.

Inherits master workflow. Specializes step 3 (provider chain composition) and step 5 (execution + match-rate validation).

---

## Inputs Expected

From intake:
- **Input row shape**: first_name + last_name + company_domain (minimum) OR LinkedIn URL
- **Data points needed**: email / email + phone / email + phone + LinkedIn URL
- **Target match rate**: 60% (cheap) / 80% (standard) / 90% (premium)
- **Budget per row**: cents per row tolerable (e.g., 5¢ / 10¢ / 20¢)
- **Own API keys available**: which providers does the user already have seats for?
- **Verification required**: yes (recommended) / no (rare)

---

## Step 3 — Composition (Specialized)

### Email Waterfall Patterns

| Pattern | Providers | Per-Row Cost (Graceful Exit) | Match Rate |
|---------|-----------|------------------------------|------------|
| **Budget** | Apollo (Clay-managed) → Icypeas | ~2 credits | 60% |
| **Standard** | Apollo → Findymail → Datagma | ~4 credits | 80% |
| **Premium** | Apollo → Findymail → Datagma → Dropcontact | ~6 credits | 90% |
| **EU-optimized** | Apollo → Datagma → Dropcontact | ~5 credits | 85% |
| **Own-key heavy** | Apollo (own key) → Findymail → Datagma | ~3 credits | 80% |

**Always graceful exit**: configure each waterfall step to skip if previous step returned `email_status ∈ {valid, accept_all_high}`.

### Email Verification

Append **after** waterfall:
- `email_verification_status` column → ZeroBounce (1 credit)
- Run condition: `email != NULL AND email_status != "verified"` (skip Apollo "verified" — already validated)

### Phone Waterfall Patterns

| Pattern | Providers | Per-Row Cost (Graceful Exit) | Match Rate |
|---------|-----------|------------------------------|------------|
| **Budget** | Apollo (Clay-managed) | ~1 credit | 25% |
| **Standard** | Apollo → Datagma | ~2 credits | 35% |
| **Premium** | Apollo → Datagma → ContactOut | ~5 credits | 50% |
| **Enterprise (own key)** | Cognism (own key) → Apollo | ~1 credit | 60% |

Phone waterfalls top out at ~60% match rate. Set expectations.

### LinkedIn URL Discovery

Usually returned by contact-finding step. If not:
- Apollo (1 credit) — 65% match
- LinkedIn Sales Nav (Clay-managed, 2 credits) — 95% match

### Full Stack Column Spec

| # | Column | Type | Provider | Cost | Run Condition |
|---|--------|------|----------|------|---------------|
| 1 | `first_name` | text | source | 0 | — |
| 2 | `last_name` | text | source | 0 | — |
| 3 | `company_domain` | text | source | 0 | — |
| 4 | `email_apollo` | enrichment | Apollo | 1 | gate_qualified = TRUE |
| 5 | `email_findymail` | enrichment | Findymail | 2 | email_apollo IS NULL |
| 6 | `email_datagma` | enrichment | Datagma | 2 | email_findymail IS NULL |
| 7 | `email` | formula | coalesce(email_apollo, email_findymail, email_datagma) | 0 | — |
| 8 | `email_source` | formula | which provider returned it | 0 | — |
| 9 | `email_verified` | enrichment | ZeroBounce | 1 | email IS NOT NULL AND email_source != "apollo_verified" |
| 10 | `phone_apollo` | enrichment | Apollo | 1 | email_verified = "valid" |
| 11 | `phone_datagma` | enrichment | Datagma | 2 | phone_apollo IS NULL |
| 12 | `phone` | formula | coalesce(phone_apollo, phone_datagma) | 0 | — |
| 13 | `linkedin_url` | enrichment | Apollo | 1 | gate_qualified = TRUE |
| 14 | `enrichment_complete` | formula | email AND (phone OR phone_optional) AND linkedin_url | 0 | — |

---

## Step 5 — Execution (Specialized)

### Preferred Path: Tier 1 (official Agent Plugin) — see resources/execution-surface.md

```
1. clay credits — balance pre-flight
2. Estimate: row_count × waterfall_per_row × (1 + phone_per_row × phone_flag)
3. Pre-flight prompt
4. Find existing routine:
   clay routines list
   → "Email Waterfall" or "Contact Enrichment" likely exists
5. If routine exists:
   clay routines get → map inputs
   → clay routines runs to launch + poll status
6. If no routine — for ad-hoc:
   mcp__claude_ai_Clay__find-and-enrich-list-of-contacts (Tier 2 — connector)
   → returns contacts with email/phone/LinkedIn already waterfallled
   → verify results via clay tables rows/query or the `table` MCP tool
```

### Manual Fallback (Tier 3) — Build the Waterfall in Clay UI

Enrichment-column setup and run conditions are still UI-only (see resources/execution-surface.md):

1. In an existing contact-keyed table, + Add Column → **Enrichment** → search "email waterfall" → select Clay's prebuilt **or** chain providers manually.
2. **Chain providers manually** for cost control:
   - Column 4 `email_apollo`: Apollo people enrichment → input domain + name
   - Column 5 `email_findymail`: Findymail → run condition `{email_apollo IS NULL}`
   - Column 6 `email_datagma`: Datagma → run condition `{email_findymail IS NULL}`
3. Column 7 `email`: Formula `coalesce(email_apollo, email_findymail, email_datagma)`
4. Column 8 `email_source`: Formula identifying which column returned the value
5. Column 9 `email_verified`: ZeroBounce → run condition `{email IS NOT NULL AND email_source != "apollo_verified"}`
6. Repeat for phone (columns 10–12).
7. Column 14 `enrichment_complete`: Formula combining required fields.
8. Set `auto_run = false`.

---

## Match-Rate Validation Protocol

Sample-driven graduated rollout:

```
Sample 1: 5 rows
  Target: any matches at all (sanity check)

Sample 2: 25 rows
  Target: stack match rate within 10% of planned (e.g., 80% planned → 70–90% actual)
  IF below 60%:
    DIAGNOSE — check input data quality (typos in domains? wrong name format?)
    REVIEW — provider chain may need different mix for this ICP

Sample 3: 100 rows
  Target: final calibration; phone match rate; verification pass-through
  IF email valid rate < 70% of total found:
    Many catch-all domains. Consider Bouncer or Kickbox for catch-all scoring.

Full run only after Sample 3 passes.
```

---

## Match-Rate Benchmarks (from `resources/enrichment-benchmarks.md`)

| Metric | Single Provider | Standard Waterfall | Premium Waterfall |
|--------|-----------------|--------------------|--------------------|
| Email found | 40% | 80% | 90% |
| Email valid (after verify) | 30% | 65% | 75% |
| Phone found | 25% | 35% | 50% |
| LinkedIn URL found | 65% | 95% (with Sales Nav) | 95% |

If actuals lag benchmarks by >15%, route to `/clay-troubleshoot`.

---

## Anti-Patterns

❌ Running all providers in parallel instead of waterfall — burns 4–6x credits.
❌ Verifying Apollo "verified" emails — waste of credit (already validated).
❌ Running phone waterfall on rows where email failed — wasted credits.
❌ Pushing unverified emails to sequencer — domain reputation damage.
❌ No graceful exit — chains through every provider even after first match.
❌ Mixing own-key + Clay-managed without tracking which is which.

---

## Cost-Optimization Decisions

| Situation | Recommendation |
|-----------|---------------|
| Budget < 5¢/row | Use Budget pattern (Apollo + Icypeas); accept 60% match |
| Need 80%+ match | Standard pattern is the sweet spot |
| 90%+ required and budget allows | Premium with Dropcontact |
| EU-heavy list | EU-optimized — drop Findymail (US-skewed) |
| You have Apollo seat | Use own key for cost-zero first step |
| You have Cognism seat | Phone waterfall starts there for ~50% match free |

---

## Related

- For sourcing TAM upstream (no table needed) → `/clay-tam-source` via `clay search filters-mode`.
- Source of contacts → `/clay-abm-list` (account list) + persona definition
- After enrichment → `/clay-icp-score` (rank), `/clay-outbound` (generate copy)
- Match rate too low → `/clay-troubleshoot`
