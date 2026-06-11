# Signal Monitor — Job Change Watcher

**Slug**: `signal-monitor-job-change` · **Version**: `1.0` · **Use case**: `monitoring` · **Motion**: `hybrid`

Recurring (daily/weekly) job-change monitor for a watch list of contacts. Champify or UserGems as primary detection; Claygent LinkedIn scan as fallback. Severity-tiered routing to Slack + CRM update. Wakes up on its own schedule — no manual list refresh.

## When to use this
- Champion-alumni watchlist (former champions who left → new ICP company = HOT)
- Current-customer expansion (champion leaves → new co might be your next deal)
- ICP persona pipeline (target persona changes companies → trigger SDR play)
- Investor / advisor monitor for top-of-funnel signal
- Sales rep activity tracking (your team's prior contacts → who's now in a buying seat)

## What it produces
- Per watched contact: changed yes/no, new company, new title, days_since_change, ICP fit of new co
- Severity classification: HOT (champion to ICP within 90d) / WARM (any change to ICP-fit within 180d) / COLD / NONE
- Recommended play: SDR_NOW / AE_2WK_FOLLOWUP / NURTURE / SUPPRESS
- Slack alerts (HOT real-time, WARM in daily digest)
- CRM contact write-back so the source-of-truth stays accurate

## Required inputs (placeholders to fill)
| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{JOB_CHANGE_PROVIDER}}` | `champify` / `usergems` / leave blank for Claygent-only | `champify` |
| `{{REFRESH_INTERVAL_DAYS}}` | Days between re-checks per contact | `14` |
| `{{ICP_CRITERIA_TEXT}}` | Free-text ICP definition fed to Claygent fit check | `"B2B SaaS, 250-2500 employees, US/UK/CA HQ, Series B+"` |
| `{{SLACK_HOT_CHANNEL}}` | Real-time HOT alerts | `#hot-job-changes` |
| `{{SLACK_WARM_DIGEST_CHANNEL}}` | Daily digest for WARM | `#signals-digest` |

## Required integrations
- Champify or UserGems (recommended primary) — drop to Claygent-only if neither is available
- Claygent (use-ai) — fallback
- Clay subroutine: schedule to run daily/weekly
- Slack: outbound webhook
- CRM: HubSpot or Salesforce (for contact field write-back)

## Cost
- Estimated credits/contact/cycle: 2–5 (most cycles return "no change" at provider cost)
- 1000 watched contacts, daily cycle: ~3,000 credits/day ≈ $30/day
- HOT/WARM matches add 4 credits each (ICP fit Claygent)
- Tune `{{REFRESH_INTERVAL_DAYS}}` UP to control burn — daily for champions, weekly for cold ICP personas

## Known good for
- Pattern derived from `/clay-signal-monitor` SKILL spec

## Notes / Gotchas
- **`auto_run = TRUE` from day one.** This is a monitor, not a one-time build. Validate manually on 5 rows first, then flip auto_run + scheduler.
- **Watch segment matters for severity.** A champion changing jobs = HOT. An ICP persona changing jobs to a non-ICP co = COLD. Don't blanket-alert on all changes.
- Champify and UserGems each have ~85% detection within 14 days — keep `{{REFRESH_INTERVAL_DAYS}}` at ≥7 days or you'll burn credits checking before they've detected.
- The Claygent fallback fires ONLY when primary provider returns null — keeps cost down but means if Champify drops a contact, you'll still catch it.
- For high-value champions, consider a parallel `signal-monitor-hiring-posture` on their CURRENT company too — sometimes they don't leave, but the team grows.
- CRM write-back can create audit-trail churn — confirm with your RevOps before enabling.

## Changelog
- v1.0 — 2026-06-10 — initial bootstrap from `/clay-signal-monitor` SKILL spec
