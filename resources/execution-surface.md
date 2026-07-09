# Execution Surface — Which Clay Interface to Use (v3.0)

As of v3.0, clay-workbench executes against **three tiers** of Clay access, in strict preference order. Every sub-skill's "Execute" step resolves through this document. The old rule ("MCP-first, UI fallback") is superseded.

```
Tier 1 — Official Clay Agent Plugin        clay CLI + `clay mcp` tools     ← PRIMARY
Tier 2 — claude.ai Clay connector          mcp__claude_ai_Clay__* tools    ← fallback
Tier 3 — Manual UI walkthrough             numbered click-path steps       ← last resort
```

Why this order: the official plugin (open beta, `clay-run/agent-plugins`) is Clay's supported programmatic surface — JSON output, typed exit codes, and the only path with **write access to workflows**. The claude.ai connector still covers a few conveniences the CLI doesn't wrap (ad-hoc `find-and-enrich-*` primitives), so it stays as Tier 2. UI walkthroughs remain only for the genuinely UI-only operations (table column formulas, trigger config, HTTP API column setup).

---

## Tier 1 — Official Clay Agent Plugin

### Prerequisites (once per machine)

```
claude plugin marketplace add clay-run/agent-plugins
claude plugin install clay@clay-plugins
clay login          # browser OAuth — shared by CLI and `clay mcp`
# restart Claude Code — `clay mcp` resolves its session at launch only
```

Verify: `clay whoami; echo $?` → exit 0 with user + workspace JSON. If `clay` is not on PATH or `whoami` fails, run the official plugin's `setup` skill — do NOT improvise.

### The `clay` CLI (scripting surface)

JSON to stdout on success; `{"error":{code,message}}` to stderr on failure. Branch on exit codes: `0` ok · `2` validation · `3` auth (re-run `clay login`) · `4` rate-limited (details.retryAfter) · `5` network · `6` not found.

Command groups (run `clay --help` for the authoritative list — it grows):

| Group | What it does | Workbench usage |
|-------|-------------|-----------------|
| `clay credits` | Remaining credit balance | **Credit pre-flight — use this first, always** |
| `clay search filters-mode` | Structured-filter search over Clay's native companies + people dataset, with paging | `/clay-tam-source` — TAM sourcing without a table |
| `clay tables list/get/columns/rows/query` | Inspect + structured-query existing tables (query requires per-table enable via `clay tables update`) | State inspection, verification, exports |
| `clay workbooks list/get` | List + inspect workbooks | `/clay-cost-audit` portfolio sweep |
| `clay workflows list/get/create/runs/snapshots/actions/diagram` | Full workflow lifecycle: create, run, version history, action catalog, Mermaid diagram | `/clay-workflow-build`, run testing (5/25/100) |
| `clay routines list/get/create/update/runs` | Create a routine from a function/workflow; async runs + status | Productionizing a built workflow |
| `clay functions list` | List workspace functions | Discovery |
| `clay webhooks create/list/delete/test` | Manage webhooks (signing secret returned once) | `/clay-inbound-routing` — real webhook creation, no more UI-only |
| `clay feedback` | Bug report to Clay team | When we hit a beta bug |

CLI conventions that keep runs auto-approved: prefer one plain `clay <group> <cmd>` per call; avoid `&&`, `>`, `$(…)` chains; piping to `jq` is fine.

### The `clay mcp` tools (in-editor surface)

Registered by the plugin as a local MCP proxy sharing the CLI's session:

- `read` — read workflows and nodes
- `edit_node` — **create / update / delete workflow nodes** (agent + tool types)
- `validate_workflow` — validate before running
- `execute_clay_action` — run any Clay action one-off (also the way to learn an action's input/output shape before wiring it into a node)
- `table` — schema + natural-language query + CSV export on existing tables

**Restart caveat:** these tools only authenticate if Claude Code was restarted after `clay login`. If they error on auth while `clay whoami` succeeds, the fix is a restart, not re-login.

### What Tier 1 unlocks that v2.x could not do

| v2.x "Known Gap" | v3.0 status |
|------------------|-------------|
| Create automations programmatically | ✅ `clay workflows create` + `edit_node` (Workflows are **Alpha** — snapshot before edits) |
| Discover available actions + schemas | ✅ `clay workflows actions` + `execute_clay_action` dry-run |
| Version history / undo | ✅ `clay workflows snapshots` |
| Wire a webhook source | ✅ `clay webhooks create` |
| Structured table queries with pagination | ✅ `clay tables query` |
| TAM search without building a table | ✅ `clay search filters-mode` |
| Create a raw **table** from scratch | ❌ still UI-only — build a **workflow** instead where possible |
| Edit an existing table column's formula/source | ❌ still UI-only |
| Configure workflow **triggers** (audience, webhook, table) | ❌ UI-only — design around them, tell the user what to click |

---

## Tier 2 — claude.ai Clay connector (`mcp__claude_ai_Clay__*`)

Full tool-by-tool map: `resources/mcp-tool-map.md`. Use Tier 2 when:

- The `clay` CLI is not installed/authenticated and the user declines setup.
- You need the ad-hoc enrichment primitives the CLI doesn't wrap: `find-and-enrich-company`, `find-and-enrich-contacts-at-company`, `find-and-enrich-list-of-contacts`, `add-*-data-points`, `ask-question-about-accounts`.
- Running inside claude.ai (web) where there is no shell.

Subroutine execution (`list_subroutines` / `run_subroutine*`) now has a Tier-1 equivalent (`clay routines …`) — prefer Tier 1.

---

## Tier 3 — Manual UI walkthrough

Only for the residual UI-only operations listed above. Every sub-skill keeps its "Manual Fallback" section for these. Always state WHY the operation is Tier 3 ("trigger config is not exposed to agents yet") so the user knows it's a Clay limitation, not a skill gap.

---

## Credit Pre-Flight (updated for v3.0)

```
1. clay credits                      → {"balance": N}        (Tier 1)
   └─ fallback: mcp__claude_ai_Clay__get-credits-available   (Tier 2)
2. Estimate rows × credits/row       → resources/credit-cost-table.md
3. Block if estimate > balance × 0.5
4. Present cost + balance, run only on explicit confirmation
```

Unchanged in substance — Global Rule #1 enforcement. Only the balance source moved.

---

## Beta Discipline

The Agent Plugin is **open beta**; Workflows are **Alpha**. House rules:

1. **Snapshot before edit** — before any `edit_node` series on an existing workflow, note the latest snapshot id (`clay workflows snapshots`).
2. **Validate before run** — `validate_workflow` after every build, before any run.
3. **Dry-run actions** — `execute_clay_action` on ONE row to learn a schema before wiring a node. This costs that action's credits for one row; say so.
4. **Plan-first** — never `edit_node` before the user has approved the workflow plan (trigger, nodes, data flow). This mirrors the official plugin's own instruction and our Global Rule #6.
5. **Version pin awareness** — the CLI is pinned by the plugin; `clay update` may report "managed by plugin." Update the plugin, not the binary.
