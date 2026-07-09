---
name: clay-workflow-build
description: Build and edit Clay Workflows (Alpha) programmatically via the official Clay Agent Plugin — Claygent (agent) nodes + tool nodes, validated, snapshot-protected, tested 5/25/100, and productionized as a routine. Enforces the Global Rules at the node level — gate node before paid tool nodes, Sending Gate node before any sequencer push. Triggers — "build a Clay workflow", "Clay automation", "workflow nodes", "edit_node", "Claygent workflow", "automate this in Clay", "Clay agent workflow", "wire up a workflow", "/clay-workflow-build".
---

# clay-workflow-build — Build Clay Workflows via the Agent Plugin

Loads when the user wants to **build or edit a Clay Workflow** — the graph-based automations of Claygent (agent) nodes and tool nodes. This is the v3.0 capability the old "Known Gaps" list said was impossible: the official Agent Plugin's `edit_node` / `validate_workflow` / `execute_clay_action` MCP tools plus the `clay workflows` CLI give real write access.

Inherits `clay-workbench/SKILL.md` master workflow. Requires **Tier 1** (see `resources/execution-surface.md`) — if the `clay` CLI isn't authenticated, run the official plugin's `setup` skill first; there is no Tier 2 fallback for workflow writes.

**Workflows are Alpha.** Snapshot before edits, validate before runs, and never skip the plan-approval step.

---

## Workflow vs. Workbook — route correctly

| Signal | Route |
|--------|-------|
| Row-by-row table enrichment, columns, formulas | Table workbook skills (`/clay-abm-list`, `/clay-enrich-waterfall`, …) |
| Event-driven or multi-step automation with reasoning steps | **This skill** |
| "Run an existing workflow/routine" | `clay routines runs` directly — don't load this skill |
| Table creation from scratch | Still UI-only — but ask whether a *workflow* solves the underlying need |

---

## Inputs Expected

