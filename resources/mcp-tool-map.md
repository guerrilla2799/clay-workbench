# Clay MCP — Tool Map

Authoritative map of every `mcp__claude_ai_Clay__*` tool and when to call it. This is your primary execution path. Fall back to manual walkthrough only when the operation isn't supported.

---

## Discovery & State

### `mcp__claude_ai_Clay__list_subroutines`
**What**: Lists every available Clay subroutine (saved workflow / template) in the workspace.
**When**: Always call first when user wants to "run an existing workflow" or "use a template."
**Cost**: 0 credits.

### `mcp__claude_ai_Clay__get_subroutine_input_options`
**What**: Returns the input schema for a specific subroutine — what fields it expects.
**When**: Before calling `run_subroutine` so you know exactly what to pass.
**Cost**: 0 credits.

### `mcp__claude_ai_Clay__get-credits-available`
**What**: Returns current Clay credit balance.
**When**: **MANDATORY pre-flight** before any run touching >100 rows or any paid waterfall. Per Global Rule #5.
**Cost**: 0 credits.

### `mcp__claude_ai_Clay__query-objects`
**What**: Read rows from an existing Clay table.
**When**: For inspecting current data, verifying enrichments completed, or pulling state into Claude for analysis.
**Cost**: 0 credits (read-only).

### `mcp__claude_ai_Clay__get-task` / `get-task-context`
**What**: Inspect a specific Clay task / job state.
**When**: Debugging a running or failed run.
**Cost**: 0 credits.

---

## Execution (CAUTION — burns credits)

### `mcp__claude_ai_Clay__run_subroutine`
**What**: Runs a subroutine with mapped inputs (Clay performs input mapping).
**When**: Standard execution path for any saved workflow.
**Cost**: Variable — depends on subroutine. **Always estimate via credit-cost-table.md first.**
**Pre-flight required**: ALWAYS.

### `mcp__claude_ai_Clay__run_subroutine_direct`
**What**: Runs a subroutine with explicit input passthrough (no Clay mapping).
**When**: When you need exact control over which input field receives which value.
**Cost**: Same as `run_subroutine`.
**Pre-flight required**: ALWAYS.

### `mcp__claude_ai_Clay__run_subroutine_no_mapping`
**What**: Runs a subroutine without input mapping at all.
**When**: Advanced — when inputs are already pre-shaped.
**Cost**: Same as above.
**Pre-flight required**: ALWAYS.

---

## Enrichment Primitives

### `mcp__claude_ai_Clay__find-and-enrich-company`
**What**: Given a domain or company name, returns Clay's company enrichment (firmographics, tech, funding, employees).
**When**: Single-row company enrichment, or building the firmographic foundation for a workbook.
**Cost**: ~1 credit per company.

### `mcp__claude_ai_Clay__find-and-enrich-contacts-at-company`
**What**: Given a company + persona criteria (titles, departments, seniority), returns matched contacts with enrichment.
**When**: Building persona contact rows from an account list.
**Cost**: Variable — depends on contacts found + provider waterfall used. Estimate 1–4 credits per contact.

### `mcp__claude_ai_Clay__find-and-enrich-list-of-contacts`
**What**: Bulk version of contact finding across many companies.
**When**: ABM account list → contacts at each. Most common pattern.
**Cost**: Variable. **HIGH CREDIT SPEND. Always pre-flight.**

---

## Schema Operations

### `mcp__claude_ai_Clay__add-company-data-points`
**What**: Adds enrichment columns to a company-keyed Clay table (e.g., adds "Employee count" column).
**When**: Extending an existing workbook with additional firmographic fields.
**Cost**: Per-column credit cost when rows are filled.

### `mcp__claude_ai_Clay__add-contact-data-points`
**What**: Adds enrichment columns to a contact-keyed Clay table (e.g., adds "Verified email," "LinkedIn URL").
**When**: Extending an existing contact list.
**Cost**: Per-column credit cost when rows are filled.

---

## Q&A / Analysis

### `mcp__claude_ai_Clay__ask-question-about-accounts`
**What**: Natural-language query against the accounts table.
**When**: User asks "how many Tier 1 accounts have we enriched?" or similar.
**Cost**: 0 credits.

---

## Observability

### `mcp__claude_ai_Clay__track-event`
**What**: Log a custom event in Clay's event stream.
**When**: Mark milestones in a multi-step run (e.g., "ICP gate complete," "Sending Gate complete").
**Cost**: 0 credits.

---

## Decision Tree — Which Tool to Use

```
User wants to...
├── See what workflows exist
│   └── list_subroutines
├── Run an existing saved workflow
│   ├── get_subroutine_input_options  (first, to learn schema)
│   ├── get-credits-available          (mandatory pre-flight)
│   └── run_subroutine                 (execution)
├── Enrich a single company / domain
│   └── find-and-enrich-company
├── Find contacts at a company
│   └── find-and-enrich-contacts-at-company
├── Bulk: account list → contacts at each
│   ├── get-credits-available          (mandatory pre-flight)
│   └── find-and-enrich-list-of-contacts
├── Add columns to an existing table
│   └── add-company-data-points / add-contact-data-points
├── Inspect current state
│   ├── query-objects                  (read rows)
│   ├── get-task                       (check job state)
│   └── ask-question-about-accounts    (NL summary)
└── Build a brand-new workbook from scratch
    ├── MCP can't create raw tables yet
    └── FALLBACK: manual walkthrough + clay-builder.py (claycast pattern)
```

---

## Known Gaps (MCP Cannot Do)

Use manual walkthrough or claycast-style scripting when:

- **Create a new Clay table from scratch** — MCP can only operate on existing tables / subroutines. Workaround: build subroutine in Clay UI first, then expose via MCP.
- **Modify an existing column's formula / source** — schema edits aren't supported via MCP.
- **Wire a new HTTP API enrichment** — must be configured in Clay UI.
- **Reorder columns** — UI-only.
- **Set up the Sending Gate filter on an export action** — must configure in Clay UI on the destination action.

When any of these are needed, fall back to a step-by-step walkthrough — see each sub-skill's "Manual Fallback" section.

---

## Pre-Flight Pattern (Apply Before Every Paid Run)

```
1. get-credits-available           → current balance
2. Estimate rows × credit/row      → see credit-cost-table.md
3. Compare estimate vs balance     → block if estimate > balance × 0.5
4. Present to user:
   "This will run N rows through {waterfall}.
    Estimated cost: X credits (~$Y at your tier).
    Current balance: Z credits.
    Continue? [Y/n]"
5. Only run if user confirms.
```

Per Global Rule #1: **Gates Before Credits.** Pre-flight is the last gate.
