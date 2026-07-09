# clay-workbench v3.0.0 — Built on Clay's Agent Plugin

Clay's [Agent Plugin](https://github.com/clay-run/agent-plugins) went open beta: a real `clay` CLI (JSON output, typed exit codes) plus in-editor MCP tools with **workflow write access**. v3.0 rebuilds clay-workbench's entire execution layer around it — the workbench keeps the GTM governance layer (Global Rules, gates, pre-flights, client voice) and now drives Clay's official plumbing instead of working around it.

19 sub-skills total (16 migrated + 3 new). Tier-1-first execution, connector fallback, UI walkthrough last.

## What's new

### 3 new sub-skills

- **`/clay-workflow-build`** — build Clay Workflows (Alpha) programmatically: Claygent + tool nodes via `edit_node`, `validate_workflow`, `execute_clay_action`. The Global Rules are enforced at the node level — gate node before any paid tool node, Sending Gate node before any sequencer push, snapshot-before-edit, 5/25 test discipline, productionized as a routine. This was the roadmap item marked "blocked on Clay exposing a write API." Unblocked.
- **`/clay-tam-source`** — TAM sourcing straight from Clay's native companies + people dataset via `clay search filters-mode`: sizing probe → 5-name sanity check → paged pull → suppression dedup → handoff to `/clay-list-clean` → `/clay-abm-list`.
- **`/clay-table-debug`** — record-level mechanical debugging: routes symptoms to the official `table-analyze` / `table-trace` / `table-value-trace` / `table-error-sweep` / `table-capacity` skills and translates findings into Global Rules terms ("correctly gated" vs "actually broken"). `/clay-troubleshoot` keeps the economic diagnosis.

### New execution layer

- **`resources/execution-surface.md`** — the 3-tier policy every sub-skill now resolves through: official Agent Plugin first (`clay` CLI + workflow MCP tools), claude.ai connector second (still uniquely owns the ad-hoc `find-and-enrich-*` primitives), manual UI walkthrough last.
- All 16 legacy sub-skills' execution sections migrated: `clay credits` pre-flight, `clay routines` for saved-workflow runs, `clay tables query` + `table` MCP tool for state, tier-labeled fallbacks throughout.
- **Programmatic webhooks** — `/clay-inbound-routing` now creates, tests, and manages webhooks via `clay webhooks` (signing secret handling included) instead of sending you to the UI.
- **Portfolio audit over real inventory** — `/clay-cost-audit` enumerates the estate via `clay workbooks/tables/workflows list` + `clay workflows diagram`, and adds workflow-level checks: paid tool node with no upstream gate, LLM node doing deterministic work.
- **Template round-trip via Tier 1** — `/clay-template-library` EXPORT reads full workflow/routine configs (`clay workflows get`, `clay routines get`), and workflow templates re-instantiate via `clay workflows create` + `edit_node`.

### Fixed

- `plugin.json` now passes `claude plugin validate` (v2.x carried non-schema keys and object-shaped fields).

## Still UI-only (honest list)

Table creation, table column formula edits, and workflow trigger configuration remain UI-only even in the Agent Plugin. Sub-skills say so explicitly and hand you exact click paths.

## Install

Prerequisite (Tier 1):

```
claude plugin marketplace add clay-run/agent-plugins
claude plugin install clay@clay-plugins
clay login     # then restart Claude Code
```

Then install clay-workbench per the README (clone + register, or plugin manifest). Restart Claude Code. All 19 sub-skills should resolve.
