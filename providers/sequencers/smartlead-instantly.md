# Smartlead + Instantly

**Type**: Cold email infrastructure (mailbox warmup + sending at scale)
**Best for**: High-volume cold email; multi-mailbox rotation; growth-stage SaaS

---

## When to Choose Smartlead/Instantly vs SalesLoft/Outreach

| Use Smartlead/Instantly | Use SalesLoft/Outreach |
|-------------------------|------------------------|
| 1k+ contacts/week cold email | <500/week SDR cadence |
| Mailbox warming critical | Pre-warmed established sender |
| Volume-driven motion | High-touch SDR motion |
| Founder-led GTM, no SDR team | Established SDR team |
| Lower budget per contact | Premium tooling budget |

## Push Patterns

### Smartlead
- Action: `clay/smartlead-push`
- Required: `campaign_id`, `lead_data`
- Smartlead rotates across pre-warmed mailboxes

### Instantly
- Action: `clay/instantly-push`
- Required: `campaign_id`, `lead_data`
- Similar mailbox rotation model

## Mandatory: Sending Gate Filter

```
Action: push-smartlead OR push-instantly
Run Condition: sending_gate_eligible = TRUE
```

## Daily Send Limits

Both platforms impose daily sending limits per mailbox:
- Smartlead default: 30-50 emails/mailbox/day
- Instantly default: 30-50 emails/mailbox/day

If your batch is 500 contacts and you have 5 mailboxes:
- 5 × 50 = 250 sends/day capacity
- Configure your Clay push to drip-feed 250/day (use Clay's row-throttling)

## Field Mapping (Both Tools)

| Clay Column | Field |
|-------------|-------|
| email | email |
| first_name | first_name |
| last_name | last_name |
| company_name | company |
| custom variables (first_line, subject) | custom_field_N |

## Custom Variables in Templates

Both platforms support template variables. Map Claygent outputs into them:
- In Smartlead/Instantly template, use `{{custom_first_line}}` or `{{custom_subject}}`
- Map Clay column to that custom field on push

## Sender Domain Hygiene

For high-volume cold email, mailbox hygiene is critical:

1. Use dedicated sending domains (not your main marketing domain) → e.g., `getbrand.io` instead of `brand.com`
2. Warm new mailboxes for 4-6 weeks before pushing volume
3. Monitor bounce rate (target <2%) and reply rate (target >2%)
4. Pause campaigns immediately if bounce >5% — domain reputation rescue needed

## Common Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| High bounce rate | Source list polluted or stale | Re-verify with ZeroBounce; tighten Sending Gate |
| Replies marked as bounces | Misconfigured reply detection | Set up Smartlead's reply-handling webhooks |
| Low open rates | Subject quality OR sender domain reputation issue | A/B test subjects; check sender score (Senderscore.org) |
| Spam trap hit | Source list bought or scraped poorly | DROP. Domain reputation recovery takes weeks |

## Notes

- Smartlead/Instantly = "send the email" tools. Clay does the targeting + content; they handle deliverability.
- For founder-led GTM at small companies, this combo (Clay + Smartlead/Instantly) often replaces a $20k/mo SDR + SalesLoft stack at fraction of cost.
- Higher tooling skill required — deliverability isn't push-button.
