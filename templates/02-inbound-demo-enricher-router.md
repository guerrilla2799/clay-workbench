# Golden Workbook 02 — Inbound Demo-Form Enricher + Router

A production-ready Clay workbook for real-time inbound demo-form enrichment, scoring, and routing. Triggers within 30 seconds of form submission. Hot leads go to round-robin SDR with Slack alert; warm to nurture; cold to self-serve.

**Use when**: every B2B SaaS — demo request, contact-us, eval request, free-trial signup with business email.

**Complete time to build (manual)**: ~30 minutes plus 1-week live-ops monitoring.
**Complete time (MCP-assisted)**: ~10 minutes for a saved subroutine reuse, plus verification.

⚠️ This workbook runs with `auto_run = TRUE` once verified. Get the gates right BEFORE flipping the switch.

---

## Intake Answers (Example)

| Question | Answer |
|----------|--------|
| Source | Webhook from HubSpot demo-request form |
| Input fields | email, first_name, last_name, company_input, persona_role (custom), use_case (custom) |
| Enrichments | Company data (industry, size, revenue, HQ, funding), person data (title, seniority), trigger event |
| Gates | Personal-email auto-route-to-nurture; pass_1 = company size 50–10,000 + valid B2B; intent boost on title or use_case |
| AI columns | Persona summary (1 sentence) for SDR briefing in Slack alert |
| Outputs | HubSpot contact upsert + SalesLoft cadence push (for Hot) + Slack `#hot-inbound` |
| Auto-run | Phase 1 = OFF for testing; Phase 2 = ON after verification |
| Sample size | 10 test webhook payloads → 50 live form fills monitored → full |

---

## Column-by-Column Spec

| # | Column | Type | Provider | Credits | Run Condition |
|---|--------|------|----------|---------|---------------|
| 1 | `webhook_payload` | webhook source | form | 0 | — |
| 2 | `submitted_at` | from payload | — | 0 | — |
| 3 | `email` | from payload | — | 0 | — |
| 4 | `email_domain` | formula | — | 0 | — |
| 5 | `is_personal_email` | formula | — | 0 | — |
| 6 | `first_name`, `last_name`, `company_input`, `persona_role`, `use_case` | from payload | — | 0 | — |
| 7 | `company_domain` | formula | use email_domain if !personal else NULL | 0 | — |
| 8 | **`pass_1_qualified`** | formula | — | 0 | — |
| 9 | `company_data` | enrichment | Clay native find-company | 1 | `pass_1_qualified = TRUE` |
| 10 | `industry`, `employee_count`, `hq_country`, `revenue_range` | extracted | — | included | — |
| 11 | `person_data` | enrichment | find-and-enrich (person) | 2 | `pass_1_qualified = TRUE` |
| 12 | `title`, `seniority` | extracted | — | included | — |
| 13 | `trigger_event` | enrichment | Predictleads | 2 | `pass_1_qualified = TRUE` |
| 14 | `fit_score`, `intent_score`, `icp_score` | formula | — | 0 | — |
| 15 | `icp_band` | formula | — | 0 | — |
| 16 | `suppression_check` | lookup | — | 0 | — |
| 17 | `persona_summary` | Claygent | use-ai | 3 | `icp_band IN ["Hot", "Warm"]` |
| 18 | `route_to` | formula | — | 0 | — |
| 19 | `assigned_owner` | formula round-robin | — | 0 | `route_to = "SDR_QUEUE"` |
| 20 | `slack_message` | formula | — | 0 | `route_to = "SDR_QUEUE"` |

**Estimated cost per form fill**: ~8 credits average (most submissions disqualify or warm-route, only Hot get Claygent).
**1,000 form fills**: ~6,000 credits ≈ $60.

---

## Formulas

### `email_domain`

```clayscript
SPLIT(email, "@")[1]
```

### `is_personal_email`

