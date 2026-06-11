# Account Research — Tier 1 Executive Brief

**Slug**: `account-research-tier-1-brief` · **Version**: `1.0` · **Use case**: `research` · **Motion**: `slg`

Multi-source Claygent account brief generator. Per-account synthesis: strategic priorities → recent news → funding → hiring posture → leadership → competitive → product launches → risk signals → **entry-point hypothesis**. Output: in-Clay summary + optional Markdown export per account (for Obsidian / Notion / Doc handoff to AE 1:1).

## When to use this
- Tier 1 ABM kickoff — generate executive briefs for the top 25–100 accounts before AE outreach
- Board deck — top 10 portfolio accounts, DEEP depth + Opus model
- Exec dinner targeting — LIGHT depth + add a speaker-engagement Claygent column
- Pre-call prep for AE 1:1s — markdown export → paste into call notes

## What it produces
- 95%+ firmographic resolution
- 80%+ surface usable strategic priorities (with evidence URLs)
- Per-account markdown brief ready to hand to AE
- Entry-point hypothesis (who to target, why them, opening angle, timing rationale, confidence)

## Required inputs (placeholders to fill)
| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{ICP_INDUSTRIES}}` / `{{ICP_GEO}}` / `{{ICP_SIZE_MIN}}` / `{{ICP_SIZE_MAX}}` | ICP gating | per upstream workbook |
| `{{TARGET_FUNCTIONS}}` | Leadership functions to map | `["Sales", "Marketing", "RevOps"]` |
| `{{LEADERSHIP_CHANGE_PROVIDER}}` | `champify` / `usergems` / leave Claygent | `champify` |
| `{{RELEVANT_TECH_CATEGORIES}}` | Wappalyzer/BuiltWith filter | `["CRM", "Marketing Automation", "Data Warehouse"]` |
| `{{COMPETITIVE_SPACE}}` | The market category for competitive scan | `B2B sales tooling` |
| `{{TOOL_CATEGORY}}` | Our product category for vendor-displacement angle | `sales engagement platform` |
| `{{OUR_PRODUCT_CATEGORY}}` | What we sell, for entry-point synthesis | `AI-native sales engagement` |
| `{{MARKDOWN_EXPORT_PATH}}` | Webhook target for markdown brief export | `/path/to/obsidian/vault/briefs/` |
| `{{NOTION_DB_ID}}` (optional) | Notion DB ID for high-confidence accounts | `xyz123` |

## Required integrations
- Clay native: find-company
- Predictleads or Crunchbase: funding history
- Wappalyzer or BuiltWith: tech stack (optional)
- Claygent (use-ai): the heavy lifter — Sonnet for STANDARD, Opus for DEEP
- Champify / UserGems (optional): leadership change signal

## Cost
- Estimated credits/account: 40–70 at STANDARD depth (Sonnet, 3 sources/Claygent)
- DEEP depth (Opus, 5 sources): 80–120 credits/account
- 100 Tier 1 accounts at STANDARD: ~5,500 credits ≈ $55
- ⚠️ **Claygent-heavy** — run `/clay-claygent-iterator` on `entry_point_hypothesis` and `strategic_priorities` prompts BEFORE scaling past 25 accounts.

## Known good for
- Pattern derived from `/clay-account-research` SKILL spec

## Notes / Gotchas
- **Anti-pattern**: running DEEP depth on all 100 accounts before validating prompts on 5–10. Always iterate first.
- The `entry_point_hypothesis` column depends on 6+ upstream Claygent columns; if any of those are weak, the synthesis is weak. Spot-check upstream first.
- For board decks, use Opus model on `entry_point_hypothesis` only — keeps cost manageable while raising synthesis quality where it matters.
- Markdown export filename template uses `{company_domain}` — if you have multi-region same-domain accounts, switch to `{company_name}` or add a suffix.
- Pair with `/clay-prospect-research` once you have a who_to_target from `entry_point_hypothesis` — that hands the personalized line to outbound.

## Changelog
- v1.0 — 2026-06-10 — initial bootstrap from `/clay-account-research` SKILL spec
