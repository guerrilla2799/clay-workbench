# Outbound — 3-Step Cold Cadence (Email + LinkedIn)

**Slug**: `outbound-3-step-cadence-cold` · **Use case**: `outbound` · **Motion**: `slg` · **Version**: `1.0`

Contact-keyed cold outbound workbook. Takes a verified-email contact list, generates per-contact first line + subject line via Claygent, gates strictly on Sending Gate, and pushes to a sequencer with per-step eligibility (email-1, LinkedIn-connect, email-2).

⚠️ **Designed to attach to upstream `abm-account-keyed-tier-1` + an email waterfall — don't run standalone.**

## When to use this
- Cold outbound to T1/T2 accounts where you have account context (trigger, pain hypothesis) and verified emails
- AE-led outbound on a Tier 1 account list with named contacts
- Replacing a brittle one-off cadence build with a repeatable, gated, verified flow

## What it produces
- Sending Gate pass rate: 50–70% of enriched rows (strict by design)
- Per-contact personalized first line (Read-Out-Loud quality target: 18/20)
- 3–6 word subjects, no clichés
- Per-step eligibility columns (email-1, LinkedIn-connect, email-2 with bounce/reply gates)
- Sequencer push only on per-step TRUE

## Required inputs (placeholders to fill)
| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{TARGET_SENIORITY}}` | Seniority levels eligible to send | `["VP", "C-level", "Director", "Senior Manager"]` |
| `{{ELIGIBLE_TIERS}}` | Account tiers eligible to send | `["T1"]` |
| `{{SUPPRESSION_TABLE_ID}}` | Clay table with customers, opt-outs, bounced-in-last-90 | `tbl_suppression_v3` |
| `{{VOICE_DESCRIPTOR}}` | One sentence of voice/tone guidance for the Claygent first-line writer | `"Direct, practitioner-focused, no marketing-speak. We sound like a peer in their role."` |
| `{{SEQUENCER_PLATFORM}}` | `salesloft` / `outreach` / `apollo` / `smartlead` / `11x` | `salesloft` |
| `{{CADENCE_ID_STEP_1}}` | Sequencer cadence ID for email-1 | `12345` |
| `{{CADENCE_ID_LINKEDIN}}` | LinkedIn-connect cadence ID (optional) | `67890` |
| `{{LINKEDIN_AUTOMATION_PLATFORM}}` | If running LinkedIn automation | `heyreach` / `dripify` / blank |

## Required integrations
- Upstream account workbook + email waterfall (one of `email-waterfall-us-smb` / `email-waterfall-eu`)
- Suppression lookup table
- Claygent (use-ai, Sonnet)
- Sequencer: any one of SalesLoft / Outreach / Apollo / Smartlead / 11x
- CRM: HubSpot or Salesforce

## Cost
- Claygent layer: 10–12 credits per contact that passes Sending Gate
- Upstream waterfall: budget separately (4–7 credits/contact)
- 1k contacts (50% Sending Gate pass): ~5,000 Claygent credits ≈ $50

## Known good for
- Pattern derived from golden ref 03 (cadence + Sending Gate + per-step eligibility sections)

## Notes / Gotchas
- **`auto_run = FALSE` during build.** Never flip to TRUE before the Read-Out-Loud test passes on 20 contacts.
- **Read-Out-Loud test is non-negotiable.** Take 20 first lines and read each aloud. If 5+ sound vendor-y, retune the prompt BEFORE pushing.
- **MUST run `/clay-claygent-iterator`** on `first_line` and `personalization_source` prompts before scaling past 25 rows. Claygent ships passable-looking-but-bad copy daily.
- The step-2 eligibility includes `step_1_bounced != TRUE` — commonly omitted, causes step-2 to fire on already-dead emails and tank sender reputation.
- LinkedIn step is optional — leave the `linkedin_url` field blank in source data to skip cleanly.
- Sender reputation lives or dies on the Sending Gate. Loosen it once, you spend months rebuilding.
- For warm/triggered outbound (signal-driven, not cold), use `outbound-3-step-cadence-warm` instead.

## Changelog
- v1.0 — 2026-06-10 — initial bootstrap from golden ref 03 cadence subset