From intake (`resources/intake-questions.md`, adapted):
- **Trigger**: how does the workflow launch? (audience segment / webhook / Clay table / manual runs) — triggers are configured by the user in the UI; you design around them
- **Steps**: the reasoning and data operations, in order
- **Paid actions**: which steps hit paid providers (enrichment, email finders, phone)
- **Gate criteria**: cheapest-signal disqualification (Global Rule #4) — what disqualifies a record BEFORE paid nodes run
- **Destination**: CRM write, sequencer push, Slack, webhook out
- **Voice/client context**: if the workflow drafts copy, run client-voice detection first

---

## Step 3 — Composition (Specialized)

Design the graph on paper before touching `edit_node`:

```
[Trigger (UI-configured)]
  → [gate node]            agent or tool node evaluating cheap signals — routes DISQUALIFIED to exit
  → [paid tool node(s)]    enrichments, waterfalls — ONLY downstream of the gate
  → [Claygent node(s)]     reasoning / drafting / classification
  → [sending gate node]    eligibility check — ONLY if a sequencer/CRM push follows
  → [destination node]     CRM write / sequencer / Slack / webhook
```

Node type selection:
- **Claygent (agent) nodes** — LLM loops: reasoning, drafting, summarizing, classifying, edge routing. Cannot be created *with tools attached* via MCP (user can add tools in the UI afterward).
- **Tool nodes** (`nodeType: "tool"`) — exactly one Clay action, no LLM: enrichments, HTTP calls, CRM writes.

Global Rules at the node level:
1. **Gate node before paid tool nodes** (Rules #1, #4) — the graph equivalent of the two-pass gate. A workflow whose first paid node has no upstream disqualification path violates Gates Before Credits.
2. **Sending Gate node before any sequencer push** (Rule #2) — an explicit eligibility node whose FALSE edge exits, never straight into the push.
3. **Free before paid** (Rule #5) — order waterfall tool nodes cheapest-first.
4. **Prefer deterministic over LLM** — if a step is a lookup or a format transform, use a tool node or formula, not a Claygent. (This is also the official `workflow-simplify` guidance — cheaper and more reliable.)

Present the plan as a Mermaid graph + node table (`node | type | action/prompt summary | cost | depends_on`) and **wait for approval** before building.

---

## Step 5 — Execution (Specialized)

### Discover and verify actions first

```
clay workflows actions                      # browse the action catalog (or /workflow-discover-actions)
execute_clay_action (MCP)                   # dry-run the chosen action on ONE record —
                                            # confirms workspace availability + exact input/output shape
                                            # (costs that action's credits for 1 row — say so)
```

Refer to actions by human-readable names ("Waterfall Email Finder"), never raw `actionKey`s — and remember the `actionKey: "ai"` silent-drop gotcha from `resources/action-registry.md`.

### Build

```
1. clay credits                              # pre-flight baseline
2. clay workflows create --name "..."        # new workflow, or clay workflows get <id> for existing
3. clay workflows snapshots <id>             # existing workflow? note latest snapshot id FIRST
4. edit_node (MCP)                           # create nodes per approved plan, gate-first order
5. validate_workflow (MCP)                   # after every meaningful change
6. clay workflows diagram <id>               # render Mermaid — show the user the current graph
```

Narrate as you go: what changed, why, current graph. This mirrors the official plugin's own operating instructions.

### Test — 5 / 25 / full (same discipline as Claygent iteration)

```
clay workflows runs start <id> ...           # 5 records first
clay workflows runs get <runId>              # poll status + inspect outputs
→ verify gate behavior: disqualified records must exit BEFORE paid nodes
→ verify paid node outputs against expectations
→ 25 records → check match rates vs resources/enrichment-benchmarks.md
→ full volume only after both samples pass + credit pre-flight on projected volume
```

If a Claygent node underperforms (fabrication, blanks), take the prompt through `/clay-claygent-iterator` before scaling.

### Productionize

```
clay routines create workflow <workflowId>   # expose as a named, runnable routine
clay routines runs start ...                 # async runs + status for ongoing operation
```

Then tell the user what to configure in the UI (Tier 3): the trigger (audience / webhook / table) and any Claygent tool attachments.

---

## Verify-and-Handoff Checklist

- [ ] Plan (graph + node table) approved by user before first `edit_node`
- [ ] Snapshot id recorded before editing any existing workflow
- [ ] Gate node upstream of every paid tool node — no bypass path
- [ ] Sending Gate node upstream of any sequencer/CRM push — FALSE edge exits
- [ ] `validate_workflow` clean
- [ ] 5-record run: gate exits verified, outputs correct
- [ ] 25-record run: match rates within benchmarks, credits/record recorded
- [ ] Routine created; trigger + tool-attachment steps handed to user as explicit UI clicks
- [ ] Final Mermaid diagram delivered

---

## Anti-Patterns

❌ `edit_node` before the user approved the plan — Alpha surface + unreviewed graph = expensive mess.
❌ Claygent node doing a deterministic lookup a tool node handles — pays LLM cost for no reasoning.
❌ Paid tool node reachable without passing the gate node.
❌ Sequencer push node with no Sending Gate upstream — Rule #2 violation, `gate-override` required.
❌ Editing an existing workflow without noting the latest snapshot — no undo path.
❌ Scaling past 25 records with an untuned Claygent node prompt.

---

## Related

- Prompt quality for agent nodes → `/clay-claygent-iterator`
- Cutting a built workflow's credit/LLM cost → official `workflow-optimize-credits` + `workflow-simplify` skills, findings fed into `/clay-cost-audit`
- Version history / undo → official `workflow-snapshots` skill
- Sourcing the records the workflow runs on → `/clay-tam-source`, `/clay-abm-list`
- Inbound webhook wiring → `/clay-inbound-routing` (now creates webhooks via `clay webhooks create`)
