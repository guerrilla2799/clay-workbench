---
name: clay-prospect-research
description: Generate deep person-level research briefs in Clay via orchestrated Claygent columns. Builds a contact-keyed workbook that returns a structured prospect dossier — recent activity, public content + POVs, career history, role context, mutual connections, hiring/team responsibility, and a personalized entry-line hypothesis — ready for executive outreach, AE 1:1 prep, exec dinner targeting, or warm intro mapping. Triggers — "prospect research", "person research", "contact dossier", "research these contacts", "deep dive on a person", "exec prep", "speaker research", "warm intro mapping", "/clay-prospect-research".
---

# clay-prospect-research — Deep Person Briefs

The research skill for **person-level** intelligence. Use when the user needs a structured dossier per individual contact (exec outreach, AE 1:1 prep, podcast/speaker prep, exec dinner invite list, warm-intro mapping), not just contact info.

Inherits `clay-workbench/SKILL.md` master workflow. Specializes step 3 (composition — Claygent orchestration around a person) and step 5 (execution — relevance gate + 5/25/full pattern).

**Difference from `/clay-enrich-waterfall`**: that skill finds emails/phones. This skill goes deep on a small list of named people with multi-source narrative research per person.

**Difference from `/clay-account-research`**: account-research is company-keyed; prospect-research is person-keyed and surfaces individual-level entry hooks.

---

## Inputs Expected

From intake:
- **Prospect list source**: CSV / LinkedIn URL list / HubSpot view / Tier 1 account list from `/clay-account-research` (with named champions)
- **Brief use case**: exec ABM outreach / AE 1:1 prep / podcast or speaker research / event invite list / warm-intro mapping / partner identification
- **Depth**: LIGHT (5 fields) / STANDARD (10 fields) / DEEP (15 fields with multi-source per field)
- **Output format**: in-Clay columns / Markdown export per person / Notion DB row per person / Google Doc per VIP
- **Personalized entry-line required?** Yes/no — generates first line/hook draft (handoff-ready for `/clay-outbound`)
- **Warm-path mapping?** Yes/no — Claygent searches mutual connections via sender's LinkedIn graph

---

## Step 3 — Composition (Specialized)

### Canonical Column Order (Left → Right)

| # | Column | Type | Source / Provider | Cost | Depends On |
|---|--------|------|-------------------|------|------------|
| 1 | `linkedin_url` OR `email` | text | source | 0 | — |
| 2 | `full_name` | text | find-and-enrich-contact | 1 | 1 |
| 3 | `title` | text | find-and-enrich-contact | 1 | 1 |
| 4 | `company_name` | text | find-and-enrich-contact | 1 | 1 |
| 5 | `company_domain` | text | find-and-enrich-contact | 1 | 1 |
| 6 | `seniority` | formula | clayscript (parse title) | 0 | 3 |
| 7 | **`pass_1_relevant`** | formula | clayscript | 0 | 3, 4, 6 |
| 8 | `linkedin_about` | claygent | Claygent LinkedIn profile scrape | 5 | 1 |
| 9 | `tenure_months_in_role` | claygent | Claygent LinkedIn parse | 5 | 1 |
| 10 | `career_history_summary` | claygent | Claygent LinkedIn parse | 5–10 | 1 |
| 11 | `recent_linkedin_posts_90d` | claygent | Claygent LinkedIn activity scan | 5–10 | 1 |
| 12 | `recent_public_content` | claygent | Claygent web search (blogs, podcasts, talks) | 5–10 | 2, 4 |
| 13 | `stated_priorities_or_povs` | claygent | Claygent synthesis | 5–10 | 11, 12 |
| 14 | `role_scope` | claygent | Claygent (team size, budget signals) | 5–10 | 2, 3, 4 |
| 15 | `mutual_connections` | claygent OR LinkedIn API | sender-graph lookup | 2–5 | 1 |
| 16 | `recent_job_change` | enrichment | Champify / UserGems / Claygent | 2–5 | 1 |
| 17 | `notable_quotes_or_takes` | claygent | Claygent pull from content | 5–10 | 11, 12 |
| 18 | `champion_score` | formula | clayscript (10-point) | 0 | 6, 9, 13, 14 |
| 19 | **`personalized_entry_line`** | claygent | Claygent synthesis | 5–10 | 2, 3, 11, 13, 17 |
| 20 | `warm_intro_path` | formula | clayscript | 0 | 15 |
| 21 | `prospect_brief_markdown` | formula | clayscript template concat | 0 | all above |
| 22 | `route_to` | formula | clayscript | 0 | `champion_score`, `pass_1_relevant` |

