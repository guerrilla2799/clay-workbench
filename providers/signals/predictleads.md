# Predictleads

**Type**: Trigger event signals — funding, hiring, job changes, executive moves
**Available via**: Clay-managed OR own key
**Best for**: Trigger-event ABM motions; signal-driven outbound

---

## Signals Available

| Signal | Detection | Latency |
|--------|-----------|---------|
| Funding events | Press release + Crunchbase + SEC scraping | Same day |
| Hiring (open reqs) | Job board scraping | Daily refresh |
| Job changes | LinkedIn + alumni network analysis | Weekly refresh |
| Executive changes | News + LinkedIn announcements | 1-3 days |
| Tech adoption | Web crawl + integration scanning | Weekly refresh |

## Cost

| Operation | Credits |
|-----------|---------|
| Check company for any signal | 2 |
| Pull last N signals for company | 2 (returns up to 10 recent) |
| Job change for specific person | 2 |

## When to Use

- ✅ Trigger-driven ABM Pattern 1
- ✅ Job change reach-out Pattern 4
- ✅ Account refresh Pattern 3 (recurring trigger check)
- ✅ Real-time signal alerts (via webhook from Predictleads)

## When NOT to Use

- ❌ As cold ICP filter (signals are noisy without ICP fit)
- ❌ Without recency window (90-day default)
- ❌ Solo signal source (combine with Champify or The Swarm for job changes)

## Configuration

```
Column: trigger_event
Provider: Predictleads
Input: {company_domain}
Returns: trigger_event_type, trigger_event_date, trigger_event_url, trigger_event_description
Run Condition: pass_1_qualified = TRUE
```

## Trigger Classification

Always pair with Claygent classifier (`ai-prompt-templates.md` Template 5) to filter:
- `actionable` → use in gates/scoring
- `neutral` → ignore
- `noise` → drop

Without classifier, expect 30-40% false positive rate.

## Common Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Many triggers but low conversion | Triggers not classified — including noise | Add Claygent classifier |
| Funding triggers showing Seed for known Series A companies | Predictleads scraped outdated source | Compare against Crunchbase Pro for verification |
| Hiring trigger fires on single open req | Too broad | Require min_open_reqs >= 3 in formula |

## Job Change Coverage Comparison

| Provider | Coverage | Refresh Cadence | Best For |
|----------|----------|-----------------|----------|
| Predictleads | Broad | Weekly | General job change detection |
| Champify | Customer alumni focus | Weekly | Customer/champion tracking |
| The Swarm | Network-graph focus | Weekly | Warm intro path discovery |
| UserGems | CRM-integrated focus | Weekly | CRM-linked alumni alerts |

For comprehensive job change coverage, use 2 of these in parallel (Predictleads + Champify is a common combo).
