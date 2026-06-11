# Dropcontact

**Type**: Premium email discovery + verification (GDPR-compliant)
**Available via**: Clay-managed
**Best for**: Premium waterfall step; GDPR-sensitive lists; high-confidence-required campaigns

---

## What It Returns

| Data Point | Coverage | Confidence |
|------------|----------|------------|
| Email | 70% standalone | Very high |
| Email verification | Built-in | Very high |
| LinkedIn URL | 75% | High |

## Cost

| Operation | Credits |
|-----------|---------|
| Find email + verify | 3 |
| Find LinkedIn URL | included |

## When to Use

- ✅ Final step in premium waterfall (highest match rate per dollar after others miss)
- ✅ GDPR-sensitive lists — EU compliance built-in
- ✅ High-stakes outbound where false-positive emails would damage domain reputation
- ✅ EU contacts

## When NOT to Use

- ❌ As first step (3 credits per row vs Apollo at 1)
- ❌ Budget-constrained runs (use Standard waterfall, not Premium)
- ❌ Volume runs where match rate >85% isn't required

## Waterfall Position

**Premium**: Apollo → Findymail → Datagma → **Dropcontact**
**EU-optimized**: Apollo → Datagma → **Dropcontact**

Run Condition: `email_datagma IS NULL` (or earlier provider null)

## Common Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Cost spike when added to waterfall | Other providers under-performing | First diagnose upstream — Dropcontact shouldn't be carrying the load |

## Notes

- Dropcontact's verification is among the strictest — emails returned as valid have very low bounce rate (~1-2%).
- GDPR-friendly: doesn't store enriched data, returns results live per query.
- Use as the "safety net" final step — most rows shouldn't reach it if upstream is configured right.
