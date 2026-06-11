---
name: clay-template-library
description: Save, load, share, and version Clay workbook templates. Capture a working workbook as a portable JSON spec (columns + formulas + run conditions + waterfall order + Claygent prompts), store in the plugin's templates/ directory, instantiate into new workbooks for new clients, and keep a versioned library across engagements. The persistence layer for clay-workbench. Triggers — "save this as a template", "load template", "Clay template", "template library", "reusable workbook", "clone workbook", "version this workbook", "share workbook", "import template", "/clay-template-library".
---

# clay-template-library — Save, Load, Share Workbook Templates

The persistence skill. Turns ad-hoc workbooks into reusable, versioned, portable templates so a working workbook for Obin becomes a starting point for Vantage in 2 minutes instead of 2 hours.

Inherits `clay-workbench/SKILL.md` master workflow but specializes the whole flow around capture, instantiation, and versioning — not net-new composition.

**Template store location:** `~/.claude/claudecodeskills/clay-workbench/templates/`
- `01-abm-account-keyed.md` (existing golden ref — keep)
- `02-contact-waterfall.md` (existing golden ref — keep)
- `03-inbound-routing.md` (existing golden ref — keep)
- `library/<template-slug>/template.json` — JSON specs added by this skill
- `library/<template-slug>/README.md` — human-readable description
- `library/INDEX.md` — registry of all templates with one-line descriptions

---

## Operating Modes

State the mode at the start of any response.

| Mode | Triggered By | Output |
|------|-------------|--------|
| **SAVE** | "save this workbook as a template", "capture this as a template" | template.json + README.md + INDEX.md update (manual or hybrid composition) |
| **EXPORT** | "export subroutine `<id>`", "round-trip this Clay subroutine to a template", "make this subroutine portable" | template.json + README.md + INDEX.md + portability report (automated MCP round-trip from a live Clay subroutine or table) |
| **LOAD** | "instantiate template X", "load template X for {client}", "use template X as a starting point" | Step-by-step Clay UI walkthrough OR MCP run with parameterized inputs |
| **LIST** | "what templates do I have?", "list templates" | Read of INDEX.md with filters (use case, motion, client) |
| **DIFF** | "what changed between template v1 and v2?", "diff templates" | Column-by-column diff between two versions |
| **VERSION** | "bump this template", "save v2 of template X" | New version dir + version-pinned INDEX entry |
| **SHARE** | "share template X with a teammate / commit to repo" | Bundled markdown + JSON ready to paste / commit |

---

## SAVE Mode

### Inputs

- Source workbook ID (table ID in Clay) OR description of an in-progress workbook
- Template slug (kebab-case)
- One-line description (used in INDEX.md)
- Use case: ABM list / enrichment / scoring / outbound / inbound / research / monitoring / hygiene
- Motion (SLG / PLG / hybrid)
- Client to anonymize from (strip client-specific values to placeholders)
- Estimated cost per row at default settings

### template.json Schema

```json
{
  "schema_version": "1.0",
  "template": {
    "slug": "<kebab-case>",
    "name": "<human-readable>",
    "version": "1.0",
    "description": "<one line>",
    "use_case": "<abm-list | enrichment | scoring | outbound | inbound | research | monitoring | hygiene>",
    "motion": "<slg | plg | hybrid>",
    "created_at": "<ISO date>",
    "created_from_workbook_id": "<clay table id or 'manual'>",
    "estimated_cost_per_row": "<credits>",
    "expected_match_rate": "<percent>",
    "required_resources": ["<provider names>", "<integrations>"]
  },
  "intake_defaults": {
    "source_type": "<csv | hubspot_view | salesforce_report | webhook | subroutine>",
    "icp_industries": ["<placeholder>"],
    "icp_geo": ["<placeholder>"],
    "icp_size_min": "<placeholder>",
    "icp_size_max": "<placeholder>",
    "trigger_required": "<true | false>"
  },
  "columns": [
    {
      "name": "<column_name>",
      "type": "<text | number | formula | enrichment | claygent | action>",
      "source": "<provider or formula or claygent>",
      "cost_credits": "<int>",
      "depends_on": ["<column_names>"],
      "run_condition": "<formula or null>",
      "config": {
        "provider_key": "<e.g. apollo, findymail, use-ai>",
        "package": "<if applicable>",
        "max_sources": "<for claygent>",
        "model": "<sonnet | opus | null>"
      },
      "formula_text": "<clayscript with {{PLACEHOLDERS}} for client-specific values>",
      "claygent_prompt": "<5-block prompt with {{PLACEHOLDERS}}>",
      "notes": "<gotchas or rationale>"
    }
  ],
  "actions": [
    {
      "name": "<action_name>",
      "type": "<slack | crm_create | crm_update | sequencer_push | webhook | google_sheets>",
      "run_condition": "<formula>",
      "config": { "channel": "<placeholder>", "destination": "<placeholder>" },
      "notes": "<gotchas>"
    }
  ],
  "verification_checklist": [
    "<checklist item>"
  ]
}
```

