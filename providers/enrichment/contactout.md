# ContactOut

**Type**: Email + phone discovery (premium)
**Available via**: Clay-managed OR own key
**Best for**: Premium phone discovery; LinkedIn-URL-input enrichment

---

## What It Returns

| Data Point | Coverage | Confidence |
|------------|----------|------------|
| Email | 75% | High |
| Mobile phone | 40% | High |
| Direct phone | 35% | High |
| LinkedIn-based enrichment | 80% | High |

## Cost

| Operation | Credits |
|-----------|---------|
| Find email | 2 |
| Find phone | 4 |

## When to Use

- ✅ Premium phone waterfall (third step)
- ✅ When you have LinkedIn URL as input (ContactOut's LinkedIn integration is strong)
- ✅ Enterprise targets where Apollo / Datagma under-cover

## When NOT to Use

- ❌ As budget first step (4 credits per phone vs Apollo at 1)
- ❌ Without LinkedIn URL — input quality matters
- ❌ Email-only campaigns (other providers cheaper)

## Waterfall Position

**Premium Phone**: Apollo → Datagma → **ContactOut**

Run Condition: `phone_datagma IS NULL`

## Notes

- ContactOut's strength: LinkedIn URL input. If you already have LinkedIn URL, ContactOut over-performs other providers.
- Phone match rates are the highest in Clay's prebuilt waterfalls — pay premium for it.
- Premium tier: useful for T1 ABM where every contact matters.
