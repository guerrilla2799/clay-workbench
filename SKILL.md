---
name: clay-workbench
description: Build, debug, and run Clay.com workbooks end-to-end via Claude Code. Hybrid router skill — auto-detects intent (ABM list build, enrichment waterfall, ICP scoring, outbound generation, inbound routing, troubleshooting) and routes to the right sub-skill. MCP-first execution (mcp__claude_ai_Clay__*) with manual UI walkthrough fallback. Mandatory credit pre-flight, ICP-gates-before-credits enforcement, client-voice detection. Triggers — "build a Clay workbook", "Clay table", "enrich list", "Clay waterfall", "Clay ICP score", "Clay outbound", "Clay inbound enricher", "Clay router", "Clay troubleshoot", "Clay credit burn", "claygent prompt", "Clay subroutine", "/clay".
---

# Clay Workbench

The router skill for Clay.com workbook construction inside Claude Code. Delegates to 6 sub-skills based on detected intent.

**Architecture**: Hybrid router + sub-skill pack.
**Execution**: Clay MCP first, manual UI walkthrough fallback.
**Voice**: Client-agnostic core, with client-context detection routing to messaging skills.

---

## 🚨 Global Rules (Non-Negotiable)

Before any sub-skill runs, these 8 rules apply. Full text: `resources/global-rules.md`.

1. **Gates Before Credits** — ICP gate column required before any paid column.
2. **Sending Gate Before Export** — formula column required before any sequencer push.
3. **Data Unification** — score on full rows, not fragments.
4. **ICP Qualification First** — cheapest-signal disqualification before enrichment.
5. **Free Before Paid** — try free sources first in every waterfall.
6. **Never Assume — Always Ask** — run the 8-question intake; offer options when user defers.
7. **Clay-Managed vs Own API Key** — state which side each column hits.
8. **Multiple Sending Steps** — outbound assumes 2–4 step cadence, not one-shot.

Violation requires explicit `gate-override: <reason>` declaration.

---

## ⚠️ Negative Trigger Boundary

**DO NOT trigger this skill** when the user wants to:

- Run an existing Clay subroutine that's already built → use `mcp__claude_ai_Clay__run_subroutine` directly.
- Ask a single question about Clay data → use `mcp__claude_ai_Clay__ask-question-about-accounts`.
- Generic CRM / sequencer questions unrelated to Clay → don't load.

**DO trigger** when the user wants to:

- Build, design, or compose a new Clay workbook
- Add columns or enrichments to an existing workbook
- Score or qualify leads in Clay
- Build outbound or inbound routing in Clay
- Debug a broken or expensive Clay workbook
- Estimate or audit Clay credit burn

---

## 🎯 Routing Table

| User Intent | Sub-Skill | Trigger Phrases | What It Builds |
|-------------|-----------|-----------------|----------------|
| Build a list of target accounts | `clay-abm-list` | "ABM list", "target accounts", "Tier 1 accounts", "build account list", "expansion list" | Account-keyed workbook with firmographics + triggers + ICP gate |
| Find contacts + emails + phones | `clay-enrich-waterfall` | "enrich contacts", "find emails", "email waterfall", "contact enrichment", "phone enrichment" | Multi-provider waterfall with graceful exit + verification |
| Score and rank leads | `clay-icp-score` | "ICP score", "lead score", "fit score", "qualify leads", "10-point grade" | Composite fit+intent score column with routing logic |
| Generate outbound copy + push to sequencer | `clay-outbound` | "outbound message", "first line", "personalized email", "Sending Gate", "push to SalesLoft / Outreach / 11x" | AI copy columns + Sending Gate + sequencer push action |
| Route inbound demos / signups | `clay-inbound-routing` | "inbound router", "demo form router", "enrich form fills", "MQL routing", "round-robin" | Webhook source + enrichment + ICP gate + Slack/CRM routing |
| Diagnose a broken or expensive workbook | `clay-troubleshoot` | "Clay is expensive", "match rate is low", "Clay error", "credits burning", "wrong rows enriched" | Root-cause diagnostic + fix recipe + cost-savings estimate |

### Ambiguity Resolution

If the user's prompt matches multiple sub-skills, ask **one** clarifying question with 2–3 options, then route. Do not load every sub-skill in parallel — that bloats context.

---

## 📋 Master Workflow

Every sub-skill follows this 6-step workflow. The sub-skill SKILL.md specializes step 3 and step 5.

```
Step 1 — Intake (8 Questions)
        See: resources/intake-questions.md
        Output: structured spec of source, fields, enrichments, gates, AI columns, outputs, auto-run, sample size

Step 2 — ICP Gate Design
        See: resources/global-rules.md (Rule #1, #4)
        Output: gate_qualified formula column spec — cheapest possible signal

Step 3 — Workbook Composition  ← specialized per sub-skill
        Output: column-by-column spec markdown table

Step 4 — Credit Pre-Flight
        See: resources/credit-cost-table.md, resources/mcp-tool-map.md
        Output:
          - get-credits-available (current balance)
          - estimated credits per row × row count
          - cost in dollars at user's tier
          - confirm/cancel prompt

Step 5 — Execute or Walkthrough  ← specialized per sub-skill
        Path A — MCP execution (preferred):
          - list_subroutines if existing subroutine matches
          - run_subroutine with mapped inputs
          - find-and-enrich-* primitives for ad-hoc
        Path B — Manual walkthrough (fallback when MCP gap):
          - Step-by-step UI instructions
          - Column-by-column formula text
          - Configuration screenshots noted (where in UI)

Step 6 — Verify + Handoff
        Output:
          - Sample-row run (5 rows first, then 25, then full)
          - Match-rate report per waterfall step
          - Sending Gate eligibility count
          - Suggested next action (full run, fix gap, push to destination)
```