### README.md (Human-Readable Per Template)

```markdown
# <Template Name>

**Slug**: `<slug>` · **Version**: `<v>` · **Use case**: `<use_case>` · **Motion**: `<motion>`

<one-paragraph description>

## When to use this
<bullet list of triggers>

## What it produces
<bullet list of outputs>

## Required inputs (placeholders to fill)
| Placeholder | Description | Example |
|-------------|-------------|---------|
| ...         | ...         | ...     |

## Required integrations
- Clay providers: ...
- CRM: ...
- Sequencer: ...
- Slack: ...

## Cost
- Estimated credits/row: ...
- 1k-row run: ...
- Expected match rate: ...

## Known good for
- <Client A> (created from this workbook on <date>)
- <Client B> (instantiated <date>)

## Notes / Gotchas
- ...

## Changelog
- v1.0 — <date> — initial save
```

### Anonymization Rules (Critical)

When saving from a real client workbook, strip:
- Client name → `{{CLIENT_NAME}}`
- Domain whitelists → `{{ICP_DOMAINS}}`
- Specific industries → `{{ICP_INDUSTRIES}}`
- Specific titles → `{{ICP_TITLES}}`
- Slack channel names → `{{SLACK_CHANNEL}}`
- CRM object IDs / list IDs → `{{CRM_OBJECT_ID}}`
- Sender names in outbound copy → `{{SENDER_NAME}}`
- Specific competitors named in Claygent prompts → `{{COMPETITORS}}`

Never save raw client data, suppression lists, or proprietary trigger rubrics in a template intended for cross-client reuse.

### Step 5 — SAVE Execution

```
1. mcp__claude_ai_Clay__query-objects on the source workbook to enumerate columns
2. For each column → extract: name, type, provider, formula text, claygent prompt, run condition, cost estimate
3. Apply anonymization rules
4. Compose template.json
5. Compose README.md
6. Write to ~/.claude/claudecodeskills/clay-workbench/templates/library/<slug>/{template.json, README.md}
7. Append one-line entry to ~/.claude/claudecodeskills/clay-workbench/templates/library/INDEX.md
8. Confirm with user: "Template saved at <path>. Want me to commit it to the clay-workbench repo?"
```

---

## LOAD Mode

### Inputs

- Template slug (or "pick from list" → show INDEX.md)
- Target client (for voice + ICP overrides)
- Placeholder values for `{{...}}` fields in formulas / prompts

### Step 5 — LOAD Execution

```
1. Read ~/.claude/claudecodeskills/clay-workbench/templates/library/<slug>/template.json
2. Ask user to fill placeholders (use AskUserQuestion for any missing required fields)
3. For client-voice columns (outbound copy), detect client name and load matching messaging skill
4. Output a column-by-column composition spec (matches the format of the master workflow step 3)
5. Run /clay-credits in forecast mode with the filled spec
6. Confirm with user → proceed to either:
   - MCP: walk through column-by-column creation (Clay MCP doesn't yet support full workbook import from JSON)
   - Manual: produce a numbered Clay UI walkthrough
7. After workbook built → run 5/25/full verification per master workflow step 6
```

---

## LIST Mode

```
Read ~/.claude/claudecodeskills/clay-workbench/templates/library/INDEX.md
Filter by use_case / motion if user specifies
Return formatted table:

| Slug | Name | Use Case | Motion | Cost/Row | Match Rate | Last Updated |
|------|------|----------|--------|----------|-----------|--------------|
| ...  | ...  | ...      | ...    | ...      | ...       | ...          |
```

---

## DIFF Mode

```
Read template.json from two versions
Diff:
- Columns added / removed
- Formula text changed (show inline diff)
- Claygent prompts changed (show inline diff)
- Cost-per-row changed
- Run conditions changed
- Actions added / removed

Output: changelog-style markdown
```

---

## VERSION Mode

