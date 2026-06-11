# Clay Credit Cost Table

Reference costs per provider, per data point. Use for pre-flight estimates. Costs are Clay-managed credits unless noted "own key."

⚠️ Clay updates pricing periodically. Verify with `mcp__claude_ai_Clay__get-credits-available` and Clay's pricing page before high-volume runs.

---

## Company Enrichment

| Provider | Data Point | Credits | Notes |
|----------|------------|---------|-------|
| Clay native | Domain → company match | 0 | Free for basic match |
| Clay native | Industry, employee count, HQ | 1 | Bundled in basic enrichment |
| Clay native | Revenue range | 1 | Mid-confidence |
| Clearbit | Full company profile | 1–2 | Best for SMB / mid-market |
| Apollo (Clay-managed) | Company firmographics | 1 | Cheapest waterfall starting point |
| Apollo (own key) | Company firmographics | 0 | Uses your Apollo credits |
| People Data Labs | Firmographics + funding | 2 | Best for enterprise + funding data |
| Ocean.io | Lookalike accounts | 3 | When building expansion lists |
| BuiltWith | Tech stack | 5 | Expensive — use only when stack is part of ICP |
| Wappalyzer (Clay-managed) | Tech stack lite | 1 | Cheaper but less complete |
| Predictleads | Funding + hiring signals | 2 | Trigger event sourcing |

## Contact Finding

| Provider | Data Point | Credits | Match Rate (~) |
|----------|------------|---------|----------------|
| Apollo (Clay-managed) | Find contacts at company | 1 per contact | 70% |
| Apollo (own key) | Find contacts at company | 0 | Uses Apollo seats |
| LinkedIn Sales Nav (Clay-managed) | Person search | 2 | 85% — best quality |
| RocketReach | Person search | 2 | 75% |
| People Data Labs | Person search | 2 | 80% |
| ContactOut | Person search | 2 | 75% |

## Email Discovery (Waterfall Step)

| Provider | Credits | Match Rate (~) | Notes |
|----------|---------|----------------|-------|
| Apollo (Clay-managed) | 1 | 40% | Cheapest first step |
| Findymail | 2 | 60% | Strong B2B match |
| Hunter | 2 | 55% | Domain-based, deterministic |
| Datagma | 2 | 65% | Strong for EMEA |
| Prospeo | 2 | 55% | Good fallback |
| Anymailfinder | 2 | 50% | Solid waterfall middle |
| Dropcontact | 3 | 70% | Best paid quality |
| Icypeas | 1 | 45% | Budget option |

**Recommended waterfall**: Apollo → Findymail → Datagma → Dropcontact. Match rate stacks to ~85%.

## Email Verification

| Provider | Credits | Notes |
|----------|---------|-------|
| ZeroBounce | 1 | Industry standard |
| NeverBounce | 1 | Comparable |
| MillionVerifier | 1 | Cheaper bulk |
| Bouncer | 1 | EU-friendly |

**Only run on emails from waterfall — don't verify Apollo "verified" status emails, they're pre-validated.**

## Phone Discovery

| Provider | Credits | Match Rate (~) | Notes |
|----------|---------|----------------|-------|
| Apollo (Clay-managed) | 1 | 25% | Direct numbers only |
| Datagma | 2 | 35% | Mobile-friendly |
| ContactOut | 4 | 40% | Premium |
| Cognism (own key) | 0 | 50% | Best enterprise — requires seat |

**Waterfall match rate maxes at 40–60% — set expectations.**

## LinkedIn URL Discovery

| Provider | Credits | Match Rate (~) |
|----------|---------|----------------|
| Apollo | 1 | 65% |
| LinkedIn Sales Nav | 2 | 95% |
| Manual via Claygent | 5–10 | 90% |

## AI Columns (Claygent)

| Use Case | Credits | Notes |
|----------|---------|-------|
| Simple research (1 source) | 3 | Single web page summarization |
| Multi-source research | 5–10 | Crawls multiple URLs |
| Job posting analysis | 5 | Reads job pages, extracts signals |
| Personalized first line | 3 | Single-input generation |
| Deep account research | 10–15 | Full company brief |

**Claygent costs scale with sources crawled. Set explicit max-source limit in prompt.**

## Trigger / Signal Sources

| Source | Credits | Cadence |
|--------|---------|---------|
| Predictleads — funding | 2 per match | Daily |
| Predictleads — hiring | 2 per match | Daily |
| Predictleads — job changes | 2 per match | Weekly |
| Champify | Own key (subscription) | Daily |
| UserGems | Own key (subscription) | Daily |
| Common Room | Own key (subscription) | Daily |
| The Swarm (job changes) | Own key (subscription) | Daily |

## CRM / Sequencer Sync

| Destination | Credits | Notes |
|-------------|---------|-------|
| HubSpot — write | 0 | Free via integration |
| Salesforce — write | 0 | Free via integration |
| SalesLoft — push | 0 | Free via integration |
| Outreach — push | 0 | Free via integration |
| 11x AI SDR — push | 0 | Free via integration |
| Smartlead — push | 0 | Free |
| Instantly — push | 0 | Free |
| Slack — notify | 0 | Free |
| Webhook — generic | 0 | Free |

---

## Pre-Flight Estimator

For each waterfall in a workbook, estimate credits per row as the sum of:

```
credits_per_row = company_enrichment + contact_finding + email_waterfall + verification + phone_waterfall + ai_columns
```

**Worked example — standard ABM contact build:**

| Step | Credit Cost |
|------|-------------|
| Company enrichment (Clay native) | 1 |
| Find 2 contacts at company (Apollo) | 2 |
| Email waterfall (Apollo + Findymail) | ~3 (graceful exit) |
| Email verification (ZeroBounce) | 1 |
| LinkedIn URL (Apollo) | 1 |
| AI personalized first line (Claygent) | 3 |
| **Total per contact** | **~11 credits** |

**1,000-contact run** = ~11,000 credits ≈ $110 at $0.01/credit tier (varies).

---

## Cost-Optimization Rules

1. **Apply ICP gate before any paid column.** Default condition: `gate_qualified = TRUE`.
2. **Cap waterfalls at "graceful exit"** — if Apollo returns email + status=verified, skip subsequent waterfall steps for that row. Configure in Clay's waterfall action.
3. **Bulk over single.** Run enrichments in batches of 100+ to amortize subroutine setup.
4. **Cache aggressively.** If a company was enriched in the last 30 days, skip re-enrichment unless trigger event detected.
5. **Use free Apollo where possible.** Free Apollo company + contact data covers 60–70% of B2B SMB.

See `clay-troubleshoot/SKILL.md` for the "shrink burn rate by 40%" diagnostic.

---

## When to Use Own API Key vs Clay-Managed

| Scenario | Recommendation |
|----------|---------------|
| You have existing Apollo / ZoomInfo / Cognism seat | Use own key |
| Sub-1K rows/month | Clay-managed (no setup overhead) |
| 1K–10K rows/month | Mix — Clay-managed for spot, own key for bulk |
| 10K+ rows/month | Own key for primary, Clay-managed as fallback |
| Compliance-sensitive (EU GDPR, finance) | Own key to keep contracts under user control |
