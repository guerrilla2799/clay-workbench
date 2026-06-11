# Hunter

**Type**: Email discovery + verification (domain-based)
**Available via**: Clay-managed OR own key
**Best for**: Deterministic domain-pattern email construction (e.g., firstname.lastname@company.com)

---

## What It Returns

| Data Point | Coverage | Confidence |
|------------|----------|------------|
| Email | 55% standalone | Medium-high (when found) |
| Email verification | Built-in | High |
| Domain pattern hint | Yes (e.g., "{first}.{last}@") | High |

## Cost

| Operation | Credits |
|-----------|---------|
| Find email | 2 |
| Verify | included |

## When to Use

- ✅ Alternative second-step waterfall provider (when Findymail under-performs)
- ✅ Domain-pattern-based email construction (deterministic)
- ✅ When you have the domain but no person LinkedIn

## When NOT to Use

- ❌ Personal-email-heavy lists
- ❌ Companies with non-standard email patterns (e.g., randomized usernames)
- ❌ When Findymail is producing 65%+ already (no marginal gain)

## Waterfall Position

**Alternative Standard**: Apollo → **Hunter** → Datagma → Dropcontact

Run Condition: `email_apollo IS NULL`

## Common Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Match rate < 40% on a list | Companies don't use predictable email patterns | Move to Findymail or Datagma |
| Returns hot patterns but no verified email | Hunter pattern guess + person not in database | Combine pattern with manual construction → ZeroBounce verify |

## Notes

- Hunter's strength is deterministic pattern detection — useful for cold construction when person isn't in any database.
- For unfamiliar companies, Hunter often returns just the pattern; you can construct the email yourself and verify.
- Apollo + Hunter overlap significantly. Pick one as your second-step provider.
