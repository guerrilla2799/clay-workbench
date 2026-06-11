# Ocean.io

**Type**: Lookalike account discovery + ICP database
**Available via**: Clay-managed OR own key
**Best for**: Expansion lists; finding lookalikes of your best customers

---

## What It Returns

| Data Point | Coverage | Confidence |
|------------|----------|------------|
| Lookalike accounts | 80% (when given 10+ seed customers) | High |
| Firmographics | 85% | High |
| Tech stack signals | 70% | Medium-high |
| Hiring + growth signals | 65% | Medium |

## Cost

| Operation | Credits |
|-----------|---------|
| Lookalike search (per account returned) | 3 |

## When to Use

- ✅ Building expansion lists — give Ocean.io 10–20 best customers, get back 500-2000 lookalikes
- ✅ Net-new market exploration
- ✅ Identifying white space accounts similar to closed-won
- ✅ Combined with `/clay-abm-list` Pattern 1

## When NOT to Use

- ❌ Without seed customer list (lookalike needs anchors)
- ❌ As cold first-touch source (use Apollo / Sales Nav)
- ❌ Tiny ICP segments (lookalike works best on broader patterns)

## Workflow

```
1. Export 15-30 closed-won customer domains from CRM
2. Upload to Ocean.io as seed list
3. Run lookalike search
4. Export results to Clay
5. Run /clay-abm-list against Ocean.io output for tier classification
```

## Notes

- Ocean.io's algorithm weights tech stack + hiring patterns + revenue range.
- Most useful when you have 15+ ideal customers as seed. 10 minimum.
- Common pitfall: seed list contaminated with non-ideal "we got lucky" customers. Curate carefully — first-pass filter the seed list to only the customers you want more of.
