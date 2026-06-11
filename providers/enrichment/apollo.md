# Apollo

**Type**: Enrichment provider — company + contact + email + phone + LinkedIn URL
**Available via**: Clay-managed OR own API key
**Best for**: Budget-friendly first step in waterfalls; broad SMB + mid-market coverage

---

## What It Returns

| Data Point | Coverage | Confidence |
|------------|----------|------------|
| Company firmographics | 85% (B2B) | High |
| Contact list at company | 70% (B2B mid-market) | Medium-high |
| Email | 40% (Clay-managed) / 45% (own key) | Medium |
| Email verified status | Yes (Apollo-flagged) | High when "verified" |
| Mobile phone | 25% | Medium |
| Direct phone | 30% | Medium |
| LinkedIn URL | 65% | High |

## Cost

| Operation | Clay-Managed | Own Key |
|-----------|--------------|---------|
| Find company by domain | 1 credit | 0 (own seat) |
| Find contacts at company | 1 credit per contact | 0 |
| Find email | 1 credit | 0 |
| Find phone | 1 credit | 0 |
| Find LinkedIn URL | 1 credit | 0 |

## When to Use

- ✅ First step in every email waterfall (cheapest)
- ✅ Bulk contact finding for ABM lists
- ✅ Quick firmographic enrichment at scale
- ✅ When you have an Apollo seat (use own key — saves Clay credits)

## When NOT to Use

- ❌ EU-heavy lists — Apollo under-indexes vs Datagma/Dropcontact
- ❌ Enterprise / Fortune 500 — coverage gaps; supplement with Sales Nav
- ❌ Stealth startups — not in Apollo database
- ❌ As only email source — match rate too low alone (use in waterfall)

## Configuration Notes

- **Clay-managed**: works out-of-box, debits Clay credits.
- **Own key**: connect in Settings → Integrations → Apollo → paste API key. Credits hit Apollo seat, not Clay account.
- **Email verified flag**: Apollo marks emails "verified" if they passed Apollo's own validation. Trust these — don't re-verify with ZeroBounce (wasted credit).

## Common Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| 0% match rate on a list | Domains malformed (www., trailing slash) | Normalize domains first |
| Email returns "unknown" | Company too small / pre-Apollo coverage | Move to next waterfall step |
| Rate limit errors | Hit Apollo's per-minute cap | Throttle or upgrade tier |

## Waterfall Position

**Standard**: Apollo → Findymail → Datagma → Dropcontact
**EU-optimized**: Apollo → Datagma → Dropcontact
**Budget**: Apollo → Icypeas

Always position Apollo first — cheapest first step.
