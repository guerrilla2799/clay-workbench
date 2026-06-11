---
name: clay-inbound-routing
description: Build inbound enrichment and routing workbooks in Clay — webhook source from demo forms / signups / content downloads, enrich on arrival, ICP-gate, route to SDR queue or marketing nurture or self-serve. Adds round-robin assignment, Slack alerts on Hot, and CRM upsert. Triggers — "inbound router", "demo form router", "enrich form fills", "MQL routing", "round-robin", "lead routing", "inbound enricher", "form to SDR", "/clay-inbound-routing".
---

# clay-inbound-routing — Inbound Enrich + Route

Composes the webhook-fed, real-time enrichment + scoring + routing workbook for inbound leads (demo forms, content downloads, free signups, contact-us). Auto-run = ON for this workbook (unlike most others).

Inherits master workflow. Specializes step 3 (webhook + routing composition) and step 5 (live ops monitoring).

---

## Inputs Expected

From intake:
- **Source**: webhook URL from which form / Marketo / HubSpot form / product signup
- **Input fields the form sends**: email (required) / first_name / last_name / company / phone / custom
- **Routing rules**:
  - Hot threshold → SDR queue with round-robin
  - Warm threshold → nurture sequence
  - Cold → self-serve nurture or drop
- **CRM destination**: HubSpot / Salesforce — create or upsert?
- **Alert channels**: Slack channel for Hot leads, Slack channel for high-tier accounts
- **Round-robin pool**: list of SDR / AE IDs in the destination system
- **SLA target**: time-to-first-touch for Hot leads (default: 5 minutes)

---

## Step 3 — Composition (Specialized)

### Auto-Run Setting

**THIS WORKBOOK RUNS WITH `auto_run = TRUE`** — unlike ABM workbooks. Justification: inbound speed beats every other lever. Sub-5-minute follow-up multiplies connect rates 4–8x vs >1 hour.

⚠️ Verify ICP gate is bulletproof before flipping auto_run on — otherwise you'll burn credits + over-notify Slack.

### Column Spec

| # | Column | Type | Source | Cost | Run Condition |
|---|--------|------|--------|------|---------------|
| 1 | `webhook_payload` | webhook source | form submission | 0 | — |
| 2 | `email` | from payload | — | 0 | — |
| 3 | `email_domain` | formula | parse email | 0 | — |
| 4 | `is_personal_email` | formula | check against gmail/yahoo/etc. | 0 | — |
| 5 | `first_name` | from payload | — | 0 | — |
| 6 | `last_name` | from payload | — | 0 | — |
| 7 | `company_input` | from payload | — | 0 | — |
| 8 | `company_domain` | formula or enrichment | use email_domain if not personal else lookup | 0–1 | NOT is_personal_email |
| 9 | `company_data` | enrichment | find-and-enrich-company | 1 | company_domain IS NOT NULL |
| 10 | `industry`, `employee_count`, `hq_country`, `revenue_range` | enrichment fields | — | included | — |
| 11 | `person_data` | enrichment | find-and-enrich (job title, seniority) | 2 | email IS NOT NULL |
| 12 | `trigger_event_check` | enrichment | Predictleads check on company_domain | 2 | gate_pass_1 = TRUE |
| 13 | **`gate_pass_1`** | formula | quick disqualification (company size, industry) | 0 | — |
| 14 | **`icp_band`** | formula | composite score from `/clay-icp-score` | 0 | gate_pass_1 |
| 15 | `suppression_check` | lookup | against customer + opt-out tables | 0 | — |
| 16 | `route_to` | formula | band + suppression → destination | 0 | — |
| 17 | `assigned_owner` | formula | round-robin from pool | 0 | route_to = "SDR_QUEUE" |
| 18 | `crm_action` | formula | create / update / noop | 0 | — |
| 19 | `slack_message` | formula | Slack-formatted alert | 0 | route_to = "SDR_QUEUE" |

### Round-Robin Formula

```clayscript
// Simple round-robin among 4 SDRs
SDR_pool = ["sdr_alice_id", "sdr_bob_id", "sdr_carla_id", "sdr_dan_id"]
SDR_pool[MOD(ROW_INDEX, 4)]
```

For weighted round-robin (some SDRs get more):

```clayscript
weighted_pool = ["alice", "alice", "bob", "carla", "carla", "carla", "dan"]
weighted_pool[MOD(ROW_INDEX, LENGTH(weighted_pool))]
```

For territory-based (geo / industry assignment):

```clayscript
IF(industry IN ["FSI","Insurance"], "alice_id",
IF(industry IN ["Healthcare","Biotech"], "bob_id",
IF(hq_country == "UK", "carla_id",
"dan_id")))
```

### Route-To Formula

```clayscript
IF(suppression_check == TRUE, "SUPPRESSED",
IF(is_personal_email == TRUE, "PERSONAL_EMAIL_NURTURE",
IF(gate_pass_1 == FALSE, "SELF_SERVE",
IF(icp_band == "Hot", "SDR_QUEUE",
IF(icp_band == "Warm", "MARKETING_NURTURE",
"SELF_SERVE")))))
```

### Slack Alert Template