### `pass_1_relevant` Formula (Cheapest Pre-Gate)

```clayscript
IF(
  AND(
    title != NULL,
    company_name != NULL,
    OR(
      seniority IN [{ICP_SENIORITIES}],
      LOWERCASE(title) CONTAINS_ANY [{ICP_TITLE_KEYWORDS}]
    )
  ),
  TRUE,
  FALSE
)
```

Every Claygent column gets Run Condition: `pass_1_relevant == TRUE`. Saves 30–50 credits per disqualified row.

### `champion_score` Formula (10-Point)

```clayscript
SUM(
  IF(seniority IN ["VP", "C-Level", "Founder"], 2, IF(seniority IN ["Director", "Head"], 1, 0)),
  IF(tenure_months_in_role >= 6 AND tenure_months_in_role <= 36, 2, IF(tenure_months_in_role > 36, 1, 0)),
  IF(stated_priorities_or_povs CONTAINS_ANY [{ICP_PRIORITY_KEYWORDS}], 2, 0),
  IF(role_scope CONTAINS_ANY [{ICP_OWNERSHIP_KEYWORDS}], 2, 0),
  IF(recent_job_change == TRUE, 2, 0)
)
```

8–10 = primary champion · 5–7 = warm path / influencer · <5 = monitor only.

### `personalized_entry_line` Claygent Prompt Template

```
ROLE: Senior B2B GTM strategist drafting the first line of a cold message that earns a reply.

CONTEXT:
- Prospect: {full_name}, {title} at {company_name}
- LinkedIn About: {linkedin_about}
- Recent LinkedIn posts (90d): {recent_linkedin_posts_90d}
- Public content + POVs: {recent_public_content}
- Stated priorities: {stated_priorities_or_povs}
- Notable quotes: {notable_quotes_or_takes}

TASK:
Write ONE personalized opening line that:
1. References a specific, recent (90d) thing they said or did publicly
2. Is plausibly true if they read it (no flattery, no fabrication)
3. Avoids the dead phrases: "I came across", "I saw your post on", "loved your insight on", "your work in X is impressive"
4. Earns the right to the second sentence in <25 words

FORMAT: Single line, no preamble, no closing. <25 words.

FALLBACK: If there is no specific public artifact in the inputs from the last 90d, return "NO_HOOK — fall back to account-level angle" and stop.
```

Cap `max_sources = 3` for the entry-line column (already synthesizing from prior columns). Set `model = opus` here — first lines are high-leverage.

### `prospect_brief_markdown` Formula Template

```clayscript
CONCAT(
  "# ", full_name, " — Prospect Brief\n\n",
  "**Title**: ", title, " · **Company**: ", company_name, " · **Tenure**: ", tenure_months_in_role, " months\n",
  "**Champion Score**: ", champion_score, "/10\n\n",
  "## Stated Priorities / POVs\n", stated_priorities_or_povs, "\n\n",
  "## Recent LinkedIn (90d)\n", recent_linkedin_posts_90d, "\n\n",
  "## Recent Public Content\n", recent_public_content, "\n\n",
  "## Role Scope\n", role_scope, "\n\n",
  "## Career History\n", career_history_summary, "\n\n",
  "## Mutual Connections / Warm Path\n", mutual_connections, "\n\n",
  "## Notable Quotes\n", notable_quotes_or_takes, "\n\n",
  "## Personalized Entry Line\n> ", personalized_entry_line, "\n\n",
  "_Generated ", TODAY(), " · sources: Clay + Claygent_"
)
```

---

## Step 5 — Execution (Specialized)

### Preferred Path: MCP

```
1. mcp__claude_ai_Clay__get-credits-available
2. mcp__claude_ai_Clay__list_subroutines
   → If "Prospect Research Brief" subroutine exists, prefer it
3. If subroutine exists:
   mcp__claude_ai_Clay__get_subroutine_input_options
   → Map prospect list + depth + use case
   → mcp__claude_ai_Clay__run_subroutine on 5-row sample
4. If no subroutine, ad-hoc:
   For 5 rows:
     mcp__claude_ai_Clay__find-and-enrich-list-of-contacts
   → Confirm pass_1_relevant resolves
   → Iterate every Claygent prompt via /clay-claygent-iterator before scaling
   → Expand to 25, then full
```

### Manual Fallback