```
1. Read existing template at templates/library/<slug>/
2. Bump version (semver — patch for formula tweaks, minor for column adds, major for use-case shift)
3. Copy current template.json to template.json.v<old> (preserved)
4. Save new template.json
5. Append entry to README.md Changelog section
6. Update INDEX.md version + last_updated
```

---

## EXPORT Mode

The automated round-trip. Where SAVE assumes manual or hybrid composition, EXPORT reads a **live Clay subroutine or table** via MCP, extracts the complete structure, applies workspace-portability transforms + anonymization, and writes a portable `template.json` that can be loaded into a different Clay workspace.

This is the canonical way to add templates to the library going forward — manual JSON authoring (the bootstrap method) only happens when no live workbook exists yet.

### When to use EXPORT vs SAVE

| Situation | Use |
|-----------|-----|
| You have a working Clay subroutine you want to make reusable | **EXPORT** |
| You have a working Clay table (not yet promoted to subroutine) that you want to template | **EXPORT** |
| You're designing a template from a markdown spec / golden reference without a live workbook | **SAVE** |
| You're refactoring an existing template's structure | **VERSION** (not EXPORT) |

### Inputs

- Source: **subroutine_id** (preferred) OR table_id (fallback for un-promoted workbooks)
- Target template slug (kebab-case, will mkdir at `templates/library/<slug>/`)
- Anonymization profile (default: standard rules; advanced: custom denylist + allowlist)
- Include actions? (default: yes, with action targets abstracted to placeholders)

### Execution

```
1. Identify source:
   - If subroutine_id provided:
       mcp__claude_ai_Clay__list_subroutines        # confirm it exists
       mcp__claude_ai_Clay__get_subroutine_input_options   # get input schema
   - If table_id provided:
       mcp__claude_ai_Clay__query-objects           # enumerate columns + actions
       (mark template as "table-sourced, not subroutine-promoted" in description)

2. For each column extracted, capture:
   - name, type (text | number | formula | enrichment | claygent | action)
   - source (provider name)
   - cost_credits (estimated)
   - depends_on (back-references to other columns by name)
   - run_condition (raw clayscript with column refs preserved)
   - config (provider_key, package, max_sources, model — all as captured)
   - formula_text (raw clayscript)
   - claygent_prompt (raw prompt, multi-line preserved)
   - notes (gotchas observed in the live workbook)

3. For each action extracted, capture:
   - name, type, run_condition, config (target IDs → placeholders), notes

4. Apply WORKSPACE-PORTABILITY transforms (different from anonymization — these are about cross-workspace re-instantiation, not data leak prevention):
   - Slack channel IDs (`C0123ABC`) → `{{SLACK_CHANNEL_ID_<purpose>}}`
   - CRM list/object IDs → `{{CRM_<object>_ID}}`
   - Suppression / lookup table IDs → `{{<purpose>_TABLE_ID}}`
   - Webhook URLs → `{{WEBHOOK_URL_<purpose>}}`
   - Sequencer cadence IDs → `{{<sequencer>_CADENCE_<step>_ID}}`
   - Sender names / emails in outbound copy → `{{SENDER_NAME}}` / `{{SENDER_EMAIL}}`
   - Action keys that are Clay-tier-specific → preserve key BUT add `notes` flag: "Requires Clay tier X or own-key for provider Y"

5. Apply standard ANONYMIZATION rules (the same set as SAVE):
   - Client name → `{{CLIENT_NAME}}`
   - Industry / size / geo lists → `{{ICP_INDUSTRIES}}`, `{{ICP_GEO}}`, etc.
   - Title lists → `{{ICP_TITLES}}` / `{{TARGET_SENIORITY}}`
   - Specific competitors named in Claygent prompts → `{{COMPETITORS}}`
   - Internal product names / project codenames → `{{OUR_PRODUCT_CATEGORY}}` or similar
   - SDR pool user IDs → `{{SDR_POOL_LIST}}`

6. Compose template.json with auto-detected metadata:
   - schema_version: "1.0"
   - template.created_from_workbook_id: <subroutine_id or table_id>
   - template.created_at: ISO date of export
   - template.estimated_cost_per_row: computed sum of column cost_credits weighted by run conditions
   - template.required_resources: union of all provider_keys + action types

7. Compose README.md with the placeholder map auto-populated from steps 4–5. Each placeholder gets a row in the "Required inputs" table with:
   - The placeholder name
   - The original value (REDACTED in the README but shown in the portability report)
   - A description inferred from the column context
   - An example value (synthetic — never the original)

8. Write to `templates/library/<slug>/{template.json, README.md}`

9. Append a one-line entry to `templates/library/INDEX.md` under the alphabetical row + the correct stage group.

10. Generate the PORTABILITY REPORT — a transient artifact (not saved to repo) shown to the user listing:
    - Total columns + actions extracted
    - Workspace-portability transforms applied (count by category)
    - Anonymization substitutions applied (count by rule)
    - Any column keys that look workspace-specific but weren't auto-handled (manual review queue)
    - Round-trip recommendation: "Load this template into a sandbox workspace and run 5 rows to verify before adding to repo"

11. Confirm with user: "Template exported to `<path>`. Portability report above. Want me to (a) commit to clay-workbench repo, (b) keep local-only, or (c) run a round-trip verification against a sandbox workspace?"
```