```clayscript
email_domain IN [
  "gmail.com", "yahoo.com", "outlook.com", "hotmail.com",
  "aol.com", "icloud.com", "me.com", "live.com",
  "proton.me", "protonmail.com", "yandex.com", "qq.com"
]
```

### `company_domain`

```clayscript
IF(is_personal_email == TRUE,
  NULL,
  email_domain
)
```

### `pass_1_qualified`

```clayscript
IF(is_personal_email == TRUE, FALSE,
IF(company_domain IS NULL, FALSE,
  TRUE  // Pass to enrichment; downstream score does heavy lifting
))
```

### `fit_score` (5 points)

```clayscript
(IF(industry IN ["Software", "Fintech", "MarTech", "HealthTech"], 2, 0))
+ (IF(AND(employee_count >= 50, employee_count <= 10000), 1, 0))
+ (IF(hq_country IN ["United States", "United Kingdom", "Canada", "Australia"], 1, 0))
+ (IF(revenue_range IN ["$10M-$50M", "$50M-$100M", "$100M-$250M"], 1, 0))
```

### `intent_score` (5 points)

```clayscript
(IF(seniority IN ["VP", "C-level", "Director"], 2, 0))
+ (IF(trigger_event IS NOT NULL, 1, 0))
+ (IF(use_case IN ["evaluating now", "have budget", "POC"], 1, 0))
+ (IF(persona_role IN ["RevOps", "Sales", "Marketing leader"], 1, 0))
```

### `icp_band`

```clayscript
IF(suppression_check == TRUE, "SUPPRESSED",
IF(icp_score >= 8, "Hot",
IF(icp_score >= 5, "Warm",
"Cold")))
```

### `route_to`

```clayscript
IF(icp_band == "SUPPRESSED", "SUPPRESSED",
IF(is_personal_email == TRUE, "PERSONAL_EMAIL_NURTURE",
IF(icp_band == "Hot", "SDR_QUEUE",
IF(icp_band == "Warm", "MARKETING_NURTURE",
"SELF_SERVE"))))
```

### `assigned_owner` (territory + round-robin)

```clayscript
IF(hq_country IN ["United Kingdom", "Germany", "France"],
  ["sdr_emea_1", "sdr_emea_2"][MOD(ROW_INDEX, 2)],
IF(hq_country IN ["United States", "Canada"],
  ["sdr_na_1", "sdr_na_2", "sdr_na_3"][MOD(ROW_INDEX, 3)],
  ["sdr_intl_1"][0])
)
```

### Claygent `persona_summary` Prompt

```
ROLE: B2B SDR briefer. Summarize this inbound lead in ONE sentence for a 5-min SDR prep.

CONTEXT:
- Person: {first_name} {last_name}, {title} at {company_name}
- Persona role they selected: {persona_role}
- Use case they typed: "{use_case}"
- Company: {industry}, {employee_count} emp, {revenue_range}
- Trigger event (if any): {trigger_event}

TASK:
Write ONE sentence ≤30 words that gives the SDR:
1. The likely real reason they're here (interpreting use_case)
2. What to lead with on the call

FORMAT:
Return ONLY the sentence. No prefix, no quotes.

FALLBACK:
If use_case is empty or vague, default to: "Title + industry suggests evaluating for [function] — open call by asking about current stack."
```

### Slack Message Template

```
🔥 *Hot Inbound — {company_name}*
Person: {first_name} {last_name}, {title}
Email: {email} · Use case: "{use_case}"
Company: {industry} · {employee_count} emp · {hq_country}
ICP score: {icp_score}/10 · Trigger: {trigger_event}

SDR brief: {persona_summary}

Assigned: <@{assigned_owner}>
HubSpot: {hubspot_url}

🕒 SLA: 5-min response. React :raised_hand: when claimed.
```

---

## Build Sequence

### Phase 0 — Setup (5 min)

1. Create table → `"Inbound Router — Demo Form"`.
2. Add Webhook source → copy webhook URL.
3. Wire webhook URL into form platform (HubSpot form submission webhook, or direct in form action).

