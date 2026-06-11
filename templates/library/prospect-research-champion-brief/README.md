# Prospect Research — Champion Brief

**Slug**: `prospect-research-champion-brief` · **Version**: `1.0` · **Use case**: `research` · **Motion**: `slg`

Person-level deep dossier generator. Career history + recent LinkedIn activity + public POVs + role scope + mutual connections + recent job change + personalized entry line + warm intro path. Output: champion brief markdown ready to hand to `/clay-outbound` or AE 1:1 prep.

## When to use this
- AE 1:1 prep before a Tier 1 discovery call
- Champion identification within a known target account
- Warm intro mapping — finding the best human-network path to a target prospect
- Personalization input for `/clay-outbound` when boilerplate first-lines are dying
- Exec dinner / event speaker prep

## What it produces
- 95%+ contact enrichment
- 70%+ usable personalized entry line (specific to their stated POVs or recent post)
- 10-point champion score (seniority + tenure + POV depth + budget authority + job change recency)
- Markdown brief ready for Notion / Obsidian / Doc handoff
- Hands `personalized_entry_line` directly to `/clay-outbound` for high-scoring prospects

## Required inputs (placeholders to fill)
| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{TARGET_SENIORITY}}` | Seniority levels worth researching | `["VP", "C-level", "Director"]` |
| `{{INCLUDE_MUTUAL_CONNECTIONS}}` | Whether to run mutuals lookup (only useful with sender graph available) | `true` or `false` |
| `{{SENDER_LINKEDIN_URLS}}` | LinkedIn URLs of the human senders (for mutuals) | `["https://linkedin.com/in/brandon", "https://linkedin.com/in/aj"]` |
| `{{JOB_CHANGE_PROVIDER}}` | `champify` / `usergems` / blank (Claygent fallback) | `champify` |
| `{{MARKDOWN_EXPORT_PATH}}` | Where the brief markdown files land | `/path/to/obsidian/vault/prospects/` |

## Required integrations
- Clay native: find-and-enrich-contact
- Claygent (use-ai, Sonnet for STANDARD): the bulk of the columns
- Champify / UserGems (optional): job-change signal
- Sender LinkedIn graph access (optional): mutual connections

## Cost
- Estimated credits/prospect: 45–75 at STANDARD depth
- 100 prospects: ~6,000 credits ≈ $60
- ⚠️ **Claygent-heavy.** Run `/clay-claygent-iterator` on `personalized_entry_line` before scaling past 25 rows.

## Known good for
- Pattern derived from `/clay-prospect-research` SKILL spec

## Notes / Gotchas
- **The Read-Out-Loud test for `personalized_entry_line` is non-negotiable.** On the 25-row sample, read each first line aloud. If 5+ sound vendor-y or generic, re-tune the prompt before scaling.
- The `champion_score` formula favors mid-tenure (12–36 months) — too-new lacks influence, too-old has likely set their stack. Adjust if your motion targets new-hire champions specifically.
- `recent_job_change` signal can double-up with Champify; if you already have a separate `signal-monitor-job-change` workbook running, suppress this column to avoid double credit.
- For exec dinner targeting, add a `recent_speaking_engagements` Claygent column (5 credits) — flags speakers as high-priority dinner invites.
- Warm intro path defaults to COLD unless mutuals lookup is enabled — don't read absence as "we have no connection."

## Changelog
- v1.0 — 2026-06-10 — initial bootstrap from `/clay-prospect-research` SKILL spec
