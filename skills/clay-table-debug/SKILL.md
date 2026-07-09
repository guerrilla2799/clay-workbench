---
name: clay-table-debug
description: Record-level and mechanical table debugging via the official Agent Plugin — routes symptoms to Clay's table-analyze / table-trace / table-value-trace / table-error-sweep / table-capacity skills and the `clay tables` CLI. Answers "what does this table do", "where is this record", "why is this cell empty/wrong", "what's erroring", "why is the import stuck". Cost/performance diagnosis stays with /clay-troubleshoot. Triggers — "debug this table", "trace this record", "why is this cell empty", "where did this value come from", "what's erroring", "failed rows", "import stuck", "table full", "explain this table", "/clay-table-debug".
---

# clay-table-debug — Mechanical Table Debugging

Loads when the user has a **specific table, record, or cell problem** — not a cost or match-rate problem. The official Agent Plugin ships five focused table-debugging skills; this skill is the workbench's front door to them: classify the symptom, route to the right official skill, and translate findings back into Global Rules terms.

Inherits `clay-workbench/SKILL.md`. Requires **Tier 1** (`resources/execution-surface.md`) — the `table` MCP tool and `clay tables` CLI.

**Boundary vs `/clay-troubleshoot`**: troubleshoot = *economic* diagnosis (burn rate, match rates, ROI, Global Rules violations). table-debug = *mechanical* diagnosis (this row, this cell, this error). Troubleshoot delegates here when its root cause turns out to be record-level; this skill escalates there when the mechanical fix reveals a systemic cost problem.

---

## Symptom → Route Table

| Symptom | Official skill | Typical invocation |
|---------|---------------|--------------------|
| "What does this table do?" / inherited a mystery workbook | `table-analyze` | Reconstructs the column DAG and narrates the encoded workflow |
| "Where is record X?" / "did this lead finish enriching?" | `table-trace` | Locates the record across tables, snapshots each cell's status |
| "Why is this cell empty/wrong?" / "why didn't {action} run?" | `table-value-trace` | Walks the column backward through dependencies + run-gate to origin |
| "What's failing?" / "show errored rows" | `table-error-sweep` | Sweeps errors, groups by root cause |
| "Import stuck" / "rows not being added" | `table-capacity` | Checks the row-capacity ceiling before you assume a config bug |

Raw inspection underneath all five: `clay tables get / columns / rows / query` (structured JSON, paginated; `query` requires per-table enable via `clay tables update`) and the `table` MCP tool (schema + NL query + CSV export).

---

## Debugging Order (when the symptom is vague)

```
1. table-analyze          → understand what the table is SUPPOSED to do (the DAG)
2. table-capacity         → rule out the dumb ceiling problem first (30 seconds)
3. table-error-sweep      → what's actually failing, grouped by cause
4. table-value-trace      → for each root cause, walk one representative cell to origin
5. table-trace            → confirm the fix on the specific record the user cares about
```

Skip straight to the matching row of the route table when the user's symptom is specific.

---

## Translate Findings into Workbench Terms

The official skills report mechanics; add the workbench layer on top:

- **Value-trace ends at a run-gate that never fired** → check whether the gate is our `icp_gate_qualified` / `pass_1_qualified` pattern working as designed (row was *correctly* disqualified — not a bug) vs. a broken gate formula. Say which.
- **Error sweep shows a provider failing systematically** → cross-check `providers/*.md` gotchas and `resources/enrichment-benchmarks.md`; if the provider is simply weak for this segment, that's a waterfall-order fix → `/clay-enrich-waterfall`.
- **Analyze reveals paid columns upstream of any gate** → Global Rules violation; flag for `/clay-cost-audit` and propose the two-pass gate retrofit.
- **Capacity ceiling hit** → decide with the user: archive rows, split the table, or move the use case to a workflow (`/clay-workflow-build`).

---

## Verify-and-Handoff Checklist

- [ ] Symptom classified against the route table before any deep dive
- [ ] Root cause stated as one sentence + the evidence chain (DAG / trace / sweep output)
- [ ] "Correctly gated" vs. "actually broken" distinction made explicit for empty cells
- [ ] Fix applied or handed off (UI steps for column-formula edits — still Tier 3)
- [ ] Re-trace of the original record/cell confirms the fix
- [ ] Systemic findings escalated: cost → `/clay-troubleshoot` / `/clay-cost-audit`; waterfall → `/clay-enrich-waterfall`

---

## Anti-Patterns

❌ Re-running an expensive column to "see if it works now" before tracing why it failed — burns credits on an undiagnosed fault.
❌ Diagnosing a config problem when the table is simply full — run capacity first.
❌ Reporting "cell is empty" without distinguishing gated-by-design from broken.
❌ Fixing one record when the error sweep shows 400 siblings with the same root cause.
❌ Using this skill for "Clay is expensive" — that's `/clay-troubleshoot`.

---

## Related

- Economic diagnosis (burn, match rates, ROI) → `/clay-troubleshoot`
- Portfolio-wide rule violations → `/clay-cost-audit`
- Waterfall reordering after provider findings → `/clay-enrich-waterfall`
- Claygent columns fabricating/blank → `/clay-claygent-iterator`