---

## 🎤 Client Voice Detection

When the prompt mentions a known client (Obin, Vantage, Dodge, etc.), load the matching messaging skill BEFORE generating any outbound copy or persona definition.

Detection rules: `resources/client-context-detection.md`.

Without client context, fall back to universal frameworks (no fabrication).

---

## 💸 Credit Pre-Flight (Mandatory)

Before any operation that touches more than **100 rows** OR uses any **paid waterfall**:

```
1. Call mcp__claude_ai_Clay__get-credits-available
2. Compute estimate from credit-cost-table.md:
   credits_per_row × row_count = total
3. Block if: total > balance × 0.5
4. Present:
   "This run will process {N} rows.
    Estimated cost: {X} credits (~${Y} at tier).
    Current balance: {Z} credits.
    Continue? [Y/n]"
5. Run only on explicit user confirmation.
```

No exceptions. This is enforcement of Global Rule #1.

---

## 📂 Resource Index

| File | Purpose |
|------|---------|
| `resources/global-rules.md` | The 8 non-negotiables — load every time |
| `resources/intake-questions.md` | 8-question intake script |
| `resources/mcp-tool-map.md` | When to use which `mcp__claude_ai_Clay__*` tool |
| `resources/action-registry.md` | Clay action keys, packages, gotchas |
| `resources/credit-cost-table.md` | Provider costs for pre-flight estimation |
| `resources/client-context-detection.md` | Routing to client messaging skills |
| `resources/clayscript-library.md` | Reusable formulas (0-credit data manipulation) |
| `resources/ai-prompt-templates.md` | ROLE / CONTEXT / TASK / FORMAT / FALLBACK templates |
| `resources/enrichment-benchmarks.md` | Expected match rates per waterfall step |
| `resources/workflow-patterns.md` | 5 reusable workbook patterns |
| `resources/claygent-guide.md` | AI research agent column construction |

| File | Purpose |
|------|---------|
| `providers/enrichment/*.md` | One file per enrichment provider |
| `providers/databases/*.md` | Account/contact databases |
| `providers/signals/*.md` | Trigger / intent signal sources |
| `providers/crm/*.md` | HubSpot, Salesforce |
| `providers/sequencers/*.md` | SalesLoft, Outreach, Apollo, 11x, Smartlead, Instantly |
| `templates/*.md` | 3 golden reference workbooks |

| Sub-Skill | Slash Command |
|-----------|---------------|
| `skills/clay-abm-list/SKILL.md` | `/clay-abm-list` |
| `skills/clay-enrich-waterfall/SKILL.md` | `/clay-enrich-waterfall` |
| `skills/clay-icp-score/SKILL.md` | `/clay-icp-score` |
| `skills/clay-outbound/SKILL.md` | `/clay-outbound` |
| `skills/clay-inbound-routing/SKILL.md` | `/clay-inbound-routing` |
| `skills/clay-troubleshoot/SKILL.md` | `/clay-troubleshoot` |

---

## 🚀 Quick-Start Prompts

```
/clay                     → auto-routes to best sub-skill based on prompt
/clay-abm-list            → build a Tier 1/2/3 ABM account workbook
/clay-enrich-waterfall    → multi-provider email/phone waterfall
/clay-icp-score           → composite ICP fit score column
/clay-outbound            → personalized copy + Sending Gate + sequencer push
/clay-inbound-routing     → webhook source + enricher + routing
/clay-troubleshoot        → diagnose burn rate, low match, or broken column
```

When user types `/clay` without context, ask: "What are you building today?" and offer the 6 sub-skill options.

---

## 🧭 Standard Output Format

Every sub-skill returns this 4-part deliverable:

1. **Column-by-column spec** — markdown table: `column_name | source/provider | type | cost | depends_on`
2. **Pre-flight estimate** — `N rows × X credits/row = Y credits ≈ $Z`
3. **Execution plan** — either MCP tool calls (preferred) or numbered UI walkthrough (fallback)
4. **Verify-and-handoff checklist** — 5-row sample → 25-row → full, with success thresholds per step

This is the contract. Do not deviate.

---

## ⛔ Things This Skill Will Refuse

- Building any workbook without running the intake first.
- Adding paid columns before an ICP gate exists.
- Pushing to a sequencer without a Sending Gate column.
- Running anything with `auto_run = true` during construction.
- Generating outbound copy without confirming voice/client context.
- Skipping the credit pre-flight on runs > 100 rows.

These refusals are by design. The user can explicitly override per case with `gate-override: <reason>`.
