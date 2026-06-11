# Golden Workbook 03 — Cold Outbound Multi-Provider Waterfall

A production-ready Clay workbook for cold outbound that takes a target account list, finds 1–3 contacts per account, runs a multi-provider email + phone waterfall with graceful exit, generates personalized first lines and subject lines with Claygent, and pushes to a sequencer behind a strict Sending Gate.

**Use when**: net-new cold outbound to a Tier 1 or Tier 2 account list. Replaces brittle one-off lists with a repeatable, gated, verified flow.

**Complete time to build (manual)**: ~35 minutes.
**Complete time (MCP-assisted)**: ~10 minutes for saved subroutine reuse.

---

## Intake Answers (Example)

| Question | Answer |
|----------|--------|
| Source | Existing Clay table from Workbook 01 (`account_tier = "T1"`) |
| Input fields | company_domain, company_name, industry, employee_count, trigger_event |
| Enrichments | 2 contacts per account (specific titles), email + verify, phone, LinkedIn URL |
| Gates | account_tier = T1, verified email, seniority match, not suppressed |
| AI columns | Personalized first line (per contact), subject line (per contact), persona-fit summary |
| Outputs | SalesLoft cadence "T1 Cold Outbound — Step 1" + HubSpot contact upsert |
| Auto-run | OFF during build, ON only after Phase 3 verification |
| Sample size | 1 account × 2 contacts → 10 accounts → full T1 list |

---

## Column-by-Column Spec — Contact-Keyed

This workbook is **contact-keyed** (one row per contact). It branches off the account workbook from template 01.

| # | Column | Type | Provider | Credits | Run Condition |
|---|--------|------|----------|---------|---------------|
| 1 | `account_id` | lookup | Workbook 01 | 0 | source is `account_tier = "T1"` |
| 2 | `company_domain`, `company_name`, `industry`, `trigger_event`, `pain_research` | lookup | Workbook 01 | 0 | — |
| 3 | `contacts_found` | enrichment | find-and-enrich-contacts-at-company | 1/contact | gated upstream |
| 4 | `first_name`, `last_name`, `title`, `seniority`, `linkedin_url` | from contacts_found | — | included | — |
| 5 | `email_apollo` | enrichment | Apollo | 1 | seniority IN [VP, C-level, Director, Manager] |
| 6 | `email_findymail` | enrichment | Findymail | 2 | email_apollo IS NULL |
| 7 | `email_datagma` | enrichment | Datagma | 2 | email_findymail IS NULL |
| 8 | `email` | formula | coalesce | 0 | — |
| 9 | `email_source` | formula | — | 0 | — |
| 10 | `email_verified` | enrichment | ZeroBounce | 1 | email IS NOT NULL AND email_source != "apollo_verified" |
| 11 | `phone_apollo` | enrichment | Apollo | 1 | email_verified = "valid" |
| 12 | `phone_datagma` | enrichment | Datagma | 2 | phone_apollo IS NULL |
| 13 | `phone` | formula | coalesce | 0 | — |
| 14 | `enrichment_complete` | formula | email AND linkedin_url | 0 | — |
| 15 | `suppression_check` | lookup | customer + recent_contact tables | 0 | — |
| 16 | **`sending_gate_eligible`** | formula | — | 0 | — |
| 17 | `personalization_source` | Claygent | use-ai | 4 | `sending_gate_eligible = TRUE` |
| 18 | `first_line` | Claygent | use-ai | 3 | `sending_gate_eligible = TRUE` |
| 19 | `subject_line` | Claygent | use-ai | 2 | `sending_gate_eligible = TRUE` |
| 20 | `step_1_eligible` | formula | sending_gate AND first_line valid | 0 | — |
| 21 | `step_2_eligible` | formula | step_1_eligible AND not_replied_after_1 | 0 | — |
| 22 | `linkedin_step_eligible` | formula | sending_gate AND linkedin_url | 0 | — |

**Estimated cost per contact (Hot pursuit, full stack)**: ~16 credits.
**1,000 contacts** = ~16,000 credits ≈ $160 at $0.01/credit.

---

## Formulas

### `email` (coalesce)

```clayscript
COALESCE(email_apollo, email_findymail, email_datagma)
```

### `email_source`

```clayscript
IF(email_apollo IS NOT NULL, "apollo",
IF(email_findymail IS NOT NULL, "findymail",
IF(email_datagma IS NOT NULL, "datagma",
NULL)))
```

### `phone` (coalesce)

```clayscript
COALESCE(phone_apollo, phone_datagma)
```

### `enrichment_complete`

