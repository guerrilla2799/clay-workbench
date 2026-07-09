---
name: clay-account-research
description: Generate deep multi-source account research briefs in Clay via orchestrated Claygent columns. Builds an account-keyed workbook that returns a structured executive brief per company — strategic priorities, recent news, hiring posture, tech stack, leadership, financial signals, competitive context, and entry-point hypothesis — ready to drop into a sales play, ABM tier review, or board prep. Triggers — "account research", "account brief", "company deep dive", "account profile", "research these accounts", "build a one-pager on", "ABM research", "executive prep on accounts", "/clay-account-research".
---

# clay-account-research — Deep Account Briefs

The research skill for **account-level** intelligence. Use this when the user needs a structured executive brief per company (Tier 1 ABM, board prep, exec dinner targeting, customer expansion research), not just firmographics.

Inherits `clay-workbench/SKILL.md` master workflow. Specializes step 3 (composition — Claygent orchestration) and step 5 (execution — sample → expand pattern).

**Difference from `/clay-abm-list`**: that skill builds a list and qualifies it. This skill goes deep on a small list (5–250 accounts) with multi-source narrative research per account.

---

## Inputs Expected

From intake:
- **Account list source**: CSV / domain list / HubSpot view / Salesforce report / Tier 1 list from `/clay-abm-list`
- **Brief use case**: ABM exec play / board deck / customer expansion / partnership targeting / event invite list / competitive watch
- **Depth**: LIGHT (5 fields) / STANDARD (10 fields) / DEEP (15 fields, multi-source per field)
- **Output format**: in-Clay columns / exported markdown briefs / Notion DB / Google Doc per account
- **Entry-point hypothesis required?** Yes/no — generates a "best way in" recommendation per account
- **Source diversity**: which signal sources are required (news, hiring, funding, tech, social, leadership changes, product launches)

---

## Step 3 — Composition (Specialized)

### Canonical Column Order (Left → Right)

| # | Column | Type | Source / Provider | Cost | Depends On |
|---|--------|------|-------------------|------|------------|
| 1 | `company_domain` | text | source | 0 | — |
| 2 | `company_name` | text | find-company | 1 | `company_domain` |
| 3 | `industry` | text | find-company | 1 | `company_domain` |
| 4 | `employee_count` | number | find-company | 1 | `company_domain` |
| 5 | `hq_country` | text | find-company | 1 | `company_domain` |
| 6 | **`pass_1_qualified`** | formula | clayscript | 0 | 3–5 |
| 7 | `linkedin_company_url` | text | find-company | 1 | `company_domain` |
| 8 | `strategic_priorities` | claygent (use-ai) | Claygent multi-source | 5–10 | 1, 2, 7 |
| 9 | `recent_news_90d` | claygent | Claygent news scan | 5–10 | 1, 2 |
| 10 | `funding_history` | enrichment | Predictleads / Crunchbase | 2–3 | 1 |
| 11 | `hiring_posture` | claygent | Claygent LinkedIn jobs scan | 5–10 | 1, 7 |
| 12 | `leadership_team` | claygent | Claygent leadership scan | 5–10 | 7 |
| 13 | `recent_leadership_changes` | claygent | Champify / UserGems / Claygent | 2–10 | 7 |
| 14 | `tech_stack_relevant` | enrichment | Wappalyzer / BuiltWith | 1–5 | 1 |
| 15 | `competitive_context` | claygent | Claygent competitor map | 5–10 | 1, 2 |
| 16 | `customer_proof_points` | claygent | Claygent case study scan | 5–10 | 1, 2 |
| 17 | `product_launches_12mo` | claygent | Claygent product news scan | 5–10 | 1 |
| 18 | `risk_signals` | claygent | Claygent (layoffs, restructuring, exec departures) | 5–10 | 1, 2 |
| 19 | **`entry_point_hypothesis`** | claygent | Claygent synthesis | 5–10 | 8, 9, 11, 12, 15, 18 |
| 20 | `brief_summary_markdown` | formula | clayscript template concat | 0 | all above |
| 21 | `route_to` | formula | clayscript | 0 | `pass_1_qualified`, depth signals |

