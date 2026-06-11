# Outbound — 3-Step Warm/Triggered Cadence

**Slug**: `outbound-3-step-cadence-warm` · **Version**: `1.0` · **Use case**: `outbound` · **Motion**: `hybrid`

Signal-driven warm outbound variant of `outbound-3-step-cadence-cold`. Attaches to a signal monitor (job change / hiring / funding / leadership / tech adoption) and inherits the signal context directly into the Claygent first-line prompt. Tighter Sending Gate (signal severity ≥ WARM required); explicit signal_context block; warm tone calibration.

## When to use this
- Job-change champion → new ICP company (highest-converting outbound play in B2B)
- Funding-round announcement → CFO / RevOps initiative (timely, congratulations-angle works)
- Hiring posture signal → buying-team formation play
- Leadership change → new-exec courtesy intro + product fit angle
- Any signal where freshness ≤30 days drives reply rate by 2–4x vs cold

## What it produces
- Sending Gate pass rate: 70–85% (signals are pre-qualified by upstream monitor)
- Per-contact warm first line that names the signal + timing proof
- Different cadence routing for HOT vs WARM (HOT = SDR_NOW immediate cadence; WARM = AE_2WK_FOLLOWUP softer cadence)
- Tighter step-2 window (2–7 days vs cold's 3–10) because signal freshness decays fast

## Required inputs (placeholders to fill)
| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{MAX_SIGNAL_AGE_DAYS}}` | Hard cutoff for signal freshness | `30` |
| `{{SUPPRESSION_TABLE_ID}}` | Customers + opt-outs + bounced + recent-contact lookup | `tbl_suppression_v3` |
| `{{VOICE_DESCRIPTOR}}` | Voice/tone guidance for the Claygent first-line writer | `"Warm but professional. Reference the signal directly. We're a peer congratulating, not pitching."` |
| `{{SEQUENCER_PLATFORM}}` | Sequencer | `salesloft` |
| `{{CADENCE_ID_HOT_STEP_1}}` | HOT-routing cadence (SDR-driven, urgent) | `1001` |
| `{{CADENCE_ID_WARM_STEP_1}}` | WARM-routing cadence (AE-driven, slower) | `1002` |

## Required integrations
- Upstream signal monitor (one of `signal-monitor-job-change` / `signal-monitor-hiring-posture` / similar)
- Email enrichment for the new contact context (in case signal source returned only LinkedIn URL)
- Suppression lookup table
- Claygent (use-ai, Sonnet)
- Sequencer: SalesLoft / Outreach / Apollo / Smartlead / 11x
- CRM: HubSpot or Salesforce

## Cost
- 10–14 credits per signal-triggered contact at Claygent layer
- Upstream signal monitor: budget separately (2–7 credits/cycle/account)
- 200 HOT/WARM signals over a quarter: ~2,400 Claygent credits ≈ $24

## Known good for
- Pattern derived from `/clay-outbound` SKILL spec + signal monitor handoff

## Notes / Gotchas
- **Warm tone is OK here** — unlike cold cadence where "congratulations" reads like a vendor opener, in a triggered cadence the signal explicitly justifies the warm reference. Tone calibration is different from cold; don't copy/paste cold prompt voice.
- **Signal freshness is the leverage.** A 90-day-old job change is a stale signal. Keep `{{MAX_SIGNAL_AGE_DAYS}} = 30` unless you have data showing longer windows still convert.
- **Different cadences for HOT vs WARM.** A C-level champion job change (HOT) doesn't go in the same cadence as a Director-level hiring signal (WARM). Different urgency, different copy.
- The step-2 window is intentionally tighter (2–7 days vs cold's 3–10) — signal freshness erodes fast.
- The `signal_context_summary` Claygent column extracts angle + timing_proof from the raw signal payload before the first_line writer ever sees it. This 2-step approach reduces "the first line just dumps the JSON" failure mode.
- Run `/clay-claygent-iterator` on both `signal_context_summary` AND `first_line` prompts before scaling past 25 rows.

## Changelog
- v1.0 — 2026-06-10 — initial bootstrap, signal-driven warm variant of cold cadence
