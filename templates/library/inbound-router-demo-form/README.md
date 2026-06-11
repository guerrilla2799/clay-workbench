# Inbound Demo-Form Enricher + Router

**Slug**: `inbound-router-demo-form` · **Version**: `1.0` · **Use case**: `inbound` · **Motion**: `hybrid`

Real-time inbound demo-form enrichment, scoring, and routing. Triggers within 30s of form submission. Hot leads go to round-robin SDR with Slack alert; warm to nurture; cold to self-serve; personal-email to nurture pool.

⚠️ **Runs with `auto_run = TRUE` once verified. Get the gates right BEFORE flipping the switch.**

## When to use this
- Any B2B SaaS demo-request, contact-us, eval-request, or free-trial form with business email
- When SDR team complains about lead quality from inbound
- When marketing wants real-time routing instead of manual triage

## What it produces
- ~85% of submissions pass `pass_1` (excludes personal-email)
- Of those, ~10–15% score as Hot (icp_score >= 8) → SDR queue + Slack alert
- ~25–30% Warm → marketing nurture
- Remainder Cold → self-serve
- Sub-60s end-to-end latency from form submit to Slack alert

## Required inputs (placeholders to fill)
| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{ICP_INDUSTRIES}}` | In-ICP industries | `["Software", "Fintech", "MarTech", "HealthTech"]` |
| `{{ICP_GEO}}` | In-ICP HQ countries | `["United States", "United Kingdom", "Canada", "Australia"]` |
| `{{ICP_SIZE_MIN}}` / `{{ICP_SIZE_MAX}}` | Employee count band | `50` / `10000` |
| `{{ICP_REVENUE_BANDS}}` | Revenue bands | `["$10M-$50M", "$50M-$100M", "$100M-$250M"]` |
| `{{ICP_SENIORITY}}` | High-intent seniority levels | `["VP", "C-level", "Director"]` |
| `{{HIGH_INTENT_USE_CASES}}` | Free-text use_case values that signal high intent | `["evaluating now", "have budget", "POC"]` |
| `{{ICP_PERSONA_ROLES}}` | In-ICP self-selected roles | `["RevOps", "Sales", "Marketing leader"]` |
| `{{SUPPRESSION_TABLE_ID}}` | Clay table ID with customers + opt-outs + bounced emails | `tbl_xyz789` |
| `{{NA_SDR_POOL}}` / `{{EMEA_SDR_POOL}}` / `{{INTL_SDR_POOL}}` | Slack user ID arrays by territory | `["U01A", "U01B", "U01C"]` |
| `{{NA_COUNTRIES}}` / `{{EMEA_COUNTRIES}}` | Territory country lists | `["United States", "Canada"]` |
| `{{SALESLOFT_INBOUND_HOT_CADENCE_ID}}` | SalesLoft cadence for Hot inbound | `12345` |
| `{{SLACK_HOT_INBOUND_CHANNEL}}` | Slack channel for Hot alerts | `#hot-inbound` |

## Required integrations
- Webhook source from form platform (HubSpot form submission, custom form action, etc.)
- Clay providers: find-company, find-and-enrich-contact, Predictleads, Claygent (use-ai)
- CRM: HubSpot
- Sequencer: SalesLoft (swappable for Outreach / Apollo / Smartlead — adjust action key)
- Slack: outbound webhook

## Cost
- Estimated credits/row: ~8 (most submissions disqualify at pass_1 or warm-route; only Hot get Claygent)
- 1k form fills: ~6,000 credits ≈ $60
- Sub-60s end-to-end latency target

## Known good for
- Anonymized from production patterns used in standard B2B SaaS inbound flows

## Notes / Gotchas
- **Phase 1: `auto_run = FALSE`** — build, test 10 static webhook payloads. Phase 2 only flips after manual verification on 20 rows.
- Personal-email founders DO exist — if `persona_role = "Founder" AND company_input != NULL`, add override to run company find-by-name instead of routing to nurture
- Bot spam: add filter formula early (same email twice in 1m, suspicious char patterns) to avoid enrichment burn
- Latency > 60s usually means too many enrichments — cap Claygent `max_sources = 2`
- Out-of-office SDR getting leads: add OOO formula check before `assigned_owner` resolves
- Hot threshold drift: if Slack channel floods, tighten to `icp_score >= 9` OR add daily cap

## Changelog
- v1.0 — 2026-06-10 — initial bootstrap, ported from golden ref 02
