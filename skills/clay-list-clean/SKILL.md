---
name: clay-list-clean
description: Pre-Clay list hygiene — domain normalization, dedup, suppression filtering, role/title parsing, geo standardization, and bad-row triage on a source list BEFORE any paid Clay column runs. Prevents 30-60% of credit waste at the door. Triggers — "clean this list", "list hygiene", "dedup list", "normalize domains", "suppression list", "pre-clean", "scrub the list", "list prep", "prepare CSV for Clay", "/clay-list-clean".
---

# clay-list-clean — Pre-Clay List Hygiene

The hygiene skill. Runs **before** any other Clay sub-skill. Cleans the input list so paid columns never run on rows that should never have been there.

Inherits `clay-workbench/SKILL.md` master workflow but specializes the entire flow around input cleanup, not enrichment.

**Always run this first when:**
- Source CSV came from a sales database export
- Source is a HubSpot view that hasn't been audited recently
- Source is a scraped list (Sales Nav, Apollo export)
- Source is multiple lists merged

**Typical credit-saving impact: 30–60% of the would-be burn.**

---

## Inputs Expected

- **Source**: CSV path / HubSpot view / Salesforce report / Apollo URL / merged-list source
- **List type**: account-keyed (domain primary) / contact-keyed (email or LinkedIn primary)
- **Suppression sources**:
  - current customers (CRM closed-won)
  - opt-outs (CRM unsubscribes / suppression list)
  - already-engaged-last-30d (CRM engagement history)
  - active opportunities (CRM open deals)
- **Geo allowlist / blocklist**: ICP geos only / exclude EU under GDPR / etc.
- **Industry allowlist / blocklist**: ICP industries / exclude regulated industries / etc.
- **Title parsing requirements**: which roles to keep, which to drop (intern, junior, contractor, etc.)
- **Output**: cleaned table in Clay / cleaned CSV export / both

---

## Step 3 — Composition (Specialized)

### Canonical Column Order

| # | Column | Type | Source | Cost | Depends On |
|---|--------|------|--------|------|------------|
| 1 | `row_id` | text | source | 0 | — |
| 2 | `raw_input` | json | source | 0 | — |
| 3 | `domain_normalized` | formula | clayscript (lowercase, strip www/http, root domain) | 0 | 2 |
| 4 | `email_normalized` | formula | clayscript (lowercase, strip whitespace, validate format) | 0 | 2 |
| 5 | `linkedin_url_normalized` | formula | clayscript (canonical /in/ URL form) | 0 | 2 |
| 6 | `name_normalized` | formula | clayscript (title-case, strip honorifics, expand initials) | 0 | 2 |
| 7 | `title_normalized` | formula | clayscript (strip emoji, parse seniority, parse function) | 0 | 2 |
| 8 | `country_normalized` | formula | clayscript (ISO-3166 alpha-2) | 0 | 2 |
| 9 | `is_personal_email` | formula | clayscript (gmail/yahoo/hotmail/etc. detector) | 0 | 4 |
| 10 | `is_invalid_format` | formula | clayscript (missing required, format violation, etc.) | 0 | 3–8 |
| 11 | `dedup_key` | formula | clayscript hash | 0 | 3, 4, 5 |
| 12 | `is_duplicate_within_source` | formula | clayscript lookup | 0 | 11 |
| 13 | `is_in_suppression_customer` | formula | clayscript lookup against customer table | 0 | 3, 4 |
| 14 | `is_in_suppression_optout` | formula | clayscript lookup against opt-out table | 0 | 4 |
| 15 | `is_in_active_opportunity` | formula | clayscript lookup against CRM open deals | 0 | 3 |
| 16 | `is_recently_engaged_30d` | formula | clayscript lookup against CRM activity | 0 | 3, 4 |
| 17 | `country_allowed` | formula | clayscript (vs allowlist/blocklist) | 0 | 8 |
| 18 | `title_qualifies` | formula | clayscript (parsed seniority + function check) | 0 | 7 |
| 19 | **`row_passes`** | formula | clayscript AND of all gates | 0 | 9–18 |
| 20 | `drop_reason` | formula | clayscript (which gate failed — primary cause) | 0 | 9–18 |

