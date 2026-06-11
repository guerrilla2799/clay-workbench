# v2.0.0 — Full Clay workflow coverage

v1.0.0 shipped 6 sub-skills covering the obvious build → score → activate path. v2.0.0 adds 10 more so the plugin covers every stage of real Clay work: **hygiene → build → score → activate → quality/cost → persistence**.

16 sub-skills total. Hybrid router + MCP-first execution with manual UI fallback.

---

## What's new

### Hygiene (new stage)

- **`/clay-list-clean`** — Pre-Clay list hygiene. Domain/email/title/geo normalization, dedup, suppression filter. Always run first on raw source lists. Typically cuts downstream burn 30–60%.
- **`/clay-data-hygiene`** — Ongoing CRM-side hygiene. 3 linked tables: `crm_record_health` (rolling freshness), `crm_duplicates` (weekly dedup), `refresh_queue` (prioritized re-enrichment). Distinct from `/clay-list-clean` — this one is recurring, CRM-facing.

### Build (research layer)

- **`/clay-account-research`** — Deep multi-source account briefs. Strategic priorities + news + hiring + leadership + competitive + entry-point hypothesis, per company.
- **`/clay-prospect-research`** — Deep person-level dossiers. POVs + recent activity + role scope + warm path + personalized entry line, per contact. Hands clean output to `/clay-outbound`.

### Score (intent layer)

- **`/clay-buying-signals`** — Composite multi-source intent score. Fuses 6sense + Bombora + web reveal + content engagement + hiring + funding + tech adoption + leadership moves into one time-decayed "now is the moment" score. **Backfill discrimination test (≥3x lift on closed-won vs closed-lost) is mandatory before `auto_run`** — no shipping intent scores that can't prove signal.

### Activate (monitoring layer)

- **`/clay-signal-monitor`** — Recurring single-source trigger watcher. Job changes, hiring, funding, leadership moves, tech adoption, intent surges. Severity classification → Slack/CRM routing. Always-on signal layer for ABM motions.

### Quality & cost (new stage)

- **`/clay-claygent-iterator`** — Structured 5 → 25 → 100 row Claygent prompt iteration loop with scorecard (PASS %, FABRICATED %, credits/row). **Mandatory before scaling any Claygent column** — stops the classic "looked great on 5 rows, hallucinated on 500" failure mode.
- **`/clay-credits`** — Proactive credit forecasting + multi-mix provider cost comparison + workbook ROI ranking with reallocation recommendation. Answers: "Should I add own-key ZoomInfo, or upgrade my Clay tier?" with actual math.
- **`/clay-cost-audit`** — Portfolio-wide 12-check audit across every workbook in the workspace. Global Rules violations + waste + ROI laggards. Executive / engineering / Slack output modes. Complement to single-workbook `/clay-troubleshoot`.

### Persistence (new stage)

- **`/clay-template-library`** — Save / load / list / diff / version / share workbook templates. Anonymization rules baked in (no client data, no credentials, no proprietary scoring weights). Catalog at `templates/library/INDEX.md`.

---

## What changed in the existing 6

No breaking changes. The original 6 sub-skills (`/clay-abm-list`, `/clay-enrich-waterfall`, `/clay-icp-score`, `/clay-outbound`, `/clay-inbound-routing`, `/clay-troubleshoot`) are unchanged in behavior — they now reference the new sub-skills where relevant (e.g., `/clay-outbound` hands off to `/clay-prospect-research` for deep personalization; `/clay-troubleshoot` defers to `/clay-cost-audit` for portfolio-level patterns).

The parent `SKILL.md` routing table and quick-start are reorganized by **stage** (hygiene → build → score → activate → quality/cost → persistence) instead of an alphabetical list, so the right tool surfaces faster.

---

## Plugin manifest

- `version`: `1.0.0` → `2.0.0`
- Per-skill `stage` tags added to every entry in `.claude-plugin/plugin.json` for filterable installs
- Keywords expanded: `buying-signals`, `signal-monitoring`, `account-research`, `prospect-research`, `claygent`, `credit-forecasting`, `data-hygiene`, `cost-audit`, `template-library`

---

## Fixes

- README and `plugin.json` repo URLs were pointing at a non-existent `brandonredlinger` GitHub account from v1.0.0. Now correctly point at `guerrilla2799`. (If you cloned v1 and saw 404s on the manifest's repo link, this is why.)

---

## Upgrade

If you cloned v1:

```bash
cd ~/.claude/claudecodeskills/clay-workbench
git pull
```

Then re-run the install snippet from the README to register the 10 new slash commands in `~/.claude/commands/`:

```bash
SKILLS=(
  clay-list-clean clay-data-hygiene
  clay-account-research clay-prospect-research
  clay-buying-signals
  clay-signal-monitor
  clay-claygent-iterator clay-credits clay-cost-audit
  clay-template-library
)

for skill in "${SKILLS[@]}"; do
  cat > ~/.claude/commands/${skill}.md <<EOF
---
allowed-tools: Read, Write, Edit, WebSearch, WebFetch, AskUserQuestion, Glob, Grep, Bash
description: clay-workbench — ${skill}
---

\$ARGUMENTS

See ~/.claude/claudecodeskills/clay-workbench/skills/${skill}/SKILL.md for full instructions.
EOF
done
```

Restart Claude Code. All 16 sub-skills should now resolve.

---

## Known polish items still open

- Social preview image not yet uploaded (manual GitHub Settings step).

## Post-release follow-ups (landed after v2.0.0 tag)

- ✅ `resources/global-rules.md` now cross-references all 10 new sub-skills under each of the 8 rules.
- ✅ `templates/library/` seeded with the 10 bootstrap templates (each with `template.json` + `README.md`) plus a stage-grouped `INDEX.md` catalog.

---

**Full diff:** [`531b88c...6c29f7f`](https://github.com/guerrilla2799/clay-workbench/compare/531b88c...6c29f7f)