### Workspace-Portability vs Anonymization (Critical Distinction)

These are TWO separate concerns and EXPORT applies both:

| Concern | Why it matters | Example |
|---------|---------------|---------|
| **Workspace-portability** | Even within the same client, if the template gets re-instantiated in a different Clay workspace (sandbox, prod, second tenant), the workspace-specific IDs (Slack channel IDs, Cadence IDs, table IDs) won't resolve. | Slack channel `C0789` exists in workspace A, not workspace B. Template must use `{{SLACK_CHANNEL_ID_HOT_INBOUND}}` so the load step prompts for the right value per workspace. |
| **Anonymization** | If the template gets SHARED (across clients, into the public repo, in a community PR), client data must not leak. | "Obin AI" as a client name in a Claygent prompt → `{{CLIENT_NAME}}`. |

A template can be **portable but not anonymized** (safe to share within the client across workspaces but NOT to share publicly). Default EXPORT applies BOTH so the output is share-safe.

### Round-Trip Verification (Strongly Recommended)

After EXPORT, before adding the template to the public library:

```
1. Pick a sandbox Clay workspace (different from source)
2. /clay-template-library load <exported-slug>
3. Fill all placeholders with synthetic test values
4. Run the loaded workbook on 5 test rows
5. Spot-check:
   - Every column resolves with no NULL on the inputs that should have data
   - Every formula reference still parses (no orphaned column names from the source workspace)
   - Every action fires to the placeholder target (use a sandbox Slack channel + sandbox CRM)
   - Cost-per-row matches the exported estimate within ±20%
6. If pass: commit the template to the repo
7. If fail: re-EXPORT with a different anonymization profile OR manually fix the gaps that the auto-transform missed
```

### Edge Cases

- **Subroutines with multiple input variants**: a Clay subroutine can accept N different input schemas (e.g., one for "company list" mode, one for "contact list" mode). EXPORT captures the FIRST input variant by default; flag others as "additional input variants to template separately" in the portability report. Don't try to merge them into one template.
- **Columns that depend on workspace-specific lookup tables**: if a column does `LOOKUP(<table_id>, ...)`, the table_id transforms to a placeholder BUT the schema of the lookup table is workspace-specific. Add a note in the README: "Lookup target `{{X_TABLE_ID}}` must have columns: <inferred schema>."
- **Claygent prompts that reference URLs or specific search domains**: these often contain leaked client context. EXPORT applies a heuristic scan for absolute URLs in prompts and lists them in the portability report for manual review.
- **Live workbooks with `auto_run = TRUE`**: EXPORT NEVER captures the run state. Template loads always start at `auto_run = FALSE` regardless of source.

### Anti-Patterns

❌ EXPORTing a template that hasn't been verified on at least one production run — captures bugs as features.
❌ Skipping the portability report — usually contains 1–2 manual-review items per export that the auto-transform couldn't classify.
❌ Committing an EXPORTed template to the public repo without a round-trip verification — discovers anonymization misses only after they've leaked.
❌ Using EXPORT to "fix" a template — that's what VERSION mode is for. EXPORT always creates a net-new slug.
❌ Treating EXPORT as the only way to add templates — for templates without a live source workbook (golden refs, hypothetical patterns), SAVE / manual JSON authoring is correct.

---

## SHARE Mode

### For a teammate / client receiving
```
Bundle into:
- <slug>-v<version>.json (the spec)
- <slug>-v<version>.md (the README)
- import-instructions.md (steps for the recipient to instantiate)

Paste-ready or commit-ready (default: paste-ready; ask before committing to public repo).
```

