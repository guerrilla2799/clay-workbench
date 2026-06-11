# Hiring + Funding Signals

Two of the highest-converting trigger events for B2B outbound. This file covers detection sources, classification, and use in workbooks.

---

## Funding Signals

### Why It Converts
A company that just closed a round has:
- Net-new budget (you're not displacing spend, you're getting fresh allocation)
- Public commitment to growth (board pressure to deploy capital)
- Hiring pipeline filling (your tooling helps them scale)
- Press attention (warm context for outbound)

Best window: 30-90 days post-announcement. Earlier than 30 = still hiring core team; later than 90 = budget already allocated.

### Sources

| Source | Latency | Coverage |
|--------|---------|----------|
| Predictleads | Same day | Broad (Crunchbase + SEC + press) |
| Crunchbase API (own key) | Real-time | Most comprehensive |
| PitchBook (own key) | Real-time | Best for late-stage |
| Newsweek / TechCrunch RSS | Same day | Press-only filter |

### Detection

```
Column: funding_event
Provider: Predictleads
Returns: event_type, event_date, funding_amount, funding_round, source_url
Run Condition: pass_1_qualified = TRUE
```

### Use in Gates

```clayscript
funding_event_qualifies = AND(
  funding_event != NULL,
  funding_round IN ["Series A", "Series B", "Series C", "Series D"],
  DAYS_BETWEEN(NOW(), funding_event_date) BETWEEN 30 AND 120
)
```

Filter out Seed (often too early to deploy budget on your tool) unless your product specifically targets pre-PMF.

### Common Pitfalls

- **Stale data**: Predictleads occasionally lags on private rounds. Cross-check with Crunchbase if critical.
- **Round inflation**: Some companies announce extension rounds as "Series A" when they're really Seed-2. Verify with valuation if you can.
- **Recency mis-calculation**: Some sources use announcement date, others use closing date. Default to announcement.

---

## Hiring Signals

### Why It Converts
Companies with multiple open reqs are:
- Scaling in a specific function (you can target the manager who'll buy your tool for them)
- Likely under-tooled (otherwise wouldn't need more headcount)
- Acknowledging the need for capacity in that function

Best window: 7-45 days of open reqs.

### Sources

| Source | Latency | Coverage |
|--------|---------|----------|
| Predictleads | Daily refresh | Job boards + ATS scraping |
| Wellfound (Angel List) | Same day | Startup-focused |
| LinkedIn Jobs API (own key) | Real-time | Best general |
| Indeed scraping (own key/scraper) | Real-time | Volume coverage |

### Detection

```
Column: hiring_signal
Provider: Predictleads
Input: {company_domain}
Returns: open_reqs, hiring_focus_function, departments_hiring, recent_post_date
Run Condition: pass_1_qualified = TRUE
```

### Use in Gates

```clayscript
hiring_qualifies = AND(
  open_reqs >= 3,                     // single req often noise
  hiring_focus_function IN ["Sales", "RevOps", "Marketing"],  // your ICP function
  recent_post_date >= NOW() - 30 days
)
```

### Use in Personalization

```clayscript
// In Claygent first_line prompt
trigger_event = "hiring {hiring_focus_function} — {open_reqs} open reqs"
```

First-line: "Saw you're scaling {function} — typical at this growth stage. Curious how you're thinking about {pain_category} as the team grows."

---

## Combined Funding + Hiring Pattern

Funding without hiring = capital not yet deployed → wait.
Funding + hiring = capital being deployed RIGHT NOW → ideal window.

```clayscript
hot_window = AND(
  funding_event != NULL,
  DAYS_BETWEEN(NOW(), funding_event_date) BETWEEN 30 AND 120,
  open_reqs >= 5,
  hiring_focus_function IN ["{your_target_function}"]
)
```

This composite gate often returns 5-10% of an ICP list — those are the highest-converting accounts for next 30 days.

---

## Notes

- Both signals decay fast. Set automated weekly refresh in your workbook (Pattern 3 — Account Refresh).
- Don't gate too tightly on these — false negatives lose good accounts. Better to use as scoring boost than hard gate, except in trigger-required ABM.
- Pair with Claygent classifier to filter noise (re-orgs that aren't really hiring, terminated funding announcements, etc.).
