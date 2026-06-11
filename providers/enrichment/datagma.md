# Datagma

**Type**: Email + phone + LinkedIn enrichment
**Available via**: Clay-managed
**Best for**: EMEA / EU contacts; technical roles; mobile phone discovery

---

## What It Returns

| Data Point | Coverage | Confidence |
|------------|----------|------------|
| Email | 65% (EU 70%, US 60%) | High |
| Mobile phone | 35% | Medium |
| LinkedIn URL | 70% | High |

## Cost

| Operation | Credits |
|-----------|---------|
| Find email | 2 |
| Find phone | 2 |
| Find LinkedIn URL | 1 |

## When to Use

- ✅ EU / UK / EMEA contact lists (strongest provider for these geos)
- ✅ Third step in standard waterfall (after Apollo + Findymail miss)
- ✅ Technical / engineering roles (good coverage)
- ✅ Mobile phone discovery
- ✅ When you have French / German market focus

## When NOT to Use

- ❌ As first step (Apollo cheaper)
- ❌ US-only lists where Findymail performs better
- ❌ APAC contacts (limited coverage)

## Waterfall Position

**Standard**: Apollo → Findymail → **Datagma** → Dropcontact
**EU-optimized**: Apollo → **Datagma** → Dropcontact

Run Condition: `email_findymail IS NULL` (standard) OR `email_apollo IS NULL` (EU)

## Common Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Phone returns hq number, not mobile | Datagma falls back to hq when mobile not found | Filter `phone_type = "mobile"` if mobile is the requirement |
| Match rate < 50% on US lists | Wrong geo positioning in waterfall | Use Findymail before Datagma for US |

## Notes

- Strongest in France, Germany, Benelux. Solid in UK and Spain.
- Good provider for technical-persona campaigns — engineers and product folks well-indexed.
- Mobile phone match rate is the highest single-source for EMEA.
