# Enrichment Match-Rate Benchmarks

Expected match rates per provider and per waterfall pattern. Use as a yardstick when validating sample runs — if actuals lag benchmarks by >15%, route to `/clay-troubleshoot`.

Sources: forma-norden's benchmark file + Clay community-shared empirics + Brandon's observed match rates across Vantage, Obin, Dodge.

---

## Email Discovery — Single Provider

| Provider | Match Rate | Best For | Worst For |
|----------|-----------|----------|-----------|
| Apollo (Clay-managed) | 40% | SMB, mid-market US | EU, enterprise, EU-headquartered |
| Apollo (own key) | 45% | Same as above | Same |
| Findymail | 60% | B2B US, mid-market | Solopreneurs, agencies |
| Datagma | 65% | EMEA, EU buyers, technical roles | US-heavy lists |
| Hunter | 55% | Domain-based deterministic | Personal-email-heavy lists |
| Dropcontact | 70% | High-quality premium | Budget-constrained runs |
| Anymailfinder | 50% | Solid waterfall middle | Edge cases |
| Prospeo | 55% | Decent fallback | — |
| Icypeas | 45% | Budget budget | Match rate sensitive lists |

## Email Discovery — Waterfall Patterns

| Pattern | Sequence | Match Rate | Per-Row Cost (Graceful Exit) |
|---------|----------|-----------|------------------------------|
| Budget | Apollo → Icypeas | 60% | ~2 credits |
| Standard | Apollo → Findymail → Datagma | 80% | ~4 credits |
| Premium | Apollo → Findymail → Datagma → Dropcontact | 90% | ~6 credits |
| EU-Optimized | Apollo → Datagma → Dropcontact | 85% | ~5 credits |
| Own-Key Heavy | Apollo (own) → Findymail → Datagma | 80% | ~3 credits |

**Notes**:
- Graceful exit assumed (stops on first valid match).
- Verification adds ~1 credit per matched email (ZeroBounce).
- Sub-60% actuals on Standard waterfall = input data quality issue (see `/clay-troubleshoot`).

---

## Email Verification (After Discovery)

| Verifier | Valid Rate | Catch-All Rate | False Negative Rate |
|----------|-----------|----------------|---------------------|
| ZeroBounce | 65% | 25% | ~5% |
| NeverBounce | 65% | 25% | ~5% |
| MillionVerifier | 60% | 30% | ~8% |
| Bouncer | 70% | 22% | ~3% |
| Kickbox | 70% | 22% | ~3% |

**Reading the catch-all rate**: catch-all emails are domain-level accepting. They send and bounce inconsistently. Real-world deliverability is roughly 50% for catch-all.

**Production rule**: only push `email_verified IN ["valid", "accept_all_high"]` to sequencer. Drop the rest.

---

## Phone Discovery — Single Provider

| Provider | Mobile Rate | Direct Rate | HQ-Only Rate | Best For |
|----------|------------|-------------|--------------|----------|
| Apollo (Clay-managed) | 25% | 30% | 20% | Quick budget pass |
| Apollo (own key) | 30% | 35% | 20% | Same with seat |
| Datagma | 35% | 35% | 15% | EMEA |
| ContactOut | 40% | 35% | 10% | Premium |
| RocketReach | 30% | 30% | 20% | Mid-tier |
| Cognism (own key) | 50% | 40% | 5% | Best enterprise |

## Phone Waterfall Patterns

| Pattern | Sequence | Total Match Rate | Per-Row Cost |
|---------|----------|------------------|--------------|
| Budget | Apollo | 25% | ~1 credit |
| Standard | Apollo → Datagma | 35% | ~2 credits |
| Premium | Apollo → Datagma → ContactOut | 50% | ~5 credits |
| Enterprise own-key | Cognism (own) → Apollo | 60% | ~1 credit |

**Important**: phone waterfalls top out around 60% match. Set expectations explicitly. Don't promise "find a phone for every contact."

---

## LinkedIn URL Discovery

| Source | Match Rate | Cost |
|--------|-----------|------|
| Apollo | 65% | 1 credit |
| LinkedIn Sales Nav (Clay-managed) | 95% | 2 credits |
| Manual Claygent search | 90% | 5–10 credits |
| Returned in contact-finding step | 70-90% | 0 (included) |