### Phase 1 — Build with auto_run = FALSE (15 min)

4. Add columns 4–7 (parsing formulas).
5. Add column 8 `pass_1_qualified`.
6. Add columns 9, 11, 13 enrichments with Run Condition `pass_1_qualified = TRUE`.
7. Add scoring columns 14–15.
8. Add suppression check column 16 → lookup.
9. Add column 17 `persona_summary` Claygent.
10. Add columns 18–20 routing + Slack.
11. Add Actions:
    - HubSpot upsert (filter `route_to != "SUPPRESSED"`)
    - SalesLoft push (cadence_id = "Inbound Demo Hot", filter `route_to = "SDR_QUEUE"`)
    - Slack `#hot-inbound` (filter `route_to = "SDR_QUEUE"`)

### Phase 2 — Static Test (5 min)

12. Manually submit 10 test webhook payloads covering:
    - Personal email + business email
    - In-ICP (high fit + intent) + out-of-ICP
    - With trigger + without
    - Known customer (test suppression)

13. Verify each test row:
    - Routes correctly
    - Score makes sense (compare to your manual judgment)
    - Slack alert formats correctly (test row only — don't actually fire to real channel)

### Phase 3 — Go Live (immediate)

14. Flip `auto_run = TRUE`.
15. Submit through the real form (use a test email like `you+test@yourdomain.com`).
16. Confirm row appears within 30 seconds.
17. Confirm Slack alert fires.
18. Confirm SalesLoft picks up.
19. Confirm HubSpot upsert without duplicate.
20. Document the form-submit-to-Slack latency.

### Phase 4 — Monitor (Week 1)

21. Daily check: distribution of route_to over last 24h. Anomalies?
22. Daily check: any errors in failed rows?
23. End of week: review 10 random Hot routes — were they actually good? SDR feedback?
24. Tune scoring weights if back-test shows mis-classification.

---

## Verification Checklist

- [ ] Webhook fires from form → row appears within 30s
- [ ] Personal email submissions route to PERSONAL_EMAIL_NURTURE, not SDR
- [ ] Out-of-ICP submissions route to SELF_SERVE, not SDR
- [ ] Known customer test → SUPPRESSED, no Slack alert
- [ ] Hot lead → Slack within 60s of form submit (end-to-end latency)
- [ ] SalesLoft prospect created with correct cadence
- [ ] HubSpot contact upserts without duplicate on resubmit
- [ ] Round-robin distributes evenly across SDR pool over 20 submissions

---

## Common Live-Ops Issues

| Issue | Fix |
|-------|-----|
| Slack channel flooding | Tighten Hot threshold (`icp_score >= 9`) OR add Slack daily cap |
| Hot leads going to wrong territory | Inspect `assigned_owner` formula — check territory mapping |
| Out-of-office SDR getting leads | Add OOO formula check before assignment |
| Form spam → enrichment burn | Add bot filter formula early (suspicious patterns: same email twice in 1m, special chars) |
| Latency > 60s | Reduce enrichment columns; cap Claygent max_sources |
| `pass_1` too loose | Add stricter checks: minimum company_data confidence |
| Personal-email business owners (founders use gmail) | Add override: if persona_role = "Founder" AND company_input != NULL, run company find-by-name |

---

## What Not To Do

❌ Flip `auto_run = TRUE` before Phase 2 test.
❌ Set SDR queue threshold to `icp_score >= 5` — too loose; Hot dies in noise.
❌ Skip suppression — surfacing customers in Slack #hot-inbound damages trust.
❌ Single round-robin pool when you have territory structure.
❌ Pushing personal-email leads to sequencer (often Gmail = personal interest, not buying).

---

## Related

- Score logic shared with `/clay-icp-score` — keep consistent across inbound and outbound.
- Hot route into the same outbound cadences as `/clay-outbound`.
- For bot-spam detection → enhance with template variation.
