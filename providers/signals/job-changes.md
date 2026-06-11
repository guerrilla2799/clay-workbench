# Job Change Signal Sources

Job changes are one of the highest-converting trigger events — alumni from past wins moving to new ICP companies = warm pipeline.

This file covers the 4 main providers and how to combine them.

---

## Provider Overview

| Provider | Best For | Available via | Cost Model |
|----------|----------|---------------|------------|
| Predictleads | Broad job change detection | Clay-managed | 2 credits / match |
| Champify | Customer/champion alumni tracking | Own key (subscription) | 0 in Clay (own seat) |
| The Swarm | Network-graph / warm-intro paths | Own key (subscription) | 0 in Clay (own seat) |
| UserGems | CRM-integrated CRM alumni alerts | Own key (subscription) | 0 in Clay (own seat) |
| LinkedIn-direct | Manual via Sales Nav alerts | Sales Nav seat | 0 (seat) |

## When to Use Each

### Predictleads
- Detecting net-new job changes broadly
- No prior relationship required
- Pay-per-match good for occasional checks

### Champify
- "Customer X moved to Y" alerts
- Champion-tracking — find your former buyers at new accounts
- Best for customer-marketing-driven motions

### The Swarm
- Discover warm-intro paths between prospects and your team
- Identify who in your team knows someone at a target account
- Highest-leverage for founder-led / exec-led outbound

### UserGems
- CRM-native — flags alumni inside HubSpot/Salesforce directly
- Best when CRM is source of truth and you want CRM-integrated alerts
- Easier rollout to SDR / sales teams

## Pattern 4 — Job Change Workflow

```
Step 1: Collect prior contacts
  Source: CRM closed-lost, prior meeting attendees, customer alumni
  
Step 2: Job change detection
  For each prior contact, check current_company against last_known_company
  Providers: Champify (subscription) + Predictleads (per-credit) for coverage
  
Step 3: Filter to ICP-matching new companies
  current_company.industry IN ICP
  current_company.employees >= MIN
  etc.

Step 4: Classify relationship strength
  - Closed-lost AE → "AE re-engages, warm context"
  - Prior meeting attendee → "marketing re-engages"
  - Customer alumni → "founder warm intro"
  - Champion at customer → "highest priority — drop everything"

Step 5: Personalized outbound
  Reference prior relationship + new role
  Claygent prompt that includes prior context
```

## Cost Example

For 5,000 prior contacts checked monthly:

| Method | Cost |
|--------|------|
| Predictleads only | 5,000 × 2 = 10,000 credits ($100) |
| Champify subscription | $200-500/mo (varies) |
| The Swarm subscription | $300-800/mo (varies) |
| UserGems subscription | $300-1000/mo (varies) |

For high-volume tracking, subscriptions win. For < 1,000 contacts/mo, Predictleads pay-per is cheaper.

## Detection Latency

| Source | Detection Latency |
|--------|-------------------|
| Predictleads | ~7 days from public announcement |
| Champify | ~3-7 days |
| The Swarm | ~3-7 days |
| UserGems | ~1-3 days (CRM-real-time after match) |

For time-sensitive motions (e.g., congrats reach-out within 1 week), UserGems wins.

## Notes

- Don't gate on job-change recency too tightly (90 days is good). After 90 days, the warm context decays.
- Job change message MUST reference the prior relationship — generic outbound to a job-changed alum performs worse than no outbound.
- The most underutilized signal in B2B GTM. High-leverage motion.