### `domain_normalized` Pattern

```clayscript
LOWERCASE(
  TRIM(
    REGEX_REPLACE(
      raw_domain,
      "^(https?://)?(www\\.)?([^/]+)/?.*$",
      "$3"
    )
  )
)
```

### `email_normalized` Pattern

```clayscript
IF(
  REGEX_MATCH(raw_email, "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"),
  LOWERCASE(TRIM(raw_email)),
  NULL
)
```

### `is_personal_email` Detector

```clayscript
IF(
  REGEX_MATCH(email_normalized, "@(gmail|yahoo|hotmail|outlook|icloud|aol|protonmail|live|msn|me)\\."),
  TRUE,
  FALSE
)
```

### `dedup_key` Pattern

```clayscript
COALESCE(
  email_normalized,
  CONCAT(domain_normalized, "::", LOWERCASE(name_normalized)),
  linkedin_url_normalized,
  row_id
)
```

Falls back gracefully if email missing.

### `row_passes` Composite Gate

```clayscript
AND(
  is_invalid_format == FALSE,
  is_duplicate_within_source == FALSE,
  is_in_suppression_customer == FALSE,
  is_in_suppression_optout == FALSE,
  is_in_active_opportunity == FALSE,
  is_recently_engaged_30d == FALSE,
  country_allowed == TRUE,
  title_qualifies == TRUE,
  OR(is_personal_email == FALSE, {ALLOW_PERSONAL_EMAILS} == TRUE)
)
```

### `drop_reason` Pattern

```clayscript
CASE(
  is_invalid_format == TRUE, "INVALID_FORMAT",
  is_in_suppression_customer == TRUE, "CUSTOMER",
  is_in_suppression_optout == TRUE, "OPTED_OUT",
  is_in_active_opportunity == TRUE, "OPEN_OPP",
  is_recently_engaged_30d == TRUE, "RECENTLY_ENGAGED",
  is_duplicate_within_source == TRUE, "DUPLICATE",
  country_allowed == FALSE, "GEO_OUT_OF_SCOPE",
  title_qualifies == FALSE, "TITLE_OUT_OF_SCOPE",
  is_personal_email == TRUE AND {ALLOW_PERSONAL_EMAILS} == FALSE, "PERSONAL_EMAIL",
  "PASS"
)
```

---

## Step 5 — Execution (Specialized)

### Preferred Path: Tier 1 (official Agent Plugin) — see resources/execution-surface.md

```
1. clay credits — balance pre-flight (this skill costs ~0 credits — all formulas)
2. Load source via:
   - CSV upload → Clay table
   - HubSpot view → mcp__claude_ai_Clay__query-objects (Tier 2 — connector) to pull, then re-import
   - Salesforce report → CSV bridge
3. Append the 20 hygiene columns
4. Run formulas — instant (no credits)
5. Pull the report via `clay tables rows/query` or the `table` MCP tool: count by drop_reason
6. Hand back: cleaned table view (filter row_passes = TRUE) + reject view (filter row_passes = FALSE, grouped by drop_reason)
```

### Manual Fallback (Tier 3)

Table creation and column-formula edits are still UI-only (see resources/execution-surface.md):

1. New table → `"Hygiene — {source descriptor} — {date}"`
2. Source → CSV / HubSpot view / Salesforce report
3. Add columns 1–20 in order — all formula columns, all 0-credit
4. Pull the suppression tables in as linked tables (customers, opt-outs, open opps, recent activity)
5. Run all formulas (instant)
6. Build views:
   - **Clean view**: filter `row_passes = TRUE`
   - **Drop view**: filter `row_passes = FALSE`, group by `drop_reason`
7. Export the clean view to wherever the next sub-skill consumes from

---

## Standard Output (Hygiene Report)

