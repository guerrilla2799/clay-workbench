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
| **SAVE** | "save this workbook as a template", "capture this as a template" | template.json + README.md + INDEX.md update |
| **LOAD** | "instantiate template X", "load template X for {client}", "use template X as a starting point" | Step-by-step Clay UI walkthrough OR MCP run with parameterized inputs |
| **LIST** | "what templates do I have?", "list templates" | Read of INDEX.md with filters (use case, motion, client) |
| **DIFF** | "what changed between template v1 and v2?", "diff templates" | Column-by-column diff between two versions |
| **VERSION** | "bump this template", "save v2 of template X" | New version dir + version-pinned INDEX entry |
| **SHARE** | "export this template", "share template X" | Bundled markdown + JSON ready to paste / commit |

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

Brandon can save these incrementally as he builds them for real clients.

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
- Templates committed to the public repo live alongside the other plugin resources at https://github.com/guerrilla2799/clay-workbench.
