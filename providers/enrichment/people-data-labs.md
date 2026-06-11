# People Data Labs (PDL)

**Type**: Firmographic + person enrichment + funding data
**Available via**: Clay-managed OR own key
**Best for**: Enterprise firmographic detail, revenue ranges, funding data

---

## What It Returns

| Data Point | Coverage | Confidence |
|------------|----------|------------|
| Company firmographics (industry, size, geo) | 90% | High |
| Revenue range | 70% (better than Clay native at 50%) | Medium-high |
| Funding stage + dates | 80% (for funded companies) | High |
| Person enrichment (title, history) | 80% | Medium-high |
| Email | 65% | Medium |

## Cost

| Operation | Credits |
|-----------|---------|
| Company enrichment | 2 |
| Person enrichment | 2 |

## When to Use

- ✅ Need revenue ranges where Clay native is missing
- ✅ Funding data critical for ICP gating
- ✅ Enterprise + mid-market account enrichment
- ✅ Person work history for trigger detection

## When NOT to Use

- ❌ As email source (use Apollo + waterfall instead — cheaper, comparable match)
- ❌ Pre-revenue stealth startups (low coverage)
- ❌ Small SMB (<50 employees, mixed coverage)

## Common Use Cases

### Revenue Range for ICP Gate
```clayscript
revenue_range = PDL enrichment
icp_gate includes: revenue_range IN ["$10M-$50M", "$50M-$100M", ...]
```

### Funding Stage Trigger
```clayscript
funding_stage from PDL
trigger_event = IF(funding_event_date > NOW() - 90 days, "funding", NULL)
```

## Configuration

```
Column: company_data
Provider: People Data Labs
Input: {company_domain}
Returns: industry, employee_count, revenue_range, funding_stage, funding_last_round_date
Run Condition: pass_1_qualified = TRUE
```

## Common Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Revenue range NULL for known mid-market | PDL hasn't enriched that domain | Fall back to Clay native or skip column |
| Funding stage shows "Seed" for Series A company | PDL stale data | Refresh with Predictleads OR override with CRM data |
| Person history outdated | PDL refresh lag | Don't use for time-sensitive trigger detection — use The Swarm or Champify |

## Notes

- PDL is "data-rich" — many fields per enrichment. Don't pull all if you only need 1-2 columns; structure your column to extract only what's needed.
- Strong for "data hygiene" workbooks (Pattern 3) where you're updating CRM with verified firmographic data.
