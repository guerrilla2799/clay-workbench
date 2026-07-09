# Contributing to clay-workbench

`clay-workbench` is a Claude Code plugin for Clay.com workbook + workflow construction — 19 sub-skills covering hygiene, source + build, score, activate, cost/quality, and persistence. See [README.md](README.md) for the full picture.

Contributions are reviewed against one bar: does this make the plugin more useful to a GTM operator building real workbooks?

---

## What kinds of contributions are welcome

- **New templates** — anonymized `template.json` + `README.md` for the `templates/library/`. This is the easiest, highest-leverage contribution. See [Template contributions](#template-contributions) below.
- **Sub-skill improvements** — bug fixes, better intake questions, sharper Global Rules enforcement, new provider notes, additional resource refs. Open a PR.
- **Bug fixes** — broken MCP calls, wrong action keys, stale provider docs, schema drift. Open a PR; reference the issue or describe the bug in the PR body.
- **Documentation improvements** — clearer examples, tightened READMEs, fixed links. Open a PR.
- **New sub-skills** — requires an issue + discussion first. The routing surface (`/clay` master router + the 19 sub-skill split) is opinionated, and adding a new sub-skill changes routing semantics. Don't open a PR cold — file an issue, agree on the slot, then build.

---

## Template contributions

Templates are the persistence layer of the plugin. Every template lives at:

```
templates/library/<slug>/
├── template.json
└── README.md
```

…and gets one row in `templates/library/INDEX.md`.

### Workflow

1. **Fork** the repo and create a feature branch.
2. **Pick a slug** in kebab-case. Look at existing slugs in `templates/library/INDEX.md` for naming conventions (e.g. `email-waterfall-us-smb`, `signal-monitor-job-change`).
3. **Anonymize from a real workbook.** Strip everything client-specific to `{{PLACEHOLDERS}}`. See [Anonymization checklist](#anonymization-checklist) below — this is non-negotiable.
4. **Write `template.json`** matching the schema in [`skills/clay-template-library/SKILL.md`](skills/clay-template-library/SKILL.md) under the "template.json Schema" heading. Required top-level keys: `schema_version`, `template`, `intake_defaults`, `columns`, `actions`, `verification_checklist`. Required per-column keys: `name`, `type`, `source`, `cost_credits`, `depends_on`, `run_condition`, `config`, `formula_text`, `claygent_prompt`, `notes`.
5. **Write `README.md`** documenting the template: what it does, when to use it, placeholders + examples, required integrations, cost, gotchas, changelog. Use any existing template's README as a starting point.
6. **Update `INDEX.md`** — add one row in the main table (alphabetical by slug) AND add the entry under the right stage section (Hygiene / Build / Score / Activate / Quality & cost / Persistence).
7. **Run the validator** locally — see [Running the validator](#running-the-validator) below.
8. **Open a PR.** Fill out the PR template (`.github/PULL_REQUEST_TEMPLATE.md`) including the anonymization self-attestation.

### Anonymization checklist

Every template contribution must self-attest these in the PR description. The validator catches some of these automatically, but treat the checklist as authoritative:

- [ ] No client / company names anywhere in `template.json` or `README.md`
- [ ] No domain whitelists or email domains (use `{{ICP_DOMAINS}}` or `example.com`)
- [ ] No Slack channel names (use `{{SLACK_CHANNEL}}`)
- [ ] No CRM object / list / record IDs (use `{{CRM_OBJECT_ID}}` or `{{HUBSPOT_LIST_ID}}`)
- [ ] No sender names or sender emails in outbound copy (use `{{SENDER_NAME}}`)
- [ ] No specific competitor names in Claygent prompts (use `{{COMPETITORS}}`)
- [ ] No proprietary scoring weights, suppression lists, or pricing carve-outs
- [ ] All client-specific industries, titles, geos, sizes wrapped as `{{ICP_*}}`

Anonymization rules in full: see "Anonymization Rules (Critical)" in [`skills/clay-template-library/SKILL.md`](skills/clay-template-library/SKILL.md).

If you're submitting a pattern you used at a real engagement, you can reference the engagement in `README.md` under "Known good for" — but only if you've stripped client-specific values from everything else. Naming the client is fine; leaking their domain whitelist is not.

### Running the validator

The validator is stdlib-only Python — no install step.

```bash
# Check every template in templates/library/
python3 scripts/validate-template.py

# Check one template
python3 scripts/validate-template.py templates/library/<your-slug>/
```

The validator:
- Confirms `template.json` + `README.md` both exist
- Validates JSON parses and matches the schema (required keys, slug-matches-dir)
- Greps for likely anonymization leaks (email domains, Slack channels, CRM IDs, known client names)

Schema failures = ERROR (exit 1). Anonymization findings = WARNING (exit 0). Review every warning before merging — most are real, a few are false positives (e.g. legitimate "example" rows in placeholder tables).

Your PR must pass `python3 scripts/validate-template.py` with zero errors. Warnings should be either fixed or explained in the PR description.

---

## Sub-skill improvements, bug fixes, docs

- One concern per PR. A bug fix and a doc rewrite go in two PRs, not one.
- If you're changing intake questions, Global Rules enforcement, or action-registry entries, call it out in the PR body — those are load-bearing.
- For provider docs (`providers/*`), include the date you last verified the behavior. Provider APIs drift.

---

## Code of conduct

This project follows the [Contributor Covenant v2.1](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). Be civil. Disagree on the technical merits.

---

## Questions

Open a GitHub issue. For larger architectural questions (new sub-skill, routing changes, schema changes), an issue is required before the PR.
