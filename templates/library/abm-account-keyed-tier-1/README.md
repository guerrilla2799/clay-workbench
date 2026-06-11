# ABM Tier 1 — Account-Keyed with Triggers

**Slug**: `abm-account-keyed-tier-1` · **Version**: `1.0` · **Use case**: `abm-list` · **Motion**: `slg`

Account-keyed ABM workbook with two-pass ICP gate, trigger-event qualification, tier scoring, and route_to logic. Mirrors the pattern in golden reference `01-abm-tier1-with-triggers.md` but anonymized for cross-client reuse. Designed to be the starting point for any net-new outbound ABM list.

## When to use this
- Building a net-new account list for outbound (ABM motion)
- Building an expansion account list off a CRM segment
- Standing up a signal-driven account workflow (trigger → enrichment → tier → route)
- Replacing a brittle one-off Apollo export with a repeatable, gated, verified flow

## What it produces
- ~25–35% of source list passes pass_1 (cheap firmographic gate)
- Of those, ~50–60% pass full ICP gate (trigger + revenue band)
- Tiered output: T1 (~5–10%) → SDR queue, T2 (~20–30%) → marketing nurture, T3 (~remainder) → programmatic
- Per-account pain hypothesis with evidence URL (Claygent)
- HubSpot company records + Slack alerts for T1 only

## Required inputs (placeholders to fill)
| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{ICP_INDUSTRIES}}` | List of in-ICP industries | `["Software", "Fintech", "MarTech"]` |
| `{{ICP_GEO}}` | List of in-ICP HQ countries | `["United States", "United Kingdom", "Canada"]` |
| `{{ICP_SIZE_MIN}}` | Min employee count | `250` |
| `{{ICP_SIZE_MAX}}` | Max employee count | `2500` |
| `{{ICP_REVENUE_BANDS}}` | Revenue bands that qualify | `["$10M-$50M", "$50M-$100M", "$100M-$250M"]` |
| `{{PAIN_CATEGORIES}}` | Comma-separated pain categories your product addresses | `GTM, ops, finance, eng` |
| `{{PAIN_CATEGORIES_PIPE_SEP}}` | Same list pipe-separated for Claygent JSON enum | `GTM\|ops\|finance\|eng` |
| `{{SUPPRESSION_TABLE_ID}}` | Clay table ID with current customers + opt-outs | `tbl_abc123` |
| `{{SDR_POOL_LIST}}` | List of SDR slack user IDs for round-robin | `["U01A", "U01B", "U01C"]` |
| `{{HUBSPOT_LIST_ID}}` | HubSpot static list ID to append qualified accounts to | `12345` |
| `{{SLACK_CHANNEL}}` | Slack channel for T1 alerts | `#abm-tier1` |

## Required integrations
- Clay providers: Clay native (find-company), People Data Labs, Predictleads, Wappalyzer (lite), Claygent (use-ai)
- CRM: HubSpot
- Slack: outbound webhook to target channel

## Cost
- Estimated credits/row: ~14 for fully qualified accounts; most rows disqualify at pass_1 for ~3 credits
- 1k-row run: ~3,500 credits (assuming 25% pass_1 rate)
- Expected match rate: 25% pass_1 → 5–10% T1

## Known good for
- Anonymized from production patterns for T1 trigger-driven account-keyed outbound

## Notes / Gotchas
- The `pain_research` Claygent column uses `actionKey: "use-ai"` NOT `"ai"` — silent-drop bug if wrong
- Set Predictleads `trigger_recency_max_days = 90` at intake; stale triggers tank reply rate
- Round-robin assignment uses `MOD(ROW_INDEX, LENGTH(...))` so distribution stays even across reloads
- If `tech_stack_signals` isn't part of your gate, remove it — saves 1 credit per pass_1 row
- T1 Slack alerts can flood the channel on a fresh source dump; consider a daily cap (10/day default)

## Changelog
- v1.0 — 2026-06-10 — initial bootstrap, ported from golden ref 01