### `pass_1_qualified` Formula (Cheapest Pre-Gate)

```clayscript
IF(
  AND(
    company_name != NULL,
    industry != NULL,
    employee_count >= {MIN_EMPLOYEES}
  ),
  TRUE,
  FALSE
)
```

Every Claygent column gets Run Condition: `pass_1_qualified == TRUE`. Otherwise a bad input row burns 50–80 credits.

### `entry_point_hypothesis` Claygent Prompt Template

```
ROLE: Senior B2B GTM strategist preparing a one-pager for an executive ABM play.

CONTEXT:
- Account: {company_name} ({industry}, {employee_count} employees, HQ {hq_country})
- Strategic priorities: {strategic_priorities}
- Recent news: {recent_news_90d}
- Hiring posture: {hiring_posture}
- Leadership team: {leadership_team}
- Recent leadership changes: {recent_leadership_changes}
- Competitive context: {competitive_context}
- Risk signals: {risk_signals}

TASK:
Generate the single best entry-point hypothesis for this account.
Include:
1. The most likely champion role (1 person/title)
2. The pain or strategic priority that opens the door
3. The piece of proof or insight that makes the first message earn a reply
4. The angle to avoid (already saturated / wrong moment)

FORMAT: 4 bullets, no preamble. <120 words total.

FALLBACK: If fewer than 3 of the input fields contain useful data, return "INSUFFICIENT_SIGNAL — recommend manual research" and stop.
```

Cap `max_sources = 5`. Set `model = sonnet` for cost, escalate to opus only for Tier 1.

### `brief_summary_markdown` Formula Template

```clayscript
CONCAT(
  "# ", company_name, " — Account Brief\n\n",
  "**Industry**: ", industry, " · **Size**: ", employee_count, " · **HQ**: ", hq_country, "\n\n",
  "## Strategic Priorities\n", strategic_priorities, "\n\n",
  "## Recent News (90d)\n", recent_news_90d, "\n\n",
  "## Hiring Posture\n", hiring_posture, "\n\n",
  "## Leadership\n", leadership_team, "\n\n",
  "## Recent Leadership Changes\n", recent_leadership_changes, "\n\n",
  "## Competitive Context\n", competitive_context, "\n\n",
  "## Risk Signals\n", risk_signals, "\n\n",
  "## Entry-Point Hypothesis\n", entry_point_hypothesis, "\n\n",
  "_Generated ", TODAY(), " · sources: Clay + Claygent_"
)
```

---

## Step 5 — Execution (Specialized)

### Preferred Path: Tier 1 (official Agent Plugin) — see resources/execution-surface.md

```
1. clay credits — balance pre-flight
2. clay routines list
   → If an "Account Research Brief" routine exists, prefer it
3. If routine exists:
   clay routines get → map account list + brief depth + use case
   → clay routines runs on 5-row sample
4. If no routine, ad-hoc:
   For 5 rows:
     mcp__claude_ai_Clay__find-and-enrich-company (Tier 2 — connector; firmographics)
   → Confirm pass_1_qualified resolves via clay tables rows/query or the `table` MCP tool
   → Confirm Claygent prompt quality with /clay-claygent-iterator if any column underperforms
   → Expand to 25 rows
   → Full run on confirmation
```

### Manual Fallback (Tier 3)

Table creation and column-formula edits are still UI-only (see resources/execution-surface.md):