```
🔥 *Hot Inbound — {company_name}*
Person: {first_name} {last_name}, {title}
Email: {email}
Industry: {industry} · {employee_count} employees · {hq_country}
Trigger: {trigger_event} ({trigger_recency_days}d ago)
Assigned: <@{assigned_owner}>
ICP Score: {icp_score}/10
{crm_link}

SLA: 5-min response target. Reply :handshake: when claimed.
```

---

## Step 5 — Execution (Specialized)

### Pre-Live-Op Verification (Mandatory before auto_run = TRUE)

```
Phase 1 — Static test (auto_run = FALSE):
  1. Submit 10 test webhook payloads spanning:
     - Personal email + business email
     - In-ICP + out-of-ICP
     - With trigger + without
     - Known customer + new prospect
  2. Verify each routes to correct destination.
  3. Verify Slack messages format correctly.
  4. Verify CRM upsert dedups correctly.

Phase 2 — Live test on real form (auto_run = TRUE):
  1. Flip auto_run = TRUE for the workbook.
  2. Submit through real form (don't use webhook directly).
  3. Watch the row appear within 30 seconds.
  4. Verify end-to-end: form → Clay → CRM → SDR / Slack
  5. Measure: form-submit-to-Slack-alert latency. Target: <60s.

Phase 3 — Full production:
  1. Document the SLA expectations for SDR team.
  2. Set up weekly review of low-confidence routes (e.g., is_personal_email = TRUE but high-fit company in HubSpot — should they have been routed differently?)
```

### MCP Path (Live Operations)

```
# Periodic health check (run as cron-style monitoring)
mcp__claude_ai_Clay__query-objects (last 24h of rows)
→ Distribution check: % Hot / Warm / Cold / Suppressed / Self-Serve
→ Anomaly check: spike in Suppressed could indicate customer-table dirty data
→ Anomaly check: spike in SELF_SERVE could indicate ICP shift or form-spam

mcp__claude_ai_Clay__ask-question-about-accounts:
  "What's the Hot route rate by source in the last 7 days?"
  "Which industries are sourcing the most Hot leads this week?"
```

### Manual Fallback — Build in Clay UI

1. Create table → name "Inbound Router — {form_name}".
2. Set source → Webhook → copy webhook URL → wire into the form / Marketo / HubSpot.
3. Add columns 2–19 from spec.
4. Configure all paid columns (9, 11, 12) with run conditions per spec.
5. Add Actions:
   - **CRM upsert** → push-hubspot (or push-salesforce), filter: `route_to != "SUPPRESSED"`
   - **SDR queue push** → push-salesloft / push-outreach, filter: `route_to = "SDR_QUEUE"`, mapping `assigned_owner` to owner field
   - **Slack notify** → slack-notify, channel from intake, filter: `route_to = "SDR_QUEUE"`, message_template from above
6. Set `auto_run = FALSE`.
7. Run Phase 1 verification.
8. Flip `auto_run = TRUE` after Phase 1.
9. Monitor for 7 days actively.

---

## Variants

### High-Volume Inbound (>500/day)
- Add bot filter formula column: `is_likely_bot` based on email patterns, IP if available, form submit speed.
- Filter out is_likely_bot before enrichment to save credits.
- Consider sampling enrichment if volume too high — pick top 50% by gate_pass_1 score.

### Multi-Source Inbound (multiple forms)
- One workbook per source for clean reporting OR one workbook with `source` column for unified routing.
- Single workbook usually wins — reuses enrichment, scoring, suppression logic.

### Multi-Region Routing
- Territory routing formula → assigned_owner per region.
- Separate Slack channels per region (e.g., `#hot-leads-emea`).

### Free Tier / Self-Serve Product Signup
- Source from product signup webhook.
- Score on behavioral (used product? team invited?) + firmographic.
- `route_to` of "PRODUCT_ENGAGEMENT" stays in product, no SDR touch until usage threshold.

---

## Anti-Patterns

❌ Setting `auto_run = TRUE` before Phase 1 verification — burns credits + triggers false Slack alerts.
❌ No bot filter on high-volume forms — enriches obvious spam.
❌ Treating personal-email submissions as Hot — usually low quality, route to nurture or block.
❌ No suppression check on customers — embarrassing to push a current customer to SDR queue.
❌ Round-robin without out-of-office handling — leads pile up on unavailable reps.
❌ No SLA tracking — Hot routing without response time accountability defeats the speed advantage.
❌ Single mega-Slack-channel — Hot signal dies in the noise. Split by tier / territory.

---

## SLA Tracking (Recommended Add-On)

Add columns:

| Column | Purpose |
|--------|---------|
| `created_at` | webhook arrival timestamp |
| `first_touch_at` | filled by SDR / sequencer |
| `response_seconds` | formula: first_touch_at - created_at |
| `sla_met` | formula: response_seconds <= sla_target_seconds |

Weekly review: % SLA met by rep, by source, by tier. Coach on misses.

---

## Related

- Score logic shared with `/clay-icp-score` — use same rubric for inbound and outbound consistency.
- Hot route into `/clay-outbound` (SDR sequence templates).
- Form spam diagnosis → `/clay-troubleshoot`.