**Recommended**: rely on contact-finding to return LinkedIn URL. If LinkedIn URL is critical for sequencing (LinkedIn DM steps), use Sales Nav.

---

## Company Enrichment

| Data Point | Provider | Match Rate | Cost |
|------------|----------|-----------|------|
| Industry | Clay native | 92% | 1 |
| Employee count | Clay native | 88% | 1 |
| Employee count (verified to LinkedIn) | LinkedIn Sales Nav | 99% | 2 |
| HQ country | Clay native | 95% | 1 |
| Revenue range | People Data Labs | 70% | 2 |
| Revenue range | Clay native | 50% | 1 |
| Funding stage | Predictleads | 80% (for ICPs with funding) | 2 |
| Tech stack (lite) | Wappalyzer | 75% | 1 |
| Tech stack (full) | BuiltWith | 90% | 5 |

---

## Trigger / Signal Match Rates

| Signal Type | Provider | Match Rate (of ICP) | Recency Confidence |
|-------------|----------|---------------------|---------------------|
| Funding event | Predictleads | 15-25% | High (date precise) |
| Hiring (multi-req) | Predictleads | 30-40% | Medium (real-time but noisy) |
| Job change | Predictleads | 20-30% / quarter | High |
| Job change | The Swarm | 20-30% / quarter | High |
| Job change | Champify | 15-25% / quarter | High |
| Tech stack adoption | BuiltWith / Wappalyzer | 10-15% (vs baseline) | Medium |
| Executive change | Predictleads | 10-20% / year | High |

**Reading**: triggers are inherently low-percentage. Don't gate too tightly on trigger_required — you'll lose 75%+ of otherwise-good ICP. Use trigger as a **scoring boost**, not a hard gate, unless the motion explicitly requires fresh trigger.

---

## Validation Thresholds (Lag-vs-Benchmark)

| Metric | Benchmark | Yellow (Diagnose) | Red (Troubleshoot Immediately) |
|--------|-----------|------------------|--------------------------------|
| Email waterfall Standard | 80% | 70-79% | <60% |
| Email verified | 65% | 55-64% | <50% |
| Phone Standard | 35% | 25-34% | <20% |
| Company enrichment success | 88% | 80-87% | <75% |
| Trigger event match | 20-30% | 15-19% | <10% |

When Red: route to `/clay-troubleshoot` to diagnose:
- Input data quality (most common — bad domains, name typos)
- Provider mix for the ICP
- Run condition / gate misconfig
- Provider API health (rate limit, key expiry)

---

## Cost-Per-Outcome Yardsticks

For pre-flight sanity check, expect:

| Outcome | Cost Range (Credits) | Cost Range ($ at $0.01/credit) |
|---------|---------------------|------------------------------|
| 1 verified email from cold name | 4-7 | $0.04-$0.07 |
| 1 verified email + mobile phone | 7-12 | $0.07-$0.12 |
| 1 enriched account (firmographics + trigger) | 6-10 | $0.06-$0.10 |
| 1 fully prepared outbound contact | 12-18 | $0.12-$0.18 |
| 1 deep account brief with Claygent | 15-25 | $0.15-$0.25 |

If actuals are >2× these ranges, audit for:
- Missing two-pass gate
- Verification running on already-verified emails
- Claygent crawling too many sources
- Provider waterfall not graceful-exiting

---

## Industry-Specific Notes

| Industry | Match-Rate Adjustments |
|----------|------------------------|
| Healthcare / Hospitals | -10% across the board; HIPAA-driven public data restrictions |
| Government / Defense | -20% on email; .gov domains often catch-all |
| Education | -10% on phone; +10% on email (.edu deterministic) |
| FSI / Banking | -15% on phone; +5% on titles (more public) |
| EU companies | Use EU-optimized waterfall; expect 5-10% lower than US benchmarks |
| Stealth startups | -30% across the board; not enough public footprint |

---

## When to Stop Trying

There's a real "you can't find them" floor. If you've run:
- Premium waterfall (Apollo → Findymail → Datagma → Dropcontact)
- Sales Nav own-key
- Manual Claygent search

…and still no email, the email genuinely isn't findable from public sources. Don't keep stacking providers — the next +5% match rate costs +400% credits.

Better: route those rows to LinkedIn-only outreach, hand to AE for hand-research, or drop entirely.