```clayscript
AND(
  email IS NOT NULL,
  email_verified IN ["valid", "accept_all_high"],
  linkedin_url IS NOT NULL
)
```

### `sending_gate_eligible` — Strict

```clayscript
AND(
  enrichment_complete == TRUE,
  suppression_check == FALSE,
  seniority IN ["VP", "C-level", "Director", "Senior Manager"],
  account_tier == "T1",
  NOT(EXISTS(prior_contact_in_last_30_days))
)
```

### Per-Step Eligibility

```clayscript
// step_1_eligible
sending_gate_eligible == TRUE
  AND LENGTH(first_line) >= 30
  AND first_line NOT CONTAINS "[no personalization available]"

// step_2_eligible
step_1_eligible == TRUE
  AND step_1_sent_at IS NOT NULL
  AND step_1_replied != TRUE
  AND DAYS_SINCE(step_1_sent_at) >= 3
  AND DAYS_SINCE(step_1_sent_at) <= 10

// linkedin_step_eligible
sending_gate_eligible == TRUE
  AND linkedin_url IS NOT NULL
  AND linkedin_connection_status != "connected"
```

### Claygent Prompts

#### `personalization_source`

```
ROLE: B2B sales researcher finding ONE specific public observation about a prospect.

CONTEXT:
- Person: {first_name} {last_name}, {title} at {company_name}
- LinkedIn: {linkedin_url}
- Company trigger: {trigger_event}
- Company pain hypothesis: {pain_research.pain}

SOURCES TO CHECK (max 3):
1. Person's LinkedIn — recent post or work history
2. Company website /about, /careers, blog
3. Recent news / press release tied to {trigger_event}

TASK:
Identify ONE specific observation that:
- Is verifiably public (with URL)
- Connects to the persona's likely day-to-day (not generic company news)
- A peer would notice — not a robot

Return EXACT JSON:
{
  "observation": "string (15-25 words, specific, peer-noticed)",
  "url": "string (URL where verifiable)",
  "tie_to_pain": "string (1 sentence connecting to their likely pain)"
}

FALLBACK:
If no specific persona-level signal found, return:
{
  "observation": "{trigger_event} at {company_name} — broader company-level reference",
  "url": "{company_url}/news",
  "tie_to_pain": "Company-level observation; first line will be company-tier, not person-tier."
}
```

#### `first_line`

```
ROLE: Peer-to-peer B2B sales rep. Writing the OPENING line of a cold email.

CONTEXT:
- Recipient: {first_name}, {title}
- Observation: {personalization_source.observation}
- Tie to pain: {personalization_source.tie_to_pain}
- URL evidence: {personalization_source.url}

TASK:
Write ONE sentence (15-25 words) that:
- Leads with the observation (NOT "I came across" or "I noticed")
- Sounds like a colleague, not a vendor
- Sets up the pain naturally for sentence 2

Banned words: unlock, leverage, supercharge, hope, came across, noticed
Banned starts: "I", "Hope", "Hi {name}"

FORMAT:
Return the sentence ONLY. No quotes, no signature.

FALLBACK:
If personalization is generic, write a company-level first line referencing trigger_event.
If even that's weak, return: "[no personalization available]" — this will skip step 1 via gate.
```

#### `subject_line`

```
ROLE: B2B subject line writer. 3-6 words, no emoji, no ALL CAPS, no clickbait.

CONTEXT:
- Recipient: {first_name} at {company_name}
- Trigger: {trigger_event}
- Pain category: {pain_research.category}

TASK:
Write a 3-6 word subject. One of these patterns:
- "{specific_term} at {company_name}?"
- "{trigger_event} → {pain_category}?"
- "{first_name} - quick context"
- "{specific_noun_they_use_internally}"

FORMAT: Subject line only.
```

---

## Build Sequence

### Phase 1 — Branch off Workbook 01 (10 min)

1. Open Workbook 01 → filter to `account_tier = "T1"`.
2. Create new table → "Contact Outbound — T1 — {date}".
3. Source: import from Workbook 01 (T1 filter) → preserves lookup chain.
4. Add column 3 `contacts_found` → find-and-enrich-contacts-at-company.
   - Input: company_domain
   - Titles to find: ["VP Sales", "VP Marketing", "Head of RevOps", "Director Sales", "Director Marketing"]
   - Max 3 contacts per account.
   - Run Condition: (none — account_tier already gated upstream)
