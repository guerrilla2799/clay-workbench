# Clearbit

**Type**: Company + person firmographic enrichment
**Available via**: Clay-managed OR own key (HubSpot bundle)
**Best for**: SMB / mid-market firmographics; HubSpot-native enrichment if you have HubSpot Enterprise

---

## What It Returns

| Data Point | Coverage | Confidence |
|------------|----------|------------|
| Company firmographics | 85% (SMB best) | High |
| Tech stack (high level) | 60% | Medium |
| Person enrichment | 70% | Medium |
| Email validation | Yes | High |

## Cost

| Operation | Clay-Managed | Own Key (HubSpot) |
|-----------|--------------|-------------------|
| Company enrichment | 1-2 credits | 0 |
| Person enrichment | 1-2 credits | 0 |

## When to Use

- ✅ SMB / mid-market lists (sweet spot)
- ✅ HubSpot Enterprise users (Clearbit included — own key = 0 credits)
- ✅ Alternative to Clay native when richness matters

## When NOT to Use

- ❌ Enterprise (PDL has better depth)
- ❌ Without HubSpot Enterprise (Clay-managed cost not better than alternatives)
- ❌ EU contacts (US-skewed coverage)

## Configuration

```
Column: company_data
Provider: Clearbit
Input: {company_domain}
Returns: industry, employee_count, tech_stack_basic, revenue_estimate
```

## Notes

- HubSpot acquired Clearbit; HubSpot Enterprise customers have Clearbit included. Use own key path.
- For non-HubSpot users, often more cost-effective to combine Clay native + PDL than to add Clearbit.
- Tech stack data is high-level only — for full stack detail, use BuiltWith.
