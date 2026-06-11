# Email Waterfall — US SMB

**Slug**: `email-waterfall-us-smb` · **Version**: `1.0` · **Use case**: `enrichment` · **Motion**: `slg`

Contact-keyed email waterfall optimized for **US SMB ICPs** (10–500 employees, US-headquartered). Apollo → Findymail → Dropcontact, with ZeroBounce verification on uncertain matches.

## When to use this
- You have an account-keyed source workbook (e.g. `abm-account-keyed-tier-1`) and need to attach contacts + verified emails
- ICP is US-focused, SMB-range
- You're willing to trade ~10% match rate for ~50% lower per-row credit cost vs the EU-heavy variant

## What it produces
- 80–90% email match rate on US SMB ICPs
- `email_source` column for diagnostic + downstream skip logic
- `email_deliverable` boolean for the downstream Sending Gate

## Required inputs (placeholders to fill)
| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{ICP_GATE_FORMULA}}` | Clayscript formula that returns TRUE for in-ICP rows. **Must be present** — Global Rule 1. | `AND(account_tier == "T1", seniority IN ["VP", "C-level", "Director"])` |

## Required integrations
- Clay providers (in order): Apollo, Findymail, Dropcontact, ZeroBounce
- Apollo: Clay-managed OR own-key (own-key cheaper at volume)

## Cost
- Estimated credits/row: 4–6 (depending on cascade depth)
- 1k contacts: ~$45–60 at $0.01/credit
- Match rate: 80–90% (US SMB)

## Known good for
- Anonymized from production patterns in golden ref 03 (US-focused subset)

## Notes / Gotchas
- **Apollo verification trap**: Apollo-verified emails do NOT need ZeroBounce re-verification. The `email_source != "apollo_verified"` condition saves 1 credit per Apollo match.
- LinkedIn URL input is optional but increases match rate by 5–10% — pass it through from upstream if available.
- For EU-heavy lists, use `email-waterfall-eu` instead — Dropcontact and Datagma outperform Apollo there.
- Pair with `clay-claygent-iterator` before scaling any Claygent column downstream of this.

## Changelog
- v1.0 — 2026-06-10 — initial bootstrap from golden ref 03 waterfall section