```
## List Hygiene Report — {source_name}

### Source
- Raw rows: {N}
- Source type: {csv|hubspot|salesforce|apollo|merged}
- Date pulled: {date}

### Outcomes
| Outcome | Count | % |
|---------|-------|---|
| PASS                     | ... | ... |
| INVALID_FORMAT           | ... | ... |
| CUSTOMER (suppressed)    | ... | ... |
| OPTED_OUT                | ... | ... |
| OPEN_OPP                 | ... | ... |
| RECENTLY_ENGAGED         | ... | ... |
| DUPLICATE                | ... | ... |
| GEO_OUT_OF_SCOPE         | ... | ... |
| TITLE_OUT_OF_SCOPE       | ... | ... |
| PERSONAL_EMAIL           | ... | ... |
| **Net to enrich**        | ... | ... |

### Credit Savings Estimate
- Avoided enrichment cost: {dropped_rows} × {avg_credits_per_row} = {credits_saved}
- ≈ ${dollar_savings} at current tier

### Anomalies to Flag
- {e.g., "40% of rows had non-canonical domains — recommend fixing source extract"}
- {e.g., "Suppression hits clustered in one tier — check if a customer renewal data refresh is missing"}

### Handoff
- Clean view: {N} rows ready for {next sub-skill}
- Drop view stored at {table_url} for audit
```

---

## Verify-and-Handoff Checklist

- [ ] 5-row spot-check: every normalized field correct
- [ ] Suppression tables linked and current (customers refreshed ≤7d ago)
- [ ] `is_personal_email` detector covers user's known personal-domain list
- [ ] Country normalization covers all forms in raw data (US/USA/United States all normalize to `US`)
- [ ] Title parsing matches user's ICP rubric
- [ ] Dedup logic produces zero false-positive merges (verify by hand on 10 rows)
- [ ] Drop view grouped by `drop_reason` is readable
- [ ] Net-to-enrich count matches the downstream sub-skill's expected input shape
- [ ] Anomaly callouts in the hygiene report capture upstream data issues (so source can be fixed)

---

## Use-Case Variants

| Source | Common Issues to Watch | Special Handling |
|--------|----------------------|------------------|
| Apollo export | Personal-email-only rows; outdated titles | Aggressive `is_personal_email` filter; gate to LinkedIn-verified titles only |
| HubSpot view | Multiple records per person across companies | Dedup on email primary, not domain+name |
| Salesforce report | Inactive contacts still flagged active | Re-check `is_in_active_opportunity` against current SF state |
| Sales Nav scrape | Names with emojis/non-Latin chars | Stronger `name_normalized`, watch encoding |
| Merged sources | Same person from 3 sources | Dedup with source-precedence priority (prefer CRM > Apollo > Sales Nav) |
| Conference attendee CSV | Personal emails + no titles | Allow personal emails as exception; gate harder on title-out-of-scope |
| Customer expansion list | Should NOT be suppressed as customer | Override `is_in_suppression_customer` for this use case |

---

## Anti-Patterns

❌ Running enrichment columns before this hygiene pass — guaranteed credit waste.
❌ Stale suppression lists (>14d old for customer list) — enriching and outbound-ing to current customers.
❌ Dedup on `domain_normalized` alone for contact lists — drops legit multi-contact records.
❌ Skipping personal-email filter for B2B outbound — kills sender reputation.
❌ Treating "INVALID_FORMAT" as small — usually 5–15% of any sales DB export, all wasted credits otherwise.
❌ Single drop_reason per row when multiple gates fail — primary reason only is fine; don't get fancy.
❌ Hygiene table not preserved post-cleanup — auditors / future-you need to see what got dropped and why.

---

## Related

- After clean → feeds directly into `/clay-abm-list`, `/clay-enrich-waterfall`, `/clay-account-research`, `/clay-prospect-research`, or `/clay-outbound`.
- For ongoing list health (not pre-clean) → `/clay-troubleshoot` for stale-data and decay analysis.
- For CRM-level dedup (Clay-adjacent) → use HubSpot/Salesforce native dedup; this skill targets the Clay-side input.