1. New Table → `"Prospect Research — {list descriptor} — {date}"`
2. Source → CSV / LinkedIn URLs / HubSpot view
3. Add columns 1–7 (firmographics + seniority + pass_1_relevant) — no Run Condition needed
4. Add columns 8–17 (Claygent + enrichments) — each gets Run Condition `pass_1_relevant == TRUE`
5. Add column 18 (`champion_score`) — formula
6. Add column 19 (`personalized_entry_line`) — Run Condition: at least 2 of (11, 12, 17) != NULL, else NO_HOOK
7. Add columns 20–22 — formulas
8. `auto_run = false` during build
9. Run 5 → manually validate every personalized_entry_line by hand (the highest-stakes output)
10. Run 25 → check NO_HOOK rate (target ≤30% — higher means input list is too cold)
11. Full run only after quality check

---

## Output Modes

| Mode | What Happens |
|------|--------------|
| In-Clay only | Stop after `prospect_brief_markdown` |
| Markdown export | Webhook → one file per person → Obsidian vault |
| Notion DB | HTTP action → one Notion page per prospect |
| Google Doc per VIP | Only for `champion_score >= 8` — Doc shared with exec sender |
| Handoff to `/clay-outbound` | `personalized_entry_line` becomes first-line input to outbound sequence |

---

## Credit Pre-Flight (Mandatory)

```
Per row (STANDARD depth, mixed sonnet + opus on entry line):
  - Contact enrichment:          ~3 credits
  - 7 Claygent columns:          ~35–60 credits
  - personalized_entry_line:     ~10 credits (opus)
  Total: ~50–75 credits per qualified row

100-row run: 5,000–7,500 credits (~$50–75)
250-row run: 12,500–18,750 credits (~$125–187)
```

Brandon's frequent pattern: 25 named champions from `/clay-account-research` → run deep on those only. Keeps cost <$30 with the highest-leverage output.

---

## Verify-and-Handoff Checklist

- [ ] 5-row sample: contact enrichment resolves (>95%)
- [ ] 5-row sample: every Claygent column returns on-topic, specific output (manually read all 5)
- [ ] 5-row sample: every `personalized_entry_line` would actually open a real conversation (gut check by sender)
- [ ] 25-row sample: each Claygent column coverage ≥80%
- [ ] 25-row sample: NO_HOOK rate ≤30%
- [ ] 25-row sample: at least 3 NO_HOOK outputs (proves fallback fires — no fabrication)
- [ ] Briefs exported to chosen destination
- [ ] Cost per Champion-Score-≥8 prospect documented
- [ ] Sender sign-off on tone before push to `/clay-outbound`

---

## Use-Case Variants

| Use Case | Adjustments |
|----------|------------|
| Exec ABM outreach (1:few) | DEEP depth, opus on entry_line, Google Doc per prospect |
| AE 1:1 weekly prep | STANDARD depth, in-Clay only, queued every Sunday |
| Podcast / speaker prep | Add `recent_speaking_engagements` + `controversial_takes` Claygent columns |
| Exec dinner invite list | LIGHT depth + add `dietary_or_logistics` field for hosts |
| Warm-intro mapping | Heavy emphasis on `mutual_connections`; output sorted by graph distance |
| Job-change follow-up (Champify) | Source = recent job changes; gate to new-role tenure 0–6 months |
| Customer expansion (CSM 1:1) | Source = existing customer contacts; emphasize `role_scope` + product adoption signals |

---

## Anti-Patterns

❌ Running deep prospect research on cold-input lists (>500 names) without gating — burns 25k+ credits.
❌ Sonnet on `personalized_entry_line` — quality drop is visible; opus is worth it on the line that lands the meeting.
❌ Skipping the 5-row manual quality check — first line is the highest-blast-radius output in the plugin.
❌ Letting Claygent fabricate a "recent post" — every prompt must include NO_HOOK fallback explicitly.
❌ Running this on a prospect list without first running `/clay-account-research` on their employer — context cascade breaks.
❌ Using LinkedIn scraping at scale without rotating — accounts get throttled.

---

## Related

- For the account-level brief that surrounds these prospects → `/clay-account-research` (run first).
- For per-column prompt iteration before scaling → `/clay-claygent-iterator` (mandatory before 100+ rows).
- For finding email/phone for these prospects → `/clay-enrich-waterfall`.
- For taking the `personalized_entry_line` into a sequence → `/clay-outbound`.
- For ongoing monitoring of these prospects' moves → `/clay-signal-monitor`.
