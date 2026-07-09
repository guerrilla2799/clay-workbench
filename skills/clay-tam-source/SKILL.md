---
name: clay-tam-source
description: Source TAM directly from Clay's native companies + people dataset via `clay search filters-mode` — structured ICP filters, count preview, paged pulls, CRM/suppression dedup, and handoff to list hygiene + ABM build. No table required, no UI. Triggers — "source my TAM", "TAM sourcing", "how big is my TAM", "pull companies from Clay", "find companies matching", "search Clay for prospects", "market sizing from Clay", "build a prospecting universe", "/clay-tam-source".
---

# clay-tam-source — TAM Sourcing from Clay's Native Dataset

Loads when the user wants to **find companies or people in Clay's own GTM database** from structured criteria — TAM sizing, net-new prospecting universes, lookalike pulls — *without* building a table first. This is the v3.0 `search` primitive from the official Agent Plugin; v2.x had no equivalent.

Inherits `clay-workbench/SKILL.md` master workflow. Requires **Tier 1** (`resources/execution-surface.md`).

**Boundary**: this skill *sources* raw matches. It does not enrich, score, or activate — it hands off. Searching an **existing table** is `clay tables query` / `/clay-table-debug` territory, not this skill.

---

## Inputs Expected

From intake (adapted):
- **Entity**: companies, people, or companies-then-people
- **ICP filters**: industry/vertical, employee band, geo, funding stage, tech signals — pull from the client's `icp.md` when client context is detected
- **Exclusions**: current customers, open opps, competitors, DNC — which suppression sources exist (CRM export, suppression table)
- **Volume intent**: sizing only ("how big is my TAM?") vs. pull ("give me the list")
- **Destination**: CSV for review / `/clay-list-clean` → `/clay-abm-list` / directly into a workflow

---

## Step 3 — Composition (Specialized)

### Filter design — mirror the two-pass gate

Order filters strictest-first and keep pass 1 purely firmographic. Anything the search filters can disqualify is a row you never pull, dedupe, or enrich — the cheapest gate in the entire stack (Global Rule #4 applied *before* Clay even returns data).

```
Pass 1 — search filters (this skill):   industry, size band, geo, funding stage
Pass 2 — enrichment gates (later):      tech stack, triggers, persona presence
```

Run `clay search filters-mode --help` for the authoritative filter schema — the surface is beta and grows; do not assume filters from memory.

### Sizing before pulling

Always probe with one page first. Report: matches found, filter recall sanity check (spot-check 5 names against the ICP by hand), and only then page the full pull.

---

## Step 5 — Execution (Specialized)

```
1. clay credits                              # baseline balance
2. clay search filters-mode ... (page 1)     # probe: result count + 5-name sanity check
3. Present sizing:
   "TAM at these filters: ~{N} companies.
    Sample: {5 names} — confirm these look ICP."
4. Adjust filters with the user until the sample is clean
5. Page through the full pull → accumulate to CSV/JSON
6. clay credits                              # diff vs step 1 — record actual cost of the pull
7. Dedupe against suppression sources:
   - CRM export (domains of customers/open opps)
   - existing Clay tables (clay tables rows / query)
8. Deliver: raw_pull.csv + deduped_net_new.csv + drop_reason counts
```

Search cost is beta-variable — the step 1/6 balance diff on the probe page is the authoritative per-page cost; extrapolate it in the pre-flight before the full pull, per `resources/credit-cost-table.md` conventions.

### Manual Fallback (Tier 3)

Clay UI → new Search → apply the same filter set → export. Use only when the CLI is unavailable and the user declines setup — the CLI path is strictly better (repeatable, diffable, scriptable).

---

## Verify-and-Handoff Checklist

- [ ] Filter set documented (re-runnable as a saved command — quarterly TAM refresh = same command, diffed)
- [ ] 5-name sanity check confirmed by user before full pull
- [ ] Actual credits/page recorded from the balance diff
- [ ] Suppression dedup run — net-new count + drop reasons reported
- [ ] Handoff executed: `/clay-list-clean` for hygiene → `/clay-abm-list` for the gated workbook, or workflow input via `/clay-workflow-build`
- [ ] Cost-per-net-new-account documented

---

## Anti-Patterns

❌ Pulling the full TAM before the 5-name sanity check — wrong industry filter × 40k rows.
❌ Broad filters "to be safe," planning to gate later — pay the gate here, it's free.
❌ Skipping suppression dedup — enriching and routing your own customers downstream.
❌ Treating one pull as durable — TAM pulls decay; save the filter command, not just the CSV.
❌ Using this skill to query an existing table — that's `clay tables query`.

---

## Related

- Next step for every pull → `/clay-list-clean` (hygiene) → `/clay-abm-list` (gated workbook)
- Scoring the sourced universe → `/clay-icp-score`
- Feeding a workflow instead of a table → `/clay-workflow-build`
- Sizing math for content/strategy (SAM/SOM cuts) → deliver counts per filter variation
