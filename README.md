# clay-workbench

> The complete Clay.com workbook plugin for Claude Code.

Build, debug, and run Clay workbooks end-to-end via Claude Code — ABM list building, multi-provider enrichment waterfalls, ICP composite scoring, outbound copy with Sending Gate + sequencer push, real-time inbound enrichment + routing, and diagnostic troubleshooting.

**Hybrid router + 6 sub-skills. MCP-first execution with manual UI walkthrough fallback. Mandatory credit pre-flight. ICP-gates-before-credits enforcement.**

---

## What this gives you

| Slash Command | What it builds |
|---------------|----------------|
| `/clay` | Master router — auto-detects intent, routes to the right sub-skill |
| `/clay-abm-list` | Account-keyed ABM workbook with firmographic + trigger gating |
| `/clay-enrich-waterfall` | Multi-provider email + phone + LinkedIn waterfall, graceful exit |
| `/clay-icp-score` | 10-point composite ICP fit + intent score with routing by band |
| `/clay-outbound` | Personalized copy + Sending Gate + sequencer push, client-voice aware |
| `/clay-inbound-routing` | Real-time webhook enrichment + scoring + routing + Slack alerts |
| `/clay-troubleshoot` | Diagnose broken / expensive / under-performing workbooks |

---

## Why it's different

Most Clay skills are either "consultancy markdown" (here are the steps) or "raw scripts" (here is the JSON). This one is both — and more:

- **MCP-first execution.** Calls `mcp__claude_ai_Clay__*` tools directly to actually run workbooks. Falls back to step-by-step UI walkthrough when MCP can't do it yet.
- **Mandatory credit pre-flight.** Estimates `rows × credits/row` against your current balance before ANY paid run > 100 rows. Blocks at 50% balance threshold by default.
- **Two-pass ICP gate as a global rule.** Cheap signals first (industry, size, geo); paid enrichments gated on pass 1. Typically cuts burn 40–60%.
- **Strict Sending Gate.** Sequencer push requires `sending_gate_eligible = TRUE` formula column. Per-step eligibility (step 1, step 2, LinkedIn) supported out of the box.
- **Client voice detection.** When the prompt mentions a known client (Obin, Vantage, etc.), routes to the matching messaging skill for ICP + voice. Generic otherwise.
- **3 golden reference workbooks.** Production-ready templates — copy/paste into Clay.
- **Action registry with gotchas.** The classic `actionKey: "ai"` silent-drop bug? Documented and avoided.

---

## The 8 Global Rules (Non-Negotiable)

Every sub-skill enforces these:

1. **Gates Before Credits** — ICP gate column required before any paid column
2. **Sending Gate Before Export** — formula column required before any sequencer push
3. **Data Unification** — score on full rows, not fragments
4. **ICP Qualification First** — cheapest-signal disqualification before enrichment
5. **Free Before Paid** — try free sources first in every waterfall
6. **Never Assume — Always Ask** — run the 8-question intake; offer options when user defers
7. **Clay-Managed vs Own API Key** — state which side each column hits
8. **Multiple Sending Steps** — outbound assumes 2–4 step cadence, not one-shot

Violation requires explicit `gate-override: <reason>` declaration.

---

## Installation

### Option A — Clone + symlink into Claude Code skills dir

```bash
git clone https://github.com/brandonredlinger/clay-workbench ~/.claude/claudecodeskills/clay-workbench
```

Then register each slash command:

```bash
for skill in clay clay-abm-list clay-enrich-waterfall clay-icp-score clay-outbound clay-inbound-routing clay-troubleshoot; do
  cat > ~/.claude/commands/${skill}.md <<EOF
---
allowed-tools: Read, Write, Edit, WebSearch, WebFetch, AskUserQuestion, Glob, Grep, Bash
description: clay-workbench — ${skill}
---

\$ARGUMENTS

See ~/.claude/claudecodeskills/clay-workbench/${skill == 'clay' ? 'SKILL.md' : "skills/${skill}/SKILL.md"} for full instructions.
EOF
done
```

### Option B — Install as a Claude Code plugin

The `.claude-plugin/plugin.json` manifest is included for plugin-manager-based installs. Drop the folder into your Claude Code plugins directory.

### Required: Clay MCP server

This plugin assumes the **official Clay MCP server** is connected (`mcp__claude_ai_Clay__*` tools). If not:

1. Connect at https://claude.ai/settings/connectors (or your equivalent Claude Code MCP config)
2. Authenticate with your Clay workspace
3. Verify with `mcp__claude_ai_Clay__list_subroutines` — should return your subroutines