1. New Table → `"Account Research — {list descriptor} — {date}"`
2. Source → CSV / HubSpot view / output of `/clay-abm-list`
3. Add columns 1–7 (firmographics + pass_1_qualified) — no Run Condition needed
4. Add columns 8–18 (Claygent + enrichments) — each gets Run Condition `pass_1_qualified == TRUE`
5. Add column 19 (`entry_point_hypothesis`) — Run Condition: ALL of 8, 9, 11, 12, 15, 18 != NULL
6. Add column 20 (`brief_summary_markdown`) — formula concat
7. `auto_run = false` during build
8. Run 5 → inspect every Claygent output by hand → tune prompts via `/clay-claygent-iterator`
9. Run 25 → check coverage % per Claygent column (target ≥85%)
10. Full run only after coverage threshold hit

---

## Output Modes

| Mode | What Happens |
|------|--------------|
| In-Clay only | Stop after `brief_summary_markdown` — user reads in Clay |
| Markdown export | Webhook → save each `brief_summary_markdown` as `briefs/{company_domain}.md` |
| Notion DB | HTTP action → create one Notion page per account in target DB |
| Google Doc | HTTP action → one Doc per Tier 1 account, shared with named exec |

Default: in-Clay + Markdown export to Obsidian vault path supplied at intake.

---

## Credit Pre-Flight (Mandatory)

Claygent-heavy. Costs add up fast.

```
Per row (STANDARD depth, sonnet):
  - Firmographics:           ~5 credits
  - 6 Claygent columns:      ~30–50 credits
  - Enrichments (funding, tech): ~5 credits
  - entry_point_hypothesis:  ~10 credits
  Total: ~50–70 credits per qualified row

100-row run: 5,000–7,000 credits (~$50–70 at standard tier)
250-row run: 12,500–17,500 credits (~$125–175)
```

Always run on 5 → 25 → full. Never go straight to full on this skill.

---

## Verify-and-Handoff Checklist

- [ ] 5-row sample: firmographics resolve (>95%)
- [ ] 5-row sample: every Claygent column returns non-blank, on-topic output (manually read all 5)
- [ ] 5-row sample: `entry_point_hypothesis` would actually inform a real outreach decision (human gut check)
- [ ] 25-row sample: each Claygent column coverage ≥85%
- [ ] 25-row sample: at least 3 INSUFFICIENT_SIGNAL outputs — proves the fallback is firing (not silently fabricating)
- [ ] Briefs exported to chosen output destination
- [ ] Cost per qualified brief documented (total credits / brief count)
- [ ] Sample-quality review with end consumer (AE, exec, founder) before full run

---

## Use-Case Variants

| Use Case | Adjustments |
|----------|------------|
| Board deck — top 10 portfolio companies | DEEP depth, opus model for entry_point_hypothesis, Google Doc export |
| Tier 1 ABM kickoff | STANDARD depth, Markdown export, hand to AE 1:1 |
| Exec dinner targeting | LIGHT depth + add `recent_speaking_engagements` Claygent column |
| Customer expansion play | Source = existing customers' parent companies / business units |
| Competitive watch | Source = competitor customer list; brief focuses on switching signals |
| Investor / partner research | DEEP, add `funding_thesis` and `portfolio_overlap` Claygent columns |

---

## Anti-Patterns

❌ Running deep Claygent research on unqualified accounts — burns 50+ credits per row for nothing.
❌ Single-prompt Claygent doing everything in one column — degrades quality and obscures cost.
❌ Skipping the 5-row manual quality check — you find out about hallucinations at row 200.
❌ Using opus for every Claygent column — sonnet is fine for 80% of fields.
❌ Letting Claygent silently fabricate — every prompt must include the INSUFFICIENT_SIGNAL fallback.

---

## Related

- For building the list before researching → `/clay-abm-list`.
- For per-Claygent-column prompt iteration → `/clay-claygent-iterator` (mandatory before scaling past 25 rows).
- For person-level briefs at qualified accounts → `/clay-prospect-research`.
- For ongoing trigger monitoring on these accounts → `/clay-signal-monitor`.
- For exporting briefs to outbound → `/clay-outbound`.
