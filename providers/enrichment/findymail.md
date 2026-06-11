# Findymail

**Type**: Email discovery + verification
**Available via**: Clay-managed
**Best for**: B2B mid-market US email discovery; reliable second step in waterfalls

---

## What It Returns

| Data Point | Coverage | Confidence |
|------------|----------|------------|
| Email | 60% standalone | Medium-high |
| Email status | Yes (deliverable / catch-all / risky) | High |

## Cost

| Operation | Credits |
|-----------|---------|
| Find email | 2 |
| Verify email | included |

## When to Use

- ✅ Second step in email waterfall after Apollo
- ✅ B2B mid-market US lists (sweet spot)
- ✅ When Apollo returned "unknown" or low-confidence

## When NOT to Use

- ❌ EU lists — use Datagma instead
- ❌ Personal-email-heavy lists
- ❌ As only email source (single-provider match rate caps at 60%)
- ❌ Already-verified Apollo results (wasted spend)

## Waterfall Position

Apollo → **Findymail** → Datagma → Dropcontact

Run Condition: `email_apollo IS NULL`

## Common Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Returns valid-flagged email that bounces | Catch-all domain | Add post-verification with ZeroBounce; threshold "valid + accept_all_high" only |
| Low match on agencies / freelancers | Findymail under-indexes | Skip these rows or route to LinkedIn-only |

## Notes

- Findymail's catch-all detection is strict — emails flagged "catch_all" often deliver fine. Adjust deliverability gate accordingly.
- Match rate on stealth-mode or pre-launch startups is near zero. Reroute or drop.
