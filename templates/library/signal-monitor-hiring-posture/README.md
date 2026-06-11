# Signal Monitor — Hiring Posture Watcher

**Slug**: `signal-monitor-hiring-posture` · **Version**: `1.0` · **Use case**: `monitoring` · **Motion**: `hybrid`

Recurring weekly hiring-trigger monitor across an ICP account watchlist. Detects when target accounts start hiring for the role categories that buy your product (RevOps Director, Head of GTM Engineering, VP Marketing Ops, etc.). Predictleads or Claygent LinkedIn jobs scan; severity-tiered routing.

## When to use this
- "When a target company starts hiring [X role], they're 6–9 months away from buying [our product]" — classic GTM signal
- Weekly trigger for Tier 1 and Tier 2 ABM accounts that haven't engaged yet
- Buying-team-formation signal (e.g. company hiring their first VP Marketing)
- Complement to `signal-monitor-job-change` — that watches PEOPLE, this watches COMPANY HIRING

## What it produces
- Per watched account/week: number of matching roles open, hottest role, recency (FRESH = posted ≤14d ago)
- Severity classification: HOT (T1 + FRESH) / WARM (T1-T2 + FRESH) / COLD / NONE
- Slack alerts (HOT real-time, WARM in weekly digest)
- CRM company write-back: `hiring_signal_last_detected` for downstream segmentation

## Required inputs (placeholders to fill)
| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{TARGET_ROLE_KEYWORDS}}` | Keyword filter for matching roles | `["RevOps", "Sales Operations", "GTM Engineer", "Head of GTM"]` |
| `{{SLACK_HOT_CHANNEL}}` | Real-time HOT hiring alerts | `#hot-hiring-signals` |
| `{{SLACK_WEEKLY_DIGEST_CHANNEL}}` | Weekly digest for WARM | `#signals-digest` |

## Required integrations
- Predictleads (recommended primary) — has clean hiring trigger data
- Claygent (use-ai) — fallback
- Clay subroutine: weekly schedule
- Slack: outbound webhook
- CRM: HubSpot or Salesforce (for company-level write-back)

## Cost
- Estimated credits/account/week: 3–7 (Predictleads cheap; Claygent fallback costs more)
- 500 watched accounts, weekly: ~2,500 credits/week ≈ $25/week
- ⚠️ Run `/clay-claygent-iterator` on the fallback prompt before scaling past 100 accounts — keyword extraction from jobs pages is a common Claygent failure mode.

## Known good for
- Pattern derived from `/clay-signal-monitor` SKILL spec (hiring variant)

## Notes / Gotchas
- **Keyword filter has to be tight.** "Sales" as a keyword matches anything sales-adjacent and floods. Use full role names like `"RevOps Director"` or `"Head of GTM Engineering"`.
- The recency window (14d for FRESH) is the difference between actionable signal and stale list — don't widen it just to surface more alerts.
- Severity respects `account_tier` — a T3 hiring fresh roles still shouldn't be HOT. If you want T3 to trigger, redo account tiering first, not this severity formula.
- Avoid running on T3 accounts at all if budget is tight — filter the watchlist upstream rather than burning credits on rows that will severity-classify to COLD/NONE.
- Common Claygent parse bug: posted_date returned as today's date instead of actual post date. Spot-check the first 10 rows.

## Changelog
- v1.0 — 2026-06-10 — initial bootstrap, hiring variant of `/clay-signal-monitor`