Without the MCP server, the plugin falls back to manual UI walkthroughs (which work but lose live execution).

---

## Quick start

```
# Pick your motion. Auto-router will pick the right sub-skill if you're unsure.
/clay

# Or jump to a specific sub-skill:
/clay-abm-list build a Tier 1 ABM list of B2B SaaS companies with 500-2500 employees
              that closed a Series A or B in the last 90 days

/clay-enrich-waterfall add an email + phone waterfall to my contacts table —
                      budget is 10¢/row, EU-heavy list, need 80% match rate

/clay-icp-score build a 10-point fit+intent score for my MQL routing —
                back-test against last 12 months closed-won

/clay-outbound generate 4-step cold outbound copy from my T1 contacts table,
              push to SalesLoft, voice is Obin AI

/clay-inbound-routing wire up real-time enrichment + routing on my HubSpot demo form

/clay-troubleshoot my email waterfall is burning $400/day with 30% match rate —
                   diagnose and fix
```

---

## Plugin structure

```
clay-workbench/
├── SKILL.md                       # Master router
├── .claude-plugin/
│   └── plugin.json                # Formal plugin manifest
├── skills/                        # 6 sub-skills
│   ├── clay-abm-list/SKILL.md
│   ├── clay-enrich-waterfall/SKILL.md
│   ├── clay-icp-score/SKILL.md
│   ├── clay-outbound/SKILL.md
│   ├── clay-inbound-routing/SKILL.md
│   └── clay-troubleshoot/SKILL.md
├── resources/
│   ├── global-rules.md
│   ├── intake-questions.md
│   ├── mcp-tool-map.md
│   ├── action-registry.md
│   ├── credit-cost-table.md
│   ├── client-context-detection.md
│   ├── clayscript-library.md
│   ├── ai-prompt-templates.md
│   ├── enrichment-benchmarks.md
│   ├── claygent-guide.md
│   └── workflow-patterns.md
├── providers/                     # Per-provider notes
│   ├── enrichment/                # Apollo, Findymail, Datagma, Dropcontact, ZeroBounce, Hunter, PDL, Clearbit, ContactOut
│   ├── databases/                 # Sales Nav, Ocean.io
│   ├── signals/                   # Predictleads, job changes, hiring/funding
│   ├── crm/                       # HubSpot, Salesforce
│   └── sequencers/                # SalesLoft, Outreach, Apollo, 11x, Smartlead/Instantly
└── templates/                     # 3 golden reference workbooks
    ├── 01-abm-tier1-with-triggers.md
    ├── 02-inbound-demo-enricher-router.md
    └── 03-cold-outbound-multi-provider-waterfall.md
```

---

## Design provenance

Composed from the best patterns across the Claude Code Clay ecosystem:

| Pattern | Source |
|---------|--------|
| Master + sub-skill split with routing table | forma-norden/clay-claude-code-skill-pack |
| 8 Global Rules (Gates Before Credits, etc.) | mariosworkflows/clay-engineer |
| 8-question mandatory intake | LirKonu/clay-campaign |
| Action registry + verification pattern | TenSpy-ai/claycast |
| Pre-built workflow patterns | sachacoldiq/ColdIQ-s-GTM-Skills |
| Standalone + cross-link footer | ColdIQ |

The four load-bearing patterns: forma's routing table, clay-engineer's Global Rules, clay-campaign's 8-Q intake, claycast's action registry.

---

## What it WON'T do

- Build a workbook without running the 8-question intake first
- Add paid columns before an ICP gate exists
- Push to a sequencer without a Sending Gate column
- Run anything with `auto_run = true` during construction
- Generate outbound copy without confirming voice / client context
- Skip the credit pre-flight on runs > 100 rows

These are by design. Override per case with `gate-override: <reason>`.

---

## Roadmap

- [ ] Subroutine save / load (capture an MCP-executed workbook as reusable subroutine)
- [ ] Cost analytics dashboard (track burn rate per workbook over time)
- [ ] Claygent prompt iteration loop (5/25/100 row sample → auto-refine)
- [ ] Schema operations (create new tables via MCP when Clay exposes the API)
- [ ] Backfill pattern: detect existing workbooks missing Global Rules, suggest fixes

---

## License

MIT — see [LICENSE](LICENSE).

## Author

[Brandon Redlinger](https://stackandscale.ai) — Fractional VP Marketing / GTM engineer.

Built for the Stack & Scale audience: GTM operators who think in systems, not tactics.