### For the clay-workbench public repo
- Strip ALL client identifiers (use the anonymization checklist)
- Verify no proprietary rubrics, suppression sources, or sender identities remain
- Commit to `templates/library/<slug>/` in the repo
- Open a PR if Brandon wants community contribution

---

## INDEX.md Format

```markdown
# Template Library Index

| Slug | Name | Use Case | Motion | Cost/Row | Match Rate | Version | Last Updated |
|------|------|----------|--------|----------|-----------|---------|--------------|
| ...  | ...  | ...      | ...    | ...      | ...       | ...     | ...          |
```

This file is the registry. Maintain alphabetical by slug.

---

## Verify-and-Handoff Checklist

For SAVE:
- [ ] Anonymization rules applied — no client identifiers in template.json or README
- [ ] template.json validates against schema (every column has required fields)
- [ ] README.md filled in (not a shell)
- [ ] INDEX.md updated
- [ ] Decision made: keep local OR commit to repo

For EXPORT:
- [ ] Source subroutine_id or table_id confirmed live (MCP returns metadata)
- [ ] All extracted columns have their `depends_on` references intact (no orphans)
- [ ] Workspace-portability transforms applied — every workspace-specific ID is a `{{PLACEHOLDER}}`
- [ ] Anonymization transforms applied — every client identifier is a `{{PLACEHOLDER}}`
- [ ] Portability report reviewed — manual-review queue items resolved or accepted
- [ ] Round-trip verification run on a sandbox workspace OR explicit decision to skip with reason logged
- [ ] No `auto_run = TRUE` carried over from source
- [ ] Lookup table schema notes added to README if applicable

For LOAD:
- [ ] Every `{{PLACEHOLDER}}` resolved before instantiation
- [ ] `/clay-credits` forecast run on the filled spec
- [ ] Client-voice messaging skill loaded if outbound copy involved
- [ ] 5-row sample run before scaling

For VERSION:
- [ ] Old version preserved (renamed, not deleted)
- [ ] Changelog entry written
- [ ] INDEX.md version bumped

For SHARE:
- [ ] Anonymization re-checked at share time (not just at save time)
- [ ] Recipient instructions included

---

## Seeded Templates (Bootstrap List)

These should be saved on first use, capturing the 3 existing golden references plus key patterns from the sub-skills:

1. **abm-account-keyed-tier-1** — Tier 1 ABM account workbook with two-pass gate
2. **email-waterfall-us-smb** — Apollo → Findymail → Dropcontact for US SMB
3. **email-waterfall-eu** — Dropcontact → Datagma → Findymail for EU
4. **inbound-router-demo-form** — webhook → enrich → ICP gate → Slack routing
5. **account-research-tier-1-brief** — multi-source Claygent account brief
6. **prospect-research-champion-brief** — person-level dossier with entry line
7. **signal-monitor-job-change** — daily job-change watcher with Slack alerts
8. **signal-monitor-hiring-posture** — weekly hiring-trigger monitor
9. **outbound-3-step-cadence-cold** — first-line + sequencer push for cold outbound
10. **outbound-3-step-cadence-warm** — for triggered/warm outbound off a signal monitor

All 10 shipped 2026-06-10 as anonymized JSON in `templates/library/`. New templates beyond these should use **EXPORT mode** against live Clay subroutines as the canonical authoring path — the bootstrap pattern (manual JSON authoring) was only used because no live workbooks existed for some patterns yet.

---

## Anti-Patterns

❌ Saving raw client workbook without anonymization — leaks client ICP / suppression list across engagements.
❌ Templates with hardcoded provider keys that the next user's tier doesn't have → instantiation silently fails.
❌ No README.md → future-Brandon can't tell what the template is for.
❌ Versioning by overwriting → loses history; always preserve prior version.
❌ INDEX.md drift from filesystem → templates that exist but aren't discoverable.
❌ Treating every workbook as template-worthy → only template what's proven on ≥1 real run AND likely to repeat.

---

## Related

- For composing a workbook from scratch (then optionally saving as template) → the 11 build sub-skills.
- For cost forecasting on a loaded template → `/clay-credits` (always run before instantiating at scale).
- For auditing template-instantiated workbooks for rule violations → `/clay-cost-audit`.
- For inspecting how templates feed each other → `docs/composition/` (auto-generated graph of cross-template + intra-template dependencies).
- For contributing a community template via PR → `CONTRIBUTING.md` at the repo root.
- Templates committed to the public repo live alongside the other plugin resources at https://github.com/guerrilla2799/clay-workbench.