5. Add columns 5–7 (email waterfall) with run conditions per spec.
6. Add coalesce columns 8–9.
7. Add column 10 ZeroBounce verification.
8. Add columns 11–13 phone waterfall.
9. Add columns 14–15 (enrichment_complete, suppression_check).
10. Add column 16 `sending_gate_eligible`.

### Phase 2 — AI Copy (10 min)

11. Add column 17 personalization_source Claygent (max_sources=3, model=Sonnet).
12. Add column 18 first_line Claygent.
13. Add column 19 subject_line Claygent.
14. Add columns 20–22 per-step eligibility.

### Phase 3 — Sample Run + Read-Out-Loud Test (10 min)

15. `auto_run = FALSE`.
16. Run on 1 account → 2 contacts (≈2 rows).
17. Inspect every cell:
    - Enrichment complete?
    - Sending gate TRUE/FALSE matches manual judgment?
    - First line: read aloud. Sounds like a peer? Specific? Reject and iterate prompt if any "vendor-tone" or generic.
    - Subject line: 3–6 words. Specific.
18. If 2/2 pass, run on 10 accounts (≈20 contacts).
19. Re-test the Read-Out-Loud rule on the 20 rows. Aim 18/20 pass.

### Phase 4 — Sequencer Push (5 min)

20. Add SalesLoft push action:
    - Cadence: "T1 Cold Outbound — Step 1"
    - Run Condition: `step_1_eligible = TRUE`
    - Map: email, first_name, last_name, company_name, custom_first_line, custom_subject
21. (Optional) Add Outreach / Apollo / 11x push as well — same Run Condition.
22. Add HubSpot contact upsert.
23. Verify a 5-row test push lands correctly in SalesLoft (cadence active, fields filled).

### Phase 5 — Full Run + Monitor (ongoing)

24. Run full T1 list.
25. Track per-day:
    - Sequencer enrolled count
    - Reply rate by step
    - Bounce rate (target <2%)
    - Subjectability heuristic — open rate >30% suggests subjects working
26. After 14 days, prune step 2 push: stop pushing to step 2 for contacts where step 1 had no open.

---

## Verification Checklist

- [ ] 1-account / 2-contact sample: contacts_found returns valid people
- [ ] Email waterfall match rate ≥ 80% on 25-row sample
- [ ] Phone waterfall match rate ≥ 30% on 25-row sample
- [ ] Sending Gate filter manually verified on 20 rows (no false TRUEs)
- [ ] Read-Out-Loud first lines: 18/20 pass peer-tone test
- [ ] Subject lines all 3–6 words, no emoji, no clichés
- [ ] SalesLoft test push lands 5 contacts in cadence correctly
- [ ] HubSpot dedups (no duplicate contacts on resubmit)
- [ ] Step 2 cadence respects 3–10 day window
- [ ] Bounce rate < 2% after first 100 sends

---

## Common Issues

| Issue | Diagnosis | Fix |
|-------|-----------|-----|
| First line sounds vendor-y | Claygent prompt too lenient | Add explicit banned phrases, re-prompt with examples |
| Email match rate < 60% | Wrong waterfall mix for ICP | Swap providers per `clay-enrich-waterfall` guidance |
| Subject too long | Prompt drift | Re-tighten "3–6 words" with examples in prompt |
| step_2 firing while step_1 still bouncing | No bounce check in step_2 eligible | Add `step_1_bounced != TRUE` condition |
| SDR complaints about bad fit | Sending Gate too loose | Tighten seniority list, add account_tier check |

---

## Cost Optimization Variants

| Variant | Change | Impact |
|---------|--------|--------|
| Skip phone waterfall | Remove columns 11–13 | Save ~3 credits per contact |
| Use Apollo own-key | Set as primary email step | Save 1 credit per Apollo match |
| Claygent only on top 50% | Add `step_priority` formula | Save ~9 credits on lower-tier rows |
| Skip subject line Claygent | Use formula-based subject | Save 2 credits per row |

---

## What Not To Do

❌ Push to sequencer without `sending_gate_eligible` filter.
❌ Use one mega Sending Gate without per-step eligibility (sequencer can't fan out correctly).
❌ Skip the Read-Out-Loud test — Claygent ships passable-looking-but-bad copy daily.
❌ Verify Apollo "verified" emails — wasted credit.
❌ Run Claygent on rows where sending_gate is FALSE — wasted credit on rows that won't send.
❌ Push step 2 without bounce/reply check on step 1.

---

## Related

- Account source from template `01-abm-tier1-with-triggers.md`.
- Per-skill detail → `/clay-enrich-waterfall`, `/clay-outbound`.
- Reply analytics + diagnostic → `/clay-troubleshoot`.
