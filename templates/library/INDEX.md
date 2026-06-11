# Template Library Index

Registry of all anonymized Clay workbook templates in `templates/library/`. Maintained alphabetical by slug. Every entry below points to a `<slug>/` directory containing `template.json` + `README.md`.

To load any template into a new client engagement, use `/clay-template-library load <slug>` and fill the `{{PLACEHOLDERS}}` documented in the README.

| Slug | Name | Use Case | Motion | Cost/Row | Match Rate | Version | Last Updated |
|------|------|----------|--------|----------|-----------|---------|--------------|
| [abm-account-keyed-tier-1](abm-account-keyed-tier-1/) | ABM Tier 1 — Account-Keyed with Triggers | abm-list | slg | ~14 credits | 25% pass_1, 5–10% T1 | 1.0 | 2026-06-10 |
| [account-research-tier-1-brief](account-research-tier-1-brief/) | Account Research — Tier 1 Executive Brief | research | slg | 40–70 credits | 95% firmographic, 80% usable priorities | 1.0 | 2026-06-10 |
| [email-waterfall-eu](email-waterfall-eu/) | Email Waterfall — EU | enrichment | slg | 5–7 credits | 70–80% EU | 1.0 | 2026-06-10 |
| [email-waterfall-us-smb](email-waterfall-us-smb/) | Email Waterfall — US SMB | enrichment | slg | 4–6 credits | 80–90% US SMB | 1.0 | 2026-06-10 |
| [inbound-router-demo-form](inbound-router-demo-form/) | Inbound Demo-Form Enricher + Router | inbound | hybrid | ~8 credits | 85% pass_1, 10–15% Hot | 1.0 | 2026-06-10 |
| [outbound-3-step-cadence-cold](outbound-3-step-cadence-cold/) | Outbound — 3-Step Cold Cadence (Email + LinkedIn) | outbound | slg | 10–12 credits | 50–70% Sending Gate pass | 1.0 | 2026-06-10 |
| [outbound-3-step-cadence-warm](outbound-3-step-cadence-warm/) | Outbound — 3-Step Warm/Triggered Cadence | outbound | hybrid | 10–14 credits | 70–85% Sending Gate pass | 1.0 | 2026-06-10 |
| [prospect-research-champion-brief](prospect-research-champion-brief/) | Prospect Research — Champion Brief | research | slg | 45–75 credits | 95% enrichment, 70% usable entry line | 1.0 | 2026-06-10 |
| [signal-monitor-hiring-posture](signal-monitor-hiring-posture/) | Signal Monitor — Hiring Posture Watcher | monitoring | hybrid | 3–7 credits/cycle | 90% Predictleads, 70% Claygent fallback | 1.0 | 2026-06-10 |
| [signal-monitor-job-change](signal-monitor-job-change/) | Signal Monitor — Job Change Watcher | monitoring | hybrid | 2–5 credits/cycle | 85% Champify (14d), 60% Claygent fallback | 1.0 | 2026-06-10 |

---

## By Workflow Stage

### Hygiene
*(No library templates yet — pre-Clay hygiene is more workbook-local than reusable. Use `/clay-list-clean` for one-off list cleanup; `/clay-data-hygiene` for the ongoing 3-table CRM hygiene pattern.)*

### Build
- [abm-account-keyed-tier-1](abm-account-keyed-tier-1/) — account-keyed ABM list with triggers
- [account-research-tier-1-brief](account-research-tier-1-brief/) — multi-source Claygent account brief
- [prospect-research-champion-brief](prospect-research-champion-brief/) — person-level deep dossier
- [email-waterfall-us-smb](email-waterfall-us-smb/) — US-optimized email waterfall
- [email-waterfall-eu](email-waterfall-eu/) — EU-optimized email waterfall

### Score
*(No library templates yet — ICP scoring rubrics are usually too client-specific to template anonymously. Use `/clay-icp-score` to compose per-client. `/clay-buying-signals` composite intent: same — anonymize only after first production run with backfill discrimination ≥3x lift.)*

### Activate
- [inbound-router-demo-form](inbound-router-demo-form/) — real-time webhook → enrich → route → Slack
- [outbound-3-step-cadence-cold](outbound-3-step-cadence-cold/) — cold cadence with strict Sending Gate
- [outbound-3-step-cadence-warm](outbound-3-step-cadence-warm/) — signal-driven warm cadence
- [signal-monitor-job-change](signal-monitor-job-change/) — recurring job-change watcher
- [signal-monitor-hiring-posture](signal-monitor-hiring-posture/) — recurring hiring-trigger watcher

### Quality & cost
*(No library templates — these are diagnostic / measurement workflows, not workbook artifacts. Use `/clay-claygent-iterator`, `/clay-credits`, `/clay-cost-audit`, `/clay-troubleshoot` as runtime tools.)*

### Persistence
*(This catalog IS the persistence layer. Use `/clay-template-library` to save, load, version, diff, share.)*

---

## How templates relate

```
abm-account-keyed-tier-1 ──┬─► account-research-tier-1-brief
                           │
                           ├─► email-waterfall-us-smb / email-waterfall-eu
                           │     │
                           │     └─► outbound-3-step-cadence-cold
                           │
                           └─► prospect-research-champion-brief
                                 │
                                 └─► outbound-3-step-cadence-cold (with personalized_entry_line input)

signal-monitor-job-change ────────► outbound-3-step-cadence-warm
signal-monitor-hiring-posture ────► outbound-3-step-cadence-warm

inbound-router-demo-form (standalone)
```

---

## Anonymization status

All v1.0 templates have been scrubbed of:
- Specific client names, domains, brand language
- Specific Slack channel names, CRM list IDs, SDR user IDs (replaced with `{{PLACEHOLDERS}}`)
- Specific sender names or sender LinkedIn URLs
- Proprietary scoring weights or rubrics
- Specific suppression sources or competitor names in Claygent prompts

Templates are safe to share publicly via the repo. Per-engagement values are injected at LOAD time via README placeholder map.

---

## Adding a new template

1. Build the workbook for a real client; verify it on at least one production run.
2. Run `/clay-template-library save <kebab-case-slug>` with the workbook in scope.
3. The SAVE flow applies anonymization rules → writes `template.json` + `README.md` → appends an entry to this INDEX.md.
4. Commit to the repo if you want it shared. (Default behavior asks before committing.)

See `clay-workbench/skills/clay-template-library/SKILL.md` for the full SAVE / LOAD / DIFF / VERSION / SHARE flow.
